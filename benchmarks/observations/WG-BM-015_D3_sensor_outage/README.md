# WG-BM-015 (D3) — Sensor outage

## Scenario

A sensor reports every 5 minutes, goes silent between 20 and 40 minutes, and
resumes at 45. Latency is zero. The declared freshness requirement is 5 minutes:
an observation older than that is not a current observation.

## Derivation

| Query | Latest acquisition | Staleness | Reported value | Status |
|---|---|---|---|---|
| t = 15 | 15 | 0 min | 700 m | current |
| t = 30 | 15 | **15 min** | `null` | **stale** |
| t = 50 | 50 | 0 min | 0 m | current |

At `t = 30` the last known value, 700 m, is kept in a separate field. A caller
may ask for it, but must ask for it by name — it is never returned as if it were
a current reading. The contemporaneous truth at `t = 30` is 400 m, so the stale
value is **300 m optimistic**.

## Two failure modes, both detected here

**Imputation as zero.** `missing_as_zero` replaces the unknown with `0.0`. In
this scenario the quantity is distance from the fire front, so zero means *the
fire is here*. The imputed value is not merely wrong, it is the most alarming
possible value, and a system that panics on sensor outages is a system whose
alarms get switched off. (Reverse the variable — say, fuel moisture — and the
same bug becomes silently reassuring instead.) The general point is that the
numeric consequence of imputing zero depends on the variable's semantics, which
is exactly why the imputation cannot be done generically in a data layer.

**Silent carry-forward.** `silent_carry_forward` returns 700 m with
`stale: false`. This is the more dangerous bug, because the output is
*plausible*: it is a real measurement, it was correct 15 minutes ago, and
nothing downstream can distinguish it from a fresh one. Every consumer then
treats a 15-minute-old belief as current. Carrying a value forward is sometimes
the right operational choice; doing it without marking the staleness never is.

## Expected

| Quantity | Value |
|---|---|
| value at t = 30 | `null` |
| last known value at t = 30 | 700 m |
| staleness at t = 30 | 15 min |
| status at t = 30 | `stale` |
