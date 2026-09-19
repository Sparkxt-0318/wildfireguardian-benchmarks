# WG-BM-033 (G6) — Forecast harm

## Scenario

Five equally likely scenarios. Four are benign; `s5` is extreme.

| | s1 | s2 | s3 | s4 | s5 |
|---|---|---|---|---|---|
| `evacuate_early` | 10 | 10 | 10 | 10 | 10 |
| `wait_and_see` | 0 | 0 | 0 | 0 | **200** |

The forecast calls all five scenarios benign. It is therefore **right 4 times
out of 5** — a classification accuracy of 0.8 — and wrong exactly once.

## Derivation

Acting on the forecast means waiting in every scenario:

```
expected loss, forecast-aware = 0.8 * 0 + 0.2 * 200 = 40
expected loss, robust baseline (always evacuate early) = 10
Delta J = 10 - 40 = -30          <- the forecast is harmful
```

In the realised world (`s5`):

```
realised loss, forecast-aware = 200
realised loss, baseline       = 10
realised regret               = 190
```

And yet information *would* help:

```
clairvoyant expected loss = 0.8 * 0 + 0.2 * 10 = 2
EVPI                      = 10 - 2 = 8
```

A forecast that caught the extreme scenario would be worth **+8**. This one is
worth **-30**.

## The mechanism: errors correlated with consequences

The forecast's single error is not randomly placed. It falls in the only
scenario where the choice of action matters. This is the normal situation rather
than a contrived one, for a structural reason: the scenarios a model finds hard
to predict — rapid escalation, unexpected wind shift, plume-driven behaviour —
are the same scenarios that produce extreme losses. Model error and consequence
are positively correlated almost by construction.

The consequence for evaluation is severe: **aggregate accuracy is nearly
uninformative about decision value when errors are consequence-correlated.** A
forecast can be made arbitrarily accurate on the benign majority without
improving, or while degrading, its decision value.

## What a system should do with this

Three defensible responses, none of which is "use the forecast because it is
80% accurate":

1. **Evaluate on a loss-weighted basis.** Score the forecast by the loss its
   errors induce, not by how often it is right.
2. **Use the forecast asymmetrically.** Let it trigger escalation but never
   stand down a precaution — a one-sided use is robust to exactly this error
   pattern.
3. **Report the tail explicitly.** A probabilistic forecast saying "benign, but
   5% chance of extreme" supports the right action; a deterministic "benign"
   cannot.

The `skill_implies_value` mutation recommends the forecast-aware policy because
its skill score is the higher one, and this benchmark is among its detectors.

## Expected

| Quantity | Value |
|---|---|
| forecast classification accuracy | 0.8 |
| Delta J (value of the forecast) | **-30** |
| realised regret in `s5` | 190 |
| EVPI | 8 |
| recommended policy | `robust_baseline` |
