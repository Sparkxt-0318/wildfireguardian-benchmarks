"""Mapping from ``solver:`` identifiers in benchmark.yaml to reference solvers."""

from __future__ import annotations

from typing import Callable

from .solvers import decision, dispatch, fire, graph, observation, routing, scenario, stats, terrain

SOLVERS: dict[str, Callable[[dict], dict]] = {
    "terrain.horn_slope_aspect": terrain.solve,
    "graph.connectivity": graph.solve,
    "fire.analytic_arrival": fire.solve,
    "observation.availability": observation.solve,
    "routing.time_dependent_enumeration": routing.solve,
    "dispatch.mission_enumeration": dispatch.solve,
    "decision.value_of_information": decision.solve,
    "scenario.ensemble_analysis": scenario.solve,
    "statistics.reference": stats.solve,
}


def get_solver(name: str) -> Callable[[dict], dict]:
    if name not in SOLVERS:
        raise KeyError(
            f"unknown solver {name!r}; registered solvers: {', '.join(sorted(SOLVERS))}"
        )
    return SOLVERS[name]
