"""Statistical reference solver for the I family.

Four separate small machines:

``pseudoreplication``
    World-level versus resident-level bootstrap on a data set where residents
    inside a world are perfectly correlated.  The analytic standard errors are
    computed alongside the bootstrap so the benchmark pins an exact number as
    well as a stochastic one.

``tail_risk``
    Mean versus CVaR ranking of two policies on exactly specified discrete loss
    distributions.

``equivalence``
    Two-one-sided-tests style practical equivalence on paired differences, kept
    deterministic by construction so the confidence interval is exact.

``selection_bias``
    Unpaired comparison across differently-hard world samples versus a paired
    comparison on the common worlds.

Bootstraps use ``random.Random(seed)`` from the standard library, whose stream
is stable across CPython versions, so every number here is reproducible.
"""

from __future__ import annotations

import math
import random
from typing import Sequence

from .. import mutations
from .scenario import cvar

Z_975 = 1.959963984540054  # two-sided 95% normal quantile


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def stdev(values: Sequence[float], ddof: int = 1) -> float:
    mu = mean(values)
    return math.sqrt(sum((v - mu) ** 2 for v in values) / (len(values) - ddof))


def percentile(sorted_values: Sequence[float], q: float) -> float:
    """Linear-interpolation percentile on an already sorted sequence."""
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = q * (len(sorted_values) - 1)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return sorted_values[int(position)]
    weight = position - low
    return sorted_values[low] * (1 - weight) + sorted_values[high] * weight


def bootstrap_ci(values: Sequence[float], samples: int, rng: random.Random) -> dict:
    draws = []
    n = len(values)
    for _ in range(samples):
        draws.append(mean(rng.choices(values, k=n)))
    draws.sort()
    low, high = percentile(draws, 0.025), percentile(draws, 0.975)
    return {"lower": low, "upper": high, "width": high - low, "point": mean(values)}


def _pseudoreplication(document: dict) -> dict:
    worlds = document["worlds"]
    residents_per_world = int(document["residents_per_world"])
    samples = int(document.get("bootstrap_samples", 400))
    rng_world = random.Random(int(document.get("seed", 20240101)))
    rng_resident = random.Random(int(document.get("seed", 20240101)) + 1)

    world_values = [float(w["outcome"]) for w in worlds]
    resident_values = [v for v in world_values for _ in range(residents_per_world)]

    world_ci = bootstrap_ci(world_values, samples, rng_world)
    resident_ci = bootstrap_ci(resident_values, samples, rng_resident)

    world_se = stdev(world_values) / math.sqrt(len(world_values))
    resident_se = stdev(resident_values) / math.sqrt(len(resident_values))

    reported = world_ci
    reported_unit = "world"
    # MUTATION HOOK: resample residents as if they were independent.
    if mutations.active("resident_level_bootstrap"):
        reported = resident_ci
        reported_unit = "resident"

    return {
        "worlds": len(world_values),
        "residents_per_world": residents_per_world,
        "total_residents": len(resident_values),
        "point_estimate": mean(world_values),
        "world_bootstrap_ci_width": world_ci["width"],
        "resident_bootstrap_ci_width": resident_ci["width"],
        "analytic_world_se": world_se,
        "analytic_resident_se": resident_se,
        "analytic_ci_width_ratio": (2 * Z_975 * world_se) / (2 * Z_975 * resident_se),
        "bootstrap_ci_width_ratio": world_ci["width"] / resident_ci["width"],
        "effective_sample_size": len(world_values),
        "naive_sample_size": len(resident_values),
        "reported_ci_width": reported["width"],
        "reported_resampling_unit": reported_unit,
        "resident_bootstrap_understates_uncertainty": resident_ci["width"] < world_ci["width"] / 10,
    }


def _tail_risk(document: dict) -> dict:
    alpha = float(document.get("cvar_alpha", 0.9))
    policies = {}
    for raw in document["policies"]:
        outcomes = [(float(o["loss"]), float(o["probability"])) for o in raw["outcomes"]]
        mass = sum(p for _, p in outcomes)
        if abs(mass - 1.0) > 1e-9:
            raise ValueError(f"policy {raw['id']}: probabilities sum to {mass}")
        policies[str(raw["id"])] = {
            "mean_loss": sum(loss * p for loss, p in outcomes),
            "cvar": cvar(outcomes, alpha),
            "worst_case_loss": max(loss for loss, _ in outcomes),
        }
    by_mean = min(sorted(policies), key=lambda p: policies[p]["mean_loss"])
    by_cvar = min(sorted(policies), key=lambda p: policies[p]["cvar"])
    preference = str(document.get("risk_preference", "cvar"))
    recommended = by_cvar if preference == "cvar" else by_mean
    # MUTATION HOOK: rank on the average outcome and ignore the tail.
    if mutations.active("mean_only_ranking"):
        recommended = by_mean
    return {
        "cvar_alpha": alpha,
        "policies": policies,
        "mean_loss": {k: v["mean_loss"] for k, v in policies.items()},
        "cvar_loss": {k: v["cvar"] for k, v in policies.items()},
        "best_by_mean": by_mean,
        "best_by_cvar": by_cvar,
        "rankings_conflict": by_mean != by_cvar,
        "risk_preference": preference,
        "recommended_policy": recommended,
    }


def _differences(document: dict) -> list[float]:
    if "differences" in document:
        return [float(v) for v in document["differences"]]
    spec = document["difference_spec"]
    n = int(spec["n"])
    if n % 2 != 0:
        raise ValueError("difference_spec.n must be even for the symmetric construction")
    centre = float(spec["mean"])
    spread = float(spec["sd"])
    # Deterministic symmetric construction: exactly n/2 values at +sd and n/2 at
    # -sd around the centre, so the sample mean is exactly `mean` and the sample
    # standard deviation is exactly sd * sqrt(n / (n - 1)).
    return [centre + spread] * (n // 2) + [centre - spread] * (n // 2)


def _equivalence(document: dict) -> dict:
    differences = _differences(document)
    margin = float(document["practical_margin"])
    n = len(differences)
    point = mean(differences)
    sd = stdev(differences)
    se = sd / math.sqrt(n)
    lower, upper = point - Z_975 * se, point + Z_975 * se
    equivalent = lower >= -margin and upper <= margin
    significant = abs(point) > Z_975 * se
    return {
        "n": n,
        "mean_difference": point,
        "sd_difference": sd,
        "standard_error": se,
        "ci_lower": lower,
        "ci_upper": upper,
        "practical_margin": margin,
        "practically_equivalent": equivalent,
        "statistically_significant": significant,
        "significant_but_not_meaningful": significant and equivalent,
        "conclusion": "equivalent" if equivalent else "not_equivalent",
    }


def _selection_bias(document: dict) -> dict:
    worlds = {str(w["id"]): float(w["difficulty"]) for w in document["worlds"]}
    policies = {str(p["id"]): float(p["offset"]) for p in document["policies"]}
    assignment = {str(k): [str(w) for w in v] for k, v in document["evaluated_on"].items()}

    naive = {
        policy: mean([worlds[w] + offset for w in assignment[policy]])
        for policy, offset in policies.items()
    }
    common = sorted(set.intersection(*(set(v) for v in assignment.values())) or set(worlds))
    paired = {
        policy: mean([worlds[w] + offset for w in common]) for policy, offset in policies.items()
    }
    names = sorted(policies)
    first, second = names[0], names[1]
    naive_difference = naive[first] - naive[second]
    paired_difference = paired[first] - paired[second]
    naive_best = min(names, key=lambda p: naive[p])
    paired_best = min(names, key=lambda p: paired[p])
    recommended = paired_best
    # MUTATION HOOK: compare the two policies on the worlds each happened to be
    # run on, with no pairing.
    if mutations.active("naive_unpaired_comparison"):
        recommended = naive_best
    return {
        "worlds": len(worlds),
        "common_worlds": common,
        "naive_mean_loss": naive,
        "paired_mean_loss": paired,
        "naive_difference": naive_difference,
        "paired_difference": paired_difference,
        "naive_best_policy": naive_best,
        "paired_best_policy": paired_best,
        "ranking_sign_flip": naive_best != paired_best,
        "recommended_policy": recommended,
    }


_SECTIONS = {
    "pseudoreplication": _pseudoreplication,
    "tail_risk": _tail_risk,
    "equivalence": _equivalence,
    "selection_bias": _selection_bias,
}


def solve(inputs: dict) -> dict:
    document = inputs["statistics"]
    kind = str(document["analysis"])
    if kind not in _SECTIONS:  # pragma: no cover - guarded by schema
        raise ValueError(f"unknown statistical analysis: {kind}")
    result = _SECTIONS[kind](document)
    result["analysis"] = kind
    return result
