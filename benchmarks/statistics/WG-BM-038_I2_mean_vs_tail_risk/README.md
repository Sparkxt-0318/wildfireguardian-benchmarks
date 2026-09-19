# WG-BM-038 (I2) — Mean versus tail risk

## Scenario

Two evacuation policies with exactly specified discrete loss distributions.

| Policy | Loss | Probability |
|---|---|---|
| `policy_a` | 0 | 0.9 |
| | 100 | 0.1 |
| `policy_b` | 12 | 0.9 |
| | 20 | 0.1 |

Policy A is usually free and occasionally catastrophic. Policy B is always
mildly costly.

## Derivation

```
mean(A)       = 0.9 * 0  + 0.1 * 100 = 10
mean(B)       = 0.9 * 12 + 0.1 * 20  = 12.8

CVaR_0.9(A)   = mean loss over the worst 10% of mass = 100
CVaR_0.9(B)   = mean loss over the worst 10% of mass = 20
```

The worst 10% of the probability mass is exactly the upper atom in each case, so
both CVaR values are read off directly with no interpolation.

| | mean | CVaR(0.9) |
|---|---|---|
| `policy_a` | **10** | 100 |
| `policy_b` | 12.8 | **20** |

Policy A is better by 2.8 on the average and **five times worse** in the tail.
The rankings conflict.

## Why both numbers are needed

The mean is the right criterion when losses are fungible and the decision
repeats often enough for the average to be realised. Neither condition holds for
an evacuation: a community experiences one fire, and the loss in the 10% branch
of policy A is not 10 units of inconvenience — it is the outcome the entire
system exists to prevent.

Nor is CVaR automatically right. It discards the 90% of outcomes in which policy
A is free, and a policy chosen purely on the tail will over-evacuate, which has
its own costs in compliance, credibility and the next fire.

What this benchmark requires is that **both are reported and the criterion is
declared**. Here the declared preference is `cvar`, so the recommendation is
`policy_b`; with a declared preference of `mean` the answer would be `policy_a`
and would be equally defensible, provided it is stated.

The `mean_only_ranking` mutation ignores the declared preference and recommends
the better average; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| mean loss, A / B | 10 / 12.8 |
| CVaR(0.9), A / B | 100 / 20 |
| best by mean | `policy_a` |
| best by CVaR | `policy_b` |
| rankings conflict | `true` |
