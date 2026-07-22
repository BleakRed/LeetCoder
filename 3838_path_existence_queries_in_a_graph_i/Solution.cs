public class Solution {
    public bool[] PathExistenceQueries(int n, int[] nums, int maxDiff, int[][] queries) {
        int[] parent = new int[n];
        int[] rank = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;

        int Find(int x) {
            while (parent[x] != x) {
                parent[x] = parent[parent[x]];
                x = parent[x];
            }
            return x;
        }

        void Union(int x, int y) {
            int rx = Find(x), ry = Find(y);
            if (rx == ry) return;
            if (rank[rx] < rank[ry]) {
                parent[rx] = ry;
            } else if (rank[rx] > rank[ry]) {
                parent[ry] = rx;
            } else {
                parent[ry] = rx;
                rank[rx]++;
            }
        }

        for (int i = 1; i < n; i++) {
            if (nums[i] - nums[i - 1] <= maxDiff) {
                Union(i - 1, i);
            }
        }

        bool[] result = new bool[queries.Length];
        for (int i = 0; i < queries.Length; i++) {
            result[i] = Find(queries[i][0]) == Find(queries[i][1]);
        }

        return result;
    }
}
