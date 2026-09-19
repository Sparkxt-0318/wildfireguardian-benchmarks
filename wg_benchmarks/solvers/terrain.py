"""Terrain preprocessing reference solver.

Conventions (see ``docs/ASSUMPTIONS.md``):

* the grid is row-major with row 0 the **northern** edge; ``x`` increases east,
  ``y`` increases north;
* slope is computed with Horn's 3x3 finite difference, the de-facto GIS
  standard, and reported in degrees from horizontal;
* aspect is the compass bearing of the direction of steepest **descent**,
  degrees clockwise from north, and is ``null`` on a flat cell;
* a cell whose 3x3 neighbourhood contains a missing value yields ``null``.
  Missing elevation is not zero elevation, and the difference is a 100 m cliff.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

from .. import mutations


def _neighbourhood(grid: Sequence[Sequence[Any]], row: int, col: int) -> list[Any] | None:
    values = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            value = grid[row + dr][col + dc]
            if value is None:
                # MUTATION HOOK: silently impute missing terrain as zero.
                if mutations.active("missing_as_zero"):
                    value = 0.0
                else:
                    return None
            values.append(float(value))
    return values


def cell_slope_aspect(
    grid: Sequence[Sequence[Any]], row: int, col: int, dx: float, dy: float
) -> dict:
    """Horn slope/aspect for one interior cell."""
    rows, cols = len(grid), len(grid[0])
    if row <= 0 or col <= 0 or row >= rows - 1 or col >= cols - 1:
        return {"slope_deg": None, "aspect_deg": None, "status": "border"}
    values = _neighbourhood(grid, row, col)
    if values is None:
        return {"slope_deg": None, "aspect_deg": None, "status": "undefined_missing_neighbour"}
    nw, n, ne, w, _c, e, sw, s, se = values
    dzdx = ((ne + 2 * e + se) - (nw + 2 * w + sw)) / (8 * dx)
    dzdy = ((nw + 2 * n + ne) - (sw + 2 * s + se)) / (8 * dy)
    magnitude = math.hypot(dzdx, dzdy)
    slope_deg = math.degrees(math.atan(magnitude))
    if magnitude == 0.0:
        aspect_deg = None
    else:
        aspect_deg = math.degrees(math.atan2(-dzdx, -dzdy)) % 360.0
    return {
        "slope_deg": slope_deg,
        "aspect_deg": aspect_deg,
        "dzdx": dzdx,
        "dzdy": dzdy,
        "status": "ok",
    }


def solve(inputs: dict) -> dict:
    document = inputs["terrain"]
    grid = document["elevation"]
    dx = float(document.get("cell_size_m", 30.0))
    dy = float(document.get("cell_size_m_y", dx))
    rows, cols = len(grid), len(grid[0])

    slope_grid: list[list[Any]] = []
    aspect_grid: list[list[Any]] = []
    for row in range(rows):
        slope_row, aspect_row = [], []
        for col in range(cols):
            cell = cell_slope_aspect(grid, row, col, dx, dy)
            slope_row.append(cell["slope_deg"])
            aspect_row.append(cell["aspect_deg"])
        slope_grid.append(slope_row)
        aspect_grid.append(aspect_row)

    interior = [
        slope_grid[r][c]
        for r in range(1, rows - 1)
        for c in range(1, cols - 1)
    ]
    defined = [v for v in interior if v is not None]

    probes = {}
    for probe in document.get("probe_cells", []):
        cell = cell_slope_aspect(grid, int(probe["row"]), int(probe["col"]), dx, dy)
        probes[str(probe["id"])] = {
            "slope_deg": cell["slope_deg"],
            "aspect_deg": cell["aspect_deg"],
            "status": cell["status"],
        }

    return {
        "rows": rows,
        "cols": cols,
        "cell_size_m": dx,
        "slope_deg_grid": slope_grid,
        "aspect_deg_grid": aspect_grid,
        "interior_cells": len(interior),
        "interior_defined": len(defined),
        "interior_undefined": len(interior) - len(defined),
        "max_slope_deg": max(defined) if defined else None,
        "min_slope_deg": min(defined) if defined else None,
        "flat_interior_cells": sum(1 for v in defined if abs(v) < 1e-12),
        "probes": probes,
    }
