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
