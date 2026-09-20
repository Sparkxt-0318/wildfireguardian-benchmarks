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


# --------------------------------------------------------------------------
# Bayesian inference and the value of information
# --------------------------------------------------------------------------


def exact_posterior(
    prior: dict[str, float], likelihood: dict[str, dict[str, float]], outcome: str
) -> dict[str, float]:
    """Bayes by direct enumeration over the hypothesis set."""
    joint = {h: prior[h] * likelihood[h][outcome] for h in prior}
    evidence = sum(joint.values())
    if evidence == 0.0:
        raise ValueError(f"outcome {outcome!r} has zero probability under the prior")
    return {h: joint[h] / evidence for h in prior}


def evsi_by_rule_enumeration(
    prior: dict[str, float],
    likelihood: dict[str, dict[str, float]],
    outcomes: Sequence[str],
    actions: Sequence[str],
    loss: dict[str, dict[str, float]],
) -> dict:
    """Expected value of sample information, by enumerating every decision rule.

    A deterministic rule is a mapping from observed outcome to action, so there
    are ``len(actions) ** len(outcomes)`` of them and every one is evaluated
    against the joint distribution. This never forms a posterior at all, which
    makes it a genuinely independent route to the same number as the
    branch-by-branch computation in ``wg_benchmarks.solvers.probabilistic``.
    """
    def rule_loss(rule: dict[str, str]) -> float:
        return sum(
            prior[h] * likelihood[h][z] * loss[rule[z]][h]
            for h in prior
            for z in outcomes
        )

    best_rule, best_value = None, INF
    for assignment in itertools.product(sorted(actions), repeat=len(outcomes)):
        rule = dict(zip(outcomes, assignment))
        value = rule_loss(rule)
        if value < best_value - 1e-15:
            best_rule, best_value = rule, value

    prior_best = min(
        sum(prior[h] * loss[a][h] for h in prior) for a in actions
    )
    clairvoyant = sum(prior[h] * min(loss[a][h] for a in actions) for h in prior)
    return {
        "best_rule": best_rule,
        "expected_loss_with_observation": best_value,
        "prior_expected_loss": prior_best,
        "evsi": prior_best - best_value,
        "evpi": prior_best - clairvoyant,
    }


def normal_tail_by_quadrature(
    x: float, mean: float, sd: float, panels: int = 20000
) -> float:
    """P(X <= x) by composite Simpson quadrature of the normal density.

    An independent check on the ``erf``-based closed form used by the primary
    solver. The integrand is smooth and the interval is truncated twelve
    standard deviations below the mean, where the neglected tail is below 1e-32;
    with 20000 panels Simpson's error term is far below 1e-12, so this is a
    NUMERIC_REFERENCE with a declared bound rather than an approximation of
    unknown quality.
    """
    if panels % 2:  # Simpson needs an even number of panels
        panels += 1
    low = mean - 12.0 * sd
    if x <= low:
        return 0.0
    width = (x - low) / panels
    density = lambda t: math.exp(-0.5 * ((t - mean) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))
    total = density(low) + density(x)
    for index in range(1, panels):
        weight = 4 if index % 2 else 2
        total += weight * density(low + index * width)
    return total * width / 3.0


# --------------------------------------------------------------------------
# calibration
# --------------------------------------------------------------------------


def brier_by_case_enumeration(groups: Sequence[dict]) -> float:
    """Brier score as the mean of (p - y)^2 over individual cases.

    The primary solver works group by group with observed frequencies; this
    expands every group into its individual 0/1 outcomes and averages. Same
    number, no shared algebra.
    """
    total = 0.0
    count = 0
    for group in groups:
        n, events = int(group["n"]), int(group["events"])
        p = float(group["forecast_probability"])
        total += events * (p - 1.0) ** 2 + (n - events) * p ** 2
        count += n
    return total / count
