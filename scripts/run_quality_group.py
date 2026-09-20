#!/usr/bin/env python3
"""Run bounded quality groups with compact output and complete failure collection.

Usage:
  python scripts/run_quality_group.py core
  python scripts/run_quality_group.py world_map
  python scripts/run_quality_group.py content

Each check writes its full output under .quality-logs/<group>/ and the console
only receives PASS/FAIL plus a bounded failure tail. The runner continues after
independent failures so one run exposes the whole problem set for that group.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_ROOT = ROOT / ".quality-logs"
TAIL_LINES = 45

GROUPS: dict[str, list[tuple[str, list[str]]]] = {
    "core": [
        ("Repository hygiene", ["python scripts/validate_repo_hygiene.py"]),
        ("Bidirectional spiral", ["python scripts/test_bidirectional_spiral_field.py"]),
        ("Archive runtime", ["python scripts/validate_archive_runtime_hardening.py"]),
        ("Country refresh reliability", ["python scripts/validate_country_refresh_reliability.py"]),
        ("SEO pipeline contract", ["python scripts/validate_seo_pipeline.py"]),
        ("House governance", [
            "python scripts/validate_house_governance.py",
            "python scripts/validate_house_topology.py",
            "python scripts/validate_house_subrooms.py",
            "python scripts/validate_house_compatibility.py",
            "python scripts/validate_house_world_routing.py",
            "python scripts/test_coordination_convergence.py",
        ]),
        ("Formal grammar and Rooms", [
            "python scripts/validate_project_formal_grammar.py",
            "python scripts/validate_public_rooms.py",
        ]),
        ("Foundation layer", [
            "python scripts/validate_foundation_layer.py",
            "python scripts/validate_foundation_seed_genealogy.py",
            "python scripts/validate_foundation_axis_placement.py",
            "python scripts/validate_foundation_rooms.py",
        ]),
        ("Instrumentation", [
            "python scripts/validate_commit_crystallization.py",
            "python scripts/validate_entity_dossier_instrumentation.py",
            "python scripts/validate_route_case_instrumentation.py",
            "python scripts/validate_works_fruit_instrumentation.py",
        ]),
        ("Timeline and story", [
            "python scripts/validate_timeline_naming.py",
            "python scripts/validate_prediction_under_mined_domains.py",
            "python scripts/validate_100000_hour_page.py",
            "python scripts/validate_story_archive.py",
            "python scripts/audit_story_source_closeness.py",
        ]),
        ("Atlas and architecture", [
            "python scripts/validate_blueprints.py",
            "python scripts/stability_audit.py",
            "python scripts/validate_atlas.py",
            "python scripts/validate_atlas_view_contracts.py",
            "python scripts/validate_atlas_math_calibration.py",
            "python scripts/validate_repository_spine.py",
            "python scripts/validate_architecture_layers.py",
            "python scripts/validate_content_integrity.py",
            "python scripts/check_css_namespace_collisions.py",
        ]),
    ],
    "world_map": [
        ("Ownership and evidence", [
            "python scripts/validate_world_map_ownership.py",
            "python scripts/validate_world_map_adl_heat.py",
            "python scripts/validate_world_map_layer_integration.py",
            "python scripts/validate_world_map_data_runtime.py",
            "python scripts/validate_world_axis_systems.py",
            "python scripts/validate_world_map_system_intelligence.py",
        ]),
        ("Chains, entities and coverage", [
            "python scripts/validate_world_map_chain_explorer.py",
            "python scripts/validate_world_map_entity_africa_repair.py",
            "python scripts/validate_world_map_impact_trace.py",
            "python scripts/build_world_map_coverage.py",
            "python scripts/validate_world_map_coverage.py",
            "python scripts/validate_world_map_infrastructure.py",
            "python scripts/validate_world_map_infrastructure_integration.py",
        ]),
        ("Canonical runtime", [
            "python scripts/validate_world_map_source.py",
            "python scripts/test_world_map_auditor.py",
        ]),
        ("Runtime architecture audit", ["python scripts/audit_world_map.py"]),
        ("UI geometry and investigation", [
            "python scripts/validate_world_map_ui_layout.py",
            "python scripts/validate_world_map_spatial_overlays.py",
            "python scripts/validate_world_map_palestine.py",
            "python scripts/validate_world_map_pathfinder_source.py",
            "python scripts/validate_world_map_investigation_utility.py",
            "python scripts/validate_world_map_entity_trace.py",
        ]),
        ("Context control plane", [
            "python scripts/validate_world_map_context_visibility.py",
            "node scripts/test_world_map_context_policy.mjs",
            "node scripts/test_world_map_ui_surface_budget.mjs",
            "node scripts/test_world_map_time_policy.mjs",
            "node scripts/test_world_map_investigation_contract.mjs",
            "node scripts/test_world_map_investigation_surface_ownership.mjs",
            "node scripts/test_world_map_pinned_context_contract.mjs",
            "node scripts/test_world_map_context_status.mjs",
            "node scripts/test_world_map_display_system_contract.mjs",
            "node scripts/test_world_map_inspection_bootstrap_staging.mjs",
            "node scripts/test_world_map_inspector_visibility.mjs",
            "node scripts/test_world_map_motion_compositor.mjs",
            "node scripts/test_world_map_route_geometry_semantics.mjs",
            "python scripts/validate_world_map_visual_channels.py",
            "node scripts/test_world_map_visual_channels.mjs",
            "python scripts/validate_world_places_fixture_pipeline.py",
            "node scripts/test_world_map_reset_context_contract.mjs",
            "node scripts/test_world_map_search_selection_contract.mjs",
            "node scripts/test_world_map_relation_budget_contract.mjs",
            "python scripts/validate_world_map_runtime_telemetry.py",
            "node scripts/test_world_map_context_ci_contract.mjs",
        ]),
    ],
    "content": [
        ("Reader and projection contracts", [
            "python scripts/validate_reader_surfaces.py",
            "python scripts/validate_body_discovery.py",
            "python scripts/validate_potatoism_philosophy_projection.py",
            "python scripts/validate_public_projection.py",
            "python scripts/validate_discovery_projection.py",
            "python scripts/validate_generated_navigation.py",
            "python scripts/validate_explore_projection.py",
        ]),
        ("Religion Potatoism and expansions", [
            "python scripts/validate_religious_adjacent.py",
            "python scripts/validate_religious_layer_map.py",
            "python scripts/validate_potatoism.py",
            "python scripts/validate_expansion_layers.py",
            "python scripts/check_faq_backend.py",
            "python scripts/check_biblical_syncretism_field.py",
        ]),
        ("Bible corpus and reader", [
            "python scripts/validate_bible_layer_manifest.py",
            "python scripts/test_bible_corpus.py",
            "python scripts/test_bible_comparator_coverage.py",
            "python scripts/check_biblical_scenes.py",
            "python scripts/build_bible_comparator_quality.py",
            "python scripts/validate_bible_reader.py",
        ]),
        ("Ownership and coverage audits", [
            "python scripts/audit_backend_coverage.py",
            "python scripts/audit_atlas_links.py",
            "python scripts/audit_web.py",
        ]),
    ],
}

def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return value or "check"

def run_command(command: str, log_handle) -> int:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        executable="/bin/bash" if os.name != "nt" else None,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc.returncode

def tail(path: Path, count: int = TAIL_LINES) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "(log unavailable)"
    return "\n".join(lines[-count:])

def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in GROUPS:
        print("Usage: python scripts/run_quality_group.py <core|world_map|content>")
        return 2

    group = sys.argv[1]
    group_dir = LOG_ROOT / group
    group_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    started = time.time()

    print(f"QUALITY GROUP {group}: {len(GROUPS[group])} checks")
    for index, (name, commands) in enumerate(GROUPS[group], start=1):
        log_path = group_dir / f"{index:02d}-{slugify(name)}.log"
        check_started = time.time()
        return_code = 0
        with log_path.open("w", encoding="utf-8") as log_handle:
            for command in commands:
                log_handle.write(f"$ {command}\n")
                log_handle.flush()
                rc = run_command(command, log_handle)
                if rc != 0:
                    return_code = rc
                    break
        duration = round(time.time() - check_started, 2)
        status = "PASS" if return_code == 0 else "FAIL"
        results.append({
            "name": name,
            "status": status,
            "return_code": return_code,
            "seconds": duration,
            "log": log_path.relative_to(ROOT).as_posix(),
            "commands": commands,
        })
        print(f"[{status}] {name} ({duration:.2f}s)")
        if return_code:
            print(f"--- failure tail: {name} ---")
            print(tail(log_path))
            print("--- end failure tail ---")

    failures = [row for row in results if row["status"] == "FAIL"]
    report = {
        "group": group,
        "status": "FAIL" if failures else "PASS",
        "seconds": round(time.time() - started, 2),
        "checks": len(results),
        "failures": len(failures),
        "results": results,
    }
    report_path = ROOT / f"quality-report-{group}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as handle:
            handle.write(f"## Quality group: {group}\n\n")
            handle.write("| Check | Status | Seconds |\n|---|---:|---:|\n")
            for row in results:
                handle.write(f"| {row['name']} | {row['status']} | {row['seconds']:.2f} |\n")
            handle.write(f"\n**Failures:** {len(failures)} / {len(results)}\n")

    print(f"QUALITY GROUP {group}: {report['status']} · {len(failures)} failures · {report['seconds']:.2f}s")
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
