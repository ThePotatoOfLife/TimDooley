#!/usr/bin/env python3
"""Protect the public Bible comparison browser and its canonical data contract."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "traditions" / "bible" / "index.html"
APP = ROOT / "app" / "bible-study.js"
CSS = ROOT / "app" / "bible-study.css"
FIELD = ROOT / "knowledge" / "traditions" / "biblical-syncretism-field.json"
BUILDER = ROOT / "scripts" / "build_bible_study.py"


def require(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{owner}: missing {marker!r}")


def forbid(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"{owner}: forbidden legacy/heuristic marker {marker!r}")


def main() -> int:
    errors: list[str] = []
    for path in (PAGE, APP, CSS, FIELD, BUILDER):
        if not path.exists():
            errors.append(f"missing required Bible reader component: {path.relative_to(ROOT)}")

    page = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    app = APP.read_text(encoding="utf-8") if APP.exists() else ""
    css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""
    builder = BUILDER.read_text(encoding="utf-8") if BUILDER.exists() else ""

    require(
        page,
        (
            'href="../../app/bible-study.css"',
            'src="../../app/bible-study.js"',
            'id="focus-select"',
            'id="order-select"',
            'id="previous-relation"',
            'id="next-relation"',
            'id="result-position"',
            'id="roll-relation"',
            'id="results-toggle"',
            'id="results-list"',
            'id="filter-toggle"',
            'id="filter-count"',
            'id="bible-filters"',
            'id="active-relation"',
            'id="relations"',
            'id="search"',
        ),
        "traditions/bible/index.html",
        errors,
    )
    forbid(
        page,
        (
            'class="featured-arcs"',
            'id="study-modes"',
            'id="shuffle-comparisons"',
            "deepMatches(",
            "overlapCount(",
            "deepCandidates",
        ),
        "traditions/bible/index.html",
        errors,
    )

    require(
        app,
        (
            "biblical-syncretism-field.json",
            "biblical-passage-fragments.json",
            "tim-biblical-vocabulary-attestation-ledger.json",
            "reverse-biblical-overlap-timeline-2025-2026.json",
            "rational-potato-x-occurrence-ledger-2024-2026.json",
            "timeline-events.json",
            "BIBLE_BOOK_ORDER",
            "renderActiveRelation",
            "renderResultsList",
            "syncUrlState",
            "selectRelative",
            "relatedRows",
            "ArrowLeft",
            "ArrowRight",
            "Same-date public wording",
            "Biblical vocabulary / revelation context",
            "Evidence & chronology",
            "Sources & provenance",
            "Related comparisons",
            "exact-wording-only",
            "minimum-strength",
            "bible-book",
            "timeline_event_ids",
        ),
        "app/bible-study.js",
        errors,
    )
    forbid(
        app,
        (
            "visible.map(row=>renderRelation",
            "deepMatches(",
            "overlapCount(",
            "deepCandidates",
            "wordScore",
            "refScore",
        ),
        "app/bible-study.js",
        errors,
    )

    require(
        css,
        (
            ".reader-toolbar",
            ".comparison-nav",
            ".results-panel",
            ".relation-details",
            ".active-relation",
        ),
        "app/bible-study.css",
        errors,
    )

    require(
        builder,
        (
            'class="static-relation"',
            '<details',
            'class="static-index"',
        ),
        "scripts/build_bible_study.py",
        errors,
    )

    if FIELD.exists():
        field = json.loads(FIELD.read_text(encoding="utf-8"))
        rows = field.get("relations", [])
        if not isinstance(rows, list) or len(rows) < 20:
            errors.append("biblical relation field unexpectedly thin; expected at least 20 canonical relations")
        if not field.get("study_views"):
            errors.append("biblical relation field missing study_views registry")

    if errors:
        print("BIBLE READER VALIDATION FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print("BIBLE READER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
