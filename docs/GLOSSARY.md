# Glossary

Terms are defined as this repository uses them. Where a term is used differently
elsewhere in the literature, that is noted.

**Adversarial benchmark.** A case constructed so that the natural, reasonable
implementation gets it wrong. Difficulty level `adversarial`.

**Arrival time (hazard).** `T(x)`, the time at which the fire front reaches
location `x`, measured in minutes from the scenario epoch. The suite treats the
hazard as a time-of-arrival field, never as a static perimeter.

**Aspect.** The compass bearing of steepest **descent**, degrees clockwise from
north. `null` where the gradient vanishes. See WG-TER-3.

**Backing rate.** The rate at which a wind-driven fire spreads directly upwind.
`a - c` in the shifted-ellipse parameterisation.

**Baseline policy.** The policy against which value is measured. Declared per
benchmark, and required to be the best available *simple* policy rather than
inaction. See WG-BM-032.

**Benchmark id.** `WG-BM-0NN`. Permanent, never reused, never renumbered.

**Clairvoyant loss.** The expected loss of a decision maker who knows the
realised scenario before acting: `sum_s p_s min_a L(a, s)`.

**Contraflow.** Reversing inbound lanes so all lanes carry outbound traffic. Makes
the corridor one-way and blocks responder ingress; see WG-BM-008 and WG-BM-027.

**CVaR (conditional value at risk) at level `alpha`.** The mean loss over the
worst `1 - alpha` of the probability mass. `CVaR_0.9` is the mean of the worst
10%. Atoms straddling the tail boundary are split proportionally.

**Decision deadline.** The last time at which an action can still be taken.
Information arriving afterwards cannot influence it (WG-DEC-3).

**Dispatch time.** The time at which a responder leaves its base. The F family's
answer is the *set* of feasible dispatch times.

**Effective sample size.** The number of independent draws of the thing that
varies. In a simulation study it is the number of worlds, not the number of
residents (WG-BM-037).

**Egress / ingress.** Movement out of / into the threatened area. A responder's
ingress and the population's egress may compete for the same road (WG-BM-027).

**Entry-time semantics.** The rejected convention under which an edge may be
entered whenever it is open at the entry instant. Reported alongside the
declared answer in WG-BM-019, and injectable as the `edge_entry_time_only`
mutation.

**EVPI (expected value of perfect information).**
`E[loss(best fixed action)] - E[loss(clairvoyant)]`. A property of the decision
problem alone.

**Exactness.** How much an expected answer is worth: `CLOSED_FORM`,
`FINITE_ENUMERATION`, `NUMERIC_REFERENCE` or `SEEDED_STOCHASTIC_VALIDATION`.
Declared per benchmark, and a Monte Carlo approximation is never described as
exact.

**Feasible dispatch interval.** A maximal interval of dispatch times over which
the whole mission succeeds. The feasible *set* may be several such intervals
(WG-BM-026).

**FIFO (first-in-first-out) network.** One in which arriving earlier at a node
never produces a later arrival at the destination. Assumed by every
label-setting shortest-path algorithm and false in WG-BM-021.

**Flanking rate.** Across-wind spread. In the shifted ellipse, the perpendicular
distance reached per minute is `a b / sqrt(a^2 - c^2)`.

**Hand-checkable.** A competent reviewer can reproduce the expected answer with
pen and paper in a few minutes. A per-benchmark flag.

**Head rate.** Downwind spread rate, `a + c` in the shifted-ellipse
parameterisation.

**Interval safety (WG-SEM-1).** The suite's traversal convention: the whole
interval `[tau, tau + w]` must lie inside a single open window.

**Invariant.** A relational check over the result document, expressed as a
Python expression with the result bound as `r`. States the *point* of a
benchmark, which a pinned number cannot.

**Latency (observation).** The delay between acquisition and availability. An
observation acquired at `t_a` is usable from `t_a + L`.

**MNAR (missing not at random).** Missingness caused by the value being
measured. Sensors destroyed by the fire they are measuring (WG-BM-016). No
imputation from the observed data can fix it.

**Mutation.** A deliberately injected, plausible implementation bug. The
registry is `wg_benchmarks/mutations.py`; the results are
`reports/MUTATION_MATRIX.md`.

**Non-monotone feasibility.** A feasible set that is not an interval starting at
zero. The reason a scalar deadline is unsafe (WG-BM-026).

**Open window.** An interval during which an edge may be used. An edge carries a
*list* of them, so a road can close and reopen (WG-SEM-7).

**Pickup duration.** On-scene time to collect an assisted resident. Never zero
by default; the most commonly omitted term in assisted-evacuation models.

**Practical margin.** The smallest difference that matters operationally,
declared before the comparison (WG-STA-3).

**Pseudoreplication.** Treating correlated observations as independent samples.

**Realisable value of information.** The value actually obtainable given the
observing system's latency and the decision deadline. Distinct from EVPI, which
ignores both (WG-BM-043).

**Regret.** `loss(chosen action) - loss(best action)` in a given scenario.
*Realised* regret uses the scenario that actually occurred; *sup-regret* is the
maximum over the scenario set and grows with ensemble size (WG-BM-036).

**Robustly protectable.** There exists a single action whose loss is within the
acceptable threshold in *every* scenario of the declared uncertainty set. Does
not require knowing which scenario is true (WG-BM-041).

**Skill.** A property of a forecast alone — spatial error, a skill score. Never
used to choose an action, and never interchanged with value (WG-DEC-2).

**Staleness.** Query time minus the acquisition time of the newest available
observation. Beyond the declared `max_staleness_min`, a value is not current.

**Tenability.** Whether a location remains survivable. The resident's tenability
deadline bounds when a pickup must *complete*, not begin (WG-DIS-3).

**Value (of a policy).** `E[loss(baseline)] - E[loss(policy)]`. Positive means
better. Realised value uses the scenario that actually occurred.

**Waiting.** Holding at a node before entering the next edge. Opt-in per
scenario (WG-SEM-2), and it requires a survivable holding point.

---

## Terms added with the probabilistic families (K, L, M)

**Acquisition time.** When a sensor took the measurement. Distinct from
availability time, and the wrong one to filter an archive on (WG-BM-014).

**Admissible scenario.** An ensemble member consistent with the declared
physics. Weights renormalise over the admissible set only, and excluded members
are reported rather than dropped (WG-BM-048).

**Availability time.** When an observation's product can actually be used. The
only one of the three times a decision can consume.

**Base rate.** The unconditional probability of the event. Not a property of a
detector, and the input that does most of the work in interpreting one
(WG-BM-058).

**Brier score.** Mean squared error of a probability forecast. Decomposes as
`reliability - resolution + uncertainty` (Murphy).

**Conditional independence.** The assumption that `P(z1, z2 | H) = P(z1 | H) P(z2 | H)`.
False for co-located sensors, and undetectable from the marginals (WG-BM-054).

**Decision margin.** The gap in expected loss between the best action and the
runner-up. Reported alongside a recommendation so a reader can see how much it
took to make it.

**Decision resolved.** The recommendation survives both perfect information
(`EVPI = 0`) and a declared perturbation of the loss numbers. Independent of
whether the *state* is resolved.

**Decision threshold `p*`.** The hazard probability at which the optimal action
changes. Derived from the loss matrix; with more than two actions there is no
single one and the whole partition is reported.

**EVSI (expected value of sample information).** The reduction in expected loss
achievable by conditioning on an imperfect observation. Bounded above by EVPI.
*Statistical* EVSI ignores timing; *operational* EVSI is zero when the
observation arrives after the decision deadline.

**Expected calibration error (ECE).** The weighted mean absolute gap between
forecast probability and observed frequency.

**Information gain.** Mutual information between hypothesis and observation, in
bits. A property of the observation alone, and not a reason to acquire it
(WG-BM-050).

**Missingness indicator.** The binary variable "did the record arrive?". An
observation with its own likelihood whenever the arrival probability depends on
the quantity being estimated.

**MNAR / MAR / MCAR.** Missing not at random / at random / completely at random.
Fire-correlated sensor failure is MNAR, and no imputation from the observed data
can fix it.

**Point prediction.** A single number. One of five distinct objects the K family
keeps apart, and the least of them.

**Posterior belief.** A prior updated by a likelihood. Not a forecast, not an
ensemble, and not a decision.

**Predictive distribution.** A distribution over the predicted quantity. Under a
threshold decision it is the forecast; the mean enters only through the tail
probability.

**Reliability.** The calibration term of the Brier decomposition, the weighted
mean squared gap between forecast and observed frequency. Zero for a calibrated
forecast, and zero in aggregate for a forecast wrong in every stratum
(WG-BM-066).

**Resolution.** The Brier term measuring how far the group frequencies depart
from the base rate — the forecast's discrimination. Depends on outcomes only, so
it is unchanged by recalibration.

**State resolved.** Some scenario carries at least the declared share of the
probability mass. Says nothing about whether the decision is resolved.

**Worth acquiring.** An observation whose operational EVSI is positive.
"Acquire nothing" is a legitimate recommendation.
