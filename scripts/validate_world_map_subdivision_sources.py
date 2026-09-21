#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/"data"/"world-subdivisions"/"sources"
IMPORTER=ROOT/"scripts"/"import_world_adm1.py"
SUBDIVISION_INDEX=ROOT/"data"/"world-subdivisions"/"index.json"
PLACES_INDEX=ROOT/"data"/"world-places"/"index.json"
REQUIRED_SOURCE=("owner","product","product_url","service_url","source_vintage","license","license_id","attribution")
REQUIRED_MAPPING=("name_field","code_field","default_type")
REQUIRED_IMPORTER=("script","max_bytes","expected_count","source_label","source_ref","source_vintage","representation_note")

def main()->int:
    errors=[]
    try:
        subdivision_index=json.loads(SUBDIVISION_INDEX.read_text(encoding="utf-8"))
        places_index=json.loads(PLACES_INDEX.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"could not load live regional/place indexes: {exc}")
        subdivision_index={"partitions":{}}
        places_index={"countries":{}}
    live_partitions=set((subdivision_index.get("partitions") or {}).keys())
    place_partitions=set((places_index.get("countries") or {}).keys())
    missing_places=sorted(live_partitions-place_partitions)
    if missing_places:
        errors.append(f"live subdivision countries require bounded Places partitions: {missing_places}")
    if not SOURCES.is_dir():
        errors.append("missing data/world-subdivisions/sources")
        rows=[]
    else:
        rows=sorted(SOURCES.glob("*.json"))
    if not rows:
        errors.append("no reviewed subdivision source contracts")
    for path in rows:
        try: data=json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path.name}: invalid JSON: {exc}"); continue
        iso3=str(data.get("iso3") or "")
        if not re.fullmatch(r"[A-Z]{3}",iso3): errors.append(f"{path.name}: invalid iso3")
        if path.stem != iso3: errors.append(f"{path.name}: filename must match iso3")
        if data.get("status") not in {"source-verified-download-pending","source-acquired-review-pending","ready-for-import"}:
            errors.append(f"{path.name}: unsupported review status")
        if iso3 in live_partitions and data.get("status") != "ready-for-import":
            errors.append(f"{path.name}: live subdivision promotion requires source status ready-for-import")
        if iso3 in live_partitions and iso3 not in place_partitions:
            errors.append(f"{path.name}: live promotion requires bounded Places partition for {iso3}")
        if int(data.get("admin_level") or 0)!=1: errors.append(f"{path.name}: only ADM1 source contracts supported")
        count=int(data.get("expected_feature_count") or 0)
        if count<=0: errors.append(f"{path.name}: expected_feature_count must be positive")
        prefix=str(data.get("canonical_id_prefix") or "")
        if not prefix.endswith("-"): errors.append(f"{path.name}: canonical_id_prefix must end in '-'")
        src=data.get("source") or {}
        for key in REQUIRED_SOURCE:
            if not str(src.get(key) or "").strip(): errors.append(f"{path.name}: source.{key} missing")
        if src.get("license_id")=="dl-de/by-2-0" and "dl-de/by-2-0" not in str(src.get("attribution") or ""):
            errors.append(f"{path.name}: BKG-style attribution must preserve dl-de/by-2-0")
        acq=data.get("acquisition") or {}
        if acq.get("runtime_fetch_allowed") is not False:
            errors.append(f"{path.name}: administrative source acquisition must remain build-time only")
        mapping=data.get("field_mapping") or {}
        for key in REQUIRED_MAPPING:
            if not str(mapping.get(key) or "").strip(): errors.append(f"{path.name}: field_mapping.{key} missing")
        viewport=data.get("viewport_bounds") or {}
        for key in ("west","east","south","north"):
            if not isinstance(viewport.get(key),(int,float)): errors.append(f"{path.name}: viewport_bounds.{key} missing")
        imp=data.get("importer") or {}
        for key in REQUIRED_IMPORTER:
            if imp.get(key) in (None,""): errors.append(f"{path.name}: importer.{key} missing")
        if int(imp.get("expected_count") or 0)!=count:
            errors.append(f"{path.name}: importer.expected_count must match expected_feature_count")
        if int(imp.get("max_bytes") or 0)>1500000:
            errors.append(f"{path.name}: importer max_bytes exceeds canonical partition budget")
        reqs=data.get("promotion_requirements") or []
        if not any("Places" in str(x) for x in reqs):
            errors.append(f"{path.name}: promotion must require bounded Places coverage")
        if not any("SHA-256" in str(x) for x in reqs):
            errors.append(f"{path.name}: promotion must require source hash")
    if not IMPORTER.is_file(): errors.append("missing generic ADM1 importer")
    if errors:
        print("WORLD MAP SUBDIVISION SOURCE CONTRACT VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"WORLD MAP SUBDIVISION SOURCE CONTRACT VALIDATION PASSED · {len(rows)} reviewed source candidate(s)")
    return 0
if __name__=="__main__": sys.exit(main())
