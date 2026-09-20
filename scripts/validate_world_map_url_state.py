#!/usr/bin/env python3
"""Validate canonical World Map URL-state mutation ownership."""
from __future__ import annotations
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OWNER=ROOT/"world-map/3d-url-state.js"
BOOT=ROOT/"world-map/3d-bootstrap.js"
TEST=ROOT/"scripts/test_world_map_url_state.mjs"
MIGRATED=(
    ROOT/"world-map/3d-layer-registry.js",
    ROOT/"world-map/3d-physical-layers.js",
    ROOT/"world-map/3d-spatial-overlays.js",
    ROOT/"world-map/3d-evidence-layers.js",
    ROOT/"world-map/3d-adl-heat.js",
    ROOT/"world-map/3d-axis.js",
    ROOT/"world-map/3d-axis-depth.js",
    ROOT/"world-map/3d-mud-below-us.js",
    ROOT/"world-map/3d-spatial-overlay-ui.js",
    ROOT/"world-map/3d-lenses.js",
    ROOT/"world-map/3d-fields.js",
    ROOT/"world-map/3d-networks.js",
)

def main()->int:
    errors=[]
    for path in (OWNER,BOOT,TEST,*MIGRATED):
        if not path.is_file(): errors.append(f"missing URL-state contract file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP URL STATE VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1

    owner=OWNER.read_text(encoding="utf-8",errors="replace")
    for token in ("function claim(","function patch(","assertOwned","history.replaceState","window.__potatoAtlasUrlState","potato-atlas-url-state-ready"):
        if token not in owner: errors.append(f"URL State owner missing marker: {token}")

    boot=BOOT.read_text(encoding="utf-8",errors="replace")
    url_idx=boot.find("loadAfterPaint('URL State', './3d-url-state.js')")
    layer_idx=boot.find("loadAfterPaint('Layer Registry', './3d-layer-registry.js')")
    if url_idx < 0 or layer_idx < 0 or url_idx > layer_idx:
        errors.append("URL State must load before Layer Registry in normal bootstrap")

    for path in MIGRATED:
        text=path.read_text(encoding="utf-8",errors="replace")
        if "__potatoAtlasUrlState" not in text or ".claim(" not in text or ".patch(" not in text:
            errors.append(f"{path.relative_to(ROOT)} has not migrated to URL State owner")
        if "history.replaceState" in text:
            errors.append(f"{path.relative_to(ROOT)} still owns direct history.replaceState after migration")

    node=shutil.which("node")
    if not node: errors.append("node executable unavailable; cannot run URL-state regression")
    else:
        for path in (OWNER,*MIGRATED):
            result=subprocess.run([node,"--check",str(path)],cwd=ROOT,text=True,capture_output=True,check=False)
            if result.returncode: errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: "+(result.stderr.strip() or result.stdout.strip()))
        result=subprocess.run([node,str(TEST)],cwd=ROOT,text=True,capture_output=True,check=False)
        if result.returncode: errors.append("URL-state regression failed: "+(result.stderr.strip() or result.stdout.strip()))

    if errors:
        print("WORLD MAP URL STATE VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1
    print("WORLD MAP URL STATE VALIDATION PASSED: phase-1 domain writers are centrally owned.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
