"""Reference solver for forecast calibration (the M family).

Deliberately tiny. This is not a calibration library: it computes the reliability
of a set of exactly specified forecast/outcome groups, decomposes the Brier score
the way Murphy did, and asks the only question the benchmark suite cares about -
**does the miscalibration change an action under the declared loss matrix?**

Rows are grouped two ways: by forecast probability alone (the aggregate view) and
by forecast probability within a declared stratum (the conditional view). A
forecast can be perfect in the first and badly wrong in the second, which is what
WG-BM-066 pins down.
"""

from __future__ import annotations

from .. import mutations


def _summarise(rows: list[dict]) -> dict:
    total = sum(r["n"] for r in rows)
    events = sum(r["events"] for r in rows)
    base_rate = events / total
    groups: dict[str, dict] = {}
    reliability = resolution = ece = brier = 0.0
    for row in rows:
        weight = row["n"] / total
        observed = row["events"] / row["n"]
        forecast = row["p"]
        reliability += weight * (forecast - observed) ** 2
        resolution += weight * (observed - base_rate) ** 2
        ece += weight * abs(forecast - observed)
        brier += weight * (observed * (1 - forecast) ** 2 + (1 - observed) * forecast ** 2)
        groups[row["id"]] = {
            "forecast_probability": forecast,
            "n": row["n"],
            "events": row["events"],
            "observed_frequency": observed,
            "calibration_error": forecast - observed,
        }
    uncertainty = base_rate * (1 - base_rate)
    return {
        "groups": groups,
        "n": total,
        "base_rate": base_rate,
        "expected_calibration_error": ece,
        "brier_score": brier,
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": uncertainty,
        "murphy_residual": brier - (reliability - resolution + uncertainty),
        "perfectly_calibrated": ece < 1e-12,
    }


def _rows(document: dict, key) -> list[dict]:
    merged: dict[str, dict] = {}
    for raw in document["groups"]:
        identifier = key(raw)
        entry = merged.setdefault(
            identifier, {"id": identifier, "p": float(raw["forecast_probability"]), "n": 0, "events": 0}
        )
        entry["n"] += int(raw["n"])
        entry["events"] += int(raw["events"])
    return [merged[k] for k in sorted(merged)]


def solve(inputs: dict) -> dict:
    document = inputs["calibration"]
    aggregate = _summarise(_rows(document, lambda r: f"p={float(r['forecast_probability']):g}"))
    has_strata = any("stratum" in r for r in document["groups"])
    stratified = (
        _summarise(
            _rows(
                document,
                lambda r: f"{r.get('stratum', 'all')}|p={float(r['forecast_probability']):g}",
            )
        )
        if has_strata
        else None
    )

    reported_conditional = stratified["expected_calibration_error"] if stratified else None
    # MUTATION HOOK: report the aggregate reliability as if it were the
    # conditional one, so a regime-specific failure is hidden by the average.
    if stratified and mutations.active("aggregate_calibration_only"):
        reported_conditional = aggregate["expected_calibration_error"]

    result = {
        "aggregate": aggregate,
        "aggregate_calibration_error": aggregate["expected_calibration_error"],
        "brier_score": aggregate["brier_score"],
        "reliability": aggregate["reliability"],
        "resolution": aggregate["resolution"],
        "uncertainty": aggregate["uncertainty"],
        "murphy_residual": aggregate["murphy_residual"],
        "base_rate": aggregate["base_rate"],
        "perfectly_calibrated": aggregate["perfectly_calibrated"],
    }
    if stratified:
        result["stratified"] = stratified
        result["stratified_calibration_error"] = reported_conditional
        result["aggregate_hides_stratum_failure"] = (
            aggregate["expected_calibration_error"] < 1e-12
            and stratified["expected_calibration_error"] > 1e-12
        )

    decision = document.get("decision")
    if decision:
        loss = {
            str(a): {str(s): float(v) for s, v in row.items()}
            for a, row in decision["loss"].items()
        }
        actions = sorted(loss)
        event, no_event = str(decision.get("event_state", "event")), str(
            decision.get("no_event_state", "no_event")
        )

        def act(probability: float) -> str:
            return min(
                actions,
                key=lambda a: probability * loss[a][event] + (1 - probability) * loss[a][no_event],
            )

        def cost(action: str, probability: float) -> float:
            return probability * loss[action][event] + (1 - probability) * loss[action][no_event]

        rows = _rows(
            document,
            lambda r: f"{r.get('stratum', 'all')}|p={float(r['forecast_probability']):g}",
        ) if has_strata else _rows(document, lambda r: f"p={float(r['forecast_probability']):g}")

        per_group = {}
        total_excess = 0.0
        for row in rows:
            observed = row["events"] / row["n"]
            forecast_action = act(row["p"])
            oracle_action = act(observed)
            excess = cost(forecast_action, observed) - cost(oracle_action, observed)
            total_excess += row["n"] * excess
            per_group[row["id"]] = {
                "forecast_probability": row["p"],
                "observed_frequency": observed,
                "action_from_forecast": forecast_action,
                "action_from_observed_frequency": oracle_action,
                "action_differs": forecast_action != oracle_action,
                "excess_expected_loss_per_case": excess,
            }
        result["decision"] = {
            "decision_threshold_probability": (
                (loss[actions[1]][no_event] - loss[actions[0]][no_event])
                / (
                    (loss[actions[0]][event] - loss[actions[1]][event])
                    - (loss[actions[0]][no_event] - loss[actions[1]][no_event])
                )
                if len(actions) == 2
                else None
            ),
            "by_group": per_group,
            "groups_with_different_action": sorted(
                k for k, v in per_group.items() if v["action_differs"]
            ),
            "total_excess_expected_loss": total_excess,
            "excess_expected_loss_per_case": total_excess / aggregate["n"],
        }
    return result
