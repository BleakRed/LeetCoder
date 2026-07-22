public class Solution {
    public int[] GcdValues(int[] nums, long[] queries) {
        int maxVal = 0;
        foreach (int v in nums) if (v > maxVal) maxVal = v;

        int[] cnt = new int[maxVal + 1];
        foreach (int v in nums) cnt[v]++;

        long[] multiples = new long[maxVal + 1];
        for (int g = 1; g <= maxVal; g++) {
            for (int k = g; k <= maxVal; k += g) {
                multiples[g] += cnt[k];
            }
        }

        long[] exact = new long[maxVal + 1];
        for (int g = 1; g <= maxVal; g++) {
            long c = multiples[g];
            exact[g] = c * (c - 1) / 2;
        }

        for (int g = maxVal; g >= 1; g--) {
            for (int k = 2 * g; k <= maxVal; k += g) {
                exact[g] -= exact[k];
            }
        }

        int uniqueCnt = 0;
        for (int g = 1; g <= maxVal; g++) {
            if (exact[g] > 0) uniqueCnt++;
        }

        int[] vals = new int[uniqueCnt];
        long[] pref = new long[uniqueCnt];
        int idx = 0;
        for (int g = 1; g <= maxVal; g++) {
            if (exact[g] > 0) {
                vals[idx] = g;
                pref[idx] = (idx == 0 ? 0 : pref[idx - 1]) + exact[g];
                idx++;
            }
        }

        int m = queries.Length;
        int[] ans = new int[m];
        for (int i = 0; i < m; i++) {
            long q = queries[i];
            int lo = 0, hi = uniqueCnt - 1;
            while (lo < hi) {
                int mid = (lo + hi) / 2;
                if (pref[mid] > q)
                    hi = mid;
                else
                    lo = mid + 1;
            }
            ans[i] = vals[lo];
        }
        return ans;
    }
}
