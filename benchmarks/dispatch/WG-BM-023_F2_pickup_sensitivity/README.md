# WG-BM-023 (F2) — Pickup sensitivity

## Scenario

The WG-BM-022 network, with the on-scene pickup duration swept over
`p in {2, 5, 10, 15}` minutes.

## Derivation

```
arrive at refuge = d + 5 + p + 5 = d + p + 10
egress closes at 20   ->   d + p + 10 <= 20   ->   d <= 10 - p
```

The resident tenability constraint is `d + p <= 15`, which is slacker than the
egress constraint for every `p` in the sweep, so it never binds.

| Pickup `p` | Latest dispatch `10 - p` | Feasible at all? |
|---|---|---|
| 2 min | **8 min** | yes |
| 5 min | **5 min** | yes |
| 10 min | **0 min** | only an instantaneous dispatch |
| 15 min | `-5 min` | **no** |

The slope is exactly `-1`: every extra minute spent on scene costs one minute of
dispatch latitude. At `p = 10` the feasible set collapses to the single point
`{0}`. At `p = 15` it is empty — the mission cannot be completed however early
the crew leaves, and the correct answer is "impossible", not "dispatch now".

## Why the sweep, and not just one row

A single row cannot distinguish a model that handles pickup correctly from one
that ignores it, because both produce *some* number and the number looks
reasonable. The sweep pins the **derivative**. Under the
`ignore_pickup_duration` mutation every row collapses to the same answer,
`d <= 10`, and the slope becomes zero. A flat sensitivity to on-scene time is
the signature of the bug, and it is visible even when the absolute values happen
to look plausible.

This matters operationally because the pickup duration is the term that varies
most between residents: a mobile adult is two minutes, a bed-bound resident
needing two crew and a stretcher is twenty. A system whose dispatch advice does
not move with that input is not modelling assisted evacuation at all.

## The feasibility cliff

The transition from `p = 10` (feasible only at `d = 0`) to `p = 15` (never
feasible) is the operationally important one. It is the point at which the right
answer stops being "go now" and becomes "this resident cannot be reached by this
route from this base — find another plan". A system that always returns a
dispatch time, however tight, cannot express that.
