"""Time-dependent road-network primitives shared by the routing, dispatch and
traffic benchmarks.

Semantics are fixed here, once, and documented in ``docs/ASSUMPTIONS.md``.  The
two that matter most:

**WG-SEM-1 (interval safety).**  A traveller may traverse edge ``e`` departing at
time ``tau`` if and only if the whole traversal interval ``[tau, tau + w_e(tau)]``
lies inside a single open window of ``e``.  Checking only the entry instant is
the classic mid-edge-closure bug and is injectable as the mutation
``edge_entry_time_only``.

**WG-SEM-2 (waiting).**  Waiting at a node is *not* permitted unless the
scenario declares ``waiting: true``.  With waiting permitted a traveller may
depart at any time at or after arrival; without it, departure is forced to the
arrival instant.  Feasibility genuinely differs between the two, so every
benchmark states which one it uses.

Travel time may depend on the departure time (``travel_time_profile``).  No FIFO
assumption is made anywhere: leaving later is allowed to arrive earlier, and the
search is an exhaustive enumeration over simple paths and candidate departure
times rather than a label-setting shortest-path algorithm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from .. import mutations

INF = float("inf")


@dataclass(frozen=True)
class Node:
    id: str
    x: float = 0.0
    y: float = 0.0
    role: str | None = None
    hazard_arrival_min: float = INF
    label: str | None = None


@dataclass
class Edge:
    id: str
    tail: str
    head: str
    directed: bool = False
    travel_time_min: float | None = None
    travel_time_profile: tuple[tuple[float, float, float], ...] = ()
    free_flow_min: float | None = None
    open_intervals: tuple[tuple[float, float], ...] = ((0.0, INF),)
    ever_closes: bool = False
    note: str | None = None

    def breakpoints(self) -> list[float]:
        points = [start for start, _, _ in self.travel_time_profile]
        points += [start for start, _ in self.open_intervals]
        return sorted({p for p in points if math.isfinite(p)})

    def travel_time(self, depart: float) -> float:
        """Travel time for a departure at ``depart`` minutes."""
        # MUTATION HOOK: cost every trip at free-flow speed, ignoring the
        # capacity interaction with the outbound evacuation.
        if self.free_flow_min is not None and mutations.active("ignore_congestion"):
            return float(self.free_flow_min)
        if self.travel_time_profile:
            for start, end, minutes in self.travel_time_profile:
                if start <= depart < end:
                    return float(minutes)
            return float(self.travel_time_profile[-1][2])
        if self.travel_time_min is None:
            raise ValueError(f"edge {self.id} has neither travel_time_min nor a profile")
        return float(self.travel_time_min)


@dataclass
class Network:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)

    def adjacency(self) -> dict[str, list[tuple[Edge, str]]]:
        out: dict[str, list[tuple[Edge, str]]] = {n: [] for n in self.nodes}
        for edge in self.edges:
            out.setdefault(edge.tail, []).append((edge, edge.head))
            reverse_allowed = not edge.directed
            # MUTATION HOOK: one-way semantics discarded.
            if mutations.active("allow_reverse_travel"):
                reverse_allowed = True
            if reverse_allowed:
                out.setdefault(edge.head, []).append((edge, edge.tail))
        return out

    def edge(self, edge_id: str) -> Edge:
        for edge in self.edges:
            if edge.id == edge_id:
                return edge
        raise KeyError(edge_id)


def load_network(document: dict) -> Network:
    """Build a :class:`Network` from a benchmark input document."""
    network = Network()
    for raw in document.get("nodes", []):
        hazard = raw.get("hazard_arrival_min", None)
        node = Node(
            id=str(raw["id"]),
            x=float(raw.get("x", 0.0)),
            y=float(raw.get("y", 0.0)),
            role=raw.get("role"),
            hazard_arrival_min=INF if hazard is None else float(hazard),
            label=raw.get("label"),
        )
        network.nodes[node.id] = node
    for raw in document.get("edges", []):
        profile = tuple(
            (
                float(item["depart_from"]),
                INF if item.get("depart_to") is None else float(item["depart_to"]),
                float(item["minutes"]),
            )
            for item in raw.get("travel_time_profile", [])
        )
        intervals_raw = raw.get("open_intervals")
        if intervals_raw is None:
            if raw.get("closes_at_min") is not None:
                intervals = ((0.0, float(raw["closes_at_min"])),)
            else:
                intervals = ((0.0, INF),)
        else:
            intervals = tuple(
                (float(pair[0]), INF if pair[1] is None else float(pair[1]))
                for pair in intervals_raw
            )
        edge = Edge(
            id=str(raw["id"]),
            tail=str(raw["from"]),
            head=str(raw["to"]),
            directed=bool(raw.get("directed", False)),
            travel_time_min=None if raw.get("travel_time_min") is None else float(raw["travel_time_min"]),
            free_flow_min=None if raw.get("free_flow_min") is None else float(raw["free_flow_min"]),
            travel_time_profile=profile,
            open_intervals=intervals,
            ever_closes=any(math.isfinite(end) for _, end in intervals),
            note=raw.get("note"),
        )
        network.edges.append(edge)
        for endpoint in (edge.tail, edge.head):
            network.nodes.setdefault(endpoint, Node(id=endpoint))
    return network


# --------------------------------------------------------------------------
# traversal feasibility
# --------------------------------------------------------------------------


def open_windows(edge: Edge) -> tuple[tuple[float, float], ...]:
    # MUTATION HOOK: collapse time-of-arrival to the final perimeter, i.e. an
    # edge that ever burns is treated as unusable from the start.
    if mutations.active("final_perimeter_hazard") and edge.ever_closes:
        return ()
    return edge.open_intervals


def can_traverse(edge: Edge, depart: float, entry_only: bool | None = None) -> bool:
    """WG-SEM-1: the entire traversal interval must fit in one open window.

    ``entry_only`` forces the naive entry-time-only rule instead; it exists so a
    benchmark can *report* what the naive convention would have concluded.  When
    it is left at ``None`` the rule is the declared one, which is what the
    ``edge_entry_time_only`` mutation attacks.
    """
    if entry_only is None:
        # MUTATION HOOK: entry-time-only safety check (mid-edge closure bug).
        entry_only = mutations.active("edge_entry_time_only")
    arrive = depart + edge.travel_time(depart)
    for start, end in open_windows(edge):
        if entry_only:
            if start <= depart <= end:
                return True
        elif start <= depart and arrive <= end:
            return True
    return False


def earliest_entry(
    edge: Edge, ready: float, allow_waiting: bool, entry_only: bool | None = None
) -> float | None:
    """Earliest departure time at or after ``ready`` for which traversal works."""
    if can_traverse(edge, ready, entry_only):
        return ready
    if not allow_waiting:
        return None
    for start, _ in sorted(open_windows(edge)):
        if start >= ready and can_traverse(edge, start, entry_only):
            return start
    for breakpoint in edge.breakpoints():
        if breakpoint >= ready and can_traverse(edge, breakpoint, entry_only):
            return breakpoint
    return None


def candidate_departures(edge: Edge, ready: float, allow_waiting: bool) -> list[float]:
    """Departure times worth considering from ``ready`` onwards.

    Travel time is piecewise constant in the departure time and open windows are
    intervals, so an optimal departure is either immediate or at a breakpoint.
    Enumerating them is exact, and — unlike a Dijkstra label — makes no FIFO
    assumption.
    """
    if not allow_waiting:
        return [ready]
    times = {ready}
    for start, _ in open_windows(edge):
        if start >= ready:
            times.add(start)
    for breakpoint in edge.breakpoints():
        if breakpoint >= ready:
            times.add(breakpoint)
    return sorted(times)


# --------------------------------------------------------------------------
# path enumeration (brute force by design)
# --------------------------------------------------------------------------


def enumerate_simple_paths(
    network: Network, source: str, target: str, max_nodes: int = 12
) -> list[list[tuple[Edge, str]]]:
    """Every simple path from ``source`` to ``target`` as a list of (edge, node)."""
    adjacency = network.adjacency()
    paths: list[list[tuple[Edge, str]]] = []

    def walk(current: str, visited: list[str], trail: list[tuple[Edge, str]]) -> None:
        if current == target and trail:
            paths.append(list(trail))
            return
        if len(visited) > max_nodes:
            return
        for edge, nxt in adjacency.get(current, []):
            if nxt in visited:
                continue
            trail.append((edge, nxt))
            visited.append(nxt)
            walk(nxt, visited, trail)
            visited.pop()
            trail.pop()

    walk(source, [source], [])
    return paths


def path_node_sequence(source: str, path: Sequence[tuple[Edge, str]]) -> list[str]:
    return [source] + [node for _, node in path]


def path_edge_ids(path: Iterable[tuple[Edge, str]]) -> list[str]:
    return [edge.id for edge, _ in path]


def traverse_path(
    path: Sequence[tuple[Edge, str]],
    start_time: float,
    allow_waiting: bool,
    node_deadlines: dict[str, float] | None = None,
    entry_only: bool | None = None,
) -> dict:
    """Earliest arrival along one fixed path, or the reason it is infeasible.

    With waiting forbidden the trajectory is fully determined by ``start_time``.
    With waiting permitted, an earlier arrival at a node never hurts (the
    traveller can always wait), so a greedy sweep over candidate departures is
    exact even when travel times are non-FIFO.
    """
    node_deadlines = node_deadlines or {}
    time = float(start_time)
    timeline: list[dict] = []
    for edge, node in path:
        options = candidate_departures(edge, time, allow_waiting)
        best: tuple[float, float] | None = None
        for depart in options:
            if not can_traverse(edge, depart, entry_only):
                continue
            arrive = depart + edge.travel_time(depart)
            if best is None or arrive < best[1]:
                best = (depart, arrive)
        if best is None:
            return {
                "feasible": False,
                "blocked_at_edge": edge.id,
                "blocked_ready_time_min": time,
                "timeline": timeline,
            }
        depart, arrive = best
        timeline.append(
            {
                "edge": edge.id,
                "depart_min": depart,
                "arrive_min": arrive,
                "wait_min": depart - time,
                "to": node,
            }
        )
        deadline = node_deadlines.get(node)
        if deadline is not None and arrive > deadline:
            return {
                "feasible": False,
                "blocked_at_node": node,
                "blocked_reason": "node deadline exceeded",
                "timeline": timeline,
            }
        time = arrive
    return {"feasible": True, "arrival_min": time, "timeline": timeline}


def best_route(
    network: Network,
    source: str,
    target: str,
    start_time: float = 0.0,
    allow_waiting: bool = False,
    node_deadlines: dict[str, float] | None = None,
    entry_only: bool | None = None,
) -> dict:
    """Exhaustive search over simple paths for the earliest feasible arrival."""
    evaluations = []
    for path in enumerate_simple_paths(network, source, target):
        outcome = traverse_path(path, start_time, allow_waiting, node_deadlines, entry_only)
        outcome["edges"] = path_edge_ids(path)
        outcome["nodes"] = path_node_sequence(source, path)
        evaluations.append(outcome)
    feasible = [e for e in evaluations if e["feasible"]]
    feasible.sort(key=lambda e: (e["arrival_min"], e["edges"]))
    return {
        "paths_evaluated": len(evaluations),
        "feasible_paths": len(feasible),
        "evaluations": evaluations,
        "best": feasible[0] if feasible else None,
    }
