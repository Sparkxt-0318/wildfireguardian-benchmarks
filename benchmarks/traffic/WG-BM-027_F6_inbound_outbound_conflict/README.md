# WG-BM-027 (F6) — Inbound / outbound conflict

## Scenario

One road serves both directions. The community is evacuating outbound between
minutes 0 and 40; the responder must drive inbound along the same road, collect
one resident, and bring them out to a refuge **by minute 40**.

| Leg | Free flow | During the evacuation window |
|---|---|---|
| inbound `base -> resident` | 10 min | **25 min** (against the flow) |
| outbound `resident -> refuge` | 10 min | **15 min** (in the queue) |

Pickup is 5 minutes.

## Derivation

**Without the capacity interaction** (free flow everywhere):

```
d = 0:  reach resident 10, pickup done 15, reach refuge 25   -> 15 minutes of slack
feasible for all d <= 15
```

**With the capacity interaction:**

```
d = 0:  inbound 25 min -> reach resident 25
        pickup 5 min   -> done at 30
        outbound 15 min-> reach refuge 45        -> 5 minutes LATE
```

Dispatching later does not help. Any dispatch before minute 40 still meets the
25-minute inbound leg. A dispatch at or after 40 runs at free flow but arrives at
`d + 25 >= 65`. **The mission is infeasible at every dispatch time.**

```
with capacity:     feasible set = {}            (empty)
without capacity:  feasible set = [0, 15]
```

## What this benchmark is really about

The free-flow model does not get the answer slightly wrong. It reports a mission
with **15 minutes of slack** for a mission that **cannot be done at all**. There
is no dispatch time, no base, and no route that recovers it — the only real
options are to change the traffic plan (contraflow, a held lane, an air asset) or
to accept that this resident cannot be assisted by road during the evacuation.
A planning tool that cannot represent the conflict will never surface that
choice, and the decision will be made implicitly by the first crew that gets
stuck.

This is also why the conflict belongs in the benchmark suite rather than in a
traffic microsimulation. Nothing subtle is being modelled here: two fixed travel
times, taken as given. The point is not to predict congestion accurately, it is
to notice that ingress and egress share a road.

## What is deliberately not modelled

Queue formation and dissipation, shockwave propagation, intersection control,
the effect of the responder vehicle itself on the outbound flow, and any
feedback from the evacuation rate to the travel times. The congested travel
times are **stipulated inputs**, not outputs of a traffic model. A benchmark
that required a queueing model to state its expected answer would no longer be
hand-checkable, which is the property this suite refuses to trade away. Richer
traffic benchmarks are listed in `reports/KNOWN_GAPS.md`.

## Expected

| Quantity | Value |
|---|---|
| feasible dispatch set with capacity | empty |
| feasible dispatch set at free flow | `[0, 15]` |
| free-flow arrival at `d = 0` | 25 min (deadline 40) |
| capacity binding | `true` |
