#!/usr/bin/env python3
"""Validate the synchronized architecture, entanglement, terrain and Hawkins layers."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []

def load(rel: str):
    p = ROOT / rel
    if not p.exists():
        ERRORS.append(f"Missing required layer: {rel}")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        ERRORS.append(f"Invalid JSON: {rel} — {exc}")
        return {}

def require(value, label: str):
    if not value:
        ERRORS.append(f"Missing required field/content: {label}")

def main() -> int:
    backend = load("data/backend.json")
    manifest = load("data/atlas-manifest.json")
    workflow = load("data/project-workflow.json")
    tree = load("data/tree.json")
    ent = load("data/entanglement.json")
    terrain = load("data/axis-topology.json")
    hawkins = load("data/hawkins-scale.json")

    required_paths = {
        "data/backend.json", "data/atlas-manifest.json", "data/project-workflow.json",
        "data/tree.json", "data/entanglement.json", "data/axis-topology.json",
        "data/hawkins-scale.json", "hawkins.html"
    }
    for rel in required_paths:
        if not (ROOT / rel).exists():
            ERRORS.append(f"Missing synchronized architecture path: {rel}")

    endpoints = backend.get("endpoints", {})
    for key, rel in {
        "entanglement": "data/entanglement.json",
        "axisTopology": "data/axis-topology.json",
        "hawkinsScale": "data/hawkins-scale.json",
        "tree": "data/tree.json",
        "projectWorkflow": "data/project-workflow.json",
        "atlasManifest": "data/atlas-manifest.json",
    }.items():
        if endpoints.get(key) != rel:
            ERRORS.append(f"Backend endpoint {key} is not synchronized: {endpoints.get(key)!r}")

    required_backend = set(backend.get("required", []))
    for key in ("entanglement", "axisTopology", "hawkinsScale"):
        if key not in required_backend:
            ERRORS.append(f"Backend required list omits {key}")

    health = set(backend.get("healthChecks", []))
    for key in ("entanglement", "hawkins-schema", "terrain-schema"):
        if key not in health:
            ERRORS.append(f"Backend healthChecks omits {key}")

    manifest_files = set()
    for layer in manifest.get("layers", {}).values():
        manifest_files.update(layer.get("files", []))
    for rel in ("data/entanglement.json", "data/axis-topology.json", "data/hawkins-scale.json", "hawkins.html"):
        if rel not in manifest_files:
            ERRORS.append(f"Atlas manifest does not register {rel}")

    record_model = manifest.get("record_model", {}).get("entanglement", [])
    expected_dimensions = {"strength", "dependency", "distance", "feedback", "topology", "trajectory", "phase"}
    if not expected_dimensions.issubset(record_model):
        ERRORS.append("Atlas record_model entanglement fields are incomplete")

    ent_required = {"source", "target", "relationship", "evidence", "confidence", "date", "notes"}
    rel_ext = ent.get("relationship_record_extension", {})
    if not ent_required.issubset(set(rel_ext.get("required_fields", []))):
        ERRORS.append("Entanglement relationship required_fields are incomplete")
    if not {"strength", "distance", "dependency", "feedback", "topology", "trajectory", "phase"}.issubset(set(rel_ext.get("recommended_entanglement_fields", []))):
        ERRORS.append("Entanglement recommended fields are incomplete")

    require(ent.get("material_layer", {}).get("quantum_entanglement"), "entanglement.material_layer.quantum_entanglement")
    require(ent.get("material_layer", {}).get("network_entanglement"), "entanglement.material_layer.network_entanglement")
    require(ent.get("topology_model", {}).get("concepts"), "entanglement.topology_model.concepts")
    require(ent.get("trajectory_model", {}).get("fields"), "entanglement.trajectory_model.fields")
    if "fate_and_destiny_layer" not in ent:
        ERRORS.append("Entanglement layer lacks fate_and_destiny_layer")

    terrain_names = {x.get("id") for x in tree.get("terrain", []) if isinstance(x, dict)}
    expected_terrain = {"axis", "mountain", "plane", "mud", "swamp", "roots", "drain", "door"}
    if terrain_names != expected_terrain:
        ERRORS.append(f"Tree terrain mismatch: expected {sorted(expected_terrain)}, got {sorted(terrain_names)}")

    terrain_schema = terrain.get("terrain", terrain.get("entries", []))
    if isinstance(terrain_schema, list):
        terrain_ids = {x.get("id") for x in terrain_schema if isinstance(x, dict)}
        if terrain_ids and not expected_terrain.issubset(terrain_ids):
            ERRORS.append("Axis topology terrain schema does not cover the complete canonical terrain")
    else:
        WARNINGS.append("Axis topology file uses an unexpected terrain container shape; inspect manually")

    levels = hawkins.get("levels", hawkins.get("scale", []))
    if not isinstance(levels, list) or len(levels) < 17:
        ERRORS.append("Hawkins scale must contain at least the 17 canonical levels")
    else:
        values = []
        for level in levels:
            if not isinstance(level, dict):
                ERRORS.append("Hawkins scale contains a non-object level")
                continue
            if "level" not in level and "value" not in level:
                ERRORS.append("Hawkins level lacks numeric level/value")
            if "name" not in level:
                ERRORS.append("Hawkins level lacks name")
            values.append(level.get("level", level.get("value")))
        numeric = [x for x in values if isinstance(x, (int, float))]
        if numeric and numeric != sorted(numeric):
            ERRORS.append("Hawkins levels are not ordered numerically")

    text = json.dumps(hawkins, ensure_ascii=False).lower()
    for guardrail in ("hertz", "electromagnetic", "symbolic colour"):
        if guardrail not in text:
            ERRORS.append(f"Hawkins schema lacks explicit guardrail/concept: {guardrail}")

    phase_fields = {"initial_state", "trigger", "transition", "phase", "constraint", "attractor", "outcome", "reversal_condition"}
    if not phase_fields.issubset(set(ent.get("trajectory_model", {}).get("fields", []))):
        ERRORS.append("Trajectory model lacks required phase-transition fields")

    workflow_ids = {p.get("id") for p in workflow.get("phases", []) if isinstance(p, dict)}
    for phase in ("emotion-state", "comparative", "calculations", "website", "release-audit"):
        if phase not in workflow_ids:
            ERRORS.append(f"Workflow omits required phase: {phase}")
    if "entanglement_principle" not in workflow.get("project_introduction", {}):
        ERRORS.append("Workflow mission lacks entanglement_principle")
    if "G9" not in {g.get("id") for g in workflow.get("gates", []) if isinstance(g, dict)}:
        ERRORS.append("Workflow lacks the entanglement evidence gate G9")

    for level in levels if isinstance(levels, list) else []:
        if isinstance(level, dict) and level.get("hertz") not in (None, "not_measured", "not_applicable"):
            WARNINGS.append("Hawkins data contains a Hertz value; verify that it is explicitly sourced and not inferred from the Hawkins number")
            break

    print(f"Architecture layers checked: {len(required_paths)} required paths")
    print(f"Entanglement dimensions: {len(ent.get('relational_dimensions', []))}")
    print(f"Terrain nodes: {len(terrain_names)}")
    print(f"Hawkins levels: {len(levels) if isinstance(levels, list) else 0}")
    print(f"Workflow phases: {len(workflow.get('phases', []))}")
    print(f"Errors: {len(ERRORS)} · Warnings: {len(WARNINGS)}")
    for item in ERRORS:
        print("ERROR:", item)
    for item in WARNINGS:
        print("WARNING:", item)
    return 1 if ERRORS else 0

if __name__ == "__main__":
    raise SystemExit(main())
