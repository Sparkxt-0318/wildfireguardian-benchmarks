# WG-BM-037 (I1) — Pseudoreplication

## Scenario

Ten simulated worlds, 1000 residents each, 10000 resident-level outcomes in
total. **Within a world, every resident experiences the same outcome**, because
a single weather draw determines it. Between worlds the outcomes differ:

```
10, 14, 18, 22, 26, 30, 34, 38, 42, 46      (mean 28)
```

## Derivation

**World-level.** Sum of squared deviations is 1320 over 10 worlds:

```
s_world = sqrt(1320 / 9) = 12.1106
SE_world = 12.1106 / sqrt(10) = 3.829708
```

**Resident-level.** Each world's value appears 1000 times, so the pooled sum of
squared deviations is `1000 * 1320 = 1320000` over 10000 values:

```
s_resident = sqrt(1320000 / 9999) = 11.48970
SE_resident = 11.48970 / sqrt(10000) = 0.114897
```

**Ratio**

```
SE_world / SE_resident = 33.3317
```

The resident-level confidence interval is **33 times too narrow**.

## Why the residents carry no information

The variance of the mean of `n` observations with pairwise correlation `rho` is

```
Var = sigma^2 / n * (1 + (n - 1) rho)
```

With `rho = 1` within a world this collapses to `sigma^2`, independent of how
many residents the world contains: simulating 10000 residents per world instead
of 1000 would not narrow the interval by one part in a thousand. The effective
sample size is the number of **independent draws of the thing that varies**,
which here is the world, and that number is **10**.

Real simulations sit between `rho = 0` and `rho = 1`, but they are much closer
to 1 than intuition suggests, because the dominant sources of variation —
ignition location, wind, fuel moisture, time of day — are shared by every
resident in the run. The failure is one-sided: pseudoreplication always
overstates confidence, never understates it.

## What a system must do

Resample at the level at which the randomisation actually happened: the world,
the simulation run, the ensemble member. Resident-level summaries may be the
*quantity of interest*; they are never the *unit of resampling*. Where residents
do carry partially independent information, a hierarchical model or a
cluster bootstrap is the correct tool, and the cluster is still the world.

The `resident_level_bootstrap` mutation resamples residents and reports that
interval as the answer; this benchmark is its declared detector.

## What is checked exactly and what is checked loosely

The analytic standard errors and their ratio are exact and are checked to 1e-9.
The bootstrap confidence intervals are Monte Carlo estimates from 200 resamples
of 10 worlds — themselves quite variable — and are checked against the analytic
values within a declared band (±5 on the world width, ±0.15 on the resident
width, ±12 on the ratio). The exactness of this benchmark is recorded as
`SEEDED_STOCHASTIC_VALIDATION` for that reason.

## Expected

| Quantity | Value |
|---|---|
| analytic world standard error | `3.829708` |
| analytic resident standard error | `0.114897` |
| width ratio | `33.3317` |
| effective sample size | 10 |
| nominal sample size | 10000 |
