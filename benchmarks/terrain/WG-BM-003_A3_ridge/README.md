# WG-BM-003 (A3) — Ridge

## Scenario

A 5x7 raster of 30 m cells holding a north-south ridge:

```
z(col) = 100 - 6 |col - 3|
```

```
 82  88  94 100  94  88  82
 82  88  94 100  94  88  82
 82  88  94 100  94  88  82      <- row 2, the probed row
 82  88  94 100  94  88  82
 82  88  94 100  94  88  82
```

## Derivation

Elevation is independent of the row, so `dz/dy = 0` everywhere and the case is
one dimensional.

**West flank, column 2.** East neighbours are all at 100, west neighbours all at
88:

```
dz/dx = (4 * 100 - 4 * 88) / (8 * 30) = 48 / 240 = +0.2
slope  = atan(0.2) = 11.3099324740 degrees
aspect = bearing of -grad = due west = 270 degrees
```

**East flank, column 4.** By symmetry `dz/dx = -0.2`, the same slope, and an
aspect of 90 degrees.

**Crest, column 3.** Both neighbouring columns are at 94, so the centred
difference is *exactly zero* and the reported slope is 0 with undefined aspect.

## The point of this benchmark

The crest result is **an artefact of centred differencing, not a measurement**.
A 3x3 centred estimator cannot see a ridge line: at the crest it samples a
symmetric pair and concludes the surface is level. The benchmark pins the
artefact rather than pretending it away, and asserts two things a wildfire
preprocessing stage must get right:

1. The flanks are assigned **opposite** aspects with no smoothing across the
   crest. An implementation that low-pass filters the elevation, or that
   computes aspect from a smoothed gradient, will bleed the 270 deg flank into
   the 90 deg flank and produce a band of physically meaningless intermediate
   bearings along the ridge.
2. Exactly **three** interior cells (rows 1..3 of column 3) report zero slope.
   If a downstream stage treats "slope = 0" as "flat, no upslope run", it will
   do so precisely along the ridge line, which is where upslope runs from both
   sides converge — the single most consequential place to be wrong.

## Expected

| Quantity | Value |
|---|---|
| slope, both flanks | `11.3099324740` deg |
| aspect, west flank | `270.0` deg |
| aspect, east flank | `90.0` deg |
| slope, crest | `0.0` deg (artefact) |
| zero-slope interior cells | exactly 3 |
