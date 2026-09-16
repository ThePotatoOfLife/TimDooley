#!/usr/bin/env python3
"""Build deterministic, derived Bible consolidation indexes."""
from __future__ import annotations

import json
from pathlib import Path

try:
    from .bible_consolidation import build_duplicate_queue, build_families, classify_pair, fingerprint_relation
    from .bible_corpus import assemble_relations, assemble_scenes, load_manifest
    from .bible_excavation import build_report
except ImportError:  # direct script execution
    from bible_consolidation import build_duplicate_queue, build_families, classify_pair, fingerprint_relation
    from bible_corpus import assemble_relations, assemble_scenes, load_manifest
    from bible_excavation import build_report

ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "knowledge" / "indexes"
PATHS = {
    "fingerprints": INDEX_DIR / "bible-relation-fingerprints.json",
    "families": INDEX_DIR / "bible-relation-families.json",
    "duplicates": INDEX_DIR / "bible-duplicate-review-queue.json",
}


def _all_pairs(rows: list[dict], fps: dict[str, dict]) -> list[dict]:
    pairs: list[dict] = []
    ordered = sorted(rows, key=lambda row: str(row.get("id", "")))
    for i, left in enumerate(ordered):
        for right in ordered[i + 1:]:
            result = classify_pair(fps[left["id"]], fps[right["id"]])
            if result["classification"] != "unrelated":
                pairs.append(result)
    return sorted(pairs, key=lambda pair: tuple(pair["relation_ids"]))


def build_outputs(root: Path) -> dict[str, dict]:
    manifest = load_manifest(root)
    relations = assemble_relations(root, manifest)
    scenes = assemble_scenes(root, manifest)
    excavation = build_report(relations, scenes, str(manifest.get("version") or ""))
    assessments = {row["relation_id"]: row for row in excavation.get("relations", []) if row.get("relation_id")}
    fingerprints = {
        row["id"]: fingerprint_relation(row, assessments.get(row["id"]))
        for row in relations
        if row.get("id")
    }
    pairs = _all_pairs(relations, fingerprints)
    families = build_families(
        relations,
        assessments,
        fingerprints=fingerprints,
        pair_results=pairs,
    )
    duplicates = build_duplicate_queue(relations, fingerprints, pairs)
    relation_ids = sorted(fingerprints)
    grouped = {rid for family in families for rid in family.get("member_relation_ids", [])}
    contrast_pairs = [pair for pair in pairs if pair["classification"] == "contrast_candidate"]
    overlap_pairs = [pair for pair in pairs if pair["classification"] == "overlap_candidate"]
    duplicate_pairs = [pair for pair in pairs if pair["classification"] == "duplicate_candidate"]
    manifest_version = str(manifest.get("version") or "")
    return {
        "fingerprints": {
            "id": "bible-relation-fingerprints",
            "version": "1.0.0",
            "manifest_version": manifest_version,
            "relation_count": len(relations),
            "relations": [fingerprints[rid] for rid in relation_ids],
        },
        "families": {
            "id": "bible-relation-families",
            "version": "1.0.0",
            "manifest_version": manifest_version,
            "relation_count": len(relations),
            "family_count": len(families),
            "grouped_relation_count": len(grouped),
            "ungrouped_relation_count": len(set(relation_ids) - grouped),
            "contrast_pair_count": len(contrast_pairs),
            "overlap_pair_count": len(overlap_pairs),
            "families": families,
        },
        "duplicates": {
            "id": "bible-duplicate-review-queue",
            "version": "1.0.0",
            "manifest_version": manifest_version,
            "relation_count": len(relations),
            "candidate_count": len(duplicates),
            "pair_count": len(duplicate_pairs),
            "candidates": duplicates,
        },
    }


def summary_lines(outputs: dict[str, dict], family_limit: int = 8) -> list[str]:
    families = sorted(
        outputs["families"]["families"],
        key=lambda family: (
            -len(family.get("member_relation_ids", [])),
            str(family.get("label") or ""),
            str(family.get("id") or ""),
        ),
    )[:family_limit]
    lines: list[str] = []
    for family in families:
        lines.append(
            f"FAMILY {family.get('label')}: "
            f"members={len(family.get('member_relation_ids', []))} "
            f"representative={family.get('representative_relation_id')} "
            f"contrasts={len(family.get('contrast_relation_ids', []))} "
            f"duplicates={len(family.get('duplicate_candidate_relation_ids', []))}"
        )
    for item in outputs["duplicates"]["candidates"]:
        pair = " <> ".join(item.get("relation_ids", []))
        lines.append(
            f"DUPLICATE {pair}: "
            f"representative={item.get('recommended_representative_id')} "
            f"action={item.get('suggested_action')} "
            f"migration={'yes' if item.get('requires_evidence_migration') else 'no'}"
        )
    return lines


def write_outputs(root: Path, outputs: dict[str, dict]) -> None:
    index_dir = root / "knowledge" / "indexes"
    index_dir.mkdir(parents=True, exist_ok=True)
    for key, name in [
        ("fingerprints", "bible-relation-fingerprints.json"),
        ("families", "bible-relation-families.json"),
        ("duplicates", "bible-duplicate-review-queue.json"),
    ]:
        (index_dir / name).write_text(
            json.dumps(outputs[key], indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def main() -> int:
    outputs = build_outputs(ROOT)
    write_outputs(ROOT, outputs)
    print(
        "BIBLE CONSOLIDATION BUILT: "
        f"relations={outputs['fingerprints']['relation_count']} "
        f"families={outputs['families']['family_count']} "
        f"duplicates={outputs['duplicates']['candidate_count']} "
        f"contrasts={outputs['families']['contrast_pair_count']} "
        f"ungrouped={outputs['families']['ungrouped_relation_count']}"
    )
    for line in summary_lines(outputs):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
