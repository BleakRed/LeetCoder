class Solution(object):
    def minBitwiseArray(self, nums):
        res = []
        for n in nums:
            if n % 2 == 0:
                res.append(-1)
                continue
            ans = n - 1
            k = 1
            while (n >> k) & 1:
                cand = (n >> (k + 1)) << (k + 1) | ((1 << k) - 1)
                if cand < ans:
                    ans = cand
                k += 1
            res.append(ans)
        return res
