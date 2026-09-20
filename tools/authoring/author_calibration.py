"""Author the M family: forecast calibration (WG-BM-064..066).

Deliberately three benchmarks. This repository does not implement calibration
models; it pins the arithmetic that a calibration claim has to satisfy, and the
one question that matters operationally - does the miscalibration change an
action?
"""

from __future__ import annotations

from common import report, write_benchmark

SCRIPT = "author_calibration.py"
TOL = {"default": 1.0e-12}

# Shared group sizes and event counts. M1 and M2 differ only in the probabilities
# the forecast attaches to the same cases, so every quantity that depends on the
# outcomes alone - base rate, resolution, uncertainty - is identical.
COUNTS = [(100, 0), (200, 40), (100, 50), (300, 240), (100, 100)]
BASE_RATE = sum(k for _, k in COUNTS) / sum(n for n, _ in COUNTS)
RESOLUTION = sum(
    (n / 800) * ((k / n) - BASE_RATE) ** 2 for n, k in COUNTS
)
UNCERTAINTY = BASE_RATE * (1.0 - BASE_RATE)

M1_P = [0.0, 0.2, 0.5, 0.8, 1.0]
M2_P = [0.0, 0.05, 0.5, 0.95, 1.0]
M1_BRIER = sum(
    (n / 800) * ((k / n) * (1 - p) ** 2 + (1 - k / n) * p ** 2)
    for (n, k), p in zip(COUNTS, M1_P)
)
M2_RELIABILITY = sum((n / 800) * (p - k / n) ** 2 for (n, k), p in zip(COUNTS, M2_P))
M2_ECE = sum((n / 800) * abs(p - k / n) for (n, k), p in zip(COUNTS, M2_P))
M2_BRIER = M2_RELIABILITY - RESOLUTION + UNCERTAINTY

HAZARD_DECISION = {
    "loss": {
        "proceed": {"event": 90.0, "no_event": 0.0},
        "divert": {"event": 0.0, "no_event": 10.0},
    }
}


def groups(probabilities: list[float]) -> list[dict]:
    return [
        {"id": f"g{i}", "forecast_probability": p, "n": n, "events": k}
        for i, (p, (n, k)) in enumerate(zip(probabilities, COUNTS), start=1)
    ]


def main() -> None:
    written = []

    # ------------------------------------------------------------------ M1
    written.append(write_benchmark(
        directory="benchmarks/calibration/WG-BM-064_M1_perfectly_calibrated",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-064",
            "label": "M1",
            "title": "A perfectly calibrated binary forecast, with the Murphy decomposition exact",
            "category": "calibration",
            "difficulty": "basic",
            "purpose": "Reference case for the calibration arithmetic: reliability zero, the "
                       "Brier decomposition closing to the last bit, and no decision cost.",
            "solver": "calibration.reliability",
            "assumptions": {
                "groups_are_exhaustive_and_disjoint": True,
                "observed_frequencies_are_exact_counts": True,
                "brier_decomposition": "reliability - resolution + uncertainty",
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "binary_probability",
                "decision_threshold": 0.1,
                "loss_matrix": "proceed 90/0, divert 0/10",
            },
            "expected_behavior": {
                "aggregate_calibration_error": 0.0,
                "reliability": 0.0,
                "perfectly_calibrated": True,
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["calibration_arithmetic_error", "brier_decomposition_error"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "Positive control. If this fails, WG-BM-065 and WG-BM-066 are not "
                     "diagnostic.",
        },
        inputs={
            "calibration": {
                "description": "800 forecast-outcome pairs in five probability groups. In every "
                               "group the event occurred exactly as often as the forecast said it "
                               "would.",
                "groups": groups(M1_P),
                "decision": HAZARD_DECISION,
            }
        },
        expected={
            "benchmark_id": "WG-BM-064",
            "source": "closed_form",
            "derivation": (
                "The five groups are 100 cases at p = 0 with 0 events, 200 at 0.2 with 40, 100 at "
                "0.5 with 50, 300 at 0.8 with 240 and 100 at 1.0 with 100. Every observed "
                "frequency equals its forecast probability, so every calibration error is zero "
                "and both the expected calibration error and the reliability term are zero. "
                "The base rate is 430/800 = 0.5375, so the uncertainty term is "
                "0.5375 * 0.4625 = 0.24859375. The resolution term is the weighted sum of "
                "(observed - base rate) squared: 0.125*0.28890625 + 0.25*0.11390625 + "
                "0.125*0.00140625 + 0.375*0.06890625 + 0.125*0.21390625 = 0.11734375. "
                "By Murphy's decomposition the Brier score is 0 - 0.11734375 + 0.24859375 = "
                "0.13125, and computing it directly group by group gives the same 0.13125, so the "
                "residual is zero. "
                "The loss matrix puts the decision threshold at p* = 10/(10+90) = 0.1. In every "
                "group the action taken from the forecast probability is the same as the action "
                "taken from the observed frequency, so the excess expected loss from "
                "miscalibration is zero - which is what perfect calibration buys."
            ),
            "results": {
                "aggregate_calibration_error": 0.0,
                "reliability": 0.0,
                "resolution": RESOLUTION,
                "uncertainty": UNCERTAINTY,
                "brier_score": M1_BRIER,
                "murphy_residual": 0.0,
                "base_rate": BASE_RATE,
                "perfectly_calibrated": True,
                "decision": {
                    "decision_threshold_probability": 0.1,
                    "groups_with_different_action": [],
                    "total_excess_expected_loss": 0.0,
                    "excess_expected_loss_per_case": 0.0,
                },
            },
            "invariants": [
                {
                    "expression": "abs(r['murphy_residual']) < 1e-12",
                    "description": "Brier = reliability - resolution + uncertainty, exactly",
                },
                {
                    "expression": "all(abs(g['calibration_error']) < 1e-12 for g in r['aggregate']['groups'].values())",
                    "description": "every group is individually calibrated",
                },
                {
                    "expression": "r['decision']['total_excess_expected_loss'] == 0.0",
                    "description": "perfect calibration costs nothing in decisions",
                },
            ],
        },
        readme=f"""
# WG-BM-064 (M1) — Perfectly calibrated binary forecast

## Scenario

800 forecast-outcome pairs in five probability groups.

| forecast `p` | cases | events | observed |
|---|---|---|---|
| 0.0 | 100 | 0 | 0.0 |
| 0.2 | 200 | 40 | 0.2 |
| 0.5 | 100 | 50 | 0.5 |
| 0.8 | 300 | 240 | 0.8 |
| 1.0 | 100 | 100 | 1.0 |

## Derivation

Every observed frequency equals its forecast probability, so

```
expected calibration error = 0        reliability = 0
```

```
base rate    = 430 / 800 = 0.5375
uncertainty  = 0.5375 * 0.4625                      = {UNCERTAINTY}
resolution   = sum w_i (o_i - base)^2               = {RESOLUTION}
Brier        = reliability - resolution + uncertainty = {M1_BRIER}
```

Computing the Brier score directly, group by group, gives the same
{M1_BRIER} — the decomposition residual is **zero**.

## The decision side

With `proceed` costing 90 on an event and `divert` costing 10 otherwise, the
threshold is `p* = 0.1`. In every group the action taken from the forecast
probability matches the action taken from the observed frequency, so the excess
expected loss is **0**.

That is what calibration buys, and it is the only reason this suite measures it:
a calibrated probability can be fed straight into a loss matrix and the
resulting action is the one the data support. An uncalibrated one cannot, which
is WG-BM-065.

## Why a positive control

Reliability, resolution and uncertainty are easy to compute and easy to compute
slightly wrong — a population variance where a weighted one belongs, a base rate
taken over groups rather than cases, a decomposition with the resolution sign
flipped. This benchmark pins all three terms, the identity that links them, and
the case where the answer is the clean zero.

## Expected

| Quantity | Value |
|---|---|
| expected calibration error | **0** |
| reliability | 0 |
| resolution | {RESOLUTION} |
| uncertainty | {UNCERTAINTY} |
| Brier score | {M1_BRIER} |
| decomposition residual | 0 |
| excess expected loss from miscalibration | 0 |
""",
    ))

    # ------------------------------------------------------------------ M2
    written.append(write_benchmark(
        directory="benchmarks/calibration/WG-BM-065_M2_overconfident",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-065",
            "label": "M2",
            "title": "Same classifications, probabilities pushed to the extremes, one action changes",
            "category": "calibration",
            "difficulty": "intermediate",
            "purpose": "Identical cases and outcomes to WG-BM-064 with overconfident "
                       "probabilities. Resolution and uncertainty are unchanged; the whole Brier "
                       "penalty is the reliability term, and one group's action flips.",
            "solver": "calibration.reliability",
            "assumptions": {
                "same_cases_and_outcomes_as_WG_BM_064": True,
                "only_the_stated_probabilities_differ": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "binary_probability",
                "decision_threshold": 0.1,
                "loss_matrix": "proceed 90/0, divert 0/10",
            },
            "expected_behavior": {
                "aggregate_calibration_error": M2_ECE,
                "reliability": M2_RELIABILITY,
                "perfectly_calibrated": False,
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["overconfidence_undetected", "calibration_cost_unmeasured"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "No mutation is claimed: the miscalibration is in the data, not in the "
                     "solver. The benchmark pins what a correct calibration report says about it.",
        },
        inputs={
            "calibration": {
                "description": "The WG-BM-064 cases with the same outcomes and the same ordering, "
                               "but probabilities pushed towards 0 and 1: the 0.2 group is stated "
                               "as 0.05 and the 0.8 group as 0.95.",
                "groups": groups(M2_P),
                "decision": HAZARD_DECISION,
            }
        },
        expected={
            "benchmark_id": "WG-BM-065",
            "source": "closed_form",
            "derivation": (
                "The cases, the outcomes and the group sizes are identical to WG-BM-064; only the "
                "stated probabilities move, from 0.2 to 0.05 and from 0.8 to 0.95. Because "
                "resolution and uncertainty depend on the observed frequencies alone, both are "
                "unchanged at 0.11734375 and 0.24859375, and the entire difference in the Brier "
                "score is the reliability term. "
                "The expected calibration error is 0.25 * 0.15 + 0.375 * 0.15 = 0.0375 + 0.05625 "
                "= 0.09375, and the reliability term is 0.25 * 0.0225 + 0.375 * 0.0225 = "
                "0.0140625, so the Brier score rises from 0.13125 to 0.1453125 - exactly the "
                "reliability term. "
                "At the threshold p* = 0.1 only one group's action changes: the group stated at "
                "0.05 is below the threshold, so the forecast says proceed, while its true event "
                "rate of 0.2 is above it, so the action supported by the data is to divert. "
                "Proceeding costs 0.2 * 90 = 18 per case against 0.8 * 10 = 8 for diverting, an "
                "excess of 10 on each of 200 cases, or 2000 in total and 2.5 per case over the "
                "whole sample. The group stated at 0.95 against a true rate of 0.8 is "
                "miscalibrated by the same 0.15 and costs nothing, because both numbers are on "
                "the same side of the threshold."
            ),
            "results": {
                "aggregate_calibration_error": M2_ECE,
                "reliability": M2_RELIABILITY,
                "resolution": RESOLUTION,
                "uncertainty": UNCERTAINTY,
                "brier_score": M2_BRIER,
                "murphy_residual": 0.0,
                "base_rate": BASE_RATE,
                "perfectly_calibrated": False,
                "decision": {
                    "decision_threshold_probability": 0.1,
                    "groups_with_different_action": ["p=0.05"],
                    "total_excess_expected_loss": 2000.0,
                    "excess_expected_loss_per_case": 2.5,
                },
            },
            "invariants": [
                {
                    "expression": "abs(r['resolution'] - 0.11734375) < 1e-12 and abs(r['uncertainty'] - 0.24859375) < 1e-12",
                    "description": "resolution and uncertainty are unchanged from WG-BM-064",
                },
                {
                    "expression": "abs(r['brier_score'] - 0.13125 - r['reliability']) < 1e-12",
                    "description": "the entire Brier penalty is the reliability term",
                },
                {
                    "expression": "len(r['decision']['groups_with_different_action']) == 1",
                    "description": "exactly one group's action differs under the asymmetric loss",
                },
            ],
        },
        readme=f"""
# WG-BM-065 (M2) — Overconfident forecast

## Scenario

**The same 800 cases and the same outcomes as WG-BM-064.** Only the stated
probabilities move, towards the extremes:

| stated `p` | cases | observed | error |
|---|---|---|---|
| 0.0 | 100 | 0.0 | 0 |
| **0.05** | 200 | **0.2** | −0.15 |
| 0.5 | 100 | 0.5 | 0 |
| **0.95** | 300 | **0.8** | +0.15 |
| 1.0 | 100 | 1.0 | 0 |

## Derivation

Resolution and uncertainty depend on the **observed** frequencies alone, so both
are unchanged:

```
resolution  = {RESOLUTION}        uncertainty = {UNCERTAINTY}
ECE         = 0.25 * 0.15 + 0.375 * 0.15 = 0.09375
reliability = 0.25 * 0.0225 + 0.375 * 0.0225 = {M2_RELIABILITY}
Brier       = {M1_BRIER} + {M2_RELIABILITY} = {M2_BRIER}
```

**The entire Brier penalty is the reliability term** — a clean separation that
only holds because the two forecasts rank the cases identically.

## The decision consequence

At `p* = 0.1`, **one group out of five** changes action:

| group | stated | observed | action from forecast | action from data | excess per case |
|---|---|---|---|---|---|
| `p=0.05` | 0.05 | 0.20 | `proceed` | **`divert`** | `18 − 8 = 10` |
| `p=0.95` | 0.95 | 0.80 | `divert` | `divert` | 0 |

```
total excess = 200 * 10 = 2000        per case over the whole sample = 2.5
```

Both miscalibrated groups are wrong by exactly 0.15. One costs 2000 and the
other costs nothing, because **only one of them straddles the threshold**.

## What this says about calibration metrics

A calibration score is a summary of all the errors; a decision cost is a summary
of the errors that cross a boundary. They are different sums, and the second is
the one that matters. Here they disagree about which group is the problem: the
0.95 group contributes 60% of the reliability term and 0% of the loss.

The practical form of this: report calibration **stratified by distance to the
operating threshold**, not only in aggregate — the same discipline WG-BM-029
arrives at from the deterministic side.

## Expected

| Quantity | WG-BM-064 | here |
|---|---|---|
| ECE | 0 | **0.09375** |
| reliability | 0 | **{M2_RELIABILITY}** |
| resolution | {RESOLUTION} | {RESOLUTION} |
| Brier | {M1_BRIER} | **{M2_BRIER}** |
| groups with a different action | none | **`p=0.05`** |
| excess expected loss | 0 | **2000** (2.5 per case) |
""",
    ))

    # ------------------------------------------------------------------ M3
    written.append(write_benchmark(
        directory="benchmarks/calibration/WG-BM-066_M3_calibrated_globally_miscalibrated_conditionally",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-066",
            "label": "M3",
            "title": "Perfect aggregate calibration hiding two badly wrong regimes",
            "category": "calibration",
            "difficulty": "adversarial",
            "purpose": "Two strata, each wrong by 0.3 in opposite directions, averaging to a "
                       "flawless aggregate reliability of zero. One stratum's action is wrong at "
                       "a cost of 5 per case.",
            "solver": "calibration.reliability",
            "assumptions": {
                "strata_declared": True,
                "same_forecast_probability_in_both_strata": True,
                "decision_threshold": 0.3,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "binary_probability",
                "decision_threshold": 0.3,
                "loss_matrix": "proceed 70/0, divert 0/30",
            },
            "expected_behavior": {
                "aggregate_calibration_error": 0.0,
                "stratified_calibration_error": 0.3,
                "aggregate_hides_stratum_failure": True,
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": [
                "aggregate_calibration_masks_regime_failure",
                "conditional_calibration_unassessed",
            ],
            "mutations_expected_to_fail": ["aggregate_calibration_only"],
            "hand_checkable": True,
            "notes": "The most important of the three: an aggregate reliability of zero is "
                     "compatible with the forecast being wrong in every regime it is used in.",
        },
        inputs={
            "calibration": {
                "description": "The same forecast probability of 0.5 is issued in calm and gusty "
                               "conditions. Events follow in 20 per cent of calm cases and 80 per "
                               "cent of gusty ones, and the two strata are the same size.",
                "groups": [
                    {
                        "id": "calm", "stratum": "calm",
                        "forecast_probability": 0.5, "n": 400, "events": 80,
                    },
                    {
                        "id": "gusty", "stratum": "gusty",
                        "forecast_probability": 0.5, "n": 400, "events": 320,
                    },
                ],
                "decision": {
                    "loss": {
                        "proceed": {"event": 70.0, "no_event": 0.0},
                        "divert": {"event": 0.0, "no_event": 30.0},
                    }
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-066",
            "source": "closed_form",
            "derivation": (
                "Pooled over the 800 cases there is a single forecast probability of 0.5 and "
                "400 events, an observed frequency of exactly 0.5. The aggregate expected "
                "calibration error and reliability term are therefore both zero and the forecast "
                "is, in aggregate, perfectly calibrated. "
                "Split by stratum it is wrong everywhere: 0.5 stated against 0.2 observed in calm "
                "conditions and 0.5 against 0.8 in gusty ones, each an error of 0.3 in opposite "
                "directions. Since the strata are equally sized, the stratified expected "
                "calibration error is 0.5 * 0.3 + 0.5 * 0.3 = 0.3 and the stratified reliability "
                "term is 0.5 * 0.09 + 0.5 * 0.09 = 0.09. The two errors cancel exactly, which is "
                "why the aggregate is clean. "
                "The loss matrix gives p* = 30 / (30 + 70) = 0.3. The stated 0.5 is above it, so "
                "the forecast says divert in both strata. In gusty conditions that is right, "
                "since 0.8 is also above the threshold. In calm conditions it is wrong: the true "
                "rate of 0.2 is below the threshold, proceeding costs 0.2 * 70 = 14 per case and "
                "diverting costs 0.8 * 30 = 24, an excess of 10 on each of 400 cases - 4000 in "
                "total, or 5 per case over the whole sample."
            ),
            "results": {
                "aggregate_calibration_error": 0.0,
                "perfectly_calibrated": True,
                "brier_score": 0.25,
                "reliability": 0.0,
                "resolution": 0.0,
                "uncertainty": 0.25,
                "base_rate": 0.5,
                "stratified_calibration_error": 0.3,
                "aggregate_hides_stratum_failure": True,
                "stratified": {
                    "expected_calibration_error": 0.3,
                    "reliability": 0.09,
                    "resolution": 0.09,
                    "uncertainty": 0.25,
                    "brier_score": 0.25,
                    "base_rate": 0.5,
                },
                "decision": {
                    "decision_threshold_probability": 0.3,
                    "groups_with_different_action": ["calm|p=0.5"],
                    "total_excess_expected_loss": 4000.0,
                    "excess_expected_loss_per_case": 5.0,
                },
            },
            "invariants": [
                {
                    "expression": "r['aggregate_calibration_error'] == 0.0 and r['stratified_calibration_error'] > 0.2",
                    "description": "flawless in aggregate, badly wrong conditionally",
                },
                {
                    "expression": "r['aggregate_hides_stratum_failure'] is True",
                    "description": "and the report says so rather than leaving it to be noticed",
                },
                {
                    "expression": "r['decision']['excess_expected_loss_per_case'] > 0",
                    "description": "the hidden miscalibration has a decision cost",
                },
            ],
        },
        readme="""
# WG-BM-066 (M3) — Calibrated globally, miscalibrated conditionally

## Scenario

The same forecast probability, **0.5**, is issued in two wind regimes.

| stratum | cases | stated `p` | events | observed |
|---|---|---|---|---|
| calm | 400 | 0.5 | 80 | **0.2** |
| gusty | 400 | 0.5 | 320 | **0.8** |

## Derivation

**Pooled.** 800 cases, one forecast probability of 0.5, 400 events → observed
0.5.

```
aggregate ECE = 0        aggregate reliability = 0        "perfectly calibrated"
```

**Stratified.** Wrong by 0.3 in each regime, in opposite directions:

```
stratified ECE         = 0.5 * 0.3 + 0.5 * 0.3   = 0.3
stratified reliability = 0.5 * 0.09 + 0.5 * 0.09 = 0.09
```

The two errors **cancel exactly**, which is the only reason the aggregate is
clean. Nothing about the pooled number is wrong; it is answering a question
nobody asked.

## The decision consequence

`p* = 30 / (30 + 70) = 0.3`. The stated 0.5 is above it, so the forecast says
`divert` in both regimes.

| stratum | true rate | forecast action | correct action | cost per case |
|---|---|---|---|---|
| gusty | 0.8 | `divert` | `divert` | 0 |
| **calm** | 0.2 | `divert` | **`proceed`** | `24 − 14 = 10` |

```
total excess = 400 * 10 = 4000        5 per case over the whole sample
```

Every calm-weather decision is wrong, and the reliability diagram for the
aggregate sample is a perfect diagonal.

## Why cancellation is the normal case, not a contrivance

Aggregate calibration is a *weighted average of signed errors*, and a forecast
trained or tuned on a pooled sample is being optimised for exactly that average.
It is therefore actively driven towards cancellation: systematic over-prediction
in one regime is the cheapest way to pay for systematic under-prediction in
another. The more regimes a forecast is used across, the more room it has to
balance.

The consequence is that **an aggregate reliability of zero is not evidence of
calibration in any regime the forecast is actually used in.** It is evidence
only about the mixture, and the mixture is not a situation anybody is ever in.

## What a system must do

Report calibration **conditional on the regimes the decision cares about** —
weather regime, fuel state, time of day, distance to the operating threshold —
and treat a clean aggregate with dirty strata as a failure, not a pass. The
result document carries `aggregate_hides_stratum_failure` so that the condition
is named rather than left for a reader to notice.

The `aggregate_calibration_only` mutation reports the aggregate figure in the
conditional slot; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| aggregate ECE | **0.0** |
| stratified ECE | **0.3** |
| aggregate reliability | 0.0 |
| stratified reliability | 0.09 |
| groups with a different action | `calm\\|p=0.5` |
| excess expected loss | 4000 (5 per case) |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
