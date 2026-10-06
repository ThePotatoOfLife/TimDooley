#!/usr/bin/env python3
"""Validate the small public homepage view counter."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"
HOME_CSS = ROOT / "app" / "home-page.css"

HTML_MARKERS = (
    'class="home-view-counter"',
    'https://hits.sh/thepotatooflife.github.io/TimDooley.svg',
    'style=flat-square&amp;label=views',
    'alt="Homepage views"',
)
CSS_MARKERS = (
    '.home-view-counter{position:fixed;',
    'z-index:var(--site-z-counter,10049)',
    'bottom:calc(var(--site-access-clearance,0px) + var(--site-floating-gap,8px))',
    '.home-view-counter img{display:block;height:16px;width:auto}',
)


def fail(message: str) -> None:
    print(f"HOME VIEW COUNTER ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not HOMEPAGE.exists():
        fail("missing index.html")

    text = HOMEPAGE.read_text(encoding="utf-8", errors="replace")
    css = HOME_CSS.read_text(encoding="utf-8", errors="replace") if HOME_CSS.exists() else ""
    missing_html = [marker for marker in HTML_MARKERS if marker not in text]
    missing_css = [marker for marker in CSS_MARKERS if marker not in css]
    if missing_html:
        fail(f"index.html missing: {missing_html!r}")
    if missing_css:
        fail(f"app/home-page.css missing: {missing_css!r}")

    if text.count('class="home-view-counter"') != 1:
        fail("homepage must contain exactly one view counter")

    print("Homepage view counter contract: PASS")


if __name__ == "__main__":
    main()
