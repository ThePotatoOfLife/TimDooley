#!/usr/bin/env python3
"""Validate the generic subdivision integration surface."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_world_subdivisions.py"
MODULE = ROOT / "world-map" / "3d-subdivisions.js"
GEO_KERNEL = ROOT / "world-map" / "3d-geo-kernel.js"
SCALE = ROOT / "world-map" / "3d-scale.js"
SCALE_CONTRACT = ROOT / "data" / "world-map-scale-contract.json"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
INDEX = ROOT / "data" / "world-subdivisions" / "index.json"
USA = ROOT / "data" / "world-subdivisions" / "USA.geo.json"
DNK = ROOT / "data" / "world-subdivisions" / "DNK.geo.json"
CAN = ROOT / "data" / "world-subdivisions" / "CAN.geo.json"
GEO_KERNEL_REGRESSION = ROOT / "scripts" / "test_world_map_geo_kernel.mjs"
WRAP_MATH_REGRESSION = ROOT / "scripts" / "test_world_map_subdivision_wrap_math.mjs"
FREEZE_REGRESSION = ROOT / "scripts" / "test_world_map_subdivision_freeze.mjs"
MULTI_COUNTRY_REGRESSION = ROOT / "scripts" / "test_world_map_subdivision_multi_country.mjs"
BOUNDED_RUNTIME_REGRESSION = ROOT / "scripts" / "test_world_map_subdivision_bounded_runtime.mjs"
EXPECTED_RUNTIME_BUDGET = {
    "partition_max_bytes": 1_500_000,
    "rendered_max_bytes": 3_000_000,
    "rendered_max_partitions": 4,
    "cache_max_bytes": 6_000_000,
    "cache_max_partitions": 8,
}


def main() -> int:
    errors: list[str] = []
    required = (
        BUILDER, MODULE, GEO_KERNEL, SCALE, SCALE_CONTRACT, LIFECYCLE, INDEX, USA, DNK, CAN,
        GEO_KERNEL_REGRESSION, WRAP_MATH_REGRESSION,
        FREEZE_REGRESSION, MULTI_COUNTRY_REGRESSION, BOUNDED_RUNTIME_REGRESSION,
    )
    for path in required:
        if not path.exists():
            errors.append(f"missing subdivision integration file: {path.relative_to(ROOT)}")
    if not errors:
        builder = BUILDER.read_text(encoding="utf-8")
        module = MODULE.read_text(encoding="utf-8")
        geo_kernel = GEO_KERNEL.read_text(encoding="utf-8")
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        scale_contract = json.loads(SCALE_CONTRACT.read_text(encoding="utf-8"))
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        usa = json.loads(USA.read_text(encoding="utf-8"))
        dnk = json.loads(DNK.read_text(encoding="utf-8"))
        can = json.loads(CAN.read_text(encoding="utf-8"))
        for token in ("GENZ2025", "cb_2025_us_state_20m.zip", "NST-EST2025-ALLDATA.csv", "EXPECTED_US_UNITS = 51", "parse_state_kml", "federal district"):
            if token not in builder:
                errors.append(f"subdivision builder missing marker: {token}")
        for token in (
            "world-subdivisions/index.json", "USA.geo.json", "atlas-subdivision",
            "searchParams.get('subdivision')", "searchParams.set('subdivision'", "searchParams.delete('subdivision')",
            "potato-atlas-subdivision-select", "pendingDeepLinkId",
            "id_prefix", "viewport_bounds", "partitionForId",
            "window.__potatoAtlasGeo", "unwrappedInterval", "distanceToMapCenterKm", "haversineDistanceKm",
        ):
            if token not in module:
                errors.append(f"subdivision module missing marker: {token}")
        for token in (
            "normalizeLongitude", "shortestLongitudeDelta", "unwrapLongitude",
            "minimalLongitudeInterval", "antimeridianAwareBounds", "haversineDistanceKm",
        ):
            if token not in geo_kernel:
                errors.append(f"geospatial kernel missing marker: {token}")
        geo_load = lifecycle.find("__potatoAtlasLoadModule?.('Geo Kernel', './3d-geo-kernel.js')")
        scale_load = lifecycle.find("__potatoAtlasLoadModule?.('Scale', './3d-scale.js')")
        subdivision_load = lifecycle.find("__potatoAtlasLoadModule?.('Subdivisions', './3d-subdivisions.js')")
        if geo_load < 0:
            errors.append("shared Geo Kernel is not registered before geographic detail modules")
        if scale_load < 0 or "capabilityActive('subdivisions', 'load'" not in lifecycle:
            errors.append("regional-scale lazy subdivision loading is not owned by the Scale contract")
        if subdivision_load < 0:
            errors.append("lazy Subdivisions module loading is not registered")
        if "map.getZoom() < 3.4" in lifecycle:
            errors.append("panel lifecycle still owns the old raw 3.4 subdivision threshold")
        if geo_load >= 0 and scale_load >= 0 and geo_load >= scale_load:
            errors.append("Geo Kernel must load before Scale")
        if scale_load >= 0 and subdivision_load >= 0 and scale_load >= subdivision_load:
            errors.append("Scale must load before Subdivisions")
        if scale_contract.get("capabilities", {}).get("subdivisions", {}).get("load") != 3.4:
            errors.append("Scale contract must preserve the first-wave subdivision load threshold at 3.4")

        budget = index.get("runtime_budget")
        if budget != EXPECTED_RUNTIME_BUDGET:
            errors.append(f"subdivision runtime budget mismatch: {budget!r}")

        partitions = index.get("partitions", {})
        for partition, descriptor in partitions.items():
            path = ROOT / "data" / "world-subdivisions" / str(descriptor.get("path") or "")
            if not path.exists():
                errors.append(f"{partition}: partition path is missing")
                continue
            actual_bytes = path.stat().st_size
            if descriptor.get("bytes") != actual_bytes:
                errors.append(f"{partition}: descriptor bytes must equal {actual_bytes}")
            if actual_bytes > EXPECTED_RUNTIME_BUDGET["partition_max_bytes"]:
                errors.append(f"{partition}: partition exceeds hard byte budget")

        usa_descriptor = partitions.get("USA", {})
        if usa_descriptor.get("feature_count") != 51:
            errors.append("USA subdivision index must declare 51 first-wave features")
        if usa_descriptor.get("id_prefix") != "US-" or not isinstance(usa_descriptor.get("viewport_bounds"), dict):
            errors.append("USA subdivision descriptor must declare id_prefix and viewport_bounds")
        features = usa.get("features", []) if usa.get("type") == "FeatureCollection" else []
        if len(features) != 51:
            errors.append(f"USA subdivision snapshot must contain 51 features; found {len(features)}")
        ids = [str((feature.get("properties") or {}).get("id") or "") for feature in features]
        if len(set(ids)) != 51 or not all(value.startswith("US-") for value in ids):
            errors.append("USA subdivision ids must be 51 unique US-* identifiers")
        dc = next((feature for feature in features if (feature.get("properties") or {}).get("id") == "US-DC"), None)
        if not dc or dc.get("properties", {}).get("subdivision_type") != "federal district":
            errors.append("District of Columbia must remain explicitly typed as a federal district")
        for feature in features:
            props = feature.get("properties") or {}
            population = props.get("population") or {}
            if not isinstance(population.get("value"), (int, float)) or population.get("value", 0) <= 0:
                errors.append(f"{props.get('id')}: missing positive population")
            if population.get("period") != 2025 or population.get("unit") != "persons" or not population.get("source"):
                errors.append(f"{props.get('id')}: incomplete population provenance")
            if not props.get("area_definition") or "ALAND" not in props.get("area_definition", ""):
                errors.append(f"{props.get('id')}: area provenance is not explicit")

        dnk_descriptor = partitions.get("DNK", {})
        if dnk_descriptor.get("feature_count") != 5:
            errors.append("DNK subdivision index must declare 5 region features")
        if dnk_descriptor.get("id_prefix") != "DK-":
            errors.append("DNK subdivision descriptor must declare DK- id_prefix")
        if dnk_descriptor.get("parent_name") != "Denmark" or not isinstance(dnk_descriptor.get("viewport_bounds"), dict):
            errors.append("DNK subdivision descriptor must declare Denmark parent and viewport bounds")
        if "DAWA" not in str(dnk_descriptor.get("source") or "") and "Dataforsyningen" not in str(dnk_descriptor.get("source") or ""):
            errors.append("DNK subdivision descriptor must retain official DAWA/Dataforsyningen provenance")
        if dnk_descriptor.get("population_status") != "unknown-not-zero":
            errors.append("DNK missing population must remain explicitly unknown-not-zero")
        dnk_features = dnk.get("features", []) if dnk.get("type") == "FeatureCollection" else []
        if len(dnk_features) != 5:
            errors.append(f"DNK subdivision snapshot must contain 5 features; found {len(dnk_features)}")
        dnk_ids = [str((feature.get("properties") or {}).get("id") or "") for feature in dnk_features]
        if len(set(dnk_ids)) != 5 or not all(value.startswith("DK-") for value in dnk_ids):
            errors.append("DNK subdivision ids must be 5 unique DK-* identifiers")
        for feature in dnk_features:
            props = feature.get("properties") or {}
            if props.get("subdivision_type") != "region":
                errors.append(f"{props.get('id')}: Danish first-order subdivision must be typed region")
            provenance = f"{props.get('geometry_source') or ''} {props.get('geometry_source_url') or ''}"
            if "DAWA" not in provenance and "Dataforsyningen" not in provenance and "dataforsyningen.dk" not in provenance:
                errors.append(f"{props.get('id')}: missing official Danish geometry provenance")
            population = props.get("population")
            if isinstance(population, dict) and isinstance(population.get("value"), (int, float)):
                errors.append(f"{props.get('id')}: Denmark population must not be invented in geometry-first snapshot")

        can_descriptor = partitions.get("CAN", {})
        if can_descriptor.get("feature_count") != 13:
            errors.append("CAN subdivision index must declare 13 province/territory features")
        if can_descriptor.get("id_prefix") != "CA-":
            errors.append("CAN subdivision descriptor must declare CA- id_prefix")
        if can_descriptor.get("parent_name") != "Canada" or not isinstance(can_descriptor.get("viewport_bounds"), dict):
            errors.append("CAN subdivision descriptor must declare Canada parent and viewport bounds")
        if can_descriptor.get("population_status") != "unknown-not-zero":
            errors.append("CAN missing population must remain explicitly unknown-not-zero")
        can_features = can.get("features", []) if can.get("type") == "FeatureCollection" else []
        if len(can_features) != 13:
            errors.append(f"CAN subdivision snapshot must contain 13 features; found {len(can_features)}")
        can_ids = [str((feature.get("properties") or {}).get("id") or "") for feature in can_features]
        if len(set(can_ids)) != 13 or not all(value.startswith("CA-") for value in can_ids):
            errors.append("CAN subdivision ids must be 13 unique CA-* identifiers")
        province_count = 0
        territory_count = 0
        for feature in can_features:
            props = feature.get("properties") or {}
            kind = props.get("subdivision_type")
            if kind == "province":
                province_count += 1
            elif kind == "territory":
                territory_count += 1
            else:
                errors.append(f"{props.get('id')}: Canadian subdivision must be typed province or territory")
            if props.get("parent_iso3") != "CAN" or props.get("parent_name") != "Canada":
                errors.append(f"{props.get('id')}: Canadian parent metadata drift")
            population = props.get("population") or {}
            if population.get("value") is not None:
                errors.append(f"{props.get('id')}: Canada population must not be invented in geometry-first snapshot")
            provenance = f"{props.get('geometry_source') or ''} {props.get('administrative_reference') or ''}"
            if "Statistics Canada" not in provenance:
                errors.append(f"{props.get('id')}: missing Statistics Canada administrative provenance")
        if province_count != 10 or territory_count != 3:
            errors.append(f"Canada subdivision typing must remain 10 provinces + 3 territories; found {province_count}+{territory_count}")

        node = shutil.which("node")
        if node:
            checked = subprocess.run([node, "--check", str(MODULE)], capture_output=True, text=True)
            if checked.returncode:
                errors.append("3d-subdivisions.js syntax failed: " + (checked.stderr.strip() or checked.stdout.strip()))
            geo_checked = subprocess.run([node, "--check", str(GEO_KERNEL)], capture_output=True, text=True)
            if geo_checked.returncode:
                errors.append("3d-geo-kernel.js syntax failed: " + (geo_checked.stderr.strip() or geo_checked.stdout.strip()))
            geo_regression = subprocess.run([node, str(GEO_KERNEL_REGRESSION)], capture_output=True, text=True)
            if geo_regression.returncode:
                errors.append("geospatial-kernel regression failed: " + (geo_regression.stderr.strip() or geo_regression.stdout.strip()))
            wrap = subprocess.run([node, str(WRAP_MATH_REGRESSION)], capture_output=True, text=True)
            if wrap.returncode:
                errors.append("subdivision wrap-math regression failed: " + (wrap.stderr.strip() or wrap.stdout.strip()))
            regression = subprocess.run([node, str(FREEZE_REGRESSION)], capture_output=True, text=True)
            if regression.returncode:
                errors.append("subdivision freeze regression failed: " + (regression.stderr.strip() or regression.stdout.strip()))
            multi = subprocess.run([node, str(MULTI_COUNTRY_REGRESSION)], capture_output=True, text=True)
            if multi.returncode:
                errors.append("multi-country subdivision regression failed: " + (multi.stderr.strip() or multi.stdout.strip()))
            bounded = subprocess.run([node, str(BOUNDED_RUNTIME_REGRESSION)], capture_output=True, text=True)
            if bounded.returncode:
                errors.append("bounded subdivision runtime regression failed: " + (bounded.stderr.strip() or bounded.stdout.strip()))
    if errors:
        print("WORLD MAP SUBDIVISION VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP SUBDIVISION VALIDATION PASSED · USA 51/51 · Denmark 5/5 · Canada 13/13 · wrap-safe geo kernel · shared scale ownership · budgets · freeze + multi-country + bounded-runtime regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
