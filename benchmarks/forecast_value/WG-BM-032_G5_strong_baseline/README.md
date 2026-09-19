# WG-BM-032 (G5) — Strong baseline

## Scenario

Evacuate (cost 5 either way) or stay (0 if the fire misses, 100 if it hits),
prior 50/50, deadline minute 20.

Two sources of information:

| Source | Available | Skill | What it says |
|---|---|---|---|
| `trigger_3km` — a fire-within-3-km trip wire | minute 0 | 0.50 | tripped / clear |
| `forecast_model` — a coupled fire-weather model | minute 5 | 0.95 | hit / miss |

Both separate the same two scenarios.

## Derivation

Both policies evacuate on the threatening signal (5 beats 100) and stay on the
benign one (0 beats 5):

```
expected loss, trigger policy  = 0.5 * 5 + 0.5 * 0 = 2.5
expected loss, forecast policy = 0.5 * 5 + 0.5 * 0 = 2.5
added value of the forecast    = 0
```

Measured against the best *fixed* action (always evacuate, expected loss 5):

```
EVPI = 5 - 2.5 = 2.5
```

So information is worth 2.5 in this problem, and **the trip wire has already
collected all of it**.

## Why a zero-value benchmark belongs in the suite

Every other benchmark in the G family shows a forecast doing something — helping
(G1, G4), hurting (G2, G6), or arriving too late to matter (G3). Without a case
whose correct answer is a flat zero, a benchmark suite silently rewards
complexity: any system that reports a positive value for its most sophisticated
component passes everything, and there is nothing to lose by overclaiming.

This case is also the common one in practice. Operational wildfire decisions are
frequently governed by conservative trigger points — distance to the fire, a red
flag warning, a pre-agreed evacuation zone — that were designed by people who
understood the problem. A new forecasting system has to beat *that*, not beat a
straw-man policy of doing nothing.

The comparison that matters is therefore always **against the best available
simple policy**, not against the absence of a policy. A system reporting the
value of its forecast relative to "no information" will report 2.5 here, and 2.5
is not what the forecast is worth.

## What is deliberately excluded

The cost of building, running and maintaining the forecast. Once the added
decision value is 0, any non-zero cost makes the net value negative, but this
suite does not model programme costs and so does not assert that.

## Expected

| Quantity | Value |
|---|---|
| added value of the forecast over the trigger | **0.0** |
| identical actions to the baseline | `true` |
| EVPI against the best fixed action | 2.5 |
| realisable value of information beyond the baseline | 0.0 |
