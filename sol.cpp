#include <vector>
#include <queue>
using namespace std;

class Solution {
public:
    long long maxTotalValue(vector<int>& nums, int k) {
        int n = nums.size();
        vector<int> lg(n + 1);
        for (int i = 2; i <= n; ++i)
            lg[i] = lg[i >> 1] + 1;

        int K = lg[n] + 1;
        vector<vector<int>> st_max(n, vector<int>(K));
        vector<vector<int>> st_min(n, vector<int>(K));
        for (int i = 0; i < n; ++i)
            st_max[i][0] = st_min[i][0] = nums[i];
        for (int j = 1; j < K; ++j) {
            for (int i = 0; i + (1 << j) <= n; ++i) {
                st_max[i][j] = max(st_max[i][j - 1], st_max[i + (1 << (j - 1))][j - 1]);
                st_min[i][j] = min(st_min[i][j - 1], st_min[i + (1 << (j - 1))][j - 1]);
            }
        }

        auto query = [&](int l, int r) -> pair<int,int> {
            int k = lg[r - l + 1];
            return {max(st_max[l][k], st_max[r - (1 << k) + 1][k]),
                    min(st_min[l][k], st_min[r - (1 << k) + 1][k])};
        };

        priority_queue<pair<long long, pair<int,int>>> pq;
        for (int l = 0; l < n; ++l) {
            auto [mx, mn] = query(l, n - 1);
            pq.push({(long long)(mx - mn), {l, n - 1}});
        }

        long long ans = 0;
        while (k--) {
            auto [val, p] = pq.top(); pq.pop();
            auto [l, r] = p;
            ans += val;
            if (r > l) {
                auto [mx, mn] = query(l, r - 1);
                pq.push({(long long)(mx - mn), {l, r - 1}});
            }
        }
        return ans;
    }
};
