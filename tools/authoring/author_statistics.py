"""Author the I family: statistical benchmarks (WG-BM-037..040)."""

from __future__ import annotations

import math

from common import report, write_benchmark

SCRIPT = "author_statistics.py"
Z = 1.959963984540054

# ---------------------------------------------------------------- I1 constants
WORLD_OUTCOMES = [10.0, 14.0, 18.0, 22.0, 26.0, 30.0, 34.0, 38.0, 42.0, 46.0]
RESIDENTS_PER_WORLD = 1000
N_WORLDS = len(WORLD_OUTCOMES)
N_RESIDENTS = N_WORLDS * RESIDENTS_PER_WORLD
_MEAN = sum(WORLD_OUTCOMES) / N_WORLDS
_SS = sum((v - _MEAN) ** 2 for v in WORLD_OUTCOMES)
WORLD_SE = math.sqrt(_SS / (N_WORLDS - 1)) / math.sqrt(N_WORLDS)
RESIDENT_SE = math.sqrt(
    _SS * RESIDENTS_PER_WORLD / (N_RESIDENTS - 1)
) / math.sqrt(N_RESIDENTS)
WORLD_WIDTH = 2 * Z * WORLD_SE
RESIDENT_WIDTH = 2 * Z * RESIDENT_SE
WIDTH_RATIO = WORLD_SE / RESIDENT_SE

# ---------------------------------------------------------------- I3 constants
EQ_N = 2000
EQ_MEAN = 0.3
EQ_SPREAD = 1.0
EQ_SD = math.sqrt(EQ_N * EQ_SPREAD**2 / (EQ_N - 1))
EQ_SE = EQ_SD / math.sqrt(EQ_N)
EQ_LOWER, EQ_UPPER = EQ_MEAN - Z * EQ_SE, EQ_MEAN + Z * EQ_SE

# ---------------------------------------------------------------- I4 constants
NAIVE_A = (0 + 0 + 0 + 0 + 40 + 40) / 6 + 5
NAIVE_B = (0 + 0 + 40 + 40 + 40 + 40) / 6 + 2


def main() -> None:
    written = []

    # ------------------------------------------------------------------ I1
    written.append(write_benchmark(
        directory="benchmarks/statistics/WG-BM-037_I1_pseudoreplication",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-037",
            "label": "I1",
            "title": "Ten worlds, ten thousand residents, and an effective sample size of ten",
            "category": "statistics",
            "difficulty": "adversarial",
            "purpose": "Residents inside a simulated world are perfectly correlated. Bootstrapping "
                       "residents produces a confidence interval 33 times too narrow; "
                       "bootstrapping worlds does not.",
            "solver": "statistics.reference",
            "assumptions": {
                "within_world_correlation": 1.0,
                "worlds_independent": True,
                "resampling_unit_must_be_the_world": True,
                "seed": 20240101,
                "bootstrap_samples": 200,
            },
            "expected_behavior": {
                "effective_sample_size": 10,
                "naive_sample_size": 10000,
                "reported_resampling_unit": "world",
            },
            "tolerance": {
                "default": 1.0e-09,
                "world_bootstrap_ci_width": 5.0,
                "resident_bootstrap_ci_width": 0.15,
                "bootstrap_ci_width_ratio": 12.0,
                "reported_ci_width": 5.0,
            },
            "exactness": "SEEDED_STOCHASTIC_VALIDATION",
            "detects": ["pseudoreplication", "effective_sample_size_inflation"],
            "mutations_expected_to_fail": ["resident_level_bootstrap"],
            "hand_checkable": True,
            "notes": "The analytic standard errors are exact and are checked to 1e-9. The "
                     "bootstrap quantities are Monte Carlo estimates from 200 resamples of only "
                     "10 worlds and are checked against the analytic values within a stated band.",
        },
        inputs={
            "statistics": {
                "description": "Ten simulated worlds, each containing 1000 residents. Within a "
                               "world every resident experiences the same outcome, because the "
                               "world's weather draw determines it. Between worlds the outcomes "
                               "differ.",
                "analysis": "pseudoreplication",
                "worlds": [
                    {"id": f"w{i + 1}", "outcome": value}
                    for i, value in enumerate(WORLD_OUTCOMES)
                ],
                "residents_per_world": RESIDENTS_PER_WORLD,
                "bootstrap_samples": 200,
                "seed": 20240101,
            }
        },
        expected={
            "benchmark_id": "WG-BM-037",
            "source": "hand_derivation",
            "derivation": (
                "The ten world outcomes are 10, 14, ..., 46, with mean 28 and sum of squared "
                "deviations 1320. The sample standard deviation across worlds is "
                "sqrt(1320/9) = 12.1106, so the standard error of the mean over 10 independent "
                "worlds is 12.1106/sqrt(10) = 3.82971. "
                "Pooling residents gives 10000 values, each world's value repeated 1000 times. "
                "Their sum of squared deviations is 1000 * 1320 = 1320000 and the sample standard "
                "deviation is sqrt(1320000/9999) = 11.48970, so the naive standard error is "
                "11.48970/100 = 0.114897. "
                "The ratio of the two standard errors, and hence of the two confidence interval "
                "widths, is 3.82971/0.114897 = 33.3317. Residents carry no independent "
                "information at all here: the effective sample size is 10, not 10000, and "
                "resampling residents understates the uncertainty by a factor of about 33. "
                "The bootstrap figures are Monte Carlo estimates of these quantities from 200 "
                "resamples and are checked against them within the declared tolerance."
            ),
            "results": {
                "analysis": "pseudoreplication",
                "worlds": N_WORLDS,
                "residents_per_world": RESIDENTS_PER_WORLD,
                "total_residents": N_RESIDENTS,
                "point_estimate": 28.0,
                "analytic_world_se": WORLD_SE,
                "analytic_resident_se": RESIDENT_SE,
                "analytic_ci_width_ratio": WIDTH_RATIO,
                "effective_sample_size": 10,
                "naive_sample_size": 10000,
                "world_bootstrap_ci_width": WORLD_WIDTH,
                "resident_bootstrap_ci_width": RESIDENT_WIDTH,
                "bootstrap_ci_width_ratio": WIDTH_RATIO,
                "reported_ci_width": WORLD_WIDTH,
                "reported_resampling_unit": "world",
                "resident_bootstrap_understates_uncertainty": True,
            },
            "invariants": [
                {
                    "expression": "r['bootstrap_ci_width_ratio'] > 10.0",
                    "description": "the resident-level interval is more than ten times too narrow",
                },
                {
                    "expression": "r['effective_sample_size'] == 10 and r['naive_sample_size'] == 10000",
                    "description": "the effective and nominal sample sizes differ by three orders of magnitude",
                },
                {
                    "expression": "r['reported_resampling_unit'] == 'world'",
                    "description": "the reported interval is the world-level one",
                },
            ],
        },
        readme=f"""
# WG-BM-037 (I1) — Pseudoreplication

## Scenario

Ten simulated worlds, 1000 residents each, 10000 resident-level outcomes in
total. **Within a world, every resident experiences the same outcome**, because
a single weather draw determines it. Between worlds the outcomes differ:

```
10, 14, 18, 22, 26, 30, 34, 38, 42, 46      (mean 28)
```

## Derivation

**World-level.** Sum of squared deviations is 1320 over 10 worlds:

```
s_world = sqrt(1320 / 9) = 12.1106
SE_world = 12.1106 / sqrt(10) = {WORLD_SE:.6f}
```

**Resident-level.** Each world's value appears 1000 times, so the pooled sum of
squared deviations is `1000 * 1320 = 1320000` over 10000 values:

```
s_resident = sqrt(1320000 / 9999) = 11.48970
SE_resident = 11.48970 / sqrt(10000) = {RESIDENT_SE:.6f}
```

**Ratio**

```
SE_world / SE_resident = {WIDTH_RATIO:.4f}
```

The resident-level confidence interval is **{WIDTH_RATIO:.0f} times too narrow**.

## Why the residents carry no information

The variance of the mean of `n` observations with pairwise correlation `rho` is

```
Var = sigma^2 / n * (1 + (n - 1) rho)
```

With `rho = 1` within a world this collapses to `sigma^2`, independent of how
many residents the world contains: simulating 10000 residents per world instead
of 1000 would not narrow the interval by one part in a thousand. The effective
sample size is the number of **independent draws of the thing that varies**,
which here is the world, and that number is **10**.

Real simulations sit between `rho = 0` and `rho = 1`, but they are much closer
to 1 than intuition suggests, because the dominant sources of variation —
ignition location, wind, fuel moisture, time of day — are shared by every
resident in the run. The failure is one-sided: pseudoreplication always
overstates confidence, never understates it.

## What a system must do

Resample at the level at which the randomisation actually happened: the world,
the simulation run, the ensemble member. Resident-level summaries may be the
*quantity of interest*; they are never the *unit of resampling*. Where residents
do carry partially independent information, a hierarchical model or a
cluster bootstrap is the correct tool, and the cluster is still the world.

The `resident_level_bootstrap` mutation resamples residents and reports that
interval as the answer; this benchmark is its declared detector.

## What is checked exactly and what is checked loosely

The analytic standard errors and their ratio are exact and are checked to 1e-9.
The bootstrap confidence intervals are Monte Carlo estimates from 200 resamples
of 10 worlds — themselves quite variable — and are checked against the analytic
values within a declared band (±5 on the world width, ±0.15 on the resident
width, ±12 on the ratio). The exactness of this benchmark is recorded as
`SEEDED_STOCHASTIC_VALIDATION` for that reason.

## Expected

| Quantity | Value |
|---|---|
| analytic world standard error | `{WORLD_SE:.6f}` |
| analytic resident standard error | `{RESIDENT_SE:.6f}` |
| width ratio | `{WIDTH_RATIO:.4f}` |
| effective sample size | 10 |
| nominal sample size | 10000 |
""",
    ))

    # ------------------------------------------------------------------ I2
    written.append(write_benchmark(
        directory="benchmarks/statistics/WG-BM-038_I2_mean_vs_tail_risk",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-038",
            "label": "I2",
            "title": "Policy A has the better average and a five times worse tail",
            "category": "statistics",
            "difficulty": "intermediate",
            "purpose": "Mean and CVaR rank two policies in opposite orders. A system that "
                       "reports only the mean cannot express the difference that matters.",
            "solver": "statistics.reference",
            "assumptions": {
                "cvar_alpha": 0.9,
                "risk_preference": "cvar",
                "loss_distributions_given_exactly": True,
            },
            "expected_behavior": {
                "best_by_mean": "policy_a",
                "best_by_cvar": "policy_b",
                "rankings_conflict": True,
            },
            "tolerance": {"default": 1.0e-09},
            "exactness": "CLOSED_FORM",
            "detects": ["tail_risk_ignored", "mean_only_ranking"],
            "mutations_expected_to_fail": ["mean_only_ranking"],
            "hand_checkable": True,
        },
        inputs={
            "statistics": {
                "description": "Two evacuation policies with exactly specified discrete loss "
                               "distributions. Policy A is usually free and occasionally "
                               "catastrophic; policy B is always mildly costly.",
                "analysis": "tail_risk",
                "cvar_alpha": 0.9,
                "risk_preference": "cvar",
                "policies": [
                    {
                        "id": "policy_a",
                        "outcomes": [
                            {"loss": 0.0, "probability": 0.9},
                            {"loss": 100.0, "probability": 0.1},
                        ],
                    },
                    {
                        "id": "policy_b",
                        "outcomes": [
                            {"loss": 12.0, "probability": 0.9},
                            {"loss": 20.0, "probability": 0.1},
                        ],
                    },
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-038",
            "source": "closed_form",
            "derivation": (
                "Policy A: mean = 0.9 * 0 + 0.1 * 100 = 10. Its worst 10 per cent of probability "
                "mass is exactly the atom at 100, so CVaR at 0.9 is 100. "
                "Policy B: mean = 0.9 * 12 + 0.1 * 20 = 10.8 + 2 = 12.8. Its worst 10 per cent is "
                "exactly the atom at 20, so CVaR at 0.9 is 20. "
                "Policy A therefore has the better mean by 2.8 and the worse conditional tail by "
                "a factor of 5. Ranking by mean selects A; ranking by CVaR selects B; the two "
                "criteria disagree, and with the declared risk preference of 'cvar' the "
                "recommendation is B."
            ),
            "results": {
                "analysis": "tail_risk",
                "cvar_alpha": 0.9,
                "mean_loss": {"policy_a": 10.0, "policy_b": 12.8},
                "cvar_loss": {"policy_a": 100.0, "policy_b": 20.0},
                "best_by_mean": "policy_a",
                "best_by_cvar": "policy_b",
                "rankings_conflict": True,
                "risk_preference": "cvar",
                "recommended_policy": "policy_b",
                "policies": {
                    "policy_a": {"mean_loss": 10.0, "cvar": 100.0, "worst_case_loss": 100.0},
                    "policy_b": {"mean_loss": 12.8, "cvar": 20.0, "worst_case_loss": 20.0},
                },
            },
            "invariants": [
                {
                    "expression": "r['mean_loss']['policy_a'] < r['mean_loss']['policy_b']",
                    "description": "policy A wins on the mean",
                },
                {
                    "expression": "r['cvar_loss']['policy_b'] < r['cvar_loss']['policy_a']",
                    "description": "policy B wins on the tail",
                },
                {
                    "expression": "r['cvar_loss']['policy_a'] / r['cvar_loss']['policy_b'] == 5.0",
                    "description": "the tail difference is a factor of five",
                },
            ],
        },
        readme="""
# WG-BM-038 (I2) — Mean versus tail risk

## Scenario

Two evacuation policies with exactly specified discrete loss distributions.

| Policy | Loss | Probability |
|---|---|---|
| `policy_a` | 0 | 0.9 |
| | 100 | 0.1 |
| `policy_b` | 12 | 0.9 |
| | 20 | 0.1 |

Policy A is usually free and occasionally catastrophic. Policy B is always
mildly costly.

## Derivation

```
mean(A)       = 0.9 * 0  + 0.1 * 100 = 10
mean(B)       = 0.9 * 12 + 0.1 * 20  = 12.8

CVaR_0.9(A)   = mean loss over the worst 10% of mass = 100
CVaR_0.9(B)   = mean loss over the worst 10% of mass = 20
```

The worst 10% of the probability mass is exactly the upper atom in each case, so
both CVaR values are read off directly with no interpolation.

| | mean | CVaR(0.9) |
|---|---|---|
| `policy_a` | **10** | 100 |
| `policy_b` | 12.8 | **20** |

Policy A is better by 2.8 on the average and **five times worse** in the tail.
The rankings conflict.

## Why both numbers are needed

The mean is the right criterion when losses are fungible and the decision
repeats often enough for the average to be realised. Neither condition holds for
an evacuation: a community experiences one fire, and the loss in the 10% branch
of policy A is not 10 units of inconvenience — it is the outcome the entire
system exists to prevent.

Nor is CVaR automatically right. It discards the 90% of outcomes in which policy
A is free, and a policy chosen purely on the tail will over-evacuate, which has
its own costs in compliance, credibility and the next fire.

What this benchmark requires is that **both are reported and the criterion is
declared**. Here the declared preference is `cvar`, so the recommendation is
`policy_b`; with a declared preference of `mean` the answer would be `policy_a`
and would be equally defensible, provided it is stated.

The `mean_only_ranking` mutation ignores the declared preference and recommends
the better average; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| mean loss, A / B | 10 / 12.8 |
| CVaR(0.9), A / B | 100 / 20 |
| best by mean | `policy_a` |
| best by CVaR | `policy_b` |
| rankings conflict | `true` |
""",
    ))

    # ------------------------------------------------------------------ I3
    written.append(write_benchmark(
        directory="benchmarks/statistics/WG-BM-039_I3_practical_equivalence",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-039",
            "label": "I3",
            "title": "Overwhelmingly significant and practically equivalent at the same time",
            "category": "statistics",
            "difficulty": "intermediate",
            "purpose": "Two policies differ by 0.3 units with a practical margin of 1.0. With "
                       "n = 2000 the difference is highly significant and entirely without "
                       "operational meaning.",
            "solver": "statistics.reference",
            "assumptions": {
                "practical_margin": 1.0,
                "paired_design": True,
                "normal_approximation": True,
                "difference_construction_deterministic": True,
            },
            "expected_behavior": {
                "practically_equivalent": True,
                "statistically_significant": True,
                "significant_but_not_meaningful": True,
            },
            "tolerance": {"default": 1.0e-09},
            "exactness": "CLOSED_FORM",
            "detects": ["significance_mistaken_for_importance", "no_equivalence_test"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "The paired differences are constructed deterministically (half at +1.3, "
                     "half at -0.7) so the sample mean and standard deviation are exact and the "
                     "confidence interval can be checked by hand.",
        },
        inputs={
            "statistics": {
                "description": "Paired differences in minutes of evacuation clearance time "
                               "between two policies, evaluated on the same 2000 worlds. The "
                               "operationally meaningful difference agreed in advance is "
                               "1 minute.",
                "analysis": "equivalence",
                "practical_margin": 1.0,
                "difference_spec": {"n": EQ_N, "mean": EQ_MEAN, "sd": EQ_SPREAD},
            }
        },
        expected={
            "benchmark_id": "WG-BM-039",
            "source": "closed_form",
            "derivation": (
                "The 2000 paired differences are 1000 values of +1.3 and 1000 of -0.7, so the "
                "sample mean is exactly 0.3 and every deviation from it is exactly 1.0 in "
                "magnitude. The sample standard deviation is therefore "
                "sqrt(2000/1999) = 1.0002501 and the standard error is "
                "1.0002501/sqrt(2000) = 0.0223717. "
                "The 95 per cent normal confidence interval is 0.3 +/- 1.959964 * 0.0223717 = "
                "[0.256152, 0.343848]. "
                "Significance: the interval excludes zero by a wide margin, and |0.3| is 13.4 "
                "standard errors from zero, so the difference is significant at any conventional "
                "level. "
                "Practical equivalence: the whole interval lies inside the pre-agreed margin of "
                "+/- 1.0 minute, so the two policies are practically equivalent. Both statements "
                "are true simultaneously."
            ),
            "results": {
                "analysis": "equivalence",
                "n": EQ_N,
                "mean_difference": EQ_MEAN,
                "sd_difference": EQ_SD,
                "standard_error": EQ_SE,
                "ci_lower": EQ_LOWER,
                "ci_upper": EQ_UPPER,
                "practical_margin": 1.0,
                "practically_equivalent": True,
                "statistically_significant": True,
                "significant_but_not_meaningful": True,
                "conclusion": "equivalent",
            },
            "invariants": [
                {
                    "expression": "r['ci_lower'] > -r['practical_margin'] and r['ci_upper'] < r['practical_margin']",
                    "description": "the whole confidence interval lies inside the practical margin",
                },
                {
                    "expression": "r['ci_lower'] > 0",
                    "description": "the interval also excludes zero, so the difference is significant",
                },
                {
                    "expression": "abs(r['mean_difference'] / r['standard_error']) > 10",
                    "description": "the effect is more than ten standard errors from zero",
                },
            ],
        },
        readme=f"""
# WG-BM-039 (I3) — Practical equivalence

## Scenario

Two evacuation policies are compared on the **same 2000 simulated worlds**. The
paired differences in clearance time are constructed deterministically — 1000
values at `+1.3` minutes and 1000 at `-0.7` minutes — so that the sample
statistics are exact:

```
mean difference = 0.3 minutes         sd = sqrt(2000/1999) = {EQ_SD:.7f}
```

The operationally meaningful difference, agreed **before** looking at the data,
is **1 minute**.

## Derivation

```
SE   = {EQ_SD:.7f} / sqrt(2000) = {EQ_SE:.7f}
95% CI = 0.3 +/- 1.959964 * {EQ_SE:.7f} = [{EQ_LOWER:.6f}, {EQ_UPPER:.6f}]
```

**Significance.** The interval excludes zero; the effect is
`0.3 / {EQ_SE:.7f} = {EQ_MEAN / EQ_SE:.1f}` standard errors from zero. Significant at any
conventional level, with room to spare.

**Practical equivalence.** The entire interval lies inside `[-1, +1]`, the
pre-agreed margin. By the two-one-sided-tests criterion the policies are
**equivalent**.

Both statements are true at once, and neither contradicts the other.

## What this benchmark is for

A wildfire decision programme can afford to run 2000 simulated worlds. At that
sample size the standard error is 0.022 minutes and essentially **any**
difference becomes significant — a policy change worth 1.3 seconds of clearance
time will produce `p < 0.001`. Significance testing at this sample size measures
how much compute was purchased, not whether the policy matters.

The two things a system must do instead:

1. **Declare the practical margin in advance.** Here it is 1 minute, because
   below that the difference is inside the noise of a real evacuation —
   notification lag, household preparation time, traffic signal timing. The
   margin is a domain judgement and it must be written down before the
   comparison, not chosen afterwards.
2. **Test equivalence, not just difference.** "Not significantly different" and
   "equivalent" are different claims, and with small samples the first is
   routinely true while the second is unsupported. Here the reverse holds: the
   difference *is* significant, and the policies *are* equivalent.

## Expected

| Quantity | Value |
|---|---|
| mean difference | 0.3 min |
| 95% CI | `[{EQ_LOWER:.4f}, {EQ_UPPER:.4f}]` |
| practical margin | 1.0 min |
| statistically significant | `true` |
| practically equivalent | `true` |
| conclusion | `equivalent` |
""",
    ))

    # ------------------------------------------------------------------ I4
    written.append(write_benchmark(
        directory="benchmarks/statistics/WG-BM-040_I4_hidden_selection_bias",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-040",
            "label": "I4",
            "title": "Unpaired comparison across different worlds reverses the true ranking",
            "category": "statistics",
            "difficulty": "adversarial",
            "purpose": "Policy A is evaluated on mostly easy worlds and policy B on mostly hard "
                       "ones. The naive comparison favours A by 10.3; the paired comparison on "
                       "the common worlds favours B by 3.",
            "solver": "statistics.reference",
            "assumptions": {
                "world_difficulty_is_additive": True,
                "policy_effect_is_a_constant_offset": True,
                "common_worlds_exist": True,
            },
            "expected_behavior": {
                "naive_best_policy": "policy_a",
                "paired_best_policy": "policy_b",
                "ranking_sign_flip": True,
            },
            "tolerance": {"default": 1.0e-09},
            "exactness": "CLOSED_FORM",
            "detects": ["selection_bias", "unpaired_comparison"],
            "mutations_expected_to_fail": ["naive_unpaired_comparison"],
            "hand_checkable": True,
        },
        inputs={
            "statistics": {
                "description": "Eight worlds: four easy (difficulty 0) and four hard "
                               "(difficulty 40). Each policy adds a constant offset to the "
                               "world's difficulty. The two policies were run on overlapping but "
                               "different subsets, as happens when evaluation sets accumulate "
                               "over time.",
                "analysis": "selection_bias",
                "worlds": [
                    {"id": "w1", "difficulty": 0.0},
                    {"id": "w2", "difficulty": 0.0},
                    {"id": "w3", "difficulty": 0.0},
                    {"id": "w4", "difficulty": 0.0},
                    {"id": "w5", "difficulty": 40.0},
                    {"id": "w6", "difficulty": 40.0},
                    {"id": "w7", "difficulty": 40.0},
                    {"id": "w8", "difficulty": 40.0},
                ],
                "policies": [
                    {"id": "policy_a", "offset": 5.0},
                    {"id": "policy_b", "offset": 2.0},
                ],
                "evaluated_on": {
                    "policy_a": ["w1", "w2", "w3", "w4", "w5", "w6"],
                    "policy_b": ["w3", "w4", "w5", "w6", "w7", "w8"],
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-040",
            "source": "hand_derivation",
            "derivation": (
                "Loss is world difficulty plus the policy's offset. "
                "Policy A was run on w1..w6, whose difficulties are 0,0,0,0,40,40 with mean "
                "80/6 = 13.333, so its naive mean loss is 13.333 + 5 = 18.333. "
                "Policy B was run on w3..w8, whose difficulties are 0,0,40,40,40,40 with mean "
                "160/6 = 26.667, so its naive mean loss is 26.667 + 2 = 28.667. "
                "The naive difference is 18.333 - 28.667 = -10.333, which makes policy A look "
                "better by more than ten units. "
                "The four common worlds are w3, w4, w5, w6, with difficulties 0,0,40,40 and mean "
                "20. On those, policy A scores 25 and policy B scores 22, so the paired "
                "difference is +3 in favour of policy B - which is simply the difference of the "
                "two offsets, 5 - 2 = 3, as it must be when the policy effect is additive. "
                "The naive comparison reverses the true ranking and exaggerates the magnitude by "
                "a factor of three and a half."
            ),
            "results": {
                "analysis": "selection_bias",
                "worlds": 8,
                "common_worlds": ["w3", "w4", "w5", "w6"],
                "naive_mean_loss": {"policy_a": NAIVE_A, "policy_b": NAIVE_B},
                "paired_mean_loss": {"policy_a": 25.0, "policy_b": 22.0},
                "naive_difference": NAIVE_A - NAIVE_B,
                "paired_difference": 3.0,
                "naive_best_policy": "policy_a",
                "paired_best_policy": "policy_b",
                "ranking_sign_flip": True,
                "recommended_policy": "policy_b",
            },
            "invariants": [
                {
                    "expression": "r['naive_difference'] < 0 < r['paired_difference']",
                    "description": "the two comparisons have opposite signs",
                },
                {
                    "expression": "r['paired_difference'] == 3.0",
                    "description": "the paired difference recovers the true policy effect exactly",
                },
            ],
        },
        readme="""
# WG-BM-040 (I4) — Hidden selection bias

## Scenario

Eight worlds: `w1`-`w4` easy (difficulty 0), `w5`-`w8` hard (difficulty 40).
Loss is `world difficulty + policy offset`, with offsets `policy_a = 5` and
`policy_b = 2`. **Policy B is genuinely better, by exactly 3.**

The two policies were run on overlapping but different subsets — the situation
that arises whenever an evaluation set accumulates over time:

```
policy_a evaluated on w1 w2 w3 w4 w5 w6     (4 easy, 2 hard)
policy_b evaluated on       w3 w4 w5 w6 w7 w8   (2 easy, 4 hard)
```

## Derivation

**Naive, unpaired**

```
policy_a: mean difficulty (0,0,0,0,40,40) = 13.333  ->  loss 18.333
policy_b: mean difficulty (0,0,40,40,40,40) = 26.667 -> loss 28.667
naive difference = 18.333 - 28.667 = -10.333        ->  "A is better by 10.3"
```

**Paired, on the four common worlds `w3 w4 w5 w6`**

```
mean difficulty = 20
policy_a = 25      policy_b = 22
paired difference = +3                              ->  "B is better by 3"
```

The paired difference recovers the true policy effect **exactly**, because
pairing differences out the world difficulty term, which is what the two
policies did not share.

| | naive | paired | truth |
|---|---|---|---|
| better policy | `policy_a` | `policy_b` | `policy_b` |
| margin | 10.3 | 3.0 | 3.0 |

The naive comparison gets both the **sign** and the **magnitude** wrong.

## Why this happens without anyone cheating

Nothing in this scenario requires bad faith. Evaluation sets grow: a new policy
is tested on the scenarios that were available that quarter; an older policy's
results are reused because rerunning is expensive; a few worlds fail to converge
and are dropped, and they are not dropped at random. The result is two numbers
in a results table that were never comparable, presented in the same column.

The difficulty term does not have to be labelled, either. Here `difficulty` is
an explicit field; in a real evaluation it is the unmeasured combination of
ignition location, wind and fuel state that makes some worlds hard for every
policy. That is precisely why pairing works and covariate adjustment may not:
pairing removes the term without needing to measure it.

## What a system must do

* **Compare on common worlds.** Report the set of worlds used for each policy
  and refuse, or loudly flag, a comparison whose intersection is empty.
* **Report the paired difference,** not the difference of the means.
* **Treat a shrinking intersection as a defect,** not an inconvenience. If two
  policies share no worlds, they have not been compared at all.

The `naive_unpaired_comparison` mutation reports the unpaired ranking; this
benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| naive mean loss, A / B | 18.333 / 28.667 |
| naive difference | -10.333 (favours A) |
| common worlds | `w3 w4 w5 w6` |
| paired mean loss, A / B | 25 / 22 |
| paired difference | **+3 (favours B)** |
| ranking sign flip | `true` |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
