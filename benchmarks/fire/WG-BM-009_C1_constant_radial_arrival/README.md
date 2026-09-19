# WG-BM-009 (C1) — Constant radial arrival

## Scenario

A single ignition at the origin at `t = 0`, spreading isotropically at
`r = 10 m/min`. Arrival time is

```
T(x) = |x - x0| / r
```

## Derivation

| Point | Coordinates | Distance | Arrival |
|---|---|---|---|
| `p_origin` | (0, 0) | 0 m | 0 min |
| `p_east` | (100, 0) | 100 m | 10 min |
| `p_north` | (0, 100) | 100 m | 10 min |
| `p_ne` | (100, 100) | `100 sqrt(2)` = 141.4214 m | `14.1421356237` min |
| `p_far` | (300, 0) | 300 m | 30 min |

`p_east` and `p_north` are equidistant and therefore arrive **simultaneously**.
The reported ordering breaks the tie by identifier so that the expected sequence
is deterministic rather than dependent on dictionary iteration order.

## What this catches

* A factor-of-two or unit error in the rate (minutes vs seconds, metres vs feet)
  shows up immediately as a scaled arrival field.
* An implementation whose grid discretisation makes the diagonal arrive at
  `200/10 = 20` min instead of `14.14` min — the classic 4-connected raster
  spread artefact, where fire can only travel along rows and columns. That error
  is a 41% overestimate of diagonal arrival time and it biases every
  diagonally-oriented escape route optimistically.
* An ordering bug in which strictly later points are reported as reached first.

## What this deliberately does not test

Nothing about realistic fire behaviour. There is no wind, no fuel, no terrain,
no ignition delay. A model that passes this has demonstrated that its arrival
field is a metric, and nothing else. Wind enters in WG-BM-010, fuel in
WG-BM-011, multiple sources in WG-BM-012.
