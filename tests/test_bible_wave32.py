from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave32.json"
MANIFEST = ROOT / "knowledge" / "traditions" / "bible-layer-manifest.json"

REQUIRED_IDS = {
    "ephesians2-stranger-household-temple-access",
    "hebrews6-hope-anchor-beyond-veil",
    "psalm118-gate-rejected-stone-life",
    "adam-garden-serve-guard-meta-stewardship",
    "wheat-weeds-delayed-separation-restraint",
    "hiddenness-moral-neutral-seed-leaven-treasure",
    "farm-garden-stewardship-test",
    "son-sower-and-seed-double-role",
    "house-field-interpretation-process",
    "brother-keeper-human-stewardship",
    "ground-blood-versus-seed",
    "creation-circle-order-boundary",
    "self-binding-cords-snare",
    "dog-mud-return-closed-loop",
    "dog-boundary-outsider-reversal",
    "dogs-lazarus-gate-ambiguity",
    "earth-angels-sprout-staircase",
    "potato-angels-service-garden",
    "eye-child-sprout-ladder-chain",
    "eyes-wings-throne-living-creatures",
    "branch-sprout-spirit-house-building",
    "angel-function-messenger-service",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_wave32_promotes_specialist_findings_with_counterpressure():
    assert WAVE.exists()
    payload = load(WAVE)
    rows = payload.get("new_relations", [])
    ids = [row.get("id") for row in rows]
    assert len(rows) >= 22
    assert len(ids) == len(set(ids))
    assert REQUIRED_IDS <= set(ids)

    for row in rows:
        rid = row.get("id", "<missing>")
        assert row.get("project_anchor"), f"{rid}: project_anchor"
        assert row.get("biblical_refs"), f"{rid}: biblical_refs"
        assert row.get("source_direction"), f"{rid}: source_direction"
        assert row.get("boundary"), f"{rid}: boundary"
        assert row.get("source_owners"), f"{rid}: source_owners"
        arg = row.get("relation_argument") or {}
        for key in ("project_sequence", "biblical_sequence", "maximum_claim", "why_it_matters"):
            assert arg.get(key), f"{rid}: relation_argument.{key}"

    manifest = load(MANIFEST)
    layers = [x for x in manifest.get("layers", []) if x.get("path") == "knowledge/traditions/biblical-syncretism-dossiers-wave32.json"]
    assert len(layers) == 1
    assert layers[0].get("kind") == "relations"
    assert layers[0].get("status") == "additive"
