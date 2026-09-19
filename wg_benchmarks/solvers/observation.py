"""Observation-availability reference solver.

The single rule this module exists to enforce: **an observation acquired at
time ``t_a`` by a sensor with latency ``L`` is available to a decision maker at
time ``t`` if and only if ``t_a + L <= t``.**  Everything else here is
bookkeeping around that rule — staleness, outages, informative missingness and
false negatives.

Missing is not zero, stale is not current, and silence is not safety.
"""

from __future__ import annotations

from .. import mutations

INF = float("inf")


def available_records(sensor: dict, at_time: float) -> list[dict]:
    latency = float(sensor.get("latency_min", 0.0))
    # MUTATION HOOK: latency dropped, so the decision maker reads the future.
    if mutations.active("observation_future_leak"):
        latency = 0.0
    return [
        record
        for record in sensor.get("records", [])
        if float(record["acquisition_time_min"]) + latency <= at_time + 1e-12
    ]


def query_sensor(sensor: dict, at_time: float, max_staleness_min: float) -> dict:
    records = available_records(sensor, at_time)
    if not records:
        return {
            "available_records": 0,
            "latest_acquisition_time_min": None,
            "value": None,
            "staleness_min": None,
            "stale": True,
            "status": "no_data",
        }
    latest = max(records, key=lambda r: float(r["acquisition_time_min"]))
    acquisition = float(latest["acquisition_time_min"])
    staleness = at_time - acquisition
    stale = staleness > max_staleness_min + 1e-12
    value = latest["value"]
    status = "stale" if stale else "current"
    if stale:
        value_reported = None
        # MUTATION HOOK: hand back the last value as if it were current.
        if mutations.active("silent_carry_forward"):
            value_reported = value
            stale = False
            status = "current"
        # MUTATION HOOK: missing data imputed as zero.
        elif mutations.active("missing_as_zero"):
            value_reported = 0.0
            status = "current"
    else:
        value_reported = value
    return {
        "available_records": len(records),
        "latest_acquisition_time_min": acquisition,
        "value": value_reported,
        "last_known_value": value,
        "staleness_min": staleness,
        "stale": stale,
        "status": status,
    }


def solve(inputs: dict) -> dict:
    document = inputs["observations"]
    sensors = {str(s["id"]): s for s in document.get("sensors", [])}
    truth = {float(t["time_min"]): t["value"] for t in document.get("truth", [])}
    max_staleness = float(document.get("max_staleness_min", 0.0))

    queries: dict[str, dict] = {}
    for query in document.get("queries", []):
        sensor = sensors[str(query["sensor"])]
        at_time = float(query["at_time_min"])
        outcome = query_sensor(sensor, at_time, float(query.get("max_staleness_min", max_staleness)))
        if at_time in truth:
            outcome["truth_value"] = truth[at_time]
            if isinstance(outcome["value"], (int, float)) and isinstance(truth[at_time], (int, float)):
                outcome["error"] = float(outcome["value"]) - float(truth[at_time])
                outcome["matches_truth"] = abs(outcome["error"]) < 1e-12
            else:
                outcome["error"] = None
                outcome["matches_truth"] = outcome["value"] == truth[at_time]
        queries[str(query["id"])] = outcome

    result: dict = {"queries": queries}

    mnar = document.get("mnar_query")
    if mnar:
        at_time = float(mnar["at_time_min"])
        reporting, silent = [], []
        for sensor_id, sensor in sorted(sensors.items()):
            hazard = sensor.get("hazard_arrival_min")
            hazard = INF if hazard is None else float(hazard)
            if hazard <= at_time:
                silent.append(sensor_id)
            else:
                reporting.append(sensor_id)
        burning_value = float(mnar["burning_value"])
        unburnt_value = float(mnar["unburnt_value"])
        observed_values = [unburnt_value for _ in reporting]
        truth_values = [burning_value for _ in silent] + [unburnt_value for _ in reporting]
        observed_mean = sum(observed_values) / len(observed_values) if observed_values else None
        true_mean = sum(truth_values) / len(truth_values)
        # MUTATION HOOK: assume the dropouts are missing at random and simply
        # average whatever is still reporting.
        if mutations.active("ignore_informative_missingness"):
            corrected_mean = observed_mean
            informative = False
        else:
            corrected_mean = (
                burning_value * len(silent) + unburnt_value * len(reporting)
            ) / (len(silent) + len(reporting))
            informative = bool(silent) and all(
                float(sensors[s].get("hazard_arrival_min", INF)) <= at_time for s in silent
            )
        result["mnar"] = {
            "at_time_min": at_time,
            "reporting_sensors": reporting,
            "silent_sensors": silent,
            "observed_mean": observed_mean,
            "true_mean": true_mean,
            "naive_bias": None if observed_mean is None else observed_mean - true_mean,
            "dropout_aware_mean": corrected_mean,
            "dropout_aware_bias": None if corrected_mean is None else corrected_mean - true_mean,
            "missingness_informative": informative,
        }

    detection = document.get("detection_query")
    if detection:
        cells = detection["cells"]
        true_fire = sorted(c["id"] for c in cells if c["true_fire"])
        detected = sorted(c["id"] for c in cells if c["detected"])
        false_negatives = sorted(c["id"] for c in cells if c["true_fire"] and not c["detected"])
        confirmed_clear = sorted(
            c["id"] for c in cells if not c["detected"] and c.get("detection_reliable", False)
        )
        routes = detection["routes"]

        def route_loss(route: dict, treat_undetected_as_safe: bool) -> float:
            crosses = [c for c in cells if c["id"] in route["cells"]]
            if treat_undetected_as_safe:
                hazardous = any(c["detected"] for c in crosses)
            else:
                hazardous = any(
                    c["detected"] or not c.get("detection_reliable", False) for c in crosses
                )
            return float(route["loss_if_hazardous"] if hazardous else route["loss_if_clear"])

        def choose(treat_undetected_as_safe: bool) -> str:
            scored = sorted(
                (route_loss(r, treat_undetected_as_safe), r["id"]) for r in routes
            )
            return scored[0][1]

        def realised_loss(route_id: str) -> float:
            route = next(r for r in routes if r["id"] == route_id)
            hazardous = any(c["true_fire"] for c in cells if c["id"] in route["cells"])
            return float(route["loss_if_hazardous"] if hazardous else route["loss_if_clear"])

        trusting = choose(True)
        precaution_flag = False
        # MUTATION HOOK: no detection is read as no hazard even where the
        # detector is known to be unreliable.
        if mutations.active("assume_missing_is_safe"):
            precaution_flag = True
        precautionary = choose(True) if precaution_flag else choose(False)
        result["detection"] = {
            "true_fire_cells": true_fire,
            "detected_cells": detected,
            "false_negative_cells": false_negatives,
            "reliably_clear_cells": confirmed_clear,
            "false_negative_present": bool(false_negatives),
            "route_trusting_detections": trusting,
            "loss_trusting_detections": realised_loss(trusting),
            "route_precautionary": precautionary,
            "loss_precautionary": realised_loss(precautionary),
            "regret_of_trusting": realised_loss(trusting) - realised_loss(precautionary),
        }

    return result
