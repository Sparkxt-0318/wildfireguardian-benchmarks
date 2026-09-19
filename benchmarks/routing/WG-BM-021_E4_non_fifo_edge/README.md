# WG-BM-021 (E4) — Non-FIFO edge

## Scenario

One link. Before minute 5 the only way across is a 60-minute detour. From minute
5 an escorted convoy runs and the crossing takes 10 minutes.

```
travel_time(depart tau) = 60 min   for tau in [0, 5)
                        = 10 min   for tau >= 5
```

## Derivation

Arrival as a function of departure:

| Depart | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Arrive | 60 | 61 | 62 | 63 | 64 | **15** | 16 | 17 | 18 | 19 | 20 |

Departing at minute 5 arrives **45 minutes earlier** than departing at minute 0.
The arrival function is not non-decreasing, so the network is **not FIFO**.

* best achievable arrival: **15 min**, departing at **5**
* arrival if you leave immediately: **60 min**
* with waiting permitted: hold 5 minutes, arrive at 15

## Why this breaks standard shortest-path machinery

Time-dependent Dijkstra, A\*, contraction hierarchies and every label-setting
variant rely on the FIFO property: if you arrive at a node earlier you can do no
worse. Under FIFO a label can be settled permanently the first time it is
reached. Here that reasoning is invalid — an earlier arrival at `start`
(minute 0) yields a *worse* arrival at `refuge` than a later one (minute 5) —
and a settled label is simply wrong.

There are exactly two defensible responses:

1. **Permit waiting.** Adding a wait at the node restores the FIFO property, and
   the optimum (15 min) is recovered. This is what the result document's
   `arrival_with_waiting_min` shows.
2. **Refuse the case.** Detect that the travel-time profile is not FIFO and
   decline to answer, rather than returning the 60-minute label as if it were
   optimal.

What is **not** acceptable is silently returning 60 minutes. That is the
`fifo_assumption` mutation, which forces the reported optimum to the immediate
departure and clears the `fifo_violated` flag; this benchmark is its declared
detector.

## Where non-FIFO travel times come from in practice

They are not a contrivance. Escorted convoys, ferry and shuttle schedules,
contraflow switch-over times, pilot-car operations on a single-lane section, and
a road that is being actively defended and reopened all produce departure-time
windows where waiting strictly dominates leaving now.

## Expected

| Quantity | Value |
|---|---|
| arrival departing immediately | 60 min |
| best arrival over departures | 15 min |
| optimal departure | minute 5 |
| FIFO violated | `true` |
