using System;
using System.Collections.Generic;

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

public class Program {
    public static void Main() {
        var s = new Solution();
        Console.WriteLine(s.MaximumLength(new int[]{5,4,1,2,2})); // 3
        Console.WriteLine(s.MaximumLength(new int[]{1,3,2,4})); // 1
        Console.WriteLine(s.MaximumLength(new int[]{1,1,1})); // 3
        Console.WriteLine(s.MaximumLength(new int[]{1,1})); // 1
        Console.WriteLine(s.MaximumLength(new int[]{2,2,2,2})); // 1
        Console.WriteLine(s.MaximumLength(new int[]{2,4,2})); // 3
        Console.WriteLine(s.MaximumLength(new int[]{2,4,4,2})); // 3
        Console.WriteLine(s.MaximumLength(new int[]{2,4,16,4,2})); // 5
        Console.WriteLine(s.MaximumLength(new int[]{2,4,16,16,4,2})); // 5
        Console.WriteLine(s.MaximumLength(new int[]{3,9,3})); // 3
        Console.WriteLine(s.MaximumLength(new int[]{2,2,4,4,8,8})); // ?
    }
}
