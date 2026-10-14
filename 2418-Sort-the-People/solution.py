class Solution:
    def sortPeople(self, names: list[str], heights: list[int]) -> list[str]:
        n = len(heights)

        for i in range(n-1):
            max_index = i

            for j in range(i+1,n):
                if heights[j] > heights[max_index]:
                    max_index = j
            names[i],names[max_index] = names[i], names[max_index]
            heights[i], heights[max_index] = heights[max_index],heights[i]

