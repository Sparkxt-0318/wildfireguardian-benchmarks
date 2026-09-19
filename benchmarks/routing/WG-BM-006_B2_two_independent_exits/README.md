# WG-BM-006 (B2) — Two independent exits

## Scenario

```
            exit_north
                |  4 min
             north_a
                |  2 min
             village
                |  3 min
              south_b
                |  6 min
            exit_south
```

## Derivation

The graph is a tree, so each exit has exactly one simple path from the village:

```
village - north_a - exit_north      2 + 4 = 6 min
village - south_b - exit_south      3 + 6 = 9 min
```

Because a tree has no cycles, **every** edge is a bridge and every internal node
is an articulation point — including the village itself, whose removal separates
the two branches.

None of that makes the community single-threaded. Egress fails only when the
village can reach *no* exit, and that requires removing both `north_a` and
`south_b`. The minimum internal node cut is therefore

```
{north_a, south_b}   size 2
```

and by Menger's theorem there are 2 internally node-disjoint egress paths.

## The trap

An implementation that reasons "the graph has articulation points, therefore
there is a single evacuation path" gets this case exactly backwards. So does one
that reports "the village is an articulation point" as an egress risk: the
village is the origin, and its removal is not an evacuation scenario.

The right question is not *is there an articulation point?* but *what is the
smallest set of non-terminal nodes that separates the population from every
destination?* That is the quantity this benchmark pins, and it is 2 here versus
1 in WG-BM-005 on a graph that also has articulation points.

## Expected

| Quantity | Value |
|---|---|
| articulation points | `[north_a, south_b, village]` (non-empty!) |
| minimum internal node cut | 2 |
| node-disjoint egress paths | 2 |
| single point of failure | `false` |
| nearest reachable exit | `exit_north`, 6 min |
