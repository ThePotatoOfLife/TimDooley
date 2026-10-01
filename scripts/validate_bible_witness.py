#!/usr/bin/env python3
"""Validate that the retired witness-first overlay no longer owns the Bible page."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "traditions" / "bible" / "index.html"
STUDY = ROOT / "app" / "bible-study.js"
ATLAS = ROOT / "app" / "bible-atlas-ui.js"
DOSSIER = ROOT / "app" / "bible-dossier-loader.js"

def main() -> int:
    errors = []
    for path in (PAGE, STUDY, ATLAS, DOSSIER):
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")

    page = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    study = STUDY.read_text(encoding="utf-8") if STUDY.exists() else ""
    atlas = ATLAS.read_text(encoding="utf-8") if ATLAS.exists() else ""
    dossier = DOSSIER.read_text(encoding="utf-8") if DOSSIER.exists() else ""

    for marker in ("bible-witness-loader.js", "bible-witness-loader.css", "bible-scene-reader.js"):
        if marker in page:
            errors.append(f"Bible page still loads retired presentation layer: {marker}")

    if 'class="tim-first"' not in study or 'class="bible-under"' not in study:
        errors.append("bible-study.js must render Tim/Son first and Bible underneath")

    if "startEvidence(corpus)" in atlas:
        errors.append("Bible atlas must not replace the active comparison with an evidence-first overlay")

    for marker in ("MutationObserver", "active-relation", "paired-narrative", "dossier-open-evidence"):
        if marker in dossier:
            errors.append(f"dossier loader must be data-only; found {marker}")

    if errors:
        print("BIBLE PRESENTATION OWNERSHIP VALIDATION FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print("BIBLE PRESENTATION OWNERSHIP VALIDATION PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
