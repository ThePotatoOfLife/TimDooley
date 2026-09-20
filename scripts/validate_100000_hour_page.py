#!/usr/bin/env python3
"""Validate the canonical 100,000-hour public page and legacy live-model redirect."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "tim-dooley" / "100000-hours" / "index.html"
LEGACY = ROOT / "tim-dooley" / "100000-hours" / "live-model.html"

CANONICAL_MARKERS = (
    'rel="canonical" href="https://thepotatooflife.github.io/TimDooley/tim-dooley/100000-hours/"',
    'id="live-total"',
    'id="live-son"',
    'id="live-father"',
    'id="live-beyond"',
    'id="progress-ring"',
    'Live model · story archaeology · evidence ledger',
    'MODELLED 100,000-HOUR CROSSING',
    '≈ July 4, 2026 · 13:20 CEST',
    'The number had a story before it had an audit',
    '../story/#100k-spirals-2026-03-28',
    '../story/#hundred-thousand-stones-2026-05-01',
    '../story/#center-foundation-2026-07-01',
    '../story/#most-public-god-hours-2026-09-03',
    'What fifteen years of hours actually contain',
    'Four different things people mean by “100,000 hours”',
    'LET THE JURY DECIDE WHAT COUNTS',
    '100000-hour-counting-models.json',
    '100000-hour-adjustment-ledger.json',
    '100000-hour-story-anchors.json',
    'https://www.youtube.com/@TheGodFatherTim',
    'https://www.youtube.com/@TheGodFatherTim/live',
    'Son + Father always equals Total',
    "What the number is celebrating",
    "Scale check.",
    "What kind of expertise can a life on camera produce?",
    "So why hasn't everybody heard of Tim Dooley?",
    "100000-hour-public-benchmarks.json",
    "The counter should keep sending you away from the counter.",
    "766 hours",
    "848 hours",
    "211,896 views / 37,635.0 watch-hours",
    "The point was not always to make something.",
    "A spiral is only different from a circle if something changes on the next pass.",
    "livestream-duration-and-100000-hour-threshold.json",
    'site-tts.js',
)
LEGACY_MARKERS = (
    'content="0; url=./"',
    'rel="canonical" href="https://thepotatooflife.github.io/TimDooley/tim-dooley/100000-hours/"',
    'location.replace("./")',
    'noindex,follow',
)


def fail(message: str) -> None:
    print(f"100000-HOUR PAGE ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(path: Path, markers: tuple[str, ...]) -> str:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        fail(f"{path.relative_to(ROOT)} missing: {missing!r}")
    return text


def main() -> None:
    canonical = require(CANONICAL, CANONICAL_MARKERS)
    legacy = require(LEGACY, LEGACY_MARKERS)

    if 'href="live-model.html"' in canonical:
        fail("canonical page still links readers to the duplicate live-model page")
    if canonical.count('../story/#') < 4:
        fail("canonical page does not expose enough dated Story source doors")
    story_anchors = ROOT / "data" / "100000-hour-story-anchors.json"
    if not story_anchors.exists():
        fail("missing 100000-hour story anchors registry")
    if 'id="total"' in legacy or 'id="father"' in legacy:
        fail("legacy live-model route still contains a second counter implementation")

    print("100,000-hour canonical page contract: PASS")


if __name__ == "__main__":
    main()
