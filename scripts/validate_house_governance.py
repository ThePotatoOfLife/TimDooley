#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOMS_PATH = ROOT / "data" / "house" / "rooms.json"
ROOMS_SCHEMA_PATH = ROOT / "schemas" / "house-room-registry.schema.json"

EXPECTED_ROOM_IDS = (
    "potatoverse-canon",
    "archive-sources",
    "time-history",
    "traditions-texts",
    "science-formal-models",
    "life-body",
    "world-systems",
    "culture-information",
    "works",
    "research-lab",
)


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required House contract: {path.relative_to(ROOT)}")
        return {}
    except Exception as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"House contract must be a JSON object: {path.relative_to(ROOT)}")
        return {}
    return value


def matches_type(value, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "null": value is None,
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
    }.get(expected, True)


def validate_schema_subset(value, schema: dict, owner: str, errors: list[str]) -> None:
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not matches_type(value, expected_type):
        errors.append(f"{owner} must be {expected_type}")
        return
    if isinstance(expected_type, list) and not any(matches_type(value, item) for item in expected_type):
        errors.append(f"{owner} must match one of {expected_type}")
        return
    if "const" in schema and value != schema["const"]:
        errors.append(f"{owner} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{owner} must be one of {schema['enum']!r}")
    if isinstance(value, str) and schema.get("pattern") and not re.search(schema["pattern"], value):
        errors.append(f"{owner} does not match pattern {schema['pattern']!r}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{owner} missing required field: {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{owner} contains unexpected field: {key}")
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, dict):
                validate_schema_subset(value[key], child_schema, f"{owner}.{key}", errors)
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{owner} requires at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{owner} allows at most {schema['maxItems']} items")
        if schema.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value):
            errors.append(f"{owner} items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_schema_subset(item, item_schema, f"{owner}[{index}]", errors)


def validate_rooms(errors: list[str]) -> dict:
    schema = load_json(ROOMS_SCHEMA_PATH, errors)
    rooms = load_json(ROOMS_PATH, errors)
    if schema and rooms:
        validate_schema_subset(rooms, schema, "rooms", errors)
    entries = rooms.get("rooms", []) if isinstance(rooms, dict) else []
    ids = [row.get("id") for row in entries if isinstance(row, dict)]
    if tuple(ids) != EXPECTED_ROOM_IDS:
        errors.append(f"canonical Room IDs/order must equal {EXPECTED_ROOM_IDS!r}; got {tuple(ids)!r}")
    known = set(ids)
    for row in entries:
        if not isinstance(row, dict):
            continue
        for target in row.get("interfaces", []):
            if target not in known:
                errors.append(f"Room {row.get('id')} references unknown interface Room {target}")
    return rooms


def main() -> int:
    errors: list[str] = []
    validate_rooms(errors)
    if errors:
        print("POTATO HOUSE GOVERNANCE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("POTATO HOUSE GOVERNANCE VALIDATION PASSED: 10 canonical Domain Rooms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
