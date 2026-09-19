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
