# WG-BM-048 (K5) — Coherent scenario ensemble

## Scenario

Five worlds from an ensemble generator, describing the joint state of two roads.

| World | north | south | raw weight | admissible |
|---|---|---|---|---|
| `omega_1` | open | open | 3 | yes |
| `omega_2` | closed | open | 1 | yes |
| `omega_3` | open | closed | 1 | yes |
| `omega_4` | closed | closed | 3 | yes |
| `omega_5` | closed | closed | 2 | **no** — closes the north road under a south wind, which the declared physics forbids |

Declared semantics: **weights are unnormalised and are renormalised over the
admissible set only.**

## Derivation

```
admissible raw total = 3 + 1 + 1 + 3 = 8
weights = 0.375, 0.125, 0.125, 0.375        sum = 1
```

`omega_5` is **excluded**, not down-weighted, and it is flagged in the input
rather than silently deleted so that the exclusion is auditable.

```
P(north closed) = w2 + w4 = 0.125 + 0.375 = 0.5
P(south closed) = w3 + w4 = 0.125 + 0.375 = 0.5
P(both closed)  = w4                      = 0.375     <- read off the ensemble
product of marginals = 0.5 * 0.5          = 0.25      <- understates by 1.5x
```

Losses: `assume_egress` costs 140 when both roads are closed and 0 otherwise;
`prepare_isolation` costs 40 whatever happens.

```
E[assume_egress]     = 0.375 * 140 = 52.5
E[prepare_isolation] = 40                     ->  prepare
```

Under the independence-implied distribution (0.25 on each joint state):

```
E[assume_egress] = 0.25 * 140 = 35            ->  assume egress
```

**The recommendation flips.**

## Three ways to get this wrong, all pinned

1. **Multiply the marginals.** Both marginals are correct and their product is
   not the joint. The error is invisible from the marginals alone.
2. **Renormalise over everything.** Including `omega_5` gives weights
   0.3/0.1/0.1/0.3/0.2, a joint closure probability of 0.5, and an expected loss
   of 70 for `assume_egress` — a third distinct answer from the same file.
3. **Drop the inadmissible world silently.** Then nobody can tell whether the
   generator produced four worlds or five, and the ensemble's provenance is
   unrecoverable. The admissibility flag and the `excluded_scenarios` field
   exist so that the exclusion is a reported fact.

## Expected

| Quantity | Value |
|---|---|
| normalised weights | 0.375 / 0.125 / 0.125 / 0.375 |
| excluded | `omega_5` |
| `P(both closed)` | **0.375** |
| under independence | 0.25 |
| best action | `prepare_isolation` |
| best action under independence | `assume_egress` |
