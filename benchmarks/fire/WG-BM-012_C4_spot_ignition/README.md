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
