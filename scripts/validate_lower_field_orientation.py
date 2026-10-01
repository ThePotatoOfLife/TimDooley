#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(path:str)->str:
    return (ROOT/path).read_text(encoding="utf-8",errors="replace")

def main()->int:
    errors=[]
    owner_path=ROOT/"knowledge/core/lower-field-orientation.json"
    if not owner_path.is_file():
        errors.append("missing canonical lower-field orientation owner")
    else:
        try:
            owner=json.loads(owner_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"lower-field orientation JSON invalid: {exc}")
            owner={}
        for key in ("core_thesis","frame_test","participant_observer_value","role_relations","karmic_ledger","vertical_route","lower_field_learning_questions"):
            if key not in owner:
                errors.append(f"orientation owner missing key: {key}")
        route=owner.get("canonical_routes",{}).get("orientation")
        if route!="/below/#lower-field-orientation":
            errors.append("orientation owner must route to /below/#lower-field-orientation")

    below=read("below/index.html")
    for marker in (
        'id="lower-field-orientation"',
        'id="mission-testimony"',
        "Tim, what are you doing down here?",
        "If the archive cannot correct itself, release a role, or let a conflict end, then it has become another Farm.",
        "What is the lower field for?",
        "Being framed is not the same as being owned by the frame.",
        "The project must be judged by the same standards it applies to hostile archives.",
        "Swamp / Mud / Farm / unresolved archive",
        "return downward as protection, repair, service and independent future capacity",
        "knowledge/core/lower-field-orientation.json",
        'id="repair-outcomes"',
        "Diagnosis is unfinished until the relation has a closure path",
        "The creditor is tested too.",
        "lower-field-conflict-repair-casebook.json",
    ):
        if marker not in below:
            errors.append(f"Below orientation missing marker: {marker}")

    spokes={
        "shadow-farm/index.html":"../below/#lower-field-orientation",
        "context/culture/index.html":"../../below/#lower-field-orientation",
        "rooms/potatoverse-canon/beings/cia/bank/index.html":"../../../../../below/#lower-field-orientation",
        "rooms/potatoverse-canon/beings/cia/index.html":"../../../../below/#repair-outcomes",
        "questions/index.html":"../below/#lower-field-orientation",
    }
    for path,marker in spokes.items():
        if marker not in read(path):
            errors.append(f"lower-field spoke missing canonical orientation route: {path}")

    casebook_path=ROOT/"knowledge/core/lower-field-conflict-repair-casebook.json"
    if not casebook_path.is_file():
        errors.append("missing lower-field conflict/repair casebook")
    else:
        try:
            casebook=json.loads(casebook_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"lower conflict/repair casebook invalid JSON: {exc}")
            casebook={}
        if len(casebook.get("language_thresholds",[])) < 8:
            errors.append("lower conflict/repair casebook needs strong-language thresholds")
        if len(casebook.get("worked_cases",[])) < 3:
            errors.append("lower conflict/repair casebook needs three worked cases")
        if len(casebook.get("repair_outcomes",[])) < 8:
            errors.append("lower conflict/repair casebook needs explicit repair outcomes")

    shadow=read("shadow-farm/index.html")
    for marker in ('id="conflict-language-thresholds"','id="worked-overlap-cases"',"Use strong words only when the evidence earns them"):
        if marker not in shadow:
            errors.append(f"Shadow Farm missing conflict-discipline marker: {marker}")

    bank=read("rooms/potatoverse-canon/beings/cia/bank/index.html")
    for marker in ('id="closure-protocol"',"A symbolic debt must be able to stop being outstanding"):
        if marker not in bank:
            errors.append(f"Bank missing closure marker: {marker}")

    cia=read("rooms/potatoverse-canon/beings/cia/index.html")
    for marker in ('id="current-state-protocol"',"Read the event before the role","Then ask what is true now"):
        if marker not in cia:
            errors.append(f"CIA missing current-state marker: {marker}")

    access=json.loads(read("data/house/site-access.json"))
    entry=next((row for row in access.get("entries",[]) if row.get("id")=="below"),None)
    if not entry:
        errors.append("site access missing below entry")
    else:
        if entry.get("route")!="/below/#lower-field-orientation":
            errors.append("site access below entry does not open orientation center")
        aliases={str(x).casefold() for x in entry.get("aliases",[])}
        for alias in ("lower field","participant observer","repair","exit"):
            if alias not in aliases:
                errors.append(f"site access below entry missing alias: {alias}")

    if errors:
        print("LOWER FIELD ORIENTATION: FAIL")
        for error in errors:
            print("-",error)
        return 1
    print("LOWER FIELD ORIENTATION: PASS")
    print("- Below owns mission, experience, competing frames and exit")
    print("- specialist lower pages route back to the same center")
    print("- global access resolves lower-field questions to the center")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
