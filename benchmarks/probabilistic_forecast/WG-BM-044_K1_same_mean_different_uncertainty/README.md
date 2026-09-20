# WG-BM-044 (K1) — Same mean, different uncertainty

## Scenario

A convoy may take the valley road (fast) or the long way round. The valley road
is unusable if the fire front is within **800 m** when the convoy is on it.

| | front inside 800 m | front clear |
|---|---|---|
| `use_road` | 100 | 0 |
| `long_way` | 8 | 8 |

Two forecasts of the front distance, **with the same mean**:

| Forecast | Distribution | Point estimate |
|---|---|---|
| A | `N(1000, 50^2)` | 1000 m |
| B | `N(1000, 300^2)` | 1000 m |

## Derivation

**The threshold comes from the loss matrix, not from convention.** With `p` the
probability that the front is inside 800 m:

```
E[use_road] = 100p        E[long_way] = 8
indifference: 100 p* = 8  ->  p* = 0.08
```

**Forecast A.**

```
p_A = Phi((800 - 1000) / 50) = Phi(-4) = 3.1671241833e-05
```

`p_A << 0.08` → **use the road** (expected loss 0.003167 against 8).

**Forecast B.**

```
p_B = Phi((800 - 1000) / 300) = Phi(-2/3) = 0.2524925375
```

`p_B > 0.08` → **take the long way** (expected loss 25.2493 against 8).

## The point

Both forecasts say **1000 m**. A pipeline that carries the point estimate and
discards the spread produces one number, `1000 > 800`, and therefore one action,
in both cases — and that action is wrong under forecast B by a factor of three
in expected loss.

The spread is not a caveat attached to the forecast. Under a threshold decision
it **is** the forecast: the decision consumes `P(X <= 800)`, and the mean enters
only through that probability. Two forecasts with the same mean can sit on
opposite sides of the decision, which is what makes "the forecast said 1000 m" an
incomplete statement of what was predicted.

The `ignore_forecast_variance` mutation collapses each distribution to its mean;
this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| decision threshold `p*` | **0.08** |
| `P(front <= 800)` under A | `3.167124e-05` |
| `P(front <= 800)` under B | `0.252493` |
| action under A / B | `use_road` / **`long_way`** |
| action from the point estimate, A and B | `use_road` / `use_road` |
