# WG-BM-035 (H2) — Mutually exclusive scenarios

## Scenario

Two equally likely wind scenarios. In `s1` the fire runs south and closes route
B; in `s2` it runs north and closes route A.

| | s1 (fire runs south) | s2 (fire runs north) |
|---|---|---|
| `route_a` | 0 | **100** |
| `route_b` | **100** | 0 |
| `hold` | 30 | 30 |

## Derivation

```
E[loss | route_a] = 0.5 * 0   + 0.5 * 100 = 50
E[loss | route_b] = 0.5 * 100 + 0.5 * 0   = 50
E[loss | hold]    = 30                              <- best
```

Regret against the best action in each scenario (0 in both):

```
max regret route_a = 100      max regret route_b = 100      max regret hold = 30
minimax-regret action = hold, sup-regret = 30
clairvoyant expected loss = 0       EVPI = 30
```

Both the expected-loss and the minimax-regret criteria pick `hold`, and knowing
the wind direction would be worth 30 — the entire loss.

## The averaged-input fallacy

Now average the two **fire fields** instead of the two **losses**. The mean
field has a half-intensity front on each side of the valley, and a half-intensity
front closes neither road:

```
loss in the averaged world:  route_a 0,  route_b 0,  hold 30
recommended action:          route_a
```

The averaged world is **more benign than any scenario that can actually
happen**. It contains no blocked road, because the blockage in `s1` and the
blockage in `s2` are in different places and each is diluted to half strength.
Acting on it gives route A, which costs 100 half the time.

This is not an artefact of a crude averaging scheme. It is a general property:
the loss function is not linear in the hazard field, so

```
loss(E[field])  !=  E[loss(field)]
```

and for threshold-shaped losses — a road is open or it is not — the left-hand
side is systematically the optimistic one. Averaging ensemble members into a
"mean fire perimeter" and then routing on it reproduces this error exactly.

## The correct order of operations

**Evaluate the decision in each scenario, then average the outcomes.** Never
average the scenarios and then evaluate once. The input format of this benchmark
enforces the distinction by making the averaged world a separately declared
object rather than something a solver can compute by accident.

The mutation `average_scenario_inputs` substitutes the averaged-world losses for
the ensemble expectation; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| expected loss, route A / route B / hold | 50 / 50 / **30** |
| best action | `hold` |
| sup-regret of `hold` | 30 |
| EVPI | 30 |
| best action in the averaged world | **`route_a`** (wrong) |
