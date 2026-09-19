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
t = a q / (b sqrt(a^2 - c^2)) = 12 * 200 / (6 * sqrt(80)) = 20 sqrt(5) = 44.7213595500 min
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
| `p_crosswind` (0, 200) | `44.721360` min |
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
