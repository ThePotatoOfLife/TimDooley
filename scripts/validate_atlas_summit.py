#!/usr/bin/env python3
"""Validate the source homepage as the Atlas summit during compatibility migration."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"


def main() -> int:
    text = HOME.read_text(encoding="utf-8")
    required = (
        'href="app/design-system.css"',
        'data-reader-surface="home"',
        'data-atlas-summit="true"',
        'id="start-here"',
        'id="ways-through"',
        'id="go-deeper"',
        'href="atlas/"',
        'href="atlas/potato-of-life/"',
        'href="atlas/tim-dooley/"',
        'href="explore/"',
        'data-compatibility="legacy-five-routes"',
    )
    missing = [marker for marker in required if marker not in text]
    if missing:
        raise SystemExit(f"ATLAS SUMMIT FAILED: missing markers {missing}")

    forbidden = (
        'aria-label="Main sections"',
        "five simple doors",
        "exactly five",
    )
    present = [marker for marker in forbidden if marker in text]
    if present:
        raise SystemExit(f"ATLAS SUMMIT FAILED: legacy ownership language remains {present}")

    compatibility_start = text.find('data-compatibility="legacy-five-routes"')
    if compatibility_start < 0:
        raise SystemExit("ATLAS SUMMIT FAILED: compatibility region missing")
    compatibility = text[compatibility_start:]
    for route in ("tim-dooley/", "religion/", "philosophy/", "science/", "world/"):
        if f'href="{route}"' not in compatibility:
            raise SystemExit(f"ATLAS SUMMIT FAILED: legacy compatibility route missing: {route}")

    print("ATLAS SUMMIT PASS: homepage is Atlas-first with explicit legacy route compatibility")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
