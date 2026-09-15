from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave35.json"
MANIFEST = ROOT / "knowledge" / "traditions" / "bible-layer-manifest.json"

REQUIRED_IDS = {
    "sinai-guarded-ascent-return-instruction",
    "sinai-zion-access-regime",
    "zion-circulation-center",
    "moriah-testing-provision-temple",
    "carmel-public-test-outcome",
    "transfiguration-height-return",
    "olives-mountain-multivalence",
    "nebo-vision-without-possession",
    "mountain-house-instruction-cultivation",
    "mountain-temptation-possession-countertext",
    "eden-holy-mountain-garden-expulsion",
    "valley-through-not-identity",
    "dry-bones-valley-regeneration",
    "rod-staff-function-divergence",
    "mountain-height-no-fixed-valence",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_wave35_has_function_typed_mountains_and_valleys():
    assert WAVE.exists()
    rows = load(WAVE).get("new_relations", [])
    ids = [row.get("id") for row in rows]
    assert len(rows) >= 15
    assert len(ids) == len(set(ids))
    assert REQUIRED_IDS <= set(ids)
    for row in rows:
        rid = row.get("id", "<missing>")
        for key in ("project_anchor", "biblical_refs", "source_direction", "boundary", "source_owners"):
            assert row.get(key), f"{rid}: missing {key}"
        arg = row.get("relation_argument") or {}
        for key in ("project_sequence", "biblical_sequence", "maximum_claim", "why_it_matters"):
            assert arg.get(key), f"{rid}: missing relation_argument.{key}"


def test_wave35_is_registered_after_wave34():
    layers = load(MANIFEST).get("layers", [])
    matches = [x for x in layers if x.get("id") == "relations-wave35"]
    assert len(matches) == 1
    layer = matches[0]
    assert layer.get("status") == "additive"
    assert layer.get("kind") == "relations"
    assert layer.get("precedence", 0) > 231
