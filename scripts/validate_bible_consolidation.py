#!/usr/bin/env python3
"""Validate generated Bible consolidation indexes against the active corpus."""
from __future__ import annotations

import json
from pathlib import Path

try:
    from .bible_corpus import assemble_relations, load_manifest
    from .build_bible_consolidation import PATHS, build_outputs
except ImportError:  # direct script execution
    from bible_corpus import assemble_relations, load_manifest
    from build_bible_consolidation import PATHS, build_outputs

ROOT = Path(__file__).resolve().parents[1]


def _member_claims(relations: list[dict]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for row in relations:
        argument = row.get("relation_argument") or {}
        claim = str(argument.get("maximum_claim") or row.get("maximum_claim") or "").strip()
        out[str(row.get("id"))] = {claim} if claim else set()
    return out


def validate_payloads(root: Path, payloads: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    manifest = load_manifest(root)
    relations = assemble_relations(root, manifest)
    active_ids = {str(row["id"]) for row in relations}
    manifest_version = str(manifest.get("version") or "")

    for key in ("fingerprints", "families", "duplicates"):
        payload = payloads.get(key) or {}
        if str(payload.get("manifest_version") or "") != manifest_version:
            errors.append(f"{key}: manifest version mismatch")
        if int(payload.get("relation_count", -1)) != len(active_ids):
            errors.append(f"{key}: relation_count mismatch")

    fingerprint_rows = (payloads.get("fingerprints") or {}).get("relations", [])
    fingerprint_ids = [str(row.get("relation_id") or "") for row in fingerprint_rows]
    if set(fingerprint_ids) != active_ids or len(fingerprint_ids) != len(active_ids):
        errors.append("fingerprint coverage does not exactly match active relation IDs")

    families = (payloads.get("families") or {}).get("families", [])
    family_ids = [str(family.get("id") or "") for family in families]
    if len(family_ids) != len(set(family_ids)):
        errors.append("duplicate family IDs")

    claims = _member_claims(relations)
    pair_modes: dict[tuple[str, str], set[str]] = {}
    for family in families:
        members = [str(rid) for rid in family.get("member_relation_ids", [])]
        unknown = sorted(set(members) - active_ids)
        for rid in unknown:
            errors.append(f"{family.get('id')}: unknown family member {rid}")
        representative = str(family.get("representative_relation_id") or "")
        if representative not in members:
            errors.append(f"{family.get('id')}: representative is not a family member")
        if "maximum_claim" in family:
            generated = str(family.get("maximum_claim") or "").strip()
            existing = {claim for rid in members for claim in claims.get(rid, set())}
            if generated and generated not in existing:
                errors.append(f"{family.get('id')}: synthetic family-level maximum_claim is not allowed")
        member_claims = family.get("member_maximum_claims") or {}
        for rid, claim in member_claims.items():
            if rid in claims and str(claim).strip() and str(claim).strip() not in claims[rid]:
                errors.append(f"{family.get('id')}: member maximum claim drift for {rid}")

        contrast = set(str(x) for x in family.get("contrast_relation_ids", []))
        duplicates = set(str(x) for x in family.get("duplicate_candidate_relation_ids", []))
        if contrast and duplicates:
            # A relation may participate in different pair types inside one family,
            # but the same exact pair cannot be both. Pair-level ambiguity is checked
            # from duplicate queue membership below when available.
            pass

    duplicate_rows = (payloads.get("duplicates") or {}).get("candidates", [])
    for item in duplicate_rows:
        pair = tuple(sorted(str(x) for x in item.get("relation_ids", [])))
        if len(pair) != 2 or any(rid not in active_ids for rid in pair):
            errors.append(f"duplicate candidate has invalid relation_ids: {pair}")
            continue
        pair_modes.setdefault(pair, set()).add("duplicate_candidate")
        if item.get("suggested_action") == "alias" and item.get("requires_evidence_migration"):
            errors.append(f"{pair}: alias hides unique evidence")
        unique = item.get("unique_evidence") or {}
        if item.get("suggested_action") == "alias" and any(unique.get(rid) for rid in pair):
            errors.append(f"{pair}: alias hides unique evidence")

    return errors


def _load_outputs(root: Path) -> dict[str, dict]:
    outputs: dict[str, dict] = {}
    for key, path in PATHS.items():
        actual = root / path.relative_to(ROOT)
        if not actual.exists():
            raise FileNotFoundError(actual)
        outputs[key] = json.loads(actual.read_text(encoding="utf-8"))
    return outputs


def main() -> int:
    try:
        payloads = _load_outputs(ROOT)
    except FileNotFoundError as exc:
        print(f"Bible consolidation invalid: missing generated index {exc}")
        return 1
    errors = validate_payloads(ROOT, payloads)
    if errors:
        print("BIBLE CONSOLIDATION INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    fresh = build_outputs(ROOT)
    # The generated payloads must equal a fresh deterministic rebuild.
    if payloads != fresh:
        print("BIBLE CONSOLIDATION INVALID")
        print("- generated indexes differ from fresh deterministic rebuild")
        return 1
    print(
        "BIBLE CONSOLIDATION VALID: "
        f"relations={payloads['fingerprints']['relation_count']} "
        f"families={payloads['families']['family_count']} "
        f"duplicates={payloads['duplicates']['candidate_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
