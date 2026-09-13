#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(rel: str, errors: list[str]) -> str:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing required culture-reader file: {rel}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(rel: str, errors: list[str]) -> dict:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing required culture-reader JSON: {rel}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"culture-reader JSON must be an object: {rel}")
        return {}
    return value


def require(text: str, marker: str, owner: str, errors: list[str]) -> None:
    if marker not in text:
        errors.append(f"{owner} missing culture-reader marker: {marker}")


def main() -> int:
    errors: list[str] = []

    page = read_text("context/culture/index.html", errors)
    context = read_text("context/index.html", errors)
    farm = read_text("shadow-farm/index.html", errors)
    atlas = read_json("knowledge/culture/culture-formation-zeitgeist-atlas.json", errors)
    ledger = read_json("knowledge/culture/culture-theory-source-ledger.json", errors)
    ontology = read_json("data/culture-ontology.json", errors)
    subculture = read_json("data/subculture-research-map.json", errors)
    surfaces = read_json("data/house/public-surfaces.json", errors)

    for marker in (
        'data-reader-surface="culture"',
        'Culture is the evolving ecology of shared meaning and repeated social life',
        'What is a zeitgeist?',
        'Popular, mass, high, elite and canonical culture',
        'Cult and high-control systems',
        'Reputation, smear and narrative capture',
        'American internet subculture',
        'Garden / repair',
        'href="../../shadow-farm/"',
    ):
        require(page, marker, "context/culture/index.html", errors)

    require(context, 'href="culture/"', "context/index.html", errors)
    require(context, 'Culture &amp; Subculture', "context/index.html", errors)
    require(farm, 'href="../context/culture/"', "shadow-farm/index.html", errors)

    if atlas.get("id") != "culture-formation-zeitgeist-atlas":
        errors.append("culture atlas id must be culture-formation-zeitgeist-atlas")
    for key in ("formation_states", "cultural_dimensions", "concepts", "transformation_models", "project_mapping"):
        if not atlas.get(key):
            errors.append(f"culture atlas missing {key}")
    concepts = atlas.get("concepts", {})
    for key in ("zeitgeist", "peak-culture", "ideal-culture", "high-culture", "popular-culture", "cultural-repair"):
        if key not in concepts:
            errors.append(f"culture atlas concepts missing {key}")
    if not ledger.get("sources"):
        errors.append("culture theory source ledger must contain sources")

    for key in ("formation_states", "culture_scales", "cultural_dimensions", "distinction_rules", "zeitgeist_model", "reputation_pipeline"):
        if not ontology.get(key):
            errors.append(f"culture ontology missing {key}")

    nodes = {row.get("id") for row in subculture.get("nodes", []) if isinstance(row, dict)}
    for node_id in ("microculture", "scene", "counterpublic", "anti-fandom", "internet-bloodsports", "narrative-lock-in", "reputation-narrative-capture", "cultural-correction"):
        if node_id not in nodes:
            errors.append(f"subculture map missing node {node_id}")

    if surfaces.get("primary_gateway_ids") != ["tim", "religion", "philosophy", "science", "world"]:
        errors.append("Culture must not change the five primary gateway ids")
    by_id = {row.get("id"): row for row in surfaces.get("surfaces", []) if isinstance(row, dict)}
    culture = by_id.get("culture")
    if not culture:
        errors.append("public surfaces missing specialist culture route")
    else:
        if culture.get("canonical_route") != "/context/culture/":
            errors.append("culture canonical route must be /context/culture/")
        if culture.get("visibility") != "specialist" or culture.get("primary_navigation") is not False:
            errors.append("culture route must remain specialist and non-primary")
        if "culture-information" not in culture.get("primary_room_ids", []):
            errors.append("culture route must belong to culture-information Room")

    if errors:
        print("CULTURE READER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("CULTURE READER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
