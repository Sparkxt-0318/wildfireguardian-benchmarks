# WG-BM-039 (I3) — Practical equivalence

## Scenario

Two evacuation policies are compared on the **same 2000 simulated worlds**. The
paired differences in clearance time are constructed deterministically — 1000
values at `+1.3` minutes and 1000 at `-0.7` minutes — so that the sample
statistics are exact:

```
mean difference = 0.3 minutes         sd = sqrt(2000/1999) = 1.0002501
```

The operationally meaningful difference, agreed **before** looking at the data,
is **1 minute**.

## Derivation

```
SE   = 1.0002501 / sqrt(2000) = 0.0223663
95% CI = 0.3 +/- 1.959964 * 0.0223663 = [0.256163, 0.343837]
```

**Significance.** The interval excludes zero; the effect is
`0.3 / 0.0223663 = 13.4` standard errors from zero. Significant at any
conventional level, with room to spare.

**Practical equivalence.** The entire interval lies inside `[-1, +1]`, the
pre-agreed margin. By the two-one-sided-tests criterion the policies are
**equivalent**.

Both statements are true at once, and neither contradicts the other.

## What this benchmark is for

A wildfire decision programme can afford to run 2000 simulated worlds. At that
sample size the standard error is 0.022 minutes and essentially **any**
difference becomes significant — a policy change worth 1.3 seconds of clearance
time will produce `p < 0.001`. Significance testing at this sample size measures
how much compute was purchased, not whether the policy matters.

The two things a system must do instead:

1. **Declare the practical margin in advance.** Here it is 1 minute, because
   below that the difference is inside the noise of a real evacuation —
   notification lag, household preparation time, traffic signal timing. The
   margin is a domain judgement and it must be written down before the
   comparison, not chosen afterwards.
2. **Test equivalence, not just difference.** "Not significantly different" and
   "equivalent" are different claims, and with small samples the first is
   routinely true while the second is unsupported. Here the reverse holds: the
   difference *is* significant, and the policies *are* equivalent.

## Expected

| Quantity | Value |
|---|---|
| mean difference | 0.3 min |
| 95% CI | `[0.2562, 0.3438]` |
| practical margin | 1.0 min |
| statistically significant | `true` |
| practically equivalent | `true` |
| conclusion | `equivalent` |
