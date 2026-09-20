# WG-BM-066 (M3) — Calibrated globally, miscalibrated conditionally

## Scenario

The same forecast probability, **0.5**, is issued in two wind regimes.

| stratum | cases | stated `p` | events | observed |
|---|---|---|---|---|
| calm | 400 | 0.5 | 80 | **0.2** |
| gusty | 400 | 0.5 | 320 | **0.8** |

## Derivation

**Pooled.** 800 cases, one forecast probability of 0.5, 400 events → observed
0.5.

```
aggregate ECE = 0        aggregate reliability = 0        "perfectly calibrated"
```

**Stratified.** Wrong by 0.3 in each regime, in opposite directions:

```
stratified ECE         = 0.5 * 0.3 + 0.5 * 0.3   = 0.3
stratified reliability = 0.5 * 0.09 + 0.5 * 0.09 = 0.09
```

The two errors **cancel exactly**, which is the only reason the aggregate is
clean. Nothing about the pooled number is wrong; it is answering a question
nobody asked.

## The decision consequence

`p* = 30 / (30 + 70) = 0.3`. The stated 0.5 is above it, so the forecast says
`divert` in both regimes.

| stratum | true rate | forecast action | correct action | cost per case |
|---|---|---|---|---|
| gusty | 0.8 | `divert` | `divert` | 0 |
| **calm** | 0.2 | `divert` | **`proceed`** | `24 − 14 = 10` |

```
total excess = 400 * 10 = 4000        5 per case over the whole sample
```

Every calm-weather decision is wrong, and the reliability diagram for the
aggregate sample is a perfect diagonal.

## Why cancellation is the normal case, not a contrivance

Aggregate calibration is a *weighted average of signed errors*, and a forecast
trained or tuned on a pooled sample is being optimised for exactly that average.
It is therefore actively driven towards cancellation: systematic over-prediction
in one regime is the cheapest way to pay for systematic under-prediction in
another. The more regimes a forecast is used across, the more room it has to
balance.

The consequence is that **an aggregate reliability of zero is not evidence of
calibration in any regime the forecast is actually used in.** It is evidence
only about the mixture, and the mixture is not a situation anybody is ever in.

## What a system must do

Report calibration **conditional on the regimes the decision cares about** —
weather regime, fuel state, time of day, distance to the operating threshold —
and treat a clean aggregate with dirty strata as a failure, not a pass. The
result document carries `aggregate_hides_stratum_failure` so that the condition
is named rather than left for a reader to notice.

The `aggregate_calibration_only` mutation reports the aggregate figure in the
conditional slot; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| aggregate ECE | **0.0** |
| stratified ECE | **0.3** |
| aggregate reliability | 0.0 |
| stratified reliability | 0.09 |
| groups with a different action | `calm\|p=0.5` |
| excess expected loss | 4000 (5 per case) |
