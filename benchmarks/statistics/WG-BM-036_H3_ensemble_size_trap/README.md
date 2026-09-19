# WG-BM-036 (H3) — Ensemble size trap

## Scenario

A five-member ensemble, each member at probability 0.2:

| | s1 | s2 | s3 | s4 | s5 |
|---|---|---|---|---|---|
| `policy_a` | 10 | 10 | 10 | 10 | 10 |
| `policy_b` | 8 | 8 | 8 | 8 | 20 |

Then the **same ensemble** with two extreme members added at probability 0.001
each, the base members rescaled to 0.1996 so the total is still 1:

| | s6 | s7 |
|---|---|---|
| `policy_a` | 300 | 250 |
| `policy_b` | 12 | 12 |

## Derivation

**Base ensemble**

```
E[policy_a] = 10                 E[policy_b] = (8*4 + 20)/5 = 10.4
best per scenario: policy_b in s1..s4, policy_a in s5
max regret: policy_a = 2,        policy_b = 10
minimax-regret action = policy_a,  sup-regret = 2
```

**Extended ensemble**

```
E[policy_a] = 0.1996*10*5 + 0.001*300 + 0.001*250 = 10.53
E[policy_b] = 0.1996*(8*4+20) + 0.001*12*2        = 10.4032
max regret: policy_a = 288,      policy_b = 10
minimax-regret action = policy_b,  sup-regret = 10
```

| Quantity | Base | Extended | Change |
|---|---|---|---|
| expected loss, `policy_a` | 10 | 10.53 | **+0.53** |
| expected loss, `policy_b` | 10.4 | 10.4032 | +0.003 |
| sup-regret | 2 | 10 | **+8** |
| minimax-regret action | `policy_a` | **`policy_b`** | flipped |
| CVaR(0.9), `policy_a` | 10 | 15.3 | +5.3 |
| CVaR(0.9), `policy_b` | 20 | 20 | 0 |

## What is actually happening

Sup-regret is a **maximum over the scenario set**. A maximum has no dependence
on probability at all: a scenario of probability 0.001 counts exactly as much as
one of probability 0.2, and a scenario of probability `1e-12` would count the
same again. Consequently:

* adding scenarios can only increase sup-regret, never decrease it;
* the recommendation under minimax regret is decided by whichever member happens
  to be the most extreme, so it is a function of **how the ensemble was
  sampled**, not only of the physics;
* two teams with the same model and different ensemble sizes will reach
  different "robust" recommendations and neither will be wrong on its own terms.

CVaR at a fixed level behaves differently because it is an average over a fixed
*probability mass*, not over a set of members. Adding 0.2% of mass moves
CVaR(0.9) by at most that mass times the loss difference. It is still a tail
measure, and it is still sensitive to the extremes, but it is sensitive
*proportionately*.

## What this benchmark asserts, and what it does not

It asserts the numbers above. It does **not** assert that CVaR is the right
criterion and minimax regret the wrong one. Sup-regret answers a legitimate
question — *what is the worst thing that can happen if I am wrong?* — and in a
setting where the scenario set is a genuine bounded uncertainty set rather than
a sample, it is exactly right.

What a system must not do is report a sup-regret without reporting the size and
provenance of the scenario set alongside it, or compare sup-regrets computed
over different ensembles as if they were commensurable. This benchmark exists so
that the mechanical dependence is visible and quantified rather than argued
about.

## No mutation

No mutation is declared for this benchmark. The behaviour it pins is a property
of the decision criteria themselves, not a bug that can be injected — which is
precisely why the numbers need to be written down.
