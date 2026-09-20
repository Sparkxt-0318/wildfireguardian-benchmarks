# WG-BM-062 (L4) — Identifiable state, fragile decision

## Scenario

The fire's behaviour is nearly certain — **97 per cent** on one scenario.

| | expected (0.97) | surprise (0.03) |
|---|---|---|
| `action_a` | 10 | 10 |
| `action_b` | 10 | 17 |

The loss numbers were **elicited from an incident commander, not measured.**

## Derivation

```
E[action_a] = 10
E[action_b] = 0.97 * 10 + 0.03 * 17 = 10.21
margin      = 0.21                       about 2% of either action's magnitude
```

The smallest change to a **single loss cell** that reverses the recommendation
is the margin divided by that cell's scenario probability, minimised over cells:

```
0.21 / 0.97 = 0.2165        <  declared tolerance 1.0
```

So revising any one loss estimate by a single unit could flip the answer.

```
state certainty = 0.97  >  0.8       ->  state RESOLVED
min perturbation = 0.2165  <  1.0   ->  decision NOT stable
EVPI = 0                             ->  more data about the world would not help
```

## The mirror image of WG-BM-061

| | WG-BM-061 | WG-BM-062 (here) |
|---|---|---|
| state resolved | no (0.34) | **yes (0.97)** |
| decision resolved | **yes** | no |
| what would help | nothing | **better loss estimates** |

Both benchmarks have `EVPI = 0`, and for opposite reasons. There the action was
insensitive to the world; here the world is known and the action is sensitive to
**the loss numbers**, which no amount of observation will pin down.

That is the diagnostic value of separating the two axes. "We are 97% sure what
the fire will do" is a statement about the state, and it says nothing about
whether the recommendation that follows is worth acting on. A system that
reports only the state certainty has published the more comforting of the two
numbers.

## What a system should do here

Report the margin. `decision_margin: 0.21` next to `expected_loss: 10.00` tells
the reader that the recommendation is a coin toss dressed as an optimisation,
and that the productive next step is to re-elicit the loss of `action_b` in the
surprise scenario — not to gather more weather data.

No mutation is claimed for this benchmark: the fragility is a property of the
numbers, not a bug that can be injected.

## Expected

| Quantity | Value |
|---|---|
| expected loss, A / B | 10.00 / 10.21 |
| margin | **0.21** |
| perturbation needed to flip | **0.2165** (tolerance 1.0) |
| state resolved | **true** (0.97) |
| decision stable | **false** |
| EVPI | 0 |
