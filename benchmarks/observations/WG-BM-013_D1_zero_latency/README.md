# WG-BM-013 (D1) — Zero-latency perfect observation

## Scenario

One sensor, reporting every 5 minutes, latency zero, no measurement error. The
truth it measures is the distance from the fire front,
`truth(t) = 1000 - 20 t` metres.

## Derivation

An observation acquired at `t_a` with latency `L` is available at query time `t`
when `t_a + L <= t`. With `L = 0` and a query at an acquisition instant, the
latest available record is the one acquired at that instant:

```
q10:  latest acquisition = 10 min, value = truth(10) = 800 m, staleness 0
q25:  latest acquisition = 25 min, value = truth(25) = 500 m, staleness 0
```

The number of available records is the count of acquisitions at or before the
query: 3 at `t = 10` (0, 5, 10) and 6 at `t = 25` (0, 5, 10, 15, 20, 25).

## Purpose

This is a positive control. It asserts the *absence* of an accidental offset:
no off-by-one in the record index, no half-interval shift, no silent
interpolation. If a system fails here it will fail every other benchmark in the
D family for reasons that have nothing to do with latency, outage or
missingness, and the diagnosis would be confusing without this case to isolate
it.
