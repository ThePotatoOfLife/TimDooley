#!/usr/bin/env python3
"""Validate the canonical Biblical Syncretism Field.

This checker protects the registry from becoming another untyped overlap dump.
It validates unique IDs, relation/discovery vocabularies, required provenance fields,
owner paths, chronological source-direction metadata, and the richer dossier contract
used for high-value contextual comparisons.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = ROOT / "knowledge/traditions/biblical-syncretism-field.json"
FRAGMENTS = ROOT / "knowledge/traditions/biblical-passage-fragments.json"

REQUIRED = {"id", "actor", "project_anchor", "discovery_mode", "relation_class", "biblical_refs", "motifs", "strength", "owners"}
SCENE_STATUSES = {"exact", "recovered", "adjacent-context", "date-only", "unknown"}
RICH_SCENE_KEYS = {"setting", "activity", "conversation_trigger", "participants", "surrounding_topics", "lead_up", "before", "after"}


def nonempty(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def main() -> int:
    errors: list[str] = []
    data = json.loads(FIELD.read_text(encoding="utf-8"))
    fragment_data = json.loads(FRAGMENTS.read_text(encoding="utf-8"))
    fragments = fragment_data.get("fragments", [])
    fragment_ids = [item.get("id") for item in fragments]
    if len(fragment_ids) != len(set(fragment_ids)):
        errors.append("biblical passage fragment IDs must be unique")
    if fragment_data.get("translation") != "World English Bible (WEB)":
        errors.append("passage fragments must identify the World English Bible (WEB) translation")

    dossier_contract = data.get("dossier_contract")
    if not isinstance(dossier_contract, dict):
        errors.append("biblical field missing dossier_contract")
    else:
        statuses = set(dossier_contract.get("scene_source_statuses", []))
        if not SCENE_STATUSES.issubset(statuses):
            errors.append("dossier_contract must declare exact/recovered/adjacent-context/date-only/unknown scene statuses")

    rows = data.get("relations")
    if not isinstance(rows, list) or not rows:
        errors.append("relations must be a non-empty list")
        rows = []

    allowed_modes = {x["id"] for x in data.get("discovery_modes", [])}
    allowed_classes = {x["id"] for x in data.get("relation_classes", [])}
    seen: set[str] = set()

    for i, row in enumerate(rows):
        where = f"relations[{i}]"
        missing = sorted(REQUIRED - set(row))
        if missing:
            errors.append(f"{where}: missing {', '.join(missing)}")
        rid = row.get("id")
        if rid in seen:
            errors.append(f"{where}: duplicate id {rid}")
        if rid:
            seen.add(rid)
        if row.get("discovery_mode") not in allowed_modes:
            errors.append(f"{where}: unknown discovery_mode {row.get('discovery_mode')!r}")
        if row.get("relation_class") not in allowed_classes:
            errors.append(f"{where}: unknown relation_class {row.get('relation_class')!r}")
        strength = row.get("strength")
        if not isinstance(strength, int) or not 1 <= strength <= 5:
            errors.append(f"{where}: strength must be integer 1..5")
        if not row.get("biblical_refs"):
            errors.append(f"{where}: biblical_refs cannot be empty")
        elif not any(
            match in row["biblical_refs"]
            for fragment in fragments
            for match in fragment.get("matches", [fragment.get("reference")])
        ):
            errors.append(f"{where}: no side-by-side scripture fragment covers this relation")
        if not row.get("owners"):
            errors.append(f"{where}: owners cannot be empty")
        for owner in row.get("owners", []):
            # Library/book names can be provenance pointers rather than repo paths.
            if "/" in owner and not (ROOT / owner).exists():
                errors.append(f"{where}: missing repo owner path {owner}")
        if row.get("relation_class") in {"later-structural-parallel", "research-unlock"} and not row.get("date"):
            errors.append(f"{where}: later/research relation requires a date")

        scene = row.get("scene_context")
        if scene is not None:
            if not isinstance(scene, dict):
                errors.append(f"{where}: scene_context must be an object")
            else:
                status = scene.get("source_status")
                if status not in SCENE_STATUSES:
                    errors.append(f"{where}: invalid scene_context.source_status {status!r}")
                if status in {"date-only", "unknown"}:
                    unsupported = sorted(key for key in RICH_SCENE_KEYS if nonempty(scene.get(key)))
                    if unsupported:
                        errors.append(f"{where}: {status} scene cannot assert rich context fields: {', '.join(unsupported)}")

        if row.get("dossier_level") == "A":
            if not row.get("title"):
                errors.append(f"{where}: Level-A dossier requires title")
            if not isinstance(scene, dict) or scene.get("source_status") not in SCENE_STATUSES:
                errors.append(f"{where}: Level-A dossier requires typed scene_context")
            if not row.get("wording_status"):
                errors.append(f"{where}: Level-A dossier requires wording_status")
            if not row.get("mechanisms"):
                errors.append(f"{where}: Level-A dossier requires mechanisms")
            argument = row.get("relation_argument")
            if not isinstance(argument, dict):
                errors.append(f"{where}: Level-A dossier requires relation_argument object")
            else:
                for key in ("project_sequence", "biblical_sequence", "why_dense", "maximum_claim"):
                    if not nonempty(argument.get(key)):
                        errors.append(f"{where}: Level-A relation_argument requires {key}")
            discovery = row.get("discovery_history")
            if not isinstance(discovery, dict) or not nonempty(discovery.get("source_direction")):
                errors.append(f"{where}: Level-A dossier requires discovery_history.source_direction")
            if strength in {4, 5} and not any(nonempty(row.get(key)) for key in ("mismatch", "counter_text", "weaknesses", "boundary", "source_correction")):
                errors.append(f"{where}: strength-{strength} Level-A dossier requires mismatch/counter-fit boundary")

    if errors:
        print("Biblical Syncretism Field: FAIL")
        for e in errors:
            print(" -", e)
        return 1

    full_dossiers = sum(row.get("dossier_level") == "A" for row in rows)
    print(f"Biblical Syncretism Field: OK — {len(rows)} relations, {len(seen)} unique IDs, {len(fragments)} passage fragments, {full_dossiers} Level-A dossiers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
