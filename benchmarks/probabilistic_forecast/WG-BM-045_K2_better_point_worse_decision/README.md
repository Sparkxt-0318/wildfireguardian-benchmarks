# WG-BM-045 (K2) — Better point error, worse decision distribution

## Scenario

The WG-BM-044 decision (`use_road` 0/100, `long_way` 8/8, threshold 800 m,
`p* = 0.08`) with a **declared true world**:

```
front at 900 m   with probability 0.97      (road clear)
front at 700 m   with probability 0.03      (road unusable)

true mean = 0.97 * 900 + 0.03 * 700 = 894 m
true P(hazard) = 0.03
```

Two forecasts:

| Forecast | Distribution | Location error vs 894 m | `P(front <= 800)` |
|---|---|---|---|
| A | `N(910, 400^2)` | **16 m** | `0.391658` |
| B | `N(940, 50^2)` | 46 m | `0.002555` |

## Derivation

Best achievable: `0.03 < 0.08`, so the road should be used, at an expected loss
of `0.03 * 100 = 3`.

```
Forecast A:  P = Phi((800-910)/400) = Phi(-0.275) = 0.3916581192  >  0.08  ->  long_way
             expected loss under the truth = 8      regret = 5

Forecast B:  P = Phi((800-940)/50)  = Phi(-2.8)   = 0.0025551303  <  0.08  ->  use_road
             expected loss under the truth = 3      regret = 0
```

**Forecast A has one third of B's location error and five units more regret.**

## Why this is not a trick

A's mean is almost exactly right and its distribution is almost uninformative:
with `sd = 400` it assigns 39% probability to a hazard that occurs 3% of the
time. B's mean is 46 m too far out and its distribution is nearly right about
the thing the decision consumes — the tail mass below 800 m.

A threshold decision reads a **tail probability**, and a tail probability is
determined by the mean *and* the spread together. Mean absolute error, RMSE and
displacement scores read only the first of those, so they can rank two forecasts
in the opposite order to any decision that depends on the second.

Read next to WG-BM-029, which makes the deterministic version of the same point:
there a 20 m error cost 92 while a 500 m error cost nothing, because what
mattered was the distance to the decision boundary. Here what matters is how much
probability mass the forecast puts on the wrong side of it.

## Expected

| Quantity | Forecast A | Forecast B |
|---|---|---|
| location error | **16 m** | 46 m |
| `P(front <= 800)` | 0.3917 | 0.0026 |
| action | `long_way` | `use_road` |
| expected loss under the truth | 8 | **3** |
| regret | 5 | **0** |
