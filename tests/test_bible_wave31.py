from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave31.json"
MANIFEST = ROOT / "knowledge" / "traditions" / "bible-layer-manifest.json"

REQUIRED_IDS = {
    "creed-creator-visible-invisible",
    "creed-descent-burial-rising-ascension-return",
    "creed-harvest-kingdom-without-end",
    "creed-communion-feast-life-to-come",
    "glass-darkly-perception-explicit-quotation",
    "kingdom-within-among-explicit-quotation",
    "burdens-cross-release-transformation",
    "moon-cube-chains-entanglement-liberation",
    "mirror-self-examination-versus-projection",
    "shadow-light-exposure-transformation",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_wave31_records_explicit_intertext_and_boundaries():
    assert WAVE.exists()
    payload = load(WAVE)
    rows = payload.get("new_relations", [])
    ids = [row.get("id") for row in rows]
    assert len(rows) >= 10
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

    direct = {row["id"] for row in rows if row.get("evidence_class") == "explicit-intertext"}
    assert "glass-darkly-perception-explicit-quotation" in direct
    assert "kingdom-within-among-explicit-quotation" in direct
    assert "creed-creator-visible-invisible" in direct

    manifest = load(MANIFEST)
    layers = [x for x in manifest.get("layers", []) if x.get("path") == "knowledge/traditions/biblical-syncretism-dossiers-wave31.json"]
    assert len(layers) == 1
    assert layers[0].get("kind") == "relations"
    assert layers[0].get("status") == "additive"
