# WG-BM-063 (L5) — Robust action despite poor forecast skill

## Scenario

A poor forecast (declared skill score **0.25**) spreads its weight across four
possible fire behaviours: **0.4 / 0.3 / 0.2 / 0.1.**

| | `omega_1` | `omega_2` | `omega_3` | `omega_4` |
|---|---|---|---|---|
| `stage_at_junction` | **4** | **4** | **5** | **5** |
| `stage_north` | 6 | 9 | 12 | 20 |
| `stage_south` | 20 | 12 | 9 | 6 |

## Derivation

```
E[stage_at_junction] = 1.6 + 1.2 + 1.0 + 0.5 = 4.3
E[stage_north]       = 2.4 + 2.7 + 2.4 + 2.0 = 9.5
E[stage_south]       = 8.0 + 3.6 + 1.8 + 0.6 = 14.0
```

The junction is also the minimum **in every scenario separately**, so

```
clairvoyant = 4.3     EVPI = 0
```

```
largest weight = 0.4  <  0.8          ->  state not resolved
margin = 5.2,  flip needs 5.2/0.4 = 13.0  >>  1.0   ->  decision stable
worst case 5  <=  acceptable loss 8   ->  robust
```

## Skill and value, once more

WG-BM-031 (G4) showed a crude forecast beating an accurate one because it
arrived in time. This shows something stronger: a forecast with a skill score of
0.25 supporting a decision that **perfect skill could not improve**, because
`EVPI = 0`.

The consequence for a forecasting programme is uncomfortable and worth stating
plainly: for a decision of this shape, forecast improvement has **no** decision
value, at any level of investment. The useful question is not "how good is the
forecast?" but "which decisions does its quality actually gate?" — and answering
that requires the loss structure, which is not part of any forecast evaluation.

Read together, the three cases separate what is usually one undifferentiated
worry:

| | uncertain about | fixable by |
|---|---|---|
| WG-BM-061 | which scenario | nothing — the action is already optimal |
| WG-BM-062 | the loss numbers | re-elicitation, not observation |
| WG-BM-063 (here) | the forecast | nothing — skill does not gate this decision |

## Expected

| Quantity | Value |
|---|---|
| expected loss, junction / north / south | 4.3 / 9.5 / 14.0 |
| optimal in every scenario | `stage_at_junction` |
| EVPI | **0** |
| forecast skill score | 0.25 |
| state resolved / decision resolved | **false** / **true** |
