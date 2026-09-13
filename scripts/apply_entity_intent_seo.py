#!/usr/bin/env python3
"""Apply entity-and-intent SEO to the final built site.

This pass runs after the conservative content builders and before final sitemap
projection. It does not create public content pages or alter canonical URLs. It
classifies each final indexable page, projects page-appropriate JSON-LD,
synchronizes search/social metadata, and adds a small explicit related-context
block when the page does not already provide equivalent contextual navigation.
"""
from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from seo_strategy import classify_route, metadata_for, related_routes, schema_profile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_URL = "https://thepotatooflife.github.io/TimDooley"
SITE_NAME = "The Potato of Life"

TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
META_RE = re.compile(r"<meta\b[^>]*>", re.I)
LINK_RE = re.compile(r"<link\b[^>]*>", re.I)
ATTR_RE = re.compile(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
LD_SCRIPT_RE = re.compile(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)


def attrs(tag: str) -> dict[str, str]:
    return {m.group(1).lower(): html.unescape(m.group(3)).strip() for m in ATTR_RE.finditer(tag)}


def clean_text(value: str) -> str:
    return " ".join(html.unescape(TAG_RE.sub(" ", value)).split())


def clip(value: str, limit: int) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    cut = value[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return (cut or value[:limit]).rstrip() + "…"


def route_for(page: Path) -> str:
    rel = page.parent.relative_to(OUT)
    return "" if rel == Path(".") else rel.as_posix().strip("/")


def page_url(route: str) -> str:
    return BASE_URL + "/" if not route else f"{BASE_URL}/{route}/"


def meta_value(text: str, *, name: str | None = None, prop: str | None = None) -> str:
    for tag in META_RE.findall(text):
        values = attrs(tag)
        if name is not None and values.get("name", "").lower() == name.lower():
            return values.get("content", "")
        if prop is not None and values.get("property", "").lower() == prop.lower():
            return values.get("content", "")
    return ""


def canonical(text: str, route: str) -> str:
    for tag in LINK_RE.findall(text):
        values = attrs(tag)
        rels = {part.lower() for part in values.get("rel", "").split()}
        if "canonical" in rels and values.get("href"):
            return values["href"]
    return page_url(route)


def is_noindex(text: str) -> bool:
    robots = meta_value(text, name="robots").lower()
    tokens = {token for token in re.split(r"[,\s]+", robots) if token}
    return "noindex" in tokens or "none" in tokens


def title_value(text: str) -> str:
    match = TITLE_RE.search(text)
    return clean_text(match.group(1)) if match else ""


def replace_title(text: str, value: str) -> str:
    escaped = html.escape(value, quote=False)
    if TITLE_RE.search(text):
        return TITLE_RE.sub(f"<title>{escaped}</title>", text, count=1)
    return re.sub(r"</head>", f"<title>{escaped}</title>\n</head>", text, count=1, flags=re.I)


def replace_meta(text: str, *, key: str, value: str, property_key: bool = False) -> str:
    selector = "property" if property_key else "name"
    escaped = html.escape(value, quote=True)
    pattern = re.compile(
        rf"<meta\b(?=[^>]*\b{selector}=[\"']{re.escape(key)}[\"'])[^>]*>",
        re.I,
    )
    replacement = f'<meta {selector}="{key}" content="{escaped}">'
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return re.sub(r"</head>", replacement + "\n</head>", text, count=1, flags=re.I)


def search_description(route: str, kind: str, value: str) -> str:
    """Keep metadata concise and distinguish archive records from paper views."""
    value = " ".join(value.split()).strip()
    if kind == "record" and value and not value.casefold().startswith("canonical archive record:"):
        value = "Canonical archive record: " + value
    elif kind == "science-paper" and value and not value.casefold().startswith("research paper:"):
        value = "Research paper: " + value
    return clip(value, 170)


def label_for_route(route: str) -> str:
    labels = {
        "tim-dooley": "Tim Dooley",
        "timeline": "Timeline",
        "context/source-authority": "Sources & evidence",
        "tim-dooley/evidence": "Evidence",
        "tim-dooley/public-witness": "Public witness",
        "tim-dooley/biblical-case": "Biblical case",
        "traditions/bible": "Bible research",
        "religion": "Religion",
        "philosophy": "Philosophy",
        "science": "Science",
        "science/research-map": "Science research map",
        "north": "North",
        "world": "World",
        "world-map": "World Map",
        "world-systems": "World systems",
        "politics": "Politics",
    }
    if route in labels:
        return labels[route]
    return " ".join(part.replace("-", " ").title() for part in route.split("/"))


def target_exists(route: str) -> bool:
    return (OUT / route / "index.html").exists() if route else (OUT / "index.html").exists()


def related_block(route: str) -> str:
    targets = [target for target in related_routes(route) if target != route and target_exists(target)]
    if not targets:
        return ""
    links = "".join(
        f'<a href="{html.escape(page_url(target), quote=True)}">{html.escape(label_for_route(target))}</a>'
        for target in targets[:5]
    )
    return (
        '<aside class="related-context" aria-label="Related archive context">'
        '<strong>Related archive context</strong>'
        f'<nav>{links}</nav>'
        '</aside>'
    )


def inject_related_context(text: str, route: str) -> tuple[str, bool]:
    if 'class="related-context"' in text:
        return text, False
    block = related_block(route)
    if not block:
        return text, False
    if re.search(r"</main>", text, re.I):
        return re.sub(r"</main>", block + "\n</main>", text, count=1, flags=re.I), True
    if re.search(r"</body>", text, re.I):
        return re.sub(r"</body>", block + "\n</body>", text, count=1, flags=re.I), True
    return text, False


def strip_legacy_question_rich_result_schema(text: str) -> str:
    """Remove FAQ/QAPage rich-result markup from site-authored answer pages.

    Google limits FAQ rich results to authoritative government/health sites, and
    QAPage is for pages where users can submit answers. These archive question
    pages are authored reference pages, so the generic WebPage/Question graph
    projected below is the accurate representation.
    """
    def replace(match: re.Match[str]) -> str:
        payload = match.group(1).strip().replace("<\\/", "</")
        try:
            data = json.loads(payload)
        except Exception:
            return match.group(0)
        types = data.get("@type")
        values = {types} if isinstance(types, str) else set(types or [])
        if values & {"FAQPage", "QAPage"}:
            return ""
        return match.group(0)

    return LD_SCRIPT_RE.sub(replace, text)


def primary_schema(route: str, title: str, description: str, canonical_url: str) -> dict:
    profile = schema_profile(route)
    schema: dict[str, object] = {
        "@context": "https://schema.org",
        "@type": profile["schema_type"],
        "@id": canonical_url + "#primary",
        "url": canonical_url,
        "name": title,
        "description": description,
        "inLanguage": "en",
        "isAccessibleForFree": True,
        "isPartOf": {"@id": BASE_URL + "/#website"},
        "about": {"@type": "Thing", "name": str(profile["topic"])},
    }
    if profile.get("main_entity"):
        entity = dict(profile["main_entity"])
        entity.setdefault("@id", canonical_url + "#person")
        entity.setdefault("url", canonical_url)
        schema["mainEntity"] = entity
    if profile["schema_type"] in {"Article", "ScholarlyArticle"}:
        schema["headline"] = title
        schema["mainEntityOfPage"] = {"@type": "WebPage", "@id": canonical_url + "#webpage"}
    if profile["kind"] == "question":
        schema["mainEntity"] = {"@type": "Question", "name": title}
    return schema


def inject_schema(text: str, schema: dict) -> str:
    payload = json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tag = f'<script id="entity-intent-schema" type="application/ld+json">{payload}</script>'
    pattern = re.compile(r'<script\b[^>]*id=["\']entity-intent-schema["\'][^>]*>.*?</script>', re.I | re.S)
    if pattern.search(text):
        return pattern.sub(tag, text, count=1)
    return re.sub(r"</head>", tag + "\n</head>", text, count=1, flags=re.I)


def find_social_image() -> str | None:
    candidates = (
        "assets/social-card.png",
        "assets/social-card.jpg",
        "assets/og-image.png",
        "images/social-card.png",
        "images/og-image.png",
    )
    for rel in candidates:
        if (OUT / rel).is_file():
            return f"{BASE_URL}/{rel}"
    return None


def semantic_score(kind: str) -> int:
    return 0 if kind == "support" else 1


def main() -> int:
    if not OUT.exists():
        raise SystemExit("_site does not exist; build the site first")

    social_image = find_social_image()
    kinds: Counter[str] = Counter()
    schema_types: Counter[str] = Counter()
    titles: defaultdict[str, list[str]] = defaultdict(list)
    descriptions: defaultdict[str, list[str]] = defaultdict(list)
    errors: list[str] = []
    warnings: list[str] = []
    indexable = changed = related_count = image_count = 0
    semantic_pages = 0

    for page in sorted(OUT.rglob("index.html")):
        text = page.read_text(encoding="utf-8", errors="replace")
        if is_noindex(text):
            continue
        indexable += 1
        route = route_for(page)
        kind = classify_route(route)
        kinds[kind] += 1
        semantic_pages += semantic_score(kind)

        current_title = title_value(text)
        current_description = meta_value(text, name="description")
        projected = metadata_for(route, current_title, current_description)
        title = projected["title"] or current_title
        description = search_description(route, kind, projected["description"] or current_description)
        if not title:
            errors.append(f"{route or '/'}: no title after intent projection")
            continue
        if len(description) < 40:
            errors.append(f"{route or '/'}: weak description after intent projection")

        original = text
        if kind == "question":
            text = strip_legacy_question_rich_result_schema(text)
        text = replace_title(text, title)
        text = replace_meta(text, key="description", value=description)
        text = replace_meta(text, key="og:title", value=title, property_key=True)
        text = replace_meta(text, key="og:description", value=description, property_key=True)
        text = replace_meta(text, key="twitter:title", value=title)
        text = replace_meta(text, key="twitter:description", value=description)
        text = replace_meta(text, key="twitter:card", value="summary_large_image" if social_image else "summary")
        if social_image:
            text = replace_meta(text, key="og:image", value=social_image, property_key=True)
            text = replace_meta(text, key="twitter:image", value=social_image)
            image_count += 1

        canonical_url = canonical(text, route)
        profile = schema_profile(route)
        schema_types[str(profile["schema_type"])] += 1
        text = inject_schema(text, primary_schema(route, title, description, canonical_url))
        text, related_added = inject_related_context(text, route)
        if related_added:
            related_count += 1

        if text != original:
            page.write_text(text, encoding="utf-8")
            changed += 1

        titles[title.casefold()].append(route or "/")
        descriptions[description.casefold()].append(route or "/")

    duplicate_titles = [items for items in titles.values() if len(items) > 1]
    duplicate_descriptions = [items for key, items in descriptions.items() if key and len(items) > 1]
    for items in duplicate_titles[:20]:
        warnings.append("duplicate projected title: " + ", ".join(items[:6]))
    for items in duplicate_descriptions[:20]:
        warnings.append("duplicate projected description: " + ", ".join(items[:6]))
    if not social_image:
        warnings.append("No stable site-owned social image found; social cards remain text-only.")

    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "indexable_pages": indexable,
        "changed_pages": changed,
        "intent_kinds": dict(sorted(kinds.items())),
        "semantic_intent_pages": semantic_pages,
        "support_fallback_pages": kinds.get("support", 0),
        "primary_schema_types": dict(sorted(schema_types.items())),
        "pages_with_related_context_added": related_count,
        "pages_with_social_image": image_count,
        "social_image": social_image,
        "duplicate_title_groups": len(duplicate_titles),
        "duplicate_description_groups": len(duplicate_descriptions),
        "errors": errors,
        "warnings": warnings,
    }
    (OUT / "seo-intent-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if errors:
        print("ENTITY + INTENT SEO FAILED")
        for message in errors:
            print("-", message)
        return 1

    print(
        "ENTITY + INTENT SEO PASSED: "
        f"{indexable} indexable pages · {semantic_pages} semantic intents · "
        f"{related_count} related-context blocks · {len(schema_types)} schema types"
    )
    for message in warnings[:30]:
        print("warning:", message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
