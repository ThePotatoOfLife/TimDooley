#!/usr/bin/env python3
"""Audit the final crawler/search/LLM discovery surface.

When a built ``_site`` exists this validates the exact deployable artifact;
otherwise it can still provide a smaller source-tree diagnostic for local use.
"""
from __future__ import annotations

import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site" if (ROOT / "_site").exists() else ROOT
BASE = "https://thepotatooflife.github.io/TimDooley/"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
TAG_RE = re.compile(r"<(?:meta|link)\b[^>]*>", re.I)
ATTR_RE = re.compile(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", re.I | re.S)


def tag_attrs(tag: str) -> dict[str, str]:
    return {m.group(1).lower(): html.unescape(m.group(3)).strip() for m in ATTR_RE.finditer(tag)}


def meta_content(text: str, name: str) -> str | None:
    for tag in TAG_RE.findall(text):
        values = tag_attrs(tag)
        if tag.lower().startswith("<meta") and values.get("name", "").lower() == name.lower():
            return values.get("content", "")
    return None


def canonical_href(text: str) -> str | None:
    for tag in TAG_RE.findall(text):
        values = tag_attrs(tag)
        if tag.lower().startswith("<link") and "canonical" in {part.lower() for part in values.get("rel", "").split()}:
            return values.get("href", "")
    return None


errors: list[str] = []
warnings: list[str] = []

required_root = [
    "robots.txt",
    "sitemap.xml",
    "sitemap-index.xml",
    "llms.txt",
    "llms-full.txt",
    "discovery.json",
    "site-index.json",
    "machine-index.json",
    "manifest.json",
]
for rel in required_root:
    if not (SITE / rel).exists():
        errors.append(f"missing required machine-discovery file: {rel}")

robots = (SITE / "robots.txt").read_text(encoding="utf-8", errors="ignore") if (SITE / "robots.txt").exists() else ""
if "User-agent: *" not in robots or "Allow: /" not in robots:
    errors.append("robots.txt must permit ordinary public crawling")
if "OAI-SearchBot" not in robots:
    errors.append("robots.txt must explicitly permit OAI-SearchBot for ChatGPT Search discovery")
if f"Sitemap: {BASE}sitemap-index.xml" not in robots:
    errors.append("robots.txt must advertise the canonical sitemap index")
if re.search(r"(?im)^\s*Disallow:\s*/\s*$", robots):
    errors.append("robots.txt blocks the public archive")


def local_sitemap_path(url: str) -> Path | None:
    if not url.startswith(BASE):
        return None
    rel = url[len(BASE):].strip("/")
    if not rel or "/" in rel:
        return None
    return SITE / rel


sitemap_urls: list[str] = []
if (SITE / "sitemap-index.xml").exists():
    try:
        index = ET.parse(SITE / "sitemap-index.xml")
        for node in index.findall("sm:sitemap", NS):
            loc = node.find("sm:loc", NS)
            if loc is None or not loc.text:
                errors.append("sitemap-index.xml contains a child without loc")
                continue
            child = local_sitemap_path(loc.text.strip())
            if child is None or not child.exists():
                errors.append(f"sitemap-index.xml references missing/external child: {loc.text.strip()}")
                continue
            tree = ET.parse(child)
            for url_node in tree.findall("sm:url", NS):
                url_loc = url_node.find("sm:loc", NS)
                if url_loc is not None and url_loc.text:
                    sitemap_urls.append(url_loc.text.strip())
    except Exception as exc:
        errors.append(f"invalid sitemap index/child: {exc}")

if len(sitemap_urls) != len(set(sitemap_urls)):
    errors.append("sitemap children contain duplicate URLs")

key_pages = [
    "index.html",
    "tim-dooley/index.html",
    "religion/index.html",
    "philosophy/index.html",
    "science/index.html",
    "world-map/index.html",
    "timeline/index.html",
    "traditions/bible/index.html",
    "questions/index.html",
    "index-a-z/index.html",
]

indexable_canonicals: set[str] = set()
for page in sorted(SITE.rglob("index.html")):
    rel = page.relative_to(SITE).as_posix()
    text = page.read_text(encoding="utf-8", errors="ignore")
    robots_value = meta_content(text, "robots") or ""
    noindex = "noindex" in robots_value.lower() or "none" in robots_value.lower()
    canonical = canonical_href(text)
    if not canonical:
        errors.append(f"{rel}: missing canonical URL")
        continue
    if not canonical.startswith(BASE):
        errors.append(f"{rel}: canonical URL is outside canonical site")
        continue
    route = "" if rel == "index.html" else rel[:-len("/index.html")]
    expected = BASE if not route else BASE + route + "/"
    if not noindex:
        if canonical != expected:
            errors.append(f"{rel}: canonical URL must match the page for indexable pages")
        indexable_canonicals.add(canonical)
    elif canonical in sitemap_urls:
        errors.append(f"{rel}: noindex URLs must not appear in sitemaps")

for rel in key_pages:
    path = SITE / rel
    if not path.exists():
        errors.append(f"missing key reader/discovery page: {rel}")
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"<title>[^<]{8,}</title>", text, re.I):
        errors.append(f"{rel}: missing or weak <title>")
    description = meta_content(text, "description") or ""
    if len(description.strip()) < 40:
        errors.append(f"{rel}: missing or short meta description")
    for token in ("og:title", "og:description", "og:url", "application/ld+json"):
        if token not in text:
            errors.append(f"{rel}: missing metadata token {token}")

listed = set(sitemap_urls)
if SITE != ROOT and listed != indexable_canonicals:
    missing = sorted(indexable_canonicals - listed)
    extra = sorted(listed - indexable_canonicals)
    if missing:
        errors.append(f"sitemaps miss {len(missing)} indexable pages; first: {missing[:5]}")
    if extra:
        errors.append(f"sitemaps contain {len(extra)} non-indexable pages; first: {extra[:5]}")

llms = (SITE / "llms.txt").read_text(encoding="utf-8", errors="ignore") if (SITE / "llms.txt").exists() else ""
for token in ["Tim Dooley", "Religion", "Philosophy", "Science", "World Map", "site-index.json", "machine-index.json", "llms-full.txt", "sitemap-index.xml"]:
    if token not in llms:
        errors.append(f"llms.txt missing current discovery route/door: {token}")

full = (SITE / "llms-full.txt").read_text(encoding="utf-8", errors="ignore") if (SITE / "llms-full.txt").exists() else ""
for token in ["site-index.json", "machine-index.json", "source-index.json", "timeline-source-registry.json", "body-system-master-atlas.json", "biblical-overlap-atlas.json"]:
    if token not in full:
        errors.append(f"llms-full.txt missing deep route: {token}")

if (SITE / "discovery.json").exists():
    try:
        discovery = json.loads((SITE / "discovery.json").read_text(encoding="utf-8"))
        entrypoints = discovery.get("entrypoints", {})
        for key in ["tim", "religion", "philosophy", "science", "world_map", "site_index", "sitemap_index"]:
            if not entrypoints.get(key):
                errors.append(f"discovery.json missing entrypoints.{key}")
        doors = discovery.get("reader_architecture", {}).get("doors", [])
        if len(doors) != 5:
            errors.append("discovery.json must expose exactly five primary reader doors")
    except Exception as exc:
        errors.append(f"invalid discovery.json: {exc}")

if (SITE / "site-index.json").exists():
    try:
        site_index = json.loads((SITE / "site-index.json").read_text(encoding="utf-8"))
        pages = site_index.get("pages", [])
        urls = {row.get("url") for row in pages if isinstance(row, dict) and row.get("url")}
        if site_index.get("count") != len(pages):
            errors.append("site-index.json count does not match pages array")
        if SITE != ROOT and urls != indexable_canonicals:
            errors.append("site-index.json must equal the final indexable canonical page set")
        if len(site_index.get("primary_doors", [])) != 5:
            errors.append("site-index.json must identify the five primary doors")
    except Exception as exc:
        errors.append(f"invalid site-index.json: {exc}")

if (SITE / "machine-index.json").exists():
    try:
        machine = json.loads((SITE / "machine-index.json").read_text(encoding="utf-8"))
        surfaces = machine.get("machine_surfaces", {})
        for key in ["llms", "llms_full", "manifest", "core_index", "source_index", "sitemap", "robots"]:
            if key not in surfaces:
                errors.append(f"machine-index.json missing machine_surfaces.{key}")
        if not machine.get("canonical_branches"):
            errors.append("machine-index.json has no canonical_branches")
        if not machine.get("evidence_classes"):
            errors.append("machine-index.json has no evidence_classes")
    except Exception as exc:
        errors.append(f"invalid machine-index.json: {exc}")

report = {
    "site": str(SITE.relative_to(ROOT)) if SITE != ROOT else ".",
    "sitemap_urls": len(set(sitemap_urls)),
    "indexable_pages": len(indexable_canonicals),
    "key_pages_audited": len(key_pages),
    "errors": sorted(set(errors)),
    "warnings": sorted(set(warnings)),
}
(ROOT / "machine-discoverability-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if warnings:
    print("Machine discoverability warnings:")
    for msg in report["warnings"]:
        print(f"  - {msg}")
if errors:
    print("Machine discoverability errors:")
    for msg in report["errors"]:
        print(f"  - {msg}")
    sys.exit(1)

print(f"Machine discoverability check passed: {len(sitemap_urls)} canonical sitemap URLs, {len(key_pages)} key reader/discovery pages audited.")
