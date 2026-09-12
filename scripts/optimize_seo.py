#!/usr/bin/env python3
"""Normalize and audit SEO metadata across the built Potato of Life site.

The source archive mixes hand-written readers with several generated products.
This final build pass is intentionally conservative: it preserves curated SEO
metadata, fills only missing crawl/share metadata, strengthens internal links to
canonical records, deduplicates segmented sitemaps, and adds trustworthy
``lastmod`` values when Git history can identify the source owner.
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_URL = os.environ.get("SITE_BASE_URL", "https://thepotatooflife.github.io/TimDooley").rstrip("/")
SITE_NAME = "The Potato of Life"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ET.register_namespace("", SITEMAP_NS)

TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
P_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.I | re.S)
META_RE = re.compile(r"<meta\b[^>]*>", re.I)
LINK_RE = re.compile(r"<link\b[^>]*>", re.I)
ATTR_RE = re.compile(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", re.I | re.S)
SCRIPT_LD_RE = re.compile(r"<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", re.I | re.S)
CODE_RE = re.compile(r"<code>([^<]+)</code>", re.I)
TAG_RE = re.compile(r"<[^>]+>")


def attrs(tag: str) -> dict[str, str]:
    return {m.group(1).lower(): html.unescape(m.group(3)).strip() for m in ATTR_RE.finditer(tag)}


def clean_text(fragment: str) -> str:
    return " ".join(html.unescape(TAG_RE.sub(" ", fragment)).split())


def clip(value: str, limit: int) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    cut = value[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return (cut or value[:limit]).rstrip() + "…"


def find_meta(text: str, *, name: str | None = None, prop: str | None = None) -> str | None:
    for tag in META_RE.findall(text):
        a = attrs(tag)
        if name is not None and a.get("name", "").lower() == name.lower():
            return a.get("content", "")
        if prop is not None and a.get("property", "").lower() == prop.lower():
            return a.get("content", "")
    return None


def find_link(text: str, rel: str) -> str | None:
    wanted = rel.lower()
    for tag in LINK_RE.findall(text):
        a = attrs(tag)
        if wanted in {part.lower() for part in a.get("rel", "").split()}:
            return a.get("href", "")
    return None


def page_url(page: Path) -> str:
    rel = page.parent.relative_to(OUT)
    return BASE_URL + "/" if rel == Path(".") else f"{BASE_URL}/{rel.as_posix().strip('/')}/"


def page_title(text: str, page: Path) -> str:
    for regex in (TITLE_RE, H1_RE):
        match = regex.search(text)
        if match:
            value = clean_text(match.group(1))
            if value:
                return value
    rel = page.parent.relative_to(OUT)
    return "The Potato of Life — Tim Dooley Archive" if rel == Path(".") else " ".join(part.replace("-", " ").title() for part in rel.parts)


def page_description(text: str, title: str) -> str:
    existing = find_meta(text, name="description") or find_meta(text, prop="og:description")
    if existing and len(existing.strip()) >= 40:
        return " ".join(existing.split())
    for match in P_RE.finditer(text):
        candidate = clean_text(match.group(1))
        if len(candidate) >= 60:
            return clip(candidate, 165)
    return clip(f"Explore {title} in the {SITE_NAME} archive, with connected records, chronology, sources, evidence and related context.", 165)


def strip_site_suffix(title: str) -> str:
    for suffix in (" | The Potato of Life", " — The Potato of Life"):
        if title.endswith(suffix):
            return title[: -len(suffix)].strip()
    return title


def basic_webpage_schema(title: str, description: str, canonical: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "@id": canonical + "#webpage",
        "url": canonical,
        "name": strip_site_suffix(title),
        "description": clip(description, 300),
        "inLanguage": "en",
        "isAccessibleForFree": True,
        "isPartOf": {"@type": "WebSite", "@id": BASE_URL + "/#website", "url": BASE_URL + "/", "name": SITE_NAME},
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def inject_metadata(text: str, page: Path) -> tuple[str, int]:
    if "</head>" not in text.lower():
        return text, 0
    canonical = find_link(text, "canonical") or page_url(page)
    title = page_title(text, page)
    description = page_description(text, title)
    display_title = strip_site_suffix(title)
    added: list[str] = []
    if not find_meta(text, name="description"):
        added.append(f'<meta name="description" content="{html.escape(clip(description, 165), quote=True)}">')
    if not find_meta(text, name="robots"):
        added.append('<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">')
    if not find_link(text, "canonical"):
        added.append(f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">')
    if not find_link(text, "sitemap"):
        added.append(f'<link rel="sitemap" type="application/xml" href="{BASE_URL}/sitemap-index.xml">')
    social = {
        "og:type": "website" if page == OUT / "index.html" else "article",
        "og:site_name": SITE_NAME,
        "og:locale": "en_US",
        "og:title": display_title,
        "og:description": clip(description, 200),
        "og:url": canonical,
    }
    for prop, value in social.items():
        if find_meta(text, prop=prop) is None:
            added.append(f'<meta property="{prop}" content="{html.escape(value, quote=True)}">')
    twitter = {"twitter:card": "summary", "twitter:title": display_title, "twitter:description": clip(description, 200)}
    for name, value in twitter.items():
        if find_meta(text, name=name) is None:
            added.append(f'<meta name="{name}" content="{html.escape(value, quote=True)}">')
    if not SCRIPT_LD_RE.search(text):
        added.append(f'<script type="application/ld+json">{basic_webpage_schema(title, description, canonical)}</script>')
    if not re.search(r"<html\b[^>]*\blang=", text, re.I):
        text = re.sub(r"<html\b", '<html lang="en"', text, count=1, flags=re.I)
    if added:
        text = re.sub(r"</head>", "\n" + "\n".join(added) + "\n</head>", text, count=1, flags=re.I)
    return text, len(added)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-") or "item"


def core_record_routes() -> dict[str, str]:
    path = ROOT / "knowledge" / "indexes" / "core-index.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    routes = {}
    for record in data.get("records", []):
        if isinstance(record, dict) and record.get("id") and record.get("path"):
            routes[str(record["path"])] = f"{BASE_URL}/records/{slug(record['id'])}/"
    return routes


def link_known_record_paths(text: str, routes: dict[str, str]) -> tuple[str, int]:
    """Link only exact deployed knowledge/data code labels to existing owners."""
    linked = 0
    def replace(match: re.Match[str]) -> str:
        nonlocal linked
        raw = html.unescape(match.group(1)).strip()
        if not raw.startswith(("knowledge/", "data/")) or not (OUT / raw).is_file():
            return match.group(0)
        if re.search(r"<a\b[^>]*>\s*$", text[max(0, match.start() - 180):match.start()], re.I):
            return match.group(0)
        href = routes.get(raw, f"{BASE_URL}/{quote(raw, safe='/._-')}")
        linked += 1
        return f'<a href="{html.escape(href, quote=True)}">{match.group(0)}</a>'
    return CODE_RE.sub(replace, text), linked


def git_lastmod_map() -> dict[str, str]:
    try:
        result = subprocess.run(["git", "log", "--format=@@%cs", "--name-only", "--diff-filter=ACMR"], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)
    except Exception:
        return {}
    if result.returncode != 0:
        return {}
    dates: dict[str, str] = {}
    current = ""
    for raw in result.stdout.splitlines():
        line = raw.strip()
        if line.startswith("@@"):
            current = line[2:]
        elif line and current and line not in dates:
            dates[line] = current
    return dates


def question_source_map() -> tuple[dict[str, str], list[str]]:
    by_slug: dict[str, str] = {}
    owners: list[str] = []
    indexes = ROOT / "knowledge" / "indexes"
    for path in sorted(indexes.glob("faq-*.json")):
        rel = path.relative_to(ROOT).as_posix(); owners.append(rel)
        try: data = json.loads(path.read_text(encoding="utf-8"))
        except Exception: continue
        for entry in data.get("entries", []) if isinstance(data, dict) else []:
            if isinstance(entry, dict) and entry.get("id"): by_slug.setdefault(slug(entry["id"]), rel)
    reader = ROOT / "knowledge" / "reader" / "tim-dooley-question-index.json"
    if reader.exists():
        rel = reader.relative_to(ROOT).as_posix(); owners.append(rel)
        try: data = json.loads(reader.read_text(encoding="utf-8"))
        except Exception: data = {}
        for entry in data.get("questions", []) if isinstance(data, dict) else []:
            if isinstance(entry, dict) and entry.get("id"): by_slug.setdefault(slug(entry["id"]), rel)
    return by_slug, owners


def source_date_for_url(url: str, dates: dict[str, str], record_routes: dict[str, str], question_sources: dict[str, str], faq_owners: list[str]) -> str | None:
    if not url.startswith(BASE_URL + "/"):
        return None
    rel = url[len(BASE_URL):].strip("/")
    static = "index.html" if not rel else f"{rel}/index.html"
    if static in dates: return dates[static]
    reverse_records = {route[len(BASE_URL):].strip("/"): source for source, route in record_routes.items()}
    if rel in reverse_records: return dates.get(reverse_records[rel])
    if rel.startswith("topics/"): return dates.get("manifest.json")
    if rel.startswith("context/"): return dates.get("knowledge/indexes/context-graph.json")
    if rel.startswith("questions/"):
        tail = rel.split("/", 1)[1] if "/" in rel else ""
        if tail in question_sources: return dates.get(question_sources[tail])
        available = [dates[p] for p in faq_owners if p in dates]
        return max(available) if available else None
    if rel == "index-a-z":
        available = [dates[p] for p in faq_owners if p in dates]
        return max(available) if available else None
    if rel.startswith("science/"):
        science_dates = [date for path, date in dates.items() if path.startswith("knowledge/science/")]
        return max(science_dates) if science_dates else dates.get("science/index.html")
    return None


def sitemap_children() -> list[Path]:
    index = OUT / "sitemap-index.xml"
    if not index.exists():
        return [OUT / "sitemap.xml"] if (OUT / "sitemap.xml").exists() else []
    try: root = ET.parse(index).getroot()
    except Exception: return []
    children = []
    for node in root.findall(f"{{{SITEMAP_NS}}}sitemap"):
        loc = node.find(f"{{{SITEMAP_NS}}}loc")
        if loc is not None and loc.text and loc.text.startswith(BASE_URL + "/"):
            candidate = OUT / loc.text.rsplit("/", 1)[-1]
            if candidate.exists(): children.append(candidate)
    return children


def optimize_sitemaps(dates: dict[str, str], record_routes: dict[str, str], question_sources: dict[str, str], faq_owners: list[str]) -> tuple[int, int]:
    children = sitemap_children(); seen: set[str] = set(); removed = 0; lastmods = 0; child_max: dict[str, str] = {}
    for path in children:
        try: tree = ET.parse(path)
        except Exception: continue
        root = tree.getroot(); dates_here: list[str] = []
        for node in list(root.findall(f"{{{SITEMAP_NS}}}url")):
            loc = node.find(f"{{{SITEMAP_NS}}}loc")
            if loc is None or not loc.text: continue
            url = loc.text.strip()
            if url in seen:
                root.remove(node); removed += 1; continue
            seen.add(url)
            modified = source_date_for_url(url, dates, record_routes, question_sources, faq_owners)
            if modified:
                lm = node.find(f"{{{SITEMAP_NS}}}lastmod")
                if lm is None: lm = ET.SubElement(node, f"{{{SITEMAP_NS}}}lastmod"); lastmods += 1
                lm.text = modified; dates_here.append(modified)
        if dates_here: child_max[path.name] = max(dates_here)
        tree.write(path, encoding="utf-8", xml_declaration=True)
    index = OUT / "sitemap-index.xml"
    if index.exists() and child_max:
        try:
            tree = ET.parse(index); root = tree.getroot()
            for node in root.findall(f"{{{SITEMAP_NS}}}sitemap"):
                loc = node.find(f"{{{SITEMAP_NS}}}loc")
                if loc is None or not loc.text: continue
                name = loc.text.rsplit("/", 1)[-1]
                if name not in child_max: continue
                lm = node.find(f"{{{SITEMAP_NS}}}lastmod")
                if lm is None: lm = ET.SubElement(node, f"{{{SITEMAP_NS}}}lastmod"); lastmods += 1
                lm.text = child_max[name]
            tree.write(index, encoding="utf-8", xml_declaration=True)
        except Exception: pass
    return removed, lastmods


def audit_pages() -> tuple[list[str], list[str], dict]:
    errors: list[str] = []; warnings: list[str] = []; titles: dict[str, list[str]] = {}; descriptions: dict[str, list[str]] = {}
    pages = sorted(OUT.rglob("index.html")); structured = 0; social = 0
    for page in pages:
        rel = page.relative_to(OUT).as_posix(); text = page.read_text(encoding="utf-8", errors="replace")
        title = page_title(text, page); description = find_meta(text, name="description") or ""; canonical = find_link(text, "canonical") or ""
        if len(title) < 8: errors.append(f"{rel}: missing or weak title")
        if len(description) < 40: errors.append(f"{rel}: missing or weak meta description")
        if not canonical: errors.append(f"{rel}: missing canonical")
        elif not canonical.startswith(BASE_URL + "/"): errors.append(f"{rel}: canonical outside site: {canonical}")
        if find_meta(text, prop="og:title") and find_meta(text, prop="og:description") and find_meta(text, prop="og:url"): social += 1
        else: errors.append(f"{rel}: incomplete Open Graph metadata")
        if SCRIPT_LD_RE.search(text): structured += 1
        else: errors.append(f"{rel}: missing structured data")
        if len(title) > 75: warnings.append(f"{rel}: title is long ({len(title)} chars)")
        if len(description) > 180: warnings.append(f"{rel}: meta description is long ({len(description)} chars)")
        titles.setdefault(title.casefold(), []).append(rel); descriptions.setdefault(description.casefold(), []).append(rel)
    duplicate_titles = [items for items in titles.values() if len(items) > 1]
    duplicate_descriptions = [items for key, items in descriptions.items() if key and len(items) > 1]
    for items in duplicate_titles[:20]: warnings.append("duplicate title: " + ", ".join(items[:6]))
    for items in duplicate_descriptions[:20]: warnings.append("duplicate description: " + ", ".join(items[:6]))
    report = {"pages": len(pages), "pages_with_open_graph": social, "pages_with_structured_data": structured, "duplicate_title_groups": len(duplicate_titles), "duplicate_description_groups": len(duplicate_descriptions), "errors": len(errors), "warnings": len(warnings)}
    return errors, warnings, report


def main() -> None:
    if not OUT.exists(): raise SystemExit("_site does not exist; run the site builders first")
    routes = core_record_routes(); changed_pages = 0; metadata_tags = 0; linked_paths = 0
    for page in sorted(OUT.rglob("index.html")):
        text = page.read_text(encoding="utf-8", errors="replace"); original = text
        text, added = inject_metadata(text, page); text, linked = link_known_record_paths(text, routes)
        metadata_tags += added; linked_paths += linked
        if text != original: page.write_text(text, encoding="utf-8"); changed_pages += 1
    dates = git_lastmod_map(); question_sources, faq_owners = question_source_map()
    duplicates_removed, lastmods_added = optimize_sitemaps(dates, routes, question_sources, faq_owners)
    errors, warnings, report = audit_pages()
    report.update({"changed_pages": changed_pages, "metadata_tags_added": metadata_tags, "canonical_record_links_added": linked_paths, "duplicate_sitemap_urls_removed": duplicates_removed, "sitemap_lastmod_values_added": lastmods_added})
    (OUT / "seo-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if warnings:
        print("SEO warnings:")
        for message in warnings[:80]: print(f"  - {message}")
        if len(warnings) > 80: print(f"  - … {len(warnings) - 80} additional warnings")
    if errors:
        print("SEO errors:")
        for message in errors: print(f"  - {message}")
        sys.exit(1)
    print(f"SEO optimization passed: {report['pages']} HTML pages, {changed_pages} pages normalized, {metadata_tags} metadata tags added, {linked_paths} canonical/source links added, {duplicates_removed} duplicate sitemap URLs removed, {lastmods_added} lastmod values added.")


if __name__ == "__main__":
    main()
