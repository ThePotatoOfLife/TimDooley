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
    'WHAT AM I LOOKING AT?',
    'MODELLED 100,000-HOUR CROSSING',
    '≈ July 4, 2026 · 13:20 CEST',
    'OTHER COUNTS OF THE SAME JOURNEY',
    'LET THE JURY DECIDE WHAT COUNTS',
    '100000-hour-counting-models.json',
    '100000-hour-adjustment-ledger.json',
    'https://www.youtube.com/@TheGodFatherTim',
    'https://www.youtube.com/@TheGodFatherTim/live',
    'Son + Father always equals Total',
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
    if 'id="total"' in legacy or 'id="father"' in legacy:
        fail("legacy live-model route still contains a second counter implementation")

    print("100,000-hour canonical page contract: PASS")


if __name__ == "__main__":
    main()
