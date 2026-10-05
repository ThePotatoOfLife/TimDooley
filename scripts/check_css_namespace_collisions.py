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

generated_css = ROOT / "app" / "generated-knowledge.css"
generated_css_text = generated_css.read_text(encoding="utf-8", errors="ignore") if generated_css.exists() else ""
if not generated_css_text:
    errors.append("missing app/generated-knowledge.css shared generated-reader owner")

build_script = ROOT / "scripts" / "build_site.py"
build_script_text = build_script.read_text(encoding="utf-8", errors="ignore") if build_script.exists() else ""
if "<style>:root" in build_script_text:
    errors.append("build_site.py must not inline a private generated-reader CSS shell")

try:
    generated_pos = build_script_text.index("generate_machine_index(manifest, core_index, contexts)")
    fingerprint_pos = build_script_text.index("asset_versions = fingerprint_shared_assets()")
    if fingerprint_pos < generated_pos:
        errors.append("build_site.py must fingerprint shared assets after generated pages exist")
except ValueError:
    errors.append("build_site.py missing generated-page/fingerprint build-order markers")
for marker in (
    "app/generated-knowledge.css",
    'class="page page--reading generated-knowledge"',
    'class="page-nav"',
    'class="page-header"',
):
    if marker not in build_script_text:
        errors.append(f"generated knowledge shell missing shared integration marker: {marker}")

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

canonical_visual_tokens = (
    "--site-ink",
    "--site-copy",
    "--site-copy-strong",
    "--site-muted",
    "--site-faint",
    "--site-line",
    "--site-gold",
    "--site-font-sans",
    "--site-font-serif",
    "--site-font-mono",
    "--site-text-micro",
    "--site-text-xs",
    "--site-text-caption",
    "--site-text-sm",
    "--site-text-meta",
    "--site-text-ui",
    "--site-text-body",
    "--site-radius-sm",
    "--site-radius",
    "--site-radius-lg",
    "--site-radius-xl",
    "--site-radius-pill",
)
for css_path in sorted((ROOT / "app").glob("*.css")):
    if css_path.name == "site-system.css":
        continue
    css_text = css_path.read_text(encoding="utf-8", errors="ignore")
    for token in canonical_visual_tokens:
        if re.search(rf"{re.escape(token)}\s*:", css_text):
            errors.append(
                f"{css_path.relative_to(ROOT)} redefines canonical visual token {token}; "
                "consume the site-system token or introduce a module-scoped variable"
            )

for rel, stylesheet, marker in (
    ("north/index.html", "app/north-page.css", "north-page"),
    ("potatoism/index.html", "app/potatoism-page.css", "potatoism-page"),
    ("science/index.html", "app/science-page.css", "science-page"),
):
    page_path = ROOT / rel
    page_text = page_path.read_text(encoding="utf-8", errors="ignore") if page_path.exists() else ""
    if re.search(r"<style\b", page_text, flags=re.I):
        errors.append(f"{rel} must keep structural styling in {stylesheet}, not inline")
    if stylesheet not in page_text and ("../" + stylesheet) not in page_text:
        errors.append(f"{rel} must load {stylesheet}")
    if marker not in page_text:
        errors.append(f"{rel} missing scoped reader marker {marker}")

longform_path = ROOT / "app" / "longform-reader.css"
longform_text = longform_path.read_text(encoding="utf-8", errors="ignore") if longform_path.exists() else ""
if "style.css" in longform_text or "@import" in longform_text:
    errors.append("app/longform-reader.css must consume site-system.css directly and must not import Explore/application CSS")

politics_page = ROOT / "politics" / "index.html"
politics_text = politics_page.read_text(encoding="utf-8", errors="ignore") if politics_page.exists() else ""
if re.search(r"<style\b", politics_text, flags=re.I):
    errors.append("politics/index.html must keep page styling in app/politics-page.css, not inline")
for marker in ("app/site-system.css","app/longform-reader.css","app/politics-page.css","page page--wide politics-page","page-nav world-family","page-header longform-hero"):
    if marker not in politics_text:
        errors.append(f"politics/index.html missing shared-shell marker: {marker}")
if 'class="top"' in politics_text:
    errors.append("politics/index.html must not restore the legacy Explore top bar")

reader_path = ROOT / "app" / "reader.css"
reader_text = reader_path.read_text(encoding="utf-8", errors="ignore") if reader_path.exists() else ""
if re.search(r"\.page-nav\s+a\s*\{", reader_text) or re.search(r"\.page\s+a\s*,", reader_text):
    errors.append("app/reader.css must not override shared page-nav link color; site-system.css owns the sub-header")
for retired_reader_shell in ("a:focus-visible","prefers-reduced-motion",".page .card"):
    if retired_reader_shell in reader_text:
        errors.append(f"app/reader.css must not duplicate universal shell behavior: {retired_reader_shell}")

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

works_page = ROOT / "works" / "index.html"
works_page_text = works_page.read_text(encoding="utf-8", errors="ignore") if works_page.exists() else ""
if re.search(r"<style\b", works_page_text, flags=re.I):
    errors.append("works/index.html must keep structural styling in app/works-page.css, not an inline <style> block")
if "app/works-page.css" not in works_page_text and "../app/works-page.css" not in works_page_text:
    errors.append("works/index.html must load its owned app/works-page.css stylesheet")

timeline_page = ROOT / "timeline" / "index.html"
timeline_page_text = timeline_page.read_text(encoding="utf-8", errors="ignore") if timeline_page.exists() else ""
if re.search(r"<style\b", timeline_page_text, flags=re.I):
    errors.append("timeline/index.html must keep structural styling in app/timeline-page.css, not an inline <style> block")
if "app/timeline-page.css" not in timeline_page_text and "../app/timeline-page.css" not in timeline_page_text:
    errors.append("timeline/index.html must load its owned app/timeline-page.css stylesheet")

religion_page = ROOT / "religion" / "index.html"
religion_page_text = religion_page.read_text(encoding="utf-8", errors="ignore") if religion_page.exists() else ""
if re.search(r"<style\b", religion_page_text, flags=re.I):
    errors.append("religion/index.html must keep structural styling in app/religion-page.css, not an inline <style> block")
if "app/religion-page.css" not in religion_page_text and "../app/religion-page.css" not in religion_page_text:
    errors.append("religion/index.html must load its owned app/religion-page.css stylesheet")

law_page = ROOT / "law" / "index.html"
law_page_text = law_page.read_text(encoding="utf-8", errors="ignore") if law_page.exists() else ""
if re.search(r"<style\b", law_page_text, flags=re.I):
    errors.append("law/index.html must keep structural styling in shared app/world-domain-page.css, not an inline <style> block")
if "app/world-domain-page.css" not in law_page_text and "../app/world-domain-page.css" not in law_page_text:
    errors.append("law/index.html must load shared app/world-domain-page.css")

economy_page = ROOT / "economy" / "index.html"
economy_page_text = economy_page.read_text(encoding="utf-8", errors="ignore") if economy_page.exists() else ""
if re.search(r"<style\b", economy_page_text, flags=re.I):
    errors.append("economy/index.html must use shared app/world-domain-page.css, not an inline <style> block")
if "app/world-domain-page.css" not in economy_page_text and "../app/world-domain-page.css" not in economy_page_text:
    errors.append("economy/index.html must load shared app/world-domain-page.css")
if "world-domain-page" not in law_page_text or "world-domain-page" not in economy_page_text:
    errors.append("Law and Economy must both opt into the shared world-domain-page scope")

for rel, modifier in (
    ("questions/index.html", "questions-page"),
    ("index-a-z/index.html", "az-page"),
    ("paths/index.html", "paths-page"),
):
    page_path = ROOT / rel
    page_text = page_path.read_text(encoding="utf-8", errors="ignore") if page_path.exists() else ""
    if re.search(r"<style\b", page_text, flags=re.I):
        errors.append(f"{rel} must use shared app/discovery-reader.css instead of inline structural CSS")
    if "app/discovery-reader.css" not in page_text or "discovery-page" not in page_text or modifier not in page_text:
        errors.append(f"{rel} missing shared discovery reader ownership/modifier")

for rel, modifier in (
    ("faq/index.html", "faq-home"),
    ("faq/all/index.html", "faq-archive"),
    ("faq/all/god/index.html", "faq-god"),
):
    page_path = ROOT / rel
    page_text = page_path.read_text(encoding="utf-8", errors="ignore") if page_path.exists() else ""
    if re.search(r"<style\b", page_text, flags=re.I):
        errors.append(f"{rel} must use shared app/faq-reader.css instead of inline structural CSS")
    if "app/faq-reader.css" not in page_text or modifier not in page_text:
        errors.append(f"{rel} missing shared FAQ reader ownership/modifier")

for rel in (
    "traditions/islam/index.html",
    "traditions/judaism/index.html",
):
    page_path = ROOT / rel
    page_text = page_path.read_text(encoding="utf-8", errors="ignore") if page_path.exists() else ""
    if re.search(r"<style\b", page_text, flags=re.I):
        errors.append(f"{rel} must use shared app/tradition-reader.css instead of inline structural CSS")
    if "app/tradition-reader.css" not in page_text or "tradition-reader" not in page_text:
        errors.append(f"{rel} missing shared tradition-reader ownership")

for rel, root_selector in (
    ("app/tim-dooley.css", ".tim-page"),
    ("app/works-page.css", ".works-page"),
    ("app/timeline-page.css", '[data-reader-surface="timeline"]'),
    ("app/religion-page.css", ".religion-page"),
):
    css_path = ROOT / rel
    css_text = css_path.read_text(encoding="utf-8", errors="ignore") if css_path.exists() else ""
    for generic in (".lead", ".quiet", ".boundary"):
        if re.search(rf"(?m)(^|\}})\s*{re.escape(generic)}(?:\s|\{{|[.:>#])", css_text):
            errors.append(f"{rel} leaks generic selector {generic}; scope it under {root_selector}")
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

retired_live_assets = (
    "timeline-enhancements.css",
    "law-page.css",
)
live_text_paths = [
    *ROOT.glob("app/*.js"),
    *ROOT.glob("app/*.css"),
    *ROOT.glob("scripts/*.py"),
    *ROOT.glob("scripts/*.mjs"),
]
for path in live_text_paths:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for retired in retired_live_assets:
        if retired in text:
            errors.append(f"{path.relative_to(ROOT)} still references retired live asset {retired}")

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
for expensive_realm_marker in (
    "site-realm-page-pan",
    "animation-timeline:scroll(root block)",
    "filter:saturate(1.06) contrast(1.045)",
    "filter:saturate(.95) contrast(1.05)",
    "transform:translateZ(0)",
):
    if expensive_realm_marker in elevator_text:
        errors.append(f"site-elevator.css reintroduced continuous realm/header compositor work: {expensive_realm_marker}")
if 'html[data-site-floor] .page-header{\n  max-width:none;' not in site_system_text:
    errors.append("realm page headers must share the full Room container width")

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
