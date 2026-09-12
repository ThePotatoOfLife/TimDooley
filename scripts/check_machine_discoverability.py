#!/usr/bin/env python3
"""Audit the final crawler/search/LLM discovery surface.

When a built ``_site`` exists this validates the exact deployable artifact;
otherwise it can still provide a smaller source-tree diagnostic for local use.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site" if (ROOT / "_site").exists() else ROOT
BASE = "https://thepotatooflife.github.io/TimDooley/"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

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
    robots_match = re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)', text, re.I)
    noindex = bool(robots_match and "noindex" in robots_match.group(1).lower())
    canon = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', text, re.I)
    if not canon:
        errors.append(f"{rel}: missing canonical URL")
        continue
    canonical = canon.group(1)
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
    description = re.search(r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)', text, re.I)
    if not description or len(description.group(1).strip()) < 40:
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

if warnings:
    print("Machine discoverability warnings:")
    for msg in sorted(set(warnings)):
        print(f"  - {msg}")
if errors:
    print("Machine discoverability errors:")
    for msg in sorted(set(errors)):
        print(f"  - {msg}")
    sys.exit(1)

print(f"Machine discoverability check passed: {len(sitemap_urls)} canonical sitemap URLs, {len(key_pages)} key reader/discovery pages audited.")
