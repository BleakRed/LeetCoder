class Solution(object):
    def leftRightDifference(self, nums):
        total = sum(nums)
        left = 0
        res = []
        for x in nums:
            right = total - left - x
            res.append(abs(left - right))
            left += x
        return res
