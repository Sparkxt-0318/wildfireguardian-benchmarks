# WG-BM-020 (E3) — Waiting needed

## Scenario

```
start --5 min, always open--> muster --5 min, open only on [20, 100]--> refuge
```

The muster point is stipulated to be a **safe holding location** for the whole
period. The second leg is closed until minute 20, when the front has passed over
it and the road is reopened.

## Derivation

```
arrive at muster            = 0 + 5  = 5 min
earliest entry to leg two   = 20 min          (window opens)
hold at muster              = 20 - 5 = 15 min
arrive at refuge            = 20 + 5 = 25 min
```

**With waiting forbidden**, departure from the muster point is forced to minute
5. The traversal interval `[5, 10]` is not inside `[20, 100]`, so the route is
**infeasible** — there is no route at all, and the correct output is a refusal,
not a plan.

**With waiting permitted**, the answer is arrival at **minute 25**, with a
recorded 15-minute hold.

## Why the distinction has to be explicit

"Wait here until the road reopens" is a real operational instruction, and for a
supervised convoy it is often the right one. It is also an instruction that a
router must not issue implicitly: it requires a location that is survivable for
the whole hold, a way to tell the traveller when to move, and a fallback if the
reopening does not happen. A routing engine that permits waiting without
modelling those three things is producing plans that cannot be executed.

Conversely, a router that silently forbids waiting will report "no route" for a
community that has a perfectly good one, and the operator has no way to tell
that refusal apart from a genuine entrapment.

This suite therefore requires the waiting policy to be declared per scenario,
and requires both answers to be reported. `allow_waiting` is part of the query,
not a global setting.

## What the hazard model must preserve

The second leg is closed *and then open again*. An implementation that reduces
the hazard to a single scalar "closure time" per edge — or to the final fire
perimeter — cannot represent a reopening and will call this route permanently
impossible. That is the `final_perimeter_hazard` mutation, and this benchmark is
one of its detectors.

## Expected

| Quantity | Value |
|---|---|
| arrival with waiting | 25 min |
| hold duration | 15 min |
| feasible without waiting | `false` |
| free-flow travel time | 10 min |
