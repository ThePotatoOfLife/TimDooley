#!/usr/bin/env python3
"""Rank weak structured records across the canonical data + knowledge library.

This audit is intentionally role-aware: a tiny schema, registry or routing index can be
healthy, while a tiny first-class concept owner can be a serious content gap.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = (ROOT / "data", ROOT / "knowledge")
COUNTRY_DIRS = {"countries"}
GENERATED_NAMES = {"depth-audit-live.json"}
TEXT_FIELDS = (
    "definition", "context", "purpose", "description", "summary", "mechanisms",
    "couplings", "research_questions", "questions", "failure_modes",
    "evidence_boundary", "boundary", "sources", "source_records",
    "project_extrapolations", "history", "chronology", "function",
    "use_in_project", "interpretation", "meaning", "development", "text",
    "rules", "principles", "relationships",
)
RECORD_KEYS = {
    "records", "entries", "nodes", "events", "people", "nations", "scale",
    "levels", "sector_families", "organizations", "relationships", "facts",
    "periods", "sections", "models", "concepts", "items", "claims",
}
MAJOR_FIELDS = (
    "definition", "context", "mechanisms", "couplings", "relationships",
    "research_questions", "questions", "sources", "source_records",
)
CONTROL_PATTERNS = (
    "index", "registry", "schema", "manifest", "checklist", "backend",
    "router", "routing", "source-map", "coverage-map", "completion-matrix",
)
FIRST_CLASS_PATHS = {
    "knowledge/practice/potato-path.json",
    "knowledge/journey/tim-dooley-journey.json",
    "knowledge/core/heaven-spirit-father.json",
    "knowledge/core/root-system.json",
    "knowledge/core/tim-dooley.json",
    "knowledge/core/tim-role-synthesis.json",
    "knowledge/core/potatoverse-master-framework.json",
    "knowledge/chronology/developmental-genealogy.json",
    "knowledge/science/science-master-index.json",
    "knowledge/body/body-system-master-atlas.json",
    "knowledge/spirit/spirit-context-atlas.json",
    "knowledge/theology/tim-god-question.json",
    "knowledge/philosophy/archive-epistemics.json",
}


def text_value(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(text_value(x) for x in value)
    if isinstance(value, dict):
        return " ".join(text_value(x) for x in value.values())
    return str(value)


def looks_like_record(value):
    if not isinstance(value, dict):
        return False
    identity = value.get("id") or value.get("slug") or value.get("title") or value.get("name")
    return bool(identity) and any(k in value for k in TEXT_FIELDS)


def collect_records(obj, path=""):
    found = []
    if isinstance(obj, dict):
        if looks_like_record(obj):
            found.append((path or "$", obj))
        for key, value in obj.items():
            if key in RECORD_KEYS or isinstance(value, (dict, list)):
                found.extend(collect_records(value, f"{path}.{key}" if path else key))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            found.extend(collect_records(value, f"{path}[{i}]"))
    return found


def file_role(rel: str):
    name = Path(rel).name.lower()
    if rel in FIRST_CLASS_PATHS:
        return "first-class-owner"
    if rel.startswith("knowledge/indexes/"):
        return "routing-or-ledger"
    if any(token in name for token in CONTROL_PATTERNS):
        return "control-or-routing"
    if "source-ledger" in name or name.endswith("-ledger.json"):
        return "evidence-ledger"
    if "wave-" in name or "addendum" in name or "recovery" in name:
        return "developmental-or-recovery"
    return "substantive-owner-or-dataset"


def score(record, role):
    fields = {k: text_value(record.get(k)).strip() for k in TEXT_FIELDS}
    words = len(re.findall(r"\b\w+[\w'’-]*\b", " ".join(fields.values())))
    present = sum(bool(fields[k]) for k in MAJOR_FIELDS)
    evidence = bool(fields["sources"] or fields["source_records"] or fields["evidence_boundary"] or fields["boundary"])
    questions = bool(fields["research_questions"] or fields["questions"])
    coupling = bool(fields["couplings"] or fields["relationships"])

    if words < 40 or present == 0:
        category = "stub"
    elif words < 100 or present < 2:
        category = "label"
    elif words < 220 or present < 3:
        category = "metadata"
    elif words < 450 or not coupling:
        category = "substantive"
    else:
        category = "deep" if evidence and questions else "substantive"

    priority = {"stub": 5, "label": 4, "metadata": 3, "substantive": 1, "deep": 0}[category]
    if not evidence:
        priority += 2
    if not questions:
        priority += 1
    if not coupling:
        priority += 2
    if role == "first-class-owner" and category != "deep":
        priority += 3
    if role in {"control-or-routing", "routing-or-ledger"}:
        # Small routing files can be healthy. Keep them visible without letting them
        # crowd substantive owners off the priority list.
        priority = max(0, priority - 3)

    missing = sorted(k for k in MAJOR_FIELDS if not fields[k])
    return category, words, priority, missing, evidence, questions, coupling


def iter_json_files(roots, include_countries=False):
    for base in roots:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.json")):
            rel_parts = path.relative_to(base).parts
            if not include_countries and any(part in COUNTRY_DIRS for part in rel_parts):
                continue
            if path.name in GENERATED_NAMES:
                continue
            yield path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write data/depth-audit-live.json")
    parser.add_argument("--top", type=int, default=150)
    parser.add_argument("--include-countries", action="store_true", help="also scan large country datasets")
    parser.add_argument("--root", action="append", dest="roots", help="repository-relative directory to scan; repeatable")
    args = parser.parse_args()

    roots = tuple(ROOT / x for x in args.roots) if args.roots else DEFAULT_ROOTS
    results = []
    files_scanned = 0
    role_counts = Counter()
    file_summaries = defaultdict(lambda: {"records": 0, "categories": Counter(), "max_priority": 0})

    for path in iter_json_files(roots, include_countries=args.include_countries):
        files_scanned += 1
        rel = str(path.relative_to(ROOT))
        role = file_role(rel)
        role_counts[role] += 1
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            results.append({"file": rel, "role": role, "parse_error": str(exc)})
            continue

        records = collect_records(obj)
        if not records and isinstance(obj, dict):
            # Registry/control JSON may intentionally have no nested semantic records.
            results.append({"file": rel, "role": role, "location": "$", "id": obj.get("id") or obj.get("name") or path.stem, "name": obj.get("title") or obj.get("name") or path.stem, "category": "control" if role in {"control-or-routing", "routing-or-ledger"} else "unclassified", "word_count": 0, "priority": 0 if role in {"control-or-routing", "routing-or-ledger"} else 2, "missing_major_fields": []})
            continue

        for location, record in records:
            category, words, priority, missing, evidence, questions, coupling = score(record, role)
            row = {
                "file": rel,
                "role": role,
                "location": location,
                "id": str(record.get("id") or record.get("slug") or record.get("title") or record.get("name")),
                "name": record.get("name") or record.get("title") or record.get("label"),
                "category": category,
                "word_count": words,
                "priority": priority,
                "missing_major_fields": missing,
                "has_evidence_route": evidence,
                "has_questions": questions,
                "has_coupling_or_relationships": coupling,
            }
            results.append(row)
            fs = file_summaries[rel]
            fs["records"] += 1
            fs["categories"][category] += 1
            fs["max_priority"] = max(fs["max_priority"], priority)

    results.sort(key=lambda x: (-x.get("priority", 99), x.get("word_count", 0), x.get("file", ""), x.get("location", "")))
    category_summary = Counter(x["category"] for x in results if "category" in x)
    shallow = [x for x in results if x.get("category") in {"stub", "label", "metadata"}]
    first_class_shallow = [x for x in shallow if x.get("role") == "first-class-owner"]

    per_file = []
    for rel, stats in file_summaries.items():
        per_file.append({"file": rel, "role": file_role(rel), "records": stats["records"], "categories": dict(stats["categories"]), "max_priority": stats["max_priority"]})
    per_file.sort(key=lambda x: (-x["max_priority"], x["file"]))

    report = {
        "version": "2.0.0",
        "purpose": "Live role-aware ranking of structured content depth across data/ and knowledge/.",
        "generated_by": "scripts/audit_content_depth.py",
        "scope": [str(x.relative_to(ROOT)) for x in roots],
        "countries_included": args.include_countries,
        "files_scanned": files_scanned,
        "records_scanned": len([x for x in results if x.get("category") not in {"control", "unclassified"}]),
        "category_summary": dict(category_summary),
        "file_role_summary": dict(role_counts),
        "parse_errors": [x for x in results if "parse_error" in x],
        "first_class_shallow": first_class_shallow,
        "priority_files": per_file[:args.top],
        "top_priority_records": results[:args.top],
        "interpretation": [
            "Priority is not the same as file size. First-class concept owners are penalized for thinness; control/routing files are discounted because brevity can be correct.",
            "A low-depth wave/addendum should usually be promoted into a durable owner and retired once its unique material has been absorbed.",
            "This script audits structured JSON content; HTML/Markdown narrative duplication still requires a separate consolidation review.",
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.write:
        out = ROOT / "data" / "depth-audit-live.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {out}")
    if report["parse_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
