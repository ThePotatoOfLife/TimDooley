#!/usr/bin/env python3
"""Detect layout-class collisions between shared app CSS and static reader pages.

The interactive archive owns .archive-nav. Generic .nav is reserved for local/static
legacy pages and must never regain global layout behavior in app/style.css.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "app" / "style.css"
SITE_SYSTEM = ROOT / "app" / "site-system.css"
READER = ROOT / "app" / "reader.css"
READER_V2 = ROOT / "app" / "reader-v2.css"
GUARD = ROOT / "app" / "layout-guard.css"
HOME = ROOT / "index.html"

MIGRATED_SHELL_REQUIREMENTS = {
    HOME: ("site-system.css", 'class="page '),
    ROOT / "tim-dooley" / "index.html": ("site-system.css", "page-nav", "page-header"),
    ROOT / "religion" / "index.html": ("site-system.css", "page-nav", "page-header"),
    ROOT / "philosophy" / "index.html": ("site-system.css", "page-nav", "page-header"),
    ROOT / "science" / "index.html": ("site-system.css", "page-nav", "page-header"),
    ROOT / "world" / "index.html": ("site-system.css", "page-nav", "page-header"),
}

MIGRATED_LOCAL_STYLE_SOURCES = [
    HOME,
    ROOT / "tim-dooley" / "index.html",
    ROOT / "religion" / "index.html",
    ROOT / "philosophy" / "philosophy.css",
    ROOT / "science" / "science-library.css",
    ROOT / "world" / "index.html",
]
CANONICAL_TOKEN_LITERALS = ("#090b09", "#f4f0e5", "#b8dc82", "#d8b56b", "#30382f")

RISKY_GLOBAL = {
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
if not READER.exists() or 'reader-v2.css' not in READER.read_text(encoding='utf-8'):
    errors.append("app/reader.css must import the House-scoped reader-v2.css convergence layer")
if not READER_V2.exists():
    errors.append("app/reader-v2.css is missing")
else:
    reader_v2 = READER_V2.read_text(encoding="utf-8")
    if ".site-housebar ~ main" not in reader_v2:
        errors.append("app/reader-v2.css must scope legacy-reader convergence beneath .site-housebar ~ main")
    for forbidden in (r"(?m)^\s*body\s*\{", r"(?m)^\s*:root\s*\{", r"(?m)^\s*\.nav\s*\{", r"(?m)^\s*\.card\s*\{"):
        if re.search(forbidden, reader_v2):
            errors.append("app/reader-v2.css must not introduce unscoped global reader selectors")

style = STYLE.read_text(encoding='utf-8') if STYLE.exists() else ""

if not SITE_SYSTEM.exists():
    errors.append("app/site-system.css is missing")
else:
    site_system = SITE_SYSTEM.read_text(encoding="utf-8")
    for selector in (".nav", ".grid", ".section", ".card", ".record", ".status"):
        for block in re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", site_system):
            if re.search(r"\b(position|top|inset|z-index|display|grid-template-columns|grid-template-rows)\s*:", block):
                errors.append(
                    f"app/site-system.css must not assign structural layout through generic {selector}; use .page-* or a named component"
                )

for page, markers in MIGRATED_SHELL_REQUIREMENTS.items():
    text = page.read_text(encoding="utf-8", errors="ignore") if page.exists() else ""
    for marker in markers:
        if marker not in text:
            errors.append(f"{page.relative_to(ROOT)} missing shared shell marker: {marker}")

for path in MIGRATED_LOCAL_STYLE_SOURCES:
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    for root_block in re.findall(r":root\s*\{([^}]*)\}", text, flags=re.I | re.S):
        repeated = [literal for literal in CANONICAL_TOKEN_LITERALS if literal.lower() in root_block.lower()]
        if repeated:
            warnings.append(
                f"{path.relative_to(ROOT)} redefines canonical palette literals in :root: {', '.join(repeated)}"
            )

for block in re.findall(r"\.nav\s*\{([^}]*)\}", style):
    if re.search(r"\b(position|top|inset|z-index|display|grid-template-columns)\s*:", block):
        errors.append("app/style.css reintroduced global .nav layout; use .archive-nav or an explicit component class")

if '.archive-nav{' not in style and '.archive-nav {' not in style:
    errors.append("app/style.css must own archive sidebar layout through .archive-nav")

home = HOME.read_text(encoding='utf-8', errors='ignore') if HOME.exists() else ""
if 'id="archive-explorer"' in home:
    if 'class="archive-nav"' not in home:
        errors.append("homepage archive explorer must use class=\"archive-nav\"")
    if re.search(r'<aside\s+class=["\'][^"\']*\bnav\b[^"\']*["\']', home):
        classes = re.findall(r'<aside\s+class=["\']([^"\']+)["\']', home)
        for value in classes:
            if "nav" in value.split():
                errors.append("homepage archive explorer still uses standalone legacy .nav class")

for selector, props in RISKY_GLOBAL.items():
    matches = re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", style)
    if len(matches) > 1:
        warnings.append(f"{selector} has {len(matches)} global rule blocks in app/style.css")
    for block in matches:
        if any(re.search(rf"\b{re.escape(prop)}\s*:", block) for prop in props):
            warnings.append(f"global {selector} still controls layout; consider namespacing when next touched")

html_files = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
for path in html_files:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "app/style.css" not in text and "../app/style.css" not in text and "../../app/style.css" not in text:
        continue
    classes = re.findall(r'class=["\']([^"\']+)["\']', text)
    uses_standalone_legacy_nav = any("nav" in value.split() for value in classes)
    if uses_standalone_legacy_nav:
        protected = "reader.css" in text or "layout-guard.css" in text or "page-nav" in text
        if not protected:
            errors.append(f"{path.relative_to(ROOT)} uses legacy .nav with shared app CSS but no reader/layout guard")

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