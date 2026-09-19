"""Analytic fire-arrival-time reference solver.

Four transparent models, each with a closed-form time of arrival.  No cellular
automaton, no level set, no calibration: the point is that the answer can be
checked on paper.

``radial``
    Isotropic constant spread, ``T(x) = |x - x0| / r``.

``elliptical_wind``
    Constant wind.  The front at time ``t`` is an ellipse with semi-axes
    ``a*t`` (along wind) and ``b*t`` (across wind) whose centre has drifted
    ``c*t`` downwind, so the head rate is ``a + c``, the backing rate ``a - c``
    and the flanking rate ``a / sqrt(a^2 - c^2) * b`` ... see the derivation in
    the benchmark README.  Arrival time solves a quadratic in ``t``.

``piecewise_fuel_1d``
    Rate of spread changes at known fuel boundaries along a transect; arrival is
    the cumulative sum of segment length divided by segment rate.

``multi_ignition``
    Several ignition points, each with its own start time and rate; arrival is
    the minimum over sources.  Used to build genuinely disconnected threatened
    areas (spotting).
"""

from __future__ import annotations

import math
from typing import Sequence

from .. import mutations

INF = float("inf")


def radial_arrival(point: Sequence[float], origin: Sequence[float], rate: float) -> float:
    return math.hypot(point[0] - origin[0], point[1] - origin[1]) / rate


def elliptical_arrival(
    point: Sequence[float],
    origin: Sequence[float],
    head_rate: float,
    back_rate: float,
    flank_semi_axis: float,
    wind_bearing_deg: float,
) -> float:
    """Arrival time under a constant-wind shifted-ellipse front.

    ``a = (head + back) / 2`` is the semi-major growth rate, ``c = (head - back) / 2``
    the downwind drift rate of the ellipse centre and ``b = flank_semi_axis`` the
    across-wind growth rate.  Writing the offset in wind-aligned coordinates as
    ``(p, q)`` the front condition ``((p - c t)/a)^2 + (q/b)^2 = t^2`` gives

        A t^2 + B t + C = 0,  A = b^2 (c^2 - a^2), B = -2 b^2 c p, C = b^2 p^2 + a^2 q^2

    whose physical root (``A < 0`` whenever the fire backs at all) is
    ``t = (b^2 c p - sqrt(B^2/4 - A C)) / A``.
    """
    a = (head_rate + back_rate) / 2.0
    c = (head_rate - back_rate) / 2.0
    b = flank_semi_axis
    # MUTATION HOOK: drop the wind bias and spread isotropically at mean rate.
    if mutations.active("isotropic_fire"):
        return radial_arrival(point, origin, a)
    bearing = math.radians(wind_bearing_deg)
    # Wind bearing is the compass direction the wind blows *towards*.
    ux, uy = math.sin(bearing), math.cos(bearing)
    dx, dy = point[0] - origin[0], point[1] - origin[1]
    p = dx * ux + dy * uy
    q = -dx * uy + dy * ux
    if a == c:  # purely downwind spread, no backing
        raise ValueError("degenerate ellipse: back_rate must be positive")
    A = b * b * (c * c - a * a)
    C = b * b * p * p + a * a * q * q
    discriminant = (b * b * c * p) ** 2 - A * C
    root = math.sqrt(max(discriminant, 0.0))
    return (b * b * c * p - root) / A


def piecewise_fuel_arrival(distance_m: float, segments: Sequence[dict]) -> float:
    """Arrival along a transect whose rate of spread changes at fuel boundaries."""
    # MUTATION HOOK: average the fuel types into a single mean rate.
    if mutations.active("uniform_fuel"):
        total_length = sum(float(s["to_m"]) - float(s["from_m"]) for s in segments)
        mean_rate = sum(
            float(s["rate_m_per_min"]) * (float(s["to_m"]) - float(s["from_m"])) for s in segments
        ) / total_length
        return distance_m / mean_rate
    time = 0.0
    remaining = distance_m
    for segment in segments:
        start, end = float(segment["from_m"]), float(segment["to_m"])
        rate = float(segment["rate_m_per_min"])
        span = min(end, distance_m) - start
        if span <= 0:
            break
        time += span / rate
        remaining -= span
        if distance_m <= end:
            return time
    if remaining > 1e-12:
        rate = float(segments[-1]["rate_m_per_min"])
        time += remaining / rate
    return time


def _components(cells: set[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """4-connected components of a set of grid cells."""
    remaining = set(cells)
    out = []
    while remaining:
        seed = remaining.pop()
        component = [seed]
        stack = [seed]
        while stack:
            r, c = stack.pop()
            for neighbour in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if neighbour in remaining:
                    remaining.remove(neighbour)
                    component.append(neighbour)
                    stack.append(neighbour)
        out.append(sorted(component))
    return sorted(out)


def solve(inputs: dict) -> dict:
    document = inputs["fire"]
    model = document["model"]
    probes = document.get("probe_points", [])
    arrivals: dict[str, float] = {}

    if model == "radial":
        origin = (float(document["origin"]["x"]), float(document["origin"]["y"]))
        rate = float(document["rate_m_per_min"])
        for probe in probes:
            arrivals[str(probe["id"])] = radial_arrival((probe["x"], probe["y"]), origin, rate)
    elif model == "elliptical_wind":
        origin = (float(document["origin"]["x"]), float(document["origin"]["y"]))
        for probe in probes:
            arrivals[str(probe["id"])] = elliptical_arrival(
                (probe["x"], probe["y"]),
                origin,
                float(document["head_rate_m_per_min"]),
                float(document["back_rate_m_per_min"]),
                float(document["flank_semi_axis_m_per_min"]),
                float(document["wind_bearing_deg"]),
            )
    elif model == "piecewise_fuel_1d":
        segments = document["segments"]
        for probe in probes:
            arrivals[str(probe["id"])] = piecewise_fuel_arrival(float(probe["distance_m"]), segments)
    elif model == "multi_ignition":
        sources = document["sources"]
        # MUTATION HOOK: only the primary ignition is modelled, so spot fires
        # ahead of the main front are invisible.
        if mutations.active("single_ignition_only"):
            sources = sources[:1]
        for probe in probes:
            best = INF
            for source in sources:
                candidate = float(source.get("ignition_time_min", 0.0)) + radial_arrival(
                    (probe["x"], probe["y"]),
                    (float(source["x"]), float(source["y"])),
                    float(source["rate_m_per_min"]),
                )
                best = min(best, candidate)
            arrivals[str(probe["id"])] = best
    else:  # pragma: no cover - guarded by schema
        raise ValueError(f"unknown fire model: {model}")

    # Ties are broken by identifier so the expected ordering is deterministic.
    # Arrival times are rounded to 1e-9 min (60 ns) before comparison, so two
    # points that are analytically simultaneous are not separated by the last
    # bit of a square root.
    ordering = [
        pid for pid, _ in sorted(arrivals.items(), key=lambda kv: (round(kv[1], 9), kv[0]))
    ]

    result: dict = {
        "model": model,
        "arrival_min": arrivals,
        "arrival_order": ordering,
        "first_reached": ordering[0] if ordering else None,
        "last_reached": ordering[-1] if ordering else None,
    }

    burn_query = document.get("burned_area_query")
    if burn_query:
        time = float(burn_query["at_time_min"])
        step = float(burn_query["cell_size_m"])
        x0, x1 = float(burn_query["x_min"]), float(burn_query["x_max"])
        y0, y1 = float(burn_query["y_min"]), float(burn_query["y_max"])
        sources = document["sources"]
        if mutations.active("single_ignition_only"):  # MUTATION HOOK (see above)
            sources = sources[:1]
        burned = set()
        rows = int(round((y1 - y0) / step))
        cols = int(round((x1 - x0) / step))
        for r in range(rows):
            for c in range(cols):
                x = x0 + (c + 0.5) * step
                y = y0 + (r + 0.5) * step
                arrival = min(
                    float(s.get("ignition_time_min", 0.0))
                    + radial_arrival((x, y), (float(s["x"]), float(s["y"])), float(s["rate_m_per_min"]))
                    for s in sources
                )
                if arrival <= time:
                    burned.add((r, c))
        components = _components(burned)
        result["burned_cells"] = len(burned)
        result["burned_components"] = len(components)
        result["burned_component_sizes"] = [len(comp) for comp in components]

    return result
