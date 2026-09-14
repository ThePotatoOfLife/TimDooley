#!/usr/bin/env python3
"""Validate the small public homepage view counter."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"

REQUIRED_MARKERS = (
    'class="home-view-counter"',
    'https://hits.sh/thepotatooflife.github.io/TimDooley.svg',
    'style=flat-square&amp;label=views',
    'alt="Homepage views"',
    '.home-view-counter{position:fixed;',
    '.home-view-counter img{display:block;height:18px;width:auto}',
)


def fail(message: str) -> None:
    print(f"HOME VIEW COUNTER ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not HOMEPAGE.exists():
        fail("missing index.html")

    text = HOMEPAGE.read_text(encoding="utf-8", errors="replace")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if missing:
        fail(f"index.html missing: {missing!r}")

    if text.count('class="home-view-counter"') != 1:
        fail("homepage must contain exactly one view counter")

    print("Homepage view counter contract: PASS")


if __name__ == "__main__":
    main()
