#!/usr/bin/env python3
"""Verify that the generated Pages artifact has one canonical header on every HTML page."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
HEADER_RE = re.compile(r'<header\b[^>]*data-site-header=["\']canonical["\'][^>]*>', re.I)
LEGACY_RE = re.compile(r'<header\b(?![^>]*data-site-header=["\']canonical["\'])[^>]*>', re.I)

errors: list[str] = []

if not SITE.exists():
    errors.append("_site does not exist; build_site.py must run first")
else:
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        errors.append("_site contains no HTML pages")
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        canonical = len(HEADER_RE.findall(text))
        if canonical != 1:
            errors.append(f"{page.relative_to(SITE)}: expected exactly one canonical header, found {canonical}")
        legacy = LEGACY_RE.findall(text)
        if legacy:
            errors.append(f"{page.relative_to(SITE)}: legacy/non-canonical header remains")

print(f"Built HTML pages checked: {len(list(SITE.rglob('*.html'))) if SITE.exists() else 0}")
if errors:
    print("SITE SHELL VALIDATION FAILED")
    for error in errors:
        print("-", error)
    raise SystemExit(1)
print("SITE SHELL VALIDATION PASSED")
