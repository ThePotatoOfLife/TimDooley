#!/usr/bin/env python3
"""Validate the 3D World Relational Atlas renderer and its runtime/data contracts."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "world-map" / "3d.html"
RUNTIME = ROOT / "data" / "world-map-3d-runtime.json"
WORLD = ROOT / "data" / "world-relational-map.json"
COUNTRIES = ROOT / "data" / "countries" / "index.json"


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON: {path.relative_to(ROOT)} — {exc}")
        return {}


def fail_if_missing(text: str, tokens: tuple[str, ...], label: str, errors: list[str]) -> None:
    for token in tokens:
        if token not in text:
            errors.append(f"{label} missing required feature marker: {token}")


def check_inline_module_syntax(text: str, warnings: list[str], errors: list[str]) -> None:
    """Use Node when available to syntax-check the inline module after removing remote imports."""
    node = shutil.which("node")
    if not node:
        warnings.append("node not available; skipped JavaScript syntax check")
        return
    scripts = re.findall(r'<script\s+type=["\']module["\'][^>]*>(.*?)</script>', text, flags=re.S | re.I)
    if not scripts:
        errors.append("3d.html contains no inline module script")
        return
    js = "\n".join(scripts)
    # Node --check does not need the imported library to exist, but remote URL imports are
    # not valid in all Node parsing modes. Replace import statements with inert declarations.
    js = re.sub(r"^import\s+\*\s+as\s+maplibregl\s+from\s+['\"][^'\"]+['\"];?", "const maplibregl = {};", js, flags=re.M)
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
        handle.write(js)
        temp = Path(handle.name)
    try:
        result = subprocess.run([node, "--check", str(temp)], capture_output=True, text=True)
        if result.returncode:
            errors.append("3d.html JavaScript syntax check failed: " + (result.stderr.strip() or result.stdout.strip()))
    finally:
        temp.unlink(missing_ok=True)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for path in (HTML, RUNTIME, WORLD, COUNTRIES):
        if not path.exists():
            errors.append(f"missing required atlas file: {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1

    text = HTML.read_text(encoding="utf-8", errors="replace")
    runtime = load_json(RUNTIME, errors)
    world = load_json(WORLD, errors)
    countries = load_json(COUNTRIES, errors)

    fail_if_missing(
        text,
        (
            'id="map"', 'id="panel"', 'id="search"', 'id="country-list"',
            'id="height"', 'id="compare"', 'id="interior"', 'id="relations"',
            'id="relationType"', 'id="fit"', 'id="tilt"', 'id="globe"', 'id="world"',
            "function relationEdgesFor", "function relationData", "function compareData",
            "function updateSpatial", "function fitFeatureSet", "function setCompareMode",
            "function selectFeature", "window.openModule", "window.traceTo",
            "searchParams.set('country'", "searchParams.set('compare'", "searchParams.set('relation'",
            "semantic-hubs", "semantic-links", "compare-hubs", "relations",
            "MapLibre", "OpenStreetMap contributors",
        ),
        "world-map/3d.html",
        errors,
    )

    # Ethical/spatialization boundaries are functional requirements, not optional prose.
    for required in (
        "navigation handles, not fake geographic locations",
        "Project-canon material is separate from empirical country data",
        "documented physical/public finance",
        "A relation line describes a typed connection",
    ):
        if required not in text:
            errors.append(f"3d.html missing epistemic/spatial boundary: {required}")

    check_inline_module_syntax(text, warnings, errors)

    if runtime.get("status") != "active experimental renderer contract":
        errors.append("world-map-3d-runtime status changed or missing")
    implemented = set(runtime.get("implemented_2026_09_10", []))
    for fragment in ("Compare", "relation", "polygon", "URL"):
        if not any(fragment.lower() in str(item).lower() for item in implemented):
            errors.append(f"runtime implemented list does not document {fragment} functionality")
    if runtime.get("compare_mode", {}).get("status") not in {"implemented", "implemented-basic"}:
        errors.append("runtime compare_mode is not marked implemented")
    if runtime.get("trace_mode", {}).get("status") not in {"implemented", "implemented-one-hop", "implemented-basic"}:
        errors.append("runtime trace_mode status does not match an implemented state")

    country_rows = countries.get("countries", [])
    canonical_codes = {row.get("iso3") for row in country_rows if row.get("iso3")}
    if len(canonical_codes) != 195:
        errors.append(f"expected 195 canonical country ISO3 codes; found {len(canonical_codes)}")

    # Territory/non-state codes are permitted in the world layer, but must be explicit rather than typos.
    permitted_noncanonical = {"GRL", "FRO"}
    referenced: set[str] = set()
    for edge in world.get("curated_edges", []):
        a, b = edge.get("a"), edge.get("b")
        if not a or not b:
            errors.append(f"curated edge missing endpoint: {edge}")
            continue
        if a == b:
            errors.append(f"curated edge self-loop is probably accidental: {a}")
        referenced.update((a, b))
        if not edge.get("types"):
            errors.append(f"curated edge {a}-{b} has no relationship types")
        if not edge.get("layer"):
            errors.append(f"curated edge {a}-{b} has no layer/epistemic classification")

    for section in ("north", "west", "east"):
        for value in world.get("project_axis", {}).get(section, {}).values():
            if isinstance(value, list):
                referenced.update(code for code in value if isinstance(code, str) and len(code) == 3)

    unknown = sorted(referenced - canonical_codes - permitted_noncanonical)
    if unknown:
        errors.append(f"world-map references unknown/unapproved ISO3-like codes: {unknown}")

    relation_types = sorted({t for edge in world.get("curated_edges", []) for t in edge.get("types", [])})
    if not relation_types:
        errors.append("world relational map exposes no typed curated relationships")
    if "All relation types" not in text:
        errors.append("3d map does not expose the all-types relation filter option")

    # Prevent accidental silent regression back to centroid-only focus.
    if "fitBounds" not in text or "geometryBounds" not in text:
        errors.append("3d map no longer appears to fit actual polygon geometry")

    # Compare must be bounded so selecting the world cannot create an unmanageable client state.
    if "slice(-4)" not in text and "length>=4" not in text and "length >= 4" not in text:
        warnings.append("could not confirm a four-country Compare cap from static inspection")

    print(f"Canonical countries: {len(canonical_codes)}")
    print(f"Curated relation types: {len(relation_types)}")
    print(f"Referenced country/territory codes: {len(referenced)}")
    print(f"Errors: {len(errors)} · Warnings: {len(warnings)}")
    for warning in warnings:
        print("WARNING:", warning)
    if errors:
        print("WORLD MAP 3D VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP 3D VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
