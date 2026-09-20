# WG-BM-055 (K12) — Duplicate sensor evidence

## Scenario

One ground observer reports the ridge clear. The report reaches the system
**twice** — once over radio, once through the incident log — under two different
record ids and one measurement id.

```
record radio_0471   measurement obs_A
record log_1182     measurement obs_A
```

The two records can only ever agree, because they are the same measurement.

## Derivation

One measurement, likelihood 0.8 / 0.2, prior 0.5:

```
P(dangerous | clear) = 0.5 * 0.2 / (0.5 * 0.2 + 0.5 * 0.8) = 0.2
log-likelihood ratio = log2(0.2 / 0.8) = -2 bits
```

Counting both records as independent observations:

```
0.2 * 0.2 = 0.04   against   0.8 * 0.8 = 0.64
P = 0.04 / 0.68 = 1/17 = 0.0588
log-likelihood ratio = -4 bits          exactly twice, from no extra data
```

With `p* = 0.1`:

```
0.2000 > 0.1  ->  divert     (correct)
0.0588 < 0.1  ->  proceed    (double counting)
```

## The degenerate limit of WG-BM-054

WG-BM-054 has two sensors that agree 92% of the time; here they agree 100% of
the time. The error is the same error, and its magnitude is the same **−2 bits
of fabricated evidence**. That is the useful way to think about correlated
evidence: independence is not a binary property, and duplication is the endpoint
of a continuum rather than a separate bug.

## Why record-level deduplication is the wrong key

The two records differ in every field an ingestion pipeline normally keys on:
different ids, different arrival times, different source systems, different
formats. They are the same *measurement*. Deduplication has to be by what was
measured, when and by whom — which means the measurement identity has to survive
ingestion, and in most pipelines it does not.

Common ways one measurement becomes several records:

* a report relayed through two channels, as here;
* a satellite product reprocessed and re-ingested under a new version;
* a mosaic in which adjacent tiles share a pixel;
* an ensemble whose members share initial conditions;
* a retrospective backfill overlapping a real-time feed.

Each of them inflates confidence in exactly this way, and each is invisible in
the per-record metadata.

## Expected

| Quantity | Value |
|---|---|
| records / independent measurements | 2 / **1** |
| correct posterior | 0.2 |
| posterior counting both | 0.0588 |
| evidence, correct / double-counted | −2 bits / **−4 bits** |
| action, correct / double-counted | `divert` / **`proceed`** |
