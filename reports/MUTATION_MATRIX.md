<!-- GENERATED FILE - regenerate with `python -m wg_benchmarks report`. Edits here will be overwritten. Generation is deterministic: no timestamps, no timings, so a regenerated report is a no-op diff unless something changed. -->

# Mutation test results

Each mutation is a deliberate, plausible implementation bug injected into the reference solvers.  A benchmark *detects* a mutation when it passes clean and fails mutated.

| Mutation | Description | Detected by | Declared but missed |
|---|---|---|---|
| `aggregate_calibration_only` | Conditional calibration reported as the aggregate | `WG-BM-066` | -- |
| `allow_reverse_travel` | One-way roads traversed in both directions | `WG-BM-008` | -- |
| `assume_conditional_independence` | Correlated observations multiplied as independent | `WG-BM-054`, `WG-BM-055` | -- |
| `assume_missing_at_random` | Missingness assumed uninformative | `WG-BM-056` | -- |
| `assume_missing_is_safe` | Absence of observation read as absence of hazard | `WG-BM-017` | -- |
| `average_scenario_inputs` | Averaging inputs instead of outcomes | `WG-BM-035` | -- |
| `choose_by_information_gain` | Observation chosen by entropy reduction | `WG-BM-050`, `WG-BM-053` | -- |
| `count_duplicate_evidence` | One measurement counted twice | `WG-BM-055` | -- |
| `detection_is_certainty` | Detection treated as certainty of hazard | `WG-BM-057`, `WG-BM-058` | -- |
| `edge_entry_time_only` | Edge safety checked at entry time only | `WG-BM-018`, `WG-BM-019`, `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026` | -- |
| `euclidean_destination` | Destination chosen by straight-line distance | `WG-BM-007` | -- |
| `fifo_assumption` | FIFO travel times assumed | `WG-BM-021` | -- |
| `final_perimeter_hazard` | Final fire perimeter used instead of arrival time | `WG-BM-018`, `WG-BM-019`, `WG-BM-020`, `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026` | -- |
| `fixed_half_probability_threshold` | Decision taken at p = 0.5 regardless of loss | `WG-BM-044`, `WG-BM-045`, `WG-BM-046`, `WG-BM-047`, `WG-BM-049`, `WG-BM-054`, `WG-BM-055`, `WG-BM-056`, `WG-BM-057` | -- |
| `forecast_always_trusted` | Forecast used regardless of arrival time | `WG-BM-030`, `WG-BM-031`, `WG-BM-043` | -- |
| `ignore_availability_time` | Observation availability time not checked | `WG-BM-052`, `WG-BM-053` | -- |
| `ignore_congestion` | Free-flow travel times under congestion | `WG-BM-027` | -- |
| `ignore_forecast_variance` | Predictive distribution collapsed to its mean | `WG-BM-044`, `WG-BM-045` | -- |
| `ignore_informative_missingness` | Sensor dropout treated as missing-at-random | `WG-BM-016` | -- |
| `ignore_observation_likelihood` | Observation likelihood ignored | `WG-BM-049`, `WG-BM-050`, `WG-BM-051`, `WG-BM-052`, `WG-BM-053`, `WG-BM-054`, `WG-BM-055`, `WG-BM-056`, `WG-BM-057`, `WG-BM-058` | -- |
| `ignore_pickup_duration` | Pickup duration ignored | `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026`, `WG-BM-027` | -- |
| `independent_edge_failures` | Correlated hazards multiplied as independent | `WG-BM-034`, `WG-BM-048` | -- |
| `isotropic_fire` | Wind bias dropped from fire spread | `WG-BM-010` | -- |
| `mean_only_ranking` | Policies ranked by mean outcome only | `WG-BM-038` | -- |
| `missing_as_zero` | Missing data imputed as zero | `WG-BM-004`, `WG-BM-015`, `WG-BM-016` | -- |
| `monotone_dispatch_assumption` | Dispatch feasibility assumed monotone | `WG-BM-026` | -- |
| `naive_unpaired_comparison` | Unpaired comparison across different worlds | `WG-BM-040` | -- |
| `nearest_base_only` | Only the nearest responder base considered | `WG-BM-024` | -- |
| `non_detection_is_absence` | Non-detection treated as certainty of no hazard | `WG-BM-057`, `WG-BM-058` | -- |
| `objective_ignored_use_mean` | Declared risk objective ignored | `WG-BM-060` | -- |
| `observation_future_leak` | Observation latency ignored | `WG-BM-014` | -- |
| `posterior_replaced_by_prior` | Posterior computed and then not used | `WG-BM-049`, `WG-BM-051`, `WG-BM-052`, `WG-BM-053`, `WG-BM-056`, `WG-BM-058` | -- |
| `renormalise_including_inadmissible` | Inadmissible scenarios included in the normalisation | `WG-BM-048` | -- |
| `resident_level_bootstrap` | Bootstrap over residents instead of worlds | `WG-BM-037` | -- |
| `silent_carry_forward` | Stale observation reported as current | `WG-BM-015`, `WG-BM-016` | -- |
| `single_ignition_only` | Only the primary ignition modelled | `WG-BM-012` | -- |
| `skill_implies_value` | Forecast skill equated with decision value | `WG-BM-029`, `WG-BM-030`, `WG-BM-031`, `WG-BM-033`, `WG-BM-043` | -- |
| `uniform_fuel` | Fuel discontinuity averaged away | `WG-BM-011` | -- |
| `unresolved_state_blocks_decision` | Unresolved world state treated as an unresolved decision | `WG-BM-061`, `WG-BM-063` | -- |

**39 / 39 mutations detected.**

