#!/usr/bin/env python3
"""Regression contract for project authority and CI convergence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    surfaces = load("data/house/public-surfaces.json")
    spine = load("data/repository-spine.json")
    atlas = load("data/atlas-manifest.json")
    consolidation = load("knowledge/indexes/project-consolidation-map.json")

    if surfaces.get("authority") != "public-route-identity":
        errors.append("public-surfaces.json must remain the public-route-identity authority")

    public = spine.get("public_navigation", {})
    if public.get("source") != "data/house/public-surfaces.json":
        errors.append("repository spine must delegate route identity to public-surfaces.json")
    if public.get("archive_source") != "manifest.json":
        errors.append("repository spine must delegate archive branch/pathway navigation to manifest.json")
    if public.get("projection") != "data/frontend-atlas-bridge.json":
        errors.append("repository spine must name frontend-atlas-bridge.json as the routing projection")

    if atlas.get("public_route_registry") != "data/house/public-surfaces.json":
        errors.append("atlas manifest must name public-surfaces.json as public route registry")
    if atlas.get("public_manifest") != "manifest.json":
        errors.append("atlas manifest must retain manifest.json as archive branch/pathway manifest")
    if atlas.get("frontend_projection") != "data/frontend-atlas-bridge.json":
        errors.append("atlas manifest must retain frontend-atlas-bridge.json as projection contract")

    owners = consolidation.get("top_level_owners", {})
    if owners.get("public_navigation") != "data/house/public-surfaces.json":
        errors.append("project consolidation map must route public navigation ownership to public-surfaces.json")
    if owners.get("archive_navigation") != "manifest.json":
        errors.append("project consolidation map must identify manifest.json as archive navigation owner")

    workflow = (ROOT / ".github/workflows/quality-checks.yml").read_text(encoding="utf-8")
    runner = (ROOT / "scripts/run_quality_group.py").read_text(encoding="utf-8")
    if "Validate JavaScript syntax" in workflow:
        errors.append("quality workflow must not maintain a partial manual JavaScript syntax list")
    if "node --check app/bible-study.js" in workflow:
        errors.append("manual JavaScript syntax checks remain in quality workflow")
    if "- name: Validate World Map UI shell" in workflow:
        errors.append("quality workflow must not rerun UI-shell validation already owned by validate_world_map_source.py")
    for group in ("core", "world_map", "content"):
        if f"python scripts/run_quality_group.py {group}" not in workflow:
            errors.append(f"quality workflow must invoke grouped quality runner for {group}")
    if "python scripts/stability_audit.py" not in runner:
        errors.append("core quality runner must retain the all-JavaScript stability audit")
    if "python scripts/validate_world_map_source.py" not in runner:
        errors.append("world-map quality runner must retain canonical World Map source validation")

    if errors:
        print("COORDINATION CONVERGENCE TEST FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("Coordination convergence: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
