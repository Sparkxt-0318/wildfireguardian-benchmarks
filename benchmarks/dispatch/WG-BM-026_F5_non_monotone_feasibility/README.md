# WG-BM-026 (F5) — Non-monotone dispatch feasibility

## Scenario

```
base --6 min, corridor open on [0, 10] and [20, 40]--> resident --10 min--> refuge
```

The flaming front crosses the ingress corridor between minutes 10 and 20. Once
it has passed, the road is reopened at minute 20. Pickup is 4 minutes; the
resident's location is tenable to minute 90; the egress road is open to minute
60.

## Derivation

The 6-minute ingress traversal must fit inside **one** open window:

```
inside [0, 10]:   d + 6 <= 10                ->  0 <= d <= 4
inside [20, 40]:  d >= 20 and d + 6 <= 40    -> 20 <= d <= 34
```

No departure in `(4, 20)` works: it would either leave the vehicle on the road
when the front arrives, or start before the road reopens.

The egress leg departs at `d + 10` and arrives at `d + 20`; `[d+10, d+20]`
inside `[0, 60]` gives `d <= 40`, which does not bind. Tenability does not bind
either.

```
feasible dispatch set = [0, 4]  u  [20, 34]
```

| Dispatch | Outcome | Arrival |
|---|---|---|
| 2 | success | 22 |
| **10** | **fails at ingress** | — |
| 25 | success | 45 |
| 36 | fails at ingress | — |

## Why this is the most important benchmark in the F family

Almost every assisted-evacuation tool in the literature and in practice reports
a **single scalar**: "latest safe dispatch time", "trigger point", "time
remaining". That representation carries an implicit claim — that feasibility is
*monotone*, so that everything before the deadline works and everything after it
does not.

Here the latest feasible dispatch is **34 minutes**, and dispatching at **10
minutes** fails. Any system that reports only `34` will, if believed, send a
crew into a corridor that is on fire, and it will do so while displaying 24
minutes of remaining margin.

The mechanism is not exotic. A corridor being overrun and then reopened is the
normal life cycle of a road in a fire: it is closed while the flaming front
crosses it, and it is usable again behind the front once the fire has moved on.
Any hazard model with re-openings produces non-monotone feasibility somewhere.

## What a correct system must emit

The **set** of feasible dispatch times, not its supremum. Concretely, at least:

```
feasible_intervals: [[0, 4], [20, 34]]
```

and a warning that the scalar summary is unsafe:

```
monotone_feasibility: false
scalar_latest_sufficient: false
infeasible_dispatch_below_latest_min: 5
```

The `monotone_dispatch_assumption` mutation collapses the two intervals into
`[[0, 34]]` — exactly the scalar summary — and this benchmark is its declared
detector.

## A note on the gap counterexample

`infeasible_dispatch_below_latest_min` is reported as `5.0`: the first sampled
dispatch time below the latest feasible time at which the mission fails. Its
exact value depends on the sampling grid (1 minute here), and the benchmark pins
the value produced by that declared grid. The *existence* of such a time is what
matters and is asserted separately as an invariant.
