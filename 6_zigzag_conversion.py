class Solution(object):
    def convert(self, s, numRows):
        if numRows == 1 or numRows >= len(s):
            return s

        rows = [''] * numRows
        cur = 0
        down = True
        for c in s:
            rows[cur] += c
            cur += 1 if down else -1
            if cur == 0 or cur == numRows - 1:
                down = not down

        return ''.join(rows)
