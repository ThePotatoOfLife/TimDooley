#!/usr/bin/env python3
"""Validate World Map information-plane integration."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SURFACES=ROOT/"data/world-map-layer-surfaces.json"
EVIDENCE=ROOT/"data/world-map-evidence-layers.json"
SPATIAL=ROOT/"data/world-map-spatial-overlays.json"
BELOW=ROOT/"data/world-map-spatial/below-us-cases.geojson"
EVIDENCE_JS=ROOT/"world-map/3d-evidence-layers.js"
ADL_JS=ROOT/"world-map/3d-adl-heat.js"
SUBDIV=ROOT/"world-map/3d-subdivisions.js"
RENDER=ROOT/"world-map/3d-render-stack.js"
MAP_STATE=ROOT/"world-map/3d-map-state.js"
CONTEXT=ROOT/"world-map/3d-context-visibility.js"
PANEL=ROOT/"world-map/3d-panel-lifecycle.js"
WORLD_BAR=ROOT/"world-map/3d-world-bar.js"
SPATIAL_UI=ROOT/"world-map/3d-spatial-overlay-ui.js"

def load(path,errors):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}

def require(path,tokens,errors):
    if not path.is_file():
        errors.append(f"missing {path.relative_to(ROOT)}")
        return ""
    text=path.read_text(encoding="utf-8",errors="replace")
    for token in tokens:
        if token not in text: errors.append(f"{path.relative_to(ROOT)} missing {token}")
    return text

def node_check(path,errors):
    node=shutil.which("node")
    if not node: return
    result=subprocess.run([node,"--check",str(path)],cwd=ROOT,capture_output=True,text=True)
    if result.returncode:
        errors.append(f"{path.relative_to(ROOT)} syntax failed: {(result.stderr or result.stdout).strip()}")

def main():
    errors=[]
    for p in (SURFACES,EVIDENCE,SPATIAL,BELOW,EVIDENCE_JS,ADL_JS,SUBDIV,RENDER,MAP_STATE,CONTEXT,PANEL,WORLD_BAR,SPATIAL_UI):
        if not p.exists(): errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        for e in errors: print("ERROR:",e)
        return 1

    surfaces=load(SURFACES,errors)
    evidence=load(EVIDENCE,errors)
    spatial=load(SPATIAL,errors)
    below=load(BELOW,errors)

    plane_ids=[row.get("id") for row in surfaces.get("persistent_planes",[])]
    expected=["analytical-country","physical-world","geography-overlays","evidence"]
    if plane_ids != expected:
        errors.append(f"persistent map planes must be {expected}, got {plane_ids}")
    dim_ids={row.get("id") for row in surfaces.get("dimensions",[])}
    if dim_ids != {"time","scale","projection"}:
        errors.append("Time, scale and projection must remain dimensions rather than paint layers")
    render_order=surfaces.get("render_order") or []
    for token in ("subnational evidence fill","country/subdivision outlines","context-network points"):
        if token not in render_order: errors.append(f"layer-surface render order missing {token}")

    rows={row.get("id"):row for row in evidence.get("entries",[])}
    adl=rows.get("adl-heat") or {}
    fbi=rows.get("fbi-hate-crime") or {}
    if adl.get("availability")!="current" or adl.get("module")!="./3d-adl-heat.js":
        errors.append("ADL must be a current specialist Evidence adapter")
    if fbi.get("availability")!="planned":
        errors.append("FBI comparison must remain planned/separate until sourced")
    if adl.get("source_owner") != "Anti-Defamation League (ADL), Center on Extremism":
        errors.append("ADL source ownership must remain explicit")

    spatial_rows={row.get("id"):row for row in spatial.get("entries",[])}
    mud=spatial_rows.get("project.below.us-cases") or {}
    if mud.get("family")!="project.below" or mud.get("epistemic_type")!="project_interpretive":
        errors.append("Below U.S. cases must remain project_interpretive spatial overlays")
    if mud.get("geometry_owner")!="data/world-map-spatial/below-us-cases.geojson":
        errors.append("Below U.S. cases must use the canonical spatial owner")
    if mud.get("availability")!="current":
        errors.append("Below U.S. cases should be current once geometry exists")

    if below.get("type")!="FeatureCollection" or len(below.get("features") or [])<2:
        errors.append("Below U.S. case geometry must retain at least two broad context anchors")
    if (below.get("metadata") or {}).get("coordinate_policy")!="state-centroid-only":
        errors.append("Below U.S. case geometry must remain state-centroid-only")
    for feature in below.get("features") or []:
        props=feature.get("properties") or {}
        if props.get("epistemic_type")!="project_interpretive":
            errors.append(f"{feature.get('id') or props.get('feature_id')} lost project attribution")
        note=str(props.get("status_note","")).lower()
        if "current location" not in note and "current-location" not in note:
            errors.append(f"{props.get('feature_id')} must explicitly reject precise/current-location interpretation")

    evidence_js=require(EVIDENCE_JS,(
        "world-map-evidence-layers.json","atlasEvidenceMenu","__potatoAtlasEvidenceLayers",
        "potato-atlas-evidence-layer-change","evidenceLayer","Evidence datasets",
        "__potatoAtlasLoadModule","setEnabled","reset",
    ),errors)
    adl_js=require(ADL_JS,(
        "incidentTypeTokens","flatMap","retainPartition('USA')","releasePartition?.('USA')",
        "slot:'subnational-fill'","slot:'context-network'","State shading = filtered record count",
        "not a general hate score or crime score",
    ),errors)
    subdiv=require(SUBDIV,("forcedPartitions","retainPartition","releasePartition","reconcileActive"),errors)
    render=require(RENDER,("'subnational-fill'","atlas-subdivision-line","subnational scalar/evidence fills"),errors)
    require(MAP_STATE,("__potatoAtlasEvidenceLayers","evidenceLayer","adlYear","adlType"),errors)
    require(CONTEXT,("__potatoAtlasEvidenceLayers","potato-atlas-evidence-layer-change"),errors)
    require(PANEL,("Evidence Layers","./3d-evidence-layers.js"),errors)
    require(WORLD_BAR,("project.below.us-cases","Below · U.S. cases"),errors)
    require(SPATIAL_UI,("project.below","Below / Farm project cases","project.below.us-cases"),errors)

    for path in (EVIDENCE_JS,ADL_JS,SUBDIV,RENDER,MAP_STATE,CONTEXT,WORLD_BAR,SPATIAL_UI):
        node_check(path,errors)

    if "3d-mud-below-us.js" in "\n".join([evidence_js,adl_js,subdiv,render]):
        errors.append("Below U.S. cases must use the canonical spatial-overlay runtime, not a bespoke renderer")

    if errors:
        print("WORLD MAP LAYER INTEGRATION VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print("WORLD MAP LAYER INTEGRATION VALIDATION PASSED")
    print("Persistent planes: Analytical · Physical · Geography · Evidence")
    print("Dimensions: Time · Scale · Projection")
    print("Contextual systems: base geography · relations · infrastructure · Axis · investigation")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
