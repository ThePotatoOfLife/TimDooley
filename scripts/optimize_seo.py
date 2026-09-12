#!/usr/bin/env python3
"""Normalize, index and audit SEO metadata across the final public site.

The source archive mixes hand-written readers with generated products. This
final build pass is deliberately conservative: it preserves curated content,
fills only missing crawl/share metadata, strengthens canonical links, derives
sitemaps and a machine site index from the deployable artifact, and attaches
source-backed ``lastmod`` values when Git history identifies an owner.
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
PUBLIC_BASE_URL = "https://thepotatooflife.github.io/TimDooley"
BASE_URL = os.environ.get("SITE_BASE_URL", PUBLIC_BASE_URL).rstrip("/")
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

PRIMARY_DOORS = (
    ("tim-dooley", "Tim Dooley"),
    ("religion", "Religion"),
    ("philosophy", "Philosophy"),
    ("science", "Science"),
    ("world-map", "World Map"),
)


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
        values = attrs(tag)
        if name is not None and values.get("name", "").lower() == name.lower():
            return values.get("content", "")
        if prop is not None and values.get("property", "").lower() == prop.lower():
            return values.get("content", "")
    return None


def find_link(text: str, rel: str) -> str | None:
    wanted = rel.lower()
    for tag in LINK_RE.findall(text):
        values = attrs(tag)
        if wanted in {part.lower() for part in values.get("rel", "").split()}:
            return values.get("href", "")
    return None


def has_alternate(text: str, href: str, mime: str) -> bool:
    for tag in LINK_RE.findall(text):
        values = attrs(tag)
        rels = {part.lower() for part in values.get("rel", "").split()}
        if "alternate" in rels and values.get("href") == href and values.get("type", "").lower() == mime.lower():
            return True
    return False


def _relative_to_base(url: str, base: str) -> str | None:
    try:
        parsed = urlparse(url)
        owner = urlparse(base)
    except ValueError:
        return None
    if parsed.scheme.lower() != owner.scheme.lower() or parsed.netloc.lower() != owner.netloc.lower():
        return None
    owner_path = owner.path.rstrip("/")
    candidate_path = parsed.path.rstrip("/")
    if candidate_path == owner_path:
        return ""
    prefix = owner_path + "/"
    if candidate_path.startswith(prefix):
        return candidate_path[len(prefix):].strip("/")
    return None


def canonical_relative_path(url: str) -> str | None:
    for base in dict.fromkeys((BASE_URL, PUBLIC_BASE_URL)):
        relative = _relative_to_base(url, base)
        if relative is not None:
            return relative
    return None


def canonical_is_internal(url: str) -> bool:
    return canonical_relative_path(url) is not None


def page_relative_route(page: Path) -> str:
    rel = page.parent.relative_to(OUT)
    return "" if rel == Path(".") else rel.as_posix().strip("/")


def page_url(page: Path) -> str:
    rel = page_relative_route(page)
    return BASE_URL + "/" if not rel else f"{BASE_URL}/{rel}/"


def canonical_self_matches(page: Path, canonical: str) -> bool:
    return canonical_relative_path(canonical) == page_relative_route(page)


def is_noindex(text: str) -> bool:
    robots = (find_meta(text, name="robots") or "").lower()
    tokens = {token.strip() for token in re.split(r"[,\s]+", robots) if token.strip()}
    return "noindex" in tokens or "none" in tokens


def page_title(text: str, page: Path) -> str:
    for regex in (TITLE_RE, H1_RE):
        match = regex.search(text)
        if match:
            value = clean_text(match.group(1))
            if value:
                return value
    rel = page_relative_route(page)
    return "The Potato of Life — Tim Dooley Archive" if not rel else " ".join(part.replace("-", " ").title() for part in rel.split("/"))


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


def breadcrumb_items(page: Path, title: str) -> list[dict]:
    route = page_relative_route(page)
    items = [{"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": BASE_URL + "/"}]
    if not route:
        return items
    parts = route.split("/")
    for index, part in enumerate(parts, start=2):
        partial = "/".join(parts[: index - 1])
        name = part.replace("-", " ").title()
        items.append({"@type": "ListItem", "position": index, "name": name, "item": f"{BASE_URL}/{partial}/"})
    items[-1]["name"] = strip_site_suffix(title)
    return items


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


def site_graph_schema(page: Path, title: str) -> str:
    canonical = page_url(page)
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": BASE_URL + "/#website", "url": BASE_URL + "/", "name": SITE_NAME, "inLanguage": "en"},
            {"@type": "BreadcrumbList", "@id": canonical + "#breadcrumb", "itemListElement": breadcrumb_items(page, title)},
        ],
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
    if not has_alternate(text, BASE_URL + "/llms.txt", "text/plain"):
        added.append(f'<link rel="alternate" type="text/plain" href="{BASE_URL}/llms.txt" title="LLM retrieval index">')
    if not has_alternate(text, BASE_URL + "/site-index.json", "application/json"):
        added.append(f'<link rel="alternate" type="application/json" href="{BASE_URL}/site-index.json" title="Canonical page index">')
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
    for name, value in {"twitter:card": "summary", "twitter:title": display_title, "twitter:description": clip(description, 200)}.items():
        if find_meta(text, name=name) is None:
            added.append(f'<meta name="{name}" content="{html.escape(value, quote=True)}">')
    if not SCRIPT_LD_RE.search(text):
        added.append(f'<script type="application/ld+json">{basic_webpage_schema(title, description, canonical)}</script>')
    if 'id="site-discovery-schema"' not in text:
        added.append(f'<script id="site-discovery-schema" type="application/ld+json">{site_graph_schema(page, title)}</script>')
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
    return {str(record["path"]): f"{BASE_URL}/records/{slug(record['id'])}/" for record in data.get("records", []) if isinstance(record, dict) and record.get("id") and record.get("path")}


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
    for path in sorted((ROOT / "knowledge" / "indexes").glob("faq-*.json")):
        rel = path.relative_to(ROOT).as_posix()
        owners.append(rel)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for entry in data.get("entries", []) if isinstance(data, dict) else []:
            if isinstance(entry, dict) and entry.get("id"):
                by_slug.setdefault(slug(entry["id"]), rel)
    reader = ROOT / "knowledge" / "reader" / "tim-dooley-question-index.json"
    if reader.exists():
        rel = reader.relative_to(ROOT).as_posix()
        owners.append(rel)
        try:
            data = json.loads(reader.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        for entry in data.get("questions", []) if isinstance(data, dict) else []:
            if isinstance(entry, dict) and entry.get("id"):
                by_slug.setdefault(slug(entry["id"]), rel)
    return by_slug, owners


def source_date_for_url(url: str, dates: dict[str, str], record_routes: dict[str, str], question_sources: dict[str, str], faq_owners: list[str]) -> str | None:
    rel = canonical_relative_path(url)
    if rel is None:
        return None
    static = "index.html" if not rel else f"{rel}/index.html"
    if static in dates:
        return dates[static]
    reverse_records = {canonical_relative_path(route): source for source, route in record_routes.items() if canonical_relative_path(route) is not None}
    if rel in reverse_records:
        return dates.get(reverse_records[rel])
    if rel.startswith("topics/"):
        return dates.get("manifest.json")
    if rel.startswith("context/"):
        return dates.get("knowledge/indexes/context-graph.json")
    if rel.startswith("questions/"):
        tail = rel.split("/", 1)[1] if "/" in rel else ""
        if tail in question_sources:
            return dates.get(question_sources[tail])
        available = [dates[path] for path in faq_owners if path in dates]
        return max(available) if available else None
    if rel == "index-a-z":
        available = [dates[path] for path in faq_owners if path in dates]
        return max(available) if available else None
    if rel.startswith("science/papers/"):
        science_dates = [date for path, date in dates.items() if path.startswith(("docs/", "knowledge/science/"))]
        return max(science_dates) if science_dates else dates.get("science/index.html")
    return None


def classify_page(route: str) -> tuple[str, str]:
    if not route:
        return "home", "home"
    first = route.split("/", 1)[0]
    if route.startswith("questions/") or route == "questions":
        return "question", "questions"
    if route.startswith("records/"):
        return "record", "records"
    if route.startswith("science/papers/"):
        return "science-paper", "science"
    if first in {key for key, _ in PRIMARY_DOORS}:
        return "reader", first
    return "support", first


def build_site_index(dates: dict[str, str], record_routes: dict[str, str], question_sources: dict[str, str], faq_owners: list[str]) -> list[dict]:
    pages: list[dict] = []
    for page in sorted(OUT.rglob("index.html")):
        text = page.read_text(encoding="utf-8", errors="replace")
        if is_noindex(text):
            continue
        canonical = find_link(text, "canonical") or page_url(page)
        if not canonical_is_internal(canonical) or not canonical_self_matches(page, canonical):
            continue
        route = page_relative_route(page)
        kind, section = classify_page(route)
        title = page_title(text, page)
        pages.append({
            "url": canonical,
            "path": "/" + route + ("/" if route else ""),
            "title": strip_site_suffix(title),
            "description": page_description(text, title),
            "type": kind,
            "section": section,
            "lastmod": source_date_for_url(canonical, dates, record_routes, question_sources, faq_owners),
        })
    payload = {
        "schema_version": "1.0.0",
        "generated": datetime.now(timezone.utc).date().isoformat(),
        "canonical_site": BASE_URL + "/",
        "policy": "Only final, indexable, self-canonical HTML pages are listed.",
        "count": len(pages),
        "primary_doors": [{"name": name, "url": f"{BASE_URL}/{key}/"} for key, name in PRIMARY_DOORS],
        "pages": pages,
    }
    (OUT / "site-index.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pages


def write_urlset(path: Path, pages: list[dict]) -> str | None:
    root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    lastmods = []
    for item in pages:
        node = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(node, f"{{{SITEMAP_NS}}}loc").text = item["url"]
        if item.get("lastmod"):
            ET.SubElement(node, f"{{{SITEMAP_NS}}}lastmod").text = item["lastmod"]
            lastmods.append(item["lastmod"])
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return max(lastmods) if lastmods else None


def rebuild_sitemaps(pages: list[dict]) -> dict[str, int]:
    groups = {"sitemap.xml": [], "sitemap-questions.xml": [], "sitemap-records.xml": [], "sitemap-science.xml": []}
    for item in pages:
        if item["type"] == "question":
            groups["sitemap-questions.xml"].append(item)
        elif item["type"] == "record":
            groups["sitemap-records.xml"].append(item)
        elif item["type"] == "science-paper":
            groups["sitemap-science.xml"].append(item)
        else:
            groups["sitemap.xml"].append(item)
    child_lastmod: dict[str, str | None] = {}
    counts: dict[str, int] = {}
    for name, items in groups.items():
        path = OUT / name
        if not items and name != "sitemap.xml":
            path.unlink(missing_ok=True)
            continue
        child_lastmod[name] = write_urlset(path, items)
        counts[name] = len(items)
    index_root = ET.Element(f"{{{SITEMAP_NS}}}sitemapindex")
    for name in groups:
        if name not in counts:
            continue
        node = ET.SubElement(index_root, f"{{{SITEMAP_NS}}}sitemap")
        ET.SubElement(node, f"{{{SITEMAP_NS}}}loc").text = f"{BASE_URL}/{name}"
        if child_lastmod.get(name):
            ET.SubElement(node, f"{{{SITEMAP_NS}}}lastmod").text = child_lastmod[name]
    ET.ElementTree(index_root).write(OUT / "sitemap-index.xml", encoding="utf-8", xml_declaration=True)
    (OUT / "robots.txt").write_text("User-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: *\nAllow: /\n\n" + f"Sitemap: {BASE_URL}/sitemap-index.xml\n", encoding="utf-8")
    return counts


def sitemap_urls() -> tuple[list[str], list[str]]:
    errors, urls = [], []
    index = OUT / "sitemap-index.xml"
    if not index.exists():
        return urls, ["missing sitemap-index.xml"]
    try:
        root = ET.parse(index).getroot()
    except Exception as exc:
        return urls, [f"invalid sitemap-index.xml: {exc}"]
    for node in root.findall(f"{{{SITEMAP_NS}}}sitemap"):
        loc = node.find(f"{{{SITEMAP_NS}}}loc")
        if loc is None or not loc.text or not canonical_is_internal(loc.text.strip()):
            errors.append("sitemap index contains invalid or external child")
            continue
        child = OUT / loc.text.strip().rsplit("/", 1)[-1]
        if not child.exists():
            errors.append(f"sitemap child missing: {child.name}")
            continue
        try:
            child_root = ET.parse(child).getroot()
        except Exception as exc:
            errors.append(f"invalid sitemap child {child.name}: {exc}")
            continue
        for url_node in child_root.findall(f"{{{SITEMAP_NS}}}url"):
            url_loc = url_node.find(f"{{{SITEMAP_NS}}}loc")
            if url_loc is not None and url_loc.text:
                urls.append(url_loc.text.strip())
    return urls, errors


def audit_pages(site_pages: list[dict]) -> tuple[list[str], list[str], dict]:
    errors, warnings = [], []
    titles: dict[str, list[str]] = {}
    descriptions: dict[str, list[str]] = {}
    canonicals: dict[str, list[str]] = {}
    all_pages = sorted(OUT.rglob("index.html"))
    structured = social = 0
    indexable_urls = {item["url"] for item in site_pages}
    for page in all_pages:
        rel = page.relative_to(OUT).as_posix()
        text = page.read_text(encoding="utf-8", errors="replace")
        title = page_title(text, page)
        description = find_meta(text, name="description") or ""
        canonical = find_link(text, "canonical") or ""
        noindex = is_noindex(text)
        if len(title) < 8:
            errors.append(f"{rel}: missing or weak title")
        if len(description) < 40:
            errors.append(f"{rel}: missing or weak meta description")
        if not canonical:
            errors.append(f"{rel}: missing canonical")
        elif not canonical_is_internal(canonical):
            errors.append(f"{rel}: canonical outside site: {canonical}")
        elif not noindex and not canonical_self_matches(page, canonical):
            errors.append(f"{rel}: canonical URL must match the page for indexable pages: {canonical}")
        if find_meta(text, prop="og:title") and find_meta(text, prop="og:description") and find_meta(text, prop="og:url"):
            social += 1
        else:
            errors.append(f"{rel}: incomplete Open Graph metadata")
        if SCRIPT_LD_RE.search(text) and "BreadcrumbList" in text and '"@type":"WebSite"' in text:
            structured += 1
        else:
            errors.append(f"{rel}: incomplete structured data graph")
        if not has_alternate(text, BASE_URL + "/llms.txt", "text/plain"):
            errors.append(f"{rel}: missing llms.txt alternate discovery link")
        if not has_alternate(text, BASE_URL + "/site-index.json", "application/json"):
            errors.append(f"{rel}: missing site-index.json alternate discovery link")
        if len(title) > 75:
            warnings.append(f"{rel}: title is long ({len(title)} chars)")
        if len(description) > 180:
            warnings.append(f"{rel}: meta description is long ({len(description)} chars)")
        if not noindex:
            titles.setdefault(title.casefold(), []).append(rel)
            descriptions.setdefault(description.casefold(), []).append(rel)
            if canonical:
                canonicals.setdefault(canonical, []).append(rel)
    for canonical, items in canonicals.items():
        if len(items) > 1:
            errors.append("duplicate canonical among indexable pages: " + canonical + " -> " + ", ".join(items[:6]))
    duplicate_titles = [items for items in titles.values() if len(items) > 1]
    duplicate_descriptions = [items for key, items in descriptions.items() if key and len(items) > 1]
    for items in duplicate_titles[:30]:
        warnings.append("duplicate title: " + ", ".join(items[:6]))
    for items in duplicate_descriptions[:30]:
        warnings.append("duplicate description: " + ", ".join(items[:6]))
    listed, sitemap_errors = sitemap_urls()
    errors.extend(sitemap_errors)
    if len(listed) != len(set(listed)):
        errors.append("sitemap children contain duplicate URLs")
    listed_set = set(listed)
    missing = sorted(indexable_urls - listed_set)
    extra = sorted(listed_set - indexable_urls)
    if missing:
        errors.append(f"sitemap missing {len(missing)} indexable canonical URLs; first: {missing[:5]}")
    if extra:
        errors.append(f"noindex URLs must not appear in sitemaps; extra canonical URLs: {extra[:5]}")
    report = {
        "pages": len(all_pages), "indexable_pages": len(site_pages), "pages_with_open_graph": social,
        "pages_with_structured_data": structured, "duplicate_title_groups": len(duplicate_titles),
        "duplicate_description_groups": len(duplicate_descriptions), "sitemap_urls": len(listed_set),
        "errors": len(errors), "warnings": len(warnings),
    }
    return errors, warnings, report


def main() -> None:
    if not OUT.exists():
        raise SystemExit("_site does not exist; run the site builders first")
    routes = core_record_routes()
    changed_pages = metadata_tags = linked_paths = 0
    for page in sorted(OUT.rglob("index.html")):
        text = page.read_text(encoding="utf-8", errors="replace")
        original = text
        text, added = inject_metadata(text, page)
        text, linked = link_known_record_paths(text, routes)
        metadata_tags += added
        linked_paths += linked
        if text != original:
            page.write_text(text, encoding="utf-8")
            changed_pages += 1
    dates = git_lastmod_map()
    question_sources, faq_owners = question_source_map()
    site_pages = build_site_index(dates, routes, question_sources, faq_owners)
    sitemap_counts = rebuild_sitemaps(site_pages)
    errors, warnings, report = audit_pages(site_pages)
    report.update({
        "changed_pages": changed_pages, "metadata_tags_added": metadata_tags,
        "canonical_record_links_added": linked_paths, "sitemap_files": sitemap_counts,
        "error_messages": errors, "warning_messages": warnings,
    })
    (OUT / "seo-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if warnings:
        print("SEO warnings:")
        for message in warnings[:80]:
            print(f"  - {message}")
        if len(warnings) > 80:
            print(f"  - … {len(warnings) - 80} additional warnings")
    if errors:
        print("SEO errors:")
        for message in errors:
            print(f"  - {message}")
        sys.exit(1)
    print(f"SEO optimization passed: {report['pages']} HTML pages, {report['indexable_pages']} indexable canonical pages, {changed_pages} pages normalized, {metadata_tags} metadata tags added, {linked_paths} canonical/source links added, {report['sitemap_urls']} URLs indexed across canonical sitemaps.")


if __name__ == "__main__":
    main()
