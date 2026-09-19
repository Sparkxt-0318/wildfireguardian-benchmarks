"""Brute-force reference implementations.

Written against the benchmark definitions in ``docs/`` rather than against
``wg_benchmarks.solvers``, using plain tuples and explicit loops so that a
reader can check the code as easily as the answer.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable, Sequence

INF = float("inf")

# --------------------------------------------------------------------------
# graphs and paths
# --------------------------------------------------------------------------


def enumerate_all_paths(
    edges: Sequence[tuple[str, str, str, bool]], source: str, target: str
) -> list[list[str]]:
    """Every simple path from ``source`` to ``target`` as a list of edge ids.

    ``edges`` is a sequence of ``(edge_id, tail, head, directed)``.  The search
    is a depth-first walk that refuses to revisit a node; on graphs of the size
    this repository uses it is instantaneous and impossible to get wrong.
    """
    out: list[list[str]] = []

    def step(node: str, seen: tuple[str, ...], trail: tuple[str, ...]) -> None:
        if node == target and trail:
            out.append(list(trail))
            return
        for edge_id, tail, head, directed in edges:
            for origin, destination in ((tail, head),) if directed else ((tail, head), (head, tail)):
                if origin != node or destination in seen:
                    continue
                step(destination, seen + (destination,), trail + (edge_id,))

    step(source, (source,), ())
    return out


def walk_path(
    path: Sequence[tuple[float, Sequence[tuple[float, float]]]],
    start_time: float,
    allow_waiting: bool,
    wait_grid: float = 0.05,
) -> float | None:
    """Arrival time along a fixed sequence of ``(travel_time, open_windows)`` legs.

    Waiting, when permitted, is searched on a fine grid rather than reasoned
    about.  Slow and obviously correct.
    """
    time = float(start_time)
    for travel, windows in path:
        departure = None
        if allow_waiting:
            horizon = max((end for _, end in windows if math.isfinite(end)), default=time + travel)
            steps = int(math.ceil((horizon - time) / wait_grid)) + 1
            candidates = [time + k * wait_grid for k in range(max(steps, 1))]
            candidates += [start for start, _ in windows if start >= time]
        else:
            candidates = [time]
        for candidate in sorted(candidates):
            if any(start <= candidate and candidate + travel <= end for start, end in windows):
                departure = candidate
                break
        if departure is None:
            return None
        time = departure + travel
    return time


# --------------------------------------------------------------------------
# assisted dispatch
# --------------------------------------------------------------------------


def simulate_mission(
    dispatch: float,
    ingress_time: float,
    ingress_windows: Sequence[tuple[float, float]],
    pickup: float,
    egress_time: float,
    egress_windows: Sequence[tuple[float, float]],
    resident_deadline: float = INF,
    destination_deadline: float = INF,
) -> float | None:
    """Arrival time at the destination, or ``None`` if the mission fails."""
    if not any(s <= dispatch and dispatch + ingress_time <= e for s, e in ingress_windows):
        return None
    at_resident = dispatch + ingress_time
    ready = at_resident + pickup
    if ready > resident_deadline + 1e-12:
        return None
    if not any(s <= ready and ready + egress_time <= e for s, e in egress_windows):
        return None
    arrival = ready + egress_time
    if arrival > destination_deadline + 1e-12:
        return None
    return arrival


def enumerate_dispatch_times(
    horizon: float, step: float, **mission
) -> list[float]:
    """Every dispatch time on a fixed grid at which the mission succeeds."""
    count = int(math.floor(horizon / step)) + 1
    return [
        round(index * step, 9)
        for index in range(count)
        if simulate_mission(index * step, **mission) is not None
    ]


# --------------------------------------------------------------------------
# decisions under uncertainty
# --------------------------------------------------------------------------


def compute_exact_scenario_loss(
    probabilities: dict[str, float], losses: dict[str, float]
) -> float:
    """Expected loss of one action, as a plain weighted sum."""
    return sum(probabilities[s] * losses[s] for s in probabilities)


def enumerate_actions(
    probabilities: dict[str, float],
    actions: Sequence[str],
    loss: dict[str, dict[str, float]],
    signal: dict[str, str] | None = None,
) -> dict:
    """Exhaustively search every deterministic decision rule.

    Without a signal there are ``len(actions)`` rules (the constant ones).  With
    a signal there are ``len(actions) ** len(distinct signals)`` mappings, and
    every one of them is evaluated.  No optimisation, no Bayes rule: the minimum
    is found by looking at all of them.
    """
    if signal is None:
        scored = {a: compute_exact_scenario_loss(probabilities, loss[a]) for a in actions}
        best = min(sorted(scored), key=lambda a: scored[a])
        return {"expected_loss": scored, "best_action": best, "best_expected_loss": scored[best]}

    values = sorted({signal[s] for s in probabilities})
    best_rule, best_loss = None, INF
    for assignment in itertools.product(sorted(actions), repeat=len(values)):
        rule = dict(zip(values, assignment))
        total = sum(probabilities[s] * loss[rule[signal[s]]][s] for s in probabilities)
        if total < best_loss - 1e-15:
            best_rule, best_loss = rule, total
    clairvoyant = sum(
        probabilities[s] * min(loss[a][s] for a in actions) for s in probabilities
    )
    fixed = {a: compute_exact_scenario_loss(probabilities, loss[a]) for a in actions}
    best_fixed = min(fixed.values())
    return {
        "best_rule": best_rule,
        "best_expected_loss": best_loss,
        "clairvoyant_expected_loss": clairvoyant,
        "best_fixed_expected_loss": best_fixed,
        "evpi": best_fixed - clairvoyant,
    }


def cvar_by_expansion(
    outcomes: Iterable[tuple[float, float]], alpha: float, grain: int = 100000
) -> float:
    """CVaR computed by expanding the distribution into equal-probability atoms.

    Deliberately crude: the distribution is turned into ``grain`` atoms of equal
    weight, sorted, and the worst ``(1 - alpha) * grain`` are averaged.  The
    result converges to the exact value as ``grain`` grows and is completely
    independent of the partial-atom arithmetic used by the primary solver.
    """
    sample: list[float] = []
    for loss, probability in outcomes:
        sample.extend([loss] * int(round(probability * grain)))
    sample.sort()
    tail = max(1, int(round((1 - alpha) * len(sample))))
    return sum(sample[-tail:]) / tail
