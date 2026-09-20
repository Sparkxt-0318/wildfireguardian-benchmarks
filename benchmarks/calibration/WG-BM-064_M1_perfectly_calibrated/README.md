# WG-BM-064 (M1) — Perfectly calibrated binary forecast

## Scenario

800 forecast-outcome pairs in five probability groups.

| forecast `p` | cases | events | observed |
|---|---|---|---|
| 0.0 | 100 | 0 | 0.0 |
| 0.2 | 200 | 40 | 0.2 |
| 0.5 | 100 | 50 | 0.5 |
| 0.8 | 300 | 240 | 0.8 |
| 1.0 | 100 | 100 | 1.0 |

## Derivation

Every observed frequency equals its forecast probability, so

```
expected calibration error = 0        reliability = 0
```

```
base rate    = 430 / 800 = 0.5375
uncertainty  = 0.5375 * 0.4625                      = 0.24859375
resolution   = sum w_i (o_i - base)^2               = 0.11734375
Brier        = reliability - resolution + uncertainty = 0.13125
```

Computing the Brier score directly, group by group, gives the same
0.13125 — the decomposition residual is **zero**.

## The decision side

With `proceed` costing 90 on an event and `divert` costing 10 otherwise, the
threshold is `p* = 0.1`. In every group the action taken from the forecast
probability matches the action taken from the observed frequency, so the excess
expected loss is **0**.

That is what calibration buys, and it is the only reason this suite measures it:
a calibrated probability can be fed straight into a loss matrix and the
resulting action is the one the data support. An uncalibrated one cannot, which
is WG-BM-065.

## Why a positive control

Reliability, resolution and uncertainty are easy to compute and easy to compute
slightly wrong — a population variance where a weighted one belongs, a base rate
taken over groups rather than cases, a decomposition with the resolution sign
flipped. This benchmark pins all three terms, the identity that links them, and
the case where the answer is the clean zero.

## Expected

| Quantity | Value |
|---|---|
| expected calibration error | **0** |
| reliability | 0 |
| resolution | 0.11734375 |
| uncertainty | 0.24859375 |
| Brier score | 0.13125 |
| decomposition residual | 0 |
| excess expected loss from miscalibration | 0 |
