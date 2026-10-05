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
PILLAR_READER_PAGES = [
    ROOT / name / "index.html"
    for name in ("history", "life-body", "world-systems", "context")
]
TRADITION_READER_PAGES = [
    ROOT / "traditions" / name / "index.html"
    for name in (
        "bahai",
        "buddhism",
        "chinese-religion",
        "confucianism",
        "daoism",
        "hindu",
        "jainism",
        "shinto",
        "sikhism",
        "zoroastrianism",
    )
]
GOD_CHARACTER_READER_PAGES = [
    ROOT / "religion" / "gods-character" / "index.html",
    ROOT / "religion" / "gods-character" / "tim-powers" / "index.html",
    ROOT / "religion" / "gods-character" / "divine-tensions" / "index.html",
    ROOT / "religion" / "gods-character" / "divine-functions" / "index.html",
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


# Root-level browser assets are retired. Active CSS/JS must live under a scoped owner.
for stray in sorted(ROOT.iterdir()):
    if stray.is_file() and stray.suffix.lower() in {".css", ".js"}:
        errors.append(
            f"root-level browser asset is not allowed: {stray.name}; move it under its owning module"
        )

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

reader_path = ROOT / "app" / "reader.css"
reader_text = reader_path.read_text(encoding="utf-8", errors="ignore") if reader_path.exists() else ""
if re.search(r"\.page-nav\s+a\s*\{", reader_text) or re.search(r"\.page\s+a\s*,", reader_text):
    errors.append("app/reader.css must not override shared page-nav link color; site-system.css owns the sub-header")

home_page_css = ROOT / "app" / "home-page.css"
home_page_text = home_page_css.read_text(encoding="utf-8", errors="ignore") if home_page_css.exists() else ""
for block in re.findall(r"\.home-nav\s*\{([^}]*)\}", home_page_text, flags=re.I | re.S):
    if re.search(r"\b(background|border|border-radius|box-shadow|padding|min-height|font-size)\s*:", block):
        errors.append("app/home-page.css must not fork the shared page-nav shell; Home may only add local spacing/placement")

home = HOME.read_text(encoding='utf-8', errors='ignore') if HOME.exists() else ""

tim_profile = ROOT / "tim-dooley" / "index.html"
tim_profile_text = tim_profile.read_text(encoding="utf-8", errors="ignore") if tim_profile.exists() else ""
if re.search(r"<style\b", tim_profile_text, flags=re.I):
    errors.append("tim-dooley/index.html must keep structural styling in app/tim-dooley.css, not an inline <style> block")
if "app/tim-dooley.css" not in tim_profile_text and "../app/tim-dooley.css" not in tim_profile_text:
    errors.append("tim-dooley/index.html must load its owned app/tim-dooley.css stylesheet")
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



# Top-level pillar readers share cards, chains and pane rhythm through one scoped
# stylesheet; specialized components remain namespaced beneath .pillar-reader.
pillar_css = ROOT / "app" / "pillar-reader.css"
if not pillar_css.exists():
    errors.append("app/pillar-reader.css is missing")
else:
    pillar_text = pillar_css.read_text(encoding="utf-8", errors="ignore")
    for marker in (
        ".pillar-reader :is(.grid,.cards)",
        ".pillar-reader .card",
        ".pillar-reader .boundary",
        ".pillar-reader .explorer-shell",
        ".pillar-reader .systems-reader",
        ".pillar-reader .context-purpose",
    ):
        if marker not in pillar_text:
            errors.append(f"pillar-reader.css missing shared family marker: {marker}")

for page in PILLAR_READER_PAGES:
    text = page.read_text(encoding="utf-8", errors="ignore") if page.exists() else ""
    if "pillar-reader.css" not in text:
        errors.append(f"{page.relative_to(ROOT)} missing shared pillar-reader.css")
    if "pillar-reader" not in text:
        errors.append(f"{page.relative_to(ROOT)} missing pillar-reader scope class")
    if 'class="page-header"' not in text:
        errors.append(f"{page.relative_to(ROOT)} missing shared page-header")
    reader_link = re.search(r'href=["\'][^"\']*/reader\.css(?:\?[^"\']*)?["\']', text, flags=re.I)
    pillar_link = re.search(r'href=["\'][^"\']*/pillar-reader\.css(?:\?[^"\']*)?["\']', text, flags=re.I)
    if reader_link and pillar_link and reader_link.start() > pillar_link.start():
        errors.append(f"{page.relative_to(ROOT)} must load reader.css before pillar-reader.css so family styling wins")
    if re.search(r"<style\b", text, flags=re.I):
        errors.append(f"{page.relative_to(ROOT)} drifted back to inline structural CSS")

# Shared tradition-reader family: these pages intentionally share one component
# stylesheet and must not drift back into copied inline layout CSS.
tradition_css = ROOT / "app" / "tradition-reader.css"
if not tradition_css.exists():
    errors.append("app/tradition-reader.css is missing")
else:
    tradition_text = tradition_css.read_text(encoding="utf-8", errors="ignore")
    for marker in (
        ".tradition-reader>.lede",
        ".tradition-reader .grid",
        ".tradition-reader .card",
        ".tradition-reader :is(.timeline,.rail,.stack,.layers,.map)",
    ):
        if marker not in tradition_text:
            errors.append(f"tradition-reader.css missing shared family marker: {marker}")

for page in TRADITION_READER_PAGES:
    text = page.read_text(encoding="utf-8", errors="ignore") if page.exists() else ""
    if "tradition-reader.css" not in text:
        errors.append(f"{page.relative_to(ROOT)} missing shared tradition-reader.css")
    if "tradition-reader" not in text:
        errors.append(f"{page.relative_to(ROOT)} missing tradition-reader scope class")
    if re.search(r"<style\b", text, flags=re.I):
        errors.append(f"{page.relative_to(ROOT)} drifted back to inline structural CSS")


# Gods / Character reader family: one shared visual owner prevents four closely
# related pages from drifting through copied grid/card/rule CSS.
god_character_css = ROOT / "app" / "god-character-reader.css"
if not god_character_css.exists():
    errors.append("app/god-character-reader.css is missing")
else:
    god_character_text = god_character_css.read_text(encoding="utf-8", errors="ignore")
    for marker in (
        ".god-character-reader .grid",
        ".god-character-reader .card",
        ".god-character-reader .rule",
        ".god-character-reader .power-grid",
        ".god-character-reader .character-grid",
    ):
        if marker not in god_character_text:
            errors.append(f"god-character-reader.css missing family marker: {marker}")

for page in GOD_CHARACTER_READER_PAGES:
    text = page.read_text(encoding="utf-8", errors="ignore") if page.exists() else ""
    if "god-character-reader.css" not in text:
        errors.append(f"{page.relative_to(ROOT)} missing shared god-character-reader.css")
    if "god-character-reader" not in text:
        errors.append(f"{page.relative_to(ROOT)} missing god-character-reader scope class")
    if 'class="page-header"' not in text:
        errors.append(f"{page.relative_to(ROOT)} missing shared page-header")
    reader_link = re.search(r'href=["\'][^"\']*/reader\.css(?:\?[^"\']*)?["\']', text, flags=re.I)
    family_link = re.search(r'href=["\'][^"\']*/god-character-reader\.css(?:\?[^"\']*)?["\']', text, flags=re.I)
    if reader_link and family_link and reader_link.start() > family_link.start():
        errors.append(f"{page.relative_to(ROOT)} must load reader.css before god-character-reader.css so family styling wins")
    if re.search(r"<style\b", text, flags=re.I):
        errors.append(f"{page.relative_to(ROOT)} drifted back to inline structural CSS")

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

# Shared sub-header interaction contract: semantic role colors must not outrank
# the universal hover/focus state through !important specificity escalation.
for selector in (
    ".page-nav-home",
    ".page-nav-directory",
    ".page-nav-dwelling",
    ".page-nav-current",
    ".page-nav-room",
):
    for block in re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", site_system_text):
        if "!important" in block:
            errors.append(f"site-system.css {selector} must not use !important; shared page-nav hover/focus owns interaction state")
if ".page-nav > a:hover" not in site_system_text or ".page-nav > a:focus-visible" not in site_system_text:
    errors.append("site-system.css missing canonical page-nav hover/focus interaction state")

# Hall pages are floor-aware pages, not second page compositors. Their full-page
# artwork must be supplied by the canonical body::before renderer only.
for hall_css_name, hall_class in (
    ("potatoes-hall.css", "potatoes-hall-page"),
    ("dogs-hall.css", "dogs-hall-page"),
):
    hall_path = ROOT / "app" / hall_css_name
    hall_text = hall_path.read_text(encoding="utf-8", errors="ignore") if hall_path.exists() else ""
    if re.search(rf"body\.{re.escape(hall_class)}::after\s*\{{", hall_text):
        errors.append(f"{hall_css_name} reintroduced a duplicate fixed Hall page compositor")
    renderer_marker = f"body.{hall_class}::before"
    if renderer_marker not in elevator_text:
        errors.append(f"site-elevator.css missing canonical Hall renderer override: {renderer_marker}")

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
