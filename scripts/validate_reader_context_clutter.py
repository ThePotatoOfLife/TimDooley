#!/usr/bin/env python3
"""Guard against duplicate SEO navigation on curated reader pages."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEO_PASS = ROOT / "scripts" / "apply_entity_intent_seo.py"

CURATED = (
    "tim-dooley",
    "philosophy",
    "religion",
    "traditions/bible",
    "north",
    "world",
    "world-map",
    "science",
    "timeline",
)


def main() -> int:
    text = SEO_PASS.read_text(encoding="utf-8", errors="replace") if SEO_PASS.exists() else ""
    errors = []
    for marker in ("CURATED_READER_ROUTES", "has_strong_reader_navigation"):
        if marker not in text:
            errors.append(f"missing clutter-control marker: {marker}")
    for route in CURATED:
        if f'"{route}"' not in text:
            errors.append(f"missing curated route: {route}")
    if errors:
        print("READER CONTEXT CLUTTER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("READER CONTEXT CLUTTER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
