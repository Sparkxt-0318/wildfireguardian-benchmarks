# WG-BM-017 (D5) — False negative

## Scenario

Two candidate corridors, one cell each.

| Cell | Truth | Detector output | Detector reliable here? |
|---|---|---|---|
| `c_north` | no fire | no detection | **yes** — clear-air overflight 5 min ago |
| `c_south` | **fire** | no detection | **no** — thick smoke, sensitivity unknown |

Losses: the northern corridor is longer, costing 5 if clear. The southern
corridor is direct, costing 0 if clear. Either costs 100 if it runs through
fire.

**Both cells return "no detection".** The entire difference between the two
decisions comes from whether that non-detection carries information.

## Derivation

**Rule A — no detection means no fire.**

```
believed loss(route_north) = 5     believed loss(route_south) = 0
choose route_south
realised loss = 100                (c_south is on fire)
```

**Rule B — a non-detection is informative only where the detector is reliable.**

```
c_north: reliably clear          -> believed loss(route_north) = 5
c_south: unknown, treat as hazard-> believed loss(route_south) = 100
choose route_north
realised loss = 5                 (c_north really is clear)
```

**Regret of Rule A = 100 - 5 = 95.**

## The distinction this benchmark forces

Rule B is not "assume the worst everywhere". If it were, the northern corridor
would also be treated as hazardous and the system would be paralysed — which is
its own failure mode, and the reason `c_north` is in the scenario at all. Rule B
uses the non-detection at `c_north` and declines to use the one at `c_south`,
because the two observations have different evidential weight despite being the
same value.

That distinction requires the detector's per-cell reliability to be carried
alongside the detection, which many pipelines discard early: a detection product
is reduced to a boolean raster, the smoke/cloud mask is dropped, and by the time
the router sees the data a confirmed clear cell and an unobservable cell are
byte-identical.

The mutation `assume_missing_is_safe` erases that distinction and this benchmark
is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| false negative present | `true` |
| route under Rule A | `route_south`, realised loss 100 |
| route under Rule B | `route_north`, realised loss 5 |
| regret of trusting non-detection | 95 |
