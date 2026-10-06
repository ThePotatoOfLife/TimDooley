#!/usr/bin/env python3
"""Build a bounded, retrospective conflict event-aggregate snapshot from UCDP GED CSV.

This importer deliberately discards event-level coordinates after aggregation.
It emits coarse grid polygons with aggregate event/fatality counts only.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,re
from collections import defaultdict
from datetime import date,datetime,timezone
from pathlib import Path

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def parse_date(value:str)->date:
    text=str(value or "").strip()
    for fmt in ("%Y-%m-%d","%Y/%m/%d","%d/%m/%Y","%m/%d/%Y"):
        try: return datetime.strptime(text,fmt).date()
        except ValueError: pass
    raise ValueError(f"unsupported date {value!r}")

def num(value:str)->float:
    return float(str(value or "").strip())

def floor_cell(v:float,size:float)->float:
    return math.floor(v/size)*size

def polygon(lon:float,lat:float,size:float):
    e=lon+size;n=lat+size
    return {"type":"Polygon","coordinates":[[[lon,lat],[e,lat],[e,n],[lon,n],[lon,lat]]]}

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--source-contract",type=Path,required=True)
    p.add_argument("--start",required=True)
    p.add_argument("--end",required=True)
    p.add_argument("--retrieved-at",required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--country",action="append",default=[])
    p.add_argument("--grid-degrees",type=float,default=1.0)
    p.add_argument("--min-events",type=int,default=3)
    p.add_argument("--max-features",type=int,default=2500)
    p.add_argument("--max-bytes",type=int,default=1500000)
    args=p.parse_args()
    if not args.input.is_file() or not args.source_contract.is_file(): raise SystemExit("required input missing")
    contract=json.loads(args.source_contract.read_text(encoding="utf-8"))
    if contract.get("intended_geometry_meaning")!="event_aggregate": raise SystemExit("source contract must be event_aggregate")
    if args.grid_degrees < 0.5: raise SystemExit("grid-degrees below 0.5 is too precise for this aggregate layer")
    start,end=parse_date(args.start),parse_date(args.end)
    if start>end: raise SystemExit("start after end")
    if end>date(2025,12,31): raise SystemExit("historical aggregate must end no later than 2025-12-31")
    allowed={str(x).casefold() for x in args.country}
    required=set(contract.get("required_input_columns") or [])
    cells=defaultdict(lambda:{"events":0,"best":0,"countries":set(),"start":None,"end":None})
    with args.input.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        missing=required-set(reader.fieldnames or [])
        if missing: raise SystemExit(f"input missing columns: {sorted(missing)}")
        for row in reader:
            try:
                ds,de=parse_date(row["date_start"]),parse_date(row["date_end"])
            except ValueError:
                continue
            if de<start or ds>end: continue
            country=str(row["country"] or "").strip()
            if allowed and country.casefold() not in allowed: continue
            try:
                lat,lon=num(row["latitude"]),num(row["longitude"])
                best=max(0,int(float(str(row["best"] or "0").strip() or 0)))
            except Exception:
                continue
            if not (-90<=lat<=90 and -180<=lon<=180): continue
            x=floor_cell(lon,args.grid_degrees); y=floor_cell(lat,args.grid_degrees)
            cell=cells[(x,y)]
            cell["events"]+=1; cell["best"]+=best; cell["countries"].add(country)
            cell["start"]=ds if cell["start"] is None else min(cell["start"],ds)
            cell["end"]=de if cell["end"] is None else max(cell["end"],de)
    features=[]
    for (lon,lat),cell in sorted(cells.items()):
        if cell["events"]<args.min_events: continue
        fid=f"ucdp-ged261-{start.isoformat()}-{end.isoformat()}-{lon:.2f}-{lat:.2f}"
        features.append({
          "type":"Feature","id":fid,
          "properties":{
            "id":fid,"geometry_meaning":"event_aggregate",
            "event_count":cell["events"],"best_fatalities":cell["best"],
            "countries":sorted(x for x in cell["countries"] if x),
            "observed_start":cell["start"].isoformat(),"observed_end":cell["end"].isoformat(),
            "temporal_precision":"date-range","source_ids":["ucdp-ged-26.1"],
            "confidence":"direct","not_live":True,"administrative_independence":True,
            "status_note":"Historical coarse event aggregate. Not a live front line, control map, sovereignty claim or tactical tracking layer."
          },
          "geometry":polygon(lon,lat,args.grid_degrees)
        })
    if len(features)>args.max_features: raise SystemExit(f"output feature count {len(features)} exceeds {args.max_features}")
    payload={
      "type":"FeatureCollection",
      "properties":{
        "snapshot_id":f"ucdp-ged261-{start.isoformat()}-{end.isoformat()}",
        "conflict_id":"global-organized-violence",
        "geometry_meaning":"event_aggregate",
        "observed_start":start.isoformat(),"observed_end":end.isoformat(),
        "published_at":None,"temporal_precision":"date-range",
        "source_ids":["ucdp-ged-26.1"],"confidence":"direct",
        "status_note":"Historical coarse event aggregate from UCDP GED 26.1.",
        "not_live":True,"administrative_independence":True,
        "retrieved_at":args.retrieved_at,"built_at":datetime.now(timezone.utc).isoformat(),
        "input_sha256":sha256(args.input),"grid_degrees":args.grid_degrees,
        "minimum_events_per_cell":args.min_events
      },"features":features
    }
    raw=(json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"\n").encode()
    if len(raw)>args.max_bytes: raise SystemExit(f"output bytes {len(raw)} exceeds {args.max_bytes}")
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_bytes(raw)
    print(f"WORLD MAP CONFLICT EVENT AGGREGATE IMPORT PASSED · {len(features)} cells · {len(raw)} bytes")
    return 0
if __name__=="__main__": raise SystemExit(main())
