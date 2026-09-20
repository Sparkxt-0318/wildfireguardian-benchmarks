# WG-BM-054 (K11) — Correlated observation errors

## Scenario

Two smoke sensors on the same ridge, sharing a power supply and a sight line.
Each is individually right four times in five. **Both report clear.**

Declared joint likelihood:

| | `1,1` | `1,0` | `0,1` | `0,0` |
|---|---|---|---|---|
| `P(. \| dangerous)` | 0.76 | 0.04 | 0.04 | 0.16 |
| `P(. \| safe)` | 0.16 | 0.04 | 0.04 | 0.76 |

The marginals are exactly the independent ones — `0.76 + 0.04 = 0.80` — so
**nothing in a per-sensor calibration report would reveal the dependence.** What
differs is that the two agree with probability 0.92 instead of 0.68.

| | dangerous | safe |
|---|---|---|
| `proceed` | 90 | 0 |
| `divert` | 0 | 10 |

## Derivation

`p* = 10 / (10 + 90) = 0.1`. Prior 0.5.

```
true:          P(dangerous | 0,0) = 0.16 / (0.16 + 0.76) = 4/23  = 0.1739130435
independence:  P(dangerous | 0,0) = 0.04 / (0.04 + 0.64) = 1/17  = 0.0588235294
```

In evidence terms:

```
true log-likelihood ratio         = log2(0.16 / 0.76) = -2.247928 bits
independence-assumed              = log2(0.04 / 0.64) = -4.000000 bits
```

The independence assumption claims **two full sensors' worth of evidence from
two sensors that largely repeat each other.**

```
0.174 > 0.1  ->  divert       (correct)
0.059 < 0.1  ->  proceed      (a system assuming independence)
```

## The sharpest part

Under the **correct** joint, the observation never changes the action: every
branch diverts, so `EVSI = 0` exactly. The independence assumption does not
merely add noise to a correct answer — it **manufactures a decision change out
of an observation that should not have produced one**, and the change is towards
the unsafe action.

## Why this is the normal case in a fire

Sensor errors are correlated by construction: shared smoke plumes, shared cloud,
shared power, shared communications, shared calibration drift, shared model
background. Two agreeing readings from co-located instruments are close to one
reading, and the extreme version of that is WG-BM-055, where they *are* one
reading.

The defence is to carry the joint likelihood rather than per-sensor marginals.
The marginals here are correct and they do not contain the information needed to
avoid the error.

The `assume_conditional_independence` mutation replaces the declared joint by
the product of the marginals; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| true posterior after `0,0` | **0.17391** |
| posterior assuming independence | 0.05882 |
| true evidence | -2.2479 bits |
| evidence claimed by independence | −4.0000 bits |
| action, true / independence | `divert` / **`proceed`** |
| EVSI under the correct joint | 0 |
