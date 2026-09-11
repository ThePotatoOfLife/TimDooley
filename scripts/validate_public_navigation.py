#!/usr/bin/env python3
"""Guard the small public navigation contract without constraining archive internals."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"

ROOT_BRANCH_PATTERNS = (
    re.compile(r'''href=["'](?:\.{1,2}/)*#branch=''', re.I),
    re.compile(r'''https://thepotatooflife\.github\.io/TimDooley/#branch=''', re.I),
)
NAV = re.compile(r"<nav\b[^>]*>(.*?)</nav>", re.I | re.S)
DEEP = re.compile(r'<div\b[^>]*class=["\'][^"\']*\bdeep\b[^"\']*["\'][^>]*>(.*?)</div>', re.I | re.S)
HREF = re.compile(r'''href=["']([^"']+)["']''', re.I)
LEGACY_NAV_LABELS = (">Chronology</a>", ">Corporium</a>", ">Source authority</a>", ">Tim dossier</a>")


def duplicate_hrefs(fragment: str) -> list[str]:
    counts = Counter(HREF.findall(fragment))
    return sorted(href for href, count in counts.items() if count > 1)


def main() -> int:
    errors: list[str] = []
    if not SITE.exists():
        errors.append("_site does not exist; build_site.py must run first")
        pages: list[Path] = []
    else:
        pages = sorted(SITE.rglob("*.html"))

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        rel = page.relative_to(SITE)
        for pattern in ROOT_BRANCH_PATTERNS:
            if pattern.search(text):
                errors.append(
                    f"stale homepage branch route in {rel}; "
                    "route deep branches through /explore/#branch=... or a domain hub"
                )
                break

        for nav_index, nav in enumerate(NAV.findall(text), start=1):
            duplicates = duplicate_hrefs(nav)
            if duplicates:
                errors.append(f"duplicate href(s) inside nav {nav_index} of {rel}: {duplicates}")
            for label in LEGACY_NAV_LABELS:
                if label in nav:
                    errors.append(f"legacy visitor label {label[1:-4]!r} inside nav {nav_index} of {rel}")

        for deep_index, deep in enumerate(DEEP.findall(text), start=1):
            duplicates = duplicate_hrefs(deep)
            if duplicates:
                errors.append(f"duplicate href(s) inside deep-link group {deep_index} of {rel}: {duplicates}")

        if "← Potato of Life archive</a>" in text:
            errors.append(f"legacy home label remains in {rel}: use Home on the visitor surface")

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
