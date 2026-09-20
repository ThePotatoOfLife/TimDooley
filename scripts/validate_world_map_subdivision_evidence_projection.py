#!/usr/bin/env python3
"""Validate generic subdivision evidence projection into search and inspector."""
from __future__ import annotations
import shutil, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUB=ROOT/"world-map/3d-subdivisions.js"
SEARCH=ROOT/"world-map/3d-search.js"
ADL=ROOT/"world-map/3d-adl-heat.js"

def main()->int:
    errors=[]
    for path in (SUB,SEARCH,ADL):
        if not path.is_file(): errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP SUBDIVISION EVIDENCE PROJECTION FAILED")
        for e in errors: print("-",e)
        return 1
    sub=SUB.read_text(encoding="utf-8",errors="replace")
    search=SEARCH.read_text(encoding="utf-8",errors="replace")
    adl=ADL.read_text(encoding="utf-8",errors="replace")
    for token in ("registerEvidenceProvider","evidenceSummaries(id)","subdivisionEvidenceHtml","data-subdivision-evidence-provider"):
        if token not in sub: errors.append(f"subdivision runtime missing {token!r}")
    for token in ("evidenceSummaries?.(id)","result.evidence?.length","evidenceLabel"):
        if token not in search: errors.append(f"unified search missing generic evidence projection {token!r}")
    if "adl-heat" in search.lower():
        errors.append("unified search must not hard-code ADL provider identity")
    for token in ("registerSubdivisionEvidence","registerEvidenceProvider?.('adl-heat'"):
        if token not in adl: errors.append(f"ADL provider registration missing {token!r}")
    node=shutil.which("node")
    if node:
        for path in (SUB,SEARCH,ADL):
            result=subprocess.run([node,"--check",str(path)],cwd=ROOT,text=True,capture_output=True,check=False)
            if result.returncode: errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: "+(result.stderr.strip() or result.stdout.strip()))
    if errors:
        print("WORLD MAP SUBDIVISION EVIDENCE PROJECTION FAILED")
        for e in errors: print("-",e)
        return 1
    print("WORLD MAP SUBDIVISION EVIDENCE PROJECTION PASSED")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
