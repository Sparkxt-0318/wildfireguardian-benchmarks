<!-- GENERATED FILE - regenerate with `python -m wg_benchmarks report`. Edits here will be overwritten. Generation is deterministic: no timestamps, no timings, so a regenerated report is a no-op diff unless something changed. -->

# Coverage

## Failure mode coverage

Each row is a scientific failure mode the project cares about and the benchmarks that are designed to expose it.

| Failure mode | Benchmarks | Count |
|---|---|---|
| `accuracy_treated_as_the_objective` | `WG-BM-028` | 1 |
| `anisotropy_ignored` | `WG-BM-010` | 1 |
| `arrival_ordering_error` | `WG-BM-009` | 1 |
| `arrival_time_scaling_error` | `WG-BM-009` | 1 |
| `articulation_point_error` | `WG-BM-005` | 1 |
| `articulation_point_overinterpretation` | `WG-BM-006` | 1 |
| `aspect_convention_error` | `WG-BM-002` | 1 |
| `aspect_discontinuity_smoothing` | `WG-BM-003` | 1 |
| `average_of_inputs_fallacy` | `WG-BM-035` | 1 |
| `axis_transposition` | `WG-BM-002` | 1 |
| `baseline_too_weak` | `WG-BM-032` | 1 |
| `capacity_ignored` | `WG-BM-027` | 1 |
| `correlation_ignored` | `WG-BM-034` | 1 |
| `crest_artefact_misread_as_flat` | `WG-BM-003` | 1 |
| `decision_boundary_sensitivity` | `WG-BM-029` | 1 |
| `destination_deadline_ignored` | `WG-BM-025` | 1 |
| `direction_semantics_lost` | `WG-BM-008` | 1 |
| `dispatch_deadline_error` | `WG-BM-022` | 1 |
| `effective_sample_size_inflation` | `WG-BM-037` | 1 |
| `egress_redundancy_overcount` | `WG-BM-005` | 1 |
| `error_consequence_correlation` | `WG-BM-033` | 1 |
| `euclidean_proximity_fallacy` | `WG-BM-007` | 1 |
| `evpi_mistaken_for_realisable_value` | `WG-BM-043` | 1 |
| `fabricated_aspect` | `WG-BM-001` | 1 |
| `false_negative_treated_as_negative` | `WG-BM-017` | 1 |
| `false_single_egress_claim` | `WG-BM-006` | 1 |
| `forecast_value_overclaimed` | `WG-BM-032` | 1 |
| `free_flow_travel_time_assumed` | `WG-BM-027` | 1 |
| `fuel_boundary_smoothed` | `WG-BM-011` | 1 |
| `future_information_leakage` | `WG-BM-014` | 1 |
| `greedy_base_selection` | `WG-BM-024` | 1 |
| `heterogeneity_averaged` | `WG-BM-011` | 1 |
| `impossible_reverse_travel` | `WG-BM-008` | 1 |
| `information_value_overclaimed` | `WG-BM-041` | 1 |
| `information_value_underclaimed` | `WG-BM-042` | 1 |
| `informative_missingness` | `WG-BM-016` | 1 |
| `ingress_corridor_ignored` | `WG-BM-024` | 1 |
| `joint_from_marginals` | `WG-BM-034` | 1 |
| `latency_ignored` | `WG-BM-014` | 1 |
| `mean_only_ranking` | `WG-BM-038` | 1 |
| `mid_edge_hazard` | `WG-BM-018`, `WG-BM-019`, `WG-BM-022` | 3 |
| `missing_propagation_scope` | `WG-BM-004` | 1 |
| `missing_treated_as_zero` | `WG-BM-004`, `WG-BM-015` | 2 |
| `no_equivalence_test` | `WG-BM-039` | 1 |
| `non_fifo_network` | `WG-BM-021` | 1 |
| `non_monotone_feasibility` | `WG-BM-026` | 1 |
| `observation_pipeline_offset` | `WG-BM-013` | 1 |
| `perimeter_connectivity_assumed` | `WG-BM-012` | 1 |
| `premature_departure_assumed_optimal` | `WG-BM-021` | 1 |
| `protectability_misclassified` | `WG-BM-042` | 1 |
| `pseudoreplication` | `WG-BM-037` | 1 |
| `robust_action_missed` | `WG-BM-041` | 1 |
| `scalar_deadline_insufficient` | `WG-BM-026` | 1 |
| `scenario_blending` | `WG-BM-035` | 1 |
| `selection_bias` | `WG-BM-040` | 1 |
| `sensitivity_flat_to_service_time` | `WG-BM-023` | 1 |
| `service_time_ignored` | `WG-BM-022`, `WG-BM-023` | 2 |
| `shortest_path_without_feasibility` | `WG-BM-018` | 1 |
| `significance_mistaken_for_importance` | `WG-BM-039` | 1 |
| `skill_value_conflation` | `WG-BM-028`, `WG-BM-029`, `WG-BM-030`, `WG-BM-031`, `WG-BM-033` | 5 |
| `slope_magnitude_error` | `WG-BM-002` | 1 |
| `spotting_ignored` | `WG-BM-012` | 1 |
| `spurious_slope_on_flat_terrain` | `WG-BM-001` | 1 |
| `stale_data_presented_as_current` | `WG-BM-015` | 1 |
| `static_destination_assignment` | `WG-BM-025` | 1 |
| `sup_regret_scales_with_ensemble_size` | `WG-BM-036` | 1 |
| `survivorship_bias` | `WG-BM-016` | 1 |
| `tail_risk_ignored` | `WG-BM-038` | 1 |
| `time_window_reopening_ignored` | `WG-BM-020` | 1 |
| `timeliness_ignored` | `WG-BM-030`, `WG-BM-031`, `WG-BM-043` | 3 |
| `undeclared_traversal_semantics` | `WG-BM-019` | 1 |
| `unpaired_comparison` | `WG-BM-040` | 1 |
| `unreachable_destination_selected` | `WG-BM-007` | 1 |
| `unverified_clear_claim` | `WG-BM-017` | 1 |
| `waiting_policy_undeclared` | `WG-BM-020` | 1 |
| `wind_direction_sign_error` | `WG-BM-010` | 1 |
| `worst_case_criterion_instability` | `WG-BM-036` | 1 |

## Category coverage

| Category | Benchmarks |
|---|---|
| assisted_dispatch | 5 |
| fire | 4 |
| forecast_value | 6 |
| observation | 5 |
| protectability | 3 |
| road_graph | 4 |
| routing | 4 |
| scenario_uncertainty | 3 |
| statistics | 4 |
| terrain | 4 |
| traffic | 1 |

## Mutation coverage

24 of 24 injected bugs are caught by at least one benchmark.

| Mutation | Failure mode | Detected by |
|---|---|---|
| `allow_reverse_travel` | `direction_semantics_lost` | `WG-BM-008` |
| `assume_missing_is_safe` | `false_negative_treated_as_negative` | `WG-BM-017` |
| `average_scenario_inputs` | `average_of_inputs_fallacy` | `WG-BM-035` |
| `edge_entry_time_only` | `mid_edge_hazard` | `WG-BM-018`, `WG-BM-019`, `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026` |
| `euclidean_destination` | `unreachable_destination_selected` | `WG-BM-007` |
| `fifo_assumption` | `non_fifo_network` | `WG-BM-021` |
| `final_perimeter_hazard` | `time_of_arrival_collapsed` | `WG-BM-018`, `WG-BM-019`, `WG-BM-020`, `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026` |
| `forecast_always_trusted` | `timeliness_ignored` | `WG-BM-030`, `WG-BM-031`, `WG-BM-043` |
| `ignore_congestion` | `capacity_ignored` | `WG-BM-027` |
| `ignore_informative_missingness` | `informative_missingness` | `WG-BM-016` |
| `ignore_pickup_duration` | `service_time_ignored` | `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026`, `WG-BM-027` |
| `independent_edge_failures` | `correlation_ignored` | `WG-BM-034` |
| `isotropic_fire` | `anisotropy_ignored` | `WG-BM-010` |
| `mean_only_ranking` | `tail_risk_ignored` | `WG-BM-038` |
| `missing_as_zero` | `missing_treated_as_zero` | `WG-BM-004`, `WG-BM-015`, `WG-BM-016` |
| `monotone_dispatch_assumption` | `non_monotone_feasibility` | `WG-BM-026` |
| `naive_unpaired_comparison` | `selection_bias` | `WG-BM-040` |
| `nearest_base_only` | `greedy_base_selection` | `WG-BM-024` |
| `observation_future_leak` | `future_information_leakage` | `WG-BM-014` |
| `resident_level_bootstrap` | `pseudoreplication` | `WG-BM-037` |
| `silent_carry_forward` | `stale_data_presented_as_current` | `WG-BM-015`, `WG-BM-016` |
| `single_ignition_only` | `spotting_ignored` | `WG-BM-012` |
| `skill_implies_value` | `skill_value_conflation` | `WG-BM-029`, `WG-BM-030`, `WG-BM-031`, `WG-BM-033`, `WG-BM-043` |
| `uniform_fuel` | `heterogeneity_averaged` | `WG-BM-011` |
