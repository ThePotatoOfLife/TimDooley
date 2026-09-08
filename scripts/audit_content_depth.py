#!/usr/bin/env python3
"""Rank shallow records so the repository can deepen substance before multiplying nodes."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
IGNORE_DIRS = {"countries"}
TEXT_FIELDS = ("definition", "context", "purpose", "description", "summary", "mechanisms", "couplings", "research_questions", "questions", "failure_modes", "evidence_boundary", "sources", "project_extrapolations", "history", "chronology", "function", "use_in_project")
RECORD_KEYS = {"records", "entries", "nodes", "events", "people", "nations", "scale", "levels", "sector_families", "organizations", "relationships", "facts"}
MAJOR_FIELDS = ("definition", "context", "mechanisms", "couplings")


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
    return bool(value.get("id") or value.get("slug")) and any(k in value for k in TEXT_FIELDS)


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


def score(record):
    fields = {k: text_value(record.get(k)).strip() for k in TEXT_FIELDS}
    words = len(re.findall(r"\b\w+[\w'’-]*\b", " ".join(fields.values())))
    present = sum(bool(fields[k]) for k in MAJOR_FIELDS)
    evidence = bool(fields["sources"] or fields["evidence_boundary"])
    questions = bool(fields["research_questions"] or fields["questions"])
    coupling = bool(fields["couplings"])
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
    priority = 0
    if category == "stub": priority += 5
    elif category == "label": priority += 4
    elif category == "metadata": priority += 3
    elif category == "substantive": priority += 1
    if not evidence: priority += 2
    if not questions: priority += 1
    if not coupling: priority += 2
    return category, words, priority, sorted(k for k in MAJOR_FIELDS if not fields[k])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write data/depth-audit-live.json")
    parser.add_argument("--top", type=int, default=100)
    args = parser.parse_args()
    results = []
    for path in sorted(DATA.rglob("*.json")):
        if any(part in IGNORE_DIRS for part in path.relative_to(DATA).parts):
            continue
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            results.append({"file": str(path.relative_to(ROOT)), "parse_error": str(exc)})
            continue
        for location, record in collect_records(obj):
            category, words, priority, missing = score(record)
            results.append({
                "file": str(path.relative_to(ROOT)),
                "location": location,
                "id": str(record.get("id") or record.get("slug")),
                "name": record.get("name") or record.get("title") or record.get("label"),
                "category": category,
                "word_count": words,
                "priority": priority,
                "missing_major_fields": missing,
            })
    results.sort(key=lambda x: (-x.get("priority", 99), x.get("word_count", 0), x.get("file", "")))
    summary = {}
    for row in results:
        if "category" in row:
            summary[row["category"]] = summary.get(row["category"], 0) + 1
    report = {
        "version": "1.0.0",
        "purpose": "Live machine-generated ranking of record depth and missing substance.",
        "generated_by": "scripts/audit_content_depth.py",
        "summary": summary,
        "records_scanned": len([x for x in results if "category" in x]),
        "parse_errors": [x for x in results if "parse_error" in x],
        "top_priority": results[:args.top],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.write:
        (DATA / "depth-audit-live.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {DATA / 'depth-audit-live.json'}")
    if report["parse_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
