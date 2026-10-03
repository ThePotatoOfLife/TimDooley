#!/usr/bin/env python3
"""Detect CSS namespace regressions across the shared site system and archive explorer.

Static readers use site-system.css directly. app/style.css is reserved for the
interactive Explore archive and must not reintroduce generic structural classes.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "app" / "style.css"
SITE_SYSTEM = ROOT / "app" / "site-system.css"
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
CANONICAL_TOKEN_LITERALS = ("#070707", "#f4f0e5", "#d8b56b", "#302d29", "#0d0d0d")
RETIRED_GREEN_MARKERS = ("--site-green", "var(--site-green", "--green:", "#b8dc82", "#a8ce72")

RISKY_GLOBAL = {
    ".grid": ("grid-template-columns", "position", "top"),
    ".section": ("position", "top", "z-index"),
    ".record": ("position", "top", "z-index"),
    ".status": ("position", "top", "z-index"),
}

errors = []
warnings = []


style = STYLE.read_text(encoding='utf-8') if STYLE.exists() else ""

# One foundation only: site-system.css owns :root and the bare body selector.
# Floor/room/component styles may scope variables under their own root class.
for css_path in sorted((ROOT / "app").glob("*.css")):
    if css_path == SITE_SYSTEM:
        continue
    css_text = css_path.read_text(encoding="utf-8", errors="ignore")
    if re.search(r":root\s*\{", css_text, flags=re.I):
        errors.append(f"{css_path.relative_to(ROOT)} must not define :root; scope room/floor variables to the component root")
    if re.search(r"(?m)(^|\})\s*body\s*\{", css_text, flags=re.I):
        errors.append(f"{css_path.relative_to(ROOT)} must not define bare body styles; site-system.css owns the document foundation")
    for marker in RETIRED_GREEN_MARKERS:
        if marker.casefold() in css_text.casefold():
            errors.append(f"{css_path.relative_to(ROOT)} still contains retired green-theme marker: {marker}")


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
    if matches:
        errors.append(f"app/style.css still defines retired generic archive selector {selector}; use archive-* classes")

html_files = [
    p for p in ROOT.rglob("*.html")
    if ".git" not in p.parts and "archive" not in p.parts and "docs" not in p.parts
]
for path in html_files:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "var(--site-green" in text or "--site-green" in text:
        errors.append(f"{path.relative_to(ROOT)} still references retired --site-green")

EXPLORE_PAGE = ROOT / "explore" / "index.html"
for path in html_files:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "app/style.css" in text and path != EXPLORE_PAGE:
        errors.append(
            f"{path.relative_to(ROOT)} loads app/style.css; archive application CSS is owned only by explore/index.html"
        )

# Realm readability/fidelity contract: background art may remain expressive, but
# ordinary text surfaces must not rely on text-shadow alone for legibility.
site_system_text = SITE_SYSTEM.read_text(encoding="utf-8", errors="ignore") if SITE_SYSTEM.exists() else ""
elevator_path = ROOT / "app" / "site-elevator.css"
elevator_text = elevator_path.read_text(encoding="utf-8", errors="ignore") if elevator_path.exists() else ""
for marker in (
    "--site-pane-soft:",
    "--site-pane-paper:",
    "html[data-site-floor] .page > :where(section,article,aside,details)",
    ".surface-pane--paper",
    ".surface-clear",
):
    if marker not in site_system_text:
        errors.append(f"realm readability contract missing from site-system.css: {marker}")
if "backdrop-filter:" in site_system_text:
    warnings.append("site-system.css uses backdrop-filter; prefer opaque/translucent panes that preserve realm sharpness")
if "--site-realm-art-size:max(1086px,100vw)" not in elevator_text.replace(" ", ""):
    errors.append("site-elevator.css realm scale contract drifted away from native-source floor")
if "filter:saturate(1.06) contrast(1.045)" not in elevator_text:
    errors.append("site-elevator.css missing realm edge-separation fidelity filter")

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
