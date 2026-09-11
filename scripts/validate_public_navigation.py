#!/usr/bin/env python3
"""Guard the small public navigation contract without constraining archive internals."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"

ROOT_BRANCH_PATTERNS = (
    re.compile(r'''href=["'](?:\.{1,2}/)*#branch=''', re.I),
    re.compile(r'''https://thepotatooflife\.github\.io/TimDooley/#branch=''', re.I),
)


def main() -> int:
    errors: list[str] = []
    if not SITE.exists():
        errors.append("_site does not exist; build_site.py must run first")
        pages: list[Path] = []
    else:
        pages = sorted(SITE.rglob("*.html"))

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for pattern in ROOT_BRANCH_PATTERNS:
            if pattern.search(text):
                errors.append(
                    f"stale homepage branch route in {page.relative_to(SITE)}; "
                    "route deep branches through /explore/#branch=... or a domain hub"
                )
                break

    required_pages = (
        "religion/index.html",
        "traditions/bible/index.html",
        "traditions/vesica/index.html",
    )
    for rel in required_pages:
        if not (SITE / rel).exists():
            errors.append(f"missing public navigation page: {rel}")

    for rel in ("traditions/bible/index.html", "traditions/vesica/index.html"):
        path = SITE / rel
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            if '../../religion/' not in text:
                errors.append(f"{rel} does not link back to its Religion parent hub")

    if errors:
        print("PUBLIC NAVIGATION VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PUBLIC NAVIGATION VALIDATION PASSED ({len(pages)} HTML pages checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
