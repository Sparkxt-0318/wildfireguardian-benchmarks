# WG-BM-018 (E1) — Short unsafe route vs long safe route

## Scenario

```
              e_short_unsafe:  5 min, open only on [0, 4]
origin  ====================================================  refuge
              e_long_safe:     9 min, open throughout
```

Departure at `t = 0`, no waiting permitted.

## Derivation

Under **WG-SEM-1 (interval safety)** a traversal departing at `tau` is feasible
only if the entire interval `[tau, tau + w]` lies inside one open window of the
edge.

```
short route:  [0, 0 + 5] = [0, 5]  vs  open window [0, 4]   ->  INFEASIBLE
long route:   [0, 0 + 9] = [0, 9]  vs  open window [0, inf) ->  feasible, arrival 9
```

The traveller who enters the canyon road at minute 0 is still 1 minute from the
far end when the fire arrives at minute 4. That the road was open when they
entered is no comfort.

**Answer: the only feasible route is the 9-minute one, arriving at minute 9.**

## The counterfactual, stated explicitly

Under the naive entry-time rule — "the edge is open at the moment I enter, so I
may enter" — the short route is judged feasible and the reported arrival is
minute 5. The result document reports this as
`feasible_under_entry_time_semantics: true` and
`arrival_under_entry_time_semantics_min: 5.0`, next to the real answer, so that
a reader can see exactly which convention produced which number.

This is not a stylistic difference. The naive rule reports a 5-minute
evacuation that ends inside the fire, and it reports it with the same confidence
as a correct answer.

## Expected

| Quantity | Value |
|---|---|
| feasible routes | `[e_long_safe]` |
| earliest safe arrival | 9 min |
| shortest route | `e_short_unsafe`, 5 min |
| shortest route feasible | `false` |
| arrival under entry-time semantics | 5 min (wrong) |
