#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
IMPORTER=ROOT/"scripts"/"import_world_subdivision_statistics.py"

def main()->int:
    errors=[]
    with tempfile.TemporaryDirectory(prefix="adm1-stats-") as tmp:
        root=Path(tmp)
        contract={
            "parent_iso3":"DNK",
            "source_owner":"Statistics Denmark / fixture",
            "reference_period":"2026-01-01",
            "metrics":{
                "population":{"table":"BEFOLK3","source_url":"https://example.test/BEFOLK3"},
                "area_km2":{"table":"ARE207","source_url":"https://example.test/ARE207"},
            },
            "subdivision_mapping":[
                {"subdivision_id":"DK-1083","name":"Region Syddanmark","statbank_area_code":"R3"},
                {"subdivision_id":"DK-1084","name":"Region Hovedstaden","statbank_area_code":"R4"},
            ],
        }
        contract_path=root/"source.json"
        pop_path=root/"population.csv"
        area_path=root/"area.csv"
        out_path=root/"DNK.json"
        contract_path.write_text(json.dumps(contract),encoding="utf-8")
        pop_path.write_text("code;name;value\nR3;Region Syddanmark;1234567\nR4;Region Hovedstaden;2000000\n",encoding="utf-8")
        area_path.write_text("code;name;value\nR3;Region Syddanmark;12262,5\nR4;Region Hovedstaden;2568,1\n",encoding="utf-8")
        cmd=[
            sys.executable,str(IMPORTER),
            "--source-contract",str(contract_path),
            "--population",str(pop_path),
            "--area",str(area_path),
            "--population-code-column","code","--population-name-column","name","--population-value-column","value",
            "--area-code-column","code","--area-name-column","name","--area-value-column","value",
            "--retrieved-at","2026-09-21T00:00:00Z",
            "--output",str(out_path),
        ]
        result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        if result.returncode:
            errors.append("valid fixture import failed: "+(result.stderr or result.stdout).strip())
        else:
            payload=json.loads(out_path.read_text(encoding="utf-8"))
            if len(payload.get("records") or [])!=2: errors.append("fixture output must contain two records")
            row={r["subdivision_id"]:r for r in payload["records"]}["DK-1083"]
            if row.get("population")!=1234567: errors.append("population semantics changed")
            if row.get("area_km2")!=12262.5: errors.append("Danish decimal-comma area parsing changed")
            if row.get("population_meta",{}).get("source_geography_code")!="R3": errors.append("verified source geography code not retained")
            if not payload.get("inputs",{}).get("population_sha256") or not payload.get("inputs",{}).get("area_sha256"):
                errors.append("source input hashes must be recorded")

        pending=dict(contract)
        pending["subdivision_mapping"]=[{"subdivision_id":"DK-1083","name":"Region Syddanmark"}]
        pending_path=root/"pending.json"; pending_path.write_text(json.dumps(pending),encoding="utf-8")
        bad=subprocess.run([
            sys.executable,str(IMPORTER),"--source-contract",str(pending_path),
            "--population",str(pop_path),"--area",str(area_path),
            "--population-code-column","code","--population-name-column","name","--population-value-column","value",
            "--area-code-column","code","--area-name-column","name","--area-value-column","value",
            "--retrieved-at","2026-09-21T00:00:00Z","--output",str(root/"bad.json")
        ],cwd=ROOT,capture_output=True,text=True)
        if bad.returncode==0: errors.append("importer must fail while source geography codes remain unverified")

    if errors:
        print("WORLD MAP SUBDIVISION STATISTICS IMPORTER TEST FAILED")
        for error in errors: print("-",error)
        return 1
    print("WORLD MAP SUBDIVISION STATISTICS IMPORTER TEST PASSED")
    return 0
if __name__=="__main__": raise SystemExit(main())
