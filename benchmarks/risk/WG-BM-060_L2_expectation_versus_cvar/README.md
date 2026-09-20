# WG-BM-060 (L2) — Expectation versus CVaR

## Scenario

| | routine (0.85) | awkward (0.10) | extreme (0.05) |
|---|---|---|---|
| `policy_a` | 0 | 20 | **300** |
| `policy_b` | 18 | 18 | 40 |

Declared objective: **CVaR at alpha = 0.9.**

## Derivation

```
E[policy_a] = 0 + 2 + 15        = 17         <- better mean
E[policy_b] = 15.3 + 1.8 + 2    = 19.1
```

CVaR averages the worst tenth of the **probability mass**, so the tail boundary
falls inside an atom and the atom is split:

```
CVaR_0.9(A) = (0.05 * 300 + 0.05 * 20) / 0.1 = (15 + 1)  / 0.1 = 160
CVaR_0.9(B) = (0.05 * 40  + 0.05 * 18) / 0.1 = (2 + 0.9) / 0.1 = 29
```

A's conditional tail loss is **5.5 times** B's, for 2.1 units of better average.

```
max regret:  A 260,  B 18        ->  B is also minimax-regret
clairvoyant = 3.8                ->  EVPI = 13.2
```

**Declared objective is CVaR → recommend `policy_b`.**

## The atom split matters

This is the reason the benchmark has three outcomes rather than two. With two
outcomes the worst tenth of the mass usually sits entirely inside the worst
atom, and CVaR degenerates to the maximum — at which point an implementation
that computes the maximum and calls it CVaR passes. Here the boundary falls
strictly inside the `awkward` atom, and getting 160 rather than 300 (the
maximum) or 158 (dropping the partial atom) requires the proportional split.

## The interface with evaluation

The objective is an input, and the recommendation follows it. That matters for
`wildfireguardian-evaluation`: a policy comparison reported without its
objective is not interpretable, and two comparisons with different objectives
are not commensurable. The `objective_ignored_use_mean` mutation reports the
expected-loss winner whatever the configuration says; this benchmark is its
declared detector.

## Expected

| Quantity | `policy_a` | `policy_b` |
|---|---|---|
| expected loss | **17** | 19.1 |
| CVaR(0.9) | 160 | **29** |
| worst case | 300 | **40** |
| max regret | 260 | **18** |
| recommended (objective = CVaR) | | **yes** |
