# WG-BM-022 (F1) — Basic round trip

## Scenario

```
base --5 min--> resident --[pickup 5 min]--> --5 min--> refuge
```

* ingress road open on `[0, 30]`
* egress road open on `[0, 20]` — the hazard closes it at minute 20
* the resident's location becomes untenable at minute 25
* waiting is not permitted; traversals obey WG-SEM-1 (interval safety)

## Derivation

Let `d` be the dispatch time.

```
arrive at resident   = d + 5
pickup complete      = d + 10
depart for refuge    = d + 10
arrive at refuge     = d + 15
```

Three constraints:

| # | Constraint | Algebra | Bound |
|---|---|---|---|
| 1 | ingress traversal inside `[0, 30]` | `d + 5 <= 30` | `d <= 25` |
| 2 | pickup finishes before the resident's location is untenable | `d + 10 <= 25` | `d <= 15` |
| 3 | egress traversal inside `[0, 20]` | `d + 15 <= 20` | **`d <= 5`** |

The binding constraint is the egress closure.

```
latest feasible dispatch = 5 min
feasible set             = [0, 5]
```

| Dispatch | Arrive resident | Pickup done | Arrive refuge | Outcome |
|---|---|---|---|---|
| 0 | 5 | 10 | 15 | success, 5 min slack |
| 5 | 10 | 15 | 20 | success, **zero slack** |
| 6 | 11 | 16 | 21 | fails at egress |

## What this catches

**Ignoring the pickup.** Drop the 5-minute pickup and the arithmetic becomes
`d + 10 <= 20`, giving a latest dispatch of 10 minutes — twice the truth. A
dispatcher acting on that number sends the crew at minute 8 and the resident is
still being loaded when the road closes. This is the `ignore_pickup_duration`
mutation. On-scene time is the single most commonly omitted term in assisted
evacuation models, because it is the one term that is not a property of the
road network.

**Entry-time-only edge safety.** Under the naive rule the egress constraint
becomes `d + 10 <= 20`, again giving 10. The two bugs are independent and
produce the same wrong number here, which is itself worth knowing: a single
benchmark cannot distinguish them, and WG-BM-023 is needed to separate them.

## What this deliberately does not model

The responder's own survival, refuelling, crew endurance, the possibility of
more than one resident per vehicle, and any uncertainty whatsoever. Those belong
in later benchmarks; this one exists so that the arithmetic can be checked in
thirty seconds on paper.
