# WG-BM-007 (B3) — Disconnected shelter

## Scenario

```
village (0, 0) ----2 min---- a (1000, 0) ----4 min---- refuge_north (3000, 0)

        shelter_island (0, 500)        <- no incident road edge
```

`shelter_island` is a real place with a real capacity record. It is 500 m from
the village. There is no bridge in the road network.

## Derivation

By straight-line distance:

```
shelter_island   500 m
refuge_north    3000 m
```

so the Euclidean-nearest destination is `shelter_island`, six times closer.

By road: `shelter_island` has degree 0, hence zero simple paths from the
village, hence it is in its own connected component. The only reachable
destination is `refuge_north` at `2 + 4 = 6` minutes, and it must be selected.

## Why this benchmark exists

Destination selection is frequently implemented as a spatial nearest-neighbour
query against a facility table, because that table is the thing that exists and
the road graph is the thing that is awkward. The result is a plan that routes
people to a shelter across a river, a canyon, or a closed military boundary. The
failure is invisible in aggregate statistics — mean distance to shelter improves
— and catastrophic for the individual sent there.

The mutation `euclidean_destination` injects exactly this bug and this benchmark
is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| connected components | 2 |
| reachable destinations | `[refuge_north]` |
| unreachable destinations | `[shelter_island]` |
| Euclidean-nearest destination | `shelter_island` |
| selected destination | `refuge_north` |

## A note on what is *not* asserted

This benchmark does not say a system may never consider off-road movement. It
says that if the road network is the movement model, a node with no edges is not
a destination. A system that models walking must add the walking edges to the
graph — at which point this benchmark's input changes and its expected answer
changes with it.
