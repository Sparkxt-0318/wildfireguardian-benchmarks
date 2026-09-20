<!-- GENERATED FILE - regenerate with `python -m wg_benchmarks report`. Edits here will be overwritten. Generation is deterministic: no timestamps, no timings, so a regenerated report is a no-op diff unless something changed. -->

# Last recorded suite run

66/66 benchmarks pass against the reference solvers.

| ID | Label | Status | Title |
|---|---|---|---|
| `WG-BM-001` | A1 | PASS | Flat plane has zero slope and undefined aspect |
| `WG-BM-002` | A2 | PASS | Tilted plane reproduces the analytic slope and aspect |
| `WG-BM-003` | A3 | PASS | Ridge crest: directional transition and the zero-slope artefact |
| `WG-BM-004` | A4 | PASS | Missing terrain stays missing and does not become zero elevation |
| `WG-BM-005` | B1 | PASS | Single-exit village has exactly one egress route |
| `WG-BM-006` | B2 | PASS | Two independent exits: articulation points exist but egress is redundant |
| `WG-BM-007` | B3 | PASS | A shelter that exists geographically but is unreachable by road |
| `WG-BM-008` | B4 | PASS | One-way roads are not traversable in reverse |
| `WG-BM-009` | C1 | PASS | Constant radial spread reproduces T(x) = |x - x0| / r |
| `WG-BM-010` | C2 | PASS | Constant wind produces a known anisotropic arrival field |
| `WG-BM-011` | C3 | PASS | Rate of spread changes at a known fuel boundary |
| `WG-BM-012` | C4 | PASS | Spot ignition creates a disconnected threatened area |
| `WG-BM-013` | D1 | PASS | Zero-latency perfect observation equals contemporaneous truth |
| `WG-BM-014` | D2 | PASS | Ten-minute acquisition latency makes the present unobservable |
| `WG-BM-015` | D3 | PASS | A sensor outage stays missing and is never imputed or carried forward |
| `WG-BM-016` | D4 | PASS | Sensors fail because the fire reaches them (missing not at random) |
| `WG-BM-017` | D5 | PASS | A false negative: fire exists, the detector reports nothing |
| `WG-BM-018` | E1 | PASS | The shortest route is infeasible; the long route is the answer |
| `WG-BM-019` | E2 | PASS | Mid-edge closure: the answer depends on a semantic choice that must be declared |
| `WG-BM-020` | E3 | PASS | Waiting is required: infeasible now, feasible after the front passes |
| `WG-BM-021` | E4 | PASS | Non-FIFO edge: leaving later arrives earlier |
| `WG-BM-022` | F1 | PASS | Latest feasible dispatch for a basic assisted round trip |
| `WG-BM-023` | F2 | PASS | Latest dispatch moves one-for-one with pickup duration |
| `WG-BM-024` | F3 | PASS | The nearest base is not the right base when its corridor closes first |
| `WG-BM-025` | F4 | PASS | The right destination changes with the dispatch time |
| `WG-BM-026` | F5 | PASS | Dispatch feasibility is feasible, then infeasible, then feasible again |
| `WG-BM-027` | F6 | PASS | Responder ingress competes with evacuee egress on one road |
| `WG-BM-028` | G1 | PASS | A 500 m forecast error that changes no decision and costs nothing |
| `WG-BM-029` | G2 | PASS | A 20 m forecast error on a decision boundary costs 92 |
| `WG-BM-030` | G3 | PASS | An almost-perfect forecast that arrives after the last useful decision time |
| `WG-BM-031` | G4 | PASS | A crude, timely forecast beats an excellent, late one |
| `WG-BM-032` | G5 | PASS | A conservative trigger already gets it right: forecast added value is zero |
| `WG-BM-033` | G6 | PASS | Forecast harm: 80% accurate, and worse than the robust baseline |
| `WG-BM-034` | H1 | PASS | Perfectly correlated road failures: multiplying marginals is wrong by 3.3x |
| `WG-BM-035` | H2 | PASS | Mutually exclusive scenarios: averaging the inputs says both routes are fine |
| `WG-BM-036` | H3 | PASS | Adding two 0.1% scenarios moves expected loss by 0.5 and sup-regret by 8 |
| `WG-BM-037` | I1 | PASS | Ten worlds, ten thousand residents, and an effective sample size of ten |
| `WG-BM-038` | I2 | PASS | Policy A has the better average and a five times worse tail |
| `WG-BM-039` | I3 | PASS | Overwhelmingly significant and practically equivalent at the same time |
| `WG-BM-040` | I4 | PASS | Unpaired comparison across different worlds reverses the true ranking |
| `WG-BM-041` | J1 | PASS | Deep uncertainty, but one action is acceptable in every world |
| `WG-BM-042` | J2 | PASS | No robust action exists, and a timely observation supplies one |
| `WG-BM-043` | J3 | PASS | The same observation, five minutes too late, is worth nothing |
| `WG-BM-044` | K1 | PASS | Same mean, different uncertainty, different correct action |
| `WG-BM-045` | K2 | PASS | Better point error, worse decision: a 16 m forecast beaten by a 46 m one |
| `WG-BM-046` | K3 | PASS | The action switches at p* = 0.2, which the loss matrix fixes and 0.5 does not |
| `WG-BM-047` | K4 | PASS | Asymmetric loss puts the threshold at one per cent |
| `WG-BM-048` | K5 | PASS | A coherent ensemble: admissibility, normalisation and the joint |
| `WG-BM-049` | K6 | PASS | Observation, posterior, decision: the canonical update |
| `WG-BM-050` | K7 | PASS | The posterior moves, the action does not: EVSI is exactly zero |
| `WG-BM-051` | K8 | PASS | Exact expected value of sample information: 22 against an EVPI of 40 |
| `WG-BM-052` | K9 | PASS | Statistical value 22, operational value 0: the sensor reports at minute 12 |
| `WG-BM-053` | K10 | PASS | A weak timely sensor beats a perfect late one, 13 to 0 |
| `WG-BM-054` | K11 | PASS | Two sensors that fail together: independence turns 0.174 into 0.059 |
| `WG-BM-055` | K12 | PASS | One measurement, two records: duplicate evidence must not double confidence |
| `WG-BM-056` | K13 | PASS | Silence is evidence: a missing report raises P(dangerous) from 0.05 to 0.387 |
| `WG-BM-057` | K14 | PASS | No detection leaves P(fire) at 0.073, which is still above the threshold |
| `WG-BM-058` | K15 | PASS | A detection raises P(fire) from 0.02 to 0.22, and 0.22 is not 1 |
| `WG-BM-059` | L1 | PASS | Better average, worse worst case, and no winner declared |
| `WG-BM-060` | L2 | PASS | Ranking reversal between the mean and CVaR, with the objective declared |
| `WG-BM-061` | L3 | PASS | The world is unresolved and the decision is not |
| `WG-BM-062` | L4 | PASS | The world is 97 per cent resolved and the decision turns on 0.21 |
| `WG-BM-063` | L5 | PASS | Poor forecast skill, stable decision |
| `WG-BM-064` | M1 | PASS | A perfectly calibrated binary forecast, with the Murphy decomposition exact |
| `WG-BM-065` | M2 | PASS | Same classifications, probabilities pushed to the extremes, one action changes |
| `WG-BM-066` | M3 | PASS | Perfect aggregate calibration hiding two badly wrong regimes |
