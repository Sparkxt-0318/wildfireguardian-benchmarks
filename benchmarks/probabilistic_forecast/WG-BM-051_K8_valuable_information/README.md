# WG-BM-051 (K8) — Valuable information

## Scenario

The fire approaches from the north or the south, equally likely. Evacuating
along the road on the fire's side is disastrous.

| | `omega_north` | `omega_south` |
|---|---|---|
| `via_north` | 90 | 0 |
| `via_south` | 0 | 90 |
| `shelter` | 40 | 40 |

A bearing sensor is right four times in five:
`P(signal_north | omega_north) = 0.8`.

## Derivation

**Prior.** `E[via_north] = E[via_south] = 45`, `E[shelter] = 40` → **shelter**,
expected loss 40.

**Posterior.**

```
P(signal_north) = 0.5 * 0.8 + 0.5 * 0.2 = 0.5
P(omega_north | signal_north) = 0.4 / 0.5 = 0.8
    E[via_north] = 72   E[via_south] = 18   E[shelter] = 40   ->  via_south, 18

P(omega_north | signal_south) = 0.1 / 0.5 = 0.2
    mirror image                                             ->  via_north, 18
```

**Value.**

```
EVSI = 40 - (0.5 * 18 + 0.5 * 18) = 40 - 18 = 22
EVPI = 40 - 0                                  = 40
the sensor captures 22/40 = 55% of the available value
```

Every number is a finite sum over two hypotheses and two outcomes. **No
simulation is required or permitted**: a Monte Carlo estimate of 22 would be an
approximation to a quantity that can be written down.

## Three optimality regions, not one threshold

With three actions the optimal choice as a function of `p = P(omega_north)` is
the lower envelope of three lines:

```
p < 4/9        via_north
4/9 < p < 5/9  shelter
p > 5/9        via_south
```

So "the threshold" does not exist here, and a system that reports one has
flattened a three-way decision into a two-way one. The benchmark pins the whole
partition.

## Expected

| Quantity | Value |
|---|---|
| prior action | `shelter`, loss 40 |
| posterior on `signal_north` | 0.8 → `via_south`, loss 18 |
| posterior on `signal_south` | 0.2 → `via_north`, loss 18 |
| **EVSI** | **22** |
| EVPI | 40 |
| mutual information | 0.278072 bits |
