
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
USERNAME = os.getenv("LEETCODE_USERNAME", "seYEfSEx0n")
REPO = os.getenv("GITHUB_REPOSITORY", "sahil51/DSA")
URL = "https://leetcode.com/graphql/"

HEADERS = {
    "Content-Type": "application/json",
    "Referer": f"https://leetcode.com/u/{USERNAME}/",
    "User-Agent": "Mozilla/5.0 DSA-README-Bot",
}

EXCLUDED = {
    ".git", ".github", ".venv", "venv",
    "__pycache__", ".pytest_cache", "node_modules",
    "dist", "build", "scripts",
}

STATS_QUERY = """
query userStats($username: String!) {
  matchedUser(username: $username) {
    profile { ranking }
    submitStats {
      acSubmissionNum { difficulty count }
    }
    userCalendar { streak totalActiveDays }
  }
}
"""

RECENT_QUERY = """
query recentAccepted($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title titleSlug timestamp lang
  }
}
"""


def query_graphql(query, variables):
    payload = json.dumps({
        "query": query,
        "variables": variables,
    }).encode()

    request = Request(
        URL,
        data=payload,
        headers=HEADERS,
        method="POST",
    )

    with urlopen(request, timeout=20) as response:
        result = json.loads(response.read().decode())

    if result.get("errors") or not result.get("data"):
        raise RuntimeError("Invalid LeetCode response")

    return result["data"]


def replace_section(text, start, end, body):
    if start not in text or end not in text:
        raise RuntimeError(f"Missing markers: {start}")

    before, remaining = text.split(start, 1)
    _, after = remaining.split(end, 1)

    return before + start + "\n" + body.strip() + "\n" + end + after


def safe(value):
    return str(value).replace("|", r"\|").replace("\n", " ")


def fetch_leetcode():
    data = query_graphql(
        STATS_QUERY,
        {"username": USERNAME},
    )

    user = data.get("matchedUser")
    if not user:
        raise RuntimeError("LeetCode user not found")

    recent_data = query_graphql(
        RECENT_QUERY,
        {"username": USERNAME, "limit": 10},
    )

    return user, recent_data.get("recentAcSubmissionList") or []


def stats_markdown(user):
    counts = {
        item["difficulty"]: item["count"]
        for item in user["submitStats"]["acSubmissionNum"]
    }

    calendar = user.get("userCalendar") or {}
    ranking = (user.get("profile") or {}).get("ranking")

    rows = [
        f"**Profile:** [@{USERNAME}](https://leetcode.com/u/{USERNAME}/)",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Total solved | {counts.get('All', 0)} |",
        f"| Easy | {counts.get('Easy', 0)} |",
        f"| Medium | {counts.get('Medium', 0)} |",
        f"| Hard | {counts.get('Hard', 0)} |",
        f"| Calendar streak | {calendar.get('streak', 0)} days |",
        f"| Active days | {calendar.get('totalActiveDays', 0)} |",
    ]

    if ranking is not None:
        rows.append(f"| Global ranking | {ranking:,} |")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows.extend(["", f"<sub>Last successful refresh: {now}</sub>"])

    return "\n".join(rows)


def recent_markdown(items):
    if not items:
        return "_No recent accepted submissions returned._"

    rows = [
        "| Problem | Language | Accepted time (UTC) |",
        "|---|---|---|",
    ]

    for item in items:
        title = safe(item.get("title", "Unknown"))
        slug = item.get("titleSlug", "")
        language = safe(item.get("lang", "Unknown"))

        link = (
            f"https://leetcode.com/problems/{slug}/"
            if slug else f"https://leetcode.com/u/{USERNAME}/"
        )

        try:
            stamp = datetime.fromtimestamp(
                int(item["timestamp"]), timezone.utc
            ).strftime("%Y-%m-%d %H:%M")
        except (KeyError, ValueError, TypeError, OSError):
            stamp = "Unknown"

        rows.append(f"| [{title}]({link}) | {language} | {stamp} |")

    return "\n".join(rows)


def repository_markdown():
    files = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(ROOT)

        if any(part in EXCLUDED for part in relative.parts):
            continue

        if path.name == "README.md":
            continue

        files.append(path)

    python_files = [
        path for path in files
        if path.suffix.lower() == ".py"
    ]

    folders = sorted({
        path.parent for path in python_files
        if path.parent != ROOT
    }, key=lambda path: str(path).lower())

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    metrics = "\n".join([
        "| Metric | Value |",
        "|---|---:|",
        f"| Repository files | {len(files)} |",
        f"| Python files | {len(python_files)} |",
        f"| Folders with Python files | {len(folders)} |",
        f"| Last scan (UTC) | {now} |",
    ])

    if not folders:
        problems = "_No nested folders with Python solutions found._"
    else:
        rows = ["| Folder | Python files |", "|---|---:|"]

        for folder in folders:
            count = sum(
                1 for path in python_files
                if path.parent == folder
            )

            relative = folder.as_posix()
            link = f"https://github.com/{REPO}/tree/main/{relative}"

            rows.append(
                f"| [`{safe(relative)}`]({link}) | {count} |"
            )

        problems = "\n".join(rows)

    return metrics, problems


def main():
    content = README.read_text(encoding="utf-8")

    metrics, problems = repository_markdown()

    content = replace_section(
        content,
        "<!-- DSA_REPO_METRICS_START -->",
        "<!-- DSA_REPO_METRICS_END -->",
        metrics,
    )

    content = replace_section(
        content,
        "<!-- DSA_REPO_PROBLEMS_START -->",
        "<!-- DSA_REPO_PROBLEMS_END -->",
        problems,
    )

    try:
        user, recent = fetch_leetcode()

        content = replace_section(
            content,
            "<!-- DSA_STATS_START -->",
            "<!-- DSA_STATS_END -->",
            stats_markdown(user),
        )

        content = replace_section(
            content,
            "<!-- DSA_RECENT_START -->",
            "<!-- DSA_RECENT_END -->",
            recent_markdown(recent),
        )

        print("LeetCode sections updated.")

    except Exception as error:
        print(
            f"LeetCode refresh failed; keeping existing stats: {error}",
            file=sys.stderr,
        )

    README.write_text(content, encoding="utf-8")
    print("Repository sections updated.")


if __name__ == "__main__":
    main()
