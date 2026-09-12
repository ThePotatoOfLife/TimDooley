#!/usr/bin/env python3
"""Validate Wave A World Map foundation enrichment behavior."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCALARS = ROOT / "scripts" / "world_map_scalars.py"
COVERAGE = ROOT / "scripts" / "build_world_map_coverage.py"
RUNTIME_BUILDER = ROOT / "scripts" / "build_world_map_runtime.py"
ENTITIES = ROOT / "data" / "world-map-entities.json"
AXIS = ROOT / "data" / "world-axis-profiles.json"
REGISTRY = ROOT / "data" / "world-map-layer-registry.json"
MEMBERSHIPS = ROOT / "data" / "world-institution-memberships.json"
COUNTRIES = ROOT / "data" / "countries"
INDEX = COUNTRIES / "index.json"
CARD = ROOT / "world-map" / "3d-country-card.js"
ENTITY_RUNTIME = ROOT / "world-map" / "3d-entity-runtime.js"
HOVER = ROOT / "world-map" / "3d-hover.js"
SCALAR_BRIDGE = ROOT / "world-map" / "3d-scalar-runtime-bridge.js"
LAYER_RUNTIME = ROOT / "world-map" / "3d-layer-registry.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"

FIRST_NORTH = {"LVA":("primary","high"),"LTU":("primary","high"),"POL":("primary","high"),"ROU":("secondary","medium"),"CZE":("secondary","medium"),"SVK":("secondary","medium")}
NEW_METRIC_ENTRIES = {
    "gdp_per_capita_ppp":"stat.gdp-per-capita-ppp",
    "labour_force_participation":"stat.labour-force-participation",
    "life_expectancy":"stat.life-expectancy",
    "fertility":"stat.fertility",
    "urbanization":"stat.urbanization",
    "internet_use":"stat.internet-use",
    "co2_per_capita":"stat.co2-per-capita",
}
CORE_GROUPS={"nato","brics","aukus","five-eyes"}


def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def import_path(path: Path,name: str):
    spec=importlib.util.spec_from_file_location(name,path)
    if not spec or not spec.loader: raise RuntimeError(f"cannot import {path}")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def main() -> int:
    errors=[]
    if not SCALARS.is_file(): errors.append("missing scripts/world_map_scalars.py")
    else:
        try:
            scalars=import_path(SCALARS,"world_map_scalars")
            pop=scalars.resolve_population({"population":{"value":12.5,"unit":"million","year":2024,"source":"fixture"}})
            if not pop or pop.get("value")!=12_500_000: errors.append("top-level population resolver must normalize million-person values")
            if scalars.resolve_population({}) is not None: errors.append("missing population must resolve None, never 0")
        except Exception as exc: errors.append(f"scalar helper contract failed: {exc}")

    grl=load(ENTITIES).get("entities",{}).get("GRL",{})
    if grl.get("population",{}).get("value")!=56740: errors.append("Greenland population must remain 56,740")
    area=grl.get("area",{})
    if area.get("value")!=2166086 or area.get("unit")!="km²" or area.get("definition")!="total area": errors.append("Greenland must own total area 2,166,086 km²")
    for path in (CARD,ENTITY_RUNTIME,HOVER):
        text=path.read_text(encoding="utf-8",errors="replace")
        for token in ("populationObservation","areaObservation"):
            if token not in text: errors.append(f"{path.relative_to(ROOT)} must consume shared {token}")
    bridge=SCALAR_BRIDGE.read_text(encoding="utf-8",errors="replace") if SCALAR_BRIDGE.is_file() else ""
    for token in ("runtime_scalar","scalars?.by_entity","atlasEntityScalarValue"):
        if token not in bridge: errors.append(f"scalar bridge missing {token}")
    if "3d-scalar-runtime-bridge.js" not in BOOTSTRAP.read_text(encoding="utf-8",errors="replace"): errors.append("bootstrap must load scalar runtime bridge")

    if not COVERAGE.is_file(): errors.append("missing scripts/build_world_map_coverage.py")
    else:
        try:
            coverage=import_path(COVERAGE,"build_world_map_coverage")
            derived=coverage.derive_record_coverage({"coverage":{"relationships":0,"sources":0},"relationships":[{"type":"trade","target":"X"}],"sources":["official source"]})
            if derived.get("relationships",{}).get("represented")!=1: errors.append("coverage ledger must derive actual relationships")
            if derived.get("provenance",{}).get("source_records",0)<1: errors.append("coverage ledger must derive actual sources")
        except Exception as exc: errors.append(f"coverage helper contract failed: {exc}")

    index=load(INDEX); canonical={row["iso3"]:row["id"] for row in index.get("countries",[])}
    if canonical.get("TUR")!="turkiye": errors.append("canonical TUR owner must be turkiye")
    if (COUNTRIES/"turkey.json").is_file(): errors.append("legacy turkey.json must not remain active")
    turkey_text=json.dumps(load(COUNTRIES/"turkiye.json"),ensure_ascii=False).lower()
    for token in ("turkish straits","nato","g20","european union"):
        if token not in turkey_text: errors.append(f"turkiye missing recovered context: {token}")
    if "migration_source" not in turkey_text or "turkey.json" not in turkey_text: errors.append("turkiye must retain migration provenance")

    profiles=load(AXIS).get("profiles",{})
    for code,(role,confidence) in FIRST_NORTH.items():
        north=[o for o in profiles.get(code,{}).get("orientations",[]) if o.get("axis")=="north"]
        if not north: errors.append(f"{code} missing North profile"); continue
        item=north[0]
        if item.get("role")!=role or item.get("confidence")!=confidence: errors.append(f"{code} North role/confidence must be {role}/{confidence}")
        if not item.get("basis") or not item.get("note"): errors.append(f"{code} North profile must retain basis/note")

    registry=load(REGISTRY); entries={e.get("id"):e for e in registry.get("entries",[]) if isinstance(e,dict)}
    if entries.get("axis.north",{}).get("runtime_axis")!="north": errors.append("axis.north must consume runtime North membership")
    memberships=load(MEMBERSHIPS).get("groups",{})
    for group in CORE_GROUPS:
        if group not in memberships: errors.append(f"membership owner missing {group}")
        if entries.get(f"group.{group}",{}).get("source_owner")!="data/world-institution-memberships.json": errors.append(f"group.{group} must use canonical institutional owner")
    gate_text=LAYER_RUNTIME.read_text(encoding="utf-8",errors="replace")
    for token in ("effectiveAvailable","coverage > 0","runtime_metric"):
        if token not in gate_text: errors.append(f"layer runtime missing coverage gate {token}")

    try:
        builder=import_path(RUNTIME_BUILDER,"build_world_map_runtime"); runtime=builder.build_runtime()
        if runtime.get("country_count")!=195: errors.append("runtime country_count must remain 195")
        north_members=set(runtime.get("axis",{}).get("memberships",{}).get("north",[]))
        for code in {"EST","UKR","TUR",*FIRST_NORTH.keys()}:
            if code not in north_members: errors.append(f"runtime North membership missing {code}; pressing N would omit it")
        scalar_plane=runtime.get("scalars",{}).get("by_entity",{})
        if scalar_plane.get("GRL",{}).get("population",{}).get("value")!=56740: errors.append("runtime GRL population missing")
        if scalar_plane.get("GRL",{}).get("area",{}).get("value")!=2166086: errors.append("runtime GRL area missing")
        metrics=runtime.get("metrics",{})
        for metric,entry_id in NEW_METRIC_ENTRIES.items():
            if metric not in metrics: errors.append(f"runtime missing metric definition {metric}")
            entry=entries.get(entry_id,{})
            if entry.get("runtime_metric")!=metric: errors.append(f"registry missing runtime_metric mapping for {entry_id}")
    except Exception as exc: errors.append(f"runtime build contract failed: {exc}")

    if errors:
        print("World Map foundation enrichment validation FAILED:"); [print(f" - {e}") for e in errors]; return 1
    print("World Map foundation enrichment validation passed."); return 0

if __name__=="__main__": sys.exit(main())
