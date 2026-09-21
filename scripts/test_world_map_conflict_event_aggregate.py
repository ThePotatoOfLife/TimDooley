#!/usr/bin/env python3
from __future__ import annotations
import csv,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IMP=ROOT/"scripts/import_world_conflict_event_aggregate.py"
def main()->int:
  errors=[]
  with tempfile.TemporaryDirectory(prefix="conflict-agg-") as td:
    d=Path(td); src=d/"ged.csv"; contract=d/"source.json"; out=d/"out.geojson"
    contract.write_text(json.dumps({"intended_geometry_meaning":"event_aggregate","required_input_columns":["id","date_start","date_end","latitude","longitude","country","best"]}),encoding="utf-8")
    rows=[
      ["1","2025-01-02","2025-01-02","50.1","30.1","Exampleland","2"],
      ["2","2025-01-03","2025-01-03","50.2","30.2","Exampleland","1"],
      ["3","2025-01-04","2025-01-04","50.3","30.3","Exampleland","4"],
      ["4","2025-02-04","2025-02-04","51.3","31.3","Exampleland","5"],
    ]
    with src.open("w",encoding="utf-8",newline="") as f:
      w=csv.writer(f); w.writerow(["id","date_start","date_end","latitude","longitude","country","best"]); w.writerows(rows)
    cmd=[sys.executable,str(IMP),"--input",str(src),"--source-contract",str(contract),"--start","2025-01-01","--end","2025-12-31","--retrieved-at","2026-09-21T00:00:00Z","--output",str(out)]
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    if r.returncode: errors.append((r.stderr or r.stdout).strip())
    else:
      data=json.loads(out.read_text())
      if len(data["features"])!=1: errors.append("min-events suppression or 1-degree aggregation changed")
      else:
        p=data["features"][0]["properties"]
        if p["event_count"]!=3 or p["best_fatalities"]!=7: errors.append("aggregate counts changed")
        if p.get("not_live") is not True or p.get("administrative_independence") is not True: errors.append("safety boundary missing")
      if any("latitude" in json.dumps(f) or "longitude" in json.dumps(f) for f in data["features"]): errors.append("raw coordinate fields leaked")
    too_precise=subprocess.run(cmd+["--grid-degrees","0.1"],cwd=ROOT,capture_output=True,text=True)
    if too_precise.returncode==0: errors.append("sub-0.5-degree tactical precision must fail")
  if errors:
    print("WORLD MAP CONFLICT EVENT AGGREGATE TEST FAILED"); [print("-",e) for e in errors]; return 1
  print("WORLD MAP CONFLICT EVENT AGGREGATE TEST PASSED"); return 0
if __name__=="__main__": raise SystemExit(main())
