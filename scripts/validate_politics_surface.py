#!/usr/bin/env python3
"""Validate Politics reader, backend ownership and SEO/provenance boundaries."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(rel:str)->str:
    return (ROOT/rel).read_text(encoding="utf-8",errors="replace")

def main()->int:
    errors=[]
    page=read("politics/index.html")
    part1=read("politics/parts/part-01.html")
    part3=read("politics/parts/part-03.html")
    comp=json.loads(read("knowledge/politics/tim-dooley-politics-geopolitics-compendium.json"))
    domains=json.loads(read("knowledge/politics/tim-dooley-politics-policy-domain-index.json"))
    source_map=json.loads(read("data/canonical-source-map.json"))
    seo=read("scripts/seo_strategy.py")

    required_page=[
        '<link rel="canonical" href="https://thepotatooflife.github.io/TimDooley/politics/">',
        'property="og:type" content="article"',
        'name="twitter:card" content="summary"',
        '"@type":"Article"',
        '"@type":"BreadcrumbList"',
        '"@type":"FAQPage"',
        'id="policy-domains-title"',
        'tim-dooley-politics-policy-domain-index.json',
        'Comparator, not provenance',
        'What remains unresolved',
    ]
    for marker in required_page:
        if marker not in page:
            errors.append(f"politics/index.html missing marker: {marker}")

    if page.find("~2015") > page.find("2026-01-15"):
        errors.append("static politics corpus should present early political history before 2026 material where chronology is intended")

    if part1.find("<td>~2015</td>") > part1.find("<td>2026-01-15</td>"):
        errors.append("political development timeline is not chronological: ~2015 appears after 2026-01-15")
    if part1.find("<td>~2016</td>") > part1.find("<td>2026-01-15</td>"):
        errors.append("political development timeline is not chronological: ~2016 appears after 2026-01-15")

    for marker in ("Current-world comparator, checked 30 September 2026","does not establish authorship, influence or identity"):
        if marker not in part3:
            errors.append(f"politics technology comparator missing boundary marker: {marker}")

    if comp.get("method",{}).get("derived_domain_view")!="knowledge/politics/tim-dooley-politics-policy-domain-index.json":
        errors.append("politics compendium does not point to derived policy-domain view")
    if "provenance_contract" not in comp.get("method",{}):
        errors.append("politics compendium missing provenance_contract")

    entries=comp.get("entries",[])
    for domain in domains.get("domains",[]):
        if not domain.get("entry_indexes"):
            errors.append(f"policy domain {domain.get('id')} has no canonical entry references")
        for idx in domain.get("entry_indexes",[]):
            if not isinstance(idx,int) or idx<0 or idx>=len(entries):
                errors.append(f"policy domain {domain.get('id')} references invalid compendium entry index {idx}")
    if domains.get("canonical_owner")!="knowledge/politics/tim-dooley-politics-geopolitics-compendium.json":
        errors.append("policy-domain index must remain derived from canonical politics compendium")

    politics_family=source_map.get("families",{}).get("politics")
    if not politics_family:
        errors.append("canonical-source-map missing politics family")
    else:
        if politics_family.get("canonical_owner")!="knowledge/politics/tim-dooley-politics-geopolitics-compendium.json":
            errors.append("canonical-source-map politics owner is wrong")
        if politics_family.get("domain_view")!="knowledge/politics/tim-dooley-politics-policy-domain-index.json":
            errors.append("canonical-source-map politics domain view is wrong")

    for marker in ('"politics": Strategy(', '"Article"', '"politics",\n        "Tim Dooley politics and geopolitics"', '    "politics",\n    "world",'):
        if marker not in seo:
            errors.append(f"seo_strategy.py missing Politics first-class route marker: {marker}")

    modes={e.get("mode") for e in entries}
    expected={"explicit_position","policy_proposal","programme_design","geopolitical_prediction","research_lead","mythic_symbolism"}
    missing=sorted(expected-modes)
    if missing:
        errors.append("politics compendium lost required mode distinctions: "+", ".join(missing))

    if errors:
        print("POLITICS SURFACE VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"POLITICS SURFACE VALIDATION PASSED · {len(entries)} dated entries · {len(domains.get('domains',[]))} policy domains")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
