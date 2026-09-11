#!/usr/bin/env python3
"""Audit crawlability, canonical metadata, sitemap integrity and AI/LLM discovery files."""
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://thepotatooflife.github.io/TimDooley/"

errors = []
warnings = []

required_root = [
    "robots.txt",
    "sitemap.xml",
    "llms.txt",
    "llms-full.txt",
    "machine-index.json",
    "manifest.json",
]
for rel in required_root:
    if not (ROOT / rel).exists():
        errors.append(f"missing required machine-discovery file: {rel}")

# robots.txt: allow crawl and advertise canonical sitemap.
robots = (ROOT / "robots.txt").read_text(encoding="utf-8", errors="ignore") if (ROOT / "robots.txt").exists() else ""
if "User-agent: *" not in robots:
    errors.append("robots.txt must include User-agent: *")
if f"Sitemap: {BASE}sitemap.xml" not in robots:
    errors.append("robots.txt must advertise the canonical sitemap URL")
if re.search(r"(?im)^\s*Disallow:\s*/\s*$", robots):
    errors.append("robots.txt blocks the entire public archive")

# Parse sitemap and map public URLs back to source HTML paths.
sitemap_urls = []
if (ROOT / "sitemap.xml").exists():
    try:
        tree = ET.parse(ROOT / "sitemap.xml")
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = [el.text.strip() for el in tree.findall("sm:url/sm:loc", ns) if el.text]
    except Exception as exc:
        errors.append(f"invalid sitemap.xml: {exc}")

if len(sitemap_urls) != len(set(sitemap_urls)):
    errors.append("sitemap.xml contains duplicate URLs")

for url in sitemap_urls:
    if not url.startswith(BASE):
        errors.append(f"sitemap URL outside canonical site: {url}")
        continue
    rel = url[len(BASE):].strip("/")
    page = ROOT / (rel + "/index.html" if rel else "index.html")
    if not page.exists():
        errors.append(f"sitemap URL has no source page: {url} -> {page.relative_to(ROOT)}")

# High-value reader surfaces must remain discoverable and self-canonicalized.
key_pages = [
    "index.html",
    "tim-dooley/index.html",
    "tim-dooley/ontology/index.html",
    "tim-dooley/how-much-is-tim-god/index.html",
    "tim-dooley/public-witness/index.html",
    "timeline/index.html",
    "traditions/bible/index.html",
    "faq/index.html",
    "faq/all/index.html",
    "faq/all/god/index.html",
    "context/index.html",
    "context/source-authority/index.html",
    "corporium/index.html",
    "science/index.html",
    "traditions/vesica/index.html",
    "theology/honor/index.html",
]

for rel in key_pages:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing key reader page: {rel}")
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"<title>[^<]{8,}</title>", text, re.I):
        errors.append(f"{rel}: missing or weak <title>")
    if not re.search(r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']{40,}["\']', text, re.I):
        errors.append(f"{rel}: missing or short meta description")
    canon = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', text, re.I)
    if not canon:
        errors.append(f"{rel}: missing canonical URL")
    elif not canon.group(1).startswith(BASE):
        errors.append(f"{rel}: canonical URL is outside canonical site")
    if "noindex" in text.lower():
        warnings.append(f"{rel}: contains noindex; confirm this is intentional")

# Homepage should point machines toward the compact guide and sitemap.
home = (ROOT / "index.html").read_text(encoding="utf-8", errors="ignore") if (ROOT / "index.html").exists() else ""
if "llms.txt" not in home:
    errors.append("homepage does not link/describe llms.txt")
if "sitemap.xml" not in home:
    warnings.append("homepage does not expose sitemap.xml directly")

# LLM files should orient to one another and the machine index.
llms = (ROOT / "llms.txt").read_text(encoding="utf-8", errors="ignore") if (ROOT / "llms.txt").exists() else ""
for token in ["machine-index.json", "llms-full.txt", "manifest.json", "data/timeline-events.json", "knowledge/indexes/source-index.json"]:
    if token not in llms:
        errors.append(f"llms.txt missing canonical route: {token}")

full = (ROOT / "llms-full.txt").read_text(encoding="utf-8", errors="ignore") if (ROOT / "llms-full.txt").exists() else ""
for token in ["machine-index.json", "body-system-master-atlas.json", "timeline-source-registry.json", "biblical-overlap-atlas.json"]:
    if token not in full:
        errors.append(f"llms-full.txt missing deep route: {token}")

# machine-index JSON must parse and expose canonical machine surfaces.
if (ROOT / "machine-index.json").exists():
    try:
        machine = json.loads((ROOT / "machine-index.json").read_text(encoding="utf-8"))
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

print(f"Machine discoverability check passed: {len(sitemap_urls)} sitemap URLs, {len(key_pages)} key pages audited.")
