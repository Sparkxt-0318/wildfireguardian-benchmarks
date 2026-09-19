# WG-BM-014 (D2) — Fixed 10-minute latency

## Scenario

The same 5-minute reporting sensor as WG-BM-013, but every acquisition takes
10 minutes to become usable: downlink, geolocation, cloud/smoke screening,
ingest.

```
available(t) = { records with t_acquisition + 10 <= t }
```

## Derivation

| Query time | Latest usable acquisition | Value | Contemporaneous truth | Error |
|---|---|---|---|---|
| 5 min | none (0 is available from 10) | `null` | 900 m | — |
| 25 min | 15 min | 700 m | 500 m | **+200 m** |
| 40 min | 30 min | 400 m | 200 m | **+200 m** |

At `t = 25` the acquisitions at 20 and 25 minutes exist in the archive and are
**not available**. A retrospective evaluation that loads the whole archive and
filters on `acquisition_time <= t` will use them, and will report a system that
is 200 m better informed than any real-time deployment can be.

Note the sign. The available observation always says the fire is *further away*
than it is, by `latency x rate of approach = 10 min x 20 m/min = 200 m`. Latency
does not add noise; it adds a systematic optimistic bias. Averaged over many
cases it does not cancel.

## What this catches

The mutation `observation_future_leak` sets the latency to zero while leaving
everything else intact — the one-character change of filtering on
`acquisition_time <= t` instead of `acquisition_time + latency <= t`. This
benchmark is its declared detector, and it is the reason the D family exists.

Leakage of this kind is not usually a deliberate choice. It appears when:

* an archive is joined on acquisition timestamp because that is the column that
  exists;
* a "latest observation" view is materialised without a validity interval;
* a nowcast product is back-filled into the archive under its valid time rather
  than its issue time.

Each of these produces a system that scores well offline and degrades
inexplicably in deployment.

## Expected

| Quantity | Value |
|---|---|
| latest usable acquisition at t = 25 | 15 min |
| value at t = 25 | 700 m |
| error against truth at t = 25 | +200 m |
| available records at t = 5 | 0 |
