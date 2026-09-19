# WG-BM-043 (J3) — Observation arrives too late

## Scenario

**Identical to WG-BM-042 in every respect except one**: the recon flight reports
at **minute 15** instead of minute 5. The decision deadline is still minute 10.

| | `w_north` | `w_south` |
|---|---|---|
| `evacuate_north` | 0 | 90 |
| `evacuate_south` | 95 | 0 |
| `shelter` | 50 | 50 |

## Derivation

The decision problem is unchanged, so:

```
clairvoyant expected loss = 0
best fixed action         = evacuate_north, expected loss 45
EVPI                      = 45          <- exactly as in WG-BM-042
```

But the observation can no longer influence the action. A decision maker who
waits for it has, at minute 10, not evacuated — which is the shelter outcome:

```
expected loss, wait_for_recon = 0.5 * 50 + 0.5 * 50 = 50
expected loss, act_on_prior   = 45
value of waiting              = 45 - 50 = -5
realisable value of information = 0
```

In the realised world (`w_north`) acting on the prior happens to be exactly
right and loses 0, while waiting loses 50.

The worst case under the waiting policy is 50, still outside the acceptable
threshold of 10: **the late observation does not make the resident
protectable.**

## The three-way comparison

| | J1 (WG-BM-041) | J2 (WG-BM-042) | J3 (WG-BM-043) |
|---|---|---|---|
| robust action on the prior | yes | no | no |
| observation available before deadline | yes | yes | **no** |
| EVPI | 0 | 45 | **45** |
| realisable value of the observation | 0 | **45** | **0** |
| protectable at the end | yes | yes | **no** |

J1 and J3 both have zero realisable value, for opposite reasons: in J1 there is
nothing worth knowing, in J3 there is a great deal worth knowing and no way to
know it in time. A system that reports only "value of information = 0" for both
has collapsed two situations that demand completely different responses — accept
the robust action in J1, and change the observing system, the deadline, or the
action set in J3.

## The design consequence

EVPI is a property of the decision problem. Realisable value is a property of
the decision problem **and** the observing system's latency. A sensing
investment case built on EVPI alone will fund instruments whose data arrive
after every deadline they were bought to inform.

The corresponding engineering question is not "how accurate can this sensor be?"
but "what is the latest moment at which its output can still change an action,
and does it report before then?" — the same question WG-BM-030 (G3) asks of
forecasts.

The `forecast_always_trusted` mutation removes the timeliness check, making the
late observation usable and its value +45; this benchmark is one of its
declared detectors.

## Expected

| Quantity | Value |
|---|---|
| EVPI | 45 |
| realisable value of information | **0** |
| value of waiting for the recon | **-5** |
| worst case when waiting | 50 (threshold 10) |
| recommended policy | `act_on_prior` |
