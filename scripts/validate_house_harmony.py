#!/usr/bin/env python3
"""Validate whole-House coherence across ownership, Rooms, objects and public projection."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def main():
    errors=[]
    rooms=load("data/house/rooms.json").get("rooms",[])
    subs=load("data/house/subrooms.json").get("subrooms",[])
    interfaces=load("data/house/interfaces.json").get("interfaces",[])
    holdings=load("data/house/holdings.json").get("holdings",[])
    dossiers=load("data/house/room-dossiers.json").get("dossiers",[])
    inhabitants=load("data/house/room-inhabitants.json").get("inhabitants",[])
    surfaces=load("data/house/public-surfaces.json").get("surfaces",[])
    health=load("data/house/spatial-house-health.json")

    room_ids={x.get("id") for x in rooms if isinstance(x,dict)}
    sub_ids={x.get("id") for x in subs if isinstance(x,dict)}
    surface_ids={x.get("id") for x in surfaces if isinstance(x,dict)}
    holding_ids={x.get("room_id") for x in holdings if isinstance(x,dict)}
    dossier_ids={x.get("room_id") for x in dossiers if isinstance(x,dict)}
    holding_by={x.get("room_id"):x for x in holdings if isinstance(x,dict)}
    dossier_by={x.get("room_id"):x for x in dossiers if isinstance(x,dict)}

    if len(room_ids)!=10:
        errors.append(f"expected 10 canonical Dwellings, found {len(room_ids)}")
    if len(sub_ids)!=38:
        errors.append(f"expected 38 nested Rooms, found {len(sub_ids)}")

    inhabitant_room_ids=set()
    maturity=Counter()
    for obj in inhabitants:
        if not isinstance(obj,dict):
            continue
        maturity[obj.get("maturity","unspecified")]+=1
        for rid in obj.get("room_ids",[]):
            if rid not in sub_ids:
                errors.append(f"inhabitant {obj.get('id')} references unknown Room {rid}")
            else:
                inhabitant_room_ids.add(rid)

    for row in subs:
        if not isinstance(row,dict):
            continue
        rid=row.get("id")
        parent=row.get("parent_room_id")
        if parent not in room_ids:
            errors.append(f"{rid} has unknown parent {parent}")
        if not row.get("adjacent_subroom_ids"):
            errors.append(f"{rid} has no adjacent Room")
        for other in row.get("adjacent_subroom_ids",[]):
            if other not in sub_ids:
                errors.append(f"{rid} references unknown adjacent Room {other}")
        if not row.get("public_surface_ids"):
            errors.append(f"{rid} has no public projection")
        for sid in row.get("public_surface_ids",[]):
            if sid not in surface_ids:
                errors.append(f"{rid} references unknown public surface {sid}")
        if rid not in holding_ids:
            errors.append(f"{rid} has no House holdings record")
        if rid not in dossier_ids:
            errors.append(f"{rid} has no Room dossier")
        if rid not in inhabitant_room_ids:
            errors.append(f"{rid} has no registered inhabitant/case/object")
        if rid in holding_by and rid in dossier_by:
            sub_surfaces=sorted(row.get("public_surface_ids",[]))
            holding_surfaces=sorted(holding_by[rid].get("public_surface_ids",[]))
            dossier_surfaces=sorted(
                x.get("id") for x in dossier_by[rid].get("public_surfaces",[])
                if isinstance(x,dict) and x.get("id")
            )
            if sub_surfaces!=holding_surfaces or sub_surfaces!=dossier_surfaces:
                errors.append(
                    f"{rid} public-surface projection drift: "
                    f"subroom={sub_surfaces} holdings={holding_surfaces} dossier={dossier_surfaces}"
                )

    for edge in interfaces:
        if not isinstance(edge,dict):
            continue
        if edge.get("from") not in sub_ids or edge.get("to") not in sub_ids:
            errors.append(f"interface {edge.get('id')} has unknown endpoint")
        if not edge.get("guard") or not edge.get("preserves"):
            errors.append(f"interface {edge.get('id')} is missing guard/preserved invariants")

    by_surface={x.get("id"):x for x in surfaces if isinstance(x,dict)}
    for sid,row in by_surface.items():
        seen=set()
        cur=sid
        while cur:
            if cur in seen:
                errors.append(f"public-surface parent cycle detected from {sid}: {cur}")
                break
            seen.add(cur)
            parent=(by_surface.get(cur) or {}).get("primary_parent")
            if parent==cur:
                errors.append(f"public surface {cur} cannot parent itself")
                break
            cur=parent
    for s in surfaces:
        if not isinstance(s,dict):
            continue
        parent=s.get("primary_parent")
        if parent and parent not in by_surface:
            errors.append(f"surface {s.get('id')} has unknown parent {parent}")
        for rid in s.get("primary_room_ids",[]):
            if rid not in room_ids:
                errors.append(f"surface {s.get('id')} references unknown Dwelling {rid}")

    counts=health.get("counts",{})
    if counts.get("dwellings")!=len(room_ids):
        errors.append("House health dwelling count drift")
    if counts.get("nested_rooms")!=len(sub_ids):
        errors.append("House health nested-room count drift")
    if counts.get("inhabitants")!=len(inhabitants):
        errors.append(f"House health inhabitant count drift: snapshot={counts.get('inhabitants')} live={len(inhabitants)}")
    if counts.get("inhabitant_maturity")!=dict(maturity):
        errors.append(f"House health maturity counts drift: snapshot={counts.get('inhabitant_maturity')} live={dict(maturity)}")

    checks=health.get("checks",{})
    expected_true=(
        "all_nested_rooms_have_valid_parent",
        "all_registered_adjacencies_resolve",
        "all_inhabitant_room_ids_resolve",
        "all_nested_room_interior_routes_exist",
        "all_nested_rooms_have_inhabitants",
        "all_public_surface_references_resolve",
        "all_room_dossiers_present",
        "all_room_holdings_present",
    )
    for key in expected_true:
        if checks.get(key) is not True:
            errors.append(f"House health invariant not asserted true: {key}")

    if errors:
        print("HOUSE HARMONY VALIDATION FAILED")
        for e in errors:
            print("-",e)
        return 1

    print(
        "HOUSE HARMONY VALIDATION PASSED: "
        f"{len(room_ids)} Dwellings · {len(sub_ids)} Rooms · "
        f"{len(interfaces)} guarded interfaces · {len(inhabitants)} inhabitants · "
        f"{len(surfaces)} public surfaces"
    )
    return 0

if __name__=="__main__":
    raise SystemExit(main())
