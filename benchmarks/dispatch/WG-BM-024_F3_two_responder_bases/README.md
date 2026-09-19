# WG-BM-024 (F3) — Two responder bases

## Scenario

```
base_near (2 km) --4 min, corridor open [0, 6]---> resident --8 min--> refuge
base_far  (8 km) --10 min, corridor open [0, 60]-/          egress open [0, 30]
```

Pickup 5 minutes. The resident's location is tenable to minute 40.

## Derivation

**From the near base**

```
ingress: [d, d + 4]   inside [0, 6]    ->  d <= 2     <- binds
egress:  [d + 9, d + 17] inside [0, 30] ->  d <= 13
latest dispatch = 2 min
```

**From the far base**

```
ingress: [d, d + 10]  inside [0, 60]   ->  d <= 50
egress:  [d + 15, d + 23] inside [0, 30] -> d <= 7    <- binds
latest dispatch = 7 min
```

The far base is 6 minutes further away and offers **5 more minutes** of dispatch
latitude, because the near base's short corridor is the first thing the fire
closes. Overall the feasible dispatch set is `[0, 7]`.

| Dispatch | Near base | Far base | Selected | Arrival |
|---|---|---|---|---|
| 0 | feasible | feasible | near (arrives sooner) | 17 |
| 5 | **infeasible** | feasible | far | 28 |
| 8 | infeasible | infeasible | — | — |

## Two distinct decisions

This benchmark separates two things that are easy to conflate:

* **Which base to use at a given moment** — at `d = 0` the near base is right,
  because it delivers the resident 6 minutes sooner and every minute of slack
  matters.
* **How long the option stays open** — the near base's option expires at minute
  2, the far base's at minute 7. Planning the *deadline* from the near base
  understates the community's remaining decision time by 5 minutes; planning it
  from the far base and then dispatching from the near base at minute 5 sends a
  crew into a closed corridor.

A correct system reports both, keyed by base. The `nearest_base_only` mutation
considers only the geographically nearest base, reports a latest dispatch of 2,
and declares the mission impossible at minute 5 when in fact it is
straightforward. This benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| latest dispatch, near base | 2 min |
| latest dispatch, far base | 7 min |
| best base | `base_far` |
| nearest base | `base_near` |
| feasible bases at `d = 5` | `[base_far]` |
