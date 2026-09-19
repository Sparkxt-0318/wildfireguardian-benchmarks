# WG-BM-041 (J1) — Uncertainty with a robust action available

## Scenario

One resident. Two plausible worlds, equally likely: the fire arrives from the
north, or from the south.

| | `w_north` | `w_south` |
|---|---|---|
| `reinforce_shelter` | **4** | **4** |
| `evacuate_north` | 5 | 90 |
| `evacuate_south` | 90 | 5 |

The declared acceptable loss threshold is **10**.

A perfect reconnaissance flight is available at minute 5, comfortably before the
minute-10 decision deadline.

## Derivation

Reinforcing the shelter is the best action **in each world separately**, not
merely on average: 4 beats 5 in `w_north` and 4 beats 5 in `w_south`. Therefore

```
clairvoyant expected loss = 0.5 * 4 + 0.5 * 4 = 4
best fixed action         = reinforce_shelter, expected loss 4
EVPI                      = 4 - 4 = 0
```

The recon flight is timely and perfectly informative, and its value is **zero**:
on either signal the Bayes action is still to reinforce the shelter. The
informed policy's action map is identical to the baseline's.

The worst case under the robust action is 4, inside the acceptable threshold of
10, so the resident is **robustly protectable**: there exists a single
action that is acceptable across the whole uncertainty set.

## Definitions this benchmark fixes

**Robustly protectable.** There exists an action whose loss is within the
acceptable threshold in every scenario of the declared uncertainty set. Note
what this does *not* require: it does not require knowing which scenario is
true, it does not require the scenarios to be probabilistically weighted, and it
does not require the action to be optimal in any of them.

**Value of information is relative to the decision, not to the uncertainty.**
There is a great deal of uncertainty here — the two worlds could hardly disagree
more about where the fire goes — and none of it is decision-relevant. Resolving
uncertainty is only worth something when the resolution would change what you
do.

## Why a zero-value case has to be in the suite

Without it, a system is rewarded for recommending observation, reconnaissance
and further modelling in every situation, since a positive recommendation is
never penalised. Reconnaissance flights are scarce, and tasking one to resolve
an uncertainty that cannot change the action is a real cost paid by whichever
decision genuinely needed it.

This benchmark is the reference point for WG-BM-042, which is the same structure
with the robust action removed.

## Expected

| Quantity | Value |
|---|---|
| EVPI | **0** |
| value of the recon flight | 0 |
| robust action | `reinforce_shelter` |
| worst-case loss of the robust action | 4 (threshold 10) |
| informed actions identical to baseline | `true` |
