class Solution(object):
    def myAtoi(self, s):
        i, n = 0, len(s)
        while i < n and s[i] == ' ':
            i += 1
        if i == n:
            return 0

        sign = 1
        if s[i] == '-':
            sign = -1
            i += 1
        elif s[i] == '+':
            i += 1

        INT_MAX = 2**31 - 1
        INT_MIN = -2**31
        res = 0
        while i < n and s[i].isdigit():
            d = ord(s[i]) - 48
            if res > (INT_MAX - d) // 10:
                return INT_MAX if sign == 1 else INT_MIN
            res = res * 10 + d
            i += 1

        return sign * res
