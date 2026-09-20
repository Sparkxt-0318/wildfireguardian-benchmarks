# WG-BM-061 (L3) — Unresolved state, resolved decision

## Scenario

The fire could break north, south or east. The ensemble is close to uniform:
**0.34 / 0.33 / 0.33.**

| | north | south | east |
|---|---|---|---|
| `reinforce_refuge` | **6** | **6** | **6** |
| `evacuate_north` | 8 | 50 | 50 |
| `evacuate_south` | 50 | 8 | 50 |
| `evacuate_east` | 50 | 50 | 8 |

Declared: acceptable loss 10, state-resolution threshold 0.8, perturbation
tolerance 1.0.

## Derivation

Reinforcing costs 6 everywhere. Every evacuation costs at least 8 **even in the
scenario it was chosen for**, so reinforcing is the best action in each scenario
separately:

```
clairvoyant expected loss = 6 = E[reinforce_refuge]
EVPI = 0                                          exactly
```

```
largest scenario weight = 0.34  <  0.8   ->  state NOT resolved
runner-up expected loss = 35.72,  margin = 29.72
smallest single-cell perturbation that flips it = 29.72 / 0.34 = 87.41  >>  1.0
                                         ->  decision IS resolved
```

Reinforcing is also **robust**: worst case 6, inside the acceptable loss of 10.
No evacuation is; each has a worst case of 50.

## The governance point

> Uncertainty about the world does not imply a need for more information.

The state here is as unresolved as a three-way ensemble can be, and the decision
is completely determined: perfect knowledge of which way the fire breaks would
change nothing and be worth nothing. A system that reports "cannot decide,
acquire more data" has answered the wrong question — and in an incident the cost
of that answer is the time spent waiting.

The right question is not *how uncertain are we?* but **would any resolution of
the uncertainty change what we do?** Those come apart in both directions:

| | WG-BM-061 (here) | WG-BM-062 |
|---|---|---|
| state resolved | **no** (0.34) | yes (0.97) |
| decision resolved | **yes** | **no** |

The `unresolved_state_blocks_decision` mutation reports an unresolved decision
whenever the state is unresolved; this benchmark and WG-BM-063 are its declared
detectors.

## Expected

| Quantity | Value |
|---|---|
| expected loss, reinforce | 6 |
| EVPI | **0** |
| optimal in every scenario | `reinforce_refuge` |
| state certainty | 0.34 → not resolved |
| perturbation needed to flip | 87.41 → stable |
| decision resolved | **true** |
