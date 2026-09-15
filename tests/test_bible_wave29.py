from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave29.json"
MANIFEST = ROOT / "knowledge" / "traditions" / "bible-layer-manifest.json"

REQUIRED_IDS = {
    "sabbath-soil-rest-renewal",
    "hidden-life-dormancy-secret-growth",
    "seasons-dormancy-activation",
    "adoption-inheritance-children",
    "jeremiah-cistern-mud-ropes-extraction",
    "psalm40-mire-rock-established-steps",
    "psalm69-deep-mire-no-standing-pit-mouth",
    "psalm18-cords-sheol-flood-high-rescue",
    "hosea-cords-love-yoke-feed",
    "romans11-root-supports-branches",
    "jeremiah17-roots-river-drought-fruit",
    "rooted-grounded-in-love",
    "scarlet-cord-window-house-rescue",
    "creation-measure-foundation",
    "portion-lot-boundary",
    "justice-line-plumb",
    "jerusalem-measure-without-material-wall",
    "temple-city-measurement-trajectory",
    "threefold-cord-resilience",
    "race-weight-entanglement",
    "level-path-healing",
    "straight-path-guidance",
    "broad-place-release",
    "debt-release-open-hand",
    "jubilee-restoration-capacity",
    "forgiveness-debt-reciprocity",
    "ransom-redemption-release",
    "restitution-repair-changed-conduct",
    "blood-cries-better-word",
    "treasure-heaven-stored-value",
    "mammon-spiritual-bank-countertext",
    "cancel-record-debt-identity-release",
    "jubilee-release-rebuilding",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_wave29_is_registered_and_structurally_bounded():
    assert WAVE.exists(), "Wave 29 dossier must exist"
    data = load_json(WAVE)
    rows = data.get("new_relations", [])
    ids = [row.get("id") for row in rows]

    assert len(rows) >= 33
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

    manifest = load_json(MANIFEST)
    layers = manifest.get("layers", [])
    match = [
        layer for layer in layers
        if layer.get("path") == "knowledge/traditions/biblical-syncretism-dossiers-wave29.json"
    ]
    assert len(match) == 1
    assert match[0].get("status") == "additive"
    assert match[0].get("kind") == "relations"
