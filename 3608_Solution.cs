public class Solution {
    private int Gcd(int a, int b) {
        while (b != 0) {
            int t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    public int SubsequencePairCount(int[] nums) {
        const int MOD = 1000000007;
        const int M = 201; // max value is 200, plus 0 for empty
        int[] dp = new int[M * M];
        dp[0] = 1; // g1 = 0, g2 = 0

        foreach (int x in nums) {
            int[] ndp = (int[])dp.Clone();
            for (int g1 = 0; g1 < M; g1++) {
                int baseRow = g1 * M;
                for (int g2 = 0; g2 < M; g2++) {
                    int cur = dp[baseRow + g2];
                    if (cur == 0) continue;

                    int ng1 = Gcd(g1, x);
                    int idx1 = ng1 * M + g2;
                    ndp[idx1] = (ndp[idx1] + cur) % MOD;

                    int ng2 = Gcd(g2, x);
                    int idx2 = g1 * M + ng2;
                    ndp[idx2] = (ndp[idx2] + cur) % MOD;
                }
            }
            dp = ndp;
        }

        long result = 0;
        for (int g = 1; g < M; g++) {
            result += dp[g * M + g];
        }
        return (int)(result % MOD);
    }
}
