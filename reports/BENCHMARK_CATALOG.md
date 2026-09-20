<!-- GENERATED FILE - regenerate with `python -m wg_benchmarks report`. Edits here will be overwritten. Generation is deterministic: no timestamps, no timings, so a regenerated report is a no-op diff unless something changed. -->

# Benchmark catalogue

66 benchmarks.

`exactness` says how much trust the expected answer deserves:

| value | meaning |
|---|---|
| `CLOSED_FORM` | an analytic expression derived by hand; exact to machine precision |
| `FINITE_ENUMERATION` | exhaustive enumeration of a finite set; no approximation |
| `NUMERIC_REFERENCE` | a numerical procedure with a declared, analytically justified error bound |
| `SEEDED_STOCHASTIC_VALIDATION` | reproducible given the seed, checked within a stated Monte Carlo band |

| ID | Label | Category | Difficulty | Exactness | Hand-checkable | Title |
|---|---|---|---|---|---|---|
| `WG-BM-001` | A1 | terrain | basic | `CLOSED_FORM` | yes | Flat plane has zero slope and undefined aspect |
| `WG-BM-002` | A2 | terrain | basic | `CLOSED_FORM` | yes | Tilted plane reproduces the analytic slope and aspect |
| `WG-BM-003` | A3 | terrain | intermediate | `CLOSED_FORM` | yes | Ridge crest: directional transition and the zero-slope artefact |
| `WG-BM-004` | A4 | terrain | adversarial | `CLOSED_FORM` | yes | Missing terrain stays missing and does not become zero elevation |
| `WG-BM-005` | B1 | road_graph | basic | `FINITE_ENUMERATION` | yes | Single-exit village has exactly one egress route |
| `WG-BM-006` | B2 | road_graph | intermediate | `FINITE_ENUMERATION` | yes | Two independent exits: articulation points exist but egress is redundant |
| `WG-BM-007` | B3 | road_graph | adversarial | `FINITE_ENUMERATION` | yes | A shelter that exists geographically but is unreachable by road |
| `WG-BM-008` | B4 | road_graph | basic | `FINITE_ENUMERATION` | yes | One-way roads are not traversable in reverse |
| `WG-BM-009` | C1 | fire | basic | `CLOSED_FORM` | yes | Constant radial spread reproduces T(x) = |x - x0| / r |
| `WG-BM-010` | C2 | fire | intermediate | `CLOSED_FORM` | yes | Constant wind produces a known anisotropic arrival field |
| `WG-BM-011` | C3 | fire | intermediate | `CLOSED_FORM` | yes | Rate of spread changes at a known fuel boundary |
| `WG-BM-012` | C4 | fire | adversarial | `FINITE_ENUMERATION` | yes | Spot ignition creates a disconnected threatened area |
| `WG-BM-013` | D1 | observation | basic | `CLOSED_FORM` | yes | Zero-latency perfect observation equals contemporaneous truth |
| `WG-BM-014` | D2 | observation | adversarial | `CLOSED_FORM` | yes | Ten-minute acquisition latency makes the present unobservable |
| `WG-BM-015` | D3 | observation | adversarial | `CLOSED_FORM` | yes | A sensor outage stays missing and is never imputed or carried forward |
| `WG-BM-016` | D4 | observation | adversarial | `CLOSED_FORM` | yes | Sensors fail because the fire reaches them (missing not at random) |
| `WG-BM-017` | D5 | observation | adversarial | `FINITE_ENUMERATION` | yes | A false negative: fire exists, the detector reports nothing |
| `WG-BM-018` | E1 | routing | basic | `CLOSED_FORM` | yes | The shortest route is infeasible; the long route is the answer |
| `WG-BM-019` | E2 | routing | adversarial | `CLOSED_FORM` | yes | Mid-edge closure: the answer depends on a semantic choice that must be declared |
| `WG-BM-020` | E3 | routing | intermediate | `CLOSED_FORM` | yes | Waiting is required: infeasible now, feasible after the front passes |
| `WG-BM-021` | E4 | routing | adversarial | `FINITE_ENUMERATION` | yes | Non-FIFO edge: leaving later arrives earlier |
| `WG-BM-022` | F1 | assisted_dispatch | basic | `CLOSED_FORM` | yes | Latest feasible dispatch for a basic assisted round trip |
| `WG-BM-023` | F2 | assisted_dispatch | basic | `CLOSED_FORM` | yes | Latest dispatch moves one-for-one with pickup duration |
| `WG-BM-024` | F3 | assisted_dispatch | intermediate | `CLOSED_FORM` | yes | The nearest base is not the right base when its corridor closes first |
| `WG-BM-025` | F4 | assisted_dispatch | intermediate | `CLOSED_FORM` | yes | The right destination changes with the dispatch time |
| `WG-BM-026` | F5 | assisted_dispatch | adversarial | `FINITE_ENUMERATION` | yes | Dispatch feasibility is feasible, then infeasible, then feasible again |
| `WG-BM-027` | F6 | traffic | adversarial | `CLOSED_FORM` | yes | Responder ingress competes with evacuee egress on one road |
| `WG-BM-028` | G1 | forecast_value | basic | `CLOSED_FORM` | yes | A 500 m forecast error that changes no decision and costs nothing |
| `WG-BM-029` | G2 | forecast_value | adversarial | `CLOSED_FORM` | yes | A 20 m forecast error on a decision boundary costs 92 |
| `WG-BM-030` | G3 | forecast_value | adversarial | `CLOSED_FORM` | yes | An almost-perfect forecast that arrives after the last useful decision time |
| `WG-BM-031` | G4 | forecast_value | adversarial | `CLOSED_FORM` | yes | A crude, timely forecast beats an excellent, late one |
| `WG-BM-032` | G5 | forecast_value | intermediate | `CLOSED_FORM` | yes | A conservative trigger already gets it right: forecast added value is zero |
| `WG-BM-033` | G6 | forecast_value | adversarial | `CLOSED_FORM` | yes | Forecast harm: 80% accurate, and worse than the robust baseline |
| `WG-BM-034` | H1 | scenario_uncertainty | adversarial | `CLOSED_FORM` | yes | Perfectly correlated road failures: multiplying marginals is wrong by 3.3x |
| `WG-BM-035` | H2 | scenario_uncertainty | adversarial | `CLOSED_FORM` | yes | Mutually exclusive scenarios: averaging the inputs says both routes are fine |
| `WG-BM-036` | H3 | scenario_uncertainty | adversarial | `CLOSED_FORM` | yes | Adding two 0.1% scenarios moves expected loss by 0.5 and sup-regret by 8 |
| `WG-BM-037` | I1 | statistics | adversarial | `SEEDED_STOCHASTIC_VALIDATION` | yes | Ten worlds, ten thousand residents, and an effective sample size of ten |
| `WG-BM-038` | I2 | statistics | intermediate | `CLOSED_FORM` | yes | Policy A has the better average and a five times worse tail |
| `WG-BM-039` | I3 | statistics | intermediate | `CLOSED_FORM` | yes | Overwhelmingly significant and practically equivalent at the same time |
| `WG-BM-040` | I4 | statistics | adversarial | `CLOSED_FORM` | yes | Unpaired comparison across different worlds reverses the true ranking |
| `WG-BM-041` | J1 | protectability | basic | `CLOSED_FORM` | yes | Deep uncertainty, but one action is acceptable in every world |
| `WG-BM-042` | J2 | protectability | intermediate | `CLOSED_FORM` | yes | No robust action exists, and a timely observation supplies one |
| `WG-BM-043` | J3 | protectability | adversarial | `CLOSED_FORM` | yes | The same observation, five minutes too late, is worth nothing |
| `WG-BM-044` | K1 | probabilistic_forecast | basic | `CLOSED_FORM` | yes | Same mean, different uncertainty, different correct action |
| `WG-BM-045` | K2 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | Better point error, worse decision: a 16 m forecast beaten by a 46 m one |
| `WG-BM-046` | K3 | probabilistic_forecast | basic | `CLOSED_FORM` | yes | The action switches at p* = 0.2, which the loss matrix fixes and 0.5 does not |
| `WG-BM-047` | K4 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | Asymmetric loss puts the threshold at one per cent |
| `WG-BM-048` | K5 | probabilistic_forecast | intermediate | `FINITE_ENUMERATION` | yes | A coherent ensemble: admissibility, normalisation and the joint |
| `WG-BM-049` | K6 | probabilistic_forecast | basic | `CLOSED_FORM` | yes | Observation, posterior, decision: the canonical update |
| `WG-BM-050` | K7 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | The posterior moves, the action does not: EVSI is exactly zero |
| `WG-BM-051` | K8 | probabilistic_forecast | intermediate | `CLOSED_FORM` | yes | Exact expected value of sample information: 22 against an EVPI of 40 |
| `WG-BM-052` | K9 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | Statistical value 22, operational value 0: the sensor reports at minute 12 |
| `WG-BM-053` | K10 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | A weak timely sensor beats a perfect late one, 13 to 0 |
| `WG-BM-054` | K11 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | Two sensors that fail together: independence turns 0.174 into 0.059 |
| `WG-BM-055` | K12 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | One measurement, two records: duplicate evidence must not double confidence |
| `WG-BM-056` | K13 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | Silence is evidence: a missing report raises P(dangerous) from 0.05 to 0.387 |
| `WG-BM-057` | K14 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | No detection leaves P(fire) at 0.073, which is still above the threshold |
| `WG-BM-058` | K15 | probabilistic_forecast | adversarial | `CLOSED_FORM` | yes | A detection raises P(fire) from 0.02 to 0.22, and 0.22 is not 1 |
| `WG-BM-059` | L1 | risk | basic | `FINITE_ENUMERATION` | yes | Better average, worse worst case, and no winner declared |
| `WG-BM-060` | L2 | risk | intermediate | `FINITE_ENUMERATION` | yes | Ranking reversal between the mean and CVaR, with the objective declared |
| `WG-BM-061` | L3 | risk | adversarial | `FINITE_ENUMERATION` | yes | The world is unresolved and the decision is not |
| `WG-BM-062` | L4 | risk | adversarial | `FINITE_ENUMERATION` | yes | The world is 97 per cent resolved and the decision turns on 0.21 |
| `WG-BM-063` | L5 | risk | intermediate | `FINITE_ENUMERATION` | yes | Poor forecast skill, stable decision |
| `WG-BM-064` | M1 | calibration | basic | `CLOSED_FORM` | yes | A perfectly calibrated binary forecast, with the Murphy decomposition exact |
| `WG-BM-065` | M2 | calibration | intermediate | `CLOSED_FORM` | yes | Same classifications, probabilities pushed to the extremes, one action changes |
| `WG-BM-066` | M3 | calibration | adversarial | `CLOSED_FORM` | yes | Perfect aggregate calibration hiding two badly wrong regimes |

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
- **WG-BM-044 (K1)** — Two forecasts with identical mean and different spread. A point-estimate policy cannot tell them apart; the correct action differs. <br/>`benchmarks/probabilistic_forecast/WG-BM-044_K1_same_mean_different_uncertainty`
- **WG-BM-045 (K2)** — Forecast A has a third of B's location error and a fat tail; B is further out and tight. B attains the best achievable expected loss and A does not. <br/>`benchmarks/probabilistic_forecast/WG-BM-045_K2_better_point_worse_decision`
- **WG-BM-046 (K3)** — Derive the Bayes-optimal action as a function of the hazard probability and verify the switch point. At p = 0.35 a half-probability rule gives the wrong answer. <br/>`benchmarks/probabilistic_forecast/WG-BM-046_K3_calibrated_probability_changes_action`
- **WG-BM-047 (K4)** — When an unnecessary precaution costs 5 and an entrapment costs 495, the action switches at p* = 5/500 = 0.01. A half-probability rule proceeds at p = 0.4, at 66 times the optimal expected loss. <br/>`benchmarks/probabilistic_forecast/WG-BM-047_K4_asymmetric_loss_threshold`
- **WG-BM-048 (K5)** — Four admissible worlds and one inadmissible one. Weights renormalise over the admissible set, the joint closure probability is read off the ensemble, and multiplying marginals flips the decision. <br/>`benchmarks/probabilistic_forecast/WG-BM-048_K5_coherent_scenario_ensemble`
- **WG-BM-049 (K6)** — Two hypotheses, known priors, known likelihoods. Bayes' rule moves the belief across the decision threshold and the action changes from stay to evacuate. <br/>`benchmarks/probabilistic_forecast/WG-BM-049_K6_posterior_update`
- **WG-BM-050 (K7)** — An observation with positive mutual information and zero decision value. More information does not necessarily change or improve a decision. <br/>`benchmarks/probabilistic_forecast/WG-BM-050_K7_information_without_decision_value`
- **WG-BM-051 (K8)** — Two worlds needing opposite actions. The prior-optimal action is to shelter at a cost of 40; an imperfect bearing sensor reduces that to 18, so EVSI is 22. Computed by enumeration, not simulation. <br/>`benchmarks/probabilistic_forecast/WG-BM-051_K8_valuable_information`
- **WG-BM-052 (K9)** — WG-BM-051 with acquisition at minute 5, availability at minute 12 and a decision deadline at minute 10. The information exists and cannot be used. <br/>`benchmarks/probabilistic_forecast/WG-BM-052_K9_information_arrives_too_late`
- **WG-BM-053 (K10)** — Two candidate observations on the same decision. Ranked by information the perfect late sensor wins; ranked by operational value the weak early one does. Quality and timing must be evaluated jointly. <br/>`benchmarks/probabilistic_forecast/WG-BM-053_K10_weaker_but_timely_wins`
- **WG-BM-054 (K11)** — Identical marginals, a strongly correlated joint. Multiplying the marginals produces an overconfident posterior and flips the action to the unsafe one. <br/>`benchmarks/probabilistic_forecast/WG-BM-054_K11_correlated_observation_errors`
- **WG-BM-055 (K12)** — The degenerate limit of WG-BM-054. Two records carry the same underlying measurement; counting both doubles the log-likelihood ratio from -2 to -4 bits and flips the action. <br/>`benchmarks/probabilistic_forecast/WG-BM-055_K12_duplicate_evidence`
- **WG-BM-056 (K13)** — The probability that a report goes missing depends on the hazard, so missingness is itself an observation. An MCAR assumption leaves the belief at the prior and takes the unsafe action. <br/>`benchmarks/probabilistic_forecast/WG-BM-056_K13_fire_correlated_missingness`
- **WG-BM-057 (K14)** — A detector with a 30 per cent false-negative rate. After a negative reading the posterior falls from 0.2 to 0.073 and the conservative action is still correct. Non-detection does not license standing down. <br/>`benchmarks/probabilistic_forecast/WG-BM-057_K14_non_detection_is_not_absence`
- **WG-BM-058 (K15)** — Against a low base rate a detection is strong evidence and far from proof. Treating it as certainty escalates from traffic diversion to full evacuation and triples the expected loss. <br/>`benchmarks/probabilistic_forecast/WG-BM-058_K15_false_positive`
- **WG-BM-059 (L1)** — Both metrics are computed exactly and neither is preferred. A suite that always names a winner has an undeclared risk attitude built into it. <br/>`benchmarks/risk/WG-BM-059_L1_expectation_versus_worst_case`
- **WG-BM-060 (L2)** — A three-outcome distribution where A has the better mean by 2.1 and a CVaR five times worse. The declared objective is CVaR and the recommendation must follow it. <br/>`benchmarks/risk/WG-BM-060_L2_expectation_versus_cvar`
- **WG-BM-061 (L3)** — Three near-equal scenarios and one action that is optimal in all of them. EVPI is exactly zero: uncertainty about the world does not imply a need for more information. <br/>`benchmarks/risk/WG-BM-061_L3_unresolved_state_resolved_decision`
- **WG-BM-062 (L4)** — The mirror image of WG-BM-061. State certainty is high, the two actions differ by 0.21 in expected loss, and a perturbation of 0.22 to a single loss cell reverses the recommendation. <br/>`benchmarks/risk/WG-BM-062_L4_resolved_state_fragile_decision`
- **WG-BM-063 (L5)** — A forecast with a skill score of 0.25 spread over four worlds, all of which select the same staging action. Poor skill does not imply a poor decision. <br/>`benchmarks/risk/WG-BM-063_L5_robust_action_despite_poor_skill`
- **WG-BM-064 (M1)** — Reference case for the calibration arithmetic: reliability zero, the Brier decomposition closing to the last bit, and no decision cost. <br/>`benchmarks/calibration/WG-BM-064_M1_perfectly_calibrated`
- **WG-BM-065 (M2)** — Identical cases and outcomes to WG-BM-064 with overconfident probabilities. Resolution and uncertainty are unchanged; the whole Brier penalty is the reliability term, and one group's action flips. <br/>`benchmarks/calibration/WG-BM-065_M2_overconfident`
- **WG-BM-066 (M3)** — Two strata, each wrong by 0.3 in opposite directions, averaging to a flawless aggregate reliability of zero. One stratum's action is wrong at a cost of 5 per case. <br/>`benchmarks/calibration/WG-BM-066_M3_calibrated_globally_miscalibrated_conditionally`
