#!/usr/bin/env python3
"""Validate the witness-first Bible reader overlay."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "traditions" / "bible" / "index.html"
JS = ROOT / "app" / "bible-witness-loader.js"
CSS = ROOT / "app" / "bible-witness-loader.css"


def main() -> int:
    errors = []
    for path in (PAGE, JS, CSS):
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")

    page = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    js = JS.read_text(encoding="utf-8") if JS.exists() else ""
    css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""

    required_js = (
        "projectSceneText",
        "scene.summary",
        "row.project_anchor",
        "biblicalSceneText",
        "discoveryText",
        "counterpressureText",
        "Witness the event first",
        "What happened",
        "What the biblical text does",
        "What becomes visible when they are read together",
        "Where the reading is tested",
        "MutationObserver",
    )
    for marker in required_js:
        if marker not in js:
            errors.append(f"app/bible-witness-loader.js missing {marker!r}")

    forbidden_js = ("row.what_happened", "scrollIntoView(")
    for marker in forbidden_js:
        if marker in js:
            errors.append(f"app/bible-witness-loader.js contains forbidden {marker!r}")

    if '../../app/bible-witness-loader.css' not in page:
        errors.append("Bible page does not load witness stylesheet")
    if '../../app/bible-witness-loader.js' not in page:
        errors.append("Bible page does not load witness renderer")

    dossier = page.find('bible-dossier-loader.js')
    witness = page.find('bible-witness-loader.js')
    study = page.find('bible-study.js')
    if min(dossier, witness, study) < 0 or not dossier < witness < study:
        errors.append("witness loader must load after dossier loader and before bible-study.js")

    for marker in (".witness-dossier", ".witness-opening", ".witness-chapter", ".witness-quote"):
        if marker not in css:
            errors.append(f"app/bible-witness-loader.css missing {marker!r}")

    if errors:
        print("BIBLE WITNESS VALIDATION FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print("BIBLE WITNESS VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
