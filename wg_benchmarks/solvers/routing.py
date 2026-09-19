"""Time-dependent evacuation-routing reference solver.

Brute force by construction: every simple path is enumerated, every path is
walked forward in time under the declared semantics, and the earliest feasible
arrival is the minimum over paths.  No shortest-path algorithm is used, because
the whole point of several of these benchmarks is that the usual shortest-path
assumptions (FIFO travel times, monotone feasibility, safety judged at entry)
are false.

The solver deliberately reports the *alternative* conventions as well
(``feasible_under_entry_time_semantics``, ``arrival_with_waiting``) so that a
reader can see exactly which convention produced which number.
"""

from __future__ import annotations

from .. import mutations
from .network import best_route, load_network

INF = float("inf")


def _summarise(outcome: dict) -> dict:
    routes = []
    for evaluation in outcome["evaluations"]:
        routes.append(
            {
                "route": "+".join(evaluation["edges"]),
                "nodes": evaluation["nodes"],
                "feasible": evaluation["feasible"],
                "arrival_min": evaluation.get("arrival_min"),
                "blocked_at_edge": evaluation.get("blocked_at_edge"),
                "total_wait_min": sum(step["wait_min"] for step in evaluation.get("timeline", [])),
            }
        )
    routes.sort(key=lambda r: r["route"])
    return {
        "routes": routes,
        "feasible_routes": sorted(r["route"] for r in routes if r["feasible"]),
        "earliest_arrival_min": outcome["best"]["arrival_min"] if outcome["best"] else None,
        "best_route": "+".join(outcome["best"]["edges"]) if outcome["best"] else None,
        "any_feasible": outcome["best"] is not None,
    }


def solve(inputs: dict) -> dict:
    network = load_network(inputs["network"])
    query = inputs["query"]
    origin = str(query["origin"])
    destination = str(query["destination"])
    start_time = float(query.get("start_time_min", 0.0))
    allow_waiting = bool(query.get("allow_waiting", False))
    deadlines = {str(k): float(v) for k, v in (query.get("node_deadlines") or {}).items()}

    declared = _summarise(
        best_route(network, origin, destination, start_time, allow_waiting, deadlines)
    )

    result: dict = {
        "origin": origin,
        "destination": destination,
        "start_time_min": start_time,
        "declared_waiting_allowed": allow_waiting,
        **declared,
    }

    # Nominal (hazard-free) travel time of each route, so a benchmark can state
    # "the shortest route is not the feasible one" without ambiguity.
    nominal = {}
    for evaluation in best_route(network, origin, destination, start_time, True, None)["evaluations"]:
        route_id = "+".join(evaluation["edges"])
        edges = [network.edge(e) for e in evaluation["edges"]]
        nominal[route_id] = sum(edge.travel_time(start_time) for edge in edges)
    result["nominal_travel_min"] = nominal
    if nominal:
        shortest = min(sorted(nominal), key=lambda k: nominal[k])
        result["shortest_route"] = shortest
        result["shortest_route_travel_min"] = nominal[shortest]
        result["shortest_route_feasible"] = shortest in result["feasible_routes"]

    # Counterfactual conventions, always reported, never used for the verdict.
    with_waiting = _summarise(best_route(network, origin, destination, start_time, True, deadlines))
    without_waiting = _summarise(best_route(network, origin, destination, start_time, False, deadlines))
    entry_only = _summarise(
        best_route(network, origin, destination, start_time, allow_waiting, deadlines, entry_only=True)
    )
    result["feasible_with_waiting"] = with_waiting["any_feasible"]
    result["arrival_with_waiting_min"] = with_waiting["earliest_arrival_min"]
    result["feasible_without_waiting"] = without_waiting["any_feasible"]
    result["arrival_without_waiting_min"] = without_waiting["earliest_arrival_min"]
    result["feasible_under_entry_time_semantics"] = entry_only["any_feasible"]
    result["arrival_under_entry_time_semantics_min"] = entry_only["earliest_arrival_min"]

    sweep = query.get("departure_sweep")
    if sweep:
        start, stop = float(sweep["from_min"]), float(sweep["to_min"])
        step = float(sweep["step_min"])
        samples = []
        time = start
        index = 0
        while time <= stop + 1e-9:
            outcome = best_route(network, origin, destination, time, allow_waiting, deadlines)
            samples.append(
                {
                    "depart_min": round(time, 9),
                    "arrival_min": outcome["best"]["arrival_min"] if outcome["best"] else None,
                }
            )
            index += 1
            time = start + index * step
        reachable = [s for s in samples if s["arrival_min"] is not None]
        earliest = min(reachable, key=lambda s: (s["arrival_min"], s["depart_min"])) if reachable else None
        immediate = next((s for s in samples if abs(s["depart_min"] - start_time) < 1e-9), None)
        fifo_violated = False
        for earlier, later in zip(reachable, reachable[1:]):
            if later["arrival_min"] < earlier["arrival_min"] - 1e-12:
                fifo_violated = True
        # MUTATION HOOK: assume FIFO, i.e. that departing as early as possible
        # is optimal, and stop looking.
        if mutations.active("fifo_assumption"):
            earliest = immediate
            fifo_violated = False
        result["departure_sweep"] = samples
        result["earliest_arrival_over_departures_min"] = earliest["arrival_min"] if earliest else None
        result["optimal_departure_min"] = earliest["depart_min"] if earliest else None
        result["immediate_departure_arrival_min"] = immediate["arrival_min"] if immediate else None
        result["fifo_violated"] = fifo_violated
    return result
