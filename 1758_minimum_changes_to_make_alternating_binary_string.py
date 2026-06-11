class Solution(object):
    def minOperations(self, s):
        changes0 = changes1 = 0
        for i, c in enumerate(s):
            if i % 2 == 0:
                if c != '0':
                    changes0 += 1
                if c != '1':
                    changes1 += 1
            else:
                if c != '1':
                    changes0 += 1
                if c != '0':
                    changes1 += 1
        return min(changes0, changes1)
