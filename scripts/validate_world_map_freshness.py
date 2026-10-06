#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"data/world-map-freshness-contract.json"
RUNTIME=ROOT/"world-map/3d-data-freshness.js"
EVIDENCE=ROOT/"world-map/3d-evidence-layers.js"
PLACES=ROOT/"world-map/3d-places.js"
WORLD_BAR=ROOT/"world-map/3d-world-bar.js"
TEST=ROOT/"scripts/test_world_map_freshness.mjs"
EXPECTED={"current","latest-available","delayed","historical","stale","unknown-vintage","planned"}
def main():
    errors=[]
    for path in (CONTRACT,RUNTIME,EVIDENCE,PLACES,WORLD_BAR,TEST):
        if not path.is_file(): errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP FRESHNESS VALIDATION FAILED"); [print("-",e) for e in errors]; return 1
    data=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if set((data.get("statuses") or {}).keys()) != EXPECTED: errors.append("freshness vocabulary drift")
    rules=" ".join(data.get("rules") or []).lower()
    if "age alone" not in rules or "availability" not in rules: errors.append("freshness contract must reject age-only inference and separate provider availability")
    runtime=RUNTIME.read_text(encoding="utf-8",errors="replace")
    for token in ("window.__potatoAtlasFreshness","function describe(","function register(","function active(","unknown-vintage","latest-available","historical-snapshot"):
        if token not in runtime: errors.append(f"freshness runtime missing {token}")
    evidence=EVIDENCE.read_text(encoding="utf-8",errors="replace")
    places=PLACES.read_text(encoding="utf-8",errors="replace")
    for label,source in (("Evidence",evidence),("Places",places)):
        if "__potatoAtlasFreshness" not in source or "freshness.describe" not in source: errors.append(f"{label} must consume shared freshness owner")
        if "freshness.register" not in source: errors.append(f"{label} must register active freshness with the shared owner")
    world_bar=WORLD_BAR.read_text(encoding="utf-8",errors="replace")
    for token in ("__potatoAtlasFreshness?.active?.()", "Data status", "potato-atlas-freshness-change"):
        if token not in world_bar: errors.append(f"Current Map freshness projection missing {token}")
    node=shutil.which("node")
    if node:
        for path in (RUNTIME,EVIDENCE,PLACES,WORLD_BAR):
            result=subprocess.run([node,"--check",str(path)],cwd=ROOT,text=True,capture_output=True)
            if result.returncode: errors.append(f"syntax failed {path.relative_to(ROOT)}: {(result.stderr or result.stdout).strip()}")
        result=subprocess.run([node,str(TEST)],cwd=ROOT,text=True,capture_output=True)
        if result.returncode: errors.append("freshness regression failed: "+(result.stderr or result.stdout).strip())
    if errors:
        print("WORLD MAP FRESHNESS VALIDATION FAILED"); [print("-",e) for e in errors]; return 1
    print("WORLD MAP FRESHNESS VALIDATION PASSED")
    return 0
if __name__=="__main__": raise SystemExit(main())
