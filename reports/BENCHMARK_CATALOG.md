<!-- GENERATED FILE - regenerate with `python -m wg_benchmarks report`. Edits here will be overwritten. Generation is deterministic: no timestamps, no timings, so a regenerated report is a no-op diff unless something changed. -->

# Benchmark catalogue

43 benchmarks.

`exactness` says how much trust the expected answer deserves:

| value | meaning |
|---|---|
| `exact_analytic` | closed form derived by hand in the benchmark README |
| `exact_enumeration` | finite exhaustive enumeration; no approximation |
| `seeded_stochastic` | deterministic given the seed, checked within a stated tolerance |
| `qualitative` | an ordering, a sign or a flag rather than a number |

| ID | Label | Category | Difficulty | Exactness | Hand-checkable | Title |
|---|---|---|---|---|---|---|
| `WG-BM-001` | A1 | terrain | basic | `exact_analytic` | yes | Flat plane has zero slope and undefined aspect |
| `WG-BM-002` | A2 | terrain | basic | `exact_analytic` | yes | Tilted plane reproduces the analytic slope and aspect |
| `WG-BM-003` | A3 | terrain | intermediate | `exact_analytic` | yes | Ridge crest: directional transition and the zero-slope artefact |
| `WG-BM-004` | A4 | terrain | adversarial | `exact_analytic` | yes | Missing terrain stays missing and does not become zero elevation |
| `WG-BM-005` | B1 | road_graph | basic | `exact_enumeration` | yes | Single-exit village has exactly one egress route |
| `WG-BM-006` | B2 | road_graph | intermediate | `exact_enumeration` | yes | Two independent exits: articulation points exist but egress is redundant |
| `WG-BM-007` | B3 | road_graph | adversarial | `exact_enumeration` | yes | A shelter that exists geographically but is unreachable by road |
| `WG-BM-008` | B4 | road_graph | basic | `exact_enumeration` | yes | One-way roads are not traversable in reverse |
| `WG-BM-009` | C1 | fire | basic | `exact_analytic` | yes | Constant radial spread reproduces T(x) = |x - x0| / r |
| `WG-BM-010` | C2 | fire | intermediate | `exact_analytic` | yes | Constant wind produces a known anisotropic arrival field |
| `WG-BM-011` | C3 | fire | intermediate | `exact_analytic` | yes | Rate of spread changes at a known fuel boundary |
| `WG-BM-012` | C4 | fire | adversarial | `exact_enumeration` | yes | Spot ignition creates a disconnected threatened area |
| `WG-BM-013` | D1 | observation | basic | `exact_analytic` | yes | Zero-latency perfect observation equals contemporaneous truth |
| `WG-BM-014` | D2 | observation | adversarial | `exact_analytic` | yes | Ten-minute acquisition latency makes the present unobservable |
| `WG-BM-015` | D3 | observation | adversarial | `exact_analytic` | yes | A sensor outage stays missing and is never imputed or carried forward |
| `WG-BM-016` | D4 | observation | adversarial | `exact_analytic` | yes | Sensors fail because the fire reaches them (missing not at random) |
| `WG-BM-017` | D5 | observation | adversarial | `exact_enumeration` | yes | A false negative: fire exists, the detector reports nothing |
| `WG-BM-018` | E1 | routing | basic | `exact_analytic` | yes | The shortest route is infeasible; the long route is the answer |
| `WG-BM-019` | E2 | routing | adversarial | `exact_analytic` | yes | Mid-edge closure: the answer depends on a semantic choice that must be declared |
| `WG-BM-020` | E3 | routing | intermediate | `exact_analytic` | yes | Waiting is required: infeasible now, feasible after the front passes |
| `WG-BM-021` | E4 | routing | adversarial | `exact_enumeration` | yes | Non-FIFO edge: leaving later arrives earlier |
| `WG-BM-022` | F1 | assisted_dispatch | basic | `exact_analytic` | yes | Latest feasible dispatch for a basic assisted round trip |
| `WG-BM-023` | F2 | assisted_dispatch | basic | `exact_analytic` | yes | Latest dispatch moves one-for-one with pickup duration |
| `WG-BM-024` | F3 | assisted_dispatch | intermediate | `exact_analytic` | yes | The nearest base is not the right base when its corridor closes first |
| `WG-BM-025` | F4 | assisted_dispatch | intermediate | `exact_analytic` | yes | The right destination changes with the dispatch time |
| `WG-BM-026` | F5 | assisted_dispatch | adversarial | `exact_enumeration` | yes | Dispatch feasibility is feasible, then infeasible, then feasible again |
| `WG-BM-027` | F6 | traffic | adversarial | `exact_analytic` | yes | Responder ingress competes with evacuee egress on one road |
| `WG-BM-028` | G1 | forecast_value | basic | `exact_analytic` | yes | A 500 m forecast error that changes no decision and costs nothing |
| `WG-BM-029` | G2 | forecast_value | adversarial | `exact_analytic` | yes | A 20 m forecast error on a decision boundary costs 92 |
| `WG-BM-030` | G3 | forecast_value | adversarial | `exact_analytic` | yes | An almost-perfect forecast that arrives after the last useful decision time |
| `WG-BM-031` | G4 | forecast_value | adversarial | `exact_analytic` | yes | A crude, timely forecast beats an excellent, late one |
| `WG-BM-032` | G5 | forecast_value | intermediate | `exact_analytic` | yes | A conservative trigger already gets it right: forecast added value is zero |
| `WG-BM-033` | G6 | forecast_value | adversarial | `exact_analytic` | yes | Forecast harm: 80% accurate, and worse than the robust baseline |
| `WG-BM-034` | H1 | scenario_uncertainty | adversarial | `exact_analytic` | yes | Perfectly correlated road failures: multiplying marginals is wrong by 3.3x |
| `WG-BM-035` | H2 | scenario_uncertainty | adversarial | `exact_analytic` | yes | Mutually exclusive scenarios: averaging the inputs says both routes are fine |
| `WG-BM-036` | H3 | scenario_uncertainty | adversarial | `exact_analytic` | yes | Adding two 0.1% scenarios moves expected loss by 0.5 and sup-regret by 8 |
| `WG-BM-037` | I1 | statistics | adversarial | `seeded_stochastic` | yes | Ten worlds, ten thousand residents, and an effective sample size of ten |
| `WG-BM-038` | I2 | statistics | intermediate | `exact_analytic` | yes | Policy A has the better average and a five times worse tail |
| `WG-BM-039` | I3 | statistics | intermediate | `exact_analytic` | yes | Overwhelmingly significant and practically equivalent at the same time |
| `WG-BM-040` | I4 | statistics | adversarial | `exact_analytic` | yes | Unpaired comparison across different worlds reverses the true ranking |
| `WG-BM-041` | J1 | protectability | basic | `exact_analytic` | yes | Deep uncertainty, but one action is acceptable in every world |
| `WG-BM-042` | J2 | protectability | intermediate | `exact_analytic` | yes | No robust action exists, and a timely observation supplies one |
| `WG-BM-043` | J3 | protectability | adversarial | `exact_analytic` | yes | The same observation, five minutes too late, is worth nothing |

## Purpose of each benchmark

- **WG-BM-001 (A1)** — Pin the degenerate case: on perfectly flat terrain slope is exactly zero and aspect is undefined, not an arbitrary compass bearing. <br/>`benchmarks/terrain/WG-BM-001_A1_flat_plane`
- **WG-BM-002 (A2)** — Check slope magnitude and aspect convention against a plane whose gradient is known in closed form, including the sign convention of the aspect. <br/>`benchmarks/terrain/WG-BM-002_A2_tilted_plane`
- **WG-BM-003 (A3)** — Verify behaviour at a directional transition: the two flanks must face opposite ways, and the crest cell must be recognised as an artefact of the finite difference rather than as flat ground. <br/>`benchmarks/terrain/WG-BM-003_A3_ridge`
- **WG-BM-004 (A4)** — A single no-data cell must propagate as undefined slope over its 3x3 neighbourhood and nowhere else. Imputing zero elevation manufactures a 100 m cliff. <br/>`benchmarks/terrain/WG-BM-004_A4_missing_cells`
- **WG-BM-005 (B1)** — Establish the ground truth for a genuine single point of failure: one egress route, one articulation node, two bridges. <br/>`benchmarks/routing/WG-BM-005_B1_single_exit_village`
- **WG-BM-006 (B2)** — Distinguish 'this graph contains articulation points' from 'this community has one way out'. The two are routinely conflated. <br/>`benchmarks/routing/WG-BM-006_B2_two_independent_exits`
- **WG-BM-007 (B3)** — The nearest destination in metres is 6x closer than the nearest destination by road, and has no road to it at all. A router must not select it. <br/>`benchmarks/routing/WG-BM-007_B3_disconnected_shelter`
- **WG-BM-008 (B4)** — A contraflow corridor is directed. Reachability must be asymmetric: the outbound trip exists, the return trip does not. <br/>`benchmarks/routing/WG-BM-008_B4_directed_road`
- **WG-BM-009 (C1)** — Fix the simplest possible hazard field so that arrival times and their ordering can be checked exactly, including the tie between equidistant points. <br/>`benchmarks/fire/WG-BM-009_C1_constant_radial_arrival`
- **WG-BM-010 (C2)** — Pin head, back and flank arrival times for a shifted-ellipse front so that anisotropy cannot be quietly averaged away. <br/>`benchmarks/fire/WG-BM-010_C2_constant_wind_bias`
- **WG-BM-011 (C3)** — A sharp fuel break must produce a kink in the arrival-time profile, not a smooth average. <br/>`benchmarks/fire/WG-BM-011_C3_fuel_discontinuity`
- **WG-BM-012 (C4)** — A spot fire 2 km ahead of the main front threatens an area that is not connected to the main perimeter. Area-connectivity assumptions break. <br/>`benchmarks/fire/WG-BM-012_C4_spot_ignition`
- **WG-BM-013 (D1)** — Positive control for the observation pipeline: with no latency and no outage, the available observation is exactly the current truth. <br/>`benchmarks/observations/WG-BM-013_D1_zero_latency`
- **WG-BM-014 (D2)** — The decision maker at time t may only see observations acquired at or before t - 10. Future information leakage is the single most common way an offline evaluation flatters a forecasting system. <br/>`benchmarks/observations/WG-BM-014_D2_fixed_latency`
- **WG-BM-015 (D3)** — During a 30-minute outage the correct answer is 'unknown, last seen 30 minutes ago', not zero and not the stale value presented as current. <br/>`benchmarks/observations/WG-BM-015_D3_sensor_outage`
- **WG-BM-016 (D4)** — Dropout is caused by the hazard, so averaging the surviving sensors estimates the hazard at zero. Silence is evidence, not absence of evidence. <br/>`benchmarks/observations/WG-BM-016_D4_fire_correlated_failure`
- **WG-BM-017 (D5)** — Absence of detection is not detection of absence. The route chosen by trusting a non-detection through an unreliable detector is fatal; the precautionary route costs 5. <br/>`benchmarks/observations/WG-BM-017_D5_false_negative`
- **WG-BM-018 (E1)** — Distance is not feasibility. A 5-minute route that closes at minute 4 is not a route. <br/>`benchmarks/routing/WG-BM-018_E1_short_unsafe_vs_long_safe`
- **WG-BM-019 (E2)** — A traveller enters a 10-minute edge at t = 0 and the hazard reaches it at t = 5. There is no convention-free answer, so the convention is part of the benchmark. <br/>`benchmarks/routing/WG-BM-019_E2_mid_edge_closure`
- **WG-BM-020 (E3)** — Some routes only exist for a traveller willing to hold at a junction. A system that forbids waiting must report infeasible, not silently allow it. <br/>`benchmarks/routing/WG-BM-020_E3_waiting_needed`
- **WG-BM-021 (E4)** — Break the FIFO assumption that every time-dependent Dijkstra variant relies on. Departing at minute 5 arrives 45 minutes before departing at minute 0. <br/>`benchmarks/routing/WG-BM-021_E4_non_fifo_edge`
- **WG-BM-022 (F1)** — The canonical assisted-dispatch arithmetic: ingress, pickup and egress must all complete before their respective deadlines, and the latest dispatch time follows by subtraction. <br/>`benchmarks/dispatch/WG-BM-022_F1_basic_round_trip`
- **WG-BM-023 (F2)** — Sweep the on-scene pickup duration and check that the latest feasible dispatch decreases by exactly the same amount, until the mission becomes impossible at any dispatch time. <br/>`benchmarks/dispatch/WG-BM-023_F2_pickup_sensitivity`
- **WG-BM-024 (F3)** — Base selection must consider the ingress corridor's closure time, not just travel distance. The far base gives 5 more minutes of dispatch latitude. <br/>`benchmarks/dispatch/WG-BM-024_F3_two_responder_bases`
- **WG-BM-025 (F4)** — A near refuge that closes early and a far shelter that stays open. The correct destination is a function of when the mission starts. <br/>`benchmarks/dispatch/WG-BM-025_F4_alternate_destination`
- **WG-BM-026 (F5)** — Prove that a single scalar latest-dispatch-time is not sufficient. The feasible set here is two disjoint intervals and dispatching at minute 10 - comfortably below the latest feasible time of 34 - fails. <br/>`benchmarks/dispatch/WG-BM-026_F5_non_monotone_feasibility`
- **WG-BM-027 (F6)** — Without a capacity interaction the mission succeeds with 15 minutes to spare; with it, the mission cannot be completed at any dispatch time. <br/>`benchmarks/traffic/WG-BM-027_F6_inbound_outbound_conflict`
- **WG-BM-028 (G1)** — Degrading forecast accuracy from 0 m to 500 m leaves every action and every loss unchanged, because the error does not cross the decision boundary. Skill fell; value did not. <br/>`benchmarks/forecast_value/WG-BM-028_G1_error_without_decision_impact`
- **WG-BM-029 (G2)** — The mirror image of WG-BM-028: an error 25 times smaller, sitting on the decision boundary, flips the route choice and produces a realised regret of 92. <br/>`benchmarks/forecast_value/WG-BM-029_G2_tiny_error_large_impact`
- **WG-BM-030 (G3)** — Skill 0.98, spatial error 10 m, issued at minute 30 for a decision that must be made by minute 20. Decision value is negative, not merely zero, because waiting for it forfeits the action. <br/>`benchmarks/forecast_value/WG-BM-030_G3_accurate_but_late`
- **WG-BM-031 (G4)** — Two forecasts in one decision: skill 0.98 at minute 30 and skill 0.40 at minute 5, against a deadline of minute 20. The ranking by skill is the reverse of the ranking by value. <br/>`benchmarks/forecast_value/WG-BM-031_G4_crude_but_timely`
- **WG-BM-032 (G5)** — A cheap trip-wire policy takes exactly the same action as the sophisticated forecast in every scenario. The added value of the forecast is exactly 0, even though EVPI against a fixed action is 2.5. <br/>`benchmarks/forecast_value/WG-BM-032_G5_strong_baseline`
- **WG-BM-033 (G6)** — The forecast is right in four scenarios out of five and wrong in the one that carries the consequences. Delta J is negative: acting on it is worse than the robust policy. <br/>`benchmarks/forecast_value/WG-BM-033_G6_forecast_harm`
- **WG-BM-034 (H1)** — Two roads with marginal failure probability 0.3 each fail together. The probability of losing all egress is 0.3, not 0.09, and the difference flips the decision. <br/>`benchmarks/statistics/WG-BM-034_H1_correlated_edge_hazards`
- **WG-BM-035 (H2)** — Route A is right in scenario 1 and fatal in scenario 2, and vice versa. Averaging the fire fields produces a world in which neither route is blocked and the expected loss is zero. Averaging the losses gives 50. <br/>`benchmarks/statistics/WG-BM-035_H2_mutually_exclusive_scenarios`
- **WG-BM-036 (H3)** — Sup-regret is a maximum over the scenario set, so it grows mechanically as scenarios are added, and the minimax-regret recommendation flips on 0.2% of probability mass. CVaR does not. <br/>`benchmarks/statistics/WG-BM-036_H3_ensemble_size_trap`
- **WG-BM-037 (I1)** — Residents inside a simulated world are perfectly correlated. Bootstrapping residents produces a confidence interval 33 times too narrow; bootstrapping worlds does not. <br/>`benchmarks/statistics/WG-BM-037_I1_pseudoreplication`
- **WG-BM-038 (I2)** — Mean and CVaR rank two policies in opposite orders. A system that reports only the mean cannot express the difference that matters. <br/>`benchmarks/statistics/WG-BM-038_I2_mean_vs_tail_risk`
- **WG-BM-039 (I3)** — Two policies differ by 0.3 units with a practical margin of 1.0. With n = 2000 the difference is highly significant and entirely without operational meaning. <br/>`benchmarks/statistics/WG-BM-039_I3_practical_equivalence`
- **WG-BM-040 (I4)** — Policy A is evaluated on mostly easy worlds and policy B on mostly hard ones. The naive comparison favours A by 10.3; the paired comparison on the common worlds favours B by 3. <br/>`benchmarks/statistics/WG-BM-040_I4_hidden_selection_bias`
- **WG-BM-041 (J1)** — Two plausible worlds disagree completely about where the fire goes, and the same action is acceptable in both. EVPI is exactly zero: the resident is robustly protectable and no observation is worth making. <br/>`benchmarks/forecast_value/WG-BM-041_J1_robust_action_exists`
- **WG-BM-042 (J2)** — Two worlds require incompatible actions. Without information the best fixed action loses 45 in expectation; a timely observation reduces that to 0, so the observation is worth the full EVPI of 45. <br/>`benchmarks/forecast_value/WG-BM-042_J2_observation_changes_protectability`
- **WG-BM-043 (J3)** — WG-BM-042 with the recon flight arriving at minute 15 instead of 5. EVPI is unchanged at 45; the realisable value is 0 and waiting for it is worse than acting on the prior. <br/>`benchmarks/forecast_value/WG-BM-043_J3_observation_too_late`
