from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave30.json"
MANIFEST = ROOT / "knowledge" / "traditions" / "bible-layer-manifest.json"

REQUIRED_IDS = {
    "exodus25-two-cherubim-central-presence",
    "psalm80-compressed-potatoverse-neighbor",
    "luke15-restorative-return-versus-vomit-return",
    "isaiah55-return-rain-seed-bread",
    "isaiah58-repairer-breach-watered-garden",
    "ezekiel34-shepherd-versus-extractive-ruler",
    "psalm23-shepherd-valley-table-house",
    "john21-love-becomes-feeding",
    "romans8-creation-groaning-liberation",
    "revelation3-door-knock-meal",
    "revelation22-open-water-invitation",
    "daniel7-ancient-of-days-son-of-man-role-distribution",
    "philippians2-descent-service-death-exaltation",
    "noah-ark-versus-covenant-ark-distinction",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_wave30_promotes_legacy_research_without_role_collapse():
    assert WAVE.exists(), "Wave 30 dossier must exist"
    data = load_json(WAVE)
    rows = data.get("new_relations", [])
    ids = [row.get("id") for row in rows]
    assert len(rows) >= 14
    assert len(ids) == len(set(ids))
    assert REQUIRED_IDS <= set(ids)

    for row in rows:
        rid = row.get("id", "<missing-id>")
        assert row.get("project_anchor"), f"{rid}: missing project_anchor"
        assert row.get("biblical_refs"), f"{rid}: missing biblical_refs"
        assert row.get("source_direction"), f"{rid}: missing source_direction"
        assert row.get("boundary"), f"{rid}: missing boundary"
        assert row.get("source_owners"), f"{rid}: missing source_owners"
        arg = row.get("relation_argument") or {}
        assert arg.get("project_sequence"), f"{rid}: missing project_sequence"
        assert arg.get("biblical_sequence"), f"{rid}: missing biblical_sequence"
        assert arg.get("maximum_claim"), f"{rid}: missing maximum_claim"
        assert arg.get("why_it_matters"), f"{rid}: missing why_it_matters"

    manifest = load_json(MANIFEST)
    layers = [x for x in manifest.get("layers", []) if x.get("path") == "knowledge/traditions/biblical-syncretism-dossiers-wave30.json"]
    assert len(layers) == 1
    assert layers[0].get("kind") == "relations"
    assert layers[0].get("status") == "additive"
