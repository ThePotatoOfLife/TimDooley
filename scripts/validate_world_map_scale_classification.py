#!/usr/bin/env python3
"""Validate World Map scale ownership and zoom-threshold classification."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"data/world-map-scale-contract.json"
CLASSIFICATION=ROOT/"data/world-map-scale-classification.json"
SCALE=ROOT/"world-map/3d-scale.js"
APP=ROOT/"world-map/3d-app.js"
BEHAVIORAL=(
    ROOT/"world-map/3d-subdivisions.js",
    ROOT/"world-map/3d-places.js",
    ROOT/"world-map/3d-physical-water.js",
    ROOT/"world-map/3d-physical-hydrology.js",
    ROOT/"world-map/3d-adl-heat.js",
)
REQUIRED_CAPABILITIES={
    "subdivisions",
    "places-detail",
    "physical-water-detail",
    "physical-hydrology",
    "hydrology-rivers-medium",
    "hydrology-rivers-fine",
    "hydrology-rivers-detailed",
    "adl-heat-points",
}

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main()->int:
    errors=[]
    for path in (CONTRACT,CLASSIFICATION,SCALE,APP,*BEHAVIORAL):
        if not path.is_file(): errors.append(f"missing required scale file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP SCALE CLASSIFICATION FAILED")
        for e in errors: print("-",e)
        return 1

    contract=load(CONTRACT)
    classification=load(CLASSIFICATION)
    capabilities=set((contract.get("capabilities") or {}).keys())
    missing=sorted(REQUIRED_CAPABILITIES-capabilities)
    if missing: errors.append(f"scale contract missing capabilities: {missing}")

    scale=SCALE.read_text(encoding="utf-8",errors="replace")
    for token in ("function bandForZoom","function threshold(","function capabilityActive","window.__potatoAtlasScale"):
        if token not in scale: errors.append(f"Scale runtime missing {token!r}")

    app=APP.read_text(encoding="utf-8",errors="replace")
    if "scale.bandForZoom(map.getZoom())" not in app:
        errors.append("core HUD must derive its band from shared Scale runtime")
    if "return z < 3 ? 'world' : z < 5 ? 'regional' : z < 7 ? 'country'" in app:
        errors.append("legacy private 3/5/7 HUD band classifier returned")

    categories=(classification.get("categories") or {})
    expected={"capability","cartographic_interpolation","camera_intent","fixture"}
    if set(categories)!=expected:
        errors.append(f"scale classification categories drifted: {sorted(categories)}")
    if classification.get("authority")!="data/world-map-scale-contract.json":
        errors.append("classification must point to canonical scale contract")

    behavior_text={p.name:p.read_text(encoding="utf-8",errors="replace") for p in BEHAVIORAL}
    required_markers={
        "3d-subdivisions.js":["scale.threshold('subdivisions'","capabilityActive('subdivisions'"],
        "3d-places.js":["scale.threshold('places-detail'"],
        "3d-physical-water.js":["scale.threshold('physical-water-detail'"],
        "3d-physical-hydrology.js":["scale.threshold('physical-hydrology'","hydrology-rivers-medium","hydrology-rivers-fine","hydrology-rivers-detailed"],
        "3d-adl-heat.js":["scale.threshold('adl-heat-points'"],
    }
    for name,markers in required_markers.items():
        text=behavior_text.get(name,"")
        for marker in markers:
            if marker not in text: errors.append(f"{name} missing shared Scale marker {marker!r}")

    for category in ("cartographic_interpolation","camera_intent"):
        examples=categories.get(category,{}).get("examples",[])
        if not isinstance(examples,list) or not examples:
            errors.append(f"{category} must document concrete local examples")

    if errors:
        print("WORLD MAP SCALE CLASSIFICATION FAILED")
        for e in errors: print("-",e)
        return 1
    print("WORLD MAP SCALE CLASSIFICATION PASSED: behavioral gates are shared; presentation/camera values are classified.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
