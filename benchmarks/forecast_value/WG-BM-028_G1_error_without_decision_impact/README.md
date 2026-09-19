# WG-BM-028 (G1) — Forecast error with no decision impact

## Scenario

A community chooses between the valley road (fast, but unusable if the front
comes within 2 km) and the ridge road (slow, always usable).

| | front stays far (p = 0.9) | front comes near (p = 0.1) |
|---|---|---|
| `route_valley` | 1 | 100 |
| `route_ridge` | 8 | 8 |

Two forecasts are available before the 20-minute decision deadline:

| Forecast | Spatial error | Skill score |
|---|---|---|
| `forecast_exact` | 0 m | 1.00 |
| `forecast_displaced` | 500 m | 0.60 |

The decision boundary is at **2 km**. Both forecasts put the front on the
correct side of it in both scenarios.

## Derivation

Because both forecasts classify both scenarios correctly, both produce the same
actions: valley on "far" (1 beats 8), ridge on "near" (8 beats 100).

```
expected loss, either forecast policy = 0.9 * 1 + 0.1 * 8 = 1.7
expected loss, baseline (always ridge) = 8
value of either forecast                = 8 - 1.7 = 6.3
clairvoyant expected loss               = 1.7
EVPI                                    = 8 - 1.7 = 6.3
```

Both forecasts capture the **entire** value of perfect information. Their
decision value is identical to the last decimal, while their skill scores differ
by 40 points.

## The lesson

Forecast accuracy is a property of the forecast. Decision value is a property of
the *pair* (forecast, decision). A 500 m error matters enormously when the
decision boundary is 500 m away (see WG-BM-029, where a 20 m error costs 92) and
not at all when the boundary is 2 km away, as here.

The practical consequence: **a forecast improvement programme cannot be
evaluated on forecast metrics alone.** Reducing mean position error from 500 m
to 0 m is a genuine scientific achievement and, in this decision, is worth
nothing. Resources spent on it were resources not spent on the decisions where
the boundary is tight.

## What this benchmark does not claim

It does **not** detect the `skill_implies_value` mutation. Ranking by skill here
recommends `forecast_aware_exact` over `forecast_aware_displaced`, and since the
two are worth exactly the same, that recommendation is harmless: the conflation
is visible in the reasoning and absent from the outcome. Benchmarks whose
declared answer would not change under a bug must not claim to catch it, so the
`mutations_expected_to_fail` list here is empty. WG-BM-031 and WG-BM-033 are
where the conflation changes what actually happens.

## Expected

| Quantity | Value |
|---|---|
| value of the exact forecast | 6.3 |
| value of the 500 m-displaced forecast | **6.3** |
| EVPI | 6.3 |
| skill ranking agrees with value ranking | `false` |
