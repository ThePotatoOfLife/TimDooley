#!/usr/bin/env python3
"""Synchronize Room public-surface projections from the canonical nested-Room registry."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUBS=ROOT/"data/house/subrooms.json"
HOLD=ROOT/"data/house/holdings.json"
DOS=ROOT/"data/house/room-dossiers.json"

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def dump(path,data): path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def projected_dossier_surfaces(ids, surface_by_id):
    rows=[]
    for sid in ids:
        s=surface_by_id.get(sid)
        if not s: continue
        rows.append({"id":sid,"title":s.get("title",sid),"route":s.get("canonical_route") or s.get("route"),"surface_type":s.get("surface_type")})
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true",help="fail if projections are stale instead of writing")
    args=ap.parse_args()
    subs=load(SUBS); holds=load(HOLD); dossiers=load(DOS)
    surfaces=load(ROOT/"data/house/public-surfaces.json")
    canonical={r["id"]:list(r.get("public_surface_ids",[])) for r in subs.get("subrooms",[]) if isinstance(r,dict) and r.get("id")}
    surface_by_id={r["id"]:r for r in surfaces.get("surfaces",[]) if isinstance(r,dict) and r.get("id")}
    holding_rows={r.get("room_id"):r for r in holds.get("holdings",[]) if isinstance(r,dict) and r.get("room_id")}
    holding_counts={rid:int(row.get("primary_file_count",0)) for rid,row in holding_rows.items()}
    changes=[]

    for row in holds.get("holdings",[]):
        rid=row.get("room_id")
        if rid not in canonical: continue
        want=canonical[rid]
        if row.get("public_surface_ids",[])!=want:
            changes.append(f"holdings:{rid}")
            row["public_surface_ids"]=want

    for row in dossiers.get("dossiers",[]):
        rid=row.get("room_id")
        if rid not in canonical: continue
        want=projected_dossier_surfaces(canonical[rid],surface_by_id)
        if row.get("public_surfaces",[])!=want:
            changes.append(f"dossiers-surfaces:{rid}")
            row["public_surfaces"]=want
        holding=row.setdefault("knowledge_holdings",{})
        want_count=holding_counts.get(rid,0)
        if holding.get("primary_file_count")!=want_count:
            changes.append(f"dossiers-holding-count:{rid}")
            holding["primary_file_count"]=want_count
        want_featured=list((holding_rows.get(rid) or {}).get("featured_holdings",[]))
        if holding.get("featured",[])!=want_featured:
            changes.append(f"dossiers-featured-holdings:{rid}")
            holding["featured"]=want_featured

    if args.check:
        if changes:
            print("ROOM PUBLIC-SURFACE SYNC CHECK FAILED")
            for c in changes: print("-",c)
            return 1
        print(f"Room public-surface projections aligned for {len(canonical)} Rooms.")
        return 0

    if changes:
        holds["updated"]="2026-09-20"; dossiers["updated"]="2026-09-20"
        dump(HOLD,holds); dump(DOS,dossiers)
        print("Updated",len(changes),"Room projection records.")
    else:
        print("No Room public-surface projection changes required.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
