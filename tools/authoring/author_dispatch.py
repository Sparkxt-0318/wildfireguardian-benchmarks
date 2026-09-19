"""Author the F family: assisted-dispatch benchmarks (WG-BM-022..027)."""

from __future__ import annotations

from common import report, write_benchmark

SCRIPT = "author_dispatch.py"
TOLERANCE = {"default": 1.0e-06}


def base_network() -> dict:
    """The F1/F2 network: base --5--> resident --5--> refuge, egress closes at 20."""
    return {
        "description": "One base, one resident, one refuge. The egress road is closed by the "
                       "hazard at minute 20; the ingress road stays open to minute 30.",
        "nodes": [
            {"id": "base", "x": -4000.0, "y": 0.0, "role": "responder_base"},
            {"id": "resident", "x": 0.0, "y": 0.0, "role": "assisted_resident",
             "hazard_arrival_min": 25.0},
            {"id": "refuge", "x": 4000.0, "y": 0.0, "role": "refuge"},
        ],
        "edges": [
            {"id": "e_base_resident", "from": "base", "to": "resident",
             "travel_time_min": 5.0, "open_intervals": [[0.0, 30.0]]},
            {"id": "e_resident_refuge", "from": "resident", "to": "refuge",
             "travel_time_min": 5.0, "open_intervals": [[0.0, 20.0]],
             "note": "hazard closes the egress road at minute 20"},
        ],
    }


def main() -> None:
    written = []

    # ------------------------------------------------------------------ F1
    written.append(write_benchmark(
        directory="benchmarks/dispatch/WG-BM-022_F1_basic_round_trip",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-022",
            "label": "F1",
            "title": "Latest feasible dispatch for a basic assisted round trip",
            "category": "assisted_dispatch",
            "difficulty": "basic",
            "purpose": "The canonical assisted-dispatch arithmetic: ingress, pickup and egress "
                       "must all complete before their respective deadlines, and the latest "
                       "dispatch time follows by subtraction.",
            "solver": "dispatch.mission_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "waiting": False,
                "deterministic_hazard": True,
                "pickup_min": 5,
                "single_responder": True,
                "responder_safety_not_modelled": True,
            },
            "expected_behavior": {
                "latest_feasible_dispatch_min": 5.0,
                "feasible_interval_count": 1,
                "monotone_feasibility": True,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["service_time_ignored", "mid_edge_hazard", "dispatch_deadline_error"],
            "mutations_expected_to_fail": ["ignore_pickup_duration", "edge_entry_time_only"],
            "hand_checkable": True,
        },
        inputs={
            "network": base_network(),
            "mission": {
                "resident": "resident",
                "bases": ["base"],
                "destinations": ["refuge"],
                "pickup_min": 5.0,
                "allow_waiting": False,
                "dispatch_horizon_min": 40.0,
                "dispatch_step_min": 0.25,
                "dispatch_probes": [
                    {"id": "p00", "dispatch_min": 0.0},
                    {"id": "p05", "dispatch_min": 5.0},
                    {"id": "p06", "dispatch_min": 6.0},
                ],
            },
        },
        expected={
            "benchmark_id": "WG-BM-022",
            "source": "hand_derivation",
            "derivation": (
                "Let d be the dispatch time. The responder reaches the resident at d + 5 and the "
                "pickup finishes at d + 10. Three constraints apply. "
                "(1) Ingress: the interval [d, d + 5] must fit in [0, 30], giving d <= 25. "
                "(2) Resident tenability: the pickup must finish by minute 25, giving "
                "d + 10 <= 25, i.e. d <= 15. "
                "(3) Egress: departure is at d + 10 and arrival at d + 15, and the interval "
                "[d + 10, d + 15] must fit in [0, 20], giving d + 15 <= 20, i.e. d <= 5. "
                "The binding constraint is the egress closure, so the latest feasible dispatch is "
                "d = 5 and the feasible set is the single interval [0, 5]. At d = 0 the refuge is "
                "reached at 15; at d = 5 it is reached at exactly 20, with zero slack; at d = 6 "
                "the egress traversal would run to 21 and the mission fails at the egress stage."
            ),
            "results": {
                "resident": "resident",
                "resident_deadline_min": 25.0,
                "feasible_intervals": [[0.0, 5.0]],
                "feasible_interval_count": 1,
                "latest_feasible_dispatch_min": 5.0,
                "earliest_feasible_dispatch_min": 0.0,
                "monotone_feasibility": True,
                "scalar_latest_sufficient": True,
                "infeasible_dispatch_below_latest_min": None,
                "best_base": "base",
                "latest_dispatch_by_base": {"base": 5.0},
                "probes": {
                    "p00": {
                        "success": True,
                        "base": "base",
                        "destination": "refuge",
                        "arrival_min": 15.0,
                        "feasible_bases": ["base"],
                    },
                    "p05": {
                        "success": True,
                        "base": "base",
                        "destination": "refuge",
                        "arrival_min": 20.0,
                    },
                    "p06": {"success": False, "failure_stage": "egress", "arrival_min": None},
                },
            },
            "invariants": [
                {
                    "expression": "r['feasible_intervals'][0][0] == 0.0",
                    "description": "dispatching immediately is feasible",
                },
                {
                    "expression": "abs(r['latest_feasible_dispatch_min'] - 5.0) < 1e-6",
                    "description": "the latest dispatch time is exactly 5 minutes",
                },
            ],
        },
        readme="""
# WG-BM-022 (F1) — Basic round trip

## Scenario

```
base --5 min--> resident --[pickup 5 min]--> --5 min--> refuge
```

* ingress road open on `[0, 30]`
* egress road open on `[0, 20]` — the hazard closes it at minute 20
* the resident's location becomes untenable at minute 25
* waiting is not permitted; traversals obey WG-SEM-1 (interval safety)

## Derivation

Let `d` be the dispatch time.

```
arrive at resident   = d + 5
pickup complete      = d + 10
depart for refuge    = d + 10
arrive at refuge     = d + 15
```

Three constraints:

| # | Constraint | Algebra | Bound |
|---|---|---|---|
| 1 | ingress traversal inside `[0, 30]` | `d + 5 <= 30` | `d <= 25` |
| 2 | pickup finishes before the resident's location is untenable | `d + 10 <= 25` | `d <= 15` |
| 3 | egress traversal inside `[0, 20]` | `d + 15 <= 20` | **`d <= 5`** |

The binding constraint is the egress closure.

```
latest feasible dispatch = 5 min
feasible set             = [0, 5]
```

| Dispatch | Arrive resident | Pickup done | Arrive refuge | Outcome |
|---|---|---|---|---|
| 0 | 5 | 10 | 15 | success, 5 min slack |
| 5 | 10 | 15 | 20 | success, **zero slack** |
| 6 | 11 | 16 | 21 | fails at egress |

## What this catches

**Ignoring the pickup.** Drop the 5-minute pickup and the arithmetic becomes
`d + 10 <= 20`, giving a latest dispatch of 10 minutes — twice the truth. A
dispatcher acting on that number sends the crew at minute 8 and the resident is
still being loaded when the road closes. This is the `ignore_pickup_duration`
mutation. On-scene time is the single most commonly omitted term in assisted
evacuation models, because it is the one term that is not a property of the
road network.

**Entry-time-only edge safety.** Under the naive rule the egress constraint
becomes `d + 10 <= 20`, again giving 10. The two bugs are independent and
produce the same wrong number here, which is itself worth knowing: a single
benchmark cannot distinguish them, and WG-BM-023 is needed to separate them.

## What this deliberately does not model

The responder's own survival, refuelling, crew endurance, the possibility of
more than one resident per vehicle, and any uncertainty whatsoever. Those belong
in later benchmarks; this one exists so that the arithmetic can be checked in
thirty seconds on paper.
""",
    ))

    # ------------------------------------------------------------------ F2
    written.append(write_benchmark(
        directory="benchmarks/dispatch/WG-BM-023_F2_pickup_sensitivity",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-023",
            "label": "F2",
            "title": "Latest dispatch moves one-for-one with pickup duration",
            "category": "assisted_dispatch",
            "difficulty": "basic",
            "purpose": "Sweep the on-scene pickup duration and check that the latest feasible "
                       "dispatch decreases by exactly the same amount, until the mission becomes "
                       "impossible at any dispatch time.",
            "solver": "dispatch.mission_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "waiting": False,
                "pickup_values_min": "2, 5, 10, 15",
            },
            "expected_behavior": {
                "latest_dispatch_by_pickup": {"2": 8.0, "5": 5.0, "10": 0.0, "15": None},
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["service_time_ignored", "sensitivity_flat_to_service_time"],
            "mutations_expected_to_fail": ["ignore_pickup_duration"],
            "hand_checkable": True,
            "notes": "With the pickup ignored every row collapses to the same answer, which is "
                     "what makes this a sharper detector than WG-BM-022 alone.",
        },
        inputs={
            "network": base_network(),
            "mission": {
                "resident": "resident",
                "bases": ["base"],
                "destinations": ["refuge"],
                "pickup_min": [2.0, 5.0, 10.0, 15.0],
                "allow_waiting": False,
                "dispatch_horizon_min": 40.0,
                "dispatch_step_min": 0.25,
                "dispatch_probes": [
                    {"id": "p_short_pickup", "dispatch_min": 8.0, "pickup_min": 2.0},
                    {"id": "p_long_pickup", "dispatch_min": 8.0, "pickup_min": 10.0},
                ],
            },
        },
        expected={
            "benchmark_id": "WG-BM-023",
            "source": "hand_derivation",
            "derivation": (
                "With pickup duration p the refuge is reached at d + 5 + p + 5 = d + p + 10, and "
                "the binding egress constraint is d + p + 10 <= 20, i.e. d <= 10 - p. "
                "p = 2 gives d <= 8; p = 5 gives d <= 5; p = 10 gives d <= 0, so only an "
                "instantaneous dispatch works; p = 15 gives d <= -5, which is impossible, so the "
                "feasible set is empty and the mission cannot be completed at any dispatch time. "
                "The resident tenability constraint d + p <= 15 is slacker than the egress "
                "constraint for every p in this sweep, so it never binds. The latest dispatch "
                "therefore falls one minute for every extra minute of on-scene time, a slope of "
                "exactly -1."
            ),
            "results": {
                "pickup_values_min": [2.0, 5.0, 10.0, 15.0],
                "latest_dispatch_by_pickup": {"2": 8.0, "5": 5.0, "10": 0.0, "15": None},
                "feasible_by_pickup": {"2": True, "5": True, "10": True, "15": False},
                "latest_feasible_dispatch_min": 8.0,
                "probes": {
                    "p_short_pickup": {
                        "success": True,
                        "destination": "refuge",
                        "arrival_min": 20.0,
                    },
                    "p_long_pickup": {"success": False, "failure_stage": "egress"},
                },
            },
            "invariants": [
                {
                    "expression": "r['latest_dispatch_by_pickup']['2'] - r['latest_dispatch_by_pickup']['5'] == 3.0",
                    "description": "3 extra minutes of pickup cost exactly 3 minutes of dispatch latitude",
                },
                {
                    "expression": "r['latest_dispatch_by_pickup']['5'] - r['latest_dispatch_by_pickup']['10'] == 5.0",
                    "description": "5 extra minutes of pickup cost exactly 5 minutes of dispatch latitude",
                },
                {
                    "expression": "r['feasible_by_pickup']['15'] is False",
                    "description": "a 15 minute pickup makes the mission impossible at any dispatch time",
                },
            ],
        },
        readme="""
# WG-BM-023 (F2) — Pickup sensitivity

## Scenario

The WG-BM-022 network, with the on-scene pickup duration swept over
`p in {2, 5, 10, 15}` minutes.

## Derivation

```
arrive at refuge = d + 5 + p + 5 = d + p + 10
egress closes at 20   ->   d + p + 10 <= 20   ->   d <= 10 - p
```

The resident tenability constraint is `d + p <= 15`, which is slacker than the
egress constraint for every `p` in the sweep, so it never binds.

| Pickup `p` | Latest dispatch `10 - p` | Feasible at all? |
|---|---|---|
| 2 min | **8 min** | yes |
| 5 min | **5 min** | yes |
| 10 min | **0 min** | only an instantaneous dispatch |
| 15 min | `-5 min` | **no** |

The slope is exactly `-1`: every extra minute spent on scene costs one minute of
dispatch latitude. At `p = 10` the feasible set collapses to the single point
`{0}`. At `p = 15` it is empty — the mission cannot be completed however early
the crew leaves, and the correct answer is "impossible", not "dispatch now".

## Why the sweep, and not just one row

A single row cannot distinguish a model that handles pickup correctly from one
that ignores it, because both produce *some* number and the number looks
reasonable. The sweep pins the **derivative**. Under the
`ignore_pickup_duration` mutation every row collapses to the same answer,
`d <= 10`, and the slope becomes zero. A flat sensitivity to on-scene time is
the signature of the bug, and it is visible even when the absolute values happen
to look plausible.

This matters operationally because the pickup duration is the term that varies
most between residents: a mobile adult is two minutes, a bed-bound resident
needing two crew and a stretcher is twenty. A system whose dispatch advice does
not move with that input is not modelling assisted evacuation at all.

## The feasibility cliff

The transition from `p = 10` (feasible only at `d = 0`) to `p = 15` (never
feasible) is the operationally important one. It is the point at which the right
answer stops being "go now" and becomes "this resident cannot be reached by this
route from this base — find another plan". A system that always returns a
dispatch time, however tight, cannot express that.
""",
    ))

    # ------------------------------------------------------------------ F3
    written.append(write_benchmark(
        directory="benchmarks/dispatch/WG-BM-024_F3_two_responder_bases",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-024",
            "label": "F3",
            "title": "The nearest base is not the right base when its corridor closes first",
            "category": "assisted_dispatch",
            "difficulty": "intermediate",
            "purpose": "Base selection must consider the ingress corridor's closure time, not "
                       "just travel distance. The far base gives 5 more minutes of dispatch "
                       "latitude.",
            "solver": "dispatch.mission_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "waiting": False,
                "pickup_min": 5,
                "one_vehicle_per_base": True,
            },
            "expected_behavior": {
                "latest_dispatch_by_base": {"base_near": 2.0, "base_far": 7.0},
                "best_base": "base_far",
                "nearest_base": "base_near",
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["greedy_base_selection", "ingress_corridor_ignored"],
            "mutations_expected_to_fail": ["nearest_base_only"],
            "hand_checkable": True,
        },
        inputs={
            "network": {
                "description": "Two responder bases. The near base's corridor is closed by the "
                               "hazard at minute 6; the far base's corridor stays open.",
                "nodes": [
                    {"id": "base_near", "x": 2000.0, "y": 0.0, "role": "responder_base"},
                    {"id": "base_far", "x": 8000.0, "y": 0.0, "role": "responder_base"},
                    {"id": "resident", "x": 0.0, "y": 0.0, "role": "assisted_resident",
                     "hazard_arrival_min": 40.0},
                    {"id": "refuge", "x": 0.0, "y": -5000.0, "role": "refuge"},
                ],
                "edges": [
                    {"id": "e_near_resident", "from": "base_near", "to": "resident",
                     "travel_time_min": 4.0, "open_intervals": [[0.0, 6.0]],
                     "note": "short corridor, closed by the hazard at minute 6"},
                    {"id": "e_far_resident", "from": "base_far", "to": "resident",
                     "travel_time_min": 10.0, "open_intervals": [[0.0, 60.0]],
                     "note": "long corridor from the far side, stays open"},
                    {"id": "e_resident_refuge", "from": "resident", "to": "refuge",
                     "travel_time_min": 8.0, "open_intervals": [[0.0, 30.0]]},
                ],
            },
            "mission": {
                "resident": "resident",
                "bases": ["base_near", "base_far"],
                "destinations": ["refuge"],
                "pickup_min": 5.0,
                "allow_waiting": False,
                "dispatch_horizon_min": 40.0,
                "dispatch_step_min": 0.25,
                "dispatch_probes": [
                    {"id": "p00", "dispatch_min": 0.0},
                    {"id": "p05", "dispatch_min": 5.0},
                    {"id": "p08", "dispatch_min": 8.0},
                ],
            },
        },
        expected={
            "benchmark_id": "WG-BM-024",
            "source": "hand_derivation",
            "derivation": (
                "From the near base the ingress interval is [d, d + 4], which must fit inside "
                "[0, 6], so d <= 2. Its egress constraint, [d + 9, d + 17] inside [0, 30], gives "
                "d <= 13 and does not bind. The near base therefore offers latest dispatch 2. "
                "From the far base the ingress interval [d, d + 10] inside [0, 60] gives d <= 50, "
                "and the egress interval [d + 15, d + 23] inside [0, 30] gives d <= 7. The far "
                "base therefore offers latest dispatch 7, five minutes more than the near base, "
                "despite a 6 minute longer drive. Overall the feasible dispatch set is [0, 7]. "
                "At d = 0 both bases work and the near one arrives sooner (17 versus 23), so it "
                "is selected. At d = 5 only the far base works, arriving at 28. At d = 8 neither "
                "works."
            ),
            "results": {
                "bases_considered": ["base_near", "base_far"],
                "nearest_base": "base_near",
                "latest_dispatch_by_base": {"base_near": 2.0, "base_far": 7.0},
                "best_base": "base_far",
                "feasible_intervals": [[0.0, 7.0]],
                "latest_feasible_dispatch_min": 7.0,
                "monotone_feasibility": True,
                "probes": {
                    "p00": {
                        "success": True,
                        "base": "base_near",
                        "arrival_min": 17.0,
                        "feasible_bases": ["base_far", "base_near"],
                    },
                    "p05": {
                        "success": True,
                        "base": "base_far",
                        "arrival_min": 28.0,
                        "feasible_bases": ["base_far"],
                    },
                    "p08": {"success": False, "feasible_bases": []},
                },
            },
            "invariants": [
                {
                    "expression": "r['best_base'] != r['nearest_base']",
                    "description": "the base offering the most dispatch latitude is not the nearest one",
                },
                {
                    "expression": "r['probes']['p05']['feasible_bases'] == ['base_far']",
                    "description": "at minute 5 only the far base can still complete the mission",
                },
            ],
        },
        readme="""
# WG-BM-024 (F3) — Two responder bases

## Scenario

```
base_near (2 km) --4 min, corridor open [0, 6]---> resident --8 min--> refuge
base_far  (8 km) --10 min, corridor open [0, 60]-/          egress open [0, 30]
```

Pickup 5 minutes. The resident's location is tenable to minute 40.

## Derivation

**From the near base**

```
ingress: [d, d + 4]   inside [0, 6]    ->  d <= 2     <- binds
egress:  [d + 9, d + 17] inside [0, 30] ->  d <= 13
latest dispatch = 2 min
```

**From the far base**

```
ingress: [d, d + 10]  inside [0, 60]   ->  d <= 50
egress:  [d + 15, d + 23] inside [0, 30] -> d <= 7    <- binds
latest dispatch = 7 min
```

The far base is 6 minutes further away and offers **5 more minutes** of dispatch
latitude, because the near base's short corridor is the first thing the fire
closes. Overall the feasible dispatch set is `[0, 7]`.

| Dispatch | Near base | Far base | Selected | Arrival |
|---|---|---|---|---|
| 0 | feasible | feasible | near (arrives sooner) | 17 |
| 5 | **infeasible** | feasible | far | 28 |
| 8 | infeasible | infeasible | — | — |

## Two distinct decisions

This benchmark separates two things that are easy to conflate:

* **Which base to use at a given moment** — at `d = 0` the near base is right,
  because it delivers the resident 6 minutes sooner and every minute of slack
  matters.
* **How long the option stays open** — the near base's option expires at minute
  2, the far base's at minute 7. Planning the *deadline* from the near base
  understates the community's remaining decision time by 5 minutes; planning it
  from the far base and then dispatching from the near base at minute 5 sends a
  crew into a closed corridor.

A correct system reports both, keyed by base. The `nearest_base_only` mutation
considers only the geographically nearest base, reports a latest dispatch of 2,
and declares the mission impossible at minute 5 when in fact it is
straightforward. This benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| latest dispatch, near base | 2 min |
| latest dispatch, far base | 7 min |
| best base | `base_far` |
| nearest base | `base_near` |
| feasible bases at `d = 5` | `[base_far]` |
""",
    ))

    # ------------------------------------------------------------------ F4
    written.append(write_benchmark(
        directory="benchmarks/dispatch/WG-BM-025_F4_alternate_destination",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-025",
            "label": "F4",
            "title": "The right destination changes with the dispatch time",
            "category": "assisted_dispatch",
            "difficulty": "intermediate",
            "purpose": "A near refuge that closes early and a far shelter that stays open. The "
                       "correct destination is a function of when the mission starts.",
            "solver": "dispatch.mission_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "waiting": False,
                "pickup_min": 5,
                "destination_choice": "earliest arrival among feasible destinations",
            },
            "expected_behavior": {
                "latest_feasible_dispatch_min": 15.0,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["static_destination_assignment", "destination_deadline_ignored"],
            "mutations_expected_to_fail": ["ignore_pickup_duration", "edge_entry_time_only"],
            "hand_checkable": True,
        },
        inputs={
            "network": {
                "description": "A near refuge whose approach closes at minute 18 and a distant "
                               "shelter that remains available.",
                "nodes": [
                    {"id": "base", "x": -3000.0, "y": 0.0, "role": "responder_base"},
                    {"id": "resident", "x": 0.0, "y": 0.0, "role": "assisted_resident",
                     "hazard_arrival_min": 25.0},
                    {"id": "refuge_close", "x": 2000.0, "y": 0.0, "role": "refuge"},
                    {"id": "shelter_far", "x": 15000.0, "y": 0.0, "role": "shelter"},
                ],
                "edges": [
                    {"id": "e_base_resident", "from": "base", "to": "resident",
                     "travel_time_min": 5.0, "open_intervals": [[0.0, 60.0]]},
                    {"id": "e_resident_refuge", "from": "resident", "to": "refuge_close",
                     "travel_time_min": 5.0, "open_intervals": [[0.0, 18.0]],
                     "note": "short hop, but the hazard closes this approach at minute 18"},
                    {"id": "e_resident_shelter", "from": "resident", "to": "shelter_far",
                     "travel_time_min": 20.0, "open_intervals": [[0.0, 100.0]],
                     "note": "long haul away from the fire, stays open"},
                ],
            },
            "mission": {
                "resident": "resident",
                "bases": ["base"],
                "destinations": ["refuge_close", "shelter_far"],
                "pickup_min": 5.0,
                "allow_waiting": False,
                "dispatch_horizon_min": 40.0,
                "dispatch_step_min": 0.25,
                "dispatch_probes": [
                    {"id": "p00", "dispatch_min": 0.0},
                    {"id": "p06", "dispatch_min": 6.0},
                    {"id": "p15", "dispatch_min": 15.0},
                    {"id": "p20", "dispatch_min": 20.0},
                ],
            },
        },
        expected={
            "benchmark_id": "WG-BM-025",
            "source": "hand_derivation",
            "derivation": (
                "Pickup finishes at d + 10 in every case. "
                "To the near refuge: the egress interval [d + 10, d + 15] must fit in [0, 18], so "
                "d <= 3, and the arrival is d + 15. "
                "To the far shelter: [d + 10, d + 30] inside [0, 100] gives d <= 70, and the "
                "arrival is d + 30. "
                "The resident's location is untenable after minute 25, so the pickup constraint "
                "d + 10 <= 25 gives d <= 15, which is what limits the shelter option. "
                "Overall the mission is feasible exactly for d in [0, 15]. "
                "At d = 0 both destinations work and the refuge arrives first (15 versus 30), so "
                "it is chosen. At d = 6 the refuge is unreachable (its approach would be occupied "
                "to minute 21) and the shelter is chosen, arriving at 36. At d = 15 only the "
                "shelter remains, arriving at 45 with the pickup finishing exactly on the "
                "tenability deadline. At d = 20 the pickup would finish at 30, five minutes after "
                "the resident's location is untenable, and the mission fails at the pickup stage."
            ),
            "results": {
                "resident_deadline_min": 25.0,
                "feasible_intervals": [[0.0, 15.0]],
                "latest_feasible_dispatch_min": 15.0,
                "monotone_feasibility": True,
                "probes": {
                    "p00": {"success": True, "destination": "refuge_close", "arrival_min": 15.0},
                    "p06": {"success": True, "destination": "shelter_far", "arrival_min": 36.0},
                    "p15": {"success": True, "destination": "shelter_far", "arrival_min": 45.0},
                    "p20": {"success": False, "failure_stage": "pickup"},
                },
            },
            "invariants": [
                {
                    "expression": "r['probes']['p00']['destination'] != r['probes']['p06']['destination']",
                    "description": "the correct destination changes with the dispatch time",
                },
                {
                    "expression": "r['probes']['p20']['failure_stage'] == 'pickup'",
                    "description": "late dispatch fails because the resident's location is untenable, not because of the roads",
                },
            ],
        },
        readme="""
# WG-BM-025 (F4) — Alternate destination

## Scenario

```
                          /--5 min, open [0, 18]--> refuge_close   (2 km)
base --5 min--> resident -
                          \\--20 min, open [0, 100]-> shelter_far  (15 km)
```

Pickup 5 minutes. The resident's location is untenable after minute 25.

## Derivation

Pickup always finishes at `d + 10`.

| Destination | Egress constraint | Bound on `d` | Arrival |
|---|---|---|---|
| `refuge_close` | `[d+10, d+15]` inside `[0, 18]` | `d <= 3` | `d + 15` |
| `shelter_far` | `[d+10, d+30]` inside `[0, 100]` | `d <= 70` | `d + 30` |
| (either) | pickup by minute 25: `d + 10 <= 25` | `d <= 15` | — |

So the mission is feasible exactly on `d in [0, 15]`, and the destination
changes inside that window:

| Dispatch | Refuge | Shelter | Chosen | Arrival |
|---|---|---|---|---|
| 0 | feasible | feasible | **refuge_close** (arrives 15 vs 30) | 15 |
| 6 | infeasible | feasible | **shelter_far** | 36 |
| 15 | infeasible | feasible | **shelter_far** | 45 |
| 20 | — | — | none: pickup would end at 30 > 25 | — |

## What this is about

Destination assignment is often static: each address is pre-assigned to its
designated refuge during planning, and the runtime system routes there. That
assignment is correct here for the first three minutes and wrong afterwards.
From minute 4 the pre-assigned refuge is a trap — its approach is occupied by
the hazard before the vehicle can clear it — while a perfectly good shelter
exists 15 km away.

Note also **which constraint binds at each end** of the window. Early failures
are road failures; the last failure, at `d = 20`, is a *resident* failure: the
crew could still drive the route, but the person they are collecting cannot
survive at the pickup point long enough to be collected. Reporting "no feasible
route" there would be diagnostically wrong, and the result document distinguishes
the two with `failure_stage`.

## Expected

| Quantity | Value |
|---|---|
| feasible dispatch window | `[0, 15]` |
| destination at `d = 0` | `refuge_close`, arrive 15 |
| destination at `d = 6` | `shelter_far`, arrive 36 |
| failure stage at `d = 20` | `pickup` |
""",
    ))

    # ------------------------------------------------------------------ F5
    written.append(write_benchmark(
        directory="benchmarks/dispatch/WG-BM-026_F5_non_monotone_feasibility",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-026",
            "label": "F5",
            "title": "Dispatch feasibility is feasible, then infeasible, then feasible again",
            "category": "assisted_dispatch",
            "difficulty": "adversarial",
            "purpose": "Prove that a single scalar latest-dispatch-time is not sufficient. The "
                       "feasible set here is two disjoint intervals and dispatching at minute 10 "
                       "- comfortably below the latest feasible time of 34 - fails.",
            "solver": "dispatch.mission_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "waiting": False,
                "pickup_min": 4,
                "corridor_reopens": True,
            },
            "expected_behavior": {
                "feasible_intervals": [[0.0, 4.0], [20.0, 34.0]],
                "monotone_feasibility": False,
                "scalar_latest_sufficient": False,
                "infeasible_dispatch_below_latest_min": 5.0,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_enumeration",
            "detects": ["non_monotone_feasibility", "scalar_deadline_insufficient"],
            "mutations_expected_to_fail": ["monotone_dispatch_assumption"],
            "hand_checkable": True,
            "notes": "This is the single most important benchmark in the F family. If a system "
                     "can only express one number, it cannot express this scenario correctly.",
        },
        inputs={
            "network": {
                "description": "The ingress corridor is overrun by the flaming front between "
                               "minutes 10 and 20 and is reopened at 20 once the front has passed.",
                "nodes": [
                    {"id": "base", "x": -6000.0, "y": 0.0, "role": "responder_base"},
                    {"id": "resident", "x": 0.0, "y": 0.0, "role": "assisted_resident",
                     "hazard_arrival_min": 90.0},
                    {"id": "refuge", "x": 6000.0, "y": 0.0, "role": "refuge"},
                ],
                "edges": [
                    {"id": "e_base_resident", "from": "base", "to": "resident",
                     "travel_time_min": 6.0,
                     "open_intervals": [[0.0, 10.0], [20.0, 40.0]],
                     "note": "front crosses the corridor between 10 and 20; reopened at 20"},
                    {"id": "e_resident_refuge", "from": "resident", "to": "refuge",
                     "travel_time_min": 10.0, "open_intervals": [[0.0, 60.0]]},
                ],
            },
            "mission": {
                "resident": "resident",
                "bases": ["base"],
                "destinations": ["refuge"],
                "pickup_min": 4.0,
                "allow_waiting": False,
                "dispatch_horizon_min": 50.0,
                "dispatch_step_min": 1.0,
                "dispatch_probes": [
                    {"id": "p02", "dispatch_min": 2.0},
                    {"id": "p10", "dispatch_min": 10.0},
                    {"id": "p25", "dispatch_min": 25.0},
                    {"id": "p36", "dispatch_min": 36.0},
                ],
            },
        },
        expected={
            "benchmark_id": "WG-BM-026",
            "source": "exhaustive_enumeration",
            "derivation": (
                "The ingress traversal takes 6 minutes and must fit inside one open window of the "
                "corridor. Inside [0, 10] that requires d + 6 <= 10, i.e. d <= 4. Inside [20, 40] "
                "it requires d >= 20 and d + 6 <= 40, i.e. 20 <= d <= 34. No departure in (4, 20) "
                "works: the traversal would either still be in progress when the front arrives or "
                "would start before the road reopens. "
                "The egress leg departs at d + 10 and arrives at d + 20, and [d + 10, d + 20] "
                "inside [0, 60] gives d <= 40, which does not bind. The resident's location is "
                "tenable to minute 90, which also does not bind. "
                "The feasible dispatch set is therefore the union of [0, 4] and [20, 34]: two "
                "disjoint intervals. The latest feasible dispatch is 34, yet dispatching at any "
                "time in (4, 20) - for example at 5, or at 10 - fails. A scalar deadline is "
                "necessarily wrong about that entire 16 minute gap."
            ),
            "results": {
                "feasible_intervals": [[0.0, 4.0], [20.0, 34.0]],
                "feasible_interval_count": 2,
                "latest_feasible_dispatch_min": 34.0,
                "earliest_feasible_dispatch_min": 0.0,
                "monotone_feasibility": False,
                "scalar_latest_sufficient": False,
                "infeasible_dispatch_below_latest_min": 5.0,
                "probes": {
                    "p02": {"success": True, "arrival_min": 22.0},
                    "p10": {"success": False, "failure_stage": "ingress"},
                    "p25": {"success": True, "arrival_min": 45.0},
                    "p36": {"success": False, "failure_stage": "ingress"},
                },
            },
            "invariants": [
                {
                    "expression": "len(r['feasible_intervals']) == 2",
                    "description": "the feasible dispatch set is genuinely two intervals",
                },
                {
                    "expression": "r['infeasible_dispatch_below_latest_min'] < r['latest_feasible_dispatch_min']",
                    "description": "there exists a dispatch time below the latest feasible time that fails",
                },
                {
                    "expression": "r['probes']['p10']['success'] is False and r['probes']['p25']['success'] is True",
                    "description": "feasible, infeasible, feasible as the dispatch time increases",
                },
            ],
        },
        readme="""
# WG-BM-026 (F5) — Non-monotone dispatch feasibility

## Scenario

```
base --6 min, corridor open on [0, 10] and [20, 40]--> resident --10 min--> refuge
```

The flaming front crosses the ingress corridor between minutes 10 and 20. Once
it has passed, the road is reopened at minute 20. Pickup is 4 minutes; the
resident's location is tenable to minute 90; the egress road is open to minute
60.

## Derivation

The 6-minute ingress traversal must fit inside **one** open window:

```
inside [0, 10]:   d + 6 <= 10                ->  0 <= d <= 4
inside [20, 40]:  d >= 20 and d + 6 <= 40    -> 20 <= d <= 34
```

No departure in `(4, 20)` works: it would either leave the vehicle on the road
when the front arrives, or start before the road reopens.

The egress leg departs at `d + 10` and arrives at `d + 20`; `[d+10, d+20]`
inside `[0, 60]` gives `d <= 40`, which does not bind. Tenability does not bind
either.

```
feasible dispatch set = [0, 4]  u  [20, 34]
```

| Dispatch | Outcome | Arrival |
|---|---|---|
| 2 | success | 22 |
| **10** | **fails at ingress** | — |
| 25 | success | 45 |
| 36 | fails at ingress | — |

## Why this is the most important benchmark in the F family

Almost every assisted-evacuation tool in the literature and in practice reports
a **single scalar**: "latest safe dispatch time", "trigger point", "time
remaining". That representation carries an implicit claim — that feasibility is
*monotone*, so that everything before the deadline works and everything after it
does not.

Here the latest feasible dispatch is **34 minutes**, and dispatching at **10
minutes** fails. Any system that reports only `34` will, if believed, send a
crew into a corridor that is on fire, and it will do so while displaying 24
minutes of remaining margin.

The mechanism is not exotic. A corridor being overrun and then reopened is the
normal life cycle of a road in a fire: it is closed while the flaming front
crosses it, and it is usable again behind the front once the fire has moved on.
Any hazard model with re-openings produces non-monotone feasibility somewhere.

## What a correct system must emit

The **set** of feasible dispatch times, not its supremum. Concretely, at least:

```
feasible_intervals: [[0, 4], [20, 34]]
```

and a warning that the scalar summary is unsafe:

```
monotone_feasibility: false
scalar_latest_sufficient: false
infeasible_dispatch_below_latest_min: 5
```

The `monotone_dispatch_assumption` mutation collapses the two intervals into
`[[0, 34]]` — exactly the scalar summary — and this benchmark is its declared
detector.

## A note on the gap counterexample

`infeasible_dispatch_below_latest_min` is reported as `5.0`: the first sampled
dispatch time below the latest feasible time at which the mission fails. Its
exact value depends on the sampling grid (1 minute here), and the benchmark pins
the value produced by that declared grid. The *existence* of such a time is what
matters and is asserted separately as an invariant.
""",
    ))

    # ------------------------------------------------------------------ F6
    written.append(write_benchmark(
        directory="benchmarks/traffic/WG-BM-027_F6_inbound_outbound_conflict",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-027",
            "label": "F6",
            "title": "Responder ingress competes with evacuee egress on one road",
            "category": "traffic",
            "difficulty": "adversarial",
            "purpose": "Without a capacity interaction the mission succeeds with 15 minutes to "
                       "spare; with it, the mission cannot be completed at any dispatch time.",
            "solver": "dispatch.mission_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "waiting": False,
                "pickup_min": 5,
                "evacuation_window_min": "0 to 40",
                "congested_travel_times_are_given": True,
                "queue_dynamics_not_modelled": True,
            },
            "expected_behavior": {
                "feasible_interval_count": 0,
                "capacity_binding": True,
                "latest_feasible_dispatch_min": None,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["capacity_ignored", "free_flow_travel_time_assumed"],
            "mutations_expected_to_fail": ["ignore_congestion"],
            "hand_checkable": True,
        },
        inputs={
            "network": {
                "description": "A single two-lane road serves both the outbound evacuation and "
                               "the inbound responder. During the evacuation window (0 to 40 min) "
                               "inbound travel takes 25 minutes instead of 10 and outbound takes "
                               "15 instead of 10.",
                "nodes": [
                    {"id": "base", "x": -8000.0, "y": 0.0, "role": "responder_base"},
                    {"id": "resident", "x": 0.0, "y": 0.0, "role": "assisted_resident",
                     "hazard_arrival_min": 60.0},
                    {"id": "refuge", "x": -16000.0, "y": 0.0, "role": "refuge"},
                ],
                "edges": [
                    {
                        "id": "e_base_resident",
                        "from": "base",
                        "to": "resident",
                        "free_flow_min": 10.0,
                        "travel_time_profile": [
                            {"depart_from": 0.0, "depart_to": 40.0, "minutes": 25.0},
                            {"depart_from": 40.0, "depart_to": None, "minutes": 10.0},
                        ],
                        "note": "inbound against the evacuation flow",
                    },
                    {
                        "id": "e_resident_refuge",
                        "from": "resident",
                        "to": "refuge",
                        "free_flow_min": 10.0,
                        "travel_time_profile": [
                            {"depart_from": 0.0, "depart_to": 40.0, "minutes": 15.0},
                            {"depart_from": 40.0, "depart_to": None, "minutes": 10.0},
                        ],
                        "note": "outbound in the evacuation queue",
                    },
                ],
            },
            "mission": {
                "resident": "resident",
                "bases": ["base"],
                "destinations": ["refuge"],
                "destination_deadlines": {"refuge": 40.0},
                "pickup_min": 5.0,
                "allow_waiting": False,
                "dispatch_horizon_min": 60.0,
                "dispatch_step_min": 0.5,
                "dispatch_probes": [
                    {"id": "p00", "dispatch_min": 0.0},
                    {"id": "p40", "dispatch_min": 40.0},
                ],
            },
        },
        expected={
            "benchmark_id": "WG-BM-027",
            "source": "hand_derivation",
            "derivation": (
                "The refuge must be reached by minute 40. "
                "Without the capacity interaction every leg runs at free flow: dispatch at d, "
                "reach the resident at d + 10, finish the pickup at d + 15, reach the refuge at "
                "d + 25. That is within the deadline for all d <= 15, and at d = 0 the refuge is "
                "reached at minute 25, fifteen minutes early. "
                "With the capacity interaction, a dispatch at d = 0 travels inbound against the "
                "evacuation flow in 25 minutes, finishes the pickup at 30, departs outbound into "
                "the queue and takes 15 minutes, arriving at 45 - five minutes late. Dispatching "
                "later is worse: any dispatch before 40 keeps the 25 minute inbound leg, and a "
                "dispatch at or after 40 arrives at d + 10 + 5 + 10 = d + 25 >= 65. The mission "
                "is therefore infeasible at every dispatch time, while the free-flow "
                "counterfactual is feasible on [0, 15]. The capacity interaction alone turns a "
                "mission with 15 minutes of slack into an impossible one."
            ),
            "results": {
                "feasible_intervals": [],
                "feasible_interval_count": 0,
                "latest_feasible_dispatch_min": None,
                "capacity_binding": True,
                "free_flow_counterfactual": {
                    "feasible": True,
                    "feasible_intervals": [[0.0, 15.0]],
                    "latest_feasible_dispatch_min": 15.0,
                    "arrival_at_dispatch_zero_min": 25.0,
                    "success_at_dispatch_zero": True,
                },
                "probes": {
                    "p00": {"success": False, "failure_stage": "egress"},
                    "p40": {"success": False, "failure_stage": "egress"},
                },
            },
            "invariants": [
                {
                    "expression": "r['free_flow_counterfactual']['feasible'] and not r['feasible_intervals']",
                    "description": "feasible without capacity, infeasible with it",
                },
                {
                    "expression": "r['free_flow_counterfactual']['arrival_at_dispatch_zero_min'] == 25.0",
                    "description": "the free-flow mission finishes 15 minutes inside the deadline",
                },
            ],
        },
        readme="""
# WG-BM-027 (F6) — Inbound / outbound conflict

## Scenario

One road serves both directions. The community is evacuating outbound between
minutes 0 and 40; the responder must drive inbound along the same road, collect
one resident, and bring them out to a refuge **by minute 40**.

| Leg | Free flow | During the evacuation window |
|---|---|---|
| inbound `base -> resident` | 10 min | **25 min** (against the flow) |
| outbound `resident -> refuge` | 10 min | **15 min** (in the queue) |

Pickup is 5 minutes.

## Derivation

**Without the capacity interaction** (free flow everywhere):

```
d = 0:  reach resident 10, pickup done 15, reach refuge 25   -> 15 minutes of slack
feasible for all d <= 15
```

**With the capacity interaction:**

```
d = 0:  inbound 25 min -> reach resident 25
        pickup 5 min   -> done at 30
        outbound 15 min-> reach refuge 45        -> 5 minutes LATE
```

Dispatching later does not help. Any dispatch before minute 40 still meets the
25-minute inbound leg. A dispatch at or after 40 runs at free flow but arrives at
`d + 25 >= 65`. **The mission is infeasible at every dispatch time.**

```
with capacity:     feasible set = {}            (empty)
without capacity:  feasible set = [0, 15]
```

## What this benchmark is really about

The free-flow model does not get the answer slightly wrong. It reports a mission
with **15 minutes of slack** for a mission that **cannot be done at all**. There
is no dispatch time, no base, and no route that recovers it — the only real
options are to change the traffic plan (contraflow, a held lane, an air asset) or
to accept that this resident cannot be assisted by road during the evacuation.
A planning tool that cannot represent the conflict will never surface that
choice, and the decision will be made implicitly by the first crew that gets
stuck.

This is also why the conflict belongs in the benchmark suite rather than in a
traffic microsimulation. Nothing subtle is being modelled here: two fixed travel
times, taken as given. The point is not to predict congestion accurately, it is
to notice that ingress and egress share a road.

## What is deliberately not modelled

Queue formation and dissipation, shockwave propagation, intersection control,
the effect of the responder vehicle itself on the outbound flow, and any
feedback from the evacuation rate to the travel times. The congested travel
times are **stipulated inputs**, not outputs of a traffic model. A benchmark
that required a queueing model to state its expected answer would no longer be
hand-checkable, which is the property this suite refuses to trade away. Richer
traffic benchmarks are listed in `reports/KNOWN_GAPS.md`.

## Expected

| Quantity | Value |
|---|---|
| feasible dispatch set with capacity | empty |
| feasible dispatch set at free flow | `[0, 15]` |
| free-flow arrival at `d = 0` | 25 min (deadline 40) |
| capacity binding | `true` |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
