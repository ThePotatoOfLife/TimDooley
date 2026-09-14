#!/usr/bin/env python3
"""Validate the generic, lazy subdivision integration surface."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_world_subdivisions.py"
POPULATION_ENRICHER = ROOT / "scripts" / "enrich_world_subdivision_population.py"
POPULATION_TEST = ROOT / "scripts" / "test_world_subdivision_population.py"
MODULE = ROOT / "world-map" / "3d-subdivisions.js"
SEARCH = ROOT / "world-map" / "3d-search.js"
SEARCH_CORE = ROOT / "world-map" / "3d-search-core.js"
SPATIAL_CORE = ROOT / "world-map" / "3d-spatial-core.js"
INFRASTRUCTURE = ROOT / "world-map" / "3d-infrastructure.js"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
INDEX = ROOT / "data" / "world-subdivisions" / "index.json"
USA = ROOT / "data" / "world-subdivisions" / "USA.geo.json"
DNK = ROOT / "data" / "world-subdivisions" / "DNK.geo.json"
INTERACTION_TEST = ROOT / "scripts" / "test_world_map_subdivision_interaction.mjs"
SEARCH_TEST = ROOT / "scripts" / "test_world_map_search.mjs"
SPATIAL_TEST = ROOT / "scripts" / "test_world_map_spatial_core.mjs"


def main() -> int:
    errors: list[str] = []
    required = (
        BUILDER, POPULATION_ENRICHER, POPULATION_TEST, MODULE, SEARCH, SEARCH_CORE,
        SPATIAL_CORE, INFRASTRUCTURE, LIFECYCLE, INDEX, USA, DNK,
        INTERACTION_TEST, SEARCH_TEST, SPATIAL_TEST,
    )
    for path in required:
        if not path.exists():
            errors.append(f"missing subdivision integration file: {path.relative_to(ROOT)}")
    if not errors:
        builder = BUILDER.read_text(encoding="utf-8")
        enricher = POPULATION_ENRICHER.read_text(encoding="utf-8")
        module = MODULE.read_text(encoding="utf-8")
        search = SEARCH.read_text(encoding="utf-8")
        search_core = SEARCH_CORE.read_text(encoding="utf-8")
        spatial_core = SPATIAL_CORE.read_text(encoding="utf-8")
        infrastructure = INFRASTRUCTURE.read_text(encoding="utf-8")
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        usa = json.loads(USA.read_text(encoding="utf-8"))
        dnk = json.loads(DNK.read_text(encoding="utf-8"))

        for token in (
            "GENZ2025", "cb_2025_us_state_20m.zip", "NST-EST2025-ALLDATA.csv",
            "EXPECTED_US_UNITS = 51", "parse_state_kml", "federal district",
            "DAWA_REGIONS_GEOJSON", "normalize_denmark_regions", "subdivision_search_records",
        ):
            if token not in builder:
                errors.append(f"subdivision builder missing marker: {token}")
        for token in (
            "BEFOLK3", "Statistics Denmark", "unknown-not-zero", "enrich_denmark_payload",
            "official-statistical-observation",
        ):
            if token not in enricher:
                errors.append(f"subdivision population enricher missing marker: {token}")

        for token in (
            "world-subdivisions/index.json", "atlas-subdivision", "subdivision=",
            "potato-atlas-subdivision-select", "potato-atlas-subdivision-clear",
            "__potatoAtlasOverlayHandled", "pendingDeepLinkId", "partitionForId",
            "viewport_bounds", "id_prefix", "handSubdivisionToInfrastructure",
        ):
            if token not in module:
                errors.append(f"subdivision module missing marker: {token}")

        for token in ("pointInGeometry", "assetsWithinGeometry", "Polygon", "MultiPolygon"):
            if token not in spatial_core:
                errors.append(f"spatial containment core missing marker: {token}")
        for token in (
            "showForSubdivision", "assetsWithinGeometry", "potato-atlas-subdivision-select",
            "potato-atlas-subdivision-clear", "contained-location-context",
            "spatial containment", "fallBackContext",
        ):
            if token not in infrastructure:
                errors.append(f"infrastructure subdivision context missing marker: {token}")

        if "startsWith('US-') ? 'USA'" in module or 'USA_BOUNDS' in module:
            errors.append("subdivision renderer regressed to hard-coded U.S.-only partition selection")
        if "subdivisionSearchRows" not in search or "subdivisionSearchRows" not in search_core:
            errors.append("search must read lightweight subdivision manifests from the partition index")
        if "world-subdivisions/${descriptor.path}" in search:
            errors.append("search must not download subdivision polygon files during startup")
        if "3d-subdivisions.js" not in lifecycle or "map.getZoom() < 3.4" not in lifecycle:
            errors.append("regional-scale lazy subdivision loading is not registered")

        usa_descriptor = index.get("partitions", {}).get("USA", {})
        if usa_descriptor.get("feature_count") != 51:
            errors.append("USA subdivision index must declare 51 first-wave features")
        if usa_descriptor.get("id_prefix") != "US-" or not usa_descriptor.get("viewport_bounds"):
            errors.append("USA partition must expose generic id_prefix and viewport_bounds metadata")
        search_records = usa_descriptor.get("search_records") or []
        if len(search_records) != 51:
            errors.append(f"USA subdivision search manifest must contain 51 records; found {len(search_records)}")
        if any("geometry" in row for row in search_records):
            errors.append("subdivision search manifest must remain geometry-free")

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

        dnk_descriptor = index.get("partitions", {}).get("DNK", {})
        dnk_features = dnk.get("features", []) if dnk.get("type") == "FeatureCollection" else []
        if len(dnk_features) != 5:
            errors.append(f"DNK subdivision snapshot must contain five current regions; found {len(dnk_features)}")
        if dnk_descriptor.get("id_prefix") != "DK-" or not dnk_descriptor.get("viewport_bounds"):
            errors.append("DNK partition must expose generic id_prefix and viewport_bounds metadata")
        if any("geometry" in row for row in (dnk_descriptor.get("search_records") or [])):
            errors.append("DNK subdivision search records must remain geometry-free")
        for feature in dnk_features:
            props = feature.get("properties") or {}
            population = props.get("population")
            if population is not None:
                if not isinstance(population.get("value"), (int, float)) or population.get("value", 0) <= 0:
                    errors.append(f"{props.get('id')}: Danish population must be positive when present")
                if population.get("unit") != "persons" or "Statistics Denmark" not in population.get("source", ""):
                    errors.append(f"{props.get('id')}: Danish population provenance is incomplete")

        population_test = subprocess.run(
            [sys.executable, "-m", "unittest", "scripts.test_world_subdivision_population", "-v"],
            cwd=ROOT, capture_output=True, text=True,
        )
        if population_test.returncode:
            errors.append("subdivision population regression failed: " + (population_test.stderr.strip() or population_test.stdout.strip()))

        node = shutil.which("node")
        if node:
            for js_path in (MODULE, SEARCH, SEARCH_CORE, SPATIAL_CORE, INFRASTRUCTURE):
                checked = subprocess.run([node, "--check", str(js_path)], capture_output=True, text=True)
                if checked.returncode:
                    errors.append(f"{js_path.name} syntax failed: " + (checked.stderr.strip() or checked.stdout.strip()))
            for label, test_path in (
                ("subdivision interaction", INTERACTION_TEST),
                ("subdivision search", SEARCH_TEST),
                ("subdivision spatial containment", SPATIAL_TEST),
            ):
                test = subprocess.run([node, str(test_path)], capture_output=True, text=True)
                if test.returncode:
                    errors.append(f"{label} regression failed: " + (test.stderr.strip() or test.stdout.strip()))
    if errors:
        print("WORLD MAP SUBDIVISION VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP SUBDIVISION VALIDATION PASSED · USA 51/51 · DNK 5/5 · sourced observations · generic partitions/search · spatial infrastructure context · state refit loop guarded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
