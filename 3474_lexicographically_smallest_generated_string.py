class Solution(object):
    def generateString(self, str1, str2):
        n, m = len(str1), len(str2)
        L = n + m - 1

        word = [None] * L
        forced = [False] * L

        # Phase 1: enforce all T constraints
        for i in range(n):
            if str1[i] == 'T':
                for k in range(m):
                    pos = i + k
                    c = str2[k]
                    if word[pos] is None:
                        word[pos] = c
                        forced[pos] = True
                    elif word[pos] != c:
                        return ""
                    else:
                        forced[pos] = True

        # Phase 2: for each F window, find its last modifiable position
        f_sat = [False] * n
        last_idx = [-1] * n     # rightmost position that can save this window
        last_need = [''] * n    # str2 char at that offset (must differ from it)

        need_at = [[] for _ in range(L)]  # position -> list of (window_idx, needed_char)

        for i in range(n):
            if str1[i] == 'F':
                found = False
                for k in range(m - 1, -1, -1):
                    pos = i + k
                    if forced[pos]:
                        if word[pos] != str2[k]:
                            f_sat[i] = True
                            found = True
                            break
                    else:
                        last_idx[i] = pos
                        last_need[i] = str2[k]
                        need_at[pos].append((i, str2[k]))
                        found = True
                        break
                if not found:
                    return ""

        # Phase 3: sweep left-to-right
        for p in range(L):
            # ---- last-chance windows that must be fixed at p ----
            need = set()
            for i, c in need_at[p]:
                if not f_sat[i]:
                    need.add(c)

            if need:
                if forced[p]:
                    if word[p] in need:
                        return ""
                else:
                    for c_ord in range(ord('a'), ord('z') + 1):
                        c = chr(c_ord)
                        if c not in need:
                            word[p] = c
                            break
                    if word[p] is None:
                        return ""

                for i, _ in need_at[p]:
                    f_sat[i] = True

            # ---- default free positions ----
            if word[p] is None:
                word[p] = 'a'

            # ---- satisfy any F window covering p ----
            left = max(0, p - m + 1)
            right = min(p, n - 1)
            for i in range(left, right + 1):
                if str1[i] == 'F' and not f_sat[i]:
                    if word[p] != str2[p - i]:
                        f_sat[i] = True

        # All F windows must be satisfied
        for i in range(n):
            if str1[i] == 'F' and not f_sat[i]:
                return ""

        return ''.join(word)
