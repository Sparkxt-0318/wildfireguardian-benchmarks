# WG-BM-059 (L1) — Expectation versus worst case

## Scenario

| | benign (p = 0.8) | severe (p = 0.2) |
|---|---|---|
| `policy_a` | 0 | **60** |
| `policy_b` | 15 | 25 |

## Derivation

```
E[policy_a] = 0.8 * 0  + 0.2 * 60 = 12          <- better average
E[policy_b] = 0.8 * 15 + 0.2 * 25 = 17

worst(policy_a) = 60
worst(policy_b) = 25                            <- better worst case

CVaR(0.9): the worst tenth of the mass lies inside the severe scenario for both,
so CVaR equals the severe loss:  60  and  25

max regret (best per scenario: 0 benign, 25 severe):  35  and  15
clairvoyant = 0.8 * 0 + 0.2 * 25 = 5            EVPI = 12 - 5 = 7
```

**A is better by 5 on the average and worse by 35 in the worst case.**

## Why no winner

The declared objective is `report_only`, and the result document's
`recommended_action` is `null`.

This is not indecision. Choosing between 5 units of expected loss and 35 units
of worst-case loss requires a **risk attitude**, and a risk attitude is a policy
input — it belongs to whoever is accountable for the outcome, not to the
software. A system that always returns a single ranked answer has one anyway; it
is simply undeclared, and in practice it is almost always "minimise the mean",
because that is the easiest thing to compute.

What the suite requires instead:

* both numbers are computed and reported;
* the objective is a declared input (`expected_loss`, `cvar`, `worst_case` or
  `report_only`);
* the recommendation follows the declared objective and nothing else.

WG-BM-060 exercises the same machinery with the objective set to CVaR, where
there *is* a right answer and ignoring the declaration produces the wrong one.

## Expected

| Quantity | `policy_a` | `policy_b` |
|---|---|---|
| expected loss | **12** | 17 |
| worst case | 60 | **25** |
| CVaR(0.9) | 60 | **25** |
| max regret | 35 | **15** |
| recommended | — | — |
