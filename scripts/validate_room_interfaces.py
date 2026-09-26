#!/usr/bin/env python3
"""Validate governed nested-Room interfaces and required high-value handoffs."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUBROOMS=ROOT/"data/house/subrooms.json"
INTERFACES=ROOT/"data/house/interfaces.json"

REQUIRED_PAIRS={
    frozenset(("symbolic-architecture","math-geometry")):"formalization",
    frozenset(("math-geometry","physics-cosmology")):"empirical-promotion",
    frozenset(("theology-god-language","bible-christianity")):"comparative-translation",
    frozenset(("politics-governance","law-justice")):"institutional-translation",
    frozenset(("politics-governance","economy-finance")):"policy-impact",
    frozenset(("subculture-group-formation","provenance-evidence")):"claim-audit",
    frozenset(("information-ecology","provenance-evidence")):"source-resolution",
    frozenset(("canon-identities","developmental-genealogy")):"historical-decomposition",
    frozenset(("prediction-revelation-time","witness-attestation")):"prior-wording-check",
    frozenset(("visual-art","symbolic-architecture")):"composition-to-operator",
    frozenset(("games-simulations","systems-dynamics")):"mechanics-to-model",
    frozenset(("music-sound","developmental-genealogy")):"creative-attestation",
}

def main()->int:
    errors=[]
    sub=json.loads(SUBROOMS.read_text(encoding="utf-8"))
    data=json.loads(INTERFACES.read_text(encoding="utf-8"))
    room_ids={r.get("id") for r in sub.get("subrooms",[]) if isinstance(r,dict)}
    rows=[r for r in data.get("interfaces",[]) if isinstance(r,dict)]
    seen=set()
    by_pair={}
    for row in rows:
        iid=row.get("id")
        if not iid: errors.append("interface missing id"); continue
        if iid in seen: errors.append(f"duplicate interface id: {iid}")
        seen.add(iid)
        a,b=row.get("from"),row.get("to")
        if a not in room_ids: errors.append(f"{iid}: unknown from Room {a}")
        if b not in room_ids: errors.append(f"{iid}: unknown to Room {b}")
        if a==b: errors.append(f"{iid}: self-interface is invalid")
        if not str(row.get("changes") or "").strip(): errors.append(f"{iid}: missing changes")
        if not str(row.get("guard") or "").strip(): errors.append(f"{iid}: missing guard")
        pair=frozenset((a,b))
        by_pair.setdefault(pair,[]).append(row)
    for pair,itype in REQUIRED_PAIRS.items():
        matches=by_pair.get(pair,[])
        if not matches:
            errors.append("missing required high-value interface: "+" <-> ".join(sorted(pair)))
            continue
        if not any(r.get("type")==itype for r in matches):
            errors.append("required interface type mismatch for "+" <-> ".join(sorted(pair))+f": expected {itype}")
    if errors:
        print("ROOM INTERFACE VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"Room interfaces: PASS · {len(rows)} governed handoffs; {len(REQUIRED_PAIRS)} high-value crossings protected")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
