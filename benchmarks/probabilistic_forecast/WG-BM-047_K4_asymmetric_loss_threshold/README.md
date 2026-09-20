# WG-BM-047 (K4) — Asymmetric loss threshold

## Scenario

A crew can be sent down a spur road or held back.

| | road dangerous | road safe |
|---|---|---|
| `proceed` | **495** | 0 |
| `hold_back` | 0 | 5 |

Holding back costs 5 in lost time when the road was in fact safe, and nothing
when it was not. Proceeding costs nothing when the road is safe, and 495 when
the crew is caught.

## Derivation

The conservative action fully protects, so

```
E[proceed]   = p * L_failure
E[hold_back] = (1 - p) * L_conservative

p* L_f = (1 - p*) L_c   ->   p* = L_c / (L_c + L_f) = 5 / (5 + 495) = 0.01
```

| `p` | `E[proceed]` | `E[hold_back]` | Bayes action | 0.5 rule |
|---|---|---|---|---|
| 0.005 | 2.475 | 4.975 | `proceed` | `proceed` |
| 0.02 | 9.9 | 4.9 | `hold_back` | `proceed` — wrong |
| **0.40** | **198** | **3.0** | **`hold_back`** | **`proceed`** — wrong by 66x |

Under the prior of 0.02: prior action `hold_back`, expected loss 4.9;
clairvoyant expected loss 0; **EVPI = 4.9**.

## The point

The threshold is **1 per cent**. There is nothing unusual about the numbers: a
100:1 ratio between an entrapment and a delay is conservative if anything. The
consequence is that for most of the probability range the answer is "hold back",
and a system that waits for the hazard to become *likely* has already waited
forty times too long.

Note also what the formula depends on. Doubling both losses leaves `p*`
unchanged, so the threshold is a property of the **ratio** of the two costs, not
their scale — which is why it can be elicited from an incident commander who
would not put a number on either loss alone.

Two different matrices give two different formulas, and both appear in this
suite:

| Situation | Threshold |
|---|---|
| conservative action costs the same either way (WG-BM-046) | `p* = L_c / L_f` |
| conservative action fully protects (here) | `p* = L_c / (L_c + L_f)` |

Neither is 0.5, and an implementation must derive the threshold rather than
assume one. The `fixed_half_probability_threshold` mutation assumes one; this
benchmark and WG-BM-046 are its declared detectors.

## Expected

| Quantity | Value |
|---|---|
| `p*` | **0.01** |
| action at 0.005 / 0.02 / 0.4 | `proceed` / `hold_back` / `hold_back` |
| EVPI under the prior | 4.9 |
