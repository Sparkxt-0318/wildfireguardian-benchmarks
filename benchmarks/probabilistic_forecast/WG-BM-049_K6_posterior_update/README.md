# WG-BM-049 (K6) — Posterior update

## Scenario

Will the fire reach the settlement?

```
prior:  P(H_reaches) = 0.1        P(H_misses) = 0.9
```

A satellite pass reports a thermal anomaly on the intervening ridge:

```
P(anomaly | reaches) = 0.9        P(anomaly | misses) = 0.2
```

| | fire reaches | fire misses |
|---|---|---|
| `evacuate` | 0 | 5 |
| `stay` | 20 | 0 |

## Derivation

**Threshold from the loss matrix.**

```
p* = L_conservative / (L_conservative + L_failure) = 5 / (5 + 20) = 0.2
```

**Prior decision.** `E[stay] = 0.1 * 20 = 2` against `E[evacuate] = 0.9 * 5 = 4.5`
→ **stay**.

**Bayes.**

```
P(anomaly) = 0.1 * 0.9 + 0.9 * 0.2 = 0.09 + 0.18 = 0.27
P(reaches | anomaly) = 0.09 / 0.27 = 1/3 = 0.3333...        > p*  ->  evacuate

P(no anomaly) = 0.01 + 0.72 = 0.73
P(reaches | no anomaly) = 0.01 / 0.73 = 0.01370...          < p*  ->  stay
```

**Value.**

```
EVSI = 2 - (0.27 * 10/3 + 0.73 * 0.27397...) = 2 - (0.9 + 0.2) = 0.9
EVPI = 2 - 0 = 2
mutual information = 0.1448297915 bits
```

## The chain this pins

```
observation  ->  likelihood  ->  posterior  ->  expected loss  ->  action
```

Every arrow is somewhere a system can break, and the four failure points are
different bugs with different signatures:

* **the likelihood is not used** — the posterior equals the prior (1/3 becomes
  0.1) and the action never changes;
* **the posterior is computed and then not used** — the reported posterior is
  correct and the action is still `stay`;
* **the normalisation is skipped** — `0.1 * 0.9 = 0.09` is reported as the
  posterior, which is below `p*`, so the action is wrong while the number looks
  plausible;
* **the threshold is not derived from the loss** — at 1/3 a half-probability
  rule also says stay.

The first two are injected as `ignore_observation_likelihood` and
`posterior_replaced_by_prior`, and this benchmark is the declared detector for
both. They are distinguishable in the result document: the first changes the
reported posterior, the second does not.

## Expected

| Quantity | Value |
|---|---|
| `p*` | 0.2 |
| `P(reaches \| anomaly)` | **1/3** |
| `P(reaches \| no anomaly)` | 0.013699 |
| prior action → posterior action | `stay` → **`evacuate`** |
| EVSI / EVPI | 0.9 / 2.0 |
