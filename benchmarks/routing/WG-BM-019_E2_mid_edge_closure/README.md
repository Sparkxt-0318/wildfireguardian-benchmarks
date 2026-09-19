# WG-BM-019 (E2) — Mid-edge closure

## Scenario

One road. Ten minutes end to end. The traveller enters at `t = 0`. The hazard
reaches the road at `t = 5`.

```
origin ---------------- 10 min, open on [0, 5] ---------------- refuge
                                ^
                          hazard arrives t = 5
```

## There is no convention-free answer

This is the case that forces a project to write its semantics down. At least
four rules are defensible:

| Rule | Verdict here | Comment |
|---|---|---|
| **Interval safety** — the whole traversal must fit in an open window | infeasible | conservative; assumes no mid-route escape |
| **Entry-time only** — the edge must be open when you enter | feasible, arrival 10 | assumes you outrun or survive the front |
| **Partial traversal** — you may proceed to the point reached at closure and then stop | reaches the midpoint, stranded | needs a model of what happens to a stranded vehicle |
| **Reversible** — you may turn back on detecting the closure | return to origin at minute 10 | needs a detection model and a turnaround time |

They give different answers, and none of them is a fact about the world. Each is
a modelling assumption about vehicle behaviour, driver information and
survivability inside a fire front.

## What this benchmark asserts

**This suite declares interval safety (WG-SEM-1) as its convention**, so the
expected verdict is `infeasible`. The benchmark additionally requires that the
implementation report what the entry-time rule would have concluded, as
`feasible_under_entry_time_semantics: true` with an arrival at minute 10.

An implementation may legitimately use a different convention. What it may not
do is fail to say which one it uses, because a downstream consumer cannot
otherwise tell whether "route available" means "you will arrive" or "you may
enter". The assumptions block of this benchmark is therefore as much a part of
the expected answer as the numbers.

## Waiting does not rescue it

The only open window starts at 0 and ends at 5. A 10-minute traversal never fits
inside it, at any departure time. `feasible_with_waiting` is also `false`.

## Expected

| Quantity | Value |
|---|---|
| feasible under interval safety | `false` |
| earliest arrival | `null` |
| feasible under entry-time rule | `true` |
| arrival under entry-time rule | 10 min |
