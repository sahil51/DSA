
#!/usr/bin/env python3

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

START = "<!-- DSA_PROGRESS_START -->"
END = "<!-- DSA_PROGRESS_END -->"

EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    "scripts",
}


def get_python_files():
    for path in ROOT.rglob("*.py"):
        relative_parts = path.relative_to(ROOT).parts

        if any(part in EXCLUDED_DIRS for part in relative_parts):
            continue

        yield path


def main():
    if not README.exists():
        raise SystemExit("README.md not found.")

    files = list(get_python_files())

    problem_folders = {
        path.parent
        for path in files
        if path.parent != ROOT
    }

    updated_at = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    replacement = "\n".join([
        START,
        "| Metric | Progress |",
        "|---|---:|",
        f"| Folders containing Python solutions | {len(problem_folders)} |",
        f"| Python solution files detected | {len(files)} |",
        f"| Last automated update (UTC) | {updated_at} |",
        "",
        "> These metrics track repository files, not your live LeetCode solved count or actual daily streak.",
        END,
    ])

    content = README.read_text(encoding="utf-8")

    if START not in content or END not in content:
        raise SystemExit(
            "Progress markers are missing from README.md."
        )

    before, rest = content.split(START, 1)
    _, after = rest.split(END, 1)

    new_content = before + replacement + after

    if new_content != content:
        README.write_text(new_content, encoding="utf-8")
        print(
            f"Updated: {len(problem_folders)} folders, "
            f"{len(files)} Python files."
        )
    else:
        print("README progress is already up to date.")


if __name__ == "__main__":
    main()
