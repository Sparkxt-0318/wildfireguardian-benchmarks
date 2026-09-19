# WG-BM-042 (J2) — Observation changes protectability

## Scenario

The same two worlds as WG-BM-041, with the robust action removed: sheltering is
no longer survivable, and the two evacuation directions are mutually exclusive.

| | `w_north` | `w_south` |
|---|---|---|
| `evacuate_north` | 0 | **90** |
| `evacuate_south` | **95** | 0 |
| `shelter` | 50 | 50 |

Acceptable loss threshold: **10**. Decision deadline: minute 10.
A perfect recon flight reports at **minute 5**.

## Derivation

```
E[evacuate_north] = 0.5*0  + 0.5*90 = 45     <- best fixed action
E[evacuate_south] = 0.5*95 + 0.5*0  = 47.5
E[shelter]        = 50

worst case of the best fixed action = 90     >> threshold 10
```

**No action is acceptable across both worlds**, so on the prior alone the
resident is *not* robustly protectable.

```
clairvoyant expected loss = 0.5*0 + 0.5*0 = 0
EVPI = 45 - 0 = 45
```

The recon flight arrives 5 minutes before the deadline and separates the worlds,
so the informed policy evacuates north on "north" and south on "south":

```
expected loss with the observation = 0
value of the observation           = 45 = EVPI      (all of it)
worst case with the observation    = 0   <= threshold 10
```

**The observation converts a resident who is not robustly protectable into one
who is.** That, and not the reduction in expected loss, is the operationally
important statement.

## Contrast with WG-BM-041

| | WG-BM-041 (J1) | WG-BM-042 (J2) |
|---|---|---|
| uncertainty | identical | identical |
| robust action exists on the prior | **yes** | **no** |
| EVPI | 0 | 45 |
| worth tasking a recon flight | no | **yes** |

The uncertainty is the same in both. What differs is whether the action set
contains something acceptable everywhere. This is why "how uncertain are we?" is
the wrong question to ask when deciding whether to gather information, and
"would the answer change what we do?" is the right one.

## Expected

| Quantity | Value |
|---|---|
| best fixed action | `evacuate_north`, expected loss 45 |
| worst case without information | 90 (not protectable) |
| EVPI | 45 |
| realisable value of the observation | 45 |
| worst case with information | 0 (protectable) |
