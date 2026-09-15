#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "knowledge/guides/reader-residency-map.json"
EXPECTED = {
    "tim-making-things", "ordinary-absurd-tim", "builder-gardener-service",
    "information-architecture-feb-2026", "spiritual-bank-mar-2026",
    "ontology-reversal-mar-apr-2026", "not-a-ghost-repair-may-2026",
    "north-vocabulary-evolution", "door-root-mud-sprout",
    "creative-objects-navigation",
}
FILES = {
    "tim": "tim-dooley/index.html", "collection": "corporium/index.html",
    "works": "works/index.html", "timeline": "timeline/index.html",
    "religion": "religion/index.html", "science": "science/index.html",
    "world": "world/index.html",
}
REQUIRED = {
    "tim": {"tim-making-things", "ordinary-absurd-tim", "builder-gardener-service", "not-a-ghost-repair-may-2026"},
    "collection": {"ordinary-absurd-tim", "builder-gardener-service", "north-vocabulary-evolution", "door-root-mud-sprout", "not-a-ghost-repair-may-2026"},
    "works": {"creative-objects-navigation", "tim-making-things"},
    "timeline": {"information-architecture-feb-2026", "spiritual-bank-mar-2026", "ontology-reversal-mar-apr-2026", "not-a-ghost-repair-may-2026", "north-vocabulary-evolution", "builder-gardener-service"},
    "religion": {"ontology-reversal-mar-apr-2026"},
    "science": {"information-architecture-feb-2026"},
    "world": {"north-vocabulary-evolution"},
}
ALLOWED_TARGETS = set(FILES) | {"story"}
ALLOWED_QUERY = {"tl_q", "tl_epistemic", "tl_exact", "tl_detail", "tl_from", "tl_to", "tl_sort", "tl_layers", "tl_actors", "tl_event"}


def main() -> int:
    errors = []
    if not MAP.exists():
        errors.append("missing knowledge/guides/reader-residency-map.json")
        data = {}
    else:
        data = json.loads(MAP.read_text(encoding="utf-8"))
    if data.get("knowledge_owner") is not False:
        errors.append("residency map must set knowledge_owner=false")
    rows = data.get("residencies", [])
    ids = [r.get("id") for r in rows if isinstance(r, dict)]
    if set(ids) != EXPECTED or len(ids) != len(EXPECTED):
        errors.append("Wave 001 residency IDs do not match the required set")
    by_id = {r["id"]: r for r in rows if isinstance(r, dict) and r.get("id")}
    for rid, row in by_id.items():
        for key in ("title", "summary", "source_class", "canonical_owners", "target_surfaces", "public_copy_rule", "epistemic_boundary"):
            if row.get(key) in (None, "", []):
                errors.append(f"{rid}: missing {key}")
        for owner in row.get("canonical_owners", []):
            if not (ROOT / owner).exists():
                errors.append(f"{rid}: missing owner {owner}")
        unknown = set(row.get("target_surfaces", [])) - ALLOWED_TARGETS
        if unknown:
            errors.append(f"{rid}: unknown targets {sorted(unknown)}")
        if row.get("source_class") == "MEMORY_SUMMARY_PHRASE" and "verified" in str(row.get("public_copy_rule", "")).lower():
            errors.append(f"{rid}: memory-summary material cannot authorize verified quotation")
        if row.get("timeline_query"):
            params = set(parse_qs(urlparse(row["timeline_query"]).query, keep_blank_values=True))
            bad = params - ALLOWED_QUERY
            if bad:
                errors.append(f"{rid}: unsupported Timeline parameters {sorted(bad)}")
    marker_re = re.compile(r'data-residency-id=["\']([^"\']+)["\']')
    for surface, rel in FILES.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        markers = set(marker_re.findall(text))
        for rid in REQUIRED[surface]:
            if rid not in markers:
                errors.append(f"{surface}: missing marker {rid}")
        for rid in markers:
            if rid not in by_id:
                errors.append(f"{surface}: unknown residency marker {rid}")
            elif surface not in by_id[rid].get("target_surfaces", []):
                errors.append(f"{surface}: residency {rid} not targeted here")
    if errors:
        print("Reader residency validation FAILED")
        for error in errors:
            print("-", error)
        return 1
    print(f"Reader residency validation PASS — {len(rows)} residencies across {len(FILES)} surfaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
