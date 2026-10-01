#!/usr/bin/env python3
"""Audit Tim/Son-side quality across the assembled active Bible relation corpus."""
from __future__ import annotations

import json
from pathlib import Path

from bible_corpus import assemble_relations, load_manifest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "knowledge" / "research" / "bible-tim-side-quality-audit.json"


def arr(value):
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def has_source_wording(row):
    return any(
        [
            *arr(row.get("project_quote")),
            *arr(row.get("exact_wording")),
            *arr(row.get("public_wording")),
            *arr(row.get("recovered_wording")),
            row.get("quote"),
            *arr(row.get("occurrence_ids")),
        ]
    )


def project_sequence(row):
    arg = row.get("relation_argument") or {}
    if not isinstance(arg, dict):
        return []
    return [str(x).strip() for x in arr(arg.get("project_sequence")) if str(x).strip()]


def later_meaning(row):
    arg = row.get("relation_argument") or {}
    if not isinstance(arg, dict):
        arg = {}
    return (
        row.get("project_development")
        or arg.get("why_it_matters")
        or arg.get("why_dense")
        or ""
    )


def context_text(row):
    return str(row.get("project_context") or row.get("project_anchor") or "").strip()


def classify(row):
    wording = has_source_wording(row)
    context = context_text(row)
    sequence = project_sequence(row)
    development = str(later_meaning(row)).strip()

    issues = []
    if not wording:
        issues.append("no-source-near-wording")
    if len(context) < 120:
        issues.append("thin-project-context")
    if not sequence:
        issues.append("no-project-sequence")
    if len(development) < 100:
        issues.append("thin-later-meaning")
    if context.lower().startswith(("the project ", "the mature project ", "canonical project ")):
        issues.append("analyst-first-anchor")

    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "date": row.get("date"),
        "dossier_level": row.get("dossier_level"),
        "strength": row.get("strength"),
        "has_source_wording": wording,
        "context_chars": len(context),
        "project_sequence_steps": len(sequence),
        "later_meaning_chars": len(development),
        "issues": issues,
        "priority": (
            3 if row.get("dossier_level") == "A" or row.get("strength") == 5 else
            2 if row.get("dossier_level") == "B" or row.get("strength") == 4 else
            1
        ),
    }


def main():
    manifest = load_manifest(ROOT)
    rows = assemble_relations(ROOT, manifest)
    audited = [classify(row) for row in rows]
    needs_work = [x for x in audited if x["issues"]]
    needs_work.sort(key=lambda x: (-x["priority"], -len(x["issues"]), str(x["date"] or ""), str(x["id"] or "")))

    report = {
        "id": "bible-tim-side-quality-audit",
        "updated": "2026-10-01",
        "purpose": "Drive source-first improvement of the Tim/Son side of the public Bible comparator.",
        "rules": {
            "source_wording": "Prefer exact/public/recovered Tim-side wording or linked public occurrence IDs when available.",
            "context": "Explain what happened and what the project was saying; do not rely on taxonomy labels alone.",
            "sequence": "Use structured project_sequence where the relation depends on movement or transformation.",
            "development": "Separate later theological meaning from the earlier event/wording.",
            "analyst_first": "Anchors beginning with generic 'The project...' language are candidates for source-near rewriting."
        },
        "counts": {
            "active_relations": len(audited),
            "with_source_near_wording": sum(1 for x in audited if x["has_source_wording"]),
            "without_source_near_wording": sum(1 for x in audited if not x["has_source_wording"]),
            "needing_any_work": len(needs_work),
            "priority_high": sum(1 for x in needs_work if x["priority"] == 3),
        },
        "priority_queue": needs_work,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
