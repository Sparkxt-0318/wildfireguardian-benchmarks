# WG-BM-031 (G4) — Crude but timely

## Scenario

The WG-BM-030 decision — evacuate (cost 10) versus shelter in place (0 if the
fire misses, 100 if it hits), prior 50/50, deadline **minute 20** — with **two**
forecasts available:

| Forecast | Issued | Spatial error | Skill | Resolves hit/miss? |
|---|---|---|---|---|
| `forecast_accurate_late` | minute 30 | 10 m | 0.98 | yes, but too late |
| `forecast_crude_early` | minute 5 | 800 m | 0.40 | **yes, in time** |

The crude forecast is 800 m out on the front position and still gets the binary
question right: *does the fire reach the town?* That is the only question the
decision actually asks.

## Derivation

```
use_crude_early:     evacuate on "hit", shelter on "miss"
                     expected loss = 0.5 * 10 + 0.5 * 0 = 5
                     value         = 10 - 5 = +5

use_accurate_late:   arrives after the deadline -> shelters by default
                     expected loss = 0.5 * 100 + 0.5 * 0 = 50
                     value         = 10 - 50 = -40

EVPI = 10 - 5 = 5        realisable value = 5   (captured entirely by the crude forecast)
```

| Ranking | 1st | 2nd | 3rd |
|---|---|---|---|
| by **value** | `use_crude_early` (+5) | `baseline_trigger` (0) | `use_accurate_late` (-40) |
| by **skill** | `use_accurate_late` (0.98) | `use_crude_early` (0.40) | `baseline_trigger` |

**The rankings are exactly reversed.**

## Why the crude forecast captures the full EVPI

Because the decision is binary and the crude forecast resolves the binary
question. Spatial precision beyond "does it reach the town" is, for this
decision, unused information. The extra 790 m of accuracy in the late forecast
buys nothing at all, and the 10 minutes of extra lead time in the crude one buy
everything.

This generalises: the value of a forecast is bounded by the resolution of the
decision it informs. A binary decision can extract at most the value of a binary
signal. Increasing forecast resolution past the decision's own granularity has
zero marginal value, which is the same phenomenon WG-BM-028 shows from the other
direction.

## What this means for a forecasting programme

The relevant design question is not "how accurate can we get?" but "what is the
most useful thing we can say **before minute 20**?" Those are different
optimisation problems, and this pair of benchmarks (G3, G4) exists so that a
system cannot answer the first while claiming to have answered the second.

Two mutations are detected here: `skill_implies_value`, which picks
`use_accurate_late` as the recommendation, and `forecast_always_trusted`, which
makes the late forecast usable and erases the distinction.
