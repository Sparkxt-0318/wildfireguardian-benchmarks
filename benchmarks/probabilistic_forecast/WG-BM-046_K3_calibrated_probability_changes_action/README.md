# WG-BM-046 (K3) — Calibrated uncertainty changes the action

## Scenario

One route, with a calibrated probability `p` of closing before the convoy is
through.

| | route closes | route stays open |
|---|---|---|
| `proceed` | 120 | 0 |
| `divert` | 24 | 24 |

## Derivation

```
E[proceed] = 120 p        E[divert] = 24
indifference:  120 p* = 24   ->   p* = 24 / 120 = 0.2
```

`proceed` is optimal strictly below 0.2 and `divert` at or above it.

| `p` | `E[proceed]` | `E[divert]` | Bayes action | action under a 0.5 rule |
|---|---|---|---|---|
| 0.10 | 12 | 24 | `proceed` | `proceed` (agrees by luck) |
| **0.35** | **42** | **24** | **`divert`** | **`proceed`** — wrong |
| 0.60 | 72 | 24 | `divert` | `divert` (agrees by luck) |

Under the declared prior of 0.1 the prior-optimal action is `proceed`, expected
loss 12; the clairvoyant expected loss is `0.1 * 24 + 0.9 * 0 = 2.4`, so EVPI is
9.6.

## The point

`p = 0.5` is not a decision threshold. It is the point at which one *hypothesis*
becomes more likely than another, which is a different question from which
*action* is better. The two coincide only when the loss matrix is symmetric, and
a wildfire loss matrix never is.

The probe at 0.35 exists because the other two agree with the wrong rule. A
benchmark whose cases all happen to agree with the bug does not detect it; this
is the same discipline that removed the overclaim from WG-BM-028.

WG-BM-047 takes the asymmetry to its operational extreme, where `p*` is 0.01.

## Expected

| Quantity | Value |
|---|---|
| `p*` | **0.2** |
| action at 0.1 / 0.35 / 0.6 | `proceed` / `divert` / `divert` |
| EVPI under the prior | 9.6 |
