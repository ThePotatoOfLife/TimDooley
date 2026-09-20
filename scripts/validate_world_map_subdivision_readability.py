#!/usr/bin/env python3
"""Validate U.S. subdivision readability and narrow-screen presentation rules."""
from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/world-subdivisions/USA.geo.json"
RUNTIME=ROOT/"world-map/3d-subdivisions.js"
TEST=ROOT/"scripts/test_world_map_subdivision_bounded_runtime.mjs"

def main()->int:
    errors=[]
    for p in (DATA,RUNTIME,TEST):
        if not p.is_file(): errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP SUBDIVISION READABILITY FAILED")
        for e in errors: print("-",e)
        return 1

    payload=json.loads(DATA.read_text(encoding="utf-8"))
    features=payload.get("features") or []
    ids={str(f.get("id") or (f.get("properties") or {}).get("id") or "") for f in features}
    for sid in ("US-AK","US-HI","US-DC"):
        if sid not in ids: errors.append(f"canonical USA partition missing {sid}")
    if len(ids) != 51: errors.append(f"USA readability fixture expects 50 states + DC; got {len(ids)}")

    runtime=RUNTIME.read_text(encoding="utf-8",errors="replace")
    for token in (
        "SELECTED_LABEL_ID",
        "atlas-subdivision-selected-label",
        "NARROW_SCREEN_MAX",
        "NARROW_LABEL_DELAY",
        "GLOBE_LABEL_DELAY",
        "function projectionMode()",
        "function labelPresentation()",
        "function syncSelectedLabel(",
        "function syncLabelPresentation()",
        "'text-allow-overlap':true",
        "window.addEventListener?.('resize', syncLabelPresentation)",
        "window.addEventListener?.('potato-atlas-projection-change', syncLabelPresentation)",
    ):
        if token not in runtime: errors.append(f"subdivision runtime missing readability marker {token!r}")
    if "setLayerZoomRange?.(LABEL_ID" not in runtime:
        errors.append("narrow-screen label policy must adjust presentation zoom without changing shared capability thresholds")
    if "syncSelectedLabel(selectedId)" not in runtime or "syncSelectedLabel(null)" not in runtime:
        errors.append("selected-label filter must follow select and clear lifecycle")

    node=shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run subdivision readability regression")
    else:
        result=subprocess.run([node,"--check",str(RUNTIME)],cwd=ROOT,text=True,capture_output=True,check=False)
        if result.returncode: errors.append("subdivision runtime syntax failed: "+(result.stderr.strip() or result.stdout.strip()))
        result=subprocess.run([node,str(TEST)],cwd=ROOT,text=True,capture_output=True,check=False)
        if result.returncode: errors.append("bounded subdivision regression failed: "+(result.stderr.strip() or result.stdout.strip()))

    if errors:
        print("WORLD MAP SUBDIVISION READABILITY FAILED")
        for e in errors: print("-",e)
        return 1
    print("WORLD MAP SUBDIVISION READABILITY PASSED: AK/HI/DC present, narrow/globe labels deferred, selected label guaranteed.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
