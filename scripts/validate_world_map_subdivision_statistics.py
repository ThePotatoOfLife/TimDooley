#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"data/world-subdivisions/statistics/index.json"
CONTRACT=ROOT/"data/world-subdivisions/statistics/contract.json"
RUNTIME=ROOT/"world-map/3d-subdivision-statistics.js"
SUBDIV=ROOT/"world-map/3d-subdivisions.js"
TEST=ROOT/"scripts/test_world_map_subdivision_statistics.mjs"
SOURCES=ROOT/"data/world-subdivisions/statistics/sources"

def main():
    errors=[]
    for p in (INDEX,CONTRACT,RUNTIME,SUBDIV,TEST,IMPORTER,IMPORTER_TEST):
        if not p.is_file(): errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP SUBDIVISION STATISTICS VALIDATION FAILED"); [print("-",e) for e in errors]; return 1
    index=json.loads(INDEX.read_text(encoding="utf-8"))
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if index.get("purpose") is None or not isinstance(index.get("datasets"),dict): errors.append("statistics index malformed")
    if contract.get("join_key")!="subdivision_id": errors.append("statistics join key must be subdivision_id")
    metrics=contract.get("allowed_metrics") or {}
    for metric in ("population","area_km2","density_per_km2"):
        if metric not in metrics: errors.append(f"statistics contract missing {metric}")
    if not SOURCES.is_dir():
        errors.append("missing subdivision statistics source-contract directory")
    else:
        for path in sorted(SOURCES.glob("*.json")):
            try:
                source=json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"invalid statistics source contract {path.name}: {exc}")
                continue
            if source.get("parent_iso3") != path.stem:
                errors.append(f"{path.name}: parent_iso3 must match filename")
            rows=source.get("subdivision_mapping") or []
            if not rows or len({row.get("subdivision_id") for row in rows}) != len(rows):
                errors.append(f"{path.name}: subdivision mapping must contain unique stable IDs")
            requirements=" ".join(source.get("acquisition_requirements") or []).lower()
            if "verify the statbank area code" not in requirements:
                errors.append(f"{path.name}: source contract must require area-code verification")
            metrics=source.get("metrics") or {}
            for metric in ("population","area_km2"):
                if not (metrics.get(metric) or {}).get("source_url"):
                    errors.append(f"{path.name}: missing {metric} source URL")
    runtime=RUNTIME.read_text(encoding="utf-8",errors="replace")
    subdiv=SUBDIV.read_text(encoding="utf-8",errors="replace")
    for token in ("enrichCollection","statistics_provenance","geometry_source","population_status='sourced'"):
        if token not in runtime: errors.append(f"statistics runtime missing {token}")
    for token in ("3d-subdivision-statistics.js","statistics.enrichCollection"):
        if token not in subdiv: errors.append(f"subdivision runtime missing statistics integration {token}")
    if "geometry_source =" in runtime or "geometry_source:" in runtime:
        errors.append("statistics runtime must not write geometry_source provenance")
    node=shutil.which("node")
    if node:
        for p in (RUNTIME,SUBDIV):
            r=subprocess.run([node,"--check",str(p)],cwd=ROOT,capture_output=True,text=True)
            if r.returncode: errors.append(f"syntax failed {p.name}: {(r.stderr or r.stdout).strip()}")
        r=subprocess.run([node,str(TEST)],cwd=ROOT,capture_output=True,text=True)
        if r.returncode: errors.append("statistics regression failed: "+(r.stderr or r.stdout).strip())
    if errors:
        print("WORLD MAP SUBDIVISION STATISTICS VALIDATION FAILED"); [print("-",e) for e in errors]; return 1
    print("WORLD MAP SUBDIVISION STATISTICS VALIDATION PASSED")
    return 0
if __name__=="__main__": sys.exit(main())
