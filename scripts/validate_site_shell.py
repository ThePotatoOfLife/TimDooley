#!/usr/bin/env python3
"""Verify that the generated Pages artifact has one canonical header on every HTML page."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
HEADER_RE = re.compile(r'<header\b[^>]*data-site-header=["\']canonical["\'][^>]*>', re.I)
ALL_HEADER_RE = re.compile(r'<header\b[^>]*>', re.I)

errors: list[str] = []

if not SITE.exists():
    errors.append("_site does not exist; build_site.py must run first")
else:
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        errors.append("_site contains no HTML pages")
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        canonical = HEADER_RE.findall(text)
        all_headers = ALL_HEADER_RE.findall(text)
        legacy_count = len(all_headers) - len(canonical)
        if len(canonical) != 1:
            errors.append(f"{page.relative_to(SITE)}: expected exactly one canonical header, found {len(canonical)}")
        if legacy_count:
            errors.append(f"{page.relative_to(SITE)}: {legacy_count} legacy/non-canonical header(s) remain")

count = len(list(SITE.rglob("*.html"))) if SITE.exists() else 0
print(f"Built HTML pages checked: {count}")
if errors:
    print("SITE SHELL VALIDATION FAILED")
    for error in errors:
        print("-", error)
    raise SystemExit(1)
print("SITE SHELL VALIDATION PASSED")
