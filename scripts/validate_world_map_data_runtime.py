#!/usr/bin/env python3
"""Validate the generated empirical data contract for the ordinary World Map."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "build_world_map_runtime.py"
MEMBERSHIPS = ROOT / "data" / "world-institution-memberships.json"
REGISTRY = ROOT / "data" / "world-map-layer-registry.json"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"
CARD = ROOT / "world-map" / "3d-country-card.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
BUILD_SITE = ROOT / "scripts" / "build_site.py"

REQUIRED_GROUPS = {
    "eu": 27,
    "nato": 32,
    "brics": 11,
    "aukus": 3,
    "five-eyes": 5,
    "oecd": 38,
    "g7": 7,
    "g20": 19,
    "schengen": 29,
    "euro-area": 21,
}
CURRENT_STATS = {
    "stat.gdp-per-capita": "gdp_per_capita",
    "stat.gdp-per-capita-ppp": "gdp_per_capita_ppp",
    "stat.real-growth": "real_growth",
    "stat.inflation": "inflation",
    "stat.unemployment": "unemployment",
    "stat.labour-force-participation": "labour_force_participation",
    "stat.life-expectancy": "life_expectancy",
    "stat.fertility": "fertility",
    "stat.urbanization": "urbanization",
    "stat.internet-use": "internet_use",
    "stat.co2-per-capita": "co2_per_capita",
}
GATED_STATS = {"stat.debt-to-gdp": "debt_to_gdp"}
RUNTIME_STATS = {**CURRENT_STATS, **GATED_STATS}


def load_json(path: Path, errors: list[str]):
    if not path.is_file():
        errors.append(f"missing required World Map runtime source: {path.relative_to(ROOT)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}


def read(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required World Map runtime file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def load_generator(errors: list[str]):
    if not GENERATOR.is_file():
        errors.append("missing scripts/build_world_map_runtime.py")
        return None
    spec = importlib.util.spec_from_file_location("build_world_map_runtime", GENERATOR)
    if not spec or not spec.loader:
        errors.append("could not load scripts/build_world_map_runtime.py")
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "build_runtime"):
        errors.append("World Map runtime generator must expose build_runtime()")
        return None
    return module


def main() -> int:
    errors: list[str] = []
    memberships = load_json(MEMBERSHIPS, errors)
    registry = load_json(REGISTRY, errors)
    compositor = read(COMPOSITOR, errors)
    card = read(CARD, errors)
    world_bar = read(WORLD_BAR, errors)
    build_site = read(BUILD_SITE, errors)
    generator = load_generator(errors)

    groups = memberships.get("groups", {}) if isinstance(memberships, dict) else {}
    for group_id, expected_count in REQUIRED_GROUPS.items():
        group = groups.get(group_id, {})
        members = group.get("members", []) if isinstance(group, dict) else []
        if len(members) != expected_count:
            errors.append(f"{group_id} must expose {expected_count} ISO3 country members; found {len(members)}")
        if len(set(members)) != len(members) or any(not isinstance(code, str) or len(code) != 3 or code != code.upper() for code in members):
            errors.append(f"{group_id} membership must be unique uppercase ISO3 codes")
        for key in ("source", "source_url", "as_of"):
            if not group.get(key):
                errors.append(f"{group_id} membership must retain {key}")
    if groups.get("g20", {}).get("non_country_members") != ["African Union", "European Union"]:
        errors.append("G20 must record African Union and European Union as non-country members")
    if "BGR" not in groups.get("euro-area", {}).get("members", []):
        errors.append("2026 Euro Area membership must include Bulgaria (BGR)")

    entries = {entry.get("id"): entry for entry in registry.get("entries", []) if isinstance(entry, dict)}
    for group_id in REQUIRED_GROUPS:
        entry = entries.get(f"group.{group_id}", {})
        if entry.get("availability") != "current":
            errors.append(f"group.{group_id} must be current in the map registry")
        if entry.get("source_owner") != "data/world-institution-memberships.json":
            errors.append(f"group.{group_id} must point to canonical institutional memberships")
    for entry_id, runtime_metric in CURRENT_STATS.items():
        entry = entries.get(entry_id, {})
        if entry.get("availability") != "current":
            errors.append(f"{entry_id} must be current in the map registry")
        if entry.get("source_owner") != "data/world-map-data-runtime.json":
            errors.append(f"{entry_id} must use the generated World Map data runtime")
        if entry.get("runtime_metric") != runtime_metric:
            errors.append(f"{entry_id} must declare runtime_metric={runtime_metric}")
    for entry_id, runtime_metric in GATED_STATS.items():
        entry = entries.get(entry_id, {})
        if entry.get("availability") != "planned":
            errors.append(f"{entry_id} must remain planned until comparable canonical coverage exists")
        if entry.get("source_owner") != "data/world-map-data-runtime.json":
            errors.append(f"{entry_id} must still point at the generated runtime for future promotion")
        if entry.get("runtime_metric") != runtime_metric:
            errors.append(f"{entry_id} must declare runtime_metric={runtime_metric}")

    for token in (
        "WORLD_DATA_RUNTIME_URL",
        "__potatoAtlasDataRuntime",
        "applyRuntimeScalar",
        "runtime_metric",
        "coverage",
    ):
        if token not in compositor:
            errors.append(f"compositor missing runtime integration marker: {token}")
    for token in ("__potatoAtlasDataRuntime", "runtime_metric", "metricMeta", "populationObservation", "areaObservation"):
        if token not in card:
            errors.append(f"country card missing shared runtime marker: {token}")
    for token in ("__potatoAtlasDataRuntime", "coverage", "countries"):
        if token not in world_bar:
            errors.append(f"lower-left context missing runtime coverage marker: {token}")
    if "build_world_map_runtime" not in build_site:
        errors.append("build_site.py must generate the World Map data runtime before copying the public tree")

    if generator:
        try:
            runtime = generator.build_runtime()
        except Exception as exc:
            errors.append(f"build_runtime() failed: {exc}")
            runtime = {}
        if runtime:
            if runtime.get("country_count") != 195:
                errors.append(f"runtime must cover canonical 195-country index; found {runtime.get('country_count')}")
            runtime_groups = runtime.get("groups", {})
            for group_id, expected_count in REQUIRED_GROUPS.items():
                if runtime_groups.get(group_id, {}).get("member_count") != expected_count:
                    errors.append(f"runtime group {group_id} has incorrect member_count")
            metrics = runtime.get("metrics", {})
            countries = runtime.get("countries", {})
            for metric in RUNTIME_STATS.values():
                meta = metrics.get(metric, {})
                coverage = meta.get("coverage", 0)
                if not isinstance(coverage, int) or coverage < 0 or coverage > 195:
                    errors.append(f"runtime metric {metric} has invalid coverage: {coverage}")
                if not meta.get("unit"):
                    errors.append(f"runtime metric {metric} must declare a comparable unit")
            for metric in CURRENT_STATS.values():
                if metrics.get(metric, {}).get("coverage", 0) <= 0:
                    errors.append(f"current runtime metric {metric} must have real canonical coverage")
            if metrics.get("debt_to_gdp", {}).get("coverage", 0) == 0 and entries.get("stat.debt-to-gdp", {}).get("availability") == "current":
                errors.append("debt/GDP cannot be current with zero comparable canonical coverage")
            for code, country in countries.items():
                for metric_id, cell in country.get("metrics", {}).items():
                    if cell.get("value") == 0 and cell.get("missing") is True:
                        errors.append(f"{code}/{metric_id} converts missing data to zero")
                    for key in ("value", "unit", "period", "source"):
                        if key not in cell:
                            errors.append(f"{code}/{metric_id} metric cell missing {key}")
            scalars = runtime.get("scalars", {}).get("by_entity", {})
            if scalars.get("GRL", {}).get("population", {}).get("value") != 56740:
                errors.append("runtime scalar plane must expose Greenland population")
            if scalars.get("GRL", {}).get("area", {}).get("value") != 2166086:
                errors.append("runtime scalar plane must expose Greenland area")

    if errors:
        print("World Map data runtime validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("World Map data runtime validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
