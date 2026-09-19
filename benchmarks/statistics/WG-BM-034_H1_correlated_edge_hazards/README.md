# WG-BM-034 (H1) — Perfectly correlated edge hazards

## Scenario

A valley with two egress roads. Both are threatened by the same front driven by
the same wind, so in this scenario set either both survive or both are lost.

```
s_both_closed   p = 0.3    north closed, south closed
s_both_open     p = 0.7    north open,   south open
```

Decision: prepare for isolation (cost 20 whatever happens) or assume egress
(cost 0 if any road survives, 100 if none does).

## Derivation

Each road is closed only in `s_both_closed`, so:

```
marginal P(north closed) = 0.3
marginal P(south closed) = 0.3
true P(both closed)      = 0.3        <- read off the scenario set
P(both closed) assuming independence = 0.3 * 0.3 = 0.09
understatement factor    = 0.3 / 0.09 = 10/3 = 3.33
```

### The decision consequence

| | true correlated ensemble | independence-implied ensemble |
|---|---|---|
| `prepare_for_isolation` | 20 | 20 |
| `assume_egress` | `0.3 * 100 = ` **30** | `0.09 * 100 = ` **9** |
| recommended action | **prepare** | **assume egress** |

The independence assumption does not merely mis-state a probability by a factor
of three. It **reverses the decision**, and it does so in the direction of doing
less.

## Why this is not a corner case

Road failures in a wildfire are driven by a small number of shared causes: one
front, one wind field, one fuel state, often one ridge line. Conditional on the
day, they are close to comonotone. Marginal failure probabilities, on the other
hand, are the natural output of a per-edge hazard model, and multiplying them is
the natural next step. The combination is a standard and severe error:

* the understatement grows with the number of redundant roads — three
  perfectly-correlated roads at 0.3 each give `0.3` truth against `0.027`
  assumed, a factor of 11;
* it is worst exactly where redundancy is being claimed as a safety argument;
* it cannot be detected from the marginals, which are correct.

The only reliable defence is to carry **joint scenarios** rather than per-edge
probabilities through the pipeline, which is what this benchmark's input format
does deliberately.

The mutation `independent_edge_failures` reconstructs the joint from the
marginals; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| marginal closure probability, each road | 0.3 |
| true joint probability both closed | **0.3** |
| joint under independence | **0.09** |
| understatement factor | 3.33 |
| best action, true ensemble | `prepare_for_isolation` |
| best action, independence ensemble | `assume_egress` |
