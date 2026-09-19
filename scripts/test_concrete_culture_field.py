#!/usr/bin/env python3
"""Regression contract for the evidence-backed concrete Culture field."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "knowledge/culture/concrete-culture-field-atlas.json"
LEDGER = ROOT / "knowledge/culture/concrete-culture-source-ledger.json"
PROJECTOR = ROOT / "scripts/project_public_culture_field.py"

REQUIRED_TOP_LEVEL = (
    "formations",
    "human_cases",
    "events",
    "flows",
    "relationships",
    "pathways",
    "case_groups",
    "public_projection",
    "topic_groundings",
)
REQUIRED_CASE_IDS = {
    "loyal-to-familia",
    "otf-grimm-violence-as-a-service",
    "nxivm",
    "kiwi-farms",
    "online-snark-communities",
    "hip-hop",
    "medecins-sans-frontieres",
    "icrc",
    "organization-for-transformative-works-ao3",
    "burning-man",
    "skateboarding",
    "wikipedia",
    "mastodon-activitypub",
}
REQUIRED_HUMAN_CASE_IDS = {"ghyslain-raza-star-wars-kid"}
REQUIRED_GROUNDING_IDS = {
    "formation-in-practice",
    "control-in-practice",
    "tribunal-role-lock-in-practice",
    "classification-in-practice",
    "infrastructure-in-practice",
}
REQUIRED_EXPANSION_FIELDS = {
    "organization-for-transformative-works-ao3": {"governance_model", "infrastructure_model"},
    "burning-man": {"governance_model", "correction_mechanisms"},
    "skateboarding": {"commercialization_tensions"},
    "wikipedia": {"governance_model", "correction_mechanisms"},
    "mastodon-activitypub": {"governance_model", "infrastructure_model", "exit_or_portability"},
}
PRIVATE_FIELD_TOKENS = {
    "home_address",
    "phone",
    "phone_number",
    "private_email",
    "credentials",
    "password",
}


def load_json(path: Path, errors: list[str]) -> dict:
    if not path.exists():
        errors.append(f"missing canonical Culture file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)} must contain a JSON object")
        return {}
    return value


def source_refs(record: dict) -> list[str]:
    refs = record.get("source_refs", [])
    return refs if isinstance(refs, list) else []


def validate_source_refs(atlas: dict, ledger: dict, errors: list[str]) -> None:
    source_ids = {
        item.get("id")
        for item in ledger.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if not source_ids:
        errors.append("source ledger must expose a non-empty sources array")
        return

    for collection in ("formations", "human_cases", "events", "flows", "relationships", "pathways"):
        for record in atlas.get(collection, []):
            if not isinstance(record, dict):
                errors.append(f"{collection} contains a non-object record")
                continue
            rid = record.get("id") or f"{record.get('from', '?')}->{record.get('to', '?')}"
            refs = source_refs(record)
            if not refs:
                errors.append(f"{collection}:{rid} missing source_refs")
            for ref in refs:
                if ref not in source_ids:
                    errors.append(f"{collection}:{rid} has dangling source ref {ref}")


def validate_privacy_and_types(atlas: dict, errors: list[str]) -> None:
    for formation in atlas.get("formations", []):
        if not isinstance(formation, dict):
            continue
        types = formation.get("formation_types", [])
        if any(str(value).lower() == "lolcow" for value in types if isinstance(value, str)):
            errors.append(f"formation {formation.get('id')} stores lolcow as an intrinsic type")

    for case in atlas.get("human_cases", []):
        if not isinstance(case, dict):
            continue
        cid = case.get("id")
        if not case.get("public_basis"):
            errors.append(f"human case {cid} missing public_basis")
        if not case.get("privacy_notes"):
            errors.append(f"human case {cid} missing privacy_notes")
        if str(case.get("case_type", "")).lower() == "lolcow":
            errors.append(f"human case {cid} stores lolcow as an intrinsic case type")
        lowered_keys = {str(key).lower() for key in case}
        for token in PRIVATE_FIELD_TOKENS & lowered_keys:
            errors.append(f"human case {cid} exposes forbidden private field {token}")


def validate_money_flows(atlas: dict, errors: list[str]) -> None:
    money_types = {"money", "grant", "donation", "membership_fee", "commercial_revenue", "illicit_proceeds"}
    for flow in atlas.get("flows", []):
        if not isinstance(flow, dict) or flow.get("flow_type") not in money_types:
            continue
        if "amount" in flow and not flow.get("currency"):
            errors.append(f"money flow {flow.get('id')} has amount without currency")
        if not flow.get("period"):
            errors.append(f"money flow {flow.get('id')} missing period")


def validate_expansion_fields(atlas: dict, errors: list[str]) -> None:
    by_id = {
        item.get("id"): item
        for item in atlas.get("formations", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for case_id, required_fields in REQUIRED_EXPANSION_FIELDS.items():
        record = by_id.get(case_id)
        if not record:
            continue
        missing = sorted(field for field in required_fields if not record.get(field))
        if missing:
            errors.append(f"formation {case_id} missing expansion fields: {missing}")


def validate_topic_groundings(atlas: dict, errors: list[str]) -> None:
    collections = {
        "formation": "formations",
        "human_case": "human_cases",
        "event": "events",
        "flow": "flows",
        "relationship": "relationships",
        "pathway": "pathways",
    }
    indexes = {
        kind: {
            item.get("id")
            for item in atlas.get(collection, [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        for kind, collection in collections.items()
    }
    rows = [x for x in atlas.get("topic_groundings", []) if isinstance(x, dict)]
    ids = {x.get("id") for x in rows}
    missing = sorted(REQUIRED_GROUNDING_IDS - ids)
    if missing:
        errors.append(f"atlas missing required topic groundings: {missing}")
    for row in rows:
        gid = row.get("id")
        if not row.get("anchor_before"):
            errors.append(f"topic grounding {gid} missing anchor_before")
        if not row.get("summary"):
            errors.append(f"topic grounding {gid} missing summary")
        cards = row.get("cards", [])
        if not isinstance(cards, list) or len(cards) < 2:
            errors.append(f"topic grounding {gid} must contain at least two concrete cards")
            continue
        for card in cards:
            if not isinstance(card, dict):
                errors.append(f"topic grounding {gid} contains invalid card")
                continue
            kind = card.get("object_type")
            oid = card.get("object_id")
            if kind not in indexes:
                errors.append(f"topic grounding {gid} uses unknown object_type {kind}")
            elif oid not in indexes[kind]:
                errors.append(f"topic grounding {gid} points to missing {kind} {oid}")
            if not card.get("point"):
                errors.append(f"topic grounding {gid}/{oid} missing concrete point")


def validate_projector(errors: list[str]) -> None:
    if not PROJECTOR.exists():
        errors.append("missing public projector: scripts/project_public_culture_field.py")
        return
    spec = importlib.util.spec_from_file_location("project_public_culture_field", PROJECTOR)
    if spec is None or spec.loader is None:
        errors.append("unable to import Culture projector")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    render = getattr(module, "render_concrete_culture_field", None)
    inject = getattr(module, "inject_concrete_culture_field", None)
    render_grounding = getattr(module, "render_topic_grounding", None)
    inject_groundings = getattr(module, "inject_topic_groundings", None)
    if not callable(render) or not callable(inject) or not callable(render_grounding) or not callable(inject_groundings):
        errors.append("Culture projector must expose concrete-field and topic-grounding render/inject functions")
        return

    atlas = {"formations": [], "human_cases": [], "events": [], "flows": [], "relationships": [], "pathways": [], "case_groups": [], "public_projection": {}, "topic_groundings": []}
    rendered = render(atlas, {})
    required = (
        'data-culture-field',
        "Who is actually here?",
        "Where violence actually appears",
        "Follow the flows",
        "People behind the labels",
        "How a formation changes type",
        "Concrete Tree of Strife",
        "Who owns the infrastructure?",
        "How correction works",
        "Ritual without captivity",
        "When underground becomes institution",
    )
    for marker in required:
        if marker not in rendered:
            errors.append(f"Culture projector output missing marker: {marker}")

    base = (
        '<main class="culture-page">'
        '<h2>From scene to canon</h2>'
        '<h2>When conflict becomes culture</h2>'
        '<h2>Reputation, narrative capture and correction</h2>'
        '<h2>Cultural infrastructure</h2>'
        '<h2>Culture is multidimensional</h2>'
        '</main>'
    )
    grounding_fixture = {
        "topic_groundings": [
            {
                "id": "fixture",
                "anchor_before": "From scene to canon",
                "title": "Fixture",
                "summary": "Concrete fixture",
                "cards": [],
            }
        ]
    }
    grounded_once = inject_groundings(base, grounding_fixture, {})
    grounded_twice = inject_groundings(grounded_once, grounding_fixture, {})
    if 'data-culture-grounding="fixture"' not in grounded_once:
        errors.append("Culture projector did not inject topic grounding beside its theory anchor")
    if grounded_once != grounded_twice:
        errors.append("Culture topic-grounding injection must be idempotent")
    once = inject(grounded_once, rendered)
    twice = inject(once, rendered)
    if once == grounded_once:
        errors.append("Culture projector did not inject before the stable Culture anchor")
    if once != twice:
        errors.append("Culture concrete-field injection must be idempotent")


def main() -> int:
    errors: list[str] = []
    atlas = load_json(ATLAS, errors)
    ledger = load_json(LEDGER, errors)

    if atlas:
        for key in REQUIRED_TOP_LEVEL:
            if key not in atlas:
                errors.append(f"atlas missing top-level collection: {key}")
        formation_ids = {
            item.get("id") for item in atlas.get("formations", []) if isinstance(item, dict)
        }
        missing_cases = sorted(REQUIRED_CASE_IDS - formation_ids)
        if missing_cases:
            errors.append(f"atlas missing required formation cases: {missing_cases}")
        human_case_ids = {
            item.get("id") for item in atlas.get("human_cases", []) if isinstance(item, dict)
        }
        missing_human = sorted(REQUIRED_HUMAN_CASE_IDS - human_case_ids)
        if missing_human:
            errors.append(f"atlas missing required human cases: {missing_human}")
        validate_privacy_and_types(atlas, errors)
        validate_money_flows(atlas, errors)
        validate_expansion_fields(atlas, errors)
        validate_topic_groundings(atlas, errors)

    if atlas and ledger:
        validate_source_refs(atlas, ledger, errors)

    validate_projector(errors)

    if errors:
        print("CONCRETE CULTURE FIELD VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CONCRETE CULTURE FIELD VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
