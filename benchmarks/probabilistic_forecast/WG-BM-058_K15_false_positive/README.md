# WG-BM-058 (K15) — False positive

## Scenario

The WG-BM-057 detector, applied where fire is **rare**.

```
prior: P(fire) = 0.02

P(detect | fire)    = 0.70
P(detect | no fire) = 0.05
```

**It reports a detection.** Three responses are available:

| | fire | no fire |
|---|---|---|
| `monitor` | 200 | 0 |
| `divert_traffic` | 30 | 6 |
| `full_evacuation` | 0 | 40 |

## Derivation

```
P(detect) = 0.02 * 0.70 + 0.98 * 0.05 = 0.014 + 0.049 = 0.063
P(fire | detect) = 0.014 / 0.063 = 2/9 = 0.2222222222
```

The detection multiplies the fire probability **elevenfold** — and leaves more
than three quarters of the mass on there being no fire, because at a 2% base rate
the detector generates 49 false alarms for every 14 true ones.

At `p = 2/9`:

```
monitor          200 * 2/9            = 44.44
divert_traffic   6 * 7/9 + 30 * 2/9   = 11.33      <- correct
full_evacuation  40 * 7/9             = 31.11
```

Under the prior the response was `monitor` (expected loss 4), so the detection
does change the action, and `EVSI = 4 - 1.914 = 2.086`.

**Treating the detection as certainty** sets `p = 1`, where the losses are 200,
30 and 0, so the response escalates to a full evacuation. Evaluated at the true
posterior that costs **31.11 against 11.33** — nearly three times the loss, and
the excess is borne as an unnecessary evacuation 78% of the time.

## The escalation ladder

Three actions give two switch points, not one threshold:

```
p < 3/88 = 0.0341        monitor
0.0341 < p < 0.53125     divert_traffic
p > 0.53125              full_evacuation
```

A detection at a 2% base rate lands in the middle band. That is the operational
content of the benchmark: the correct response to a credible detection is
usually the **proportionate** one, and a system that maps `detection -> maximum
response` has no middle band to land in.

## Why base-rate neglect is the standing risk here

Detection pipelines are tuned on their conditional performance — sensitivity and
specificity — and those two numbers do not determine the posterior. The same
detector that leaves `P(fire) = 0.22` here leaves `P(fire) = 0.78` in WG-BM-057,
where the base rate is 0.2. **Nothing about the detector changed.** Any system
that reports "fire detected" without the prevailing base rate has discarded the
input that does most of the work.

Repeated unnecessary escalation also has a cost this suite does not model:
the next warning is believed less. That is a real dynamic and there is no
benchmark for it; it is recorded in `reports/KNOWN_GAPS.md`.

## Expected

| Quantity | Value |
|---|---|
| `P(fire \| detect)` | **2/9 = 0.2222** |
| action | `divert_traffic` |
| action if the detection is treated as certain | `full_evacuation` |
| loss of that escalation, at the true posterior | 31.11 vs 11.33 |
| EVSI | 2.086 |
