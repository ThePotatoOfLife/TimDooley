#!/usr/bin/env python3
"""Audit the final crawler/search/LLM discovery surface."""
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


def attrs(tag: str) -> dict[str, str]:
    return {m.group(1).lower(): html.unescape(m.group(3)).strip() for m in ATTR_RE.finditer(tag)}


def meta(text: str, name: str) -> str:
    for tag in TAG_RE.findall(text):
        values = attrs(tag)
        if tag.lower().startswith("<meta") and values.get("name", "").lower() == name.lower():
            return values.get("content", "")
    return ""


def canonical(text: str) -> str:
    for tag in TAG_RE.findall(text):
        values = attrs(tag)
        if tag.lower().startswith("<link") and "canonical" in {x.lower() for x in values.get("rel", "").split()}:
            return values.get("href", "")
    return ""


def page_url(rel: str) -> str:
    if rel == "index.html":
        return BASE
    return BASE + rel[:-len("index.html")]


errors: list[str] = []
warnings: list[str] = []
for rel in ["robots.txt", "sitemap.xml", "sitemap-index.xml", "llms.txt", "llms-full.txt", "discovery.json", "site-index.json", "machine-index.json", "manifest.json"]:
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

sitemap_urls: list[str] = []
index_path = SITE / "sitemap-index.xml"
if index_path.exists():
    try:
        for node in ET.parse(index_path).findall("sm:sitemap", NS):
            loc = node.find("sm:loc", NS)
            if loc is None or not loc.text or not loc.text.startswith(BASE):
                errors.append("sitemap-index.xml contains an invalid child")
                continue
            filename = loc.text.rsplit("/", 1)[-1]
            child = SITE / filename
            if not child.exists():
                errors.append(f"sitemap-index.xml references missing child: {filename}")
                continue
            for url_node in ET.parse(child).findall("sm:url", NS):
                url_loc = url_node.find("sm:loc", NS)
                if url_loc is not None and url_loc.text:
                    sitemap_urls.append(url_loc.text.strip())
    except Exception as exc:
        errors.append(f"invalid sitemap index/child: {exc}")
if len(sitemap_urls) != len(set(sitemap_urls)):
    errors.append("sitemap children contain duplicate URLs")

indexable: set[str] = set()
for path in sorted(SITE.rglob("index.html")):
    rel = path.relative_to(SITE).as_posix()
    text = path.read_text(encoding="utf-8", errors="ignore")
    robots_value = meta(text, "robots").lower()
    noindex = "noindex" in robots_value or "none" in robots_value
    owner = canonical(text)
    own_url = page_url(rel)
    if not owner:
        errors.append(f"{rel}: missing canonical URL")
        continue
    if not owner.startswith(BASE):
        errors.append(f"{rel}: canonical URL is outside canonical site")
        continue
    if noindex:
        if own_url in sitemap_urls:
            errors.append(f"{rel}: noindex URLs must not appear in sitemaps")
    else:
        if owner != own_url:
            errors.append(f"{rel}: canonical URL must match the page for indexable pages")
        indexable.add(owner)

key_pages = ["index.html", "tim-dooley/index.html", "religion/index.html", "philosophy/index.html", "science/index.html", "world-map/index.html", "timeline/index.html", "traditions/bible/index.html", "questions/index.html", "index-a-z/index.html"]
for rel in key_pages:
    path = SITE / rel
    if not path.exists():
        errors.append(f"missing key reader/discovery page: {rel}")
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"<title>[^<]{8,}</title>", text, re.I):
        errors.append(f"{rel}: missing or weak title")
    if len(meta(text, "description")) < 40:
        errors.append(f"{rel}: missing or short meta description")
    for token in ("og:title", "og:description", "og:url", "application/ld+json"):
        if token not in text:
            errors.append(f"{rel}: missing metadata token {token}")

listed = set(sitemap_urls)
if SITE != ROOT:
    for url in sorted(indexable - listed)[:5]:
        errors.append(f"sitemaps miss indexable page: {url}")
    for url in sorted(listed - indexable)[:5]:
        errors.append(f"sitemaps contain non-indexable page: {url}")

llms = (SITE / "llms.txt").read_text(encoding="utf-8", errors="ignore") if (SITE / "llms.txt").exists() else ""
for token in ["Tim Dooley", "Religion", "Philosophy", "Science", "World Map", "site-index.json", "machine-index.json", "llms-full.txt", "sitemap-index.xml"]:
    if token not in llms:
        errors.append(f"llms.txt missing current discovery route/door: {token}")
full = (SITE / "llms-full.txt").read_text(encoding="utf-8", errors="ignore") if (SITE / "llms-full.txt").exists() else ""
for token in ["site-index.json", "machine-index.json", "source-index.json", "timeline-source-registry.json", "body-system-master-atlas.json", "biblical-overlap-atlas.json"]:
    if token not in full:
        errors.append(f"llms-full.txt missing deep route: {token}")

try:
    discovery = json.loads((SITE / "discovery.json").read_text(encoding="utf-8"))
    entrypoints = discovery.get("entrypoints", {})
    for key in ["tim", "religion", "philosophy", "science", "world_map", "site_index", "sitemap_index"]:
        if not entrypoints.get(key):
            errors.append(f"discovery.json missing entrypoints.{key}")
    if len(discovery.get("reader_architecture", {}).get("doors", [])) != 5:
        errors.append("discovery.json must expose exactly five primary reader doors")
except Exception as exc:
    errors.append(f"invalid discovery.json: {exc}")

try:
    site_index = json.loads((SITE / "site-index.json").read_text(encoding="utf-8"))
    pages = site_index.get("pages", [])
    urls = {row.get("url") for row in pages if isinstance(row, dict) and row.get("url")}
    if site_index.get("count") != len(pages):
        errors.append("site-index.json count does not match pages array")
    if SITE != ROOT and urls != indexable:
        errors.append("site-index.json must equal the final indexable canonical page set")
    if len(site_index.get("primary_doors", [])) != 5:
        errors.append("site-index.json must identify the five primary doors")
except Exception as exc:
    errors.append(f"invalid site-index.json: {exc}")

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

report = {"site": "_site" if SITE != ROOT else ".", "sitemap_urls": len(listed), "indexable_pages": len(indexable), "key_pages_audited": len(key_pages), "errors": sorted(set(errors)), "warnings": sorted(set(warnings))}
(ROOT / "machine-discoverability-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if errors:
    print("Machine discoverability errors:")
    for message in report["errors"]:
        print("  -", message)
    sys.exit(1)
print(f"Machine discoverability check passed: {len(listed)} canonical sitemap URLs, {len(key_pages)} key reader/discovery pages audited.")
