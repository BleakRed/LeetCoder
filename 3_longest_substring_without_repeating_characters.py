class Solution(object):
    def lengthOfLongestSubstring(self, s):
        last = {}
        left = ans = 0
        for right, c in enumerate(s):
            if c in last and last[c] >= left:
                left = last[c] + 1
            last[c] = right
            ans = max(ans, right - left + 1)
        return ans
