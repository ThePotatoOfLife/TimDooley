#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "world/index.html": (
        "Ways through the World room",
        "../timeline/?tl_q=North&amp;tl_detail=1",
        "../context/source-authority/",
    ),
    "timeline/index.html": (
        "Follow a development",
        "Creative work",
        "Research &amp; formalization",
        "North through time",
    ),
    "works/index.html": (
        "Jump through Works",
        "Creative timeline",
        "Find the archive record",
        "Follow voice and formulation",
    ),
    "corporium/index.html": (
        "Ways through the Collection",
        "Voice in time",
        "Phrase into scene",
        "Phrase into evidence",
    ),
    "science/science-library.js": (
        "addResearchPath",
        "How does a question become a research object?",
        "roadmap,formalization",
    ),
    "app/longform-tts-adapter.js": (
        "addRoomPaths",
        "Ways through this room",
        "Bible comparison",
        "Collection",
        "Works",
    ),
}


def main() -> int:
    errors = []
    for rel, markers in CHECKS.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in markers:
            if marker not in text:
                errors.append(f"{rel}: missing {marker}")
    story = ROOT / "tim-dooley/story/index.html"
    if not story.exists():
        errors.append("Story reader missing")
    if errors:
        print("READER RESIDENCY VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("READER RESIDENCY VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
