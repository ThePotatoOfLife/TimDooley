#!/usr/bin/env python3
"""Validate the entity-and-intent SEO strategy contract."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRATEGY = ROOT / "scripts" / "seo_strategy.py"
PASS = ROOT / "scripts" / "apply_entity_intent_seo.py"


def main() -> int:
    errors: list[str] = []
    if not STRATEGY.exists():
        errors.append("missing scripts/seo_strategy.py")
        strategy = ""
    else:
        strategy = STRATEGY.read_text(encoding="utf-8")
        try:
            ast.parse(strategy)
        except SyntaxError as exc:
            errors.append(f"seo_strategy.py syntax error: {exc}")

    required = (
        "def classify_route(",
        "def metadata_for(",
        "def schema_profile(",
        "def related_routes(",
        '"home"',
        '"tim-profile"',
        '"bible"',
        '"north"',
        '"science"',
        '"science-paper"',
        '"timeline"',
        '"source-authority"',
        '"question"',
        '"record"',
        '"ProfilePage"',
        '"ScholarlyArticle"',
        '"CollectionPage"',
        '"Article"',
    )
    for marker in required:
        if marker not in strategy:
            errors.append(f"seo_strategy.py missing contract marker: {marker}")

    forbidden = ("sameAs", "God", "Messiah", "divine identity")
    for marker in forbidden:
        if marker in strategy:
            errors.append(f"seo_strategy.py contains unsupported entity-schema marker: {marker}")

    if PASS.exists():
        patch = PASS.read_text(encoding="utf-8")
        try:
            ast.parse(patch)
        except SyntaxError as exc:
            errors.append(f"apply_entity_intent_seo.py syntax error: {exc}")
        for marker in (
            "classify_route",
            "metadata_for",
            "schema_profile",
            "related_routes",
            "entity-intent-schema",
            "related-context",
            "seo-intent-report.json",
        ):
            if marker not in patch:
                errors.append(f"apply_entity_intent_seo.py missing contract marker: {marker}")

    if errors:
        print("SEMANTIC SEO STRATEGY VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("SEMANTIC SEO STRATEGY VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
