# Roadmap

Ordered by the value of the failure mode closed, not by effort.

## Phase 1 — Foundation (complete)

- [x] benchmark and expected-result schemas
- [x] 43 benchmark scenarios across the A-J families (66 after Phase 2)
- [x] authored expected answers with written derivations
- [x] primary reference solvers for nine domains
- [x] independent brute-force solvers and cross-check tests
- [x] automated validators (schema, structure, external results)
- [x] `wg-benchmarks` CLI
- [x] 24 injectable mutations, all detected
- [x] coverage and mutation matrices
- [x] figures for the benchmarks where a picture earns its place
- [x] readiness and known-gap reports

## Phase 2 — Stochastic information, forecasting and risk (complete)

- [x] **Family K — probabilistic forecasts** (WG-BM-044..058). Predictive
      distributions against a threshold; loss-derived decision thresholds;
      coherent ensembles with admissibility; the posterior-to-decision chain;
      exact EVSI; information with no decision value; timeliness against
      quality; correlated and duplicate evidence; informative missingness; false
      negatives and false positives.
- [x] **Family L — decision risk** (WG-BM-059..063). Expected loss against
      worst case and CVaR with a declared objective; state resolution and
      decision resolution as independent axes; fragile recommendations.
- [x] **Family M — calibration** (WG-BM-064..066). Reliability and the Murphy
      decomposition; overconfidence with a decision cost; aggregate calibration
      masking conditional failure.
- [x] 15 further mutations, all detected
- [x] independent Bayesian, EVSI, quadrature and Brier cross-checks
- [x] `reports/INTEGRATION_COVERAGE.md`, `reports/BENCHMARK_SELF_AUDIT.md`,
      `reports/V0_1_SCIENTIFIC_AUDIT.md`
- [x] frozen at `v0.1.0`

## Phase 3 — Not scheduled (the suite is frozen)

These are the open gaps from `reports/KNOWN_GAPS.md`. **None is scheduled.**
Under WG-D-018 a benchmark is added only when a real project failure exposes the
need, so this list is a record of what is known to be missing, not a plan.

- Continuous and sequential inference (G-1) — the largest gap
- Multi-resident dispatch sequencing (G-2)
- Estimating the likelihoods rather than being given them (G-3)
- Alert fatigue and dynamic credibility (G-4)
- Proper scoring rules beyond Brier (G-5)
- Where the loss matrix comes from (G-6)
- Directed-graph connectivity theory (G-7)
- The three traversal conventions WG-BM-019 rejects (G-8)
- Responder-on-responder interaction (G-9)
- Terrain across a resolution change (G-10)
- A second independent solver for the D and I families (G-11)
- Ensemble provenance reporting (G-12)
- Property-based fuzzing; a measured rather than asserted difficulty audit

## Phase 4 — Integration (the next work on this repository)

Requirements are specified per repository in `reports/INTEGRATION_COVERAGE.md`
and the mechanics in `benchmarks/integration_future/README.md`. Not to be
started until the instruction to keep production repositories disconnected is
lifted.

- [ ] the eight-benchmark **OSSE gate** before forecast-value experiments scale
      beyond the minimum viable experiment

- [ ] end-to-end composition benchmark
- [ ] determinism and CRS-invariance benchmarks
- [ ] archive-versus-realtime observation replay
- [ ] out-of-domain refusal
- [ ] scale benchmark embedding the WG-BM-026 structure in a 5,000-node network
- [ ] pipeline-latency benchmark against a decision deadline
