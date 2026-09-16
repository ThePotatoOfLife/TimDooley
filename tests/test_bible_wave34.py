from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave34.json"
MANIFEST = ROOT / "knowledge" / "traditions" / "bible-layer-manifest.json"

REQUIRED_IDS = {
    "valley-mountain-leveling-traversability",
    "road-obstacle-removal-access",
    "holy-highway-protected-return",
    "micah-breach-distributed-threshold",
    "door-as-barrier-release",
    "heavenly-pattern-embodied-sanctuary",
    "earthly-copy-heavenly-sanctuary",
    "ezekiel-mountain-city-river",
    "ezekiel-revelation-city-continuity",
    "holy-of-holies-to-city-presence",
    "tribal-gates-community-architecture",
    "forehead-inscription-identity-seal",
    "open-gates-boundary-circulation",
    "cord-taxonomy-multivalence",
    "teaching-yoke-vs-slavery-yoke",
    "race-course-burden-orientation",
    "plan-and-directed-steps",
    "branch-choice-life-death",
    "path-light-guidance-not-fate",
    "predestination-not-mechanics",
    "moses-distributed-speaking",
    "jeremiah-objection-supplied-word",
    "ordinary-witness-prestige-reversal",
    "weak-lowly-status-reversal",
    "women-tomb-witness-chain",
    "tomb-gardener-recognition-father",
    "gate-widow-dead-son-return",
    "mourning-absence-return-jeremiah",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_wave34_promotes_distinct_functional_relations_with_boundaries():
    assert WAVE.exists(), "Wave 34 dossier must exist"
    data = load_json(WAVE)
    rows = data.get("new_relations", [])
    ids = [row.get("id") for row in rows]

    assert len(rows) >= 28
    assert len(ids) == len(set(ids))
    assert REQUIRED_IDS <= set(ids)

    for row in rows:
        rid = row.get("id", "<missing-id>")
        assert row.get("project_anchor"), f"{rid}: missing project_anchor"
        assert row.get("biblical_refs"), f"{rid}: missing biblical_refs"
        assert row.get("source_direction"), f"{rid}: missing source_direction"
        assert row.get("boundary"), f"{rid}: missing boundary"
        assert row.get("source_owners"), f"{rid}: missing source_owners"
        argument = row.get("relation_argument") or {}
        assert argument.get("project_sequence"), f"{rid}: missing project_sequence"
        assert argument.get("biblical_sequence"), f"{rid}: missing biblical_sequence"
        assert argument.get("maximum_claim"), f"{rid}: missing maximum_claim"
        assert argument.get("why_it_matters"), f"{rid}: missing why_it_matters"


def test_wave34_is_additive_and_registered_after_existing_excavation_layer():
    manifest = load_json(MANIFEST)
    layers = manifest.get("layers", [])
    matches = [layer for layer in layers if layer.get("id") == "relations-wave34"]
    assert len(matches) == 1
    layer = matches[0]
    assert layer.get("path") == "knowledge/traditions/biblical-syncretism-dossiers-wave34.json"
    assert layer.get("status") == "additive"
    assert layer.get("kind") == "relations"
    assert layer.get("precedence", 0) > 230
