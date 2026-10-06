#!/usr/bin/env python3
"""Finalize homepage structured metadata before validation/deployment."""
from __future__ import annotations

from pathlib import Path

from site_shell_contract import normalize_home_structured_data

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "_site" / "index.html"


def main() -> int:
    if not HOME.exists():
        print("PUBLIC HOME FINALIZATION FAILED: _site/index.html missing")
        return 1
    original = HOME.read_text(encoding="utf-8")
    normalized = normalize_home_structured_data(original)
    if normalized != original:
        HOME.write_text(normalized, encoding="utf-8")
        print("Finalized homepage structured metadata")
    else:
        print("Homepage structured metadata already finalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
