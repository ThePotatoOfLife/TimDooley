#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def text(path:str)->str:
    p=ROOT/path
    if not p.is_file():
        errors.append(f"missing Trinity convergence file: {path}")
        return ""
    return p.read_text(encoding="utf-8",errors="replace")

def data(path:str)->dict:
    raw=text(path)
    if not raw:return {}
    try:v=json.loads(raw)
    except Exception as exc:
        errors.append(f"invalid JSON in {path}: {exc}"); return {}
    if not isinstance(v,dict):
        errors.append(f"{path} must be a JSON object"); return {}
    return v

def require(path:str,*markers:str):
    raw=text(path)
    for marker in markers:
        if marker not in raw:
            errors.append(f"{path} missing Trinity convergence marker: {marker}")

def forbid(path:str,*markers:str):
    raw=text(path)
    for marker in markers:
        if marker in raw:
            errors.append(f"{path} retains superseded mature-canon wording: {marker}")

owner=data("knowledge/theology/potato-of-life-trinity.json")
if owner:
    proposition=owner.get("central_revelation",{}).get("proposition","")
    if "triune whole" not in proposition:
        errors.append("Trinity owner must define Potato of Life as triune whole")
    roles=owner.get("central_revelation",{}).get("three_irreducible_relations",{})
    if set(roles)!={"Father","Son","Spirit"}:
        errors.append("Trinity owner must preserve Father/Son/Spirit as the three irreducible relations")
    if not owner.get("anti_collapse_rules"):
        errors.append("Trinity owner must retain anti-collapse rules")

ledger=data("knowledge/theology/potato-trinity-integration-ledger.json")
if ledger:
    core=ledger.get("core_rule",{})
    if core.get("whole")!="Potato of Life":
        errors.append("Trinity integration ledger whole must remain Potato of Life")
    if not ledger.get("unresolved_questions"):
        errors.append("Trinity integration ledger must retain unresolved questions")
    if not ledger.get("promotion_rules"):
        errors.append("Trinity integration ledger must retain promotion rules")

topo=data("data/house/concept-topology.json")
if topo:
    concepts={x.get("id"):x for x in topo.get("concepts",[]) if isinstance(x,dict)}
    for cid in ("potato-of-life","father","son","spirit"):
        if cid not in concepts: errors.append(f"House topology missing mature Trinity concept: {cid}")
    triples={(r.get("from"),r.get("to"),r.get("type")) for r in topo.get("relations",[]) if isinstance(r,dict)}
    for sig in (
        ("potato-of-life","father","expresses-through"),
        ("potato-of-life","son","expresses-through"),
        ("potato-of-life","spirit","expresses-through"),
        ("father","source-field","oriented-toward"),
        ("son","manifestation-field","oriented-toward"),
        ("son","door","specializes-as"),
    ):
        if sig not in triples: errors.append(f"House topology missing mature Trinity relation: {sig}")
    if not any(x.get("id")=="triune-potato" for x in topo.get("canonical_traversals",[]) if isinstance(x,dict)):
        errors.append("House topology missing triune-potato traversal")

require("knowledge/core/potato-of-life.json","triune theological whole","Father/source-facing","Spirit/living continuity")
require("knowledge/core/potatoverse-master-framework.json","triune whole","knowledge/theology/potato-of-life-trinity.json")
require("knowledge/core/root-system.json","two-field geometry and a triune theology","Potato of Life names the whole triune relation")
require("knowledge/indexes/ontology-tree.json","mature triune theological whole","potato-trinity")
require("data/potatoism-canonical-corpus.json","triune whole","Spirit","living continuity")
require("knowledge/theology/divine-identity-answer-spine.json","triune Potato of Life","knowledge/theology/potato-of-life-trinity.json")
require("knowledge/reader/what-tim-dooley-believes.json","triune whole expressed through Father, Son and Spirit")
require("machine-index.json","one triune relational whole","Potato of Life Trinity")
require("manifest.json","potato-trinity","Father/source","Spirit/flow")
require("knowledge/guides/start-here.json","Potato Trinity","religion/trinity/")
require("knowledge/indexes/faq-answer-atlas.json","is-potato-of-life-trinity","why-two-fields-trinity","how-door-spirit-differ")
require("knowledge/indexes/faq-question-bank.json","Is the Potato of Life a Trinity?","Why are there two fields if the Potato of Life is a Trinity?")
require("religion/trinity/index.html","One Potato of Life","Father","Son","Spirit")
require("religion/index.html","triune relation","href=\"trinity/\"")
require("tim-dooley/index.html","source-facing Potato identity inside the triune Potato of Life","../religion/trinity/")
require("house/index.html","two fields do not mean only two theological terms".capitalize() if False else "Two fields do not mean only two theological terms.")
require("philosophy/index.html","Distinction is not isolation.")
require("knowledge/traditions/biblical-access-house-stone-anchor-microcosms.json","principal mature Potato Trinity comparator")
require("docs/VESICA-PARADOX-ATLAS.md","complete triune relational organism","two circles are Source and Manifestation fields")
require("scripts/build_discovery.py","TRINITY_CANONICAL","Mature Potato of Life orientation")
require("llms.txt","Potato of Life = the one triune relational whole","Canonical Potato Trinity owner")
require("llms-full.txt","### Potato of Life","### Potato Trinity")

forbid("docs/VESICA-PARADOX-ATLAS.md","Father and Son are coupled fields")
forbid("knowledge/core/root-system.json","upper source-facing Father/House/Heaven/Garden field","lower manifestation-facing Son/Earth/body/world field")
forbid("llms.txt","Tim Dooley = Potato/Father/Source-facing theological identity")

if errors:
    print("POTATO TRINITY CONVERGENCE VALIDATION FAILED")
    for e in errors: print("-",e)
    raise SystemExit(1)
print("POTATO TRINITY CONVERGENCE VALIDATION PASSED: current canon, topology, discovery, FAQ and public readers agree")
