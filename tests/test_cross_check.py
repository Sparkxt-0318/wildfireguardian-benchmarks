"""Cross-check the primary solvers against the independent brute-force ones.

The modules under ``tools/analytic_solvers`` were written from the benchmark
definitions and share no code with ``wg_benchmarks.solvers``.  Agreement between
them is the strongest evidence this repository can offer that a computed answer
is right; disagreement means one of the two implementations is wrong and the
suite cannot say which.
"""

from __future__ import annotations

import math

import pytest

from analytic_solvers import (
    compute_exact_scenario_loss,
    cvar_by_expansion,
    enumerate_actions,
    enumerate_all_paths,
    enumerate_dispatch_times,
)
from wg_benchmarks.runner import discover, run_benchmark
from wg_benchmarks.solvers.network import enumerate_simple_paths, load_network

BENCHMARKS = {b.benchmark_id: b for b in discover()}


def _inputs(benchmark_id: str) -> dict:
    return BENCHMARKS[benchmark_id].load_inputs()


def _edge_tuples(document: dict) -> list[tuple[str, str, str, bool]]:
    return [
        (str(e["id"]), str(e["from"]), str(e["to"]), bool(e.get("directed", False)))
        for e in document["edges"]
    ]


NETWORK_BENCHMARKS = [
    bid for bid, b in BENCHMARKS.items() if "network" in (b.meta.get("inputs") or {})
]


@pytest.mark.parametrize("benchmark_id", sorted(NETWORK_BENCHMARKS))
def test_path_enumeration_agrees(benchmark_id):
    """Both path enumerators find the same simple paths between the same nodes."""
    inputs = _inputs(benchmark_id)
    document = inputs["network"]
    network = load_network(document)
    edges = _edge_tuples(document)
    node_ids = sorted(network.nodes)
    for source in node_ids:
        for target in node_ids:
            if source == target:
                continue
            primary = sorted(
                tuple(edge.id for edge, _ in path)
                for path in enumerate_simple_paths(network, source, target)
            )
            independent = sorted(tuple(p) for p in enumerate_all_paths(edges, source, target))
            assert primary == independent, (benchmark_id, source, target)


def _legs(benchmark_id: str):
    """Pull the (ingress, egress) legs out of a single-base, single-destination mission."""
    inputs = _inputs(benchmark_id)
    document, mission = inputs["network"], inputs["mission"]
    base = str(mission["bases"][0])
    resident = str(mission["resident"])
    destination = str(mission["destinations"][0])

    def find(a: str, b: str) -> dict:
        for edge in document["edges"]:
            if {str(edge["from"]), str(edge["to"])} == {a, b}:
                return edge
        raise KeyError((a, b))

    def windows(edge: dict) -> list[tuple[float, float]]:
        raw = edge.get("open_intervals") or [[0.0, float("inf")]]
        return [(float(a), float("inf") if b is None else float(b)) for a, b in raw]

    ingress, egress = find(base, resident), find(resident, destination)
    deadline = (mission.get("destination_deadlines") or {}).get(destination, float("inf"))
    resident_deadline = mission.get("resident_deadline_min")
    if resident_deadline is None:
        node = next(n for n in document["nodes"] if str(n["id"]) == resident)
        resident_deadline = node.get("hazard_arrival_min", float("inf"))
    return {
        "ingress_time": float(ingress["travel_time_min"]),
        "ingress_windows": windows(ingress),
        "egress_time": float(egress["travel_time_min"]),
        "egress_windows": windows(egress),
        "resident_deadline": float(resident_deadline),
        "destination_deadline": float(deadline),
    }, mission


@pytest.mark.parametrize("benchmark_id", ["WG-BM-022", "WG-BM-026"])
def test_dispatch_feasibility_agrees(benchmark_id):
    """A naive grid sweep reproduces the primary solver's feasible intervals."""
    legs, mission = _legs(benchmark_id)
    pickup = mission["pickup_min"]
    pickup = float(pickup[0] if isinstance(pickup, list) else pickup)
    horizon = float(mission["dispatch_horizon_min"])
    step = float(mission["dispatch_step_min"])

    grid = set(enumerate_dispatch_times(horizon, step, pickup=pickup, **legs))
    intervals = run_benchmark(BENCHMARKS[benchmark_id]).result["feasible_intervals"]

    count = int(math.floor(horizon / step)) + 1
    for index in range(count):
        time = round(index * step, 9)
        inside = any(start - 1e-9 <= time <= end + 1e-9 for start, end in intervals)
        assert inside == (time in grid), (benchmark_id, time, inside, time in grid)


def test_pickup_sweep_agrees():
    """Each row of the F2 sweep matches an independent grid enumeration."""
    legs, mission = _legs("WG-BM-023")
    horizon = float(mission["dispatch_horizon_min"])
    step = float(mission["dispatch_step_min"])
    reported = run_benchmark(BENCHMARKS["WG-BM-023"]).result["latest_dispatch_by_pickup"]
    for pickup in mission["pickup_min"]:
        grid = enumerate_dispatch_times(horizon, step, pickup=float(pickup), **legs)
        expected = max(grid) if grid else None
        assert reported[f"{float(pickup):g}"] == expected, pickup


DECISION_BENCHMARKS = [
    bid for bid, b in BENCHMARKS.items() if "decision" in (b.meta.get("inputs") or {})
]


@pytest.mark.parametrize("benchmark_id", sorted(DECISION_BENCHMARKS))
def test_decision_quantities_agree(benchmark_id):
    """EVPI and the best fixed action are reproduced by exhaustive rule search."""
    document = _inputs(benchmark_id)["decision"]
    probabilities = {str(s["id"]): float(s["probability"]) for s in document["scenarios"]}
    actions = [str(a) for a in document["actions"]]
    loss = {
        str(a): {str(s): float(v) for s, v in row.items()}
        for a, row in document["loss"].items()
    }
    signal = {s: s for s in probabilities}  # perfect information
    independent = enumerate_actions(probabilities, actions, loss, signal)
    result = run_benchmark(BENCHMARKS[benchmark_id]).result

    assert independent["best_expected_loss"] == pytest.approx(
        result["clairvoyant_expected_loss"], abs=1e-12
    )
    assert independent["evpi"] == pytest.approx(result["evpi"], abs=1e-12)
    assert independent["best_fixed_expected_loss"] == pytest.approx(
        result["best_fixed_expected_loss"], abs=1e-12
    )
    for action in actions:
        assert compute_exact_scenario_loss(probabilities, loss[action]) == pytest.approx(
            sum(probabilities[s] * loss[action][s] for s in probabilities), abs=1e-12
        )


def test_cvar_agrees_with_expansion():
    """CVaR from partial atoms matches CVaR from an expanded equal-weight sample."""
    document = _inputs("WG-BM-038")["statistics"]
    result = run_benchmark(BENCHMARKS["WG-BM-038"]).result
    alpha = float(document["cvar_alpha"])
    for policy in document["policies"]:
        outcomes = [(float(o["loss"]), float(o["probability"])) for o in policy["outcomes"]]
        independent = cvar_by_expansion(outcomes, alpha)
        assert independent == pytest.approx(result["cvar_loss"][str(policy["id"])], abs=1e-6)


def test_scenario_expected_losses_agree():
    """Ensemble expected losses match a plain weighted sum computed separately."""
    for benchmark_id in ("WG-BM-034", "WG-BM-035", "WG-BM-036"):
        document = _inputs(benchmark_id)["scenario_analysis"]
        result = run_benchmark(BENCHMARKS[benchmark_id]).result
        losses = {
            str(a): {str(s): float(v) for s, v in row.items()}
            for a, row in document["losses"].items()
        }
        for ensemble in document["ensembles"]:
            probabilities = {
                str(s["id"]): float(s["probability"]) for s in ensemble["scenarios"]
            }
            reported = result["ensembles"][str(ensemble["id"])]["expected_loss"]
            for action in document["actions"]:
                independent = compute_exact_scenario_loss(probabilities, losses[str(action)])
                assert independent == pytest.approx(reported[str(action)], abs=1e-12), (
                    benchmark_id,
                    ensemble["id"],
                    action,
                )


# --------------------------------------------------------------------------
# Probabilistic families: K, L and M
# --------------------------------------------------------------------------

BAYES_BENCHMARKS = [
    bid
    for bid, b in BENCHMARKS.items()
    if b.meta.get("solver") == "probabilistic.bayes_decision"
]


@pytest.mark.parametrize("benchmark_id", sorted(BAYES_BENCHMARKS))
def test_posteriors_agree(benchmark_id):
    """Bayes by direct enumeration reproduces every reported posterior."""
    from analytic_solvers import exact_posterior  # noqa: PLC0415

    document = _inputs(benchmark_id)["probabilistic"]
    prior = {str(h["id"]): float(h["prior"]) for h in document["hypotheses"]}
    hazard = str(document.get("hazard_hypothesis", sorted(prior)[0]))
    result = run_benchmark(BENCHMARKS[benchmark_id]).result
    for raw in document.get("observations", []):
        likelihood = {
            str(h): {str(z): float(v) for z, v in row.items()}
            for h, row in raw["likelihood"].items()
        }
        reported = result["observations"][str(raw["id"])]["posterior_hazard_by_outcome"]
        for outcome in raw["outcomes"]:
            independent = exact_posterior(prior, likelihood, str(outcome))
            assert independent[hazard] == pytest.approx(reported[str(outcome)], abs=1e-12), (
                benchmark_id,
                outcome,
            )


@pytest.mark.parametrize("benchmark_id", sorted(BAYES_BENCHMARKS))
def test_evsi_agrees_with_rule_enumeration(benchmark_id):
    """EVSI from enumerating every decision rule matches the branch computation.

    The independent implementation never forms a posterior, so agreement is
    evidence about the quantity rather than about a shared derivation.
    """
    from analytic_solvers import evsi_by_rule_enumeration  # noqa: PLC0415

    document = _inputs(benchmark_id)["probabilistic"]
    prior = {str(h["id"]): float(h["prior"]) for h in document["hypotheses"]}
    actions = [str(a) for a in document["actions"]]
    loss = {
        str(a): {str(h): float(v) for h, v in row.items()}
        for a, row in document["loss"].items()
    }
    result = run_benchmark(BENCHMARKS[benchmark_id]).result
    for raw in document.get("observations", []):
        likelihood = {
            str(h): {str(z): float(v) for z, v in row.items()}
            for h, row in raw["likelihood"].items()
        }
        outcomes = [str(z) for z in raw["outcomes"]]
        independent = evsi_by_rule_enumeration(prior, likelihood, outcomes, actions, loss)
        reported = result["observations"][str(raw["id"])]
        assert independent["evsi"] == pytest.approx(reported["evsi_statistical"], abs=1e-12), (
            benchmark_id,
            raw["id"],
        )
        assert independent["prior_expected_loss"] == pytest.approx(
            result["prior_expected_loss"], abs=1e-12
        )
        assert independent["evpi"] == pytest.approx(result["evpi"], abs=1e-12)


def test_normal_tails_agree_with_quadrature():
    """The erf closed form matches an independent Simpson quadrature.

    A NUMERIC_REFERENCE cross-check: the quadrature carries a declared error
    bound far below the comparison tolerance, so a disagreement is a bug in the
    closed form and not quadrature error.
    """
    from analytic_solvers import normal_tail_by_quadrature  # noqa: PLC0415

    for benchmark_id in ("WG-BM-044", "WG-BM-045"):
        document = _inputs(benchmark_id)["probabilistic"]
        threshold = float(document["threshold"])
        result = run_benchmark(BENCHMARKS[benchmark_id]).result
        for forecast in document["forecasts"]:
            independent = normal_tail_by_quadrature(
                threshold, float(forecast["mean"]), float(forecast["sd"])
            )
            reported = result["hazard_probability_by_forecast"][str(forecast["id"])]
            assert independent == pytest.approx(reported, abs=1e-11), (
                benchmark_id,
                forecast["id"],
            )


def test_brier_scores_agree_with_case_enumeration():
    """Group-wise Brier scores match a per-case enumeration."""
    from analytic_solvers import brier_by_case_enumeration  # noqa: PLC0415

    for benchmark_id in ("WG-BM-064", "WG-BM-065", "WG-BM-066"):
        document = _inputs(benchmark_id)["calibration"]
        result = run_benchmark(BENCHMARKS[benchmark_id]).result
        independent = brier_by_case_enumeration(document["groups"])
        assert independent == pytest.approx(result["brier_score"], abs=1e-12), benchmark_id


RISK_BENCHMARKS = [
    bid for bid, b in BENCHMARKS.items() if b.meta.get("solver") == "risk.objective_comparison"
]


@pytest.mark.parametrize("benchmark_id", sorted(RISK_BENCHMARKS))
def test_risk_quantities_agree(benchmark_id):
    """Expected loss and CVaR match independent implementations."""
    from analytic_solvers import compute_exact_scenario_loss, cvar_by_expansion  # noqa: PLC0415

    document = _inputs(benchmark_id)["risk"]
    probabilities = {str(s["id"]): float(s["probability"]) for s in document["scenarios"]}
    losses = {
        str(a): {str(s): float(v) for s, v in row.items()}
        for a, row in document["losses"].items()
    }
    alpha = float(document.get("cvar_alpha", 0.9))
    result = run_benchmark(BENCHMARKS[benchmark_id]).result
    for action in document["actions"]:
        action = str(action)
        assert compute_exact_scenario_loss(probabilities, losses[action]) == pytest.approx(
            result["expected_loss"][action], abs=1e-12
        )
        outcomes = [(losses[action][s], probabilities[s]) for s in probabilities]
        assert cvar_by_expansion(outcomes, alpha) == pytest.approx(
            result["cvar"][action], abs=1e-6
        ), (benchmark_id, action)
