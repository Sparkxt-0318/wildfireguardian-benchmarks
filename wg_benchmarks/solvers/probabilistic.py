"""Reference solver for probabilistic forecasts, Bayesian belief and the
decisions that depend on them (the K family).

Five things are kept rigorously apart, because treating them as interchangeable
is the failure mode this family exists to catch:

``point prediction``
    a single number. Carries no uncertainty, so it cannot answer a threshold
    question whose answer depends on the tail.

``predictive distribution``
    a distribution over the quantity. ``model: predictive_threshold`` evaluates
    one against a threshold decision in closed form.

``scenario ensemble``
    a finite set of weighted worlds, with an explicit admissibility flag.
    ``model: scenario_ensemble``.

``posterior belief``
    a prior updated by a likelihood. ``model: bayes_decision``.

``decision``
    the action that minimises expected loss under the belief. Never the
    hypothesis with the largest probability, and never "p >= 0.5".

Everything here is exact: normal tail probabilities through ``math.erf``, Bayes
by direct arithmetic, expected value of sample information by enumeration over
the finite outcome set. Nothing is simulated.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

from .. import mutations

INF = float("inf")


# --------------------------------------------------------------------------
# small exact primitives
# --------------------------------------------------------------------------


def normal_cdf(x: float, mean: float, sd: float) -> float:
    """P(X <= x) for X ~ N(mean, sd^2), in closed form through erf."""
    return 0.5 * (1.0 + math.erf((x - mean) / (sd * math.sqrt(2.0))))


def expected_loss(belief: dict[str, float], row: dict[str, float]) -> float:
    return sum(belief[state] * row[state] for state in belief)


def bayes_action(belief: dict[str, float], actions: Sequence[str],
                 loss: dict[str, dict[str, float]]) -> str:
    """The loss-minimising action. Ties break by identifier, never by chance."""
    return min(sorted(actions), key=lambda a: expected_loss(belief, loss[a]))


def entropy_bits(probabilities: Iterable[float]) -> float:
    return -sum(p * math.log2(p) for p in probabilities if p > 0.0)


def action_partition(
    actions: Sequence[str],
    loss: dict[str, dict[str, float]],
    hazard_state: str,
    clear_state: str,
) -> list[dict]:
    """Exact partition of p = P(hazard) into intervals where each action is optimal.

    With two states every action's expected loss is a straight line in ``p``, so
    the optimal action is the lower envelope of ``len(actions)`` lines. The
    breakpoints are the pairwise crossings; evaluating one interior point per
    interval identifies the segment. No search, no grid.
    """
    def value(action: str, p: float) -> float:
        return p * loss[action][hazard_state] + (1.0 - p) * loss[action][clear_state]

    breakpoints = {0.0, 1.0}
    ordered = sorted(actions)
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            denominator = (loss[a][hazard_state] - loss[b][hazard_state]) - (
                loss[a][clear_state] - loss[b][clear_state]
            )
            if denominator == 0.0:
                continue
            crossing = (loss[b][clear_state] - loss[a][clear_state]) / denominator
            if 0.0 < crossing < 1.0:
                breakpoints.add(crossing)
    edges = sorted(breakpoints)
    segments: list[dict] = []
    for low, high in zip(edges, edges[1:]):
        midpoint = (low + high) / 2.0
        best = min(ordered, key=lambda a: (value(a, midpoint), a))
        if segments and segments[-1]["action"] == best:
            segments[-1]["p_to"] = high
        else:
            segments.append({"p_from": low, "p_to": high, "action": best})
    return segments


def _threshold_from_partition(segments: list[dict]) -> float | None:
    """The single switch point, when the partition has exactly two segments."""
    return segments[0]["p_to"] if len(segments) == 2 else None


def _choose(
    belief: dict[str, float],
    actions: Sequence[str],
    loss: dict[str, dict[str, float]],
    hazard_state: str | None = None,
    clear_state: str | None = None,
) -> str:
    # MUTATION HOOK: decide on p >= 0.5 rather than on the loss-derived
    # threshold. Only defined for a binary two-action problem.
    if (
        mutations.active("fixed_half_probability_threshold")
        and hazard_state is not None
        and clear_state is not None
        and len(actions) == 2
    ):
        conservative = min(sorted(actions), key=lambda a: loss[a][hazard_state])
        permissive = next(a for a in sorted(actions) if a != conservative)
        return conservative if belief[hazard_state] >= 0.5 else permissive
    return bayes_action(belief, actions, loss)


# --------------------------------------------------------------------------
# model 1: predictive distribution against a threshold
# --------------------------------------------------------------------------


def _predictive_threshold(document: dict) -> dict:
    threshold = float(document["threshold"])
    side = str(document.get("hazard_when", "below"))
    actions = [str(a) for a in document["actions"]]
    loss = {
        str(a): {str(s): float(v) for s, v in row.items()}
        for a, row in document["loss"].items()
    }
    hazard_state = str(document.get("hazard_state", "hazard"))
    clear_state = str(document.get("clear_state", "clear"))

    segments = action_partition(actions, loss, hazard_state, clear_state)
    threshold_probability = _threshold_from_partition(segments)

    truth = document.get("true_world")
    true_scenarios = {}
    if truth:
        true_scenarios = {
            str(s["id"]): (float(s["probability"]), float(s["value"]))
            for s in truth["scenarios"]
        }
        true_hazard_probability = sum(
            p for _, (p, value) in true_scenarios.items()
            if (value <= threshold if side == "below" else value >= threshold)
        )
        true_mean = sum(p * value for p, value in true_scenarios.values())
    else:
        true_hazard_probability = None
        true_mean = None

    forecasts: dict[str, dict] = {}
    for raw in document["forecasts"]:
        name = str(raw["id"])
        mean, sd = float(raw["mean"]), float(raw["sd"])
        if side == "below":
            hazard_probability = normal_cdf(threshold, mean, sd)
        else:
            hazard_probability = 1.0 - normal_cdf(threshold, mean, sd)
        # MUTATION HOOK: collapse the predictive distribution to its mean, so
        # the hazard probability becomes a hard 0 or 1.
        if mutations.active("ignore_forecast_variance"):
            hazard_probability = 1.0 if (
                mean <= threshold if side == "below" else mean >= threshold
            ) else 0.0
        belief = {hazard_state: hazard_probability, clear_state: 1.0 - hazard_probability}
        action = _choose(belief, actions, loss, hazard_state, clear_state)
        point_belief = {
            hazard_state: 1.0 if (mean <= threshold if side == "below" else mean >= threshold) else 0.0,
            clear_state: 0.0 if (mean <= threshold if side == "below" else mean >= threshold) else 1.0,
        }
        entry = {
            "mean": mean,
            "sd": sd,
            "hazard_probability": hazard_probability,
            "expected_loss": {a: expected_loss(belief, loss[a]) for a in actions},
            "action": action,
            "point_estimate_action": bayes_action(point_belief, actions, loss),
        }
        if true_mean is not None:
            entry["location_error"] = abs(mean - true_mean)
            true_belief = {
                hazard_state: true_hazard_probability,
                clear_state: 1.0 - true_hazard_probability,
            }
            entry["expected_loss_under_truth"] = expected_loss(true_belief, loss[action])
        forecasts[name] = entry

    result = {
        "model": "predictive_threshold",
        "threshold": threshold,
        "decision_threshold_probability": threshold_probability,
        "action_partition": segments,
        "forecasts": forecasts,
        "hazard_probability_by_forecast": {
            k: v["hazard_probability"] for k, v in forecasts.items()
        },
        "action_by_forecast": {k: v["action"] for k, v in forecasts.items()},
        "point_estimate_action_by_forecast": {
            k: v["point_estimate_action"] for k, v in forecasts.items()
        },
        "point_estimate_distinguishes_forecasts": len(
            {v["point_estimate_action"] for v in forecasts.values()}
        ) > 1,
        "distribution_distinguishes_forecasts": len(
            {v["action"] for v in forecasts.values()}
        ) > 1,
    }
    if true_mean is not None:
        result["true_mean"] = true_mean
        result["true_hazard_probability"] = true_hazard_probability
        true_belief = {
            hazard_state: true_hazard_probability,
            clear_state: 1.0 - true_hazard_probability,
        }
        result["best_action_under_truth"] = bayes_action(true_belief, actions, loss)
        result["best_expected_loss_under_truth"] = min(
            expected_loss(true_belief, loss[a]) for a in actions
        )
        result["location_error_by_forecast"] = {
            k: v["location_error"] for k, v in forecasts.items()
        }
        result["expected_loss_under_truth_by_forecast"] = {
            k: v["expected_loss_under_truth"] for k, v in forecasts.items()
        }
        result["regret_by_forecast"] = {
            k: v["expected_loss_under_truth"] - result["best_expected_loss_under_truth"]
            for k, v in forecasts.items()
        }
    return result


# --------------------------------------------------------------------------
# model 2: Bayesian hypothesis model
# --------------------------------------------------------------------------


def _bayes_decision(document: dict) -> dict:
    prior = {str(h["id"]): float(h["prior"]) for h in document["hypotheses"]}
    mass = sum(prior.values())
    if abs(mass - 1.0) > 1e-12:
        raise ValueError(f"priors sum to {mass}, not 1")
    actions = [str(a) for a in document["actions"]]
    loss = {
        str(a): {str(h): float(v) for h, v in row.items()}
        for a, row in document["loss"].items()
    }
    hazard = str(document.get("hazard_hypothesis", sorted(prior)[0]))
    clear = next(h for h in sorted(prior) if h != hazard) if len(prior) == 2 else None
    deadline = document.get("decision_deadline_min")
    deadline = INF if deadline is None else float(deadline)

    segments = (
        action_partition(actions, loss, hazard, clear) if clear is not None else []
    )

    prior_action = _choose(prior, actions, loss, hazard, clear)
    prior_expected_loss = expected_loss(prior, loss[prior_action])
    clairvoyant = sum(prior[h] * min(loss[a][h] for a in actions) for h in prior)

    def posterior_for(likelihood: dict[str, dict[str, float]], outcome: str) -> tuple[dict, float]:
        joint = {h: prior[h] * likelihood[h][outcome] for h in prior}
        evidence = sum(joint.values())
        if evidence == 0.0:
            return dict(prior), 0.0
        return {h: joint[h] / evidence for h in prior}, evidence

    # Stated hazard probabilities, used by the benchmarks whose subject is the
    # decision threshold itself rather than any particular belief update.
    probes: dict[str, dict] = {}
    for probe in document.get("probe_probabilities", []):
        value = float(probe)
        belief = {hazard: value, clear: 1.0 - value} if clear is not None else {hazard: value}
        probes[f"{value:g}"] = {
            "hazard_probability": value,
            "expected_loss": {a: expected_loss(belief, loss[a]) for a in actions},
            "action": _choose(belief, actions, loss, hazard, clear),
            "above_threshold": (
                None
                if _threshold_from_partition(segments) is None
                else value > _threshold_from_partition(segments)
            ),
        }

    observations: dict[str, dict] = {}
    for raw in document.get("observations", []):
        name = str(raw["id"])
        records = raw.get("records")
        likelihood = {
            str(h): {str(z): float(v) for z, v in row.items()}
            for h, row in raw["likelihood"].items()
        }
        outcomes = [str(z) for z in raw["outcomes"]]
        independent_likelihood = raw.get("independent_likelihood")
        if independent_likelihood is not None:
            independent_likelihood = {
                str(h): {str(z): float(v) for z, v in row.items()}
                for h, row in independent_likelihood.items()
            }

        effective = likelihood
        # MUTATION HOOK: multiply per-sensor marginals as if the two sensors
        # failed independently, discarding the declared joint.
        if mutations.active("assume_conditional_independence") and independent_likelihood:
            effective = independent_likelihood
        if records is not None:
            unique = {str(r["measurement_id"]) for r in records}
            duplicated = len(records) > len(unique)
            # MUTATION HOOK: two records of one measurement counted as two
            # independent observations.
            if duplicated and mutations.active("count_duplicate_evidence") and independent_likelihood:
                effective = independent_likelihood
        # MUTATION HOOK: the likelihood carries no information about the
        # hypothesis, so the observation cannot move the belief.
        if mutations.active("ignore_observation_likelihood"):
            effective = {h: {z: 1.0 / len(outcomes) for z in outcomes} for h in prior}
        # MUTATION HOOK: missingness treated as missing-at-random, so a record
        # that failed to arrive carries no information.
        if raw.get("is_missingness_indicator") and mutations.active("assume_missing_at_random"):
            effective = {h: {z: 1.0 / len(outcomes) for z in outcomes} for h in prior}

        branches: dict[str, dict] = {}
        posterior_loss = 0.0
        conditional_entropy = 0.0
        for outcome in outcomes:
            belief, evidence = posterior_for(effective, outcome)
            # MUTATION HOOK: a non-detection read as certainty of no hazard.
            if mutations.active("non_detection_is_absence") and outcome == str(
                raw.get("negative_outcome", "")
            ):
                belief = {h: (0.0 if h == hazard else 1.0) for h in prior}
            # MUTATION HOOK: a detection read as certainty of hazard.
            if mutations.active("detection_is_certainty") and outcome == str(
                raw.get("positive_outcome", "")
            ):
                belief = {h: (1.0 if h == hazard else 0.0) for h in prior}
            decision_belief = belief
            # MUTATION HOOK: the posterior is computed and then not used.
            if mutations.active("posterior_replaced_by_prior"):
                decision_belief = prior
            action = _choose(decision_belief, actions, loss, hazard, clear)
            branches[outcome] = {
                "evidence_probability": evidence,
                "posterior": belief,
                "posterior_hazard": belief[hazard],
                "action": action,
                "expected_loss": expected_loss(belief, loss[action]),
                "best_expected_loss": min(expected_loss(belief, loss[a]) for a in actions),
            }
            posterior_loss += evidence * branches[outcome]["expected_loss"]
            conditional_entropy += evidence * entropy_bits(belief.values())
            # A likelihood ratio is only finite when both legs are positive; a
            # perfectly discriminating sensor has a zero leg and an infinite
            # ratio, which is reported as absent rather than as a number.
            if (
                clear is not None
                and effective[clear][outcome] > 0
                and effective[hazard][outcome] > 0
            ):
                branches[outcome]["log_likelihood_ratio_bits"] = math.log2(
                    effective[hazard][outcome] / effective[clear][outcome]
                )
            if independent_likelihood is not None:
                naive_belief, _ = posterior_for(independent_likelihood, outcome)
                branches[outcome]["posterior_under_independence"] = naive_belief[hazard]
                branches[outcome]["action_under_independence"] = _choose(
                    naive_belief, actions, loss, hazard, clear
                )
                if (
                    clear is not None
                    and independent_likelihood[clear][outcome] > 0
                    and independent_likelihood[hazard][outcome] > 0
                ):
                    branches[outcome]["log_likelihood_ratio_bits_under_independence"] = math.log2(
                        independent_likelihood[hazard][outcome]
                        / independent_likelihood[clear][outcome]
                    )

        evsi = prior_expected_loss - posterior_loss
        information_gain = entropy_bits(prior.values()) - conditional_entropy
        availability = raw.get("availability_time_min")
        availability = INF if availability is None else float(availability)
        timely = availability <= deadline + 1e-12
        # MUTATION HOOK: the arrival time of the observation is not checked.
        if mutations.active("ignore_availability_time"):
            timely = True
        entry = {
            "acquisition_time_min": raw.get("acquisition_time_min"),
            "availability_time_min": None if availability == INF else availability,
            "available_before_deadline": timely,
            "branches": branches,
            "evsi_statistical": evsi,
            "evsi_operational": evsi if timely else 0.0,
            "information_gain_bits": information_gain,
            "changes_action": any(b["action"] != prior_action for b in branches.values()),
            "posterior_hazard_by_outcome": {
                z: b["posterior_hazard"] for z, b in branches.items()
            },
            "action_by_outcome": {z: b["action"] for z, b in branches.items()},
        }
        realised = raw.get("realised")
        if realised is not None:
            entry["realised_outcome"] = str(realised)
            entry["realised_posterior_hazard"] = branches[str(realised)]["posterior_hazard"]
            entry["realised_action"] = branches[str(realised)]["action"]
            if "log_likelihood_ratio_bits" in branches[str(realised)]:
                entry["realised_log_likelihood_ratio_bits"] = branches[str(realised)][
                    "log_likelihood_ratio_bits"
                ]
            if "log_likelihood_ratio_bits_under_independence" in branches[str(realised)]:
                entry["realised_log_likelihood_ratio_bits_under_independence"] = branches[
                    str(realised)
                ]["log_likelihood_ratio_bits_under_independence"]
            if "posterior_under_independence" in branches[str(realised)]:
                entry["realised_posterior_under_independence"] = branches[str(realised)][
                    "posterior_under_independence"
                ]
                entry["realised_action_under_independence"] = branches[str(realised)][
                    "action_under_independence"
                ]
        if records is not None:
            unique = sorted({str(r["measurement_id"]) for r in records})
            entry["record_count"] = len(records)
            entry["independent_measurements"] = len(unique)
            entry["contains_duplicates"] = len(records) > len(unique)
        observations[name] = entry

    ranked_by_value = sorted(
        observations, key=lambda k: (-observations[k]["evsi_operational"], k)
    )
    ranked_by_information = sorted(
        observations, key=lambda k: (-observations[k]["information_gain_bits"], k)
    )
    # An observation is worth acquiring when it can change what is done, not
    # when it can change what is believed. With no such observation the
    # recommendation is to acquire nothing, which is a legitimate answer.
    worth_acquiring = sorted(
        k for k in observations if observations[k]["evsi_operational"] > 1e-12
    )
    recommended = ranked_by_value[0] if worth_acquiring else None
    # MUTATION HOOK: judge acquisition by entropy reduction rather than by
    # decision value, so information with no decision value is still acquired.
    if mutations.active("choose_by_information_gain"):
        worth_acquiring = sorted(
            k for k in observations if observations[k]["information_gain_bits"] > 1e-12
        )
        recommended = ranked_by_information[0] if worth_acquiring else None

    return {
        "model": "bayes_decision",
        "prior": prior,
        "prior_hazard": prior[hazard],
        "prior_action": prior_action,
        "prior_expected_loss": prior_expected_loss,
        "decision_threshold_probability": _threshold_from_partition(segments),
        "action_partition": segments,
        "clairvoyant_expected_loss": clairvoyant,
        "evpi": prior_expected_loss - clairvoyant,
        "probes": probes,
        "action_by_probe": {k: v["action"] for k, v in probes.items()},
        "observations": observations,
        "evsi_statistical_by_observation": {
            k: v["evsi_statistical"] for k, v in observations.items()
        },
        "evsi_operational_by_observation": {
            k: v["evsi_operational"] for k, v in observations.items()
        },
        "information_gain_by_observation": {
            k: v["information_gain_bits"] for k, v in observations.items()
        },
        "ranked_by_operational_value": ranked_by_value,
        "ranked_by_information_gain": ranked_by_information,
        "observations_worth_acquiring": worth_acquiring,
        "recommended_observation": recommended,
        "value_and_information_agree": (
            not observations or ranked_by_value[0] == ranked_by_information[0]
        ),
    }


# --------------------------------------------------------------------------
# model 3: coherent scenario ensemble
# --------------------------------------------------------------------------


def _scenario_ensemble(document: dict) -> dict:
    scenarios = document["scenarios"]
    admissible = [s for s in scenarios if s.get("admissible", True)]
    used = admissible
    # MUTATION HOOK: renormalise over every scenario in the file, including the
    # ones declared physically inadmissible.
    if mutations.active("renormalise_including_inadmissible"):
        used = list(scenarios)

    total = sum(float(s["weight"]) for s in used)
    weights = {str(s["id"]): float(s["weight"]) / total for s in used}

    actions = [str(a) for a in document["actions"]]
    losses = {
        str(a): {str(s): float(v) for s, v in row.items()}
        for a, row in document["losses"].items()
    }
    expected = {a: sum(weights[s] * losses[a][s] for s in weights) for a in actions}
    best = min(sorted(actions), key=lambda a: expected[a])

    edges = [str(e) for e in document.get("edges", [])]
    states = {str(s["id"]): {str(k): str(v) for k, v in (s.get("state") or {}).items()}
              for s in scenarios}
    marginals = {
        edge: sum(w for s, w in weights.items() if states[s].get(edge) == "closed")
        for edge in edges
    }
    joint_true = sum(
        w for s, w in weights.items()
        if edges and all(states[s].get(edge) == "closed" for edge in edges)
    )
    product = 1.0
    for edge in edges:
        product *= marginals[edge]
    reported_joint = joint_true
    # MUTATION HOOK: rebuild the joint from the marginals.
    if mutations.active("independent_edge_failures"):
        reported_joint = product

    independence_weights = None
    expected_under_independence = None
    best_under_independence = None
    if edges and len(edges) == 2:
        # The distribution implied by independent marginals, laid out over the
        # same four joint states, so the two decisions are directly comparable.
        implied = {}
        for scenario_id, state in states.items():
            if scenario_id not in weights:
                continue
            probability = 1.0
            for edge in edges:
                closed = state.get(edge) == "closed"
                probability *= marginals[edge] if closed else (1.0 - marginals[edge])
            implied[scenario_id] = probability
        implied_total = sum(implied.values())
        if implied_total > 0:
            independence_weights = {k: v / implied_total for k, v in implied.items()}
            expected_under_independence = {
                a: sum(independence_weights[s] * losses[a][s] for s in independence_weights)
                for a in actions
            }
            best_under_independence = min(
                sorted(actions), key=lambda a: expected_under_independence[a]
            )

    return {
        "model": "scenario_ensemble",
        "declared_scenarios": len(scenarios),
        "admissible_scenarios": sorted(str(s["id"]) for s in admissible),
        "excluded_scenarios": sorted(
            str(s["id"]) for s in scenarios if not s.get("admissible", True)
        ),
        "normalised_weights": weights,
        "weight_sum": sum(weights.values()),
        "expected_loss": expected,
        "best_action": best,
        "marginal_closure_probability": marginals,
        "joint_all_closed_probability": reported_joint,
        "joint_under_independence": product,
        "independence_error_factor": (joint_true / product) if product > 0 else None,
        "expected_loss_under_independence": expected_under_independence,
        "best_action_under_independence": best_under_independence,
    }


_MODELS = {
    "predictive_threshold": _predictive_threshold,
    "bayes_decision": _bayes_decision,
    "scenario_ensemble": _scenario_ensemble,
}


def solve(inputs: dict) -> dict:
    document = inputs["probabilistic"]
    model = str(document["model"])
    if model not in _MODELS:  # pragma: no cover - guarded by schema
        raise ValueError(f"unknown probabilistic model: {model}")
    return _MODELS[model](document)
