# WG-BM-029 (G2) — Tiny error, large decision impact

## Scenario

The valley road is unusable if the front is within **1000 m**. In the realised
world the front is at **990 m** — inside the boundary. The forecast puts it at
**1010 m**: an error of **20 metres**, on the wrong side.

| | front near, 990 m (p = 0.5) | front far (p = 0.5) |
|---|---|---|
| `route_valley` | 100 | 1 |
| `route_ridge` | 8 | 8 |

The forecast is taken at face value: "clear" means take the valley road.

## Derivation

The forecast reports "clear" in **both** scenarios, so the forecast-aware policy
takes the valley road in both.

```
expected loss, forecast-aware = 0.5 * 1 + 0.5 * 100 = 50.5
expected loss, baseline       = 8
value of the forecast         = 8 - 50.5 = -42.5
```

In the realised world (`s_near`) the valley road costs **100** while the best
available action costs **8**:

```
realised regret = 100 - 8 = 92
```

For contrast, a forecast that resolved this boundary correctly would have been
worth `EVPI = 8 - 4.5 = 3.5`.

## Read this next to WG-BM-028

| | WG-BM-028 (G1) | WG-BM-029 (G2) |
|---|---|---|
| spatial error | 500 m | **20 m** |
| skill score | 0.60 | **0.98** |
| distance to decision boundary | 2000 m | **10 m** |
| decision value | **+6.3** | **-42.5** |
| realised regret | 0 | **92** |

The forecast with 25 times less error and a far better skill score is the one
that causes the catastrophe. Error magnitude carries no information about
decision impact on its own; what matters is the error *relative to the distance
to the nearest decision boundary*.

## What follows for evaluation practice

* Aggregate skill scores cannot rank forecasts for a decision. A mean absolute
  error averaged over a domain is dominated by the majority of locations where
  no decision boundary is nearby.
* Forecast evaluation should be **stratified by proximity to a decision
  boundary**, and the cases that matter are precisely the rare ones where the
  forecast is nearly right.
* A well-calibrated *probabilistic* forecast would have helped here, not by
  being more accurate, but by reporting that the front position was within its
  own uncertainty of the boundary. A deterministic 1010 m cannot express that;
  "1010 m, sigma 300 m" can. This suite does not yet contain a benchmark for
  calibration under boundary proximity, and that gap is recorded in
  `reports/KNOWN_GAPS.md`.
