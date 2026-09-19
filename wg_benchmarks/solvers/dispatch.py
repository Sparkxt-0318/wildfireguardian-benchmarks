"""Assisted-dispatch reference solver.

A mission is the three-leg sequence

    base --(ingress)--> resident --(pickup)--> resident --(egress)--> refuge

and it succeeds only if *every* leg is feasible under the declared network
semantics (see :mod:`wg_benchmarks.solvers.network`), the pickup finishes before
the resident's location becomes untenable, and the refuge is reached before the
refuge deadline.

Feasibility is reported as the **set of feasible dispatch times**, not as a
single scalar.  That is the central scientific point of the F family: the set
need not be an interval, so a "latest feasible dispatch time" can be true and
useless at the same time.  The set is found by exhaustive sampling plus
bisection refinement of every transition, with all edge-window endpoints forced
into the sample so that narrow windows are not stepped over.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Iterable

from .. import mutations
from .network import Network, best_route, load_network

INF = float("inf")


def evaluate_mission(
    network: Network,
    base: str,
    resident: str,
    destinations: list[str],
    pickup_min: float,
    dispatch_min: float,
    allow_waiting: bool,
    resident_deadline_min: float,
    destination_deadlines: dict[str, float],
) -> dict:
    """Run one mission from one base at one dispatch time."""
    # MUTATION HOOK: the on-scene pickup/loading time is dropped entirely.
    if mutations.active("ignore_pickup_duration"):
        pickup_min = 0.0

    ingress = best_route(network, base, resident, dispatch_min, allow_waiting)
    if ingress["best"] is None:
        return {"success": False, "stage": "ingress", "base": base, "dispatch_min": dispatch_min}
    arrive_resident = ingress["best"]["arrival_min"]
    pickup_complete = arrive_resident + pickup_min
    if pickup_complete > resident_deadline_min + 1e-12:
        return {
            "success": False,
            "stage": "pickup",
            "base": base,
            "dispatch_min": dispatch_min,
            "arrive_resident_min": arrive_resident,
            "pickup_complete_min": pickup_complete,
            "resident_deadline_min": resident_deadline_min,
        }

    options = []
    for destination in destinations:
        egress = best_route(network, resident, destination, pickup_complete, allow_waiting)
        if egress["best"] is None:
            continue
        arrival = egress["best"]["arrival_min"]
        deadline = destination_deadlines.get(destination, INF)
        if arrival > deadline + 1e-12:
            continue
        options.append(
            {
                "destination": destination,
                "arrival_min": arrival,
                "route": "+".join(egress["best"]["edges"]),
                "deadline_min": deadline,
                "slack_min": deadline - arrival,
            }
        )
    if not options:
        return {
            "success": False,
            "stage": "egress",
            "base": base,
            "dispatch_min": dispatch_min,
            "arrive_resident_min": arrive_resident,
            "pickup_complete_min": pickup_complete,
        }
    options.sort(key=lambda o: (o["arrival_min"], o["destination"]))
    chosen = options[0]
    return {
        "success": True,
        "base": base,
        "dispatch_min": dispatch_min,
        "ingress_route": "+".join(ingress["best"]["edges"]),
        "arrive_resident_min": arrive_resident,
        "pickup_complete_min": pickup_complete,
        "destination": chosen["destination"],
        "egress_route": chosen["route"],
        "arrival_min": chosen["arrival_min"],
        "slack_min": chosen["slack_min"],
        "feasible_destinations": [o["destination"] for o in options],
    }


def free_flow_network(network: Network) -> Network:
    """The same network with every congestion-aware travel time set to free flow.

    Used to report the capacity-free counterfactual explicitly, so that a
    benchmark can state "this mission succeeds without congestion and fails with
    it" as two numbers rather than as a claim.
    """
    edges = [
        replace(edge, travel_time_min=edge.free_flow_min, travel_time_profile=())
        if edge.free_flow_min is not None
        else edge
        for edge in network.edges
    ]
    return Network(nodes=dict(network.nodes), edges=edges)


def _sample_times(network: Network, horizon: float, step: float) -> list[float]:
    """Grid samples plus every edge-window endpoint, so no window is stepped over."""
    times = set()
    count = int(math.floor(horizon / step)) + 1
    for index in range(count):
        times.add(round(index * step, 9))
    times.add(horizon)
    epsilon = min(step / 8.0, 1e-4)
    for edge in network.edges:
        for start, end in edge.open_intervals:
            for value in (start, end):
                if math.isfinite(value) and 0.0 <= value <= horizon:
                    for candidate in (value - epsilon, value, value + epsilon):
                        if 0.0 <= candidate <= horizon:
                            times.add(round(candidate, 9))
        for start, end, _ in edge.travel_time_profile:
            for value in (start, end):
                if math.isfinite(value) and 0.0 <= value <= horizon:
                    times.add(round(value, 9))
    return sorted(times)


def _refine(predicate, low: float, high: float, tolerance: float) -> float:
    """Bisection on a piecewise-constant predicate: predicate(low) != predicate(high)."""
    target = predicate(low)
    while high - low > tolerance:
        mid = (low + high) / 2.0
        if predicate(mid) == target:
            low = mid
        else:
            high = mid
    return low if target else high


def feasible_dispatch_intervals(
    predicate, horizon: float, samples: Iterable[float], tolerance: float = 1e-7
) -> list[list[float]]:
    """Merge sampled feasibility into closed intervals with refined endpoints."""
    samples = sorted(samples)
    flags = [(t, predicate(t)) for t in samples]
    intervals: list[list[float]] = []
    current_start: float | None = None
    previous_time, previous_flag = None, False
    for time, flag in flags:
        if flag and not previous_flag:
            if previous_time is None:
                current_start = time
            else:
                current_start = _refine(predicate, previous_time, time, tolerance)
                if not predicate(current_start):
                    current_start = time
        if not flag and previous_flag:
            end = _refine(predicate, previous_time, time, tolerance)
            if not predicate(end):
                end = previous_time
            intervals.append([current_start, end])
            current_start = None
        previous_time, previous_flag = time, flag
    if previous_flag and current_start is not None:
        intervals.append([current_start, previous_time])
    return [[round(a, 6), round(b, 6)] for a, b in intervals]


def solve(inputs: dict) -> dict:
    network = load_network(inputs["network"])
    mission = inputs["mission"]
    resident = str(mission["resident"])
    bases = [str(b) for b in mission["bases"]]
    destinations = [str(d) for d in mission["destinations"]]
    allow_waiting = bool(mission.get("allow_waiting", False))
    horizon = float(mission.get("dispatch_horizon_min", 60.0))
    step = float(mission.get("dispatch_step_min", 0.25))
    destination_deadlines = {
        str(k): float(v) for k, v in (mission.get("destination_deadlines") or {}).items()
    }
    resident_deadline = mission.get("resident_deadline_min")
    if resident_deadline is None:
        node = network.nodes.get(resident)
        resident_deadline = node.hazard_arrival_min if node else INF
    resident_deadline = float(resident_deadline)

    pickup_values = mission.get("pickup_min")
    if not isinstance(pickup_values, list):
        pickup_values = [pickup_values if pickup_values is not None else 0.0]
    pickup_values = [float(p) for p in pickup_values]

    considered_bases = list(bases)
    # MUTATION HOOK: plan only from the geographically nearest base.
    if mutations.active("nearest_base_only") and len(bases) > 1:
        resident_node = network.nodes[resident]
        considered_bases = [
            min(
                bases,
                key=lambda b: math.hypot(
                    network.nodes[b].x - resident_node.x, network.nodes[b].y - resident_node.y
                ),
            )
        ]

    samples = _sample_times(network, horizon, step)
    tolerance = float(mission.get("boundary_tolerance_min", 1e-7))

    def mission_at(base: str, pickup: float, dispatch: float) -> dict:
        return evaluate_mission(
            network,
            base,
            resident,
            destinations,
            pickup,
            dispatch,
            allow_waiting,
            resident_deadline,
            destination_deadlines,
        )

    by_pickup: dict[str, dict] = {}
    for pickup in pickup_values:
        by_base: dict[str, dict] = {}
        for base in considered_bases:
            predicate = lambda d, b=base, p=pickup: mission_at(b, p, d)["success"]
            intervals = feasible_dispatch_intervals(predicate, horizon, samples, tolerance)
            by_base[base] = {
                "feasible_intervals": intervals,
                "latest_feasible_dispatch_min": intervals[-1][1] if intervals else None,
                "earliest_feasible_dispatch_min": intervals[0][0] if intervals else None,
                "feasible": bool(intervals),
            }
        any_predicate = lambda d, p=pickup: any(
            mission_at(b, p, d)["success"] for b in considered_bases
        )
        combined = feasible_dispatch_intervals(any_predicate, horizon, samples, tolerance)
        # MUTATION HOOK: assume feasibility is monotone in the dispatch time and
        # summarise it as one interval ending at the latest feasible time.
        if mutations.active("monotone_dispatch_assumption") and combined:
            combined = [[combined[0][0], combined[-1][1]]]
        gap_counterexample = None
        if combined:
            latest = combined[-1][1]
            for time in samples:
                if time <= latest and not any_predicate(time):
                    gap_counterexample = time
                    break
        by_pickup[f"{pickup:g}"] = {
            "pickup_min": pickup,
            "by_base": by_base,
            "feasible_intervals": combined,
            "feasible_interval_count": len(combined),
            "latest_feasible_dispatch_min": combined[-1][1] if combined else None,
            "earliest_feasible_dispatch_min": combined[0][0] if combined else None,
            "feasible": bool(combined),
            "monotone_feasibility": len(combined) <= 1,
            "scalar_latest_sufficient": gap_counterexample is None,
            "infeasible_dispatch_below_latest_min": gap_counterexample,
            "best_base": (
                min(
                    (b for b in by_base if by_base[b]["feasible"]),
                    key=lambda b: (-by_base[b]["latest_feasible_dispatch_min"], b),
                    default=None,
                )
            ),
        }

    primary = by_pickup[f"{pickup_values[0]:g}"]
    probes = {}
    for probe in mission.get("dispatch_probes", []):
        pickup = float(probe.get("pickup_min", pickup_values[0]))
        dispatch = float(probe["dispatch_min"])
        outcomes = {b: mission_at(b, pickup, dispatch) for b in considered_bases}
        successful = [b for b, o in outcomes.items() if o["success"]]
        best = min(
            (o for o in outcomes.values() if o["success"]),
            key=lambda o: (o["arrival_min"], o["base"]),
            default=None,
        )
        probes[str(probe["id"])] = {
            "dispatch_min": dispatch,
            "pickup_min": pickup,
            "feasible_bases": sorted(successful),
            "success": bool(successful),
            "base": best["base"] if best else None,
            "destination": best["destination"] if best else None,
            "arrival_min": best["arrival_min"] if best else None,
            "failure_stage": None if best else sorted(
                {o.get("stage", "unknown") for o in outcomes.values()}
            )[0],
        }

    counterfactual = None
    if any(edge.free_flow_min is not None for edge in network.edges):
        free_flow = free_flow_network(network)
        free_samples = _sample_times(free_flow, horizon, step)

        def free_predicate(dispatch: float) -> bool:
            return any(
                evaluate_mission(
                    free_flow,
                    base,
                    resident,
                    destinations,
                    pickup_values[0],
                    dispatch,
                    allow_waiting,
                    resident_deadline,
                    destination_deadlines,
                )["success"]
                for base in considered_bases
            )

        free_intervals = feasible_dispatch_intervals(free_predicate, horizon, free_samples, tolerance)
        free_at_zero = evaluate_mission(
            free_flow,
            considered_bases[0],
            resident,
            destinations,
            pickup_values[0],
            0.0,
            allow_waiting,
            resident_deadline,
            destination_deadlines,
        )
        counterfactual = {
            "feasible": bool(free_intervals),
            "feasible_intervals": free_intervals,
            "latest_feasible_dispatch_min": free_intervals[-1][1] if free_intervals else None,
            "arrival_at_dispatch_zero_min": free_at_zero.get("arrival_min"),
            "success_at_dispatch_zero": free_at_zero["success"],
        }

    nearest_base = None
    if bases:
        resident_node = network.nodes[resident]
        nearest_base = min(
            bases,
            key=lambda b: math.hypot(
                network.nodes[b].x - resident_node.x, network.nodes[b].y - resident_node.y
            ),
        )

    return {
        "resident": resident,
        "bases_considered": considered_bases,
        "nearest_base": nearest_base,
        "resident_deadline_min": resident_deadline,
        "pickup_values_min": pickup_values,
        "by_pickup": by_pickup,
        "feasible_intervals": primary["feasible_intervals"],
        "feasible_interval_count": primary["feasible_interval_count"],
        "latest_feasible_dispatch_min": primary["latest_feasible_dispatch_min"],
        "earliest_feasible_dispatch_min": primary["earliest_feasible_dispatch_min"],
        "monotone_feasibility": primary["monotone_feasibility"],
        "scalar_latest_sufficient": primary["scalar_latest_sufficient"],
        "infeasible_dispatch_below_latest_min": primary["infeasible_dispatch_below_latest_min"],
        "best_base": primary["best_base"],
        "latest_dispatch_by_base": {
            base: data["latest_feasible_dispatch_min"] for base, data in primary["by_base"].items()
        },
        "latest_dispatch_by_pickup": {
            key: data["latest_feasible_dispatch_min"] for key, data in by_pickup.items()
        },
        "feasible_by_pickup": {key: data["feasible"] for key, data in by_pickup.items()},
        "probes": probes,
        "free_flow_counterfactual": counterfactual,
        "capacity_binding": bool(
            counterfactual is not None
            and counterfactual["feasible"]
            and not primary["feasible"]
        ),
    }
