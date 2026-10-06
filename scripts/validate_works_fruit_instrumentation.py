#!/usr/bin/env python3
"""Validate concrete Works/Fruit instrumentation."""
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"data/house/works-fruit-contract.json"
WAVE=ROOT/"data/house/works-fruit-wave-001.json"
WORKS=ROOT/"works/index.html"

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main()->int:
    errors=[]
    for p in (CONTRACT,WAVE,WORKS):
        if not p.exists():
            errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        print("WORKS FRUIT VALIDATION FAILED")
        for e in errors: print(" -",e)
        return 1

    contract=load(CONTRACT); wave=load(WAVE)
    allowed=set(contract.get("fruit_types",[]))
    required=set(contract.get("work_record_fields",[]))
    records=wave.get("records",[])
    if len(records)<5:
        errors.append("first Works/Fruit wave should instrument at least five works")
    seen=set()
    for rec in records:
        wid=rec.get("work_id")
        if not wid: errors.append("record missing work_id"); continue
        if wid in seen: errors.append(f"duplicate work_id {wid}")
        seen.add(wid)
        missing=sorted(k for k in required if k not in rec)
        if missing: errors.append(f"{wid} missing contract fields: {missing}")
        bad=sorted(set(rec.get("fruit_types",[]))-allowed)
        if bad: errors.append(f"{wid} has invalid fruit types: {bad}")
        if not rec.get("source_rooms"): errors.append(f"{wid} has no source_rooms")
        if not rec.get("center_nodes"): errors.append(f"{wid} has no center_nodes")
        if not rec.get("claim/evidence_boundary"): errors.append(f"{wid} lacks claim/evidence boundary")
        reception=rec.get("observable_reception")
        if not isinstance(reception,dict) or not reception.get("status"):
            errors.append(f"{wid} lacks typed observable_reception status")
        if not rec.get("externalities_or_risks"):
            errors.append(f"{wid} lacks risks/externalities")
        if not rec.get("future_seed"):
            errors.append(f"{wid} lacks future_seed")
        if not rec.get("revision_status"):
            errors.append(f"{wid} lacks revision_status")

    text=WORKS.read_text(encoding="utf-8",errors="replace")
    for marker in ("works-fruit-contract.json","Works are Fruit"):
        if marker not in text:
            errors.append(f"works reader missing {marker!r}")
    if "works-fruit-wave-001.json" not in text:
        errors.append("works reader does not link first instrumented Works/Fruit wave")

    if errors:
        print("WORKS FRUIT VALIDATION FAILED")
        for e in errors: print(" -",e)
        return 1
    print(f"WORKS FRUIT VALIDATION PASSED ({len(records)} instrumented works)")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
