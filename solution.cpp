#include<bits/stdc++.h>
using namespace std;

#define int long long

class Dinic {
public:
    struct Edge {
        int to, rev;
        int flow, cap;
    };

    Dinic(int n) : graph(n), level(n), start(n) {}

    void addEdge(int u, int v, int cap) {
        graph[u].push_back({v, static_cast<int>(graph[v].size()), 0, cap});
        graph[v].push_back({u, static_cast<int>(graph[u].size()) - 1, 0, 0}); // reverse edge
    }

    int maxFlow(int s, int t) {
        int total_flow = 0;
        while (bfs(s, t)) {
            std::fill(start.begin(), start.end(), 0);
            while (int flow = dfs(s, t, INT_MAX)) {
                total_flow += flow;
            }
        }
        return total_flow;
    }

private:
    std::vector<std::vector<Edge>> graph;
    std::vector<int> level, start;

    bool bfs(int s, int t) {
        std::fill(level.begin(), level.end(), -1);
        level[s] = 0;
        std::queue<int> q;
        q.push(s);
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (const Edge &e : graph[u]) {
                if (level[e.to] < 0 && e.flow < e.cap) {
                    level[e.to] = level[u] + 1;
                    q.push(e.to);
                }
            }
        }
        return level[t] >= 0;
    }

    int dfs(int u, int t, int flow) {
        if (u == t) return flow;
        for (int &i = start[u]; i < graph[u].size(); ++i) {
            Edge &e = graph[u][i];
            if (level[e.to] == level[u] + 1 && e.flow < e.cap) {
                int curr_flow = std::min(flow, e.cap - e.flow);
                int temp_flow = dfs(e.to, t, curr_flow);
                if (temp_flow > 0) {
                    e.flow += temp_flow;
                    graph[e.to][e.rev].flow -= temp_flow;
                    return temp_flow;
                }
            }
        }
        return 0;
    }
};

/*

### Explanation

- **Graph Representation**: The graph is represented using adjacency lists, where each node has a list of edges. Each edge contains the destination node, the reverse edge index, the current flow, and the capacity.
- **BFS**: Used to build the level graph, which helps in finding augmenting paths more efficiently.
- **DFS**: Used to find blocking flows along the level graph.
- **Flow Augmentation**: Flow is augmented along the path found by DFS, and both forward and reverse edges are updated.

### Guiding Question

What would you do if the graph had very large capacities that might cause integer overflow? How would you modify the implementation to handle such cases?

### Next Learning Objective

Understand how to handle large input sizes and capacities in flow algorithms, ensuring robustness against overflow.
*/


void solve() {
    int n, m;
    cin >> n >> m;

    // Coach: Create a Dinic object with n+2 number of node
/* [Coach Response]
To create a Dinic object with `n+2` nodes, you need to instantiate the Dinic class with `n+2` as the parameter. This is often done to include additional nodes such as a super-source and super-sink in flow network problems.

Here's the exact line to create the Dinic object with `n+2` nodes:
*/

Dinic dinic(n + 2);

/* [Coach Response]
### Implementation in Context

Here's how you can use this line in your `solve` function:
*/

void solve() {
    int n, m;
    cin >> n >> m;

    // Create a Dinic object with n+2 nodes
    Dinic dinic(n + 2);

    // Further implementation for adding edges and calculating max flow
}

/* [Coach Response]
### Explanation

- **`n+2` Nodes**: This setup accounts for the original `n` nodes plus two additional nodes. These extra nodes are often used as a super-source and a super-sink, which can simplify handling multiple sources or sinks in the network.

- **Dinic Initialization**: `Dinic dinic(n + 2);` initializes the graph data structures within the Dinic class to accommodate `n+2` nodes, preparing it for subsequent operations like adding edges and calculating flows.

Why might you want to use a super-source or super-sink in a flow network problem, and how do they simplify the problem?
*/
}

signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t = 1;
    cin >> t;
    while (t--) {
        solve();
    }
    return 0;
}