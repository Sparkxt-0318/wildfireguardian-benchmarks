"""A third, independent derivation of the headline numbers.

The benchmark's expected values were authored in ``tools/authoring``; the
solvers compute them from the inputs; this file re-derives them a third time
from the scenario description, written out as plain arithmetic. Where a value is
a closed form it is written here as the closed form; where it is a small integer
it is written here as that integer, typed by hand from the benchmark README.

If all three agree, the number is almost certainly right. If they disagree,
somebody has to go and find out why - which is the entire point.
"""

from __future__ import annotations

import math

import pytest

from wg_benchmarks.runner import discover

EXPECTED = {b.benchmark_id: b.expected["results"] for b in discover()}


def test_a2_tilted_plane_slope_and_aspect():
    # A plane rising 0.1 m per metre to the east and 0.1 to the north.
    slope = math.degrees(math.atan(math.sqrt(0.1**2 + 0.1**2)))
    results = EXPECTED["WG-BM-002"]
    # sqrt(x*x + y*y) and hypot(x, y) can differ in the last bit; the benchmark's
    # own tolerance is 1e-9, so anything tighter than that is agreement.
    assert results["max_slope_deg"] == pytest.approx(slope, abs=1e-12)
    assert results["probes"]["centre"]["aspect_deg"] == 225.0  # descends to the south-west


def test_a3_ridge_flank_slope():
    # 6 m of fall across one 30 m cell.
    assert EXPECTED["WG-BM-003"]["max_slope_deg"] == math.degrees(math.atan(6.0 / 30.0))
    assert EXPECTED["WG-BM-003"]["flat_interior_cells"] == 3  # rows 1..3 of the crest column


def test_a4_missing_propagates_to_exactly_nine_cells():
    # A 7x7 grid has 25 interior cells; a hole spoils its own 3x3 neighbourhood.
    assert EXPECTED["WG-BM-004"]["interior_cells"] == 25
    assert EXPECTED["WG-BM-004"]["interior_undefined"] == 3 * 3
    assert EXPECTED["WG-BM-004"]["interior_defined"] == 25 - 9


def test_c1_radial_arrivals():
    results = EXPECTED["WG-BM-009"]["arrival_min"]
    assert results["p_east"] == 100.0 / 10.0
    assert results["p_ne"] == math.sqrt(100.0**2 + 100.0**2) / 10.0
    assert results["p_far"] == 300.0 / 10.0


def test_c2_head_and_back_rates():
    # head 20 m/min, back 4 m/min, probes 200 m downwind and upwind.
    arrival = EXPECTED["WG-BM-010"]["arrival_min"]
    assert arrival["p_downwind"] == 200.0 / 20.0
    assert arrival["p_upwind"] == 200.0 / 4.0
    # Crosswind: t = a q / (b sqrt(a^2 - c^2)) with a = 12, c = 8, b = 6.
    assert arrival["p_crosswind"] == 12.0 * 200.0 / (6.0 * math.sqrt(12.0**2 - 8.0**2))


def test_c3_fuel_boundary_arrivals():
    arrival = EXPECTED["WG-BM-011"]["arrival_min"]
    assert arrival["d100"] == 100.0 / 10.0
    assert arrival["d150"] == 100.0 / 10.0 + 50.0 / 2.0
    assert arrival["d200"] == 100.0 / 10.0 + 100.0 / 2.0


def test_c4_spot_fire_arrivals():
    arrival = EXPECTED["WG-BM-012"]["arrival_min"]
    assert arrival["ahead_of_spot"] == min(2500.0 / 5.0, 30.0 + 500.0 / 5.0)
    assert arrival["between"] == min(1000.0 / 5.0, 30.0 + 1000.0 / 5.0)
    # Main radius 200 m at t=40 covers 13 cells on a 100 m grid; the spot covers 1.
    assert EXPECTED["WG-BM-012"]["burned_cells"] == 13 + 1
    assert EXPECTED["WG-BM-012"]["burned_components"] == 2


def test_d2_latency_makes_the_present_invisible():
    query = EXPECTED["WG-BM-014"]["queries"]["q25"]
    assert query["latest_acquisition_time_min"] == 25.0 - 10.0
    # truth(t) = 1000 - 20t, so the available value is 200 m optimistic.
    assert query["value"] == 1000.0 - 20.0 * 15.0
    assert query["error"] == 10.0 * 20.0


def test_d4_mnar_bias_is_maximal():
    mnar = EXPECTED["WG-BM-016"]["mnar"]
    assert mnar["true_mean"] == 3.0 / 5.0       # s1, s2, s3 have burnt by t = 60
    assert mnar["observed_mean"] == 0.0         # every surviving sensor reports unburnt
    assert mnar["naive_bias"] == 0.0 - 3.0 / 5.0


def test_e1_interval_safety_rejects_the_short_route():
    # 0 + 5 > 4, so the short route cannot be completed inside its window.
    assert 0.0 + 5.0 > 4.0
    assert EXPECTED["WG-BM-018"]["earliest_arrival_min"] == 9.0
    assert EXPECTED["WG-BM-018"]["shortest_route_feasible"] is False


def test_e3_waiting_arrival():
    assert EXPECTED["WG-BM-020"]["arrival_with_waiting_min"] == 20.0 + 5.0
    assert EXPECTED["WG-BM-020"]["feasible_without_waiting"] is False


def test_e4_non_fifo_optimum():
    assert EXPECTED["WG-BM-021"]["earliest_arrival_over_departures_min"] == 5.0 + 10.0
    assert EXPECTED["WG-BM-021"]["immediate_departure_arrival_min"] == 0.0 + 60.0


def test_f1_latest_dispatch_is_deadline_minus_the_chain():
    # egress closes at 20; the chain is ingress 5 + pickup 5 + egress 5.
    assert EXPECTED["WG-BM-022"]["latest_feasible_dispatch_min"] == 20.0 - (5.0 + 5.0 + 5.0)


def test_f2_latest_dispatch_is_ten_minus_pickup():
    table = EXPECTED["WG-BM-023"]["latest_dispatch_by_pickup"]
    for pickup in (2.0, 5.0, 10.0):
        assert table[f"{pickup:g}"] == 10.0 - pickup
    assert table["15"] is None  # 10 - 15 < 0


def test_f3_base_bounds():
    table = EXPECTED["WG-BM-024"]["latest_dispatch_by_base"]
    assert table["base_near"] == 6.0 - 4.0                  # ingress window binds
    assert table["base_far"] == 30.0 - (10.0 + 5.0 + 8.0)   # egress window binds


def test_f5_feasible_set_is_two_intervals():
    intervals = EXPECTED["WG-BM-026"]["feasible_intervals"]
    # ingress takes 6 min inside windows [0,10] and [20,40].
    assert intervals == [[0.0, 10.0 - 6.0], [20.0, 40.0 - 6.0]]
    assert EXPECTED["WG-BM-026"]["monotone_feasibility"] is False


def test_f6_capacity_turns_slack_into_impossibility():
    counterfactual = EXPECTED["WG-BM-027"]["free_flow_counterfactual"]
    assert counterfactual["arrival_at_dispatch_zero_min"] == 10.0 + 5.0 + 10.0
    assert counterfactual["latest_feasible_dispatch_min"] == 40.0 - 25.0
    assert EXPECTED["WG-BM-027"]["feasible_intervals"] == []
    # With congestion the chain is 25 + 5 + 15 = 45 against a deadline of 40.
    assert 25.0 + 5.0 + 15.0 > 40.0


def test_g3_late_forecast_value():
    results = EXPECTED["WG-BM-030"]
    # waiting means sheltering: 0.5 * 100 + 0.5 * 0 = 50 against a baseline of 10
    assert results["value_by_policy"]["wait_for_forecast"] == 10.0 - (0.5 * 100.0 + 0.5 * 0.0)
    assert results["evpi"] == 10.0 - (0.5 * 10.0 + 0.5 * 0.0)
    assert results["realizable_value_of_information"] == 0.0


def test_g4_crude_beats_accurate():
    results = EXPECTED["WG-BM-031"]
    assert results["value_by_policy"]["use_crude_early"] == 10.0 - (0.5 * 10.0 + 0.5 * 0.0)
    assert results["value_by_policy"]["use_accurate_late"] < 0
    assert results["ranked_by_value"][0] != results["ranked_by_skill"][0]


def test_g6_forecast_harm():
    results = EXPECTED["WG-BM-033"]
    assert results["expected_loss_by_policy"]["forecast_aware"] == 0.2 * 200.0
    assert results["value_by_policy"]["forecast_aware"] == 10.0 - 40.0


def test_h1_joint_probability():
    failure = EXPECTED["WG-BM-034"]["edge_failure"]
    assert failure["joint_all_closed_probability"] == 0.3
    assert failure["joint_under_independence"] == 0.3 * 0.3
    assert failure["independence_error_factor"] == 0.3 / (0.3 * 0.3)


def test_h2_expected_losses():
    losses = EXPECTED["WG-BM-035"]["ensembles"]["base"]["expected_loss"]
    assert losses["route_a"] == 0.5 * 0.0 + 0.5 * 100.0
    assert losses["hold"] == 30.0
    assert EXPECTED["WG-BM-035"]["averaged_world_best_action"] == "route_a"


def test_i1_standard_error_ratio():
    outcomes = [10.0, 14.0, 18.0, 22.0, 26.0, 30.0, 34.0, 38.0, 42.0, 46.0]
    mean = sum(outcomes) / 10
    ss = sum((v - mean) ** 2 for v in outcomes)
    world_se = math.sqrt(ss / 9) / math.sqrt(10)
    resident_se = math.sqrt(ss * 1000 / 9999) / math.sqrt(10000)
    results = EXPECTED["WG-BM-037"]
    assert results["analytic_world_se"] == world_se
    assert results["analytic_resident_se"] == resident_se
    assert results["analytic_ci_width_ratio"] == world_se / resident_se
    assert 33.0 < world_se / resident_se < 33.5


def test_i2_mean_and_cvar():
    assert EXPECTED["WG-BM-038"]["mean_loss"]["policy_a"] == 0.9 * 0.0 + 0.1 * 100.0
    assert EXPECTED["WG-BM-038"]["mean_loss"]["policy_b"] == 0.9 * 12.0 + 0.1 * 20.0
    assert EXPECTED["WG-BM-038"]["cvar_loss"]["policy_a"] == 100.0
    assert EXPECTED["WG-BM-038"]["cvar_loss"]["policy_b"] == 20.0


def test_i3_confidence_interval():
    z = 1.959963984540054
    sd = math.sqrt(2000 / 1999)
    se = sd / math.sqrt(2000)
    results = EXPECTED["WG-BM-039"]
    assert results["mean_difference"] == 0.3
    assert results["ci_lower"] == 0.3 - z * se
    assert results["ci_upper"] == 0.3 + z * se
    assert results["ci_upper"] < 1.0      # inside the practical margin
    assert results["ci_lower"] > 0.0      # and excluding zero


def test_i4_paired_difference_recovers_the_offsets():
    results = EXPECTED["WG-BM-040"]
    assert results["paired_difference"] == 5.0 - 2.0
    assert results["naive_difference"] < 0 < results["paired_difference"]


def test_j_family_information_values():
    assert EXPECTED["WG-BM-041"]["evpi"] == 0.0
    assert EXPECTED["WG-BM-042"]["evpi"] == 0.5 * 90.0        # best fixed 45, clairvoyant 0
    assert EXPECTED["WG-BM-042"]["realizable_value_of_information"] == 45.0
    assert EXPECTED["WG-BM-043"]["evpi"] == 45.0
    assert EXPECTED["WG-BM-043"]["realizable_value_of_information"] == 0.0


# --------------------------------------------------------------------------
# K, L and M families: the stochastic-information benchmarks
# --------------------------------------------------------------------------


def _phi(x, mean, sd):
    return 0.5 * (1.0 + math.erf((x - mean) / (sd * math.sqrt(2.0))))


def test_k1_threshold_and_tails():
    results = EXPECTED["WG-BM-044"]
    # 100p = 8 at indifference
    assert results["decision_threshold_probability"] == 8.0 / 100.0
    tails = results["hazard_probability_by_forecast"]
    assert tails["forecast_a"] == pytest.approx(_phi(800, 1000, 50), abs=1e-15)
    assert tails["forecast_b"] == pytest.approx(_phi(800, 1000, 300), abs=1e-15)
    # Same mean, opposite actions.
    assert results["action_by_forecast"]["forecast_a"] != results["action_by_forecast"]["forecast_b"]
    assert len(set(results["point_estimate_action_by_forecast"].values())) == 1


def test_k2_skill_and_value_disagree():
    results = EXPECTED["WG-BM-045"]
    assert results["true_mean"] == 0.97 * 900.0 + 0.03 * 700.0
    assert results["location_error_by_forecast"]["forecast_a"] == abs(910.0 - 894.0)
    assert results["location_error_by_forecast"]["forecast_b"] == abs(940.0 - 894.0)
    assert results["best_expected_loss_under_truth"] == 0.03 * 100.0
    assert results["regret_by_forecast"]["forecast_b"] == 0.0
    assert results["regret_by_forecast"]["forecast_a"] == 8.0 - 3.0


def test_k3_threshold_is_lc_over_lf():
    # divert costs the same in both states: p* = L_conservative / L_failure
    assert EXPECTED["WG-BM-046"]["decision_threshold_probability"] == 24.0 / 120.0
    assert EXPECTED["WG-BM-046"]["action_by_probe"]["0.35"] == "divert"  # and 0.35 < 0.5


def test_k4_threshold_is_lc_over_lc_plus_lf():
    # the conservative action fully protects: p* = L_c / (L_c + L_f)
    assert EXPECTED["WG-BM-047"]["decision_threshold_probability"] == 5.0 / (5.0 + 495.0)
    probes = EXPECTED["WG-BM-047"]["probes"]
    assert probes["0.4"]["expected_loss"]["proceed"] == 0.4 * 495.0
    assert probes["0.4"]["expected_loss"]["hold_back"] == 0.6 * 5.0


def test_k5_normalisation_and_joint():
    results = EXPECTED["WG-BM-048"]
    assert results["normalised_weights"]["omega_4"] == 3.0 / 8.0
    assert results["joint_all_closed_probability"] == 3.0 / 8.0
    assert results["joint_under_independence"] == 0.5 * 0.5
    assert results["expected_loss"]["assume_egress"] == (3.0 / 8.0) * 140.0
    assert results["expected_loss_under_independence"]["assume_egress"] == 0.25 * 140.0


def test_k6_bayes_by_hand():
    results = EXPECTED["WG-BM-049"]
    assert results["decision_threshold_probability"] == 5.0 / 25.0
    posterior = results["observations"]["ridge_anomaly"]["posterior_hazard_by_outcome"]
    assert posterior["anomaly"] == pytest.approx((0.1 * 0.9) / 0.27, abs=1e-15)
    assert posterior["no_anomaly"] == pytest.approx((0.1 * 0.1) / 0.73, abs=1e-15)
    assert results["observations"]["ridge_anomaly"]["evsi_statistical"] == pytest.approx(
        2.0 - (0.9 + 0.2), abs=1e-12
    )


def test_k7_zero_value_positive_information():
    observation = EXPECTED["WG-BM-050"]["observations"]["valley_haze"]
    assert observation["evsi_statistical"] == 0.0
    assert observation["information_gain_bits"] > 0.0
    assert EXPECTED["WG-BM-050"]["evpi"] > 0.0  # the zero belongs to this observation


def test_k8_evsi_arithmetic():
    results = EXPECTED["WG-BM-051"]
    assert results["prior_expected_loss"] == 40.0
    # each branch: the wrong-side road costs 0.2 * 90
    assert results["observations"]["bearing_sensor"]["evsi_statistical"] == 40.0 - 0.2 * 90.0
    assert results["evpi"] == 40.0


def test_k9_and_k10_timing():
    late = EXPECTED["WG-BM-052"]["observations"]["bearing_sensor"]
    assert late["availability_time_min"] > 10.0  # the declared deadline
    assert late["evsi_statistical"] == 22.0 and late["evsi_operational"] == 0.0
    ten = EXPECTED["WG-BM-053"]
    assert ten["evsi_statistical_by_observation"]["weak_early"] == 40.0 - 0.3 * 90.0
    assert ten["evsi_operational_by_observation"]["perfect_late"] == 0.0
    assert ten["ranked_by_operational_value"][0] != ten["ranked_by_information_gain"][0]


def test_k11_and_k12_correlated_and_duplicate():
    pair = EXPECTED["WG-BM-054"]["observations"]["sensor_pair"]
    assert pair["realised_posterior_hazard"] == pytest.approx(0.16 / 0.92, abs=1e-15)
    assert pair["realised_posterior_under_independence"] == pytest.approx(0.04 / 0.68, abs=1e-15)
    assert pair["realised_action"] != pair["realised_action_under_independence"]
    duplicate = EXPECTED["WG-BM-055"]["observations"]["duplicated_report"]
    assert duplicate["realised_posterior_hazard"] == 0.2 / (0.2 + 0.8)
    assert duplicate["realised_log_likelihood_ratio_bits"] == math.log2(0.2 / 0.8)
    assert duplicate["realised_log_likelihood_ratio_bits_under_independence"] == 2 * math.log2(
        0.2 / 0.8
    )


def test_k13_missingness_is_evidence():
    observation = EXPECTED["WG-BM-056"]["observations"]["telemetry_status"]
    assert observation["realised_posterior_hazard"] == pytest.approx(
        (0.05 * 0.6) / (0.05 * 0.6 + 0.95 * 0.05), abs=1e-15
    )
    assert observation["realised_log_likelihood_ratio_bits"] == math.log2(0.6 / 0.05)
    assert observation["evsi_statistical"] == pytest.approx(4.5 - (0.475 + 1.8), abs=1e-12)


def test_k14_non_detection():
    results = EXPECTED["WG-BM-057"]
    posterior = results["observations"]["detector"]["realised_posterior_hazard"]
    assert posterior == pytest.approx((0.2 * 0.3) / (0.2 * 0.3 + 0.8 * 0.95), abs=1e-15)
    assert posterior > results["decision_threshold_probability"] == 5.0 / (5.0 + 95.0)
    assert posterior > 0.0


def test_k15_false_positive():
    results = EXPECTED["WG-BM-058"]
    posterior = results["observations"]["detector"]["realised_posterior_hazard"]
    assert posterior == pytest.approx((0.02 * 0.7) / (0.02 * 0.7 + 0.98 * 0.05), abs=1e-15)
    assert posterior < 0.5
    # at p = 2/9 the three expected losses are 200p, 6(1-p)+30p and 40(1-p)
    p = 2.0 / 9.0
    assert min(200 * p, 6 * (1 - p) + 30 * p, 40 * (1 - p)) == pytest.approx(
        6 * (1 - p) + 30 * p, abs=1e-12
    )
    assert results["observations"]["detector"]["realised_action"] == "divert_traffic"


def test_l1_and_l2_risk_criteria():
    l1 = EXPECTED["WG-BM-059"]
    assert l1["expected_loss"]["policy_a"] == 0.8 * 0.0 + 0.2 * 60.0
    assert l1["expected_loss"]["policy_b"] == 0.8 * 15.0 + 0.2 * 25.0
    assert l1["recommended_action"] is None
    l2 = EXPECTED["WG-BM-060"]
    # CVaR at 0.9 splits the awkward atom: (0.05*300 + 0.05*20) / 0.1
    assert l2["cvar"]["policy_a"] == pytest.approx((0.05 * 300.0 + 0.05 * 20.0) / 0.1, abs=1e-12)
    assert l2["cvar"]["policy_b"] == pytest.approx((0.05 * 40.0 + 0.05 * 18.0) / 0.1, abs=1e-12)
    assert l2["recommended_action"] == l2["best_by_cvar"] != l2["best_by_expected_loss"]


def test_l3_l4_l5_state_versus_decision():
    l3 = EXPECTED["WG-BM-061"]
    assert l3["evpi"] == 0.0 and l3["state_resolved"] is False and l3["decision_resolved"] is True
    l4 = EXPECTED["WG-BM-062"]
    assert l4["decision_margin"] == pytest.approx(0.03 * 7.0, abs=1e-12)  # 0.03 * (17 - 10)
    assert l4["min_perturbation_to_flip"] == pytest.approx(l4["decision_margin"] / 0.97, abs=1e-12)
    assert l4["state_resolved"] is True and l4["decision_stable"] is False
    l5 = EXPECTED["WG-BM-063"]
    assert l5["expected_loss"]["stage_at_junction"] == pytest.approx(
        0.4 * 4 + 0.3 * 4 + 0.2 * 5 + 0.1 * 5, abs=1e-12
    )
    assert l5["evpi"] == 0.0 and l5["forecast_skill_score"] < 0.5


def test_m_family_calibration():
    m1 = EXPECTED["WG-BM-064"]
    assert m1["base_rate"] == 430.0 / 800.0
    assert m1["uncertainty"] == pytest.approx((430 / 800) * (370 / 800), abs=1e-15)
    assert m1["aggregate_calibration_error"] == 0.0
    assert m1["murphy_residual"] == 0.0
    m2 = EXPECTED["WG-BM-065"]
    assert m2["aggregate_calibration_error"] == pytest.approx(
        0.25 * 0.15 + 0.375 * 0.15, abs=1e-15
    )
    assert m2["reliability"] == pytest.approx(0.25 * 0.0225 + 0.375 * 0.0225, abs=1e-15)
    # resolution and uncertainty are unchanged, so the Brier gap is the reliability
    assert m2["brier_score"] - m1["brier_score"] == pytest.approx(m2["reliability"], abs=1e-15)
    assert m2["decision"]["total_excess_expected_loss"] == 200 * (0.2 * 90 - 0.8 * 10)
    m3 = EXPECTED["WG-BM-066"]
    assert m3["aggregate_calibration_error"] == 0.0
    assert m3["stratified_calibration_error"] == pytest.approx(0.5 * 0.3 + 0.5 * 0.3, abs=1e-15)
    assert m3["decision"]["total_excess_expected_loss"] == 400 * (0.8 * 30 - 0.2 * 70)
