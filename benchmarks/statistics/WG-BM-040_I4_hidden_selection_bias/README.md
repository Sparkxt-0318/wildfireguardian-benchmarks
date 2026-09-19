# WG-BM-040 (I4) — Hidden selection bias

## Scenario

Eight worlds: `w1`-`w4` easy (difficulty 0), `w5`-`w8` hard (difficulty 40).
Loss is `world difficulty + policy offset`, with offsets `policy_a = 5` and
`policy_b = 2`. **Policy B is genuinely better, by exactly 3.**

The two policies were run on overlapping but different subsets — the situation
that arises whenever an evaluation set accumulates over time:

```
policy_a evaluated on w1 w2 w3 w4 w5 w6     (4 easy, 2 hard)
policy_b evaluated on       w3 w4 w5 w6 w7 w8   (2 easy, 4 hard)
```

## Derivation

**Naive, unpaired**

```
policy_a: mean difficulty (0,0,0,0,40,40) = 13.333  ->  loss 18.333
policy_b: mean difficulty (0,0,40,40,40,40) = 26.667 -> loss 28.667
naive difference = 18.333 - 28.667 = -10.333        ->  "A is better by 10.3"
```

**Paired, on the four common worlds `w3 w4 w5 w6`**

```
mean difficulty = 20
policy_a = 25      policy_b = 22
paired difference = +3                              ->  "B is better by 3"
```

The paired difference recovers the true policy effect **exactly**, because
pairing differences out the world difficulty term, which is what the two
policies did not share.

| | naive | paired | truth |
|---|---|---|---|
| better policy | `policy_a` | `policy_b` | `policy_b` |
| margin | 10.3 | 3.0 | 3.0 |

The naive comparison gets both the **sign** and the **magnitude** wrong.

## Why this happens without anyone cheating

Nothing in this scenario requires bad faith. Evaluation sets grow: a new policy
is tested on the scenarios that were available that quarter; an older policy's
results are reused because rerunning is expensive; a few worlds fail to converge
and are dropped, and they are not dropped at random. The result is two numbers
in a results table that were never comparable, presented in the same column.

The difficulty term does not have to be labelled, either. Here `difficulty` is
an explicit field; in a real evaluation it is the unmeasured combination of
ignition location, wind and fuel state that makes some worlds hard for every
policy. That is precisely why pairing works and covariate adjustment may not:
pairing removes the term without needing to measure it.

## What a system must do

* **Compare on common worlds.** Report the set of worlds used for each policy
  and refuse, or loudly flag, a comparison whose intersection is empty.
* **Report the paired difference,** not the difference of the means.
* **Treat a shrinking intersection as a defect,** not an inconvenience. If two
  policies share no worlds, they have not been compared at all.

The `naive_unpaired_comparison` mutation reports the unpaired ranking; this
benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| naive mean loss, A / B | 18.333 / 28.667 |
| naive difference | -10.333 (favours A) |
| common worlds | `w3 w4 w5 w6` |
| paired mean loss, A / B | 25 / 22 |
| paired difference | **+3 (favours B)** |
| ranking sign flip | `true` |
