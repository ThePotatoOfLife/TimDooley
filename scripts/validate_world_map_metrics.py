#!/usr/bin/env python3
"""Validate the generated cross-country metric runtime for the World Atlas."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
RUNTIME = Path(os.environ.get("ATLAS_METRICS_PATH", ROOT / "data" / "world-country-metrics.json"))


def main() -> int:
    errors: list[str] = []
    if not RUNTIME.exists():
        print(f"ERROR: missing metric runtime: {RUNTIME}")
        return 1
    try:
        payload = json.loads(RUNTIME.read_text(encoding="utf-8"))
        index = json.loads(INDEX.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: invalid metric/index JSON: {exc}")
        return 1

    canonical = {row["iso3"] for row in index.get("countries", []) if row.get("iso3")}
    metrics = payload.get("metrics") or {}
    countries = payload.get("countries") or {}
    required_registry = {"population", "gdp", "gdp_per_capita", "real_growth", "unemployment", "life_expectancy"}
    missing_registry = sorted(required_registry - set(metrics))
    if missing_registry:
        errors.append(f"metric registry missing required ids: {missing_registry}")

    for metric_id, definition in metrics.items():
        if not isinstance(definition, dict):
            errors.append(f"metric {metric_id} definition is not an object")
            continue
        for key in ("label", "unit", "transform", "direction"):
            if not definition.get(key): errors.append(f"metric {metric_id} missing {key}")
        indicator = definition.get("indicator")
        if metric_id != "population_density" and not indicator:
            errors.append(f"metric {metric_id} missing source indicator")

    coverage: dict[str, int] = {metric_id: 0 for metric_id in metrics}
    for iso3, row in countries.items():
        if iso3 not in canonical:
            errors.append(f"metric runtime references noncanonical ISO3: {iso3}")
        if not isinstance(row, dict):
            errors.append(f"country {iso3} metrics row is not an object")
            continue
        for metric_id, observation in row.items():
            definition = metrics.get(metric_id)
            if not definition:
                errors.append(f"country {iso3} uses undeclared metric {metric_id}")
                continue
            if not isinstance(observation, dict):
                errors.append(f"{iso3}/{metric_id} observation is not an object")
                continue
            value = observation.get("value")
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                errors.append(f"{iso3}/{metric_id} has non-finite numeric value: {value!r}")
                continue
            if observation.get("period") in (None, ""):
                errors.append(f"{iso3}/{metric_id} missing period")
            if observation.get("source") in (None, ""):
                errors.append(f"{iso3}/{metric_id} missing source")
            expected = definition.get("indicator")
            source_id = observation.get("source_id")
            if expected and source_id and source_id != expected:
                errors.append(f"{iso3}/{metric_id} source_id {source_id} != registry {expected}")
            coverage[metric_id] = coverage.get(metric_id, 0) + 1

    for metric_id in ("population", "gdp"):
        if coverage.get(metric_id, 0) < 150:
            errors.append(f"{metric_id} coverage too low: {coverage.get(metric_id, 0)} < 150")

    for metric_id, definition in metrics.items():
        declared = definition.get("coverage")
        if declared is not None and int(declared) != coverage.get(metric_id, 0):
            errors.append(f"metric {metric_id} coverage metadata {declared} != observed {coverage.get(metric_id, 0)}")
        domain = definition.get("display_domain")
        if domain is not None:
            if not isinstance(domain, list) or len(domain) != 2 or not all(isinstance(v, (int, float)) and math.isfinite(float(v)) for v in domain):
                errors.append(f"metric {metric_id} has invalid display_domain {domain!r}")

    print(f"Metric registry: {len(metrics)} metrics · {len(countries)} country rows")
    print("Coverage:", ", ".join(f"{key}={value}" for key, value in sorted(coverage.items())))
    if errors:
        print("WORLD MAP METRIC VALIDATION FAILED")
        for error in errors: print("-", error)
        return 1
    print("WORLD MAP METRIC VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
