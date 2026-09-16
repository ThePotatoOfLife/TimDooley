from __future__ import annotations

from pathlib import Path

from scripts.bible_corpus import assemble_relations, load_manifest
from scripts.build_bible_consolidation import build_outputs

ROOT = Path(__file__).resolve().parents[1]


def test_real_corpus_has_no_relation_loss():
    manifest = load_manifest(ROOT)
    active_ids = {row["id"] for row in assemble_relations(ROOT, manifest)}
    outputs = build_outputs(ROOT)
    indexed_ids = {row["relation_id"] for row in outputs["fingerprints"]["relations"]}
    assert indexed_ids == active_ids


def test_real_corpus_build_is_deterministic():
    assert build_outputs(ROOT) == build_outputs(ROOT)


def test_real_corpus_has_multifunction_mountain_family():
    outputs = build_outputs(ROOT)
    target = {
        "sinai-guarded-ascent-return-instruction",
        "zion-circulation-center",
        "nebo-vision-without-possession",
        "mountain-temptation-possession-countertext",
    }
    matches = [
        family for family in outputs["families"]["families"]
        if len(target & set(family["member_relation_ids"])) >= 3
    ]
    assert matches, "expected current Mountain material to gather into one useful retrieval family"
    family = max(matches, key=lambda row: len(target & set(row["member_relation_ids"])))
    assert len(family["member_functions"]) >= 3
    assert "mountain-temptation-possession-countertext" in family["contrast_relation_ids"]


def test_duplicate_queue_never_aliases_unique_evidence():
    outputs = build_outputs(ROOT)
    for item in outputs["duplicates"]["candidates"]:
        if item["requires_evidence_migration"]:
            assert item["suggested_action"] != "alias"


def test_quality_workflow_builds_and_validates_consolidation_before_reader():
    text = (ROOT / ".github/workflows/quality-checks.yml").read_text(encoding="utf-8")
    build = text.index("python scripts/build_bible_consolidation.py")
    validate = text.index("python scripts/validate_bible_consolidation.py")
    reader = text.index("python scripts/validate_bible_reader.py")
    assert build < validate < reader
