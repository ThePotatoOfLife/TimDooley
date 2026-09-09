#!/usr/bin/env python3
"""Validate synchronized internal architecture, entanglement, terrain and Hawkins layers.

Public navigation is owned by manifest.json. Internal architecture datasets remain
required when they carry substantive information, but retired standalone readers
such as hawkins.html are not part of the current contract.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ERRORS=[]; WARNINGS=[]

def load(rel):
    p=ROOT/rel
    if not p.exists():ERRORS.append(f"Missing required layer: {rel}");return {}
    try:return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:ERRORS.append(f"Invalid JSON: {rel} — {exc}");return {}

def require(v,label):
    if not v:ERRORS.append(f"Missing required field/content: {label}")

def main():
    backend=load("data/backend.json")
    atlas=load("data/atlas-manifest.json")
    public=load("manifest.json")
    workflow=load("data/project-workflow.json")
    tree=load("data/tree.json")
    ent=load("data/entanglement.json")
    terrain=load("data/axis-topology.json")
    hawkins=load("data/hawkins-scale.json")

    required_paths={
        "data/backend.json","data/atlas-manifest.json","manifest.json",
        "data/project-workflow.json","data/tree.json","data/entanglement.json",
        "data/axis-topology.json","data/hawkins-scale.json"
    }
    for rel in required_paths:
        if not(ROOT/rel).exists():ERRORS.append(f"Missing synchronized architecture path: {rel}")

    if public.get("root",{}).get("id")!="potato-of-life":ERRORS.append("Public manifest root must be potato-of-life")
    if atlas.get("public_manifest")!="manifest.json":ERRORS.append("Atlas manifest must delegate public navigation to manifest.json")
    retired=set(atlas.get("retired_public_contracts",[]))
    if not any("hawkins.html" in x for x in retired):WARNINGS.append("Atlas manifest does not document retired hawkins.html contract")

    endpoints=backend.get("endpoints",{})
    expected_endpoints={
        "entanglement":"data/entanglement.json",
        "axisTopology":"data/axis-topology.json",
        "hawkinsScale":"data/hawkins-scale.json",
        "tree":"data/tree.json",
        "projectWorkflow":"data/project-workflow.json",
        "atlasManifest":"data/atlas-manifest.json"
    }
    for key,rel in expected_endpoints.items():
        if endpoints.get(key)!=rel:ERRORS.append(f"Backend endpoint {key} is not synchronized: {endpoints.get(key)!r}")
    required_backend=set(backend.get("required",[]))
    for key in ("entanglement","axisTopology","hawkinsScale"):
        if key not in required_backend:ERRORS.append(f"Backend required list omits {key}")
    health=set(backend.get("healthChecks",[]))
    for key in ("entanglement","hawkins-schema","terrain-schema"):
        if key not in health:ERRORS.append(f"Backend healthChecks omits {key}")

    layer_files={x for layer in atlas.get("layers",{}).values() if isinstance(layer,dict) for x in layer.get("files",[])}
    for rel in ("data/entanglement.json","data/axis-topology.json","data/hawkins-scale.json","data/tree.json"):
        if rel not in layer_files:ERRORS.append(f"Atlas manifest does not register internal architecture dataset: {rel}")
    expected_dimensions={"strength","dependency","distance","feedback","topology","trajectory","phase"}
    if not expected_dimensions.issubset(set(atlas.get("record_model",{}).get("entanglement",[]))):ERRORS.append("Atlas record_model entanglement fields are incomplete")

    rel_ext=ent.get("relationship_record_extension",{})
    ent_required={"source","target","relationship","evidence","confidence","date","notes"}
    if not ent_required.issubset(set(rel_ext.get("required_fields",[]))):ERRORS.append("Entanglement relationship required_fields are incomplete")
    if not expected_dimensions.issubset(set(rel_ext.get("recommended_entanglement_fields",[]))):ERRORS.append("Entanglement recommended fields are incomplete")
    require(ent.get("material_layer",{}).get("quantum_entanglement"),"entanglement.material_layer.quantum_entanglement")
    require(ent.get("material_layer",{}).get("network_entanglement"),"entanglement.material_layer.network_entanglement")
    require(ent.get("topology_model",{}).get("concepts"),"entanglement.topology_model.concepts")
    require(ent.get("trajectory_model",{}).get("fields"),"entanglement.trajectory_model.fields")
    if "fate_and_destiny_layer" not in ent:ERRORS.append("Entanglement layer lacks fate_and_destiny_layer")

    expected_terrain={"axis","mountain","plane","mud","swamp","roots","drain","door"}
    tree_terrain={x.get("id") for x in tree.get("terrain",[]) if isinstance(x,dict)}
    if tree_terrain!=expected_terrain:ERRORS.append(f"Tree terrain mismatch: expected {sorted(expected_terrain)}, got {sorted(tree_terrain)}")
    terrain_schema=terrain.get("terrain",{})
    if isinstance(terrain_schema,dict):
        if set(terrain_schema)!=expected_terrain:ERRORS.append(f"Axis topology terrain mismatch: expected {sorted(expected_terrain)}, got {sorted(terrain_schema)}")
        for tid in expected_terrain:
            if not isinstance(terrain_schema.get(tid),dict):ERRORS.append(f"Axis topology terrain node is invalid: {tid}")
    else:ERRORS.append("Axis topology terrain container must be an object keyed by canonical terrain IDs")

    levels=hawkins.get("levels",hawkins.get("scale",[]))
    if not isinstance(levels,list) or len(levels)<17:ERRORS.append("Hawkins scale must contain at least the 17 canonical levels")
    else:
        vals=[]
        for level in levels:
            if not isinstance(level,dict):ERRORS.append("Hawkins scale contains a non-object level");continue
            if "level" not in level and "value" not in level:ERRORS.append("Hawkins level lacks numeric level/value")
            if "name" not in level:ERRORS.append("Hawkins level lacks name")
            vals.append(level.get("level",level.get("value")))
        numeric=[x for x in vals if isinstance(x,(int,float))]
        if numeric and numeric!=sorted(numeric):ERRORS.append("Hawkins levels are not ordered numerically")
    text=json.dumps(hawkins,ensure_ascii=False).lower()
    for guardrail in ("hertz","electromagnetic","symbolic colour"):
        if guardrail not in text:ERRORS.append(f"Hawkins schema lacks explicit guardrail/concept: {guardrail}")

    phase_fields={"initial_state","trigger","transition","phase","constraint","attractor","outcome","reversal_condition"}
    if not phase_fields.issubset(set(ent.get("trajectory_model",{}).get("fields",[]))):ERRORS.append("Trajectory model lacks required phase-transition fields")

    # Validate the current workflow contract rather than retired phase names.
    workflow_ids={p.get("id") for p in workflow.get("phases",[]) if isinstance(p,dict)}
    required_phases={"audit","prune","canonicalize","deepen","world","relationships","religion-texts","north-programme","potatoism-canon","spiritual-inquiry","systems","entanglement","comparative","evidence","website","release-audit"}
    missing=required_phases-workflow_ids
    if missing:ERRORS.append(f"Workflow omits current required phases: {sorted(missing)}")
    intro=workflow.get("project_introduction",{})
    for key in ("mission","information_goal","public_canon_rule","core_principle"):
        if not intro.get(key):ERRORS.append(f"Workflow project introduction lacks {key}")
    gates={g.get("id"):g for g in workflow.get("gates",[]) if isinstance(g,dict)}
    for gid in ("G1","G2","G5","G6","G7","G8"):
        if gid not in gates:ERRORS.append(f"Workflow lacks current integrity gate {gid}")
    website=next((p for p in workflow.get("phases",[]) if p.get("id")=="website"),{})
    website_text=json.dumps(website,ensure_ascii=False).casefold()
    if "axis and world only at top level" in website_text:
        WARNINGS.append("Workflow website phase still contains retired AXIS/WORLD presentation wording")

    print(f"Architecture layers checked: {len(required_paths)} required paths")
    print(f"Entanglement dimensions: {len(ent.get('relational_dimensions',[]))}")
    print(f"Terrain nodes: {len(tree_terrain)}")
    print(f"Hawkins levels: {len(levels) if isinstance(levels,list) else 0}")
    print(f"Workflow phases: {len(workflow.get('phases',[]))}")
    print(f"Errors: {len(ERRORS)} · Warnings: {len(WARNINGS)}")
    for item in ERRORS:print("ERROR:",item)
    for item in WARNINGS:print("WARNING:",item)
    return 1 if ERRORS else 0
if __name__=="__main__":raise SystemExit(main())
