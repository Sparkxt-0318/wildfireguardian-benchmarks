"""Static road-graph reference solver: connectivity, articulation points,
egress redundancy and destination reachability.

Everything is brute force.  Articulation points are found by deleting each node
and re-running a search; the minimum internal node cut is found by enumerating
subsets of internal nodes in increasing size.  On a five-node village graph that
is instant, and it is impossible to get subtly wrong.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable

from .. import mutations
from .network import Network, enumerate_simple_paths, load_network


def _undirected_adjacency(network: Network, removed: Iterable[str] = ()) -> dict[str, set[str]]:
    removed = set(removed)
    adjacency: dict[str, set[str]] = {n: set() for n in network.nodes if n not in removed}
    for edge in network.edges:
        if edge.tail in removed or edge.head in removed:
            continue
        adjacency[edge.tail].add(edge.head)
        adjacency[edge.head].add(edge.tail)
    return adjacency


def _directed_adjacency(network: Network) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {n: set() for n in network.nodes}
    for edge in network.edges:
        adjacency[edge.tail].add(edge.head)
        reverse_allowed = not edge.directed
        # MUTATION HOOK: treat one-way roads as bidirectional.
        if mutations.active("allow_reverse_travel"):
            reverse_allowed = True
        if reverse_allowed:
            adjacency[edge.head].add(edge.tail)
    return adjacency


def reachable(adjacency: dict[str, set[str]], source: str) -> set[str]:
    if source not in adjacency:
        return set()
    seen, stack = {source}, [source]
    while stack:
        current = stack.pop()
        for nxt in adjacency.get(current, ()):  # pragma: no branch
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def connected_components(adjacency: dict[str, set[str]]) -> list[list[str]]:
    seen: set[str] = set()
    components = []
    for node in sorted(adjacency):
        if node in seen:
            continue
        component = reachable(adjacency, node)
        seen |= component
        components.append(sorted(component))
    return components


def articulation_points(network: Network) -> list[str]:
    base = len(connected_components(_undirected_adjacency(network)))
    points = []
    for node in sorted(network.nodes):
        adjacency = _undirected_adjacency(network, removed=[node])
        if not adjacency:
            continue
        if len(connected_components(adjacency)) > base:
            points.append(node)
    return points


def bridges(network: Network) -> list[str]:
    base = len(connected_components(_undirected_adjacency(network)))
    out = []
    for edge in network.edges:
        adjacency: dict[str, set[str]] = {n: set() for n in network.nodes}
        for other in network.edges:
            if other.id == edge.id:
                continue
            adjacency[other.tail].add(other.head)
            adjacency[other.head].add(other.tail)
        if len(connected_components(adjacency)) > base:
            out.append(edge.id)
    return out


def min_internal_node_cut(network: Network, source: str, targets: list[str]) -> dict:
    """Smallest set of non-terminal nodes whose removal cuts source from all targets."""
    internal = [n for n in sorted(network.nodes) if n != source and n not in targets]
    for size in range(0, len(internal) + 1):
        for subset in itertools.combinations(internal, size):
            adjacency = _undirected_adjacency(network, removed=subset)
            if source not in adjacency:
                continue
            seen = reachable(adjacency, source)
            if not any(t in seen for t in targets):
                return {"size": size, "cut": list(subset)}
    return {"size": len(internal) + 1, "cut": None}


def solve(inputs: dict) -> dict:
    network = load_network(inputs["network"])
    query = inputs.get("query", {}) or {}
    source = str(query.get("source"))
    destinations = [str(d) for d in query.get("destinations", [])]

    directed = _directed_adjacency(network)
    reach = reachable(directed, source)

    per_destination = {}
    for destination in destinations:
        paths = enumerate_simple_paths(network, source, destination)
        node = network.nodes.get(destination)
        euclid = None
        if node is not None and source in network.nodes:
            origin = network.nodes[source]
            euclid = math.hypot(node.x - origin.x, node.y - origin.y)
        travel_times = []
        for path in paths:
            travel_times.append(sum(edge.travel_time(0.0) for edge, _ in path))
        per_destination[destination] = {
            "reachable": destination in reach,
            "simple_path_count": len(paths),
            "paths": [[edge.id for edge, _ in path] for path in paths],
            "euclidean_distance_m": euclid,
            "min_travel_time_min": min(travel_times) if travel_times else None,
        }

    reachable_destinations = [d for d in destinations if per_destination[d]["reachable"]]
    unreachable_destinations = [d for d in destinations if not per_destination[d]["reachable"]]

    euclidean_nearest = None
    candidates = [(per_destination[d]["euclidean_distance_m"], d) for d in destinations
                  if per_destination[d]["euclidean_distance_m"] is not None]
    if candidates:
        euclidean_nearest = min(candidates)[1]
    reachable_nearest = None
    reachable_candidates = [
        (per_destination[d]["min_travel_time_min"], d)
        for d in reachable_destinations
        if per_destination[d]["min_travel_time_min"] is not None
    ]
    if reachable_candidates:
        reachable_nearest = min(reachable_candidates)[1]

    selected = reachable_nearest
    # MUTATION HOOK: pick the geographically nearest destination without
    # checking that the road network actually reaches it.
    if mutations.active("euclidean_destination"):
        selected = euclidean_nearest

    cut = min_internal_node_cut(network, source, destinations) if destinations else {"size": None, "cut": None}
    reverse_query = query.get("reverse_reachability", []) or []
    reverse_checks = {}
    for pair in reverse_query:
        origin, destination = str(pair["from"]), str(pair["to"])
        reverse_checks[f"{origin}->{destination}"] = destination in reachable(directed, origin)

    return {
        "node_count": len(network.nodes),
        "edge_count": len(network.edges),
        "components": len(connected_components(_undirected_adjacency(network))),
        "articulation_points": articulation_points(network),
        "bridges": bridges(network),
        "destinations": per_destination,
        "reachable_destinations": reachable_destinations,
        "unreachable_destinations": unreachable_destinations,
        "euclidean_nearest_destination": euclidean_nearest,
        "reachable_nearest_destination": reachable_nearest,
        "selected_destination": selected,
        "min_internal_node_cut": cut["size"],
        "min_internal_node_cut_set": cut["cut"],
        "single_point_of_failure": cut["size"] == 1,
        "node_disjoint_egress_paths": cut["size"],
        "reachability_checks": reverse_checks,
    }
