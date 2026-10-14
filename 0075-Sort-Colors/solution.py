class Solution:
    def sortColors(self, nums: list[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        n = len(nums)
        for i in range(n-1):
            min_index = i
            for j in range(i+1,n):
                if nums[j] < nums[min_index]:
                    min_index = j
            nums[j], nums[min_index] = nums[min_index],nums[j]
        return nums