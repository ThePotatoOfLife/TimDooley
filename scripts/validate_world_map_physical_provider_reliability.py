#!/usr/bin/env python3
"""Validate shared Physical provider health and explicit request-budget ownership."""
from __future__ import annotations
import shutil, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/"world-map/3d-physical-layers.js"
BUDGET=ROOT/"world-map/3d-request-budget.js"
HYDRO=ROOT/"world-map/3d-physical-hydrology.js"
MODULES={
    "terrain": ROOT/"world-map/3d-physical-terrain.js",
    "water": ROOT/"world-map/3d-physical-water.js",
    "land-cover": ROOT/"world-map/3d-physical-land-cover.js",
    "aridity": ROOT/"world-map/3d-physical-deserts.js",
}
TEST=ROOT/"scripts/test_world_map_request_budget.mjs"

def main()->int:
    errors=[]
    for p in (RUNTIME,BUDGET,HYDRO,TEST,*MODULES.values()):
        if not p.is_file():
            errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP PHYSICAL PROVIDER RELIABILITY FAILED")
        for e in errors: print("-",e)
        return 1

    runtime=RUNTIME.read_text(encoding="utf-8",errors="replace")
    for token in ("provider:row.source?.provider","retryable:true","attempts:0","lastSuccessAt:null","lastErrorAt:null","potato-atlas-physical-layer-status"):
        if token not in runtime:
            errors.append(f"Physical mixer missing health schema marker {token!r}")

    budget=BUDGET.read_text(encoding="utf-8",errors="replace")
    for token in ("createRequestBudget","maxConcurrent","inFlight","deduplicated","cacheHits","maxObservedConcurrent","clearCache","window.__potatoAtlasRequestBudget"):
        if token not in budget:
            errors.append(f"request budget missing {token!r}")
    if "setInterval(" in budget or "new MutationObserver(" in budget:
        errors.append("request budget must not use polling or DOM observation")

    hydro=HYDRO.read_text(encoding="utf-8",errors="replace")
    for token in ("__potatoAtlasRequestBudget","requestBudget.run(","cacheMs:30_000","AbortController","reportStatus('partial'","reportStatus('error'"):
        if token not in hydro:
            errors.append(f"Hydrology missing shared reliability marker {token!r}")
    if "const response = await fetch(url" in hydro and "requestBudget.run(" not in hydro:
        errors.append("Hydrology explicit fetch bypasses shared request budget")

    provider_tokens={
        "terrain":("physical.terrain","provider:'Mapterhorn'","reportStatus('loading'","reportStatus('active'","reportStatus('error'"),
        "water":("physical.water.base","provider:'Natural Earth'","reportStatus('loading'","reportStatus('active'","reportStatus('error'","reportStatus('partial'"),
        "land-cover":("physical.land-cover","provider:'ESA WorldCover'","reportStatus('loading'","reportStatus('active'","reportStatus('error'","reportStatus('partial'"),
        "aridity":("physical.aridity","provider:'The Nature Conservancy'","reportStatus('loading'","reportStatus('active'","reportStatus('error'","reportStatus('partial'"),
    }
    for name,path in MODULES.items():
        text=path.read_text(encoding="utf-8",errors="replace")
        for token in provider_tokens[name]:
            if token not in text:
                errors.append(f"{name} provider health missing {token!r}")

    node=shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run request-budget regression")
    else:
        for path in (BUDGET,HYDRO,*MODULES.values()):
            result=subprocess.run([node,"--check",str(path)],cwd=ROOT,text=True,capture_output=True,check=False)
            if result.returncode:
                errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: "+(result.stderr.strip() or result.stdout.strip()))
        result=subprocess.run([node,str(TEST)],cwd=ROOT,text=True,capture_output=True,check=False)
        if result.returncode:
            errors.append("request-budget regression failed: "+(result.stderr.strip() or result.stdout.strip()))

    if errors:
        print("WORLD MAP PHYSICAL PROVIDER RELIABILITY FAILED")
        for e in errors: print("-",e)
        return 1
    print("WORLD MAP PHYSICAL PROVIDER RELIABILITY PASSED")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
