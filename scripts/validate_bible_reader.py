#!/usr/bin/env python3
"""Protect the public Bible study instrument from being collapsed into a thin list again."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "traditions" / "bible" / "index.html"
APP = ROOT / "app" / "bible-study.js"
CSS = ROOT / "app" / "bible-study.css"
FIELD = ROOT / "knowledge" / "traditions" / "biblical-syncretism-field.json"


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
    for path in (PAGE, APP, CSS, FIELD):
        if not path.exists():
            errors.append(f"missing required Bible reader component: {path.relative_to(ROOT)}")

    page = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    app = APP.read_text(encoding="utf-8") if APP.exists() else ""

    require(
        page,
        (
            'href="../../app/bible-study.css"',
            'src="../../app/bible-study.js"',
            'id="study-modes"',
            'data-view="jesus"',
            'data-view="tim-said"',
            'data-view="tim-lived"',
            'data-view="prophecy"',
            'data-view="father-house"',
            'data-view="door-ladder"',
            'data-view="counter-texts"',
            'data-view="all"',
            'id="roll-relation"',
            'id="bible-filters"',
            'id="relations"',
        ),
        "traditions/bible/index.html",
        errors,
    )
    forbid(page, ("deepMatches(", "overlapCount(", "deepCandidates"), "traditions/bible/index.html", errors)

    require(
        app,
        (
            "biblical-syncretism-field.json",
            "biblical-passage-fragments.json",
            "tim-biblical-vocabulary-attestation-ledger.json",
            "reverse-biblical-overlap-timeline-2025-2026.json",
            "rational-potato-x-occurrence-ledger-2024-2026.json",
            "timeline-events.json",
            "Same-date public wording",
            "Biblical vocabulary / revelation context",
            "Tim / Son / project",
            "Bible",
            "exact-wording-only",
            "minimum-strength",
            "bible-book",
            "timeline_event_ids",
            "ROLL",
        ),
        "app/bible-study.js",
        errors,
    )
    forbid(app, ("deepMatches(", "overlapCount(", "deepCandidates", "wordScore", "refScore"), "app/bible-study.js", errors)

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
