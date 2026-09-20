<!-- GENERATED FILE - regenerate with `python -m wg_benchmarks report`. Edits here will be overwritten. Generation is deterministic: no timestamps, no timings, so a regenerated report is a no-op diff unless something changed. -->

# Coverage

## Failure mode coverage

Each row is a scientific failure mode the project cares about and the benchmarks that are designed to expose it.

| Failure mode | Benchmarks | Count |
|---|---|---|
| `accuracy_treated_as_the_objective` | `WG-BM-028` | 1 |
| `aggregate_calibration_masks_regime_failure` | `WG-BM-066` | 1 |
| `anisotropy_ignored` | `WG-BM-010` | 1 |
| `arbitrary_probability_cutoff` | `WG-BM-046` | 1 |
| `arrival_ordering_error` | `WG-BM-009` | 1 |
| `arrival_time_scaling_error` | `WG-BM-009` | 1 |
| `articulation_point_error` | `WG-BM-005` | 1 |
| `articulation_point_overinterpretation` | `WG-BM-006` | 1 |
| `aspect_convention_error` | `WG-BM-002` | 1 |
| `aspect_discontinuity_smoothing` | `WG-BM-003` | 1 |
| `average_of_inputs_fallacy` | `WG-BM-035` | 1 |
| `axis_transposition` | `WG-BM-002` | 1 |
| `base_rate_neglect` | `WG-BM-058` | 1 |
| `baseline_too_weak` | `WG-BM-032` | 1 |
| `bayes_rule_error` | `WG-BM-049` | 1 |
| `brier_decomposition_error` | `WG-BM-064` | 1 |
| `calibration_arithmetic_error` | `WG-BM-064` | 1 |
| `calibration_cost_unmeasured` | `WG-BM-065` | 1 |
| `capacity_ignored` | `WG-BM-027` | 1 |
| `conditional_calibration_unassessed` | `WG-BM-066` | 1 |
| `correlation_ignored` | `WG-BM-034`, `WG-BM-048` | 2 |
| `crest_artefact_misread_as_flat` | `WG-BM-003` | 1 |
| `decision_boundary_sensitivity` | `WG-BM-029` | 1 |
| `decision_threshold_not_derived_from_loss` | `WG-BM-046`, `WG-BM-047` | 2 |
| `declared_objective_ignored` | `WG-BM-060` | 1 |
| `destination_deadline_ignored` | `WG-BM-025` | 1 |
| `detection_read_as_certainty` | `WG-BM-058` | 1 |
| `deterministic_skill_mistaken_for_decision_value` | `WG-BM-045` | 1 |
| `direction_semantics_lost` | `WG-BM-008` | 1 |
| `dispatch_deadline_error` | `WG-BM-022` | 1 |
| `duplicate_evidence_double_counted` | `WG-BM-055` | 1 |
| `effective_sample_size_inflation` | `WG-BM-037` | 1 |
| `egress_redundancy_overcount` | `WG-BM-005` | 1 |
| `error_consequence_correlation` | `WG-BM-033` | 1 |
| `euclidean_proximity_fallacy` | `WG-BM-007` | 1 |
| `evpi_mistaken_for_realisable_value` | `WG-BM-043` | 1 |
| `evsi_miscomputed` | `WG-BM-051` | 1 |
| `evsi_mistaken_for_operational_value` | `WG-BM-052` | 1 |
| `fabricated_aspect` | `WG-BM-001` | 1 |
| `false_negative_ignored` | `WG-BM-057` | 1 |
| `false_negative_treated_as_negative` | `WG-BM-017` | 1 |
| `false_single_egress_claim` | `WG-BM-006` | 1 |
| `forecast_uncertainty_discarded` | `WG-BM-044`, `WG-BM-045` | 2 |
| `forecast_value_overclaimed` | `WG-BM-032` | 1 |
| `fragile_recommendation` | `WG-BM-062` | 1 |
| `free_flow_travel_time_assumed` | `WG-BM-027` | 1 |
| `fuel_boundary_smoothed` | `WG-BM-011` | 1 |
| `future_information_leakage` | `WG-BM-014` | 1 |
| `greedy_base_selection` | `WG-BM-024` | 1 |
| `heterogeneity_averaged` | `WG-BM-011` | 1 |
| `impossible_reverse_travel` | `WG-BM-008` | 1 |
| `inadmissible_scenario_included` | `WG-BM-048` | 1 |
| `information_demanded_unnecessarily` | `WG-BM-061` | 1 |
| `information_gain_mistaken_for_decision_value` | `WG-BM-050`, `WG-BM-053` | 2 |
| `information_value_overclaimed` | `WG-BM-041` | 1 |
| `information_value_underclaimed` | `WG-BM-042` | 1 |
| `informative_missingness` | `WG-BM-016`, `WG-BM-056` | 2 |
| `ingress_corridor_ignored` | `WG-BM-024` | 1 |
| `joint_from_marginals` | `WG-BM-034` | 1 |
| `latency_ignored` | `WG-BM-014` | 1 |
| `likelihood_discarded` | `WG-BM-049` | 1 |
| `loss_asymmetry_ignored` | `WG-BM-047` | 1 |
| `mean_only_ranking` | `WG-BM-038` | 1 |
| `mid_edge_hazard` | `WG-BM-018`, `WG-BM-019`, `WG-BM-022` | 3 |
| `missing_propagation_scope` | `WG-BM-004` | 1 |
| `missing_treated_as_zero` | `WG-BM-004`, `WG-BM-015` | 2 |
| `missingness_mechanism_ignored` | `WG-BM-056` | 1 |
| `no_equivalence_test` | `WG-BM-039` | 1 |
| `non_detection_read_as_absence` | `WG-BM-057` | 1 |
| `non_fifo_network` | `WG-BM-021` | 1 |
| `non_monotone_feasibility` | `WG-BM-026` | 1 |
| `observation_assumed_useful` | `WG-BM-050` | 1 |
| `observation_correlation_ignored` | `WG-BM-054` | 1 |
| `observation_pipeline_offset` | `WG-BM-013` | 1 |
| `observation_timeliness_ignored` | `WG-BM-052`, `WG-BM-053` | 2 |
| `overconfidence_undetected` | `WG-BM-065` | 1 |
| `overconfident_posterior` | `WG-BM-054` | 1 |
| `perimeter_connectivity_assumed` | `WG-BM-012` | 1 |
| `point_estimate_substituted_for_distribution` | `WG-BM-044` | 1 |
| `posterior_not_used_for_decision` | `WG-BM-049`, `WG-BM-051` | 2 |
| `premature_departure_assumed_optimal` | `WG-BM-021` | 1 |
| `premature_winner` | `WG-BM-059` | 1 |
| `protectability_misclassified` | `WG-BM-042` | 1 |
| `pseudoreplication` | `WG-BM-037` | 1 |
| `record_count_mistaken_for_evidence` | `WG-BM-055` | 1 |
| `robust_action_missed` | `WG-BM-041` | 1 |
| `scalar_deadline_insufficient` | `WG-BM-026` | 1 |
| `scenario_blending` | `WG-BM-035` | 1 |
| `scenario_weights_normalised_incorrectly` | `WG-BM-048` | 1 |
| `selection_bias` | `WG-BM-040` | 1 |
| `sensitivity_flat_to_service_time` | `WG-BM-023` | 1 |
| `service_time_ignored` | `WG-BM-022`, `WG-BM-023` | 2 |
| `shortest_path_without_feasibility` | `WG-BM-018` | 1 |
| `significance_mistaken_for_importance` | `WG-BM-039` | 1 |
| `skill_value_conflation` | `WG-BM-028`, `WG-BM-029`, `WG-BM-030`, `WG-BM-031`, `WG-BM-033`, `WG-BM-063` | 6 |
| `slope_magnitude_error` | `WG-BM-002` | 1 |
| `spotting_ignored` | `WG-BM-012` | 1 |
| `spurious_slope_on_flat_terrain` | `WG-BM-001` | 1 |
| `stale_data_presented_as_current` | `WG-BM-015` | 1 |
| `state_certainty_mistaken_for_decision_confidence` | `WG-BM-062` | 1 |
| `static_destination_assignment` | `WG-BM-025` | 1 |
| `sup_regret_scales_with_ensemble_size` | `WG-BM-036` | 1 |
| `survivorship_bias` | `WG-BM-016` | 1 |
| `tail_risk_ignored` | `WG-BM-038`, `WG-BM-060` | 2 |
| `time_window_reopening_ignored` | `WG-BM-020` | 1 |
| `timeliness_ignored` | `WG-BM-030`, `WG-BM-031`, `WG-BM-043` | 3 |
| `uncertainty_conflated_with_indecision` | `WG-BM-061`, `WG-BM-063` | 2 |
| `undeclared_risk_attitude` | `WG-BM-059` | 1 |
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
| calibration | 3 |
| fire | 4 |
| forecast_value | 6 |
| observation | 5 |
| probabilistic_forecast | 15 |
| protectability | 3 |
| risk | 5 |
| road_graph | 4 |
| routing | 4 |
| scenario_uncertainty | 3 |
| statistics | 4 |
| terrain | 4 |
| traffic | 1 |

## Mutation coverage

39 of 39 injected bugs are caught by at least one benchmark.

| Mutation | Failure mode | Detected by |
|---|---|---|
| `aggregate_calibration_only` | `aggregate_calibration_masks_regime_failure` | `WG-BM-066` |
| `allow_reverse_travel` | `direction_semantics_lost` | `WG-BM-008` |
| `assume_conditional_independence` | `observation_correlation_ignored` | `WG-BM-054`, `WG-BM-055` |
| `assume_missing_at_random` | `missingness_mechanism_ignored` | `WG-BM-056` |
| `assume_missing_is_safe` | `false_negative_treated_as_negative` | `WG-BM-017` |
| `average_scenario_inputs` | `average_of_inputs_fallacy` | `WG-BM-035` |
| `choose_by_information_gain` | `information_gain_mistaken_for_decision_value` | `WG-BM-050`, `WG-BM-053` |
| `count_duplicate_evidence` | `duplicate_evidence_double_counted` | `WG-BM-055` |
| `detection_is_certainty` | `detection_read_as_certainty` | `WG-BM-057`, `WG-BM-058` |
| `edge_entry_time_only` | `mid_edge_hazard` | `WG-BM-018`, `WG-BM-019`, `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026` |
| `euclidean_destination` | `unreachable_destination_selected` | `WG-BM-007` |
| `fifo_assumption` | `non_fifo_network` | `WG-BM-021` |
| `final_perimeter_hazard` | `time_of_arrival_collapsed` | `WG-BM-018`, `WG-BM-019`, `WG-BM-020`, `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026` |
| `fixed_half_probability_threshold` | `decision_threshold_not_derived_from_loss` | `WG-BM-044`, `WG-BM-045`, `WG-BM-046`, `WG-BM-047`, `WG-BM-049`, `WG-BM-054`, `WG-BM-055`, `WG-BM-056`, `WG-BM-057` |
| `forecast_always_trusted` | `timeliness_ignored` | `WG-BM-030`, `WG-BM-031`, `WG-BM-043` |
| `ignore_availability_time` | `observation_timeliness_ignored` | `WG-BM-052`, `WG-BM-053` |
| `ignore_congestion` | `capacity_ignored` | `WG-BM-027` |
| `ignore_forecast_variance` | `forecast_uncertainty_discarded` | `WG-BM-044`, `WG-BM-045` |
| `ignore_informative_missingness` | `informative_missingness` | `WG-BM-016` |
| `ignore_observation_likelihood` | `likelihood_discarded` | `WG-BM-049`, `WG-BM-050`, `WG-BM-051`, `WG-BM-052`, `WG-BM-053`, `WG-BM-054`, `WG-BM-055`, `WG-BM-056`, `WG-BM-057`, `WG-BM-058` |
| `ignore_pickup_duration` | `service_time_ignored` | `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026`, `WG-BM-027` |
| `independent_edge_failures` | `correlation_ignored` | `WG-BM-034`, `WG-BM-048` |
| `isotropic_fire` | `anisotropy_ignored` | `WG-BM-010` |
| `mean_only_ranking` | `tail_risk_ignored` | `WG-BM-038` |
| `missing_as_zero` | `missing_treated_as_zero` | `WG-BM-004`, `WG-BM-015`, `WG-BM-016` |
| `monotone_dispatch_assumption` | `non_monotone_feasibility` | `WG-BM-026` |
| `naive_unpaired_comparison` | `selection_bias` | `WG-BM-040` |
| `nearest_base_only` | `greedy_base_selection` | `WG-BM-024` |
| `non_detection_is_absence` | `non_detection_read_as_absence` | `WG-BM-057`, `WG-BM-058` |
| `objective_ignored_use_mean` | `declared_objective_ignored` | `WG-BM-060` |
| `observation_future_leak` | `future_information_leakage` | `WG-BM-014` |
| `posterior_replaced_by_prior` | `posterior_not_used_for_decision` | `WG-BM-049`, `WG-BM-051`, `WG-BM-052`, `WG-BM-053`, `WG-BM-056`, `WG-BM-058` |
| `renormalise_including_inadmissible` | `scenario_weights_normalised_incorrectly` | `WG-BM-048` |
| `resident_level_bootstrap` | `pseudoreplication` | `WG-BM-037` |
| `silent_carry_forward` | `stale_data_presented_as_current` | `WG-BM-015`, `WG-BM-016` |
| `single_ignition_only` | `spotting_ignored` | `WG-BM-012` |
| `skill_implies_value` | `skill_value_conflation` | `WG-BM-029`, `WG-BM-030`, `WG-BM-031`, `WG-BM-033`, `WG-BM-043` |
| `uniform_fuel` | `heterogeneity_averaged` | `WG-BM-011` |
| `unresolved_state_blocks_decision` | `uncertainty_conflated_with_indecision` | `WG-BM-061`, `WG-BM-063` |
