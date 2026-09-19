"""Figure generation for the benchmark suite.

Static SVG, written by hand with the standard library.  No matplotlib, no
dependency, no binary blobs in the repository: every figure is a text file whose
diff is reviewable.

Design rules followed here (see the project's visualisation guidance):

* one value axis per chart - where two quantities have different units they get
  two charts side by side, never two y-scales;
* categorical colours are assigned in fixed order from a validated palette
  (blue, orange, aqua) and never cycled;
* every series carries a direct label, so identity is never colour-alone - which
  is also the relief required for the aqua slot's contrast against the surface;
* grid and axes are recessive; marks are thin; values are labelled selectively
  rather than on every point.
"""

from __future__ import annotations

import html
from pathlib import Path

from . import yamlio
from .runner import REPO_ROOT, discover, run_benchmark

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
GRID = "#e2e1dd"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]


class Canvas:
    """A minimal linear-scale SVG plotting surface."""

    def __init__(
        self,
        title: str,
        x_label: str,
        y_label: str,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
        width: int = 660,
        height: int = 380,
        margin: tuple[int, int, int, int] = (56, 24, 56, 76),
    ) -> None:
        self.title = title
        self.x_label, self.y_label = x_label, y_label
        self.x0, self.x1 = x_range
        self.y0, self.y1 = y_range
        self.width, self.height = width, height
        self.top, self.right, self.bottom, self.left = margin
        self.parts: list[str] = []

    # -- coordinate transforms ------------------------------------------------
    def px(self, x: float) -> float:
        span = (self.x1 - self.x0) or 1.0
        return self.left + (x - self.x0) / span * (self.width - self.left - self.right)

    def py(self, y: float) -> float:
        span = (self.y1 - self.y0) or 1.0
        return self.height - self.bottom - (y - self.y0) / span * (
            self.height - self.top - self.bottom
        )

    # -- primitives -----------------------------------------------------------
    def text(self, x: float, y: float, content: str, size: int = 12,
             colour: str = INK_SOFT, anchor: str = "start", weight: str = "normal") -> None:
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="ui-sans-serif,-apple-system,Segoe UI,Helvetica,sans-serif" '
            f'font-size="{size}" fill="{colour}" text-anchor="{anchor}" font-weight="{weight}">'
            f"{html.escape(content)}</text>"
        )

    def line(self, points: list[tuple[float, float]], colour: str, width: float = 2.0,
             dashed: bool = False) -> None:
        path = " ".join(
            f"{'M' if i == 0 else 'L'}{self.px(x):.1f},{self.py(y):.1f}"
            for i, (x, y) in enumerate(points)
        )
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(
            f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{dash}/>'
        )

    def marker(self, x: float, y: float, colour: str, radius: float = 4.5) -> None:
        self.parts.append(
            f'<circle cx="{self.px(x):.1f}" cy="{self.py(y):.1f}" r="{radius}" fill="{colour}" '
            f'stroke="{SURFACE}" stroke-width="2"/>'
        )

    def hbar(self, y: float, x_start: float, x_end: float, colour: str, thickness: float = 16.0,
             opacity: float = 1.0) -> None:
        left, right = self.px(x_start), self.px(x_end)
        self.parts.append(
            f'<rect x="{left:.1f}" y="{self.py(y) - thickness / 2:.1f}" '
            f'width="{max(right - left, 2.0):.1f}" height="{thickness}" rx="4" '
            f'fill="{colour}" opacity="{opacity}"/>'
        )

    def vbar(self, x: float, value: float, colour: str, width: float = 34.0) -> None:
        top = self.py(value)
        base = self.py(max(self.y0, 0.0))
        self.parts.append(
            f'<rect x="{self.px(x) - width / 2:.1f}" y="{min(top, base):.1f}" width="{width}" '
            f'height="{abs(base - top):.1f}" rx="4" fill="{colour}"/>'
        )

    def vrule(self, x: float, label: str | None = None, colour: str = INK_SOFT) -> None:
        self.parts.append(
            f'<line x1="{self.px(x):.1f}" y1="{self.top}" x2="{self.px(x):.1f}" '
            f'y2="{self.height - self.bottom}" stroke="{colour}" stroke-width="1" '
            f'stroke-dasharray="4 4"/>'
        )
        if label:
            self.text(self.px(x), self.top - 6, label, 11, colour, anchor="middle")

    # -- frame ----------------------------------------------------------------
    def axes(self, x_ticks: list[float], y_ticks: list[float],
             x_tick_labels: list[str] | None = None) -> None:
        for value in y_ticks:
            y = self.py(value)
            self.parts.append(
                f'<line x1="{self.left}" y1="{y:.1f}" x2="{self.width - self.right}" '
                f'y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>'
            )
            self.text(self.left - 8, y + 4, f"{value:g}", 11, INK_SOFT, anchor="end")
        labels = x_tick_labels or [f"{v:g}" for v in x_ticks]
        for value, label in zip(x_ticks, labels):
            self.text(self.px(value), self.height - self.bottom + 18, label, 11,
                      INK_SOFT, anchor="middle")
        self.parts.append(
            f'<line x1="{self.left}" y1="{self.height - self.bottom}" '
            f'x2="{self.width - self.right}" y2="{self.height - self.bottom}" '
            f'stroke="{INK_SOFT}" stroke-width="1"/>'
        )
        self.text(
            (self.left + self.width - self.right) / 2,
            self.height - 14,
            self.x_label,
            12,
            INK_SOFT,
            anchor="middle",
        )
        self.parts.append(
            f'<text x="16" y="{(self.top + self.height - self.bottom) / 2:.1f}" '
            f'font-family="ui-sans-serif,-apple-system,Segoe UI,Helvetica,sans-serif" font-size="12" '
            f'fill="{INK_SOFT}" text-anchor="middle" '
            f'transform="rotate(-90 16 {(self.top + self.height - self.bottom) / 2:.1f})">'
            f"{html.escape(self.y_label)}</text>"
        )

    def render(self, subtitle: str | None = None) -> str:
        head = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}" role="img" '
            f'aria-label="{html.escape(self.title)}">',
            f'<rect width="{self.width}" height="{self.height}" fill="{SURFACE}"/>',
        ]
        body = list(self.parts)
        self.parts = []
        self.text(self.left - 40, 24, self.title, 14, INK, weight="600")
        if subtitle:
            self.text(self.left - 40, 40, subtitle, 11, INK_SOFT)
        head += self.parts + body + ["</svg>"]
        return "\n".join(head) + "\n"


def _write(benchmark_id: str, name: str, svg: str) -> Path:
    benchmark = next(b for b in discover() if b.benchmark_id == benchmark_id)
    path = benchmark.path.parent / "figures" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return path


def _result(benchmark_id: str) -> dict:
    benchmark = next(b for b in discover() if b.benchmark_id == benchmark_id)
    outcome = run_benchmark(benchmark)
    if outcome.result is None:  # pragma: no cover - only on a solver crash
        raise RuntimeError(f"{benchmark_id} did not produce a result")
    return outcome.result


# --------------------------------------------------------------------------
# individual figures
# --------------------------------------------------------------------------


def figure_e1() -> Path:
    """WG-BM-018: each route's traversal interval against its open window."""
    canvas = Canvas(
        "E1  Short unsafe route vs long safe route",
        "minutes from the decision epoch",
        "",
        (0, 12),
        (0, 3),
        height=300,
        margin=(60, 24, 56, 150),
    )
    canvas.axes(list(range(0, 13, 2)), [])
    rows = [
        ("e_short_unsafe", 2.1, 0.0, 4.0, 0.0, 5.0, SERIES[1], "infeasible: still on the road at 5"),
        ("e_long_safe", 1.0, 0.0, 12.0, 0.0, 9.0, SERIES[0], "feasible: arrives at 9"),
    ]
    for name, row, open_from, open_to, depart, arrive, colour, note in rows:
        canvas.hbar(row, open_from, open_to, GRID, thickness=22)
        canvas.hbar(row, depart, arrive, colour, thickness=12)
        canvas.text(canvas.left - 8, canvas.py(row) + 4, name, 11, INK, anchor="end")
        canvas.text(canvas.px(arrive) + 8, canvas.py(row) + 4, note, 11, INK_SOFT)
    canvas.vrule(4.0, "hazard closes the short route")
    return _write(
        "WG-BM-018",
        "route_feasibility.svg",
        canvas.render("grey bar: open window  \u00b7  coloured bar: traversal interval"),
    )


def figure_e4() -> Path:
    """WG-BM-021: arrival time as a function of departure time (non-FIFO)."""
    result = _result("WG-BM-021")
    samples = [(s["depart_min"], s["arrival_min"]) for s in result["departure_sweep"]]
    canvas = Canvas(
        "E4  Leaving later arrives earlier",
        "departure time (min)",
        "arrival time (min)",
        (0, 10),
        (0, 70),
    )
    canvas.axes(list(range(0, 11, 2)), list(range(0, 71, 10)))
    early = [p for p in samples if p[0] < 5]
    late = [p for p in samples if p[0] >= 5]
    canvas.line(early, SERIES[1])
    canvas.line(late, SERIES[0])
    for x, y in early:
        canvas.marker(x, y, SERIES[1])
    for x, y in late:
        canvas.marker(x, y, SERIES[0])
    canvas.text(canvas.px(0.4), canvas.py(60) - 12, "60 min detour", 11, SERIES[1])
    canvas.text(canvas.px(5.4), canvas.py(15) + 22, "10 min escorted crossing", 11, SERIES[0])
    canvas.vrule(5.0, "convoy starts")
    return _write(
        "WG-BM-021",
        "arrival_vs_departure.svg",
        canvas.render("arrival is not non-decreasing in departure: the network is not FIFO"),
    )


def figure_f2() -> Path:
    """WG-BM-023: latest feasible dispatch against pickup duration."""
    result = _result("WG-BM-023")
    points = [
        (float(k), v)
        for k, v in sorted(result["latest_dispatch_by_pickup"].items(), key=lambda kv: float(kv[0]))
        if v is not None
    ]
    canvas = Canvas(
        "F2  Latest dispatch falls one-for-one with pickup duration",
        "pickup duration (min)",
        "latest feasible dispatch (min)",
        (0, 17),
        (-6, 10),
    )
    canvas.axes(list(range(0, 18, 2)), list(range(-6, 11, 2)))
    canvas.line(points, SERIES[0])
    for x, y in points:
        canvas.marker(x, y, SERIES[0])
        canvas.text(canvas.px(x) + 10, canvas.py(y) - 8, f"{y:g}", 11, INK)
    canvas.text(canvas.px(3.2), canvas.py(8.4), "slope -1", 11, SERIES[0])
    # The 15 minute pickup needs a dispatch at 10 - 15 = -5, which does not exist.
    canvas.line([(10, 0), (15, -5)], SERIES[1], width=1.5, dashed=True)
    canvas.marker(15.0, -5.0, SERIES[1])
    canvas.text(canvas.px(14.4), canvas.py(-5.0) - 12, "15 min pickup: infeasible", 11,
                SERIES[1], anchor="end")
    return _write(
        "WG-BM-023",
        "pickup_sensitivity.svg",
        canvas.render("a flat line here is the signature of an ignored on-scene time"),
    )


def figure_f5() -> Path:
    """WG-BM-026: the feasible dispatch set is two disjoint intervals."""
    result = _result("WG-BM-026")
    canvas = Canvas(
        "F5  Feasible dispatch times are not an interval",
        "dispatch time (min)",
        "",
        (0, 50),
        (0, 3),
        height=300,
        margin=(60, 24, 56, 150),
    )
    canvas.axes(list(range(0, 51, 10)), [])
    canvas.hbar(2.0, 0, 50, GRID, thickness=22)
    for start, end in result["feasible_intervals"]:
        canvas.hbar(2.0, start, end, SERIES[0], thickness=22)
    canvas.text(canvas.left - 8, canvas.py(2.0) + 4, "mission feasible", 11, INK, anchor="end")
    canvas.hbar(1.0, 0, 10, SERIES[2], thickness=14)
    canvas.hbar(1.0, 20, 40, SERIES[2], thickness=14)
    canvas.text(canvas.left - 8, canvas.py(1.0) + 4, "ingress corridor open", 11, INK, anchor="end")
    latest = result["latest_feasible_dispatch_min"]
    gap = result["infeasible_dispatch_below_latest_min"]
    canvas.vrule(latest, f"latest feasible = {latest:g}")
    canvas.vrule(gap, f"dispatch at {gap:g} fails")
    return _write(
        "WG-BM-026",
        "feasible_dispatch_intervals.svg",
        canvas.render("a scalar deadline of 34 would authorise every failing dispatch in the gap"),
    )


def figure_c1_c3() -> list[Path]:
    """WG-BM-009 and WG-BM-011: arrival-time profiles, linear and kinked."""
    written = []
    canvas = Canvas(
        "C1  Arrival time is linear in distance",
        "distance from ignition (m)",
        "arrival time (min)",
        (0, 320),
        (0, 35),
    )
    canvas.axes(list(range(0, 321, 80)), list(range(0, 36, 5)))
    canvas.line([(0, 0), (300, 30)], SERIES[0])
    for distance, label in ((100.0, "p_east / p_north"), (141.42, "p_ne"), (300.0, "p_far")):
        canvas.marker(distance, distance / 10.0, SERIES[0])
        canvas.text(canvas.px(distance) + 8, canvas.py(distance / 10.0) - 6, label, 11, INK)
    written.append(_write("WG-BM-009", "arrival_vs_distance.svg",
                          canvas.render("isotropic spread at 10 m/min")))

    canvas = Canvas(
        "C3  A fuel boundary puts a kink in the arrival profile",
        "distance along the transect (m)",
        "arrival time (min)",
        (0, 220),
        (0, 65),
    )
    canvas.axes(list(range(0, 221, 40)), list(range(0, 66, 10)))
    canvas.line([(0, 0), (100, 10)], SERIES[0])
    canvas.line([(100, 10), (200, 60)], SERIES[1])
    canvas.line([(0, 0), (2.8 * 63, 63)], SERIES[2], width=1.5, dashed=True)
    canvas.text(canvas.px(34), canvas.py(9), "grass, 10 m/min", 11, SERIES[0])
    canvas.text(canvas.px(160), canvas.py(28), "timber litter, 2 m/min", 11, SERIES[1])
    canvas.text(canvas.px(96), canvas.py(58), "averaged fuel, 2.8 m/min", 11, SERIES[2],
                anchor="end")
    canvas.vrule(100.0, "fuel boundary")
    written.append(_write("WG-BM-011", "fuel_discontinuity.svg",
                          canvas.render("the averaged rate puts the boundary at 36 min instead of 10")))
    return written


def figure_g4() -> list[Path]:
    """WG-BM-031: skill and decision value, as two charts rather than two axes."""
    result = _result("WG-BM-031")
    order = ["use_crude_early", "baseline_trigger", "use_accurate_late"]
    short = {"use_crude_early": "crude, early", "baseline_trigger": "baseline",
             "use_accurate_late": "accurate, late"}

    value = Canvas(
        "G4  Decision value",
        "policy",
        "value vs baseline (loss units)",
        (-0.5, 2.5),
        (-45, 10),
        width=400,
        height=340,
        margin=(60, 20, 60, 76),
    )
    value.axes([0, 1, 2], list(range(-40, 11, 10)), [short[p] for p in order])
    for index, policy in enumerate(order):
        amount = result["value_by_policy"][policy]
        value.vbar(index, amount, SERIES[0] if amount >= 0 else SERIES[1])
        offset = -10 if amount >= 0 else 16
        value.text(value.px(index), value.py(amount) + offset, f"{amount:g}", 11, INK,
                   anchor="middle")
    first = _write("WG-BM-031", "decision_value.svg",
                   value.render("higher is better"))

    skill = Canvas(
        "G4  Forecast skill score",
        "policy",
        "skill score (0-1)",
        (-0.5, 2.5),
        (0, 1.0),
        width=400,
        height=340,
        margin=(60, 20, 60, 76),
    )
    skill.axes([0, 1, 2], [0.0, 0.25, 0.5, 0.75, 1.0], [short[p] for p in order])
    for index, policy in enumerate(order):
        score = result["policies"][policy]["skill_score"]
        if score is None:
            skill.text(skill.px(index), skill.py(0.03), "no forecast", 11, INK_SOFT,
                       anchor="middle")
            continue
        skill.vbar(index, score, SERIES[2])
        skill.text(skill.px(index), skill.py(score) - 10, f"{score:g}", 11, INK, anchor="middle")
    second = _write("WG-BM-031", "forecast_skill.svg",
                    skill.render("higher is 'better' - and the orders are reversed"))
    return [first, second]


def figure_i2() -> Path:
    """WG-BM-038: mean and CVaR of two policies, same units, one axis."""
    result = _result("WG-BM-038")
    canvas = Canvas(
        "I2  The better average has the worse tail",
        "policy",
        "loss",
        (-0.5, 1.5),
        (0, 110),
        width=520,
    )
    canvas.axes([0, 1], list(range(0, 111, 20)), ["policy_a", "policy_b"])
    for index, policy in enumerate(("policy_a", "policy_b")):
        mean = result["mean_loss"][policy]
        tail = result["cvar_loss"][policy]
        canvas.vbar(index - 0.13, mean, SERIES[0], width=48)
        canvas.vbar(index + 0.13, tail, SERIES[1], width=48)
        canvas.text(canvas.px(index - 0.13), canvas.py(mean) - 8, f"{mean:g}", 11, INK,
                    anchor="middle")
        canvas.text(canvas.px(index + 0.13), canvas.py(tail) - 8, f"{tail:g}", 11, INK,
                    anchor="middle")
    canvas.text(canvas.px(-0.13), canvas.py(105), "mean loss", 11, SERIES[0], anchor="middle")
    canvas.text(canvas.px(1.13), canvas.py(105), "CVaR(0.9)", 11, SERIES[1], anchor="middle")
    return _write("WG-BM-038", "mean_vs_cvar.svg",
                  canvas.render("lower is better on both measures; they disagree on the winner"))


def write_all() -> list[Path]:
    written = [figure_e1(), figure_e4(), figure_f2(), figure_f5()]
    written += figure_c1_c3()
    written += figure_g4()
    written.append(figure_i2())
    _update_benchmark_figures(written)
    return written


def _update_benchmark_figures(paths: list[Path]) -> None:
    """Record the generated figures in each benchmark.yaml."""
    by_benchmark: dict[Path, list[str]] = {}
    for path in paths:
        by_benchmark.setdefault(path.parent.parent, []).append(f"figures/{path.name}")
    for directory, names in by_benchmark.items():
        meta_path = directory / "benchmark.yaml"
        text = meta_path.read_text(encoding="utf-8")
        banner, _, body = text.partition("\n")
        meta = yamlio.loads(body)
        if meta.get("figures") == sorted(names):
            continue
        meta["figures"] = sorted(names)
        meta_path.write_text(banner + "\n" + yamlio.dumps(meta), encoding="utf-8")
