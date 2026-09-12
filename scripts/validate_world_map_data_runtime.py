#!/usr/bin/env python3
"""Validate the generated empirical data contract for the ordinary World Map."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "build_world_map_runtime.py"
MEMBERSHIPS = ROOT / "data" / "world-institution-memberships.json"
REGISTRY = ROOT / "data" / "world-map-layer-registry.json"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"
LAYER_RUNTIME = ROOT / "world-map" / "3d-layer-registry.js"
CARD = ROOT / "world-map" / "3d-country-card.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
BUILD_SITE = ROOT / "scripts" / "build_site.py"

REQUIRED_GROUPS = {"eu":27,"nato":32,"brics":11,"aukus":3,"five-eyes":5,"oecd":38,"g7":7,"g20":19,"schengen":29,"euro-area":21}
PROVEN_CURRENT_STATS = {
    "stat.gdp-per-capita":"gdp_per_capita",
    "stat.real-growth":"real_growth",
    "stat.inflation":"inflation",
    "stat.unemployment":"unemployment",
}
COVERAGE_GATED_STATS = {
    "stat.gdp-per-capita-ppp":"gdp_per_capita_ppp",
    "stat.labour-force-participation":"labour_force_participation",
    "stat.life-expectancy":"life_expectancy",
    "stat.fertility":"fertility",
    "stat.urbanization":"urbanization",
    "stat.internet-use":"internet_use",
    "stat.co2-per-capita":"co2_per_capita",
    "stat.debt-to-gdp":"debt_to_gdp",
}
RUNTIME_STATS = {**PROVEN_CURRENT_STATS, **COVERAGE_GATED_STATS}


def load_json(path: Path, errors: list[str]):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"invalid/missing {path.relative_to(ROOT)}: {exc}"); return {}

def read(path: Path, errors: list[str]):
    try: return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc: errors.append(f"missing {path.relative_to(ROOT)}: {exc}"); return ""

def load_generator(errors):
    try:
        spec = importlib.util.spec_from_file_location("build_world_map_runtime", GENERATOR); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
    except Exception as exc: errors.append(f"could not load runtime generator: {exc}"); return None


def main() -> int:
    errors=[]
    memberships=load_json(MEMBERSHIPS,errors); registry=load_json(REGISTRY,errors)
    compositor=read(COMPOSITOR,errors); layer_runtime=read(LAYER_RUNTIME,errors); card=read(CARD,errors); world_bar=read(WORLD_BAR,errors); build_site=read(BUILD_SITE,errors)
    groups=memberships.get("groups",{})
    for gid,count in REQUIRED_GROUPS.items():
        group=groups.get(gid,{}); members=group.get("members",[])
        if len(members)!=count: errors.append(f"{gid} must expose {count} members; found {len(members)}")
        if len(set(members))!=len(members): errors.append(f"{gid} members must be unique")
        for key in ("source","source_url","as_of"):
            if not group.get(key): errors.append(f"{gid} missing {key}")
    if groups.get("g20",{}).get("non_country_members") != ["African Union","European Union"]: errors.append("G20 non-country members incorrect")
    if "BGR" not in groups.get("euro-area",{}).get("members",[]): errors.append("Euro Area must include BGR")

    entries={e.get("id"):e for e in registry.get("entries",[]) if isinstance(e,dict)}
    for gid in REQUIRED_GROUPS:
        entry=entries.get(f"group.{gid}",{})
        if entry.get("availability")!="current": errors.append(f"group.{gid} must be current")
        if entry.get("source_owner")!="data/world-institution-memberships.json": errors.append(f"group.{gid} must use canonical membership owner")
    for eid,metric in RUNTIME_STATS.items():
        entry=entries.get(eid,{})
        if entry.get("source_owner")!="data/world-map-data-runtime.json": errors.append(f"{eid} must use runtime source")
        if entry.get("runtime_metric")!=metric: errors.append(f"{eid} must declare runtime_metric={metric}")
    for token in ("effectiveAvailable","runtime_metric","coverage > 0","isAvailable"):
        if token not in layer_runtime: errors.append(f"layer registry missing coverage gate marker: {token}")
    for token in ("WORLD_DATA_RUNTIME_URL","__potatoAtlasDataRuntime","applyRuntimeScalar","runtime_metric","coverage"):
        if token not in compositor: errors.append(f"compositor missing {token}")
    for token in ("__potatoAtlasDataRuntime","runtime_metric","metricMeta","populationObservation","areaObservation"):
        if token not in card: errors.append(f"country card missing {token}")
    for token in ("__potatoAtlasDataRuntime","coverage","countries"):
        if token not in world_bar: errors.append(f"world bar missing {token}")
    if "build_world_map_runtime" not in build_site: errors.append("build_site must generate runtime")

    generator=load_generator(errors)
    if generator:
        try: runtime=generator.build_runtime()
        except Exception as exc: errors.append(f"build_runtime failed: {exc}"); runtime={}
        if runtime:
            if runtime.get("country_count")!=195: errors.append("runtime country_count must remain 195")
            for gid,count in REQUIRED_GROUPS.items():
                if runtime.get("groups",{}).get(gid,{}).get("member_count")!=count: errors.append(f"runtime group {gid} count wrong")
            metrics=runtime.get("metrics",{}); countries=runtime.get("countries",{})
            for metric in RUNTIME_STATS.values():
                meta=metrics.get(metric,{}); coverage=meta.get("coverage",0)
                if not isinstance(coverage,int) or not 0 <= coverage <= 195: errors.append(f"invalid coverage for {metric}: {coverage}")
                if not meta.get("unit"): errors.append(f"{metric} missing unit")
            for metric in PROVEN_CURRENT_STATS.values():
                if metrics.get(metric,{}).get("coverage",0)<=0: errors.append(f"proven current metric {metric} lost coverage")
            for code,country in countries.items():
                for metric_id,cell in country.get("metrics",{}).items():
                    for key in ("value","unit","period","source"):
                        if key not in cell: errors.append(f"{code}/{metric_id} missing {key}")
            scalars=runtime.get("scalars",{}).get("by_entity",{})
            if scalars.get("GRL",{}).get("population",{}).get("value")!=56740: errors.append("GRL population scalar missing")
            if scalars.get("GRL",{}).get("area",{}).get("value")!=2166086: errors.append("GRL area scalar missing")
    if errors:
        print("World Map data runtime validation FAILED:"); [print(f" - {e}") for e in errors]; return 1
    print("World Map data runtime validation passed."); return 0

if __name__ == "__main__": sys.exit(main())
