# WG-BM-025 (F4) — Alternate destination

## Scenario

```
                          /--5 min, open [0, 18]--> refuge_close   (2 km)
base --5 min--> resident -
                          \--20 min, open [0, 100]-> shelter_far  (15 km)
```

Pickup 5 minutes. The resident's location is untenable after minute 25.

## Derivation

Pickup always finishes at `d + 10`.

| Destination | Egress constraint | Bound on `d` | Arrival |
|---|---|---|---|
| `refuge_close` | `[d+10, d+15]` inside `[0, 18]` | `d <= 3` | `d + 15` |
| `shelter_far` | `[d+10, d+30]` inside `[0, 100]` | `d <= 70` | `d + 30` |
| (either) | pickup by minute 25: `d + 10 <= 25` | `d <= 15` | — |

So the mission is feasible exactly on `d in [0, 15]`, and the destination
changes inside that window:

| Dispatch | Refuge | Shelter | Chosen | Arrival |
|---|---|---|---|---|
| 0 | feasible | feasible | **refuge_close** (arrives 15 vs 30) | 15 |
| 6 | infeasible | feasible | **shelter_far** | 36 |
| 15 | infeasible | feasible | **shelter_far** | 45 |
| 20 | — | — | none: pickup would end at 30 > 25 | — |

## What this is about

Destination assignment is often static: each address is pre-assigned to its
designated refuge during planning, and the runtime system routes there. That
assignment is correct here for the first three minutes and wrong afterwards.
From minute 4 the pre-assigned refuge is a trap — its approach is occupied by
the hazard before the vehicle can clear it — while a perfectly good shelter
exists 15 km away.

Note also **which constraint binds at each end** of the window. Early failures
are road failures; the last failure, at `d = 20`, is a *resident* failure: the
crew could still drive the route, but the person they are collecting cannot
survive at the pickup point long enough to be collected. Reporting "no feasible
route" there would be diagnostically wrong, and the result document distinguishes
the two with `failure_stage`.

## Expected

| Quantity | Value |
|---|---|
| feasible dispatch window | `[0, 15]` |
| destination at `d = 0` | `refuge_close`, arrive 15 |
| destination at `d = 6` | `shelter_far`, arrive 36 |
| failure stage at `d = 20` | `pickup` |
