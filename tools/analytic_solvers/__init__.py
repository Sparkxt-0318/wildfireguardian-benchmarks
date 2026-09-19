"""Independent brute-force reference solvers ("Agent B").

Nothing in this package is used to produce a benchmark's expected answer, and
nothing here imports ``wg_benchmarks.solvers``.  These are deliberately naive,
deliberately slow, second implementations written from the benchmark
definitions, whose only job is to disagree with the primary solvers if either is
wrong.  ``tests/test_cross_check.py`` runs them against the same inputs.

Where the primary solver is clever (interval refinement by bisection, partial
atoms in the CVaR integral, Pareto reasoning about waiting), the version here is
the stupidest thing that obviously works: enumerate a fine grid, expand the
distribution into equal-probability atoms, try every mapping.
"""

from .brute_force import (  # noqa: F401
    compute_exact_scenario_loss,
    cvar_by_expansion,
    enumerate_actions,
    enumerate_all_paths,
    enumerate_dispatch_times,
    simulate_mission,
    walk_path,
)
