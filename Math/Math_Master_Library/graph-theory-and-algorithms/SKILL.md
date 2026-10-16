---
name: graph-theory-and-algorithms
description: "Work on graph theory and algorithmic mathematics: trees, connectivity, paths, cycles, coloring, planarity, matchings, flows, shortest paths, spanning trees, complexity (P vs NP), network analysis. Use for graph problems, networks, and algorithm design."
---

# Graph Theory & Algorithms

## Basics
- Graph G = (V,E); degree sum = 2|E| (handshake); paths, cycles, connected components; bipartite iff no odd cycle; trees: connected acyclic, |E| = |V| - 1; forests; rooted trees.
- Euler: circuit exists iff connected and all degrees even; Hamiltonian cycles (NP-complete; Dirac and Ore conditions).
- Planarity: Euler's formula V - E + F = 2; E <= 3V - 6; Kuratowski (K5, K3,3 minors); Four Color Theorem; chromatic number chi(G) <= Delta + 1, Brooks theorem; chromatic polynomial.
- Matchings: Hall's theorem; Konig (bipartite max matching = min vertex cover); Tutte; Hungarian algorithm for assignment.
- Connectivity: Menger's theorem; max-flow min-cut (Ford-Fulkerson, Edmonds-Karp, Dinic).
- Spectral: adjacency and Laplacian eigenvalues; number of spanning trees via Kirchhoff's matrix-tree theorem; expanders; random walks.

## Algorithms
- BFS/DFS O(V+E); topological sort; strongly connected components (Tarjan/Kosaraju).
- Shortest paths: Dijkstra (non-negative weights) O((V+E) log V), Bellman-Ford (negative edges), Floyd-Warshall O(V^3), A*.
- Minimum spanning tree: Kruskal (union-find) and Prim.
- Network flow, bipartite matching, 2-SAT, LCA.
- Complexity: P, NP, NP-complete (SAT, 3-coloring, clique, vertex cover, TSP decision, Hamiltonian path); reductions; approximation algorithms (2-approx vertex cover); P vs NP open.

## Random & extremal graphs
Erdos-Renyi G(n,p) threshold phenomena (connectivity at p = ln n/n); small-world and scale-free networks; Turan; Ramsey; graph limits.

## Proof/solution pattern
Pick the right invariant (degree, parity, coloring), use induction on vertices/edges, double count edges, apply extremal choice (longest path), or reduce to a known algorithm.
