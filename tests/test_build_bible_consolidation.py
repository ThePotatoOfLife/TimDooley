from __future__ import annotations

from pathlib import Path

from scripts.bible_corpus import assemble_relations, load_manifest
from scripts.build_bible_consolidation import build_outputs

ROOT = Path(__file__).resolve().parents[1]


def test_build_outputs_cover_every_active_relation():
    manifest = load_manifest(ROOT)
    active = assemble_relations(ROOT, manifest)
    outputs = build_outputs(ROOT)
    active_ids = {row["id"] for row in active}
    fingerprint_ids = {row["relation_id"] for row in outputs["fingerprints"]["relations"]}
    assert fingerprint_ids == active_ids
    assert outputs["fingerprints"]["relation_count"] == len(active_ids)
    assert outputs["families"]["manifest_version"] == manifest["version"]
    assert outputs["duplicates"]["manifest_version"] == manifest["version"]


def test_build_outputs_are_deterministically_sorted():
    outputs = build_outputs(ROOT)
    fingerprints = outputs["fingerprints"]["relations"]
    families = outputs["families"]["families"]
    duplicates = outputs["duplicates"]["candidates"]
    assert [row["relation_id"] for row in fingerprints] == sorted(row["relation_id"] for row in fingerprints)
    assert [row["id"] for row in families] == sorted(row["id"] for row in families)
    assert [tuple(row["relation_ids"]) for row in duplicates] == sorted(tuple(row["relation_ids"]) for row in duplicates)
