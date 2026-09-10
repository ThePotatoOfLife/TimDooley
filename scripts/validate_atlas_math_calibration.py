#!/usr/bin/env python3
"""Validate the Atlas mathematical calibration contract and its implemented hooks."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "data" / "atlas-mathematical-calibration.json"
RUNTIME = ROOT / "data" / "world-map-3d-runtime.json"
APP = ROOT / "world-map" / "3d-app.js"


def load(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}


def main() -> int:
    errors: list[str] = []
    data = load(CAL, errors)
    runtime = load(RUNTIME, errors)
    app = APP.read_text(encoding="utf-8", errors="replace") if APP.exists() else ""

    if data.get("status") != "active design/calibration contract":
        errors.append("calibration contract must be active")
    if runtime.get("mathematical_calibration_contract") != "data/atlas-mathematical-calibration.json":
        errors.append("renderer runtime must point to the canonical mathematical calibration contract")

    adopted = data.get("adopted_now", {})
    for key in ("trace_levels", "semantic_hub_phyllotaxis", "axis_structural_flow", "project_logarithmic_spiral"):
        if key not in adopted:
            errors.append(f"missing adopted formalism: {key}")

    future = data.get("next_formalisms", {})
    for key in ("spectral_graph_layout", "hyperbolic_hierarchy", "hodge_edge_flow", "physical_vortex"):
        if key not in future:
            errors.append(f"missing future calibration lens: {key}")

    for token in ("const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5))", "const a=i*GOLDEN_ANGLE", "Math.sqrt(i+1)"):
        if token not in app:
            errors.append(f"semantic-hub phyllotaxis implementation missing: {token}")

    leave_start = app.find("window.leaveCompare=")
    if leave_start < 0:
        errors.append("leaveCompare handler missing")
    else:
        leave = app[leave_start:leave_start + 500]
        for token in ("clearCompareStates()", "compareCodes=[]", "compareMode=false", "updateUrl()"):
            if token not in leave:
                errors.append(f"leaveCompare does not fully clear comparison state: {token}")

    for token in ("window.removeComparedCountry", "window.inspectComparedCountry", "if (!compareMode) return emptyFC()"):
        if token not in app:
            errors.append(f"compare lifecycle hardening missing: {token}")

    invariants = data.get("invariants", {})
    expected_invariants = {
        "north_gate_arc_degrees": 42,
        "north_gate_arc_is_level_count": False,
        "north_gate_arc_is_fibonacci_derived": False,
        "north_gate_arc_is_golden_ratio_derived": False,
        "north_gate_arc_is_physical_law": False,
        "geography_uses_real_coordinates": True,
        "abstract_nodes_may_receive_fake_geographic_coordinates": False,
        "time_is_orthogonal_to_spatial_and_graph_depth": True,
        "map_height_may_encode_spiritual_rank_or_truth": False,
    }
    for key, expected in expected_invariants.items():
        if invariants.get(key) != expected:
            errors.append(f"calibration invariant {key} must be {expected!r}")

    planes = runtime.get("mathematical_planes", {})
    for plane in ("geography", "topology", "hierarchy", "time", "flow"):
        if not planes.get(plane):
            errors.append(f"renderer runtime does not document mathematical plane: {plane}")
    if runtime.get("axis_mode", {}).get("north_gate_arc_degrees") != 42:
        errors.append("renderer runtime and mathematical contract disagree on North-gate angle")

    hodge = future.get("hodge_edge_flow", {})
    gate = set(hodge.get("promotion_gate", []))
    for required in ("directed edges", "common quantity", "compatible unit", "reference period"):
        if required not in gate:
            errors.append(f"Hodge/vortex promotion gate missing: {required}")

    rejected = " ".join(data.get("rejected_shortcuts", [])).lower()
    for phrase in ("42 levels", "every spiral", "undirected relationship cycles", "fake latitude/longitude"):
        if phrase not in rejected:
            errors.append(f"missing anti-numerology/spatial guardrail: {phrase}")

    sources = data.get("sources", [])
    if len(sources) < 6 or not all(item.get("url") for item in sources):
        errors.append("mathematical calibration must retain external source provenance")

    print("Atlas math calibration:")
    print("- Trace levels: graph geodesic / BFS")
    print("- Semantic hubs: golden-angle phyllotaxis")
    print("- North gate: 42° visual geometry only")
    print("- Renderer planes: geography / topology / hierarchy / time / gated flow")
    print("- Future dense graph: spectral/hyperbolic candidates")
    print("- Future quantitative circulation: Hodge decomposition only after directed-flow gates")
    print(f"Errors: {len(errors)}")
    if errors:
        print("ATLAS MATH CALIBRATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("ATLAS MATH CALIBRATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
