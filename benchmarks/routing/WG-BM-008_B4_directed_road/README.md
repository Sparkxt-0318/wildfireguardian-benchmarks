# WG-BM-008 (B4) — Directed road

## Scenario

```
a --3 min--> b --4 min--> c        one-way (contraflow corridor)
a <--2 min--> d                    two-way local road
```

## Derivation

Following edge directions:

* from `a`: reach `b` (3 min), then `c` (7 min), and `d` (2 min);
* from `c`: there is no outgoing edge, so `c` reaches nothing;
* from `d`: the two-way road reaches `a`, and from `a` the corridor reaches `c`.

Hence

```
a -> c   true    (route e_ab + e_bc, 7 min)
c -> a   false
c -> b   false
d -> c   true
```

Reachability is asymmetric. That asymmetry is the entire content of the
benchmark.

## Why it matters operationally

Contraflow is the standard response to a mass evacuation: inbound lanes are
reversed so that every lane carries traffic out. The immediate consequence is
that responder ingress along that corridor becomes impossible, which is exactly
the interaction explored in WG-BM-024 (F3) and WG-BM-027 (F6). A graph loader
that drops the direction flag — a one-line bug, and a very common one, since
most graph libraries default to undirected — will happily route an engine *into*
the fire along a road that is physically full of outbound traffic.

The mutation `allow_reverse_travel` injects that bug and this benchmark is its
declared detector.

## A limitation, stated explicitly

The `articulation_points`, `bridges` and `min_internal_node_cut` fields in the
result document are computed on the **undirected support** of the graph. Those
notions have directed analogues (strong articulation points, directed cuts)
which this suite does not yet implement, so this benchmark does not assert them.
That gap is recorded in `reports/KNOWN_GAPS.md`.

## Expected

| Check | Value |
|---|---|
| `a -> c` | `true` |
| `c -> a` | `false` |
| `c -> b` | `false` |
| `d -> c` | `true` |
| travel time `a -> c` | 7 min |
