# Assumptions and conventions

Every convention that could change a benchmark's expected answer is fixed here
and restated in the `assumptions` block of each benchmark that depends on it.
A benchmark whose answer depends on an undeclared convention is a defect.

## Units

| Quantity | Unit | Notes |
|---|---|---|
| time | minutes | all times are minutes from a scenario-local epoch, `t = 0` |
| distance | metres | |
| rate of spread | metres per minute | |
| elevation | metres | |
| loss | dimensionless, scenario-local | comparable within a benchmark, never across benchmarks |
| probability | 0 to 1 | scenario probabilities must sum to 1 to within 1e-9 |

Loss units deserve emphasis: they are ordinal-plus-scale **within one
benchmark**. A loss of 100 in WG-BM-029 and a loss of 100 in WG-BM-033 are not
the same thing, and no benchmark compares them.

## Terrain (A family)

* **WG-TER-1.** Grids are row-major with **row 0 at the northern edge**; `x`
  increases east, `y` increases north.
* **WG-TER-2.** Slope is Horn's 3x3 finite difference, reported in degrees from
  horizontal.
* **WG-TER-3.** Aspect is the **compass bearing of steepest descent**, degrees
  clockwise from north, and is `null` where the gradient vanishes. Aspect is not
  the bearing of ascent and is not measured counter-clockwise from east.
* **WG-TER-4.** A cell whose 3x3 neighbourhood contains a missing value yields
  `null`, with status `undefined_missing_neighbour`. Missing is never zero.
* **WG-TER-5.** Border cells have no complete neighbourhood and yield `null`
  with status `border`. They are excluded from interior statistics.

## Road networks (B, E, F families)

* **WG-SEM-1 (interval safety).** A traveller may traverse edge `e` departing at
  time `tau` if and only if the closed interval `[tau, tau + w_e(tau)]` lies
  inside a **single** open window of `e`. Checking only the entry instant is the
  mid-edge-closure bug. WG-BM-019 makes the choice explicit and reports both.
* **WG-SEM-2 (waiting).** Waiting at a node is **not** permitted unless the
  scenario declares `allow_waiting: true`. With waiting permitted a traveller
  may depart at any time at or after arrival, and the node is stipulated
  survivable for the whole hold.
* **WG-SEM-3 (no FIFO assumption).** Travel time may depend on departure time
  and is not assumed non-decreasing in arrival. All searches are exhaustive over
  simple paths and candidate departure times.
* **WG-SEM-4 (direction).** `directed: true` edges are traversable only from
  `from` to `to`. The default is undirected.
* **WG-SEM-5 (no off-road movement).** A destination with no incident edge is
  unreachable, whatever its straight-line distance.
* **WG-SEM-6 (no turning back).** A traveller who enters an edge completes it or
  the traversal was infeasible. Partial traversal and reversal are not modelled;
  WG-BM-019 documents the alternatives that were rejected.
* **WG-SEM-7 (open windows, not closure times).** Edge availability is a list of
  intervals, so a road can close and reopen. Collapsing this to a single closure
  time, or to the final fire perimeter, loses WG-BM-020 and WG-BM-026.
* **WG-SEM-8 (cuts exclude terminals).** The minimum node cut separating a
  population from its destinations ranges over non-terminal nodes only:
  "remove the village" is not an evacuation scenario.

## Assisted dispatch (F family)

* **WG-DIS-1.** A mission is `base -> ingress -> resident -> pickup -> egress ->
  destination`. All three legs must be feasible under WG-SEM-1.
* **WG-DIS-2.** Pickup duration is on-scene time and is never zero by default.
* **WG-DIS-3.** The pickup must **complete** before the resident's location
  becomes untenable, not merely begin.
* **WG-DIS-4.** Among feasible destinations the one with the **earliest
  arrival** is chosen. Ties break by destination id.
* **WG-DIS-5.** Feasibility is reported as a **set of dispatch intervals**, not
  as a scalar latest time. See WG-BM-026 for why.
* **WG-DIS-6.** The responder's own safety, crew endurance, refuelling and
  vehicle capacity beyond one resident are not modelled.
* **WG-DIS-7.** Interval endpoints are found by grid sampling plus bisection
  refinement, with every edge-window endpoint forced into the sample. The grid
  step is declared per benchmark, and a quantity that depends on it (the gap
  counterexample in WG-BM-026) says so.

## Observation (D family)

* **WG-OBS-1 (availability).** An observation acquired at `t_a` by a sensor with
  latency `L` is available at `t` if and only if `t_a + L <= t`. Filtering on
  acquisition time alone leaks the future.
* **WG-OBS-2 (staleness).** A value older than the declared `max_staleness_min`
  is not a current value. It is returned as `null` with the last known value in
  a separate field and `status: stale`.
* **WG-OBS-3 (missing is not zero).** No imputation happens in the data layer.
* **WG-OBS-4 (silence is evidence).** Where dropout is caused by the hazard, the
  missingness pattern carries information and a complete-case analysis is
  biased. The correction used in WG-BM-016 is exact only because the scenario
  stipulates the mechanism.
* **WG-OBS-5 (non-detection).** A non-detection is evidence of absence only
  where the detector is known to be reliable at that location and time.

## Decisions, forecasts and scenarios (G, H, J families)

* **WG-DEC-1.** Lower loss is better everywhere.
* **WG-DEC-2.** Skill is a property of a forecast; **value** is a property of
  the pair (forecast, decision). They are never interchanged.
* **WG-DEC-3 (timeliness).** Information available after the decision deadline
  cannot influence the action. A policy that waits for it takes its declared
  fallback action.
* **WG-DEC-4.** `value = E[loss(baseline)] - E[loss(policy)]`, so positive means
  the policy is better. The baseline is declared per benchmark and is the best
  available simple policy, not the absence of a policy.
* **WG-DEC-5.** `EVPI = E[loss(best fixed action)] - E[loss(clairvoyant)]`.
  `realizable_value_of_information` additionally requires a timely source.
* **WG-DEC-6 (no input averaging).** Loss is averaged over scenarios. Scenario
  inputs are never averaged into one pseudo-world.
* **WG-DEC-7 (joint scenarios).** Dependence between hazards is carried as joint
  scenarios. Marginal probabilities are never multiplied.
* **WG-DEC-8.** `CVaR_alpha` is the mean loss over the worst `1 - alpha` of the
  probability mass, with atoms split proportionally at the tail boundary.
* **WG-DEC-9 (tie-breaking).** Where two actions or policies tie, the one whose
  identifier sorts first is chosen, so that expected answers are deterministic.
  No benchmark's substantive claim rests on a tie-break.

## Statistics (I family)

* **WG-STA-1.** The unit of resampling is the unit of randomisation — the world,
  the run, the ensemble member — never the resident.
* **WG-STA-2.** Confidence intervals are 95% two-sided and use the normal
  quantile 1.959963984540054, not a t quantile. Stated so the arithmetic is
  reproducible.
* **WG-STA-3.** Practical margins are declared before the comparison, in the
  benchmark input.
* **WG-STA-4.** Policy comparisons are paired on common worlds.
* **WG-STA-5.** Stochastic quantities are seeded, and the benchmark declares
  `exactness: seeded_stochastic` together with a tolerance justified by the
  Monte Carlo error.

## Numerical conventions

* Default comparison tolerance is `1e-9` absolute, `0` relative: exact
  benchmarks must be exact.
* Per-field tolerances are declared in each benchmark's `tolerance` block.
* Arrival-time orderings break ties after rounding to `1e-9` minutes, so two
  analytically simultaneous points are not separated by the last bit of a square
  root.
