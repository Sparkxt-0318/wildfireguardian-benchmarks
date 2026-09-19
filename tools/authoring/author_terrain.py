"""Author the A family: terrain preprocessing benchmarks (WG-BM-001..004)."""

from __future__ import annotations

import math

from common import report, write_benchmark

SCRIPT = "author_terrain.py"
CELL = 30.0

# Analytic constants, derived by hand (see each README) and written here as the
# closed form rather than as a rounded literal.
PLANE_GRADIENT = 0.1                      # dz/dx = dz/dy = 0.1 m/m
PLANE_SLOPE_DEG = math.degrees(math.atan(math.hypot(PLANE_GRADIENT, PLANE_GRADIENT)))
PLANE_ASPECT_DEG = 225.0                  # descends to the south-west
RIDGE_GRADIENT = 0.2                      # 6 m drop per 30 m cell
RIDGE_SLOPE_DEG = math.degrees(math.atan(RIDGE_GRADIENT))

TOLERANCE = {"default": 1.0e-09}


def tilted_plane(rows: int, cols: int, base: float = 100.0) -> list[list[float]]:
    """z = base + 0.1 x + 0.1 y, with row 0 the northern edge."""
    return [
        [base + PLANE_GRADIENT * CELL * col + PLANE_GRADIENT * CELL * (rows - 1 - row)
         for col in range(cols)]
        for row in range(rows)
    ]


def main() -> None:
    written = []

    # ------------------------------------------------------------------ A1
    written.append(write_benchmark(
        directory="benchmarks/terrain/WG-BM-001_A1_flat_plane",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-001",
            "label": "A1",
            "title": "Flat plane has zero slope and undefined aspect",
            "category": "terrain",
            "difficulty": "basic",
            "purpose": "Pin the degenerate case: on perfectly flat terrain slope is exactly zero "
                       "and aspect is undefined, not an arbitrary compass bearing.",
            "solver": "terrain.horn_slope_aspect",
            "assumptions": {
                "slope_method": "horn_3x3",
                "aspect_convention": "compass bearing of steepest descent, degrees clockwise from north",
                "aspect_on_flat": "null",
                "row_zero_is": "north",
            },
            "expected_behavior": {
                "max_slope_deg": 0.0,
                "flat_interior_cells": 9,
                "interior_undefined": 0,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["spurious_slope_on_flat_terrain", "fabricated_aspect"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "A system that reports aspect 0 (north) on flat ground will silently bias "
                     "any downstream aspect-dependent fire-spread adjustment.",
        },
        inputs={
            "terrain": {
                "description": "5x5 grid, every cell at 100.0 m, 30 m cells.",
                "cell_size_m": CELL,
                "elevation": [[100.0] * 5 for _ in range(5)],
                "probe_cells": [
                    {"id": "centre", "row": 2, "col": 2},
                    {"id": "off_centre", "row": 1, "col": 3},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-001",
            "source": "hand_derivation",
            "derivation": (
                "Every Horn finite difference on a constant field is a difference of equal sums, "
                "so dz/dx = dz/dy = 0 exactly and slope = atan(0) = 0. The aspect of a zero "
                "gradient is not defined: atan2(0, 0) is a convention, not a measurement, so the "
                "expected value is null. The 5x5 grid has 3x3 = 9 interior cells; border cells "
                "have no complete neighbourhood and are reported as null with status 'border'."
            ),
            "results": {
                "rows": 5,
                "cols": 5,
                "interior_cells": 9,
                "interior_defined": 9,
                "interior_undefined": 0,
                "flat_interior_cells": 9,
                "max_slope_deg": 0.0,
                "min_slope_deg": 0.0,
                "probes": {
                    "centre": {"slope_deg": 0.0, "aspect_deg": None, "status": "ok"},
                    "off_centre": {"slope_deg": 0.0, "aspect_deg": None, "status": "ok"},
                },
            },
            "invariants": [
                {
                    "expression": "all(v == 0.0 for row in r['slope_deg_grid'] for v in row if v is not None)",
                    "description": "no cell anywhere on the grid reports a non-zero slope",
                },
                {
                    "expression": "all(v is None for row in r['aspect_deg_grid'] for v in row)",
                    "description": "aspect is undefined everywhere on a flat plane",
                },
            ],
        },
        readme="""
# WG-BM-001 (A1) — Flat plane

## Scenario

A 5x5 raster of 30 m cells, every cell at exactly 100.0 m.

```
100 100 100 100 100
100 100 100 100 100
100 100 100 100 100
100 100 100 100 100
100 100 100 100 100
```

## Derivation

Horn's 3x3 estimator for the east-west gradient is

```
dz/dx = ((z_NE + 2 z_E + z_SE) - (z_NW + 2 z_W + z_SW)) / (8 dx)
```

On a constant field both bracketed sums equal `4 z`, so `dz/dx = 0` exactly, and
by the same argument `dz/dy = 0`. Therefore

```
slope = atan(sqrt(0^2 + 0^2)) = 0
```

Aspect is the bearing of the steepest descent direction. When the gradient
vanishes there is no such direction: `atan2(0, 0)` returns `0` in IEEE
arithmetic, but that `0` is an artefact of the function, not a north-facing
slope. The expected aspect is therefore **null**.

## Expected

| Quantity | Value |
|---|---|
| slope, every interior cell | `0.0` deg |
| aspect, every cell | `null` |
| interior cells | 9 |
| interior cells with undefined slope | 0 |

## What this catches

* An implementation that reports aspect `0` (due north) on flat ground. Every
  downstream aspect-dependent adjustment — fire-spread rate, insolation, fuel
  moisture — then receives a systematic, silent bias on exactly the terrain
  where the correction should be absent.
* An implementation that adds numerical noise (for example by normalising a
  zero-length gradient vector) and reports slopes of order `1e-8` degrees as if
  they were real.

## How to break it deliberately

Replace the undefined-aspect rule with `atan2(-dzdx, -dzdy)` unconditionally and
the benchmark fails immediately on the `aspect_deg_grid` invariant.
""",
    ))

    # ------------------------------------------------------------------ A2
    written.append(write_benchmark(
        directory="benchmarks/terrain/WG-BM-002_A2_tilted_plane",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-002",
            "label": "A2",
            "title": "Tilted plane reproduces the analytic slope and aspect",
            "category": "terrain",
            "difficulty": "basic",
            "purpose": "Check slope magnitude and aspect convention against a plane whose gradient "
                       "is known in closed form, including the sign convention of the aspect.",
            "solver": "terrain.horn_slope_aspect",
            "assumptions": {
                "slope_method": "horn_3x3",
                "aspect_convention": "compass bearing of steepest descent, degrees clockwise from north",
                "x_increases": "east",
                "y_increases": "north",
                "row_zero_is": "north",
            },
            "expected_behavior": {
                "max_slope_deg": PLANE_SLOPE_DEG,
                "min_slope_deg": PLANE_SLOPE_DEG,
                "interior_undefined": 0,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["slope_magnitude_error", "aspect_convention_error", "axis_transposition"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "Horn's estimator is exact on a plane, so there is no discretisation error to "
                     "hide behind: any discrepancy is a bug in the convention, not in the method.",
        },
        inputs={
            "terrain": {
                "description": "5x5 grid on the plane z = 100 + 0.1 x + 0.1 y, 30 m cells, row 0 north.",
                "cell_size_m": CELL,
                "elevation": tilted_plane(5, 5),
                "probe_cells": [
                    {"id": "centre", "row": 2, "col": 2},
                    {"id": "north_east_interior", "row": 1, "col": 3},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-002",
            "source": "closed_form",
            "derivation": (
                "The surface is the plane z = 100 + 0.1 x + 0.1 y with x east and y north, so "
                "dz/dx = dz/dy = 0.1 everywhere, and Horn's estimator is exact on a plane. "
                "slope = atan(sqrt(0.1^2 + 0.1^2)) = atan(0.1414213562373095) = 8.0490... degrees. "
                "The steepest descent direction is -grad z = (-0.1, -0.1), pointing south-west, "
                "whose compass bearing is atan2(-0.1, -0.1) = -135 deg = 225 deg clockwise from "
                "north. Every interior cell has the same answer because the surface is a plane."
            ),
            "results": {
                "rows": 5,
                "cols": 5,
                "interior_cells": 9,
                "interior_defined": 9,
                "interior_undefined": 0,
                "flat_interior_cells": 0,
                "max_slope_deg": PLANE_SLOPE_DEG,
                "min_slope_deg": PLANE_SLOPE_DEG,
                "probes": {
                    "centre": {
                        "slope_deg": PLANE_SLOPE_DEG,
                        "aspect_deg": PLANE_ASPECT_DEG,
                        "status": "ok",
                    },
                    "north_east_interior": {
                        "slope_deg": PLANE_SLOPE_DEG,
                        "aspect_deg": PLANE_ASPECT_DEG,
                        "status": "ok",
                    },
                },
            },
            "invariants": [
                {
                    "expression": "max(abs(v - r['probes']['centre']['slope_deg']) for row in r['slope_deg_grid'] for v in row if v is not None) < 1e-9",
                    "description": "slope is constant over the whole plane",
                },
                {
                    "expression": "all(abs(v - 225.0) < 1e-9 for row in r['aspect_deg_grid'] for v in row if v is not None)",
                    "description": "aspect is 225 degrees (south-west) everywhere the gradient is defined",
                },
            ],
        },
        readme=f"""
# WG-BM-002 (A2) — Tilted plane

## Scenario

A 5x5 raster of 30 m cells sampling the plane

```
z(x, y) = 100 + 0.1 x + 0.1 y        x east, y north, metres
```

Row 0 is the northern edge, so `y = (rows - 1 - row) * 30`.

```
112 115 118 121 124      <- north
109 112 115 118 121
106 109 112 115 118
103 106 109 112 115
100 103 106 109 112      <- south
```

## Derivation

The gradient of a plane is constant: `dz/dx = dz/dy = 0.1`. Horn's estimator
reproduces the gradient of a plane exactly (each weighted sum telescopes), so

```
slope = atan(sqrt(0.1^2 + 0.1^2))
      = atan(0.1414213562373095)
      = {PLANE_SLOPE_DEG:.10f} degrees
```

Aspect is the compass bearing of steepest *descent*. The descent direction is
`-grad z = (-0.1, -0.1)`: one unit west and one unit south. Measuring clockwise
from north,

```
aspect = atan2(-dz/dx, -dz/dy) mod 360 = atan2(-0.1, -0.1) mod 360 = 225 degrees
```

which is south-west, as it must be for a surface rising to the north-east.

## Expected

| Quantity | Value |
|---|---|
| slope, every interior cell | `{PLANE_SLOPE_DEG:.10f}` deg |
| aspect, every interior cell | `225.0` deg |
| variation across the grid | 0 |

## What this catches

* **Axis transposition.** Swapping the row and column axes leaves the slope
  unchanged here (the gradient is symmetric) but a grid that is not symmetric
  would move; the companion invariant on the aspect catches the sign errors.
* **Aspect measured from the wrong reference.** Reporting the bearing of
  steepest *ascent* gives 45 deg instead of 225 deg; reporting mathematical
  convention (counter-clockwise from east) gives 135 deg. Both fail.
* **Row-order confusion.** Treating row 0 as the southern edge flips the sign of
  `dz/dy` and yields 315 deg.
""",
    ))

    # ------------------------------------------------------------------ A3
    ridge = [[100.0 - 6.0 * abs(col - 3) for col in range(7)] for _ in range(5)]
    written.append(write_benchmark(
        directory="benchmarks/terrain/WG-BM-003_A3_ridge",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-003",
            "label": "A3",
            "title": "Ridge crest: directional transition and the zero-slope artefact",
            "category": "terrain",
            "difficulty": "intermediate",
            "purpose": "Verify behaviour at a directional transition: the two flanks must face "
                       "opposite ways, and the crest cell must be recognised as an artefact of the "
                       "finite difference rather than as flat ground.",
            "solver": "terrain.horn_slope_aspect",
            "assumptions": {
                "slope_method": "horn_3x3",
                "aspect_convention": "compass bearing of steepest descent, degrees clockwise from north",
                "crest_slope_is_an_artefact": True,
            },
            "expected_behavior": {
                "max_slope_deg": RIDGE_SLOPE_DEG,
                "flat_interior_cells": 3,
                "interior_cells": 15,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["crest_artefact_misread_as_flat", "aspect_discontinuity_smoothing"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "This benchmark does NOT assert that the crest slope is correct terrain "
                     "science. It asserts that a centred difference produces exactly three "
                     "zero-slope cells at the crest, and that a preprocessing stage must not "
                     "report them as genuine flat ground.",
        },
        inputs={
            "terrain": {
                "description": "5x7 grid, north-south ridge at column 3, z = 100 - 6*|col-3|, 30 m cells.",
                "cell_size_m": CELL,
                "elevation": ridge,
                "probe_cells": [
                    {"id": "crest", "row": 2, "col": 3},
                    {"id": "west_flank", "row": 2, "col": 2},
                    {"id": "east_flank", "row": 2, "col": 4},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-003",
            "source": "hand_derivation",
            "derivation": (
                "Elevation depends only on the column: z = 100 - 6|col - 3|, so dz/dy = 0 "
                "everywhere and the problem is one dimensional. On the west flank (col 2) the "
                "east neighbours are at 100 and the west neighbours at 88, giving "
                "dz/dx = (4*100 - 4*88) / (8*30) = 48/240 = +0.2; the surface rises to the east, "
                "so it descends to the west and the aspect is 270 deg. On the east flank (col 4) "
                "the same computation gives dz/dx = (4*88 - 4*100)/240 = -0.2 and an aspect of "
                "90 deg. slope = atan(0.2) = 11.3099... degrees on both flanks. At the crest "
                "(col 3) the neighbours on both sides are at 94, so the centred difference is "
                "exactly zero and the cell reports slope 0 with undefined aspect. That is a "
                "known artefact of centred differencing at a ridge line, not flat ground: the "
                "interior rows are 1..3, so exactly 3 cells show it."
            ),
            "results": {
                "rows": 5,
                "cols": 7,
                "interior_cells": 15,
                "interior_defined": 15,
                "interior_undefined": 0,
                "flat_interior_cells": 3,
                "max_slope_deg": RIDGE_SLOPE_DEG,
                "min_slope_deg": 0.0,
                "probes": {
                    "crest": {"slope_deg": 0.0, "aspect_deg": None, "status": "ok"},
                    "west_flank": {
                        "slope_deg": RIDGE_SLOPE_DEG,
                        "aspect_deg": 270.0,
                        "status": "ok",
                    },
                    "east_flank": {
                        "slope_deg": RIDGE_SLOPE_DEG,
                        "aspect_deg": 90.0,
                        "status": "ok",
                    },
                },
            },
            "invariants": [
                {
                    "expression": "all(r['aspect_deg_grid'][row][3] is None for row in (1, 2, 3))",
                    "description": "every interior crest cell has undefined aspect",
                },
                {
                    "expression": "all(r['aspect_deg_grid'][row][col] == 270.0 for row in (1, 2, 3) for col in (1, 2))",
                    "description": "the whole west flank faces west",
                },
                {
                    "expression": "all(r['aspect_deg_grid'][row][col] == 90.0 for row in (1, 2, 3) for col in (4, 5))",
                    "description": "the whole east flank faces east",
                },
            ],
        },
        readme=f"""
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
slope  = atan(0.2) = {RIDGE_SLOPE_DEG:.10f} degrees
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
| slope, both flanks | `{RIDGE_SLOPE_DEG:.10f}` deg |
| aspect, west flank | `270.0` deg |
| aspect, east flank | `90.0` deg |
| slope, crest | `0.0` deg (artefact) |
| zero-slope interior cells | exactly 3 |
""",
    ))

    # ------------------------------------------------------------------ A4
    holed = tilted_plane(7, 7)
    holed[3][3] = None
    written.append(write_benchmark(
        directory="benchmarks/terrain/WG-BM-004_A4_missing_cells",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-004",
            "label": "A4",
            "title": "Missing terrain stays missing and does not become zero elevation",
            "category": "terrain",
            "difficulty": "adversarial",
            "purpose": "A single no-data cell must propagate as undefined slope over its 3x3 "
                       "neighbourhood and nowhere else. Imputing zero elevation manufactures a "
                       "100 m cliff.",
            "solver": "terrain.horn_slope_aspect",
            "assumptions": {
                "slope_method": "horn_3x3",
                "missing_propagates": True,
                "missing_is_not_zero": True,
            },
            "expected_behavior": {
                "interior_defined": 16,
                "interior_undefined": 9,
                "max_slope_deg": PLANE_SLOPE_DEG,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["missing_treated_as_zero", "missing_propagation_scope"],
            "mutations_expected_to_fail": ["missing_as_zero"],
            "hand_checkable": True,
        },
        inputs={
            "terrain": {
                "description": "7x7 grid on the plane z = 100 + 0.1x + 0.1y with a single no-data "
                               "cell at (row 3, col 3).",
                "cell_size_m": CELL,
                "elevation": holed,
                "probe_cells": [
                    {"id": "hole", "row": 3, "col": 3},
                    {"id": "adjacent_to_hole", "row": 2, "col": 2},
                    {"id": "far_from_hole", "row": 1, "col": 1},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-004",
            "source": "hand_derivation",
            "derivation": (
                "The surface is the same plane as WG-BM-002, so every cell with a complete "
                "neighbourhood has slope atan(sqrt(0.02)) = 8.0490... deg and aspect 225 deg. "
                "One cell, (3, 3), is no-data. A Horn estimate needs the full 3x3 neighbourhood, "
                "so exactly the cells within Chebyshev distance 1 of (3, 3) are undefined: rows "
                "2..4 by columns 2..4, which is 9 cells, all of them interior. The 7x7 grid has "
                "5x5 = 25 interior cells, leaving 25 - 9 = 16 defined. Imputing the hole as 0.0 m "
                "instead would create a 112 m step against a 30 m cell and report slopes above "
                "20 degrees on a plane that is inclined at 8 degrees."
            ),
            "results": {
                "rows": 7,
                "cols": 7,
                "interior_cells": 25,
                "interior_defined": 16,
                "interior_undefined": 9,
                "flat_interior_cells": 0,
                "max_slope_deg": PLANE_SLOPE_DEG,
                "min_slope_deg": PLANE_SLOPE_DEG,
                "probes": {
                    "hole": {
                        "slope_deg": None,
                        "aspect_deg": None,
                        "status": "undefined_missing_neighbour",
                    },
                    "adjacent_to_hole": {
                        "slope_deg": None,
                        "aspect_deg": None,
                        "status": "undefined_missing_neighbour",
                    },
                    "far_from_hole": {
                        "slope_deg": PLANE_SLOPE_DEG,
                        "aspect_deg": PLANE_ASPECT_DEG,
                        "status": "ok",
                    },
                },
            },
            "invariants": [
                {
                    "expression": "all(r['slope_deg_grid'][row][col] is None for row in (2, 3, 4) for col in (2, 3, 4))",
                    "description": "the 3x3 neighbourhood of the hole is undefined",
                },
                {
                    "expression": "r['max_slope_deg'] < 9.0",
                    "description": "no manufactured cliff: every defined slope is the plane's 8.05 degrees",
                },
                {
                    "expression": "r['interior_defined'] == 16",
                    "description": "missingness does not spread beyond one cell ring",
                },
            ],
        },
        readme=f"""
# WG-BM-004 (A4) — Missing cells

## Scenario

The plane of WG-BM-002 (`z = 100 + 0.1x + 0.1y`, slope {PLANE_SLOPE_DEG:.4f} deg,
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
`{PLANE_SLOPE_DEG:.10f}` deg and aspect `225` deg.

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
| max slope over defined cells | `{PLANE_SLOPE_DEG:.10f}` deg |
| slope at the hole and its ring | `null` |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
