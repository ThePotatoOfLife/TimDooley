#!/usr/bin/env python3
from __future__ import annotations

from build_bible_study import render


def main() -> int:
    row = {
        "id": "static-example",
        "title": "Example relation",
        "project_anchor": "Summary only",
        "recovered_wording": ["Recovered A", "Recovered B"],
        "biblical_refs": ["John 10:7"],
        "relation_argument": {"why_it_matters": "Reader-facing reason."},
        "discovery_history": {"source_direction": "Project first; comparison later."},
    }
    page = render(row, {})
    assert "Recovered wording" in page
    assert "Recovered A" in page and "Recovered B" in page
    assert "Reader-facing reason." in page
    assert "Project first; comparison later." in page
    assert "Exact wording" not in page
    print("STATIC BIBLE FALLBACK TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
