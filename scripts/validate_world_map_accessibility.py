#!/usr/bin/env python3
"""Validate World Map keyboard/focus accessibility ownership."""
from __future__ import annotations
import shutil, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ACCESS=ROOT/"world-map/3d-accessibility.js"
INSPECTOR=ROOT/"world-map/3d-inspector-router.js"
LIFECYCLE=ROOT/"world-map/3d-panel-lifecycle.js"
KEY_TEST=ROOT/"scripts/test_world_map_accessibility_keyboard.mjs"
INSPECTOR_TEST=ROOT/"scripts/test_world_map_inspector_router.mjs"

def main()->int:
    errors=[]
    for p in (ACCESS,INSPECTOR,LIFECYCLE,KEY_TEST,INSPECTOR_TEST):
        if not p.is_file(): errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP ACCESSIBILITY VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1

    access=ACCESS.read_text(encoding="utf-8",errors="replace")
    inspector=INSPECTOR.read_text(encoding="utf-8",errors="replace")
    lifecycle=LIFECYCLE.read_text(encoding="utf-8",errors="replace")
    for token in ("function closeMenu(","function syncMenuAria(","event.key !== 'Escape'","aria-expanded","summary.focus","__potatoAtlasAccessibility"):
        if token not in access: errors.append(f"Accessibility owner missing {token!r}")
    for token in ("function captureFocusTarget(","function focusInspectorHeading(","function restoreFocus(","returnFocus","closed?.returnFocus"):
        if token not in inspector: errors.append(f"Inspector focus contract missing {token!r}")
    if "Accessibility', './3d-accessibility.js'" not in lifecycle:
        errors.append("panel lifecycle must boot shared accessibility owner")

    node=shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run accessibility regressions")
    else:
        for p in (ACCESS,INSPECTOR):
            result=subprocess.run([node,"--check",str(p)],cwd=ROOT,text=True,capture_output=True,check=False)
            if result.returncode: errors.append(f"JavaScript syntax failed for {p.relative_to(ROOT)}: "+(result.stderr.strip() or result.stdout.strip()))
        for p in (KEY_TEST,INSPECTOR_TEST):
            result=subprocess.run([node,str(p)],cwd=ROOT,text=True,capture_output=True,check=False)
            if result.returncode: errors.append(f"{p.name} failed: "+(result.stderr.strip() or result.stdout.strip()))

    if errors:
        print("WORLD MAP ACCESSIBILITY VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print("WORLD MAP ACCESSIBILITY VALIDATION PASSED")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
