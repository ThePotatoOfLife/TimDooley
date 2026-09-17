#!/usr/bin/env python3
"""Guard the small public navigation and deployed reader capability contract."""
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
LEGACY_NAV_LABELS = (">Corporium</a>", ">Source authority</a>", ">Tim dossier</a>")

# Readable public Rooms / sub-room surfaces that should expose the shared
# long-form speech reader in the deployed artifact. Interactive map and deep
# archive-explorer surfaces are intentionally excluded.
PROJECTED_TTS_PAGES = {
    "rooms/index.html": "rooms",
    "history/index.html": "history",
    "law/index.html": "law",
    "economy/index.html": "economy",
    "world-systems/index.html": "world-systems",
    "politics/index.html": "politics",
    "timeline/index.html": "timeline",
    "works/index.html": "works",
    "science/index.html": "science",
    "context/source-authority/index.html": "source-authority",
    "philosophy/interpretive-justice.html": "interpretive-justice",
}
TTS_ASSET_MARKERS = (
    "tts-drawer.css",
    "tts-reader.js",
    "tts-drawer.js",
    "longform-tts-adapter.js",
)

# These canonical House surfaces were historically built without the semantic
# data-reader-surface marker even though they are registered public readers.
# Keep the deployed markup aligned with data/house/public-surfaces.json.
CANONICAL_READER_SURFACES = {
    "politics/index.html": "politics",
    "timeline/index.html": "timeline",
    "context/source-authority/index.html": "sources",
}


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

    for rel, surface_id in CANONICAL_READER_SURFACES.items():
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing canonical reader surface: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        marker = f'data-reader-surface="{surface_id}"'
        if marker not in text:
            errors.append(f"{rel} missing canonical reader marker {marker}")

    for rel, reader_id in PROJECTED_TTS_PAGES.items():
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing TTS-covered public page: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        host_id = f'id="{reader_id}-tts"'
        if host_id not in text:
            errors.append(f"{rel} missing projected TTS host {host_id}")
        if "data-tts-longform" not in text:
            errors.append(f"{rel} missing data-tts-longform reader contract")
        for marker in TTS_ASSET_MARKERS:
            if marker not in text:
                errors.append(f"{rel} missing shared TTS asset {marker}")

    if errors:
        print("PUBLIC NAVIGATION VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"PUBLIC NAVIGATION VALIDATION PASSED ({len(pages)} HTML pages checked; "
        f"{len(PROJECTED_TTS_PAGES)} projected TTS surfaces; "
        f"{len(CANONICAL_READER_SURFACES)} canonical reader IDs)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
