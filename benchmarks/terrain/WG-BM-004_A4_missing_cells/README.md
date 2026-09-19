# WG-BM-004 (A4) — Missing cells

## Scenario

The plane of WG-BM-002 (`z = 100 + 0.1x + 0.1y`, slope 8.0495 deg,
aspect 225 deg) sampled on a 7x7 grid of 30 m cells, with **one cell marked
no-data** at row 3, column 3.

## Derivation

Horn's estimator consumes the full 3x3 neighbourhood of a cell. A cell is
therefore computable if and only if none of its eight neighbours, nor itself, is
no-data. The cells failing that test are exactly those within Chebyshev distance
1 of (3, 3):

```
rows 2..4 x columns 2..4  =  9 cells
```

All nine are interior cells. A 7x7 grid has `5 x 5 = 25` interior cells, so

```
interior defined   = 25 - 9 = 16
interior undefined = 9
```

and every one of the 16 defined cells lies on the plane, with slope
`8.0494669755` deg and aspect `225` deg.

## Why this is adversarial

The failure this catches is not exotic; it is the single most common data bug in
raster pipelines. A no-data sentinel (`-9999`, `NaN`, or an unfilled buffer)
reaches an arithmetic path that treats it as a number:

* **Imputed as 0.0.** The hole becomes a 112 m pit in a 30 m cell. The eight
  surrounding cells report slopes above 20 degrees on terrain inclined at 8.
  Every slope-dependent rate-of-spread model then predicts a local acceleration
  that does not exist, at a location chosen by where the sensor happened to
  fail.
* **Imputed as -9999.** Same failure, three orders of magnitude worse, and
  usually noticed. The zero case is the dangerous one precisely because the
  resulting map still looks plausible.
* **Silently interpolated.** Defensible for visualisation, indefensible for a
  decision product unless the interpolation is recorded. This benchmark requires
  `status: undefined_missing_neighbour`, so an implementation that fills the gap
  must at least say so.

The mutation `missing_as_zero` injects exactly the first bug; this benchmark is
its declared detector.

## Expected

| Quantity | Value |
|---|---|
| interior cells | 25 |
| interior cells defined | 16 |
| interior cells undefined | 9 |
| max slope over defined cells | `8.0494669755` deg |
| slope at the hole and its ring | `null` |
