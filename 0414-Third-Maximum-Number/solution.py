class Solution:
    def thirdMax(self, nums: list[int]) -> int:
        largest = float('-inf')
        secondlargest=float('-inf')
        thirdlargest=float('-inf')
        for i in range(len(nums)):
            if nums[i] == largest or nums[i] == secondlargest or nums[i] == thirdlargest:
                continue
            if nums[i]>largest:
                thirdlargest=secondlargest
                secondlargest=largest
                largest=nums[i]
            
            elif nums[i]>secondlargest and secondlargest!=largest:
                thirdlargest=secondlargest
                secondlargest=nums[i]
            
            elif nums[i]>thirdlargest and thirdlargest!=secondlargest:
                thirdlargest=nums[i]
        if thirdlargest == float('-inf'):
            return largest

        return thirdlargest
