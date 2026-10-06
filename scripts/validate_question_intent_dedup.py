#!/usr/bin/env python3
"""Validate the build-time duplicate-question canonicalization contract."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "dedupe_question_intents.py"


def main() -> int:
    errors: list[str] = []
    if not TARGET.exists():
        errors.append("missing scripts/dedupe_question_intents.py")
        text = ""
    else:
        text = TARGET.read_text(encoding="utf-8")
        try:
            ast.parse(text)
        except SyntaxError as exc:
            errors.append(f"dedupe_question_intents.py syntax error: {exc}")
    for marker in (
        "noindex,follow",
        'rel="canonical"',
        "normalize_question",
        "question-alias-report.json",
        "location.replace",
        "content_score",
    ):
        if marker not in text:
            errors.append(f"dedupe_question_intents.py missing marker: {marker}")
    if errors:
        print("QUESTION INTENT DEDUP VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("QUESTION INTENT DEDUP VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
