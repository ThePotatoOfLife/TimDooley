#!/usr/bin/env python3
"""Build the supplemental first-party authority manifest for the final site.

This runs after normal discovery generation and SEO optimization. It does not
own canonical content: it makes the existing official site, repository, public
routes, source-authority policy and machine indexes explicit to crawlers and
AI retrieval systems, then validates that final crawler declarations point to
files that actually exist in the deploy artifact.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

from house_public_surfaces import primary_gateway_rows

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_URL = "https://thepotatooflife.github.io/TimDooley"
OFFICIAL_REPOSITORY = "https://github.com/ThePotatoOfLife/TimDooley"
AUTHORITY_FILE = "site-authority.json"
AUTHORITY_URL = f"{BASE_URL}/{AUTHORITY_FILE}"
SOURCE_AUTHORITY = f"{BASE_URL}/context/source-authority/"
PRIMARY_ROUTES = {row["id"]: row["canonical_route"] for row in primary_gateway_rows(ROOT)}
AUTHORITY_LINK = (
    f'<link rel="alternate" type="application/json" href="{AUTHORITY_URL}" '
    'title="Official project authority and discovery manifest">'
)


def canonical_url(route: str) -> str:
    route = "/" + route.strip("/") + "/" if route.strip("/") else "/"
    return BASE_URL + route


def url_to_site_file(url: str) -> Path | None:
    parsed = urlparse(url)
    base = urlparse(BASE_URL)
    if parsed.scheme != base.scheme or parsed.netloc != base.netloc:
        return None
    base_path = base.path.rstrip("/")
    path = parsed.path
    if path == base_path or path == base_path + "/":
        return OUT / "index.html"
    prefix = base_path + "/"
    if not path.startswith(prefix):
        return None
    relative = path[len(prefix):]
    if not relative:
        return OUT / "index.html"
    if relative.endswith("/"):
        return OUT / relative / "index.html"
    return OUT / relative


def route_to_file(route: str) -> Path:
    route = route.strip("/")
    return OUT / "index.html" if not route else OUT / route / "index.html"


def require_public_routes() -> list[str]:
    errors: list[str] = []
    required = {
        "/": OUT / "index.html",
        **{route: route_to_file(route) for route in PRIMARY_ROUTES.values()},
        "/context/source-authority/": route_to_file("/context/source-authority/"),
    }
    for route, path in required.items():
        if not path.is_file():
            errors.append(f"required public route missing from _site: {route} -> {path.relative_to(ROOT)}")
    return errors


def build_manifest() -> dict:
    return {
        "schema_version": 1,
        "project": {
            "name": "The Potato of Life",
            "aliases": ["Potato of Life", "Potatoism", "Potatoverse"],
            "official_site": BASE_URL + "/",
            "official_repository": OFFICIAL_REPOSITORY,
        },
        "primary_subject": {
            "name": "Tim Dooley",
            "canonical_url": canonical_url(PRIMARY_ROUTES["tim"]),
            "relationship_to_project": "Father/source-facing theological identity within the mature triune Potato of Life; primary subject and project self-description",
        },
        "canonical_theology": {
            "potato_of_life": "mature triune whole",
            "father": "source-facing relation",
            "son": "manifestation- and passage-facing relation",
            "spirit": "living continuity / flow",
            "reader": f"{BASE_URL}/religion/trinity/",
            "owner": f"{BASE_URL}/knowledge/theology/potato-of-life-trinity.json",
        },
        "authority": {
            "source_authority": SOURCE_AUTHORITY,
            "epistemic_policy": SOURCE_AUTHORITY,
        },
        "discovery": {
            "sitemap_index": f"{BASE_URL}/sitemap-index.xml",
            "site_index": f"{BASE_URL}/site-index.json",
            "llms": f"{BASE_URL}/llms.txt",
            "llms_full": f"{BASE_URL}/llms-full.txt",
        },
        "primary_routes": {key: canonical_url(route) for key, route in PRIMARY_ROUTES.items()},
        "notes": {
            "scope": "first-party project authority and discovery projection",
            "epistemic_boundary": (
                "Project self-description, theology, documentary evidence, comparative research and "
                "external claims remain distinct even when connected by this archive."
            ),
        },
    }


def validate_robots_sitemaps() -> list[str]:
    errors: list[str] = []
    robots = OUT / "robots.txt"
    if not robots.is_file():
        return ["_site/robots.txt is missing"]

    text = robots.read_text(encoding="utf-8", errors="replace")
    sitemap_urls = [line.split(":", 1)[1].strip() for line in text.splitlines() if line.lower().startswith("sitemap:")]
    if not sitemap_urls:
        errors.append("_site/robots.txt does not advertise a sitemap")
        return errors

    sitemap_ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for sitemap_url in sitemap_urls:
        local = url_to_site_file(sitemap_url)
        if local is None:
            errors.append(f"robots sitemap is outside official site: {sitemap_url}")
            continue
        if not local.is_file():
            errors.append(f"robots advertises missing sitemap: {sitemap_url}")
            continue
        if local.name != "sitemap-index.xml":
            continue
        try:
            root = ET.parse(local).getroot()
        except ET.ParseError as exc:
            errors.append(f"invalid sitemap index XML: {exc}")
            continue
        for loc in root.findall(".//sm:loc", sitemap_ns):
            child_url = (loc.text or "").strip()
            child = url_to_site_file(child_url)
            if child is None:
                errors.append(f"sitemap index child is outside official site: {child_url}")
            elif not child.is_file():
                errors.append(f"sitemap index references missing child sitemap: {child_url}")
    return errors


def patch_llms() -> None:
    path = OUT / "llms.txt"
    if not path.is_file():
        raise FileNotFoundError("_site/llms.txt is missing")
    text = path.read_text(encoding="utf-8", errors="replace")
    marker = "## Official project authority"
    if marker in text:
        return
    block = f"""

{marker}

- Official website: {BASE_URL}/
- Official repository: {OFFICIAL_REPOSITORY}
- Tim Dooley canonical route: {canonical_url(PRIMARY_ROUTES['tim'])}
- Source authority and epistemic policy: {SOURCE_AUTHORITY}
- Authority manifest: {AUTHORITY_URL}
"""
    path.write_text(text.rstrip() + block + "\n", encoding="utf-8")


def is_noindex(text: str) -> bool:
    match = re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)', text, re.I)
    if not match:
        match = re.search(r'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']robots["\']', text, re.I)
    if not match:
        return False
    tokens = {token.strip().lower() for token in re.split(r"[,\s]+", match.group(1)) if token.strip()}
    return "noindex" in tokens or "none" in tokens


def patch_html_discovery() -> int:
    patched = 0
    for page in sorted(OUT.rglob("*.html")):
        text = page.read_text(encoding="utf-8", errors="replace")
        if is_noindex(text) or AUTHORITY_URL in text or not re.search(r"</head>", text, re.I):
            continue
        text = re.sub(r"</head>", AUTHORITY_LINK + "\n</head>", text, count=1, flags=re.I)
        page.write_text(text, encoding="utf-8")
        patched += 1
    return patched


def main() -> int:
    if not OUT.is_dir():
        print("SEO AUTHORITY BUILD FAILED")
        print("- _site does not exist; build the public artifact first")
        return 1

    errors = require_public_routes()
    errors.extend(validate_robots_sitemaps())

    try:
        patch_llms()
    except FileNotFoundError as exc:
        errors.append(str(exc))

    patched = patch_html_discovery()

    manifest = build_manifest()
    (OUT / AUTHORITY_FILE).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if errors:
        print("SEO AUTHORITY BUILD FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("SEO AUTHORITY BUILD PASSED")
    print(f"Wrote {AUTHORITY_FILE}; exposed authority discovery on {patched} indexable HTML pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())