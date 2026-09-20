# WG-BM-056 (K13) — Fire-correlated missingness

## Scenario

A remote weather station reports every ten minutes. Its report is **twelve times
more likely to go missing when the fire is close** — mains power first, then the
radio path.

```
prior: P(H_dangerous) = 0.05

P(missing | dangerous) = 0.60
P(missing | safe)      = 0.05
```

**This cycle, no report arrived.**

## Derivation

The missingness indicator is an observation like any other:

```
P(missing) = 0.05 * 0.60 + 0.95 * 0.05 = 0.03 + 0.0475 = 0.0775
P(dangerous | missing) = 0.03 / 0.0775 = 12/31 = 0.3870967742
```

The belief moves from **0.05 to 0.387** on the strength of a report that never
arrived. In evidence terms:

```
log2(0.60 / 0.05) = 3.584963 bits
```

— more evidence than many positive detections carry.

The other branch is mild reassurance:
`P(dangerous | received) = 0.02 / 0.9225 = 0.021680`.

With `p* = 0.1`:

| | posterior | action |
|---|---|---|
| prior | 0.050 | `proceed` |
| report received | 0.022 | `proceed` |
| **report missing** | **0.387** | **`divert`** |

```
EVSI = 4.5 - (0.0775 * 6.12903 + 0.9225 * 1.95122) = 4.5 - 2.275 = 2.225
```

Under an **MCAR** assumption the missing report carries nothing, the belief stays
at 0.05, and the system **proceeds into the hazard**.

## Relation to WG-BM-016

WG-BM-016 (D4) shows the same mechanism as an **estimation** bias: averaging the
surviving sensors gives 0.0 against a truth of 0.6. This benchmark shows it as a
**decision** error, and adds the thing D4 could not: the exact posterior, and
therefore the exact amount of evidence that silence carries.

The two together make the operational point. A monitoring system that displays
"3 of 8 stations reporting" as a data-quality warning has the sign backwards:
the five silent stations are the most informative thing on the screen.

## What the benchmark does not claim

That `P(missing | dangerous) = 0.6` is knowable. It is stipulated here. In a
real network the missingness mechanism has to be estimated, and it is
confounded with ordinary outages — which is the gap WG-BM-016's README records
and this benchmark does not close.

## Expected

| Quantity | Value |
|---|---|
| `P(dangerous \| missing)` | **12/31 = 0.3871** |
| evidence in the silence | 3.5850 bits |
| action, correct / MCAR | `divert` / **`proceed`** |
| EVSI | 2.225 |
