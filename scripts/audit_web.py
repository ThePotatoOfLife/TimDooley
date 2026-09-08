#!/usr/bin/env python3
"""Audit the static web layer for broken local references.

The audit walks nested HTML pages, resolves paths relative to each page, checks
CSS url() assets, and reports statically resolvable local JavaScript references.
Dynamic routes are deliberately handled by route-contract validation rather than
pretending arbitrary runtime strings are filesystem paths.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
warnings: list[str] = []

html_files = sorted(ROOT.rglob("*.html"))
css_files = sorted(ROOT.rglob("*.css"))
js_files = sorted(ROOT.rglob("*.js"))

attr_re = re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']", re.I)
link_re = re.compile(r'<link\b[^>]*?href=["\']([^"\']+)["\']', re.I | re.S)
style_block_re = re.compile(r"<style\b[^>]*>.*?</style>", re.I | re.S)
inline_style_re = re.compile(r"\sstyle\s*=\s*[\"']", re.I)
css_url_re = re.compile(r"url\(\s*([\"']?)([^\"')]+)\1\s*\)", re.I)
js_static_asset_re = re.compile(r"(?:fetch|import|src|href)\s*\(\s*[\"']([^\"']+)[\"']\s*\)", re.I)
external_prefixes = ("http://", "https://", "//", "mailto:", "javascript:", "data:", "blob:")
canonical = ("index.html", "repository.html", "nations.html", "people.html", "belief.html", "potatoism.html", "hawkins.html")


def local_target(raw: str):
    raw = raw.split("#", 1)[0].split("?", 1)[0].strip()
    if not raw or raw.startswith(external_prefixes) or raw.startswith(("${", "<", "`")):
        return None
    return raw


def check_target(source: Path, raw: str, label: str) -> None:
    target = local_target(raw)
    if not target:
        return
    if target.startswith("/"):
        errors.append(f"{source.relative_to(ROOT)}: root-relative reference breaks GitHub Pages project root -> {raw}")
        return
    p = (source.parent / target).resolve()
    try:
        p.relative_to(ROOT.resolve())
    except ValueError:
        return
    if not p.exists():
        errors.append(f"{source.relative_to(ROOT)}: broken {label} -> {target}")


for page in html_files:
    text = page.read_text(encoding="utf-8", errors="replace")
    styles = link_re.findall(text)
    scripts = re.findall(r'<script\b[^>]*?src=["\']([^"\']+)["\']', text, re.I | re.S)
    if len(styles) != len(set(styles)):
        errors.append(f"{page.relative_to(ROOT)}: duplicate stylesheet link")
    if len(scripts) != len(set(scripts)):
        errors.append(f"{page.relative_to(ROOT)}: duplicate script source")
    if style_block_re.findall(text):
        warnings.append(f"{page.relative_to(ROOT)}: contains embedded <style> block(s)")
    if inline_style_re.search(text):
        warnings.append(f"{page.relative_to(ROOT)}: contains inline style attribute(s)")
    for raw in attr_re.findall(text):
        check_target(page, raw, "HTML reference")


for css in css_files:
    text = css.read_text(encoding="utf-8", errors="replace")
    for _, raw in css_url_re.findall(text):
        check_target(css, raw, "CSS asset")


for js in js_files:
    text = js.read_text(encoding="utf-8", errors="replace")
    for raw in js_static_asset_re.findall(text):
        if raw.startswith(("/", "./", "../")) or "." in Path(raw).name:
            check_target(js, raw, "JavaScript asset")

for page in html_files:
    if page.name in canonical:
        styles = link_re.findall(page.read_text(encoding="utf-8", errors="replace"))
        if "consistency.css" not in styles:
            errors.append(f"{page.relative_to(ROOT)}: missing consistency.css")
        elif styles[-1] != "consistency.css":
            errors.append(f"{page.relative_to(ROOT)}: consistency.css must be the final stylesheet")

if not (ROOT / "site.css").exists():
    errors.append("Missing canonical site.css")
portal = ROOT / "portal.css"
if portal.exists() and '@import url("site.css")' not in portal.read_text(encoding="utf-8", errors="replace"):
    errors.append("portal.css is not a compatibility layer importing site.css")

print("Public application root: /TimDooley/")
print(f"HTML pages audited: {len(html_files)}")
print(f"CSS files audited: {len(css_files)}")
print(f"JS files audited: {len(js_files)}")
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")
for x in errors:
    print("ERROR:", x)
for x in warnings:
    print("WARNING:", x)
sys.exit(1 if errors else 0)
