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
      = 8.0494669755 degrees
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
| slope, every interior cell | `8.0494669755` deg |
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
