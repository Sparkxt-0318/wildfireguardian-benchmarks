"""Author the C family: fire / hazard benchmarks (WG-BM-009..012)."""

from __future__ import annotations

import math

from common import report, write_benchmark

SCRIPT = "author_fire.py"
TOLERANCE = {"default": 1.0e-09}

# C1 constants
RADIAL_RATE = 10.0
DIAGONAL_ARRIVAL = math.hypot(100.0, 100.0) / RADIAL_RATE   # 14.1421... min

# C2 constants: head 20, back 4 => a = 12, c = 8; flank semi-axis b = 6.
HEAD, BACK, FLANK_B = 20.0, 4.0, 6.0
A_RATE, C_DRIFT = (HEAD + BACK) / 2.0, (HEAD - BACK) / 2.0     # 12, 8
CROSSWIND_ARRIVAL = A_RATE * 200.0 / (FLANK_B * math.sqrt(A_RATE**2 - C_DRIFT**2))  # 20*sqrt(5)


def main() -> None:
    written = []

    # ------------------------------------------------------------------ C1
    written.append(write_benchmark(
        directory="benchmarks/fire/WG-BM-009_C1_constant_radial_arrival",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-009",
            "label": "C1",
            "title": "Constant radial spread reproduces T(x) = |x - x0| / r",
            "category": "fire",
            "difficulty": "basic",
            "purpose": "Fix the simplest possible hazard field so that arrival times and their "
                       "ordering can be checked exactly, including the tie between equidistant "
                       "points.",
            "solver": "fire.analytic_arrival",
            "assumptions": {
                "spread": "isotropic constant rate",
                "ignition_time_min": 0,
                "terrain_effect": False,
                "wind_effect": False,
            },
            "expected_behavior": {
                "first_reached": "p_origin",
                "last_reached": "p_far",
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["arrival_time_scaling_error", "arrival_ordering_error"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
        },
        inputs={
            "fire": {
                "description": "Isotropic spread at 10 m/min from the origin, ignited at t = 0.",
                "model": "radial",
                "origin": {"x": 0.0, "y": 0.0},
                "rate_m_per_min": RADIAL_RATE,
                "probe_points": [
                    {"id": "p_origin", "x": 0.0, "y": 0.0},
                    {"id": "p_east", "x": 100.0, "y": 0.0},
                    {"id": "p_north", "x": 0.0, "y": 100.0},
                    {"id": "p_ne", "x": 100.0, "y": 100.0},
                    {"id": "p_far", "x": 300.0, "y": 0.0},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-009",
            "source": "closed_form",
            "derivation": (
                "T(x) = |x - x0| / r with x0 = (0, 0) and r = 10 m/min. "
                "p_origin: 0/10 = 0. p_east: 100/10 = 10. p_north: 100/10 = 10. "
                "p_ne: sqrt(100^2 + 100^2)/10 = 141.4213562373095/10 = 14.14213562373095. "
                "p_far: 300/10 = 30. The two points at 100 m arrive simultaneously; the ordering "
                "is reported with ties broken by identifier so that the expected sequence is "
                "deterministic."
            ),
            "results": {
                "model": "radial",
                "arrival_min": {
                    "p_origin": 0.0,
                    "p_east": 10.0,
                    "p_north": 10.0,
                    "p_ne": DIAGONAL_ARRIVAL,
                    "p_far": 30.0,
                },
                "arrival_order": ["p_origin", "p_east", "p_north", "p_ne", "p_far"],
                "first_reached": "p_origin",
                "last_reached": "p_far",
            },
            "invariants": [
                {
                    "expression": "abs(r['arrival_min']['p_east'] - r['arrival_min']['p_north']) < 1e-12",
                    "description": "equidistant points arrive at the same time under isotropic spread",
                },
                {
                    "expression": "abs(r['arrival_min']['p_far'] - 3 * r['arrival_min']['p_east']) < 1e-12",
                    "description": "arrival time is linear in distance",
                },
            ],
        },
        readme=f"""
# WG-BM-009 (C1) — Constant radial arrival

## Scenario

A single ignition at the origin at `t = 0`, spreading isotropically at
`r = 10 m/min`. Arrival time is

```
T(x) = |x - x0| / r
```

## Derivation

| Point | Coordinates | Distance | Arrival |
|---|---|---|---|
| `p_origin` | (0, 0) | 0 m | 0 min |
| `p_east` | (100, 0) | 100 m | 10 min |
| `p_north` | (0, 100) | 100 m | 10 min |
| `p_ne` | (100, 100) | `100 sqrt(2)` = 141.4214 m | `{DIAGONAL_ARRIVAL:.10f}` min |
| `p_far` | (300, 0) | 300 m | 30 min |

`p_east` and `p_north` are equidistant and therefore arrive **simultaneously**.
The reported ordering breaks the tie by identifier so that the expected sequence
is deterministic rather than dependent on dictionary iteration order.

## What this catches

* A factor-of-two or unit error in the rate (minutes vs seconds, metres vs feet)
  shows up immediately as a scaled arrival field.
* An implementation whose grid discretisation makes the diagonal arrive at
  `200/10 = 20` min instead of `14.14` min — the classic 4-connected raster
  spread artefact, where fire can only travel along rows and columns. That error
  is a 41% overestimate of diagonal arrival time and it biases every
  diagonally-oriented escape route optimistically.
* An ordering bug in which strictly later points are reported as reached first.

## What this deliberately does not test

Nothing about realistic fire behaviour. There is no wind, no fuel, no terrain,
no ignition delay. A model that passes this has demonstrated that its arrival
field is a metric, and nothing else. Wind enters in WG-BM-010, fuel in
WG-BM-011, multiple sources in WG-BM-012.
""",
    ))

    # ------------------------------------------------------------------ C2
    written.append(write_benchmark(
        directory="benchmarks/fire/WG-BM-010_C2_constant_wind_bias",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-010",
            "label": "C2",
            "title": "Constant wind produces a known anisotropic arrival field",
            "category": "fire",
            "difficulty": "intermediate",
            "purpose": "Pin head, back and flank arrival times for a shifted-ellipse front so "
                       "that anisotropy cannot be quietly averaged away.",
            "solver": "fire.analytic_arrival",
            "assumptions": {
                "front_shape": "shifted ellipse (Richards / Anderson elliptical model)",
                "wind_bearing_is": "direction the wind blows towards, degrees clockwise from north",
                "head_rate_m_per_min": HEAD,
                "back_rate_m_per_min": BACK,
            },
            "expected_behavior": {
                "arrival_min": {
                    "p_downwind": 10.0,
                    "p_upwind": 50.0,
                },
            },
            "tolerance": {"default": 1.0e-09},
            "exactness": "exact_analytic",
            "detects": ["anisotropy_ignored", "wind_direction_sign_error"],
            "mutations_expected_to_fail": ["isotropic_fire"],
            "hand_checkable": True,
        },
        inputs={
            "fire": {
                "description": "Constant wind towards the east. Head 20 m/min, back 4 m/min, "
                               "across-wind semi-axis growth 6 m/min.",
                "model": "elliptical_wind",
                "origin": {"x": 0.0, "y": 0.0},
                "head_rate_m_per_min": HEAD,
                "back_rate_m_per_min": BACK,
                "flank_semi_axis_m_per_min": FLANK_B,
                "wind_bearing_deg": 90.0,
                "probe_points": [
                    {"id": "p_downwind", "x": 200.0, "y": 0.0},
                    {"id": "p_upwind", "x": -200.0, "y": 0.0},
                    {"id": "p_crosswind", "x": 0.0, "y": 200.0},
                    {"id": "p_front_flank", "x": 80.0, "y": 60.0},
                    {"id": "p_front_back", "x": -40.0, "y": 0.0},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-010",
            "source": "closed_form",
            "derivation": (
                "The front at time t is the ellipse centred at (c t, 0) with semi-axes a t along "
                "the wind and b t across it, where a = (head + back)/2 = 12, c = (head - back)/2 "
                "= 8 and b = 6. Directly downwind the front advances at a + c = 20 m/min, so "
                "200 m arrives at 10 min. Directly upwind it backs at a - c = 4 m/min, so 200 m "
                "upwind arrives at 50 min. Across the wind, setting p = 0 in the front equation "
                "gives t = a q / (b sqrt(a^2 - c^2)) = 12 * 200 / (6 * sqrt(80)) = 20 sqrt(5) = "
                "44.7213595499958 min. Two further probes are read directly off the t = 10 "
                "ellipse, which is centred at (80, 0) with semi-axes 120 and 60: the point "
                "(80, 60) is its northern extremity and (-40, 0) its western extremity, so both "
                "arrive at exactly 10 min. Note that (-40, 0) also follows from the backing rate: "
                "40 / 4 = 10."
            ),
            "results": {
                "model": "elliptical_wind",
                "arrival_min": {
                    "p_downwind": 10.0,
                    "p_upwind": 50.0,
                    "p_crosswind": CROSSWIND_ARRIVAL,
                    "p_front_flank": 10.0,
                    "p_front_back": 10.0,
                },
                "arrival_order": [
                    "p_downwind",
                    "p_front_back",
                    "p_front_flank",
                    "p_crosswind",
                    "p_upwind",
                ],
                "first_reached": "p_downwind",
                "last_reached": "p_upwind",
            },
            "invariants": [
                {
                    "expression": "abs(r['arrival_min']['p_upwind'] / r['arrival_min']['p_downwind'] - 5.0) < 1e-9",
                    "description": "head-to-back anisotropy ratio is exactly 20/4 = 5",
                },
                {
                    "expression": "r['arrival_min']['p_downwind'] < r['arrival_min']['p_crosswind'] < r['arrival_min']['p_upwind']",
                    "description": "head arrives first, flank second, back last",
                },
            ],
        },
        readme=f"""
# WG-BM-010 (C2) — Constant wind bias

## Scenario

A single ignition at the origin under a steady wind blowing **towards the east**
(bearing 090). The front is the standard shifted ellipse:

* head (downwind) rate: **20 m/min**
* backing (upwind) rate: **4 m/min**
* across-wind semi-axis growth: **6 m/min**

## Derivation

Write `a = (head + back)/2 = 12` for the semi-major growth rate and
`c = (head - back)/2 = 8` for the downwind drift of the ellipse centre. At time
`t` the front is the ellipse

```
centre (c t, 0) = (8t, 0),   semi-axes  a t = 12t  along wind,  b t = 6t  across
```

**Downwind.** Along the wind axis the front advances at `a + c = 20 m/min`, so
`(200, 0)` is reached at `200 / 20 = 10 min`.

**Upwind.** The front backs at `a - c = 4 m/min`, so `(-200, 0)` is reached at
`200 / 4 = 50 min`.

**Across wind.** Setting `p = 0` in the front equation
`((p - ct)/a)^2 + (q/b)^2 = t^2` gives

```
t = a q / (b sqrt(a^2 - c^2)) = 12 * 200 / (6 * sqrt(80)) = 20 sqrt(5) = {CROSSWIND_ARRIVAL:.10f} min
```

**Two points read straight off the t = 10 front.** At `t = 10` the ellipse is
centred at `(80, 0)` with semi-axes 120 and 60. Its northern extremity is
`(80, 60)` and its western extremity is `(80 - 120, 0) = (-40, 0)`. Both
therefore arrive at exactly **10 min** — and the second agrees with the backing
rate, `40 / 4 = 10`, which is a useful independent check on the algebra.

## Expected

| Point | Arrival |
|---|---|
| `p_downwind` (200, 0) | 10 min |
| `p_front_flank` (80, 60) | 10 min |
| `p_front_back` (-40, 0) | 10 min |
| `p_crosswind` (0, 200) | `{CROSSWIND_ARRIVAL:.6f}` min |
| `p_upwind` (-200, 0) | 50 min |

Head-to-back anisotropy ratio: exactly **5**.

## What this catches

* **Isotropic collapse.** Replacing the wind-driven field with a circular front
  at the mean rate (12 m/min) puts the downwind point at 16.7 min instead of 10
  — a 67% late arrival estimate on the one bearing where being late is fatal.
  This is the `isotropic_fire` mutation and this benchmark is its detector.
* **Wind direction sign errors.** Swapping "blows from" for "blows towards"
  exchanges the 10 min and 50 min answers. A 40-minute error on a corridor
  decision is not recoverable downstream.
* **Anisotropy applied to the wrong axis.** A 90-degree bearing error puts the
  head where the flank should be.
""",
    ))

    # ------------------------------------------------------------------ C3
    written.append(write_benchmark(
        directory="benchmarks/fire/WG-BM-011_C3_fuel_discontinuity",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-011",
            "label": "C3",
            "title": "Rate of spread changes at a known fuel boundary",
            "category": "fire",
            "difficulty": "intermediate",
            "purpose": "A sharp fuel break must produce a kink in the arrival-time profile, not a "
                       "smooth average.",
            "solver": "fire.analytic_arrival",
            "assumptions": {
                "transect_is_1d": True,
                "boundary_at_m": 100,
                "grass_rate_m_per_min": 10,
                "timber_rate_m_per_min": 2,
                "no_transition_zone": True,
            },
            "expected_behavior": {
                "arrival_min": {"d100": 10.0, "d150": 35.0},
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["heterogeneity_averaged", "fuel_boundary_smoothed"],
            "mutations_expected_to_fail": ["uniform_fuel"],
            "hand_checkable": True,
        },
        inputs={
            "fire": {
                "description": "1-D transect: fast grass to 100 m, slow timber litter beyond.",
                "model": "piecewise_fuel_1d",
                "segments": [
                    {"from_m": 0.0, "to_m": 100.0, "rate_m_per_min": 10.0, "fuel": "grass"},
                    {"from_m": 100.0, "to_m": 1000.0, "rate_m_per_min": 2.0, "fuel": "timber_litter"},
                ],
                "probe_points": [
                    {"id": "d050", "distance_m": 50.0},
                    {"id": "d100", "distance_m": 100.0},
                    {"id": "d150", "distance_m": 150.0},
                    {"id": "d200", "distance_m": 200.0},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-011",
            "source": "closed_form",
            "derivation": (
                "Arrival is the cumulative sum of segment length over segment rate. "
                "d050: 50/10 = 5 min. d100: 100/10 = 10 min, exactly at the boundary. "
                "d150: 10 + 50/2 = 35 min. d200: 10 + 100/2 = 60 min. The profile has a kink at "
                "100 m where the slope of arrival-versus-distance jumps from 0.1 min/m to "
                "0.5 min/m. Averaging the two fuels over the 1000 m transect gives a single rate "
                "of (10*100 + 2*900)/1000 = 2.8 m/min, which would put d100 at 35.7 min instead "
                "of 10 min."
            ),
            "results": {
                "model": "piecewise_fuel_1d",
                "arrival_min": {"d050": 5.0, "d100": 10.0, "d150": 35.0, "d200": 60.0},
                "arrival_order": ["d050", "d100", "d150", "d200"],
                "first_reached": "d050",
                "last_reached": "d200",
            },
            "invariants": [
                {
                    "expression": "abs((r['arrival_min']['d100'] - r['arrival_min']['d050']) / 50 - 0.1) < 1e-12",
                    "description": "slope of the arrival profile is 0.1 min/m inside the grass",
                },
                {
                    "expression": "abs((r['arrival_min']['d200'] - r['arrival_min']['d150']) / 50 - 0.5) < 1e-12",
                    "description": "slope of the arrival profile is 0.5 min/m inside the timber",
                },
            ],
        },
        readme="""
# WG-BM-011 (C3) — Fuel discontinuity

## Scenario

A one-dimensional transect from the ignition point. Grass burns to 100 m at
10 m/min; beyond 100 m the fuel is timber litter and spread drops to 2 m/min.

```
0 m ------- grass, 10 m/min ------- 100 m ------- timber litter, 2 m/min ------- 1000 m
```

## Derivation

Arrival is the cumulative sum of `length / rate`:

```
T(50)  = 50/10                = 5 min
T(100) = 100/10               = 10 min          <- the boundary
T(150) = 100/10 + 50/2        = 10 + 25 = 35 min
T(200) = 100/10 + 100/2       = 10 + 50 = 60 min
```

The arrival profile is piecewise linear with a **kink** at 100 m: its slope
jumps from `0.1 min/m` to `0.5 min/m`.

## What this catches

Averaging the fuel map is a seductive simplification: one rate is cheaper to
calibrate, cheaper to store, and produces a smoother, better-looking map. Over
this transect the length-weighted mean rate is

```
(10 * 100 + 2 * 900) / 1000 = 2.8 m/min
```

which puts the 100 m boundary at `35.7 min` instead of `10 min`. Anyone
evacuating along the first 100 m has been given a 25-minute margin that does not
exist. The error has the worst possible sign: it is optimistic precisely in the
fast-burning fuel where the margin matters.

The mutation `uniform_fuel` injects exactly that averaging, and this benchmark
is its declared detector.

## Expected

| Distance | Arrival |
|---|---|
| 50 m | 5 min |
| 100 m | 10 min |
| 150 m | 35 min |
| 200 m | 60 min |
""",
    ))

    # ------------------------------------------------------------------ C4
    written.append(write_benchmark(
        directory="benchmarks/fire/WG-BM-012_C4_spot_ignition",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-012",
            "label": "C4",
            "title": "Spot ignition creates a disconnected threatened area",
            "category": "fire",
            "difficulty": "adversarial",
            "purpose": "A spot fire 2 km ahead of the main front threatens an area that is not "
                       "connected to the main perimeter. Area-connectivity assumptions break.",
            "solver": "fire.analytic_arrival",
            "assumptions": {
                "sources_independent": True,
                "spot_ignition_time_min": 30,
                "no_merging_before_query_time": True,
            },
            "expected_behavior": {
                "burned_components": 2,
                "burned_cells": 14,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_enumeration",
            "detects": ["spotting_ignored", "perimeter_connectivity_assumed"],
            "mutations_expected_to_fail": ["single_ignition_only"],
            "hand_checkable": True,
        },
        inputs={
            "fire": {
                "description": "Main fire at the origin from t = 0; ember spot fire 2 km east "
                               "ignites at t = 30. Both spread isotropically at 5 m/min.",
                "model": "multi_ignition",
                "sources": [
                    {"id": "main", "x": 0.0, "y": 0.0, "rate_m_per_min": 5.0, "ignition_time_min": 0.0},
                    {"id": "spot", "x": 2000.0, "y": 0.0, "rate_m_per_min": 5.0, "ignition_time_min": 30.0},
                ],
                "probe_points": [
                    {"id": "near_main", "x": 100.0, "y": 0.0},
                    {"id": "between", "x": 1000.0, "y": 0.0},
                    {"id": "near_spot", "x": 2000.0, "y": 100.0},
                    {"id": "ahead_of_spot", "x": 2500.0, "y": 0.0},
                ],
                "burned_area_query": {
                    "at_time_min": 40.0,
                    "cell_size_m": 100.0,
                    "x_min": -450.0,
                    "x_max": 2550.0,
                    "y_min": -450.0,
                    "y_max": 450.0,
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-012",
            "source": "hand_derivation",
            "derivation": (
                "Arrival is the minimum over sources of ignition_time + distance/rate. "
                "near_main (100 m from the main fire): 0 + 100/5 = 20 min. "
                "between (1000 m from main, 1000 m from spot): min(200, 30 + 200) = 200 min. "
                "near_spot (2002.5 m from main, 100 m from spot): min(400.5, 30 + 20) = 50 min. "
                "ahead_of_spot (2500 m from main, 500 m from spot): min(500, 30 + 100) = 130 min. "
                "At t = 40 the main fire has radius 40*5 = 200 m and the spot, ignited 10 minutes "
                "earlier, has radius 50 m. The query grid has 100 m cells whose centres sit on "
                "multiples of 100 m, with the spot exactly on a cell centre. Cells within 200 m "
                "of the origin are (0,0), the four at 100 m, the four at 141 m and the four at "
                "200 m: 13 cells. Within 50 m of the spot there is exactly 1 cell, its own. Total "
                "14 burned cells in 2 connected components of sizes 13 and 1, separated by "
                "1750 m of unburnt ground."
            ),
            "results": {
                "model": "multi_ignition",
                "arrival_min": {
                    "near_main": 20.0,
                    "between": 200.0,
                    "near_spot": 50.0,
                    "ahead_of_spot": 130.0,
                },
                "arrival_order": ["near_main", "near_spot", "ahead_of_spot", "between"],
                "first_reached": "near_main",
                "last_reached": "between",
                "burned_cells": 14,
                "burned_components": 2,
                "burned_component_sizes": [13, 1],
            },
            "invariants": [
                {
                    "expression": "r['arrival_min']['near_spot'] < r['arrival_min']['between']",
                    "description": "ground beyond the spot burns before ground between the fires",
                },
                {
                    "expression": "r['burned_components'] == 2",
                    "description": "the threatened area is genuinely disconnected at the query time",
                },
            ],
        },
        readme="""
# WG-BM-012 (C4) — Spot ignition

## Scenario

* Main fire ignites at the origin at `t = 0`, spreading isotropically at 5 m/min.
* Embers start a **spot fire 2 km east** at `t = 30`, spreading at the same rate.

## Derivation

Arrival is the minimum over sources of `ignition_time + distance / rate`.

| Point | From main | From spot | Arrival |
|---|---|---|---|
| `near_main` (100, 0) | `100/5 = 20` | `30 + 1900/5 = 410` | **20 min** |
| `between` (1000, 0) | `1000/5 = 200` | `30 + 1000/5 = 230` | **200 min** |
| `near_spot` (2000, 100) | `2002.5/5 = 400.5` | `30 + 100/5 = 50` | **50 min** |
| `ahead_of_spot` (2500, 0) | `2500/5 = 500` | `30 + 500/5 = 130` | **130 min** |

The ordering is the point of the table: ground **2.5 km away** burns at 130 min
while ground **1 km away** burns at 200 min. Arrival time is not monotone in
distance from the main fire.

### Burned area at t = 40

The main fire has radius `40 * 5 = 200 m`. The spot, ignited 10 minutes earlier,
has radius `10 * 5 = 50 m`. On the 100 m query grid (cell centres on multiples
of 100 m, with the spot exactly on a centre):

* within 200 m of the origin: `(0,0)`, four cells at 100 m, four at
  `141 m`, four at 200 m — **13 cells**;
* within 50 m of the spot: its own cell only — **1 cell**.

Total **14 burned cells in 2 connected components**, sizes 13 and 1, separated
by 1750 m of unburnt ground.

## What this catches

* **Single-ignition models.** The `single_ignition_only` mutation drops the spot
  fire, reporting `ahead_of_spot` as safe until 500 min when it actually burns at
  130 min — a 370 minute error, and this benchmark is its declared detector.
* **Connectivity assumptions.** Any code that assumes the burned region is
  simply connected (flood fill from one seed, single-perimeter polygon, "distance
  to the fire front" as a scalar field around one curve) is wrong here at
  `t = 40`. Evacuation routing that treats the area between the two fires as
  "behind the front, therefore safe" sends people into a corridor that is about
  to be closed from both ends.
* **Threat ranking by distance to the nearest perimeter.** `between` is closer to
  the main fire than `ahead_of_spot`, and burns 70 minutes later.
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
