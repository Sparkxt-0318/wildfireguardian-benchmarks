# WG-BM-065 (M2) — Overconfident forecast

## Scenario

**The same 800 cases and the same outcomes as WG-BM-064.** Only the stated
probabilities move, towards the extremes:

| stated `p` | cases | observed | error |
|---|---|---|---|
| 0.0 | 100 | 0.0 | 0 |
| **0.05** | 200 | **0.2** | −0.15 |
| 0.5 | 100 | 0.5 | 0 |
| **0.95** | 300 | **0.8** | +0.15 |
| 1.0 | 100 | 1.0 | 0 |

## Derivation

Resolution and uncertainty depend on the **observed** frequencies alone, so both
are unchanged:

```
resolution  = 0.11734375        uncertainty = 0.24859375
ECE         = 0.25 * 0.15 + 0.375 * 0.15 = 0.09375
reliability = 0.25 * 0.0225 + 0.375 * 0.0225 = 0.014062499999999992
Brier       = 0.13125 + 0.014062499999999992 = 0.1453125
```

**The entire Brier penalty is the reliability term** — a clean separation that
only holds because the two forecasts rank the cases identically.

## The decision consequence

At `p* = 0.1`, **one group out of five** changes action:

| group | stated | observed | action from forecast | action from data | excess per case |
|---|---|---|---|---|---|
| `p=0.05` | 0.05 | 0.20 | `proceed` | **`divert`** | `18 − 8 = 10` |
| `p=0.95` | 0.95 | 0.80 | `divert` | `divert` | 0 |

```
total excess = 200 * 10 = 2000        per case over the whole sample = 2.5
```

Both miscalibrated groups are wrong by exactly 0.15. One costs 2000 and the
other costs nothing, because **only one of them straddles the threshold**.

## What this says about calibration metrics

A calibration score is a summary of all the errors; a decision cost is a summary
of the errors that cross a boundary. They are different sums, and the second is
the one that matters. Here they disagree about which group is the problem: the
0.95 group contributes 60% of the reliability term and 0% of the loss.

The practical form of this: report calibration **stratified by distance to the
operating threshold**, not only in aggregate — the same discipline WG-BM-029
arrives at from the deterministic side.

## Expected

| Quantity | WG-BM-064 | here |
|---|---|---|
| ECE | 0 | **0.09375** |
| reliability | 0 | **0.014062499999999992** |
| resolution | 0.11734375 | 0.11734375 |
| Brier | 0.13125 | **0.1453125** |
| groups with a different action | none | **`p=0.05`** |
| excess expected loss | 0 | **2000** (2.5 per case) |
