#!/usr/bin/env python3
"""Audit the files that can actually participate in the GitHub Pages surface.

The scope intentionally mirrors ``scripts/build_site.py``. Historical/archive,
tooling and build-only trees are useful repository strata but are not deployed
public assets and therefore must not create false web-integrity failures.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
warnings: list[str] = []

# Keep this aligned with build_site.py::EXCLUDE plus repository-only archives.
EXCLUDED_PARTS = {
    ".git",
    ".github",
    "_site",
    "node_modules",
    "vendor",
    "__pycache__",
    "components",
    "scripts",
    "archive",
}


def is_public_source(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return not any(part in EXCLUDED_PARTS for part in rel.parts)


html_files = sorted(p for p in ROOT.rglob("*.html") if is_public_source(p))
css_files = sorted(p for p in ROOT.rglob("*.css") if is_public_source(p))
js_files = sorted(p for p in ROOT.rglob("*.js") if is_public_source(p))

attr_re = re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']", re.I)
css_url_re = re.compile(r"url\(\s*([\"']?)([^\"')]+)\1\s*\)", re.I)
# Static import() is resolved relative to the module file. Browser fetch() paths
# are normally document/base-URL relative and cannot be checked from JS location.
js_import_re = re.compile(r"\bimport\s*\(\s*[\"']([^\"']+)[\"']\s*\)", re.I)
external = (
    "http://",
    "https://",
    "//",
    "mailto:",
    "tel:",
    "javascript:",
    "data:",
    "blob:",
)


def local(raw: str) -> str | None:
    raw = raw.split("#", 1)[0].split("?", 1)[0].strip()
    return None if not raw or raw.startswith(external) or raw.startswith(("${", "<", "`")) else raw


def check(source: Path, raw: str, label: str) -> None:
    target = local(raw)
    if not target:
        return
    # This is a GitHub Pages project site (/TimDooley/), so a root-relative path
    # would incorrectly resolve against the github.io domain root.
    if target.startswith("/"):
        errors.append(f"{source.relative_to(ROOT)}: root-relative reference -> {raw}")
        return

    p = (source.parent / target).resolve()
    try:
        p.relative_to(ROOT.resolve())
    except ValueError:
        warnings.append(f"{source.relative_to(ROOT)}: reference escapes repository -> {raw}")
        return

    if not p.exists():
        errors.append(f"{source.relative_to(ROOT)}: broken {label} -> {target}")


for page in html_files:
    text = page.read_text(encoding="utf-8", errors="replace")
    for raw in attr_re.findall(text):
        check(page, raw, "HTML reference")

for css in css_files:
    text = css.read_text(encoding="utf-8", errors="replace")
    for _, raw in css_url_re.findall(text):
        check(css, raw, "CSS asset")

for js in js_files:
    text = js.read_text(encoding="utf-8", errors="replace")
    for raw in js_import_re.findall(text):
        check(js, raw, "JavaScript import")

if not (ROOT / "index.html").exists():
    errors.append("Missing index.html public Door")
if not (ROOT / "app" / "app.js").exists():
    errors.append("Missing app/app.js archive explorer entry point")
if not (ROOT / "app" / "style.css").exists():
    errors.append("Missing app/style.css primary site stylesheet")

print("Public application root: /TimDooley/")
print(f"HTML pages audited: {len(html_files)}")
print(f"CSS files audited: {len(css_files)}")
print(f"JS files audited: {len(js_files)}")
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")
for item in errors:
    print("ERROR:", item)
for item in warnings:
    print("WARNING:", item)

sys.exit(1 if errors else 0)
