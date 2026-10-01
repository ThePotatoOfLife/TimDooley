#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(rel:str)->str:
    return (ROOT/rel).read_text(encoding="utf-8",errors="replace")

def main()->int:
    errors=[]
    page=read("context/culture/index.html")
    owner_path=ROOT/"knowledge/culture/culture-subculture-field-model.json"

    for marker in (
        'id="culture-field-checklist"',
        "Eight things make a culture legible",
        "Subculture is a relation, not a sealed box",
        "participation",
        "identification",
        "centrality",
        "belonging",
        "subcultural capital",
        "social influence &amp; group identity",
        "Roles are learned socially.",
        "Centrality is not personality essence.",
        "watch → imitate → receive feedback",
        'id="language-as-infrastructure"',
        "A role-name can behave like a miniature algorithm",
        'id="ritual-to-norm"',
        "Ritualized scripts can become norms without anyone writing a rulebook",
        'id="information-control-stack"',
        "Who controls the story depends on where in the chain they have leverage",
    ):
        if marker not in page:
            errors.append(f"Culture reader missing field-model marker: {marker}")

    if not owner_path.is_file():
        errors.append("missing structured culture/subculture field model")
    else:
        try:
            owner=json.loads(owner_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"culture field model invalid JSON: {exc}")
            owner={}
        dims=owner.get("dimensions",[])
        ids={row.get("id") for row in dims if isinstance(row,dict)}
        expected={"center","meaning","norms","status","boundary","memory","infrastructure","exit-mutation"}
        missing=expected-ids
        if missing:
            errors.append("culture field model missing dimensions: "+", ".join(sorted(missing)))
        distinctions=owner.get("distinctions",{})
        for key in ("participation_vs_identification","centrality_vs_belonging","boundary_vs_seal","role_vs_essence"):
            if key not in distinctions:
                errors.append(f"culture field model missing distinction: {key}")

    if errors:
        print("CULTURE / SUBCULTURE FIELD MODEL: FAIL")
        for err in errors:
            print("-",err)
        return 1

    print("CULTURE / SUBCULTURE FIELD MODEL: PASS")
    print("- eight reusable dimensions")
    print("- porous/overlapping subculture model")
    print("- participation, identity, centrality and belonging remain distinct")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
