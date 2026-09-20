# WG-BM-057 (K14) — Non-detection is not absence

## Scenario

An airborne detector overflies a drainage where fire is suspected.

```
prior: P(fire) = 0.2

P(no detection | fire)    = 0.30        <- it misses 3 real fires in 10
P(no detection | no fire) = 0.95
```

**It reports nothing.**

| | fire | no fire |
|---|---|---|
| `proceed` | 95 | 0 |
| `divert` | 0 | 5 |

## Derivation

```
P(no detection) = 0.2 * 0.30 + 0.8 * 0.95 = 0.06 + 0.76 = 0.82
P(fire | no detection) = 0.06 / 0.82 = 3/41 = 0.0731707317
```

The reading is **genuinely informative** — 0.2 falls to 0.073, a factor of 2.7 —
and it is **nowhere near zero**.

```
p* = 5 / (5 + 95) = 0.05
0.0732 > 0.05   ->  divert,  unchanged from the prior
```

Both branches divert (`P(fire | detect) = 0.14/0.18 = 0.778` is also above `p*`),
so `EVSI = 0`: **this detector cannot license standing down, whatever it
reports.**

## The two errors this separates

The benchmark is aimed at one error and guards against its opposite.

**"No detection means no fire."** Sets the posterior to 0, which is below `p*`,
and sends people into a drainage that is 7.3% likely to be burning. This is the
`non_detection_is_absence` mutation and this benchmark is its detector.

**"The detector is useless, ignore it."** Also wrong: the reading moved the
belief by a factor of 2.7, and that is worth having. What it did not do is cross
a decision boundary — and *that* is the question to ask of an observation, not
whether it was informative.

## Relation to WG-BM-017

WG-BM-017 (D5) makes the same point without probabilities: it distinguishes a
cell where the detector is reliable from one where it is not, and shows the
route choice flipping. This benchmark supplies the number that D5 could only
gesture at — after a negative reading from a detector with a 30% miss rate and a
20% prior, the fire probability is **7.3%**, and whether that is acceptable is a
question for the loss matrix, not for the detector.

## Expected

| Quantity | Value |
|---|---|
| `P(fire \| no detection)` | **3/41 = 0.0732** |
| `P(fire \| detection)` | 0.7778 |
| `p*` | 0.05 |
| action after non-detection | `divert` (unchanged) |
| EVSI | 0 |
