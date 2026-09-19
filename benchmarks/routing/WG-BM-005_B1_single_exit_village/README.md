# WG-BM-005 (B1) — Single exit village

## Scenario

```
village ----2 min---- a ----3 min---- exit
```

Three nodes, two undirected edges.

## Derivation

A path graph on three nodes has exactly one simple path between its endpoints,
so there is exactly one egress route and its free-flow travel time is
`2 + 3 = 5` minutes.

Deleting `a` splits the graph into `{village}` and `{exit}`, so `a` is an
articulation point. Deleting either terminal leaves two nodes still joined by an
edge, so neither terminal is. A tree has no cycles, so every edge is a bridge.

The smallest set of *non-terminal* nodes whose removal separates `village` from
`exit` is `{a}`, of size 1. By Menger's theorem the number of internally
node-disjoint `village`-`exit` paths equals that cut, so it is 1.

## Expected

| Quantity | Value |
|---|---|
| egress routes | 1 |
| egress travel time | 5 min |
| articulation points | `[a]` |
| bridges | both edges |
| minimum internal node cut | 1 |
| single point of failure | `true` |

## What this is for

This is the *positive control* for WG-BM-006. A system that claims one egress
route must be right here, or its warnings mean nothing. It also fixes the
definition used throughout the suite: the cut excludes the source and the
destinations, because "remove the village" is not an evacuation scenario.
