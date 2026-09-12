#!/usr/bin/env python3
"""Validate the canonical Biblical Syncretism Field plus dossier enrichment.

The base field remains the canonical identity registry. The dossier extension is merged
by relation id for contextual enrichment and may carry additive early-history relations
until later mechanical compaction into the base field.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = ROOT / "knowledge/traditions/biblical-syncretism-field.json"
DOSSIERS = ROOT / "knowledge/traditions/biblical-syncretism-dossiers.json"
FRAGMENTS = ROOT / "knowledge/traditions/biblical-passage-fragments.json"
DOSSIER_FRAGMENTS = ROOT / "knowledge/traditions/biblical-passage-fragments-dossiers.json"

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


def merge_rows(base_rows: list[dict], dossier_data: dict, errors: list[str]) -> list[dict]:
    merged = [copy.deepcopy(row) for row in base_rows]
    by_id = {row.get("id"): row for row in merged if row.get("id")}

    for i, enrichment in enumerate(dossier_data.get("enrichments", [])):
        relation_id = enrichment.get("relation_id")
        if relation_id not in by_id:
            errors.append(f"enrichments[{i}]: unknown relation_id {relation_id!r}")
            continue
        target = by_id[relation_id]
        for key, value in enrichment.items():
            if key != "relation_id":
                target[key] = copy.deepcopy(value)

    for i, row in enumerate(dossier_data.get("new_relations", [])):
        rid = row.get("id")
        if rid in by_id:
            errors.append(f"new_relations[{i}]: duplicate base relation id {rid!r}")
            continue
        item = copy.deepcopy(row)
        merged.append(item)
        if rid:
            by_id[rid] = item
    return merged


def main() -> int:
    errors: list[str] = []
    for path in (FIELD, DOSSIERS, FRAGMENTS, DOSSIER_FRAGMENTS):
        if not path.exists():
            errors.append(f"missing Bible relation component: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(" -", e)
        return 1

    data = json.loads(FIELD.read_text(encoding="utf-8"))
    dossier_data = json.loads(DOSSIERS.read_text(encoding="utf-8"))
    fragment_data = json.loads(FRAGMENTS.read_text(encoding="utf-8"))
    dossier_fragment_data = json.loads(DOSSIER_FRAGMENTS.read_text(encoding="utf-8"))

    if dossier_data.get("canonical_owner") != "knowledge/traditions/biblical-syncretism-field.json":
        errors.append("dossier extension must point back to canonical biblical-syncretism-field.json")
    dossier_contract = dossier_data.get("dossier_contract")
    if not isinstance(dossier_contract, dict):
        errors.append("dossier extension missing dossier_contract")
    else:
        statuses = set(dossier_contract.get("scene_source_statuses", []))
        if not SCENE_STATUSES.issubset(statuses):
            errors.append("dossier_contract must declare exact/recovered/adjacent-context/date-only/unknown scene statuses")

    fragments = list(fragment_data.get("fragments", [])) + list(dossier_fragment_data.get("fragments", []))
    fragment_ids = [item.get("id") for item in fragments]
    if len(fragment_ids) != len(set(fragment_ids)):
        errors.append("biblical passage fragment IDs must be unique across base and dossier fragments")
    for owner_name, owner in (("base", fragment_data), ("dossier", dossier_fragment_data)):
        if owner.get("translation") != "World English Bible (WEB)":
            errors.append(f"{owner_name} passage fragments must identify the World English Bible (WEB) translation")

    base_rows = data.get("relations")
    if not isinstance(base_rows, list) or not base_rows:
        errors.append("relations must be a non-empty list")
        base_rows = []
    rows = merge_rows(base_rows, dossier_data, errors)

    allowed_modes = {x["id"] for x in data.get("discovery_modes", [])}
    allowed_classes = {x["id"] for x in data.get("relation_classes", [])}
    seen: set[str] = set()

    for i, row in enumerate(rows):
        where = f"merged_relations[{i}]"
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
    print(
        f"Biblical Syncretism Field: OK — {len(rows)} merged relations, {len(seen)} unique IDs, "
        f"{len(fragments)} passage fragments, {full_dossiers} Level-A dossiers"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
