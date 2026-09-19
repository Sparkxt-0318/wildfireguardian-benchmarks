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
