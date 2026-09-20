"""Deliberate bug injection ("mutation testing") for the benchmark suite.

A benchmark that cannot fail is not a benchmark.  Each mutation below is a
*plausible* implementation error that has been observed in, or is easy to write
into, a wildfire decision-support system.  Activating a mutation changes the
behaviour of the reference solvers in exactly one way; the suite is then re-run
and every benchmark that flips from PASS to FAIL is recorded as *detecting* that
mutation.

A mutation that no benchmark detects is a coverage hole and is reported as such
in ``reports/COVERAGE.md`` and ``reports/KNOWN_GAPS.md``.

Usage::

    from wg_benchmarks import mutations
    with mutations.activate("edge_entry_time_only"):
        ...  # solvers now contain the bug

Solver code consults the registry through :func:`active`, always at a site
marked with a ``# MUTATION HOOK`` comment so the injected branches stay easy to
audit and easy to delete.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Mutation:
    """A single injectable bug."""

    mutation_id: str
    title: str
    description: str
    failure_mode: str
    expected_detectors: tuple[str, ...] = field(default=())


MUTATIONS: dict[str, Mutation] = {}


def _register(*args, **kwargs) -> None:
    mutation = Mutation(*args, **kwargs)
    MUTATIONS[mutation.mutation_id] = mutation


_register(
    "edge_entry_time_only",
    "Edge safety checked at entry time only",
    "Traversal of an edge is allowed whenever the edge is open at the moment of "
    "entry, ignoring whether it stays open for the whole traversal interval.",
    "mid_edge_hazard",
    ("WG-BM-018", "WG-BM-019", "WG-BM-022"),
)
_register(
    "observation_future_leak",
    "Observation latency ignored",
    "An observation is treated as available at its acquisition time rather than "
    "at acquisition time plus latency, so the decision maker sees the future.",
    "future_information_leakage",
    ("WG-BM-014",),
)
_register(
    "missing_as_zero",
    "Missing data imputed as zero",
    "Missing terrain cells and missing sensor records are silently replaced by "
    "0.0 instead of propagating as undefined.",
    "missing_treated_as_zero",
    ("WG-BM-004", "WG-BM-015"),
)
_register(
    "silent_carry_forward",
    "Stale observation reported as current",
    "The last received value is returned for a sensor that has stopped "
    "reporting, with no staleness flag, so outage is indistinguishable from a "
    "fresh reading.",
    "stale_data_presented_as_current",
    ("WG-BM-015",),
)
_register(
    "assume_missing_is_safe",
    "Absence of observation read as absence of hazard",
    "A cell with no positive fire detection is treated as hazard-free, so false "
    "negatives silently become safety claims.",
    "false_negative_treated_as_negative",
    ("WG-BM-017",),
)
_register(
    "ignore_informative_missingness",
    "Sensor dropout treated as missing-at-random",
    "Statistics are computed over reporting sensors only, although sensors fail "
    "*because* the hazard reached them (MNAR).",
    "informative_missingness",
    ("WG-BM-016",),
)
_register(
    "independent_edge_failures",
    "Correlated hazards multiplied as independent",
    "Joint road-failure probability is computed as the product of marginals, "
    "discarding the scenario correlation structure.",
    "correlation_ignored",
    ("WG-BM-034",),
)
_register(
    "average_scenario_inputs",
    "Averaging inputs instead of outcomes",
    "Scenario fire fields are averaged and the decision is evaluated once on the "
    "averaged world instead of evaluating loss in each scenario.",
    "average_of_inputs_fallacy",
    ("WG-BM-035",),
)
_register(
    "resident_level_bootstrap",
    "Bootstrap over residents instead of worlds",
    "Uncertainty is quantified by resampling correlated residents, treating "
    "1,000 residents in one simulated world as 1,000 independent samples.",
    "pseudoreplication",
    ("WG-BM-037",),
)
_register(
    "mean_only_ranking",
    "Policies ranked by mean outcome only",
    "Tail risk is discarded: the policy with the better average is declared "
    "better even when its conditional tail loss is an order of magnitude worse.",
    "tail_risk_ignored",
    ("WG-BM-038",),
)
_register(
    "naive_unpaired_comparison",
    "Unpaired comparison across different worlds",
    "Two policies evaluated on different world samples are compared directly, "
    "with no pairing on the common worlds.",
    "selection_bias",
    ("WG-BM-040",),
)
_register(
    "ignore_pickup_duration",
    "Pickup duration ignored",
    "Assisted-dispatch timelines omit the on-scene pickup/loading time, so the "
    "latest feasible dispatch time is reported too late.",
    "service_time_ignored",
    ("WG-BM-022", "WG-BM-023"),
)
_register(
    "monotone_dispatch_assumption",
    "Dispatch feasibility assumed monotone",
    "Feasibility is summarised by a single latest-dispatch scalar and every "
    "earlier time is assumed feasible, hiding infeasible interior windows.",
    "non_monotone_feasibility",
    ("WG-BM-026",),
)
_register(
    "nearest_base_only",
    "Only the nearest responder base considered",
    "Dispatch is planned from the geographically nearest base, even when its "
    "ingress corridor closes first.",
    "greedy_base_selection",
    ("WG-BM-024",),
)
_register(
    "ignore_congestion",
    "Free-flow travel times under congestion",
    "Inbound responder travel is costed at free-flow speed while an outbound "
    "evacuation is saturating the same road.",
    "capacity_ignored",
    ("WG-BM-027",),
)
_register(
    "allow_reverse_travel",
    "One-way roads traversed in both directions",
    "Directed edges are loaded into an undirected graph, so illegal reverse "
    "travel becomes available.",
    "direction_semantics_lost",
    ("WG-BM-008",),
)
_register(
    "euclidean_destination",
    "Destination chosen by straight-line distance",
    "The closest destination by Euclidean distance is selected without checking "
    "that a road route to it exists.",
    "unreachable_destination_selected",
    ("WG-BM-007",),
)
_register(
    "final_perimeter_hazard",
    "Final fire perimeter used instead of arrival time",
    "Any edge that eventually burns is treated as closed from t=0, discarding "
    "the time dimension of the hazard.",
    "time_of_arrival_collapsed",
    ("WG-BM-020",),
)
_register(
    "fifo_assumption",
    "FIFO travel times assumed",
    "Time-dependent travel is assumed first-in-first-out, so departing as early "
    "as possible is assumed optimal.",
    "non_fifo_network",
    ("WG-BM-021",),
)
_register(
    "isotropic_fire",
    "Wind bias dropped from fire spread",
    "Anisotropic (wind-driven) spread is replaced by an isotropic front at the "
    "mean spread rate.",
    "anisotropy_ignored",
    ("WG-BM-010",),
)
_register(
    "single_ignition_only",
    "Only the primary ignition modelled",
    "Secondary (spot) ignitions are dropped, so threatened areas ahead of the "
    "main front are reported as safe.",
    "spotting_ignored",
    ("WG-BM-012",),
)
_register(
    "uniform_fuel",
    "Fuel discontinuity averaged away",
    "A fuel-type boundary is smoothed into a single mean rate of spread.",
    "heterogeneity_averaged",
    ("WG-BM-011",),
)
_register(
    "forecast_always_trusted",
    "Forecast used regardless of arrival time",
    "A forecast is applied to a decision even when it is issued after the last "
    "useful decision time.",
    "timeliness_ignored",
    ("WG-BM-030", "WG-BM-043"),
)
_register(
    "skill_implies_value",
    "Forecast skill equated with decision value",
    "The forecast with the better accuracy score is assumed to be the one with "
    "the greater decision value.",
    "skill_value_conflation",
    ("WG-BM-031", "WG-BM-032", "WG-BM-033"),
)


# --------------------------------------------------------------------------
# Stochastic information, probabilistic forecasting and risk (K, L, M families)
# --------------------------------------------------------------------------

_register(
    "ignore_forecast_variance",
    "Predictive distribution collapsed to its mean",
    "A forecast distribution is reduced to a point estimate, so the probability "
    "of crossing a threshold becomes a hard 0 or 1 and two forecasts with the "
    "same mean and different spread become indistinguishable.",
    "forecast_uncertainty_discarded",
    ("WG-BM-044", "WG-BM-045"),
)
_register(
    "fixed_half_probability_threshold",
    "Decision taken at p = 0.5 regardless of loss",
    "The conservative action is taken when the hazard probability exceeds one "
    "half, instead of at the threshold implied by the loss matrix.",
    "decision_threshold_not_derived_from_loss",
    ("WG-BM-046", "WG-BM-047"),
)
_register(
    "renormalise_including_inadmissible",
    "Inadmissible scenarios included in the normalisation",
    "Scenario weights are renormalised over every scenario in the file, "
    "including those declared physically inadmissible, so the ensemble no "
    "longer represents a coherent belief.",
    "scenario_weights_normalised_incorrectly",
    ("WG-BM-048",),
)
_register(
    "posterior_replaced_by_prior",
    "Posterior computed and then not used",
    "The Bayesian update is performed correctly and the decision is taken on "
    "the prior anyway - the classic wiring bug, invisible in the reported "
    "posterior.",
    "posterior_not_used_for_decision",
    ("WG-BM-049", "WG-BM-051"),
)
_register(
    "ignore_observation_likelihood",
    "Observation likelihood ignored",
    "The likelihood is treated as uninformative, so the posterior equals the "
    "prior however diagnostic the observation actually was.",
    "likelihood_discarded",
    ("WG-BM-049", "WG-BM-051"),
)
_register(
    "assume_conditional_independence",
    "Correlated observations multiplied as independent",
    "A declared joint likelihood is replaced by the product of the per-sensor "
    "marginals, producing an overconfident posterior from sensors that share an "
    "error mode.",
    "observation_correlation_ignored",
    ("WG-BM-054",),
)
_register(
    "count_duplicate_evidence",
    "One measurement counted twice",
    "Two records carrying the same underlying measurement are treated as two "
    "independent observations, doubling the log-likelihood ratio.",
    "duplicate_evidence_double_counted",
    ("WG-BM-055",),
)
_register(
    "assume_missing_at_random",
    "Missingness assumed uninformative",
    "A record that failed to arrive is treated as missing at random, although "
    "its probability of arriving depends on the hazard being estimated.",
    "missingness_mechanism_ignored",
    ("WG-BM-056",),
)
_register(
    "non_detection_is_absence",
    "Non-detection treated as certainty of no hazard",
    "After a negative detection the posterior probability of fire is set to "
    "zero, ignoring the detector's false-negative rate.",
    "non_detection_read_as_absence",
    ("WG-BM-057",),
)
_register(
    "detection_is_certainty",
    "Detection treated as certainty of hazard",
    "After a positive detection the posterior probability of fire is set to "
    "one, ignoring the detector's false-positive rate and the base rate.",
    "detection_read_as_certainty",
    ("WG-BM-058",),
)
_register(
    "ignore_availability_time",
    "Observation availability time not checked",
    "The operational value of an observation is set equal to its statistical "
    "value, so information that arrives after the decision deadline still "
    "counts.",
    "observation_timeliness_ignored",
    ("WG-BM-052", "WG-BM-053"),
)
_register(
    "choose_by_information_gain",
    "Observation chosen by entropy reduction",
    "The observation that reduces uncertainty most is preferred over the one "
    "that improves the decision most, so information with no decision value is "
    "acquired.",
    "information_gain_mistaken_for_decision_value",
    ("WG-BM-050", "WG-BM-053"),
)
_register(
    "objective_ignored_use_mean",
    "Declared risk objective ignored",
    "The expected-loss winner is reported although the configured objective is "
    "CVaR, silently substituting one risk attitude for another.",
    "declared_objective_ignored",
    ("WG-BM-060",),
)
_register(
    "unresolved_state_blocks_decision",
    "Unresolved world state treated as an unresolved decision",
    "Because no scenario dominates, the system reports that it cannot decide "
    "and asks for more information, even where one action is acceptable in "
    "every scenario.",
    "uncertainty_conflated_with_indecision",
    ("WG-BM-061", "WG-BM-063"),
)
_register(
    "aggregate_calibration_only",
    "Conditional calibration reported as the aggregate",
    "Reliability is assessed over the pooled sample only, so a forecast that is "
    "calibrated on average and wrong in every regime passes.",
    "aggregate_calibration_masks_regime_failure",
    ("WG-BM-066",),
)


_ACTIVE: set[str] = set()


def active(mutation_id: str) -> bool:
    """Return ``True`` when ``mutation_id`` is currently injected."""
    if mutation_id not in MUTATIONS:
        raise KeyError(f"unknown mutation: {mutation_id}")
    return mutation_id in _ACTIVE


def active_ids() -> tuple[str, ...]:
    return tuple(sorted(_ACTIVE))


@contextlib.contextmanager
def activate(*mutation_ids: str):
    """Temporarily inject one or more mutations."""
    for mutation_id in mutation_ids:
        if mutation_id not in MUTATIONS:
            raise KeyError(f"unknown mutation: {mutation_id}")
    previous = set(_ACTIVE)
    _ACTIVE.update(mutation_ids)
    try:
        yield
    finally:
        _ACTIVE.clear()
        _ACTIVE.update(previous)
