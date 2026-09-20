"""Author the B family: road-graph benchmarks (WG-BM-005..008)."""

from __future__ import annotations

from common import report, write_benchmark

SCRIPT = "author_graph.py"
TOLERANCE = {"default": 1.0e-09}


def main() -> None:
    written = []

    # ------------------------------------------------------------------ B1
    written.append(write_benchmark(
        directory="benchmarks/routing/WG-BM-005_B1_single_exit_village",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-005",
            "label": "B1",
            "title": "Single-exit village has exactly one egress route",
            "category": "road_graph",
            "difficulty": "basic",
            "purpose": "Establish the ground truth for a genuine single point of failure: one "
                       "egress route, one articulation node, two bridges.",
            "solver": "graph.connectivity",
            "assumptions": {
                "edges_undirected": True,
                "articulation_definition": "node whose removal increases the number of connected components",
                "cut_excludes_terminals": True,
            },
            "expected_behavior": {
                "articulation_points": ["a"],
                "min_internal_node_cut": 1,
                "single_point_of_failure": True,
            },
            "tolerance": TOLERANCE,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["egress_redundancy_overcount", "articulation_point_error"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
        },
        inputs={
            "network": {
                "description": "Village -- A -- Exit, undirected.",
                "nodes": [
                    {"id": "village", "x": 0.0, "y": 0.0, "role": "population"},
                    {"id": "a", "x": 1000.0, "y": 0.0, "role": "junction"},
                    {"id": "exit", "x": 3000.0, "y": 0.0, "role": "exit"},
                ],
                "edges": [
                    {"id": "e_village_a", "from": "village", "to": "a", "travel_time_min": 2.0},
                    {"id": "e_a_exit", "from": "a", "to": "exit", "travel_time_min": 3.0},
                ],
            },
            "query": {"source": "village", "destinations": ["exit"]},
        },
        expected={
            "benchmark_id": "WG-BM-005",
            "source": "exhaustive_enumeration",
            "derivation": (
                "The graph is a path of three nodes. The only simple walk from village to exit is "
                "village-a-exit, so the egress route count is 1 and the travel time is "
                "2 + 3 = 5 min. Deleting 'a' leaves {village} and {exit} in separate components, "
                "so 'a' is an articulation point; deleting either terminal leaves a connected "
                "two-node graph, so neither is. Both edges are bridges, since a path graph has no "
                "cycles. The smallest set of non-terminal nodes separating village from exit is "
                "{a}, of size 1, so by Menger's theorem there is exactly 1 internally "
                "node-disjoint egress path."
            ),
            "results": {
                "node_count": 3,
                "edge_count": 2,
                "components": 1,
                "articulation_points": ["a"],
                "bridges": ["e_village_a", "e_a_exit"],
                "reachable_destinations": ["exit"],
                "unreachable_destinations": [],
                "selected_destination": "exit",
                "min_internal_node_cut": 1,
                "min_internal_node_cut_set": ["a"],
                "single_point_of_failure": True,
                "node_disjoint_egress_paths": 1,
                "destinations": {
                    "exit": {
                        "reachable": True,
                        "simple_path_count": 1,
                        "min_travel_time_min": 5.0,
                        "euclidean_distance_m": 3000.0,
                    }
                },
            },
            "invariants": [
                {
                    "expression": "r['destinations']['exit']['paths'] == [['e_village_a', 'e_a_exit']]",
                    "description": "the single egress route is enumerated explicitly",
                }
            ],
        },
        readme="""
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
""",
    ))

    # ------------------------------------------------------------------ B2
    written.append(write_benchmark(
        directory="benchmarks/routing/WG-BM-006_B2_two_independent_exits",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-006",
            "label": "B2",
            "title": "Two independent exits: articulation points exist but egress is redundant",
            "category": "road_graph",
            "difficulty": "intermediate",
            "purpose": "Distinguish 'this graph contains articulation points' from 'this "
                       "community has one way out'. The two are routinely conflated.",
            "solver": "graph.connectivity",
            "assumptions": {
                "edges_undirected": True,
                "egress_requires": "reaching any one exit",
                "cut_excludes_terminals": True,
            },
            "expected_behavior": {
                "min_internal_node_cut": 2,
                "single_point_of_failure": False,
                "node_disjoint_egress_paths": 2,
            },
            "tolerance": TOLERANCE,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["false_single_egress_claim", "articulation_point_overinterpretation"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "The expected articulation-point list is deliberately non-empty. A benchmark "
                     "that expected an empty list would be teaching the wrong lesson.",
        },
        inputs={
            "network": {
                "description": "Village with two disjoint corridors, one to each exit.",
                "nodes": [
                    {"id": "village", "x": 0.0, "y": 0.0, "role": "population"},
                    {"id": "north_a", "x": 0.0, "y": 1000.0, "role": "junction"},
                    {"id": "south_b", "x": 0.0, "y": -1000.0, "role": "junction"},
                    {"id": "exit_north", "x": 0.0, "y": 3000.0, "role": "exit"},
                    {"id": "exit_south", "x": 0.0, "y": -4000.0, "role": "exit"},
                ],
                "edges": [
                    {"id": "e_v_na", "from": "village", "to": "north_a", "travel_time_min": 2.0},
                    {"id": "e_na_xn", "from": "north_a", "to": "exit_north", "travel_time_min": 4.0},
                    {"id": "e_v_sb", "from": "village", "to": "south_b", "travel_time_min": 3.0},
                    {"id": "e_sb_xs", "from": "south_b", "to": "exit_south", "travel_time_min": 6.0},
                ],
            },
            "query": {"source": "village", "destinations": ["exit_north", "exit_south"]},
        },
        expected={
            "benchmark_id": "WG-BM-006",
            "source": "exhaustive_enumeration",
            "derivation": (
                "The graph is a tree with the village at the centre of two length-2 branches. "
                "Each exit has exactly one simple path from the village: village-north_a-exit_north "
                "(6 min) and village-south_b-exit_south (9 min). Because the graph is a tree, "
                "every internal node is an articulation point, and the village itself is one as "
                "well, since deleting it separates the two branches. That does NOT mean egress is "
                "fragile. Egress fails only when the village can reach NO exit, which requires "
                "deleting both north_a and south_b: the minimum internal node cut has size 2, so "
                "there are 2 internally node-disjoint egress paths. The nearest reachable exit by "
                "travel time is exit_north at 6 min."
            ),
            "results": {
                "node_count": 5,
                "edge_count": 4,
                "components": 1,
                "articulation_points": ["north_a", "south_b", "village"],
                "bridges": ["e_v_na", "e_na_xn", "e_v_sb", "e_sb_xs"],
                "reachable_destinations": ["exit_north", "exit_south"],
                "unreachable_destinations": [],
                "min_internal_node_cut": 2,
                "min_internal_node_cut_set": ["north_a", "south_b"],
                "single_point_of_failure": False,
                "node_disjoint_egress_paths": 2,
                "reachable_nearest_destination": "exit_north",
                "selected_destination": "exit_north",
                "destinations": {
                    "exit_north": {"reachable": True, "simple_path_count": 1, "min_travel_time_min": 6.0},
                    "exit_south": {"reachable": True, "simple_path_count": 1, "min_travel_time_min": 9.0},
                },
            },
            "invariants": [
                {
                    "expression": "len(r['articulation_points']) > 0 and not r['single_point_of_failure']",
                    "description": "articulation points exist yet egress is not single-threaded",
                }
            ],
        },
        readme="""
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
""",
    ))

    # ------------------------------------------------------------------ B3
    written.append(write_benchmark(
        directory="benchmarks/routing/WG-BM-007_B3_disconnected_shelter",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-007",
            "label": "B3",
            "title": "A shelter that exists geographically but is unreachable by road",
            "category": "road_graph",
            "difficulty": "adversarial",
            "purpose": "The nearest destination in metres is 6x closer than the nearest "
                       "destination by road, and has no road to it at all. A router must not "
                       "select it.",
            "solver": "graph.connectivity",
            "assumptions": {
                "edges_undirected": True,
                "destination_must_be_road_reachable": True,
                "no_off_road_travel": True,
            },
            "expected_behavior": {
                "euclidean_nearest_destination": "shelter_island",
                "reachable_nearest_destination": "refuge_north",
                "selected_destination": "refuge_north",
            },
            "tolerance": TOLERANCE,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["unreachable_destination_selected", "euclidean_proximity_fallacy"],
            "mutations_expected_to_fail": ["euclidean_destination"],
            "hand_checkable": True,
        },
        inputs={
            "network": {
                "description": "Village with one road refuge and one geographically closer shelter "
                               "across an unbridged river.",
                "nodes": [
                    {"id": "village", "x": 0.0, "y": 0.0, "role": "population"},
                    {"id": "a", "x": 1000.0, "y": 0.0, "role": "junction"},
                    {"id": "refuge_north", "x": 3000.0, "y": 0.0, "role": "refuge"},
                    {"id": "shelter_island", "x": 0.0, "y": 500.0, "role": "shelter",
                     "label": "across the river, no bridge in the road network"},
                ],
                "edges": [
                    {"id": "e_village_a", "from": "village", "to": "a", "travel_time_min": 2.0},
                    {"id": "e_a_refuge", "from": "a", "to": "refuge_north", "travel_time_min": 4.0},
                ],
            },
            "query": {"source": "village", "destinations": ["refuge_north", "shelter_island"]},
        },
        expected={
            "benchmark_id": "WG-BM-007",
            "source": "exhaustive_enumeration",
            "derivation": (
                "shelter_island is 500 m from the village in a straight line and refuge_north is "
                "3000 m, so the Euclidean-nearest destination is shelter_island by a factor of 6. "
                "shelter_island has no incident edge, so it forms its own connected component and "
                "the number of simple paths to it is 0. The only reachable destination is "
                "refuge_north, at 2 + 4 = 6 min, and it must be the selection. The graph has two "
                "connected components: {village, a, refuge_north} and {shelter_island}."
            ),
            "results": {
                "node_count": 4,
                "edge_count": 2,
                "components": 2,
                "reachable_destinations": ["refuge_north"],
                "unreachable_destinations": ["shelter_island"],
                "euclidean_nearest_destination": "shelter_island",
                "reachable_nearest_destination": "refuge_north",
                "selected_destination": "refuge_north",
                "destinations": {
                    "refuge_north": {
                        "reachable": True,
                        "simple_path_count": 1,
                        "min_travel_time_min": 6.0,
                        "euclidean_distance_m": 3000.0,
                    },
                    "shelter_island": {
                        "reachable": False,
                        "simple_path_count": 0,
                        "min_travel_time_min": None,
                        "euclidean_distance_m": 500.0,
                    },
                },
            },
            "invariants": [
                {
                    "expression": "r['selected_destination'] not in r['unreachable_destinations']",
                    "description": "the selected destination is never an unreachable one",
                },
                {
                    "expression": "r['euclidean_nearest_destination'] != r['selected_destination']",
                    "description": "the trap is live: proximity and reachability disagree",
                },
            ],
        },
        readme="""
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
""",
    ))

    # ------------------------------------------------------------------ B4
    written.append(write_benchmark(
        directory="benchmarks/routing/WG-BM-008_B4_directed_road",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-008",
            "label": "B4",
            "title": "One-way roads are not traversable in reverse",
            "category": "road_graph",
            "difficulty": "basic",
            "purpose": "A contraflow corridor is directed. Reachability must be asymmetric: the "
                       "outbound trip exists, the return trip does not.",
            "solver": "graph.connectivity",
            "assumptions": {
                "directed_edges_respected": True,
                "contraflow_is_one_way": True,
            },
            "expected_behavior": {
                "reachability_checks": {"a->c": True, "c->a": False},
            },
            "tolerance": TOLERANCE,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["direction_semantics_lost", "impossible_reverse_travel"],
            "mutations_expected_to_fail": ["allow_reverse_travel"],
            "hand_checkable": True,
            "notes": "The minimum-cut and articulation figures in the result document are computed "
                     "on the undirected support of the graph and are not asserted here; see the "
                     "README for why.",
        },
        inputs={
            "network": {
                "description": "One-way contraflow corridor a->b->c, plus a two-way local road a--d.",
                "nodes": [
                    {"id": "a", "x": 0.0, "y": 0.0, "role": "population"},
                    {"id": "b", "x": 1000.0, "y": 0.0, "role": "junction"},
                    {"id": "c", "x": 2000.0, "y": 0.0, "role": "exit"},
                    {"id": "d", "x": 0.0, "y": 800.0, "role": "junction"},
                ],
                "edges": [
                    {"id": "e_ab", "from": "a", "to": "b", "directed": True, "travel_time_min": 3.0},
                    {"id": "e_bc", "from": "b", "to": "c", "directed": True, "travel_time_min": 4.0},
                    {"id": "e_ad", "from": "a", "to": "d", "directed": False, "travel_time_min": 2.0},
                ],
            },
            "query": {
                "source": "a",
                "destinations": ["c", "d"],
                "reverse_reachability": [
                    {"from": "a", "to": "c"},
                    {"from": "c", "to": "a"},
                    {"from": "d", "to": "c"},
                    {"from": "c", "to": "b"},
                ],
            },
        },
        expected={
            "benchmark_id": "WG-BM-008",
            "source": "exhaustive_enumeration",
            "derivation": (
                "Edges e_ab and e_bc are one-way in the stated direction; e_ad is two-way. "
                "Following directions only: from a you can reach b, c (via b) and d, so a->c is "
                "true with the single route e_ab+e_bc taking 3 + 4 = 7 min. From c there is no "
                "outgoing edge at all, so c reaches nothing: c->a and c->b are both false. From d "
                "the two-way road reaches a, and from a the corridor reaches c, so d->c is true. "
                "Reachability is therefore asymmetric, which is the whole content of the case."
            ),
            "results": {
                "node_count": 4,
                "edge_count": 3,
                "reachable_destinations": ["c", "d"],
                "unreachable_destinations": [],
                "reachability_checks": {
                    "a->c": True,
                    "c->a": False,
                    "d->c": True,
                    "c->b": False,
                },
                "destinations": {
                    "c": {"reachable": True, "simple_path_count": 1, "min_travel_time_min": 7.0},
                    "d": {"reachable": True, "simple_path_count": 1, "min_travel_time_min": 2.0},
                },
            },
            "invariants": [
                {
                    "expression": "r['reachability_checks']['a->c'] and not r['reachability_checks']['c->a']",
                    "description": "reachability is asymmetric across the one-way corridor",
                }
            ],
        },
        readme="""
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
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
