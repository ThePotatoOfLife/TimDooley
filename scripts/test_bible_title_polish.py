#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave37.json"

EXPECTED = {
    "ephesians2-stranger-household-temple-access": "From Stranger to Household",
    "babel-name-centralization-versus-ladder-circulation": "Babel and the Ladder",
    "teaching-yoke-vs-slavery-yoke": "Teaching Yoke vs. Slavery Yoke",
    "mountain-height-no-fixed-valence": "Height Has No Fixed Meaning",
}
NEW_RELATION_TITLES = {
    "emmaus-return-before-recognition-bread": "Emmaus: Return Before Recognition",
    "mary-gardener-misrecognition-return": "Mary Mistakes Jesus for the Gardener",
    "acts-forty-days-resurrection-to-ascension": "Resurrection to Ascension",
    "john21-shore-recognition-feeding-after-return": "Shore Recognition and Feeding",
}


def main() -> int:
    data = json.loads(WAVE.read_text(encoding="utf-8"))
    enrichments = {row["relation_id"]: row for row in data.get("enrichments", []) if row.get("relation_id")}
    relations = {row["id"]: row for row in data.get("new_relations", []) if row.get("id")}
    errors: list[str] = []

    for relation_id, title in EXPECTED.items():
        actual = enrichments.get(relation_id, {}).get("title")
        if actual != title:
            errors.append(f"{relation_id}: expected title {title!r}, got {actual!r}")

    for relation_id, title in NEW_RELATION_TITLES.items():
        actual = relations.get(relation_id, {}).get("title")
        if actual != title:
            errors.append(f"{relation_id}: expected title {title!r}, got {actual!r}")

    title_enrichments = [row for row in data.get("enrichments", []) if row.get("title")]
    if len(title_enrichments) < 70:
        errors.append(f"expected broad title cleanup, found only {len(title_enrichments)} title enrichments")

    method_text = " ".join(data.get("method_rules", []))
    if "Ego Death" not in method_text:
        errors.append("reader-facing 2011 terminology rule must name Ego Death")

    if errors:
        print("BIBLE TITLE POLISH TEST FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print(f"BIBLE TITLE POLISH TEST PASSED ({len(title_enrichments)} title enrichments)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
