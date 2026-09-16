from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
WAVE = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave33.json"
MANIFEST = ROOT / "knowledge" / "traditions" / "bible-layer-manifest.json"
REQUIRED_IDS = {
    "ezekiel-wheel-oriented-mobility",
    "temple-wheel-water-spokes-hubs",
    "windmill-flow-wheel-work-composite",
    "millstone-little-ones-accountability",
    "babylon-millstone-downward-vector",
    "daniel-stone-mountain-expansion-vector",
    "babel-name-centralization-versus-ladder-circulation",
    "jacob-place-connected-not-escape",
    "grain-three-paths-burial-grinding-bread",
    "lion-fourfold-throne-boundary",
    "height-versus-access-independent-variables",
}
def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def test_wave33_motion_architecture_promotions_are_bounded():
    assert WAVE.exists()
    rows = load(WAVE).get("new_relations", [])
    ids = [r.get("id") for r in rows]
    assert len(rows) >= 11
    assert len(ids) == len(set(ids))
    assert REQUIRED_IDS <= set(ids)
    for r in rows:
        rid=r.get("id","<missing>")
        for key in ("project_anchor","biblical_refs","source_direction","boundary","source_owners"):
            assert r.get(key), f"{rid}: {key}"
        arg=r.get("relation_argument") or {}
        for key in ("project_sequence","biblical_sequence","maximum_claim","why_it_matters"):
            assert arg.get(key), f"{rid}: relation_argument.{key}"
    layers=[x for x in load(MANIFEST).get("layers",[]) if x.get("path")=="knowledge/traditions/biblical-syncretism-dossiers-wave33.json"]
    assert len(layers)==1 and layers[0].get("kind")=="relations" and layers[0].get("status")=="additive"
