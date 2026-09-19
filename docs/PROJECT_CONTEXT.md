# Project context

## What this repository is

`wildfireguardian-benchmarks` is the canonical benchmark, adversarial-test and
hand-solvable reference-case suite for the WildfireGuardian research programme.
It is a **unit-test laboratory for wildfire decision science**: a collection of
scenarios small enough that the scientifically correct answer is known by
derivation, together with the machinery to check an implementation against
them.

It contains no fire model, no router, no optimiser intended for use. Everything
executable here exists to produce trustworthy answers on tiny cases.

## What this repository is not

* It is **not** a production component. Nothing here is on any operational path.
* It is **not** a validation of WildfireGuardian. It is a set of tests that
  WildfireGuardian components must pass before their outputs on realistic
  problems mean anything.
* It is **not** a physics library. The fire models here are closed forms chosen
  for checkability, not for realism.

## Independence from production repositories

This repository is deliberately independent of any production WildfireGuardian
codebase, and that independence is a scientific requirement rather than a
packaging preference:

1. **No shared code.** If the suite imported the implementation's geometry,
   graph or hazard code, a bug in that code would be inherited by the expected
   answers and would become untestable by construction.
2. **No calibration against implementation output.** Expected values are
   derived from the scenario definitions. A benchmark whose expected value was
   read off a production run does not test that run; it records it.
3. **No dependency in either direction.** A production repository consumes this
   one only through `wg-benchmarks validate-results`, which reads a directory of
   result documents and never imports the implementation.

The integration path is one-way and file-based:

```
   production implementation  --writes-->  results/WG-BM-0NN.yaml
                                               |
                       wg-benchmarks validate-results results/
                                               |
                                        pass / fail per benchmark
```

## Where the benchmarks came from

Each benchmark family targets a scientific failure mode that the programme has
identified as consequential — mid-edge hazard, future information leakage,
non-monotone dispatch feasibility, correlated road failures, pseudoreplication,
the conflation of forecast skill with decision value. The catalogue of those
modes is `docs/FAILURE_MODES.md`; the mapping from modes to benchmarks is
`reports/COVERAGE.md`.

## Intended readers

* Anyone building a WildfireGuardian component, before they trust its output on
  a realistic domain.
* Reviewers who need to know what a claim of "validated" covers.
* Future contributors adding a benchmark for a newly discovered failure mode —
  see `AGENTS.md` for how.
