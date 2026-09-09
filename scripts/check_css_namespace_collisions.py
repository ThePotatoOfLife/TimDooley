#!/usr/bin/env python3
"""Detect layout-class collisions between shared app CSS and static reader pages.

This check is intentionally conservative. It does not ban generic classes everywhere;
it verifies that pages which reuse legacy structural classes are protected by the
reader/layout guard, and it flags new dangerous global layout selectors in shared CSS.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "app" / "style.css"
READER = ROOT / "app" / "reader.css"
GUARD = ROOT / "app" / "layout-guard.css"

DANGEROUS_GLOBAL = {
    ".nav": ("position", "top", "inset", "z-index"),
    ".grid": ("grid-template-columns", "position", "top"),
    ".section": ("position", "top", "z-index"),
    ".record": ("position", "top", "z-index"),
    ".status": ("position", "top", "z-index"),
}

errors = []
warnings = []

if not GUARD.exists():
    errors.append("app/layout-guard.css is missing")
if not READER.exists() or 'layout-guard.css' not in READER.read_text(encoding='utf-8'):
    errors.append("app/reader.css must import layout-guard.css")

style = STYLE.read_text(encoding='utf-8') if STYLE.exists() else ""
for selector, props in DANGEROUS_GLOBAL.items():
    # Existing .nav/.grid debt is allowed only because layout-guard.css neutralizes it
    # on reader pages. Any additional high-risk generic selector should be reviewed.
    matches = re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", style)
    if len(matches) > 1:
        warnings.append(f"{selector} has {len(matches)} global rule blocks in app/style.css")
    for block in matches:
        if any(re.search(rf"\b{re.escape(prop)}\s*:", block) for prop in props):
            warnings.append(f"legacy global {selector} controls layout; keep protected by layout guard or namespace it")

html_files = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
for path in html_files:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "app/style.css" not in text and "../app/style.css" not in text and "../../app/style.css" not in text:
        continue
    uses_legacy_nav = bool(re.search(r'class=["\'][^"\']*\bnav\b', text))
    is_home_archive = path == ROOT / "index.html" and 'id="archive-explorer"' in text
    if uses_legacy_nav and not is_home_archive:
        protected = (
            "reader.css" in text
            or "layout-guard.css" in text
            or "page-nav" in text
        )
        if not protected:
            errors.append(f"{path.relative_to(ROOT)} uses legacy .nav with app/style.css but no reader/layout guard")

if warnings:
    print("CSS namespace warnings:")
    for w in sorted(set(warnings)):
        print(f"  - {w}")

if errors:
    print("CSS namespace errors:")
    for e in sorted(set(errors)):
        print(f"  - {e}")
    sys.exit(1)

print(f"CSS namespace check passed ({len(html_files)} HTML files scanned).")
