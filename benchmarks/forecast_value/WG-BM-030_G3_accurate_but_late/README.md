# WG-BM-030 (G3) — Accurate but late

## Scenario

Evacuate now at a fixed cost of 10, or shelter in place: free if the fire misses,
catastrophic (100) if it hits. Prior 50/50.

An **excellent** forecast exists — skill score 0.98, spatial error 10 m — and it
is issued at **minute 30**. The decision must be taken by **minute 20**: after
that there is no longer time to move people.

## Derivation

The forecast cannot influence the action. A policy that waits for it has, at the
deadline, not started an evacuation — which is the shelter-in-place outcome.

```
expected loss, baseline trigger (always evacuate) = 10
expected loss, wait-for-forecast                  = 0.5 * 100 + 0.5 * 0 = 50
value of waiting for the forecast                 = 10 - 50 = -40
```

In the realised world the fire hits:

```
realised loss, baseline          = 10
realised loss, wait-for-forecast = 100
realised regret                  = 90
```

And yet the information is genuinely valuable in the abstract:

```
clairvoyant expected loss = 0.5 * 10 + 0.5 * 0 = 5
best fixed action         = evacuate, expected loss 10
EVPI                      = 5
realisable value          = 0      <- no timely policy can use it
```

## Four numbers that must be reported separately

| Quantity | Value | Meaning |
|---|---|---|
| skill score | 0.98 | the forecast is excellent |
| EVPI | 5 | knowing the outcome would be worth 5 |
| realisable value of information | **0** | nothing can be extracted by the deadline |
| realised value of waiting | **-90** | waiting for it was actively harmful |

A system that reports only the first number will conclude that the forecasting
programme is succeeding. A system that reports only EVPI will conclude that more
information is worth buying. Only the third and fourth numbers describe what
happens to the people in the scenario.

## Why this is the conceptually critical case

Forecast lead time is usually treated as a performance attribute — nice to have,
traded against accuracy. This benchmark makes it a **feasibility constraint**. A
forecast issued after the last useful decision time has exactly zero realisable
value regardless of its accuracy, and a decision process that is built around
waiting for it is strictly worse than one that acts on the prior.

The corollary is the design rule the F family keeps running into: the quantity
to optimise is not forecast accuracy at a fixed lead time, but accuracy
*conditional on being available before the decision deadline*. Those two
objectives can point in opposite directions, and WG-BM-031 shows them doing so.

The `forecast_always_trusted` mutation removes the timeliness check; the late
forecast is then applied to the decision, the value of waiting becomes +5, and
the benchmark fails. It is this benchmark's declared detector.
