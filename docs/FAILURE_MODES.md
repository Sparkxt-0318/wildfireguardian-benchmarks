# Catalogue of scientific failure modes

The failure modes this programme considers consequential, each with the
benchmarks that target it. `reports/COVERAGE.md` is the generated, always-current
version of the mapping; this file is the prose explanation of why each mode is
on the list.

## Time and information

**Future information leakage** (`WG-BM-014`). An observation is used before it
could have been available. Appears whenever an archive is joined on acquisition
time rather than availability time. Produces a system that scores well offline
and degrades inexplicably in deployment; the bias is systematic and optimistic,
not noise.

**Timeliness ignored** (`WG-BM-030`, `WG-BM-031`, `WG-BM-043`). Information that
arrives after the last useful decision time is treated as usable. Converts a
forecasting success into an operational failure, and makes investment cases for
sensing that cannot pay off.

**Stale data presented as current** (`WG-BM-015`). A carried-forward value is
indistinguishable from a fresh one. The most dangerous form of missing data,
because the output is plausible.

## Hazard representation

**Mid-edge hazard** (`WG-BM-018`, `WG-BM-019`, and the whole F family). Edge
safety is judged at the entry instant rather than over the traversal interval.
Produces evacuation plans that end inside the fire.

**Time of arrival collapsed to a final perimeter** (`WG-BM-018`, `WG-BM-020`,
and the F family). The hazard is reduced to "burns eventually" or to a single
closure time. Loses re-openings, and with them the entire non-monotone
structure of WG-BM-026.

**Anisotropy ignored** (`WG-BM-010`). Wind-driven spread replaced by an
isotropic front at a mean rate. 67% error on the head bearing.

**Heterogeneity averaged** (`WG-BM-011`). A fuel boundary smoothed into a mean
rate. Optimistic precisely in the fast-burning fuel.

**Spotting ignored** (`WG-BM-012`). Single-ignition models miss disconnected
threatened areas, and arrival time stops being monotone in distance from the
main front.

## Data quality

**Missing treated as zero** (`WG-BM-004`, `WG-BM-015`). Manufactures cliffs in
terrain and false alarms or false reassurance in observations, depending on the
variable's semantics — which is exactly why the imputation cannot be done
generically in a data layer.

**Informative missingness / MNAR** (`WG-BM-016`). Sensors fail because the
hazard reached them, so the surviving network reports calm with maximum
confidence when the situation is worst. No imputation from the observed data can
fix it.

**False negative treated as a negative** (`WG-BM-017`). Absence of detection is
read as absence of hazard, without regard to whether the detector could have
seen it. Requires per-cell reliability to be carried alongside the detection,
which many pipelines discard early.

## Network and routing semantics

**Direction semantics lost** (`WG-BM-008`). One-way and contraflow roads loaded
into an undirected graph, so responders are routed into corridors that are
physically full of outbound traffic.

**Unreachable destination selected** (`WG-BM-007`). Nearest-facility selection
by straight-line distance. Invisible in aggregate statistics, catastrophic for
the individual sent there.

**Non-FIFO networks** (`WG-BM-021`). Label-setting shortest-path algorithms
assume that arriving earlier is never worse. Escorted convoys, ferries and
contraflow switch-overs break the assumption, and the resulting label is simply
wrong rather than approximately right.

**False single-egress claims** (`WG-BM-006`). "The graph has articulation
points" conflated with "the community has one way out".

## Decision structure

**Non-monotone feasibility** (`WG-BM-026`). Feasibility summarised by a scalar
deadline when the feasible set is disjoint. A system reporting 24 minutes of
margin while the mission is already impossible.

**Service time ignored** (`WG-BM-022`, `WG-BM-023`). The on-scene pickup
duration is the term most often omitted, because it is the one term that is not
a property of the road network, and it is the term that varies most between
residents.

**Greedy base selection** (`WG-BM-024`). Nearest base chosen without regard to
which ingress corridor closes first.

**Static destination assignment** (`WG-BM-025`). Pre-assigned refuges that stop
being reachable partway through the incident.

**Capacity ignored** (`WG-BM-027`). Responder ingress costed at free flow while
the same road is saturated with outbound evacuees.

## Forecasts and value

**Skill/value conflation** (`WG-BM-028`, `WG-BM-029`, `WG-BM-031`, `WG-BM-033`).
Forecast accuracy is a property of the forecast; decision value is a property of
the pair (forecast, decision). A 500 m error can be worth nothing and a 20 m
error can cost 92.

**Error/consequence correlation** (`WG-BM-033`). The scenarios a model finds
hard are the scenarios that produce extreme losses, so aggregate accuracy is
nearly uninformative about decision value.

**Weak baselines** (`WG-BM-032`). Value measured against doing nothing rather
than against the best available simple policy. Systematically overstates the
contribution of the sophisticated component.

## Uncertainty

**Correlation ignored** (`WG-BM-034`). Joint road-failure probabilities
reconstructed by multiplying marginals. Understates the probability of losing
all egress by a factor that grows with the number of "redundant" roads, and it
does so exactly where redundancy is being claimed as a safety argument.

**Average-of-inputs fallacy** (`WG-BM-035`). Ensemble members averaged into a
mean fire field and the decision evaluated once. The averaged world is more
benign than any world that can actually occur.

**Worst-case criterion instability** (`WG-BM-036`). Sup-regret is a maximum over
a scenario *set* and grows mechanically with ensemble size, so two teams with
the same model and different ensemble sizes reach different "robust"
recommendations.

## Statistics

**Pseudoreplication** (`WG-BM-037`). Correlated residents inside a simulated
world counted as independent samples. Always overstates confidence, never
understates it.

**Tail risk ignored** (`WG-BM-038`). Policies ranked on the mean when the whole
purpose of the system is the tail.

**Significance mistaken for importance** (`WG-BM-039`). At 2000 simulated worlds
any difference is significant; significance testing measures how much compute
was purchased.

**Selection bias** (`WG-BM-040`). Policies compared on different world samples.
Reverses both the sign and the magnitude of the true effect.

## Protectability

**EVPI mistaken for realisable value** (`WG-BM-041`, `WG-BM-042`, `WG-BM-043`).
The value of information is a property of the decision *and* the observing
system's latency. Two situations with zero realisable value — nothing worth
knowing, and no way to know it in time — demand completely different responses.
