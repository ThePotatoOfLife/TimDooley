#!/usr/bin/env python3
"""Validate the repository's single-stylesheet contract and shared CSS namespaces."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "app" / "style.css"
HOME = ROOT / "index.html"

RISKY_GLOBAL = {
    ".grid": ("grid-template-columns", "position", "top"),
    ".section": ("position", "top", "z-index"),
    ".record": ("position", "top", "z-index"),
    ".status": ("position", "top", "z-index"),
}

errors = []
warnings = []

css_files = sorted(
    p for p in ROOT.rglob("*.css")
    if ".git" not in p.parts and "_site" not in p.parts
)
expected = [STYLE]
if css_files != expected:
    errors.append(
        "repository must contain exactly one source CSS file: app/style.css; found "
        + ", ".join(str(p.relative_to(ROOT)) for p in css_files)
    )

style = STYLE.read_text(encoding="utf-8") if STYLE.exists() else ""
if not STYLE.exists():
    errors.append("app/style.css is missing")
# Match a real CSS at-rule, not documentation text mentioning the word.
if re.search(r"(?m)^\s*@import\b", style, re.I):
    errors.append("app/style.css must be self-contained; CSS imports are not allowed")

# The original cross-layer collision remains prohibited. Only an actual top-level
# `.nav { ... }` selector is banned; scoped selectors such as `.page > nav.nav`
# are compatibility rules and are intentionally allowed.
for match in re.finditer(r"(?m)(?:^|})\s*\.nav\s*\{([^}]*)\}", style):
    block = match.group(1)
    if re.search(r"\b(position|top|inset|z-index|display|grid-template-columns)\s*:", block):
        errors.append("app/style.css reintroduced global .nav layout; use .archive-nav or an explicit component class")

if ".archive-nav{" not in style and ".archive-nav {" not in style:
    errors.append("app/style.css must own archive sidebar layout through .archive-nav")

home = HOME.read_text(encoding="utf-8", errors="ignore") if HOME.exists() else ""
if 'id="archive-explorer"' in home:
    if 'class="archive-nav"' not in home:
        errors.append('homepage archive explorer must use class="archive-nav"')
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

# Every external stylesheet reference must point at the one canonical file.
html_files = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "_site" not in p.parts]
stylesheet_re = re.compile(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\']', re.I)
for path in html_files:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for href in stylesheet_re.findall(text):
        clean = href.split("?", 1)[0].split("#", 1)[0]
        if not clean.endswith("app/style.css"):
            errors.append(f"{path.relative_to(ROOT)} references non-canonical stylesheet {href}")

# Runtime JavaScript must not manufacture additional CSS resources.
for path in ROOT.rglob("*.js"):
    if ".git" in path.parts or "_site" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for match in re.findall(r"[A-Za-z0-9_./-]+\.css(?:\?[^'\"`\s)]*)?", text):
        if "app/style.css" not in match:
            errors.append(f"{path.relative_to(ROOT)} contains runtime/non-canonical CSS reference {match}")

if warnings:
    print("CSS namespace warnings:")
    for warning in sorted(set(warnings)):
        print(f"  - {warning}")

if errors:
    print("CSS namespace errors:")
    for error in sorted(set(errors)):
        print(f"  - {error}")
    sys.exit(1)

print(f"Single CSS contract passed ({len(html_files)} HTML files scanned; app/style.css is canonical).")
