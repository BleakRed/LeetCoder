public class Solution {
    public int MaximumLength(int[] nums) {
        var freq = new Dictionary<int, int>();
        foreach (int v in nums) {
            freq[v] = freq.GetValueOrDefault(v, 0) + 1;
        }

        int ans = 1;
        if (freq.TryGetValue(1, out int cnt1)) {
            ans = Math.Max(ans, cnt1 % 2 == 1 ? cnt1 : cnt1 - 1);
        }

        const long limit = 1_000_000_000L;

        foreach (var kv in freq) {
            long x = kv.Key;
            if (x == 1) continue;

            int len = 1;
            long cur = x;
            while (true) {
                if (freq.TryGetValue((int)cur, out int cnt) && cnt >= 1) {
                    ans = Math.Max(ans, len);
                }
                if (cnt >= 2) {
                    long nxt = cur * cur;
                    if (nxt > limit) break;
                    cur = nxt;
                    len += 2;
                } else {
                    break;
                }
            }
        }

        return ans;
    }
}
