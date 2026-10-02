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
        "reader_scene": {"opening": "At that time, the scene began.", "turn": "And from there, the meaning changed."},
        "reader_sequence": {
            "title": "Continuous reading",
            "intro": "Read the movement in order.",
            "steps": [
                {"source_type": "project", "source_label": "Project source", "heading": "First", "text": "Project step."},
                {"source_type": "gospel", "source_label": "Gospel source", "heading": "Second", "text": "Gospel step.", "ref": "John 14:1-4"},
                {"source_type": "limit", "source_label": "Limit", "heading": "Do not collapse", "text": "Roles remain distinct."},
            ],
            "conclusion": "Movement stays ordered."
        },
        "discovery_history": {"source_direction": "Project first; comparison later."},
    }
    page = render(row, {})
    assert "Recovered wording" in page
    assert "Recovered A" in page and "Recovered B" in page
    assert "Reader-facing reason." in page
    assert "The scene" in page and "At that time, the scene began." in page
    assert "Continuous reading" in page and "Project step." in page and "Gospel step." in page
    assert "Do not collapse" in page and "Roles remain distinct." in page
    assert "Archive grounding" in page
    assert "Project first; comparison later." in page
    assert "Exact wording" not in page
    print("STATIC BIBLE FALLBACK TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
