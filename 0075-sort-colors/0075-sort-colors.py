class Solution:
    def sortColors(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        n = len(nums)
        for i in range(n):
            min_index = i
            for j in range(i+1,n):
                if nums[j] < nums[min_index]:
                    min_index = j
            nums[i], nums[min_index] = nums[min_index], nums[i]
        print(nums)

a = Solution()
nums = [2,0,2,1,1,0]
a.sortColors(nums)       