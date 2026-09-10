#!/usr/bin/env python3
"""Audit source references that participate in the GitHub Pages surface.

The source tree and deployed Pages tree are intentionally not identical. Most
public files are copied by ``scripts/build_site.py``, while discovery routes such
as ``questions/`` and ``index-a-z/`` are generated later by
``scripts/build_discovery.py``. This audit validates source-backed references
strictly without misclassifying those build-generated public routes as missing.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE_BASE = "/TimDooley"
errors: list[str] = []
warnings: list[str] = []

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

# These routes are intentionally absent from the source tree. They are emitted
# by scripts/build_discovery.py during the Pages build and verified separately
# by .github/workflows/pages.yml.
GENERATED_ROUTE_PREFIXES = (
    "faq/",
    "questions/",
    "index-a-z/",
)
GENERATED_ROUTE_FILES = {
    "discovery.json",
    "llms.txt",
    "llms-full.txt",
    "robots.txt",
    "sitemap.xml",
    "sitemap-index.xml",
    "sitemap-questions.xml",
}


def is_public_source(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return not any(part in EXCLUDED_PARTS for part in rel.parts)


html_files = sorted(p for p in ROOT.rglob("*.html") if is_public_source(p))
css_files = sorted(p for p in ROOT.rglob("*.css") if is_public_source(p))
js_files = sorted(p for p in ROOT.rglob("*.js") if is_public_source(p))

attr_re = re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']", re.I)
css_url_re = re.compile(r"url\(\s*([\"']?)([^\"')]+)\1\s*\)", re.I)
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


def resolve_target(source: Path, target: str) -> Path | None:
    if target == SITE_BASE or target == f"{SITE_BASE}/":
        return ROOT
    if target.startswith(f"{SITE_BASE}/"):
        return (ROOT / target[len(SITE_BASE) + 1 :]).resolve()
    if target.startswith("/"):
        return None
    return (source.parent / target).resolve()


def is_generated_public_target(path: Path) -> bool:
    try:
        rel = path.relative_to(ROOT.resolve()).as_posix().rstrip("/")
    except ValueError:
        return False
    if rel in GENERATED_ROUTE_FILES:
        return True
    rel_with_slash = f"{rel}/" if rel else ""
    return any(rel_with_slash.startswith(prefix) for prefix in GENERATED_ROUTE_PREFIXES)


def check(source: Path, raw: str, label: str) -> None:
    target = local(raw)
    if not target:
        return

    p = resolve_target(source, target)
    if p is None:
        errors.append(
            f"{source.relative_to(ROOT)}: unsupported root-relative reference -> {raw}"
        )
        return

    try:
        p.relative_to(ROOT.resolve())
    except ValueError:
        warnings.append(f"{source.relative_to(ROOT)}: reference escapes repository -> {raw}")
        return

    if not p.exists() and not is_generated_public_target(p):
        errors.append(f"{source.relative_to(ROOT)}: broken {label} -> {target}")


def actions_escape(value: str) -> str:
    """Escape values used in GitHub Actions workflow command annotations."""
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def emit_annotation(kind: str, item: str) -> None:
    source, separator, message = item.partition(": ")
    if separator and source and message:
        print(f"::{kind} file={actions_escape(source)}::{actions_escape(message)}")
    else:
        print(f"::{kind}::{actions_escape(item)}")


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

print(f"Public application root: {SITE_BASE}/")
print(f"HTML pages audited: {len(html_files)}")
print(f"CSS files audited: {len(css_files)}")
print(f"JS files audited: {len(js_files)}")
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")
for item in errors:
    print("ERROR:", item)
    emit_annotation("error", item)
for item in warnings:
    print("WARNING:", item)
    emit_annotation("warning", item)

sys.exit(1 if errors else 0)
