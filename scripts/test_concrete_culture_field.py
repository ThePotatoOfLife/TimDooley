#!/usr/bin/env python3
"""Regression contract for the evidence-backed concrete Culture field."""
from __future__ import annotations

import importlib.util
import json
import tempfile
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
}
REQUIRED_HUMAN_CASE_IDS = {"ghyslain-raza-star-wars-kid"}
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
    if not callable(render) or not callable(inject):
        errors.append("Culture projector must expose render_concrete_culture_field and inject_concrete_culture_field")
        return

    atlas = {"formations": [], "human_cases": [], "events": [], "flows": [], "relationships": [], "pathways": [], "case_groups": [], "public_projection": {}}
    rendered = render(atlas, {})
    required = (
        'data-culture-field',
        "Who is actually here?",
        "Where violence actually appears",
        "Follow the flows",
        "People behind the labels",
        "How a formation changes type",
        "Concrete Tree of Strife",
    )
    for marker in required:
        if marker not in rendered:
            errors.append(f"Culture projector output missing marker: {marker}")

    base = "<main class=\"culture-page\"><h2>Culture is multidimensional</h2></main>"
    once = inject(base, rendered)
    twice = inject(once, rendered)
    if once == base:
        errors.append("Culture projector did not inject before the stable Culture anchor")
    if once != twice:
        errors.append("Culture projector injection must be idempotent")


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
