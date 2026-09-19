<!-- GENERATED FILE - regenerate with `python -m wg_benchmarks report`. Edits here will be overwritten. Generation is deterministic: no timestamps, no timings, so a regenerated report is a no-op diff unless something changed. -->

# Mutation test results

Each mutation is a deliberate, plausible implementation bug injected into the reference solvers.  A benchmark *detects* a mutation when it passes clean and fails mutated.

| Mutation | Description | Detected by | Declared but missed |
|---|---|---|---|
| `allow_reverse_travel` | One-way roads traversed in both directions | `WG-BM-008` | -- |
| `assume_missing_is_safe` | Absence of observation read as absence of hazard | `WG-BM-017` | -- |
| `average_scenario_inputs` | Averaging inputs instead of outcomes | `WG-BM-035` | -- |
| `edge_entry_time_only` | Edge safety checked at entry time only | `WG-BM-018`, `WG-BM-019`, `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026` | -- |
| `euclidean_destination` | Destination chosen by straight-line distance | `WG-BM-007` | -- |
| `fifo_assumption` | FIFO travel times assumed | `WG-BM-021` | -- |
| `final_perimeter_hazard` | Final fire perimeter used instead of arrival time | `WG-BM-018`, `WG-BM-019`, `WG-BM-020`, `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026` | -- |
| `forecast_always_trusted` | Forecast used regardless of arrival time | `WG-BM-030`, `WG-BM-031`, `WG-BM-043` | -- |
| `ignore_congestion` | Free-flow travel times under congestion | `WG-BM-027` | -- |
| `ignore_informative_missingness` | Sensor dropout treated as missing-at-random | `WG-BM-016` | -- |
| `ignore_pickup_duration` | Pickup duration ignored | `WG-BM-022`, `WG-BM-023`, `WG-BM-024`, `WG-BM-025`, `WG-BM-026`, `WG-BM-027` | -- |
| `independent_edge_failures` | Correlated hazards multiplied as independent | `WG-BM-034` | -- |
| `isotropic_fire` | Wind bias dropped from fire spread | `WG-BM-010` | -- |
| `mean_only_ranking` | Policies ranked by mean outcome only | `WG-BM-038` | -- |
| `missing_as_zero` | Missing data imputed as zero | `WG-BM-004`, `WG-BM-015`, `WG-BM-016` | -- |
| `monotone_dispatch_assumption` | Dispatch feasibility assumed monotone | `WG-BM-026` | -- |
| `naive_unpaired_comparison` | Unpaired comparison across different worlds | `WG-BM-040` | -- |
| `nearest_base_only` | Only the nearest responder base considered | `WG-BM-024` | -- |
| `observation_future_leak` | Observation latency ignored | `WG-BM-014` | -- |
| `resident_level_bootstrap` | Bootstrap over residents instead of worlds | `WG-BM-037` | -- |
| `silent_carry_forward` | Stale observation reported as current | `WG-BM-015`, `WG-BM-016` | -- |
| `single_ignition_only` | Only the primary ignition modelled | `WG-BM-012` | -- |
| `skill_implies_value` | Forecast skill equated with decision value | `WG-BM-029`, `WG-BM-030`, `WG-BM-031`, `WG-BM-033`, `WG-BM-043` | -- |
| `uniform_fuel` | Fuel discontinuity averaged away | `WG-BM-011` | -- |

**24 / 24 mutations detected.**

