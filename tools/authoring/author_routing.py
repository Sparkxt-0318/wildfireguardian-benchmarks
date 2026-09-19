"""Author the E family: time-dependent routing benchmarks (WG-BM-018..021)."""

from __future__ import annotations

from common import report, write_benchmark

SCRIPT = "author_routing.py"
TOLERANCE = {"default": 1.0e-09}


def main() -> None:
    written = []

    # ------------------------------------------------------------------ E1
    written.append(write_benchmark(
        directory="benchmarks/routing/WG-BM-018_E1_short_unsafe_vs_long_safe",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-018",
            "label": "E1",
            "title": "The shortest route is infeasible; the long route is the answer",
            "category": "routing",
            "difficulty": "basic",
            "purpose": "Distance is not feasibility. A 5-minute route that closes at minute 4 is "
                       "not a route.",
            "solver": "routing.time_dependent_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "waiting": False,
                "deterministic_hazard": True,
                "start_time_min": 0,
            },
            "expected_behavior": {
                "earliest_arrival_min": 9.0,
                "shortest_route_feasible": False,
                "feasible_routes": ["e_long_safe"],
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["shortest_path_without_feasibility", "mid_edge_hazard"],
            "mutations_expected_to_fail": ["edge_entry_time_only", "final_perimeter_hazard"],
            "hand_checkable": True,
        },
        inputs={
            "network": {
                "description": "Two parallel corridors from the origin to the refuge.",
                "nodes": [
                    {"id": "origin", "x": 0.0, "y": 0.0, "role": "population"},
                    {"id": "refuge", "x": 4000.0, "y": 0.0, "role": "refuge"},
                ],
                "edges": [
                    {
                        "id": "e_short_unsafe",
                        "from": "origin",
                        "to": "refuge",
                        "travel_time_min": 5.0,
                        "open_intervals": [[0.0, 4.0]],
                        "note": "canyon road, hazard reaches it at minute 4",
                    },
                    {
                        "id": "e_long_safe",
                        "from": "origin",
                        "to": "refuge",
                        "travel_time_min": 9.0,
                        "note": "ridge road, remains open",
                    },
                ],
            },
            "query": {
                "origin": "origin",
                "destination": "refuge",
                "start_time_min": 0.0,
                "allow_waiting": False,
            },
        },
        expected={
            "benchmark_id": "WG-BM-018",
            "source": "hand_derivation",
            "derivation": (
                "Under WG-SEM-1 a traversal departing at tau is feasible only if the whole "
                "interval [tau, tau + w] lies inside one open window. Departing at 0 on the short "
                "route gives the interval [0, 5], which does not fit inside [0, 4]: the traveller "
                "would still be on the road one minute after the hazard arrives. The short route "
                "is therefore infeasible even though it is the shortest. The long route is open "
                "throughout, so [0, 9] is fine and the arrival is at minute 9. Under the naive "
                "entry-time rule the short route would be judged feasible, because the entry "
                "instant 0 lies in [0, 4], and the reported arrival would be minute 5."
            ),
            "results": {
                "origin": "origin",
                "destination": "refuge",
                "declared_waiting_allowed": False,
                "feasible_routes": ["e_long_safe"],
                "earliest_arrival_min": 9.0,
                "best_route": "e_long_safe",
                "any_feasible": True,
                "shortest_route": "e_short_unsafe",
                "shortest_route_travel_min": 5.0,
                "shortest_route_feasible": False,
                "nominal_travel_min": {"e_short_unsafe": 5.0, "e_long_safe": 9.0},
                "feasible_with_waiting": True,
                "arrival_with_waiting_min": 9.0,
                "feasible_without_waiting": True,
                "arrival_without_waiting_min": 9.0,
                "feasible_under_entry_time_semantics": True,
                "arrival_under_entry_time_semantics_min": 5.0,
            },
            "invariants": [
                {
                    "expression": "r['shortest_route'] not in r['feasible_routes']",
                    "description": "the shortest route is not among the feasible ones",
                },
                {
                    "expression": "r['arrival_under_entry_time_semantics_min'] < r['earliest_arrival_min']",
                    "description": "the naive convention reports a faster, unattainable arrival",
                },
            ],
        },
        readme="""
# WG-BM-018 (E1) — Short unsafe route vs long safe route

## Scenario

```
              e_short_unsafe:  5 min, open only on [0, 4]
origin  ====================================================  refuge
              e_long_safe:     9 min, open throughout
```

Departure at `t = 0`, no waiting permitted.

## Derivation

Under **WG-SEM-1 (interval safety)** a traversal departing at `tau` is feasible
only if the entire interval `[tau, tau + w]` lies inside one open window of the
edge.

```
short route:  [0, 0 + 5] = [0, 5]  vs  open window [0, 4]   ->  INFEASIBLE
long route:   [0, 0 + 9] = [0, 9]  vs  open window [0, inf) ->  feasible, arrival 9
```

The traveller who enters the canyon road at minute 0 is still 1 minute from the
far end when the fire arrives at minute 4. That the road was open when they
entered is no comfort.

**Answer: the only feasible route is the 9-minute one, arriving at minute 9.**

## The counterfactual, stated explicitly

Under the naive entry-time rule — "the edge is open at the moment I enter, so I
may enter" — the short route is judged feasible and the reported arrival is
minute 5. The result document reports this as
`feasible_under_entry_time_semantics: true` and
`arrival_under_entry_time_semantics_min: 5.0`, next to the real answer, so that
a reader can see exactly which convention produced which number.

This is not a stylistic difference. The naive rule reports a 5-minute
evacuation that ends inside the fire, and it reports it with the same confidence
as a correct answer.

## Expected

| Quantity | Value |
|---|---|
| feasible routes | `[e_long_safe]` |
| earliest safe arrival | 9 min |
| shortest route | `e_short_unsafe`, 5 min |
| shortest route feasible | `false` |
| arrival under entry-time semantics | 5 min (wrong) |
""",
    ))

    # ------------------------------------------------------------------ E2
    written.append(write_benchmark(
        directory="benchmarks/routing/WG-BM-019_E2_mid_edge_closure",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-019",
            "label": "E2",
            "title": "Mid-edge closure: the answer depends on a semantic choice that must be declared",
            "category": "routing",
            "difficulty": "adversarial",
            "purpose": "A traveller enters a 10-minute edge at t = 0 and the hazard reaches it at "
                       "t = 5. There is no convention-free answer, so the convention is part of "
                       "the benchmark.",
            "solver": "routing.time_dependent_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "declared_answer_under": "interval safety",
                "alternative_reported": "entry-time-only",
                "no_turning_back": True,
                "waiting": False,
            },
            "expected_behavior": {
                "any_feasible": False,
                "feasible_under_entry_time_semantics": True,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["mid_edge_hazard", "undeclared_traversal_semantics"],
            "mutations_expected_to_fail": ["edge_entry_time_only"],
            "hand_checkable": True,
            "notes": "This benchmark asserts a convention, not a law of nature. Its value is that "
                     "an implementation cannot pass it without stating which convention it uses.",
        },
        inputs={
            "network": {
                "description": "A single 10-minute edge whose hazard arrives at minute 5.",
                "nodes": [
                    {"id": "origin", "x": 0.0, "y": 0.0, "role": "population"},
                    {"id": "refuge", "x": 5000.0, "y": 0.0, "role": "refuge"},
                ],
                "edges": [
                    {
                        "id": "e_single",
                        "from": "origin",
                        "to": "refuge",
                        "travel_time_min": 10.0,
                        "open_intervals": [[0.0, 5.0]],
                        "note": "hazard reaches the midpoint of this road at minute 5",
                    }
                ],
            },
            "query": {
                "origin": "origin",
                "destination": "refuge",
                "start_time_min": 0.0,
                "allow_waiting": False,
            },
        },
        expected={
            "benchmark_id": "WG-BM-019",
            "source": "hand_derivation",
            "derivation": (
                "There is one route. Departing at 0 the traversal interval is [0, 10] and the "
                "open window is [0, 5]. Under WG-SEM-1 the traversal is infeasible, so there is "
                "no feasible route and no arrival time. Under the entry-time-only rule the entry "
                "instant 0 lies in [0, 5], the traversal is permitted, and the reported arrival "
                "is minute 10 - five minutes after the hazard reached the road. Waiting does not "
                "help: the only open window starts at 0 and the required 10 minutes never fit, so "
                "the answer is the same with waiting permitted."
            ),
            "results": {
                "declared_waiting_allowed": False,
                "feasible_routes": [],
                "any_feasible": False,
                "earliest_arrival_min": None,
                "best_route": None,
                "shortest_route": "e_single",
                "shortest_route_travel_min": 10.0,
                "shortest_route_feasible": False,
                "feasible_with_waiting": False,
                "arrival_with_waiting_min": None,
                "feasible_without_waiting": False,
                "arrival_without_waiting_min": None,
                "feasible_under_entry_time_semantics": True,
                "arrival_under_entry_time_semantics_min": 10.0,
            },
            "invariants": [
                {
                    "expression": "r['any_feasible'] is False and r['feasible_under_entry_time_semantics'] is True",
                    "description": "the two conventions give opposite verdicts on the same input",
                }
            ],
        },
        readme="""
# WG-BM-019 (E2) — Mid-edge closure

## Scenario

One road. Ten minutes end to end. The traveller enters at `t = 0`. The hazard
reaches the road at `t = 5`.

```
origin ---------------- 10 min, open on [0, 5] ---------------- refuge
                                ^
                          hazard arrives t = 5
```

## There is no convention-free answer

This is the case that forces a project to write its semantics down. At least
four rules are defensible:

| Rule | Verdict here | Comment |
|---|---|---|
| **Interval safety** — the whole traversal must fit in an open window | infeasible | conservative; assumes no mid-route escape |
| **Entry-time only** — the edge must be open when you enter | feasible, arrival 10 | assumes you outrun or survive the front |
| **Partial traversal** — you may proceed to the point reached at closure and then stop | reaches the midpoint, stranded | needs a model of what happens to a stranded vehicle |
| **Reversible** — you may turn back on detecting the closure | return to origin at minute 10 | needs a detection model and a turnaround time |

They give different answers, and none of them is a fact about the world. Each is
a modelling assumption about vehicle behaviour, driver information and
survivability inside a fire front.

## What this benchmark asserts

**This suite declares interval safety (WG-SEM-1) as its convention**, so the
expected verdict is `infeasible`. The benchmark additionally requires that the
implementation report what the entry-time rule would have concluded, as
`feasible_under_entry_time_semantics: true` with an arrival at minute 10.

An implementation may legitimately use a different convention. What it may not
do is fail to say which one it uses, because a downstream consumer cannot
otherwise tell whether "route available" means "you will arrive" or "you may
enter". The assumptions block of this benchmark is therefore as much a part of
the expected answer as the numbers.

## Waiting does not rescue it

The only open window starts at 0 and ends at 5. A 10-minute traversal never fits
inside it, at any departure time. `feasible_with_waiting` is also `false`.

## Expected

| Quantity | Value |
|---|---|
| feasible under interval safety | `false` |
| earliest arrival | `null` |
| feasible under entry-time rule | `true` |
| arrival under entry-time rule | 10 min |
""",
    ))

    # ------------------------------------------------------------------ E3
    written.append(write_benchmark(
        directory="benchmarks/routing/WG-BM-020_E3_waiting_needed",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-020",
            "label": "E3",
            "title": "Waiting is required: infeasible now, feasible after the front passes",
            "category": "routing",
            "difficulty": "intermediate",
            "purpose": "Some routes only exist for a traveller willing to hold at a junction. A "
                       "system that forbids waiting must report infeasible, not silently allow it.",
            "solver": "routing.time_dependent_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "waiting": True,
                "waiting_location_is_safe": True,
                "declared_answer_under": "waiting permitted",
            },
            "expected_behavior": {
                "feasible_with_waiting": True,
                "arrival_with_waiting_min": 25.0,
                "feasible_without_waiting": False,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["waiting_policy_undeclared", "time_window_reopening_ignored"],
            "mutations_expected_to_fail": ["final_perimeter_hazard"],
            "hand_checkable": True,
        },
        inputs={
            "network": {
                "description": "Two legs. The second cannot be entered until the fire front has "
                               "passed over it and the road has been reopened at minute 20.",
                "nodes": [
                    {"id": "start", "x": 0.0, "y": 0.0, "role": "population"},
                    {"id": "muster", "x": 2000.0, "y": 0.0, "role": "safe_holding_point"},
                    {"id": "refuge", "x": 5000.0, "y": 0.0, "role": "refuge"},
                ],
                "edges": [
                    {
                        "id": "e_start_muster",
                        "from": "start",
                        "to": "muster",
                        "travel_time_min": 5.0,
                        "note": "open throughout",
                    },
                    {
                        "id": "e_muster_refuge",
                        "from": "muster",
                        "to": "refuge",
                        "travel_time_min": 5.0,
                        "open_intervals": [[20.0, 100.0]],
                        "note": "closed until the front has passed and the road is reopened at 20",
                    },
                ],
            },
            "query": {
                "origin": "start",
                "destination": "refuge",
                "start_time_min": 0.0,
                "allow_waiting": True,
            },
        },
        expected={
            "benchmark_id": "WG-BM-020",
            "source": "hand_derivation",
            "derivation": (
                "The first leg takes 5 minutes and is always open, so the traveller reaches the "
                "muster point at minute 5. The second leg cannot be entered before minute 20. "
                "With waiting forbidden the traveller must depart at minute 5, whose traversal "
                "interval [5, 10] is not inside [20, 100], so the route is infeasible. With "
                "waiting permitted the traveller holds 15 minutes at the muster point, departs at "
                "20, and arrives at 25. The muster point is stipulated safe for the whole holding "
                "period; without that stipulation the waiting option would not be available and "
                "the expected answer would change."
            ),
            "results": {
                "declared_waiting_allowed": True,
                "any_feasible": True,
                "earliest_arrival_min": 25.0,
                "best_route": "e_start_muster+e_muster_refuge",
                "feasible_routes": ["e_start_muster+e_muster_refuge"],
                "feasible_with_waiting": True,
                "arrival_with_waiting_min": 25.0,
                "feasible_without_waiting": False,
                "arrival_without_waiting_min": None,
                "nominal_travel_min": {"e_start_muster+e_muster_refuge": 10.0},
            },
            "invariants": [
                {
                    "expression": "r['routes'][0]['total_wait_min'] == 15.0",
                    "description": "the feasible trajectory holds exactly 15 minutes at the muster point",
                },
                {
                    "expression": "r['arrival_with_waiting_min'] > r['nominal_travel_min']['e_start_muster+e_muster_refuge']",
                    "description": "arrival exceeds free-flow travel time because of the hold",
                },
            ],
        },
        readme="""
# WG-BM-020 (E3) — Waiting needed

## Scenario

```
start --5 min, always open--> muster --5 min, open only on [20, 100]--> refuge
```

The muster point is stipulated to be a **safe holding location** for the whole
period. The second leg is closed until minute 20, when the front has passed over
it and the road is reopened.

## Derivation

```
arrive at muster            = 0 + 5  = 5 min
earliest entry to leg two   = 20 min          (window opens)
hold at muster              = 20 - 5 = 15 min
arrive at refuge            = 20 + 5 = 25 min
```

**With waiting forbidden**, departure from the muster point is forced to minute
5. The traversal interval `[5, 10]` is not inside `[20, 100]`, so the route is
**infeasible** — there is no route at all, and the correct output is a refusal,
not a plan.

**With waiting permitted**, the answer is arrival at **minute 25**, with a
recorded 15-minute hold.

## Why the distinction has to be explicit

"Wait here until the road reopens" is a real operational instruction, and for a
supervised convoy it is often the right one. It is also an instruction that a
router must not issue implicitly: it requires a location that is survivable for
the whole hold, a way to tell the traveller when to move, and a fallback if the
reopening does not happen. A routing engine that permits waiting without
modelling those three things is producing plans that cannot be executed.

Conversely, a router that silently forbids waiting will report "no route" for a
community that has a perfectly good one, and the operator has no way to tell
that refusal apart from a genuine entrapment.

This suite therefore requires the waiting policy to be declared per scenario,
and requires both answers to be reported. `allow_waiting` is part of the query,
not a global setting.

## What the hazard model must preserve

The second leg is closed *and then open again*. An implementation that reduces
the hazard to a single scalar "closure time" per edge — or to the final fire
perimeter — cannot represent a reopening and will call this route permanently
impossible. That is the `final_perimeter_hazard` mutation, and this benchmark is
one of its detectors.

## Expected

| Quantity | Value |
|---|---|
| arrival with waiting | 25 min |
| hold duration | 15 min |
| feasible without waiting | `false` |
| free-flow travel time | 10 min |
""",
    ))

    # ------------------------------------------------------------------ E4
    sweep = []
    for depart in range(0, 11):
        travel = 60.0 if depart < 5 else 10.0
        sweep.append({"depart_min": float(depart), "arrival_min": float(depart) + travel})
    written.append(write_benchmark(
        directory="benchmarks/routing/WG-BM-021_E4_non_fifo_edge",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-021",
            "label": "E4",
            "title": "Non-FIFO edge: leaving later arrives earlier",
            "category": "routing",
            "difficulty": "adversarial",
            "purpose": "Break the FIFO assumption that every time-dependent Dijkstra variant "
                       "relies on. Departing at minute 5 arrives 45 minutes before departing at "
                       "minute 0.",
            "solver": "routing.time_dependent_enumeration",
            "assumptions": {
                "edge_semantics": "WG-SEM-1 interval safety",
                "waiting": False,
                "fifo": False,
                "travel_time_depends_on_departure_time": True,
            },
            "expected_behavior": {
                "fifo_violated": True,
                "optimal_departure_min": 5.0,
                "earliest_arrival_over_departures_min": 15.0,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_enumeration",
            "detects": ["non_fifo_network", "premature_departure_assumed_optimal"],
            "mutations_expected_to_fail": ["fifo_assumption"],
            "hand_checkable": True,
        },
        inputs={
            "network": {
                "description": "A single link served by a ferry/escort convoy. Before minute 5 the "
                               "only way across is a 60-minute detour; from minute 5 the escorted "
                               "crossing runs and takes 10 minutes.",
                "nodes": [
                    {"id": "start", "x": 0.0, "y": 0.0, "role": "population"},
                    {"id": "refuge", "x": 8000.0, "y": 0.0, "role": "refuge"},
                ],
                "edges": [
                    {
                        "id": "e_crossing",
                        "from": "start",
                        "to": "refuge",
                        "travel_time_profile": [
                            {"depart_from": 0.0, "depart_to": 5.0, "minutes": 60.0},
                            {"depart_from": 5.0, "depart_to": None, "minutes": 10.0},
                        ],
                        "note": "escorted convoy begins at minute 5",
                    }
                ],
            },
            "query": {
                "origin": "start",
                "destination": "refuge",
                "start_time_min": 0.0,
                "allow_waiting": False,
                "departure_sweep": {"from_min": 0.0, "to_min": 10.0, "step_min": 1.0},
            },
        },
        expected={
            "benchmark_id": "WG-BM-021",
            "source": "exhaustive_enumeration",
            "derivation": (
                "Travel time is 60 minutes for departures in [0, 5) and 10 minutes for departures "
                "at or after 5. Arrival as a function of departure is therefore "
                "tau + 60 on [0, 5) and tau + 10 on [5, inf). Departing at 0 arrives at 60; "
                "departing at 5 arrives at 15. Leaving 5 minutes later arrives 45 minutes "
                "earlier, so the arrival function is not non-decreasing and the network is not "
                "FIFO. Sweeping departures on the integer minutes from 0 to 10 gives arrivals "
                "60, 61, 62, 63, 64 then 15, 16, 17, 18, 19, 20, whose minimum is 15 at departure "
                "5. With waiting forbidden and a start time of 0 the traveller is stuck with the "
                "60-minute crossing; with waiting permitted they hold 5 minutes and arrive at 15."
            ),
            "results": {
                "declared_waiting_allowed": False,
                "any_feasible": True,
                "earliest_arrival_min": 60.0,
                "feasible_without_waiting": True,
                "arrival_without_waiting_min": 60.0,
                "feasible_with_waiting": True,
                "arrival_with_waiting_min": 15.0,
                "departure_sweep": sweep,
                "earliest_arrival_over_departures_min": 15.0,
                "optimal_departure_min": 5.0,
                "immediate_departure_arrival_min": 60.0,
                "fifo_violated": True,
            },
            "invariants": [
                {
                    "expression": "r['earliest_arrival_over_departures_min'] < r['immediate_departure_arrival_min']",
                    "description": "the best departure is not the earliest departure",
                },
                {
                    "expression": "r['arrival_with_waiting_min'] == r['earliest_arrival_over_departures_min']",
                    "description": "waiting recovers the optimum that the FIFO assumption would miss",
                },
            ],
        },
        readme="""
# WG-BM-021 (E4) — Non-FIFO edge

## Scenario

One link. Before minute 5 the only way across is a 60-minute detour. From minute
5 an escorted convoy runs and the crossing takes 10 minutes.

```
travel_time(depart tau) = 60 min   for tau in [0, 5)
                        = 10 min   for tau >= 5
```

## Derivation

Arrival as a function of departure:

| Depart | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Arrive | 60 | 61 | 62 | 63 | 64 | **15** | 16 | 17 | 18 | 19 | 20 |

Departing at minute 5 arrives **45 minutes earlier** than departing at minute 0.
The arrival function is not non-decreasing, so the network is **not FIFO**.

* best achievable arrival: **15 min**, departing at **5**
* arrival if you leave immediately: **60 min**
* with waiting permitted: hold 5 minutes, arrive at 15

## Why this breaks standard shortest-path machinery

Time-dependent Dijkstra, A\\*, contraction hierarchies and every label-setting
variant rely on the FIFO property: if you arrive at a node earlier you can do no
worse. Under FIFO a label can be settled permanently the first time it is
reached. Here that reasoning is invalid — an earlier arrival at `start`
(minute 0) yields a *worse* arrival at `refuge` than a later one (minute 5) —
and a settled label is simply wrong.

There are exactly two defensible responses:

1. **Permit waiting.** Adding a wait at the node restores the FIFO property, and
   the optimum (15 min) is recovered. This is what the result document's
   `arrival_with_waiting_min` shows.
2. **Refuse the case.** Detect that the travel-time profile is not FIFO and
   decline to answer, rather than returning the 60-minute label as if it were
   optimal.

What is **not** acceptable is silently returning 60 minutes. That is the
`fifo_assumption` mutation, which forces the reported optimum to the immediate
departure and clears the `fifo_violated` flag; this benchmark is its declared
detector.

## Where non-FIFO travel times come from in practice

They are not a contrivance. Escorted convoys, ferry and shuttle schedules,
contraflow switch-over times, pilot-car operations on a single-lane section, and
a road that is being actively defended and reopened all produce departure-time
windows where waiting strictly dominates leaving now.

## Expected

| Quantity | Value |
|---|---|
| arrival departing immediately | 60 min |
| best arrival over departures | 15 min |
| optimal departure | minute 5 |
| FIFO violated | `true` |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
