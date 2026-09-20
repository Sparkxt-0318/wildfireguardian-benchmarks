# WG-BM-052 (K9) — Information arrives too late

## Scenario

**Identical to WG-BM-051** except for three timestamps:

```
acquisition time    =  5 min      the sensor takes the measurement
availability time   = 12 min      the product reaches the decision maker
decision deadline   = 10 min      after this the evacuation cannot start
```

## Derivation

The decision problem has not changed, so neither have the statistical
quantities:

```
prior action  = shelter, expected loss 40
each branch   = 18
EVSI          = 22
EVPI          = 40
```

The timing has changed, and the product arrives **two minutes after the last
moment it could matter**. No policy can condition on it.

```
EVSI, statistical  = 22
EVSI, operational  =  0
action             = shelter, the prior-optimal one
```

## The distinction this establishes for the OSSE

Three times are routinely collapsed into one, and they are different:

| Time | Meaning | Consequence of confusing it |
|---|---|---|
| acquisition | when the sensor looked | an evaluation dated here leaks the future (WG-BM-014) |
| **availability** | when the product could be used | the only one a decision can consume |
| deadline | when the action must be taken | a forecast after it has zero operational value |

An observing-system experiment that scores sensors on statistical information —
mutual information, EVSI, error reduction — will rank this sensor at 22 and
recommend building more of them. Its operational contribution is zero, and it
would remain zero if its accuracy were doubled.

The corollary is a design rule: the quantity to maximise is not information, and
not information per unit cost, but **information available before the deadline**.
Latency is a feasibility constraint, not a performance attribute.

The `ignore_availability_time` mutation sets the operational value equal to the
statistical one; this benchmark is its declared detector, together with
WG-BM-053, which shows the ranking consequence.

## Expected

| Quantity | Value |
|---|---|
| EVSI, statistical | 22 |
| EVSI, operational | **0** |
| available before the deadline | `false` |
| action taken | `shelter` (unchanged from the prior) |
