# WG-BM-053 (K10) — Less informative but timely beats better information

## Scenario

The WG-BM-051 decision, with two candidate observing systems and a **minute-10
deadline**:

| Observation | Accuracy | Available | Mutual information |
|---|---|---|---|
| `perfect_late` | resolves the world exactly | minute 12 | 1.000 bits |
| `weak_early` | right 7 times in 10 | **minute 4** | 0.1187 bits |

## Derivation

Prior action: `shelter`, expected loss 40.

**Perfect overflight.** Each branch has posterior 1 or 0, the matching road
costs nothing, so `EVSI = 40 - 0 = 40`. Available at minute 12 → **operational
value 0**.

**Crude ground report.**

```
P(signal_north) = 0.5 * 0.7 + 0.5 * 0.3 = 0.5
P(omega_north | signal_north) = 0.35 / 0.5 = 0.7
    E[via_south] = 0.3 * 90 = 27   <  E[shelter] = 40   ->  via_south
mirror image on the other branch
EVSI = 40 - 27 = 13,  all of it operational
```

| Ranking | 1st | 2nd |
|---|---|---|
| by information | `perfect_late` (1.000 bits) | `weak_early` (0.1187 bits) |
| by **operational value** | **`weak_early` (13)** | `perfect_late` (0) |

**The rankings are opposite.**

## What this tests

This is the WildfireGuardian thesis in its smallest form: **information quality
and timing must be evaluated jointly, because neither dominates the other.** A
factor-of-eight advantage in information is worth nothing against eight minutes
of latency.

Two consequences for an observing-system experiment:

1. A sensor-tasking objective built on information content will task the
   overflight and get nothing. The objective has to be
   `E[loss reduction | available before the deadline]`.
2. Improving the crude sensor's accuracy and improving the overflight's latency
   are not comparable investments, and only the second can change the
   overflight's contribution from zero.

Note also what is *not* claimed: the overflight is not useless in general. It is
useless for **this decision with this deadline**. Move the deadline to minute 15
and the ranking reverses again — which is exactly why the deadline is a declared
input and not a constant.

## Expected

| Quantity | `perfect_late` | `weak_early` |
|---|---|---|
| EVSI, statistical | 40 | 13 |
| EVSI, operational | **0** | **13** |
| mutual information | 1.000 bits | 0.1187 bits |
| recommended | | **yes** |
