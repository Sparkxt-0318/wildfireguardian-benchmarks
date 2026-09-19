# Roadmap

Ordered by the value of the failure mode closed, not by effort.

## Phase 1 — Foundation (complete)

- [x] benchmark and expected-result schemas
- [x] 43 benchmark scenarios across the A-J families
- [x] authored expected answers with written derivations
- [x] primary reference solvers for nine domains
- [x] independent brute-force solvers and cross-check tests
- [x] automated validators (schema, structure, external results)
- [x] `wg-benchmarks` CLI
- [x] 24 injectable mutations, all detected
- [x] coverage and mutation matrices
- [x] figures for the benchmarks where a picture earns its place
- [x] readiness and known-gap reports

## Phase 2 — Closing the named gaps

Each item is a gap currently recorded in `reports/KNOWN_GAPS.md`.

- [ ] **Probabilistic forecast calibration.** Every information source today
      emits a deterministic signal. Needed: a benchmark where a well-calibrated
      probabilistic forecast beats a better-scoring deterministic one because it
      reports its own uncertainty near a decision boundary (the missing partner
      to WG-BM-029).
- [ ] **Directed connectivity theory.** WG-BM-008 checks directed reachability;
      articulation points and cuts are still computed on the undirected support.
      Needed: strong articulation points and directed minimum cuts.
- [ ] **Two residents, one vehicle.** The first sequencing benchmark: which
      resident is collected first changes who survives. Must stay
      hand-checkable.
- [ ] **Two vehicles, one corridor.** Responder-on-responder interaction, the
      companion to WG-BM-027.
- [ ] **General MNAR correction.** WG-BM-016's dropout-aware estimator is exact
      only because the scenario stipulates the mechanism. Needed: a case with
      *two* dropout causes (hazard and battery) where the naive correction is
      itself wrong.
- [ ] **Partial-traversal semantics.** WG-BM-019 lists four conventions and
      pins one. Needed: benchmarks that pin the other three, so an
      implementation that chose differently has something to conform to.
- [ ] **Terrain at a real resolution boundary.** Slope and aspect under a
      resolution change, where the ridge of WG-BM-003 is at sub-cell scale.

## Phase 3 — Structure and process

- [ ] **Benchmark difficulty audit.** Confirm every `adversarial` benchmark is
      failed by at least one plausible naive implementation, not merely by a
      mutation we wrote.
- [ ] **Convention-variant families.** Where a convention is a choice, ship the
      variant pair rather than one benchmark plus a note.
- [ ] **A second independent solver for the D and I families.** Cross-checking
      currently covers graphs, dispatch, decisions and CVaR; observation and
      statistics have only the primary implementation.
- [ ] **Property-based fuzzing of the solvers** against the brute-force ones on
      randomly generated tiny networks.

## Phase 4 — Integration (deferred, out of scope for now)

Specified in `benchmarks/integration_future/README.md`. Not to be started until
the instruction to keep production repositories disconnected is lifted.

- [ ] end-to-end composition benchmark
- [ ] determinism and CRS-invariance benchmarks
- [ ] archive-versus-realtime observation replay
- [ ] out-of-domain refusal
- [ ] scale benchmark embedding the WG-BM-026 structure in a 5,000-node network
- [ ] pipeline-latency benchmark against a decision deadline
