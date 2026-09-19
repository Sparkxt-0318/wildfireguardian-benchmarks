# WG-BM-016 (D4) — Fire-correlated sensor failure

## Scenario

Five field sensors report burn state (`0` unburnt, `1` burning). Each is
destroyed at the moment the fire reaches it:

| Sensor | Fire arrives |
|---|---|
| s1 | 20 min |
| s2 | 30 min |
| s3 | 40 min |
| s4 | 90 min |
| s5 | 120 min |

The question is asked at **t = 60 min**.

## Derivation

At `t = 60`, sensors s1, s2 and s3 are silent and s4, s5 are reporting. Every
sensor that is still reporting reports `0`, because a sensor that could report
`1` has already been destroyed. Therefore:

```
mean over reporting sensors  = (0 + 0) / 2            = 0.0
true fraction burnt          = 3 / 5                  = 0.6
naive bias                   = 0.0 - 0.6              = -0.6
```

The complete-case estimate is **maximally wrong**, and it is wrong using data
that contain no contradictory observation whatsoever. There is nothing in the
reporting record to notice.

An estimator that treats *silence after the modelled hazard arrival* as evidence
of burning recovers the truth exactly:

```
(3 * 1 + 2 * 0) / 5 = 0.6
```

## Why this is the MNAR case and not a nuisance

Missingness here is caused by the variable being measured. That is the textbook
definition of **missing not at random**, and it has three consequences that a
wildfire system must handle explicitly:

1. **No imputation from observed data can fix it.** Mean imputation, regression
   imputation and multiple imputation all condition on the observed
   distribution, which contains no burning sensors. Every one of them imputes
   towards zero.
2. **The bias grows as the situation worsens.** The more of the area that burns,
   the more sensors are destroyed and the more confidently the surviving network
   reports calm. The estimator is least reliable exactly when it matters most.
3. **Silence is a measurement.** The dropout pattern carries the information the
   destroyed sensors would have reported. Discarding "sensors with no data"
   discards the signal.

The mutation `ignore_informative_missingness` performs the complete-case
analysis and reports it as the answer; this benchmark is its declared detector.

## A caveat on the correction

The dropout-aware estimate here is exact *because the scenario stipulates that
dropout is caused by hazard arrival and by nothing else*. Real sensor networks
also lose nodes to battery failure, communications outage and vandalism. The
correct general treatment is a model of the dropout mechanism, not the
substitution used here. This benchmark pins the sign and the magnitude of the
naive error; it does not endorse a universal correction, and that limitation is
recorded in `reports/KNOWN_GAPS.md`.
