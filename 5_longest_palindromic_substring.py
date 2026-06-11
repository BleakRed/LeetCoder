class Solution(object):
    def longestPalindrome(self, s):
        n = len(s)
        start = end = 0

        for i in range(n):
            # odd length palindrome centered at i
            l = r = i
            while l >= 0 and r < n and s[l] == s[r]:
                l -= 1
                r += 1
            if r - l - 1 > end - start:
                start, end = l + 1, r - 1

            # even length palindrome centered between i and i+1
            l, r = i, i + 1
            while l >= 0 and r < n and s[l] == s[r]:
                l -= 1
                r += 1
            if r - l - 1 > end - start:
                start, end = l + 1, r - 1

        return s[start:end + 1]
