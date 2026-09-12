#!/usr/bin/env python3
"""Regression gate for reader-question provenance in machine discovery."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = ROOT / "scripts" / "build_discovery.py"
QUESTION_PATH = ROOT / "knowledge" / "reader" / "tim-dooley-question-index.json"
QUESTION_SOURCE = str(QUESTION_PATH.relative_to(ROOT))


def load_builder():
    spec = importlib.util.spec_from_file_location("build_discovery_projection", BUILD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load scripts/build_discovery.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def as_expected_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def main() -> int:
    reader = json.loads(QUESTION_PATH.read_text(encoding="utf-8"))
    source_questions = [
        q for q in reader.get("questions", [])
        if isinstance(q, dict) and q.get("id") and q.get("deep_sources") and q.get("class")
    ]
    if not source_questions:
        print("Discovery projection validation FAILED")
        print(" - no Tim reader question contains both deep_sources and class; fixture contract disappeared")
        return 1

    builder = load_builder()
    entries = {entry.get("id"): entry for entry in builder.faq_entries() if isinstance(entry, dict)}
    errors = []
    checked = 0
    for source in source_questions:
        output = entries.get(source["id"])
        if not output or output.get("source_faq_view") != QUESTION_SOURCE:
            # Duplicate IDs are intentionally owned by the canonical FAQ atlas;
            # provenance projection is only applicable when the reader row was
            # actually imported into the merged discovery view.
            continue
        checked += 1
        expected_owners = as_expected_list(source.get("canonical_owners", source.get("deep_sources")))
        expected_class = as_expected_list(source.get("epistemic_class", source.get("class")))
        if output.get("canonical_owners") != expected_owners:
            errors.append(
                f"{source['id']}: canonical_owners {output.get('canonical_owners')!r} != expected {expected_owners!r}"
            )
        if output.get("epistemic_class") != expected_class:
            errors.append(
                f"{source['id']}: epistemic_class {output.get('epistemic_class')!r} != expected {expected_class!r}"
            )
        break

    if checked == 0:
        errors.append("could not find a reader-owned Tim question to verify")

    if errors:
        print("Discovery projection validation FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Discovery projection validation passed: imported Tim question provenance is preserved and normalized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
