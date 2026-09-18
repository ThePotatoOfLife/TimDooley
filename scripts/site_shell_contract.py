#!/usr/bin/env python3
"""Validate the built GitHub Pages shell and durable reader-route ownership.

Question semantics have their own source validator. This gate stays deliberately
narrow: required public pages, five-door homepage ownership, compatibility
redirects, World-domain specialists, no iframe dependency, and local-link integrity.
Deploy-generated runtime assets are recognized explicitly rather than treated as
source-tree files.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
REPORT = ROOT / "site-shell-report.txt"
BASE = "https://thepotatooflife.github.io/TimDooley/"

CANONICAL_HOME_LINKS = (
    "tim-dooley/",
    "religion/",
    "philosophy/",
    "science/",
    "world/",
)
DEPLOY_GENERATED_DIRS = (
    SITE / "world-map" / "vendor",
)
WORLD_MACHINE_ROUTES = {
    "World": BASE + "world/",
    "World Map": BASE + "world-map/",
    "Politics & Geopolitics": BASE + "politics/",
    "North Axis / North Programme": BASE + "north/",
    "World Systems": BASE + "world-systems/",
}
HOUSE_BRIDGE_EXCLUDED = {"home", "house", "rooms", "explore", "world-map", "questions", "index-a-z"}

SITE_DISCOVERY_SCHEMA_RE = re.compile(
    r'<script\b[^>]*id=["\']site-discovery-schema["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)



def canonical_route_to_rel(route: str) -> str:
    raw = str(route or "/")
    if raw == "/":
        return "index.html"
    clean = raw.strip("/")
    return f"{clean}/index.html" if raw.endswith("/") else clean


def validate_house_bridges(errors: list[str]) -> None:
    registry_path = ROOT / "data" / "house" / "public-surfaces.json"
    if not registry_path.exists():
        errors.append("missing House public-surface registry for bridge validation")
        return
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid House public-surface registry: {exc}")
        return
    for surface in registry.get("surfaces", []):
        if not isinstance(surface, dict) or surface.get("status") != "active":
            continue
        sid = surface.get("id")
        if sid in HOUSE_BRIDGE_EXCLUDED:
            continue
        rel = canonical_route_to_rel(surface.get("canonical_route", "/"))
        path = SITE / rel
        if not path.exists():
            errors.append(f"registered House surface missing built page for bridge: {sid} -> {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        marker = f'data-house-bridge="{sid}"'
        if marker not in text:
            errors.append(f"{rel} missing shared House bridge marker {marker}")
        if text.count(marker) != 1:
            errors.append(f"{rel} must contain exactly one House bridge marker for {sid}")
        if "See all Dwellings &amp; Rooms" not in text:
            errors.append(f"{rel} House bridge missing Rooms return path")

def read(rel: str, errors: list[str]) -> str:
    path = SITE / rel
    if not path.exists():
        errors.append(f"missing required site file: {rel}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def require(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{owner} missing required marker: {marker}")


def forbid(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"{owner} contains retired/clutter marker: {marker}")


def deploy_generated(target: Path) -> bool:
    resolved = target.resolve()
    for directory in DEPLOY_GENERATED_DIRS:
        try:
            resolved.relative_to(directory.resolve())
            return True
        except ValueError:
            continue
    return False


def normalize_home_structured_data(text: str) -> str:
    """Remove ineligible one-item homepage breadcrumb markup before deploy."""
    def replace(match: re.Match[str]) -> str:
        raw = match.group(1)
        try:
            payload = json.loads(raw.replace("<\\/", "</"))
        except Exception:
            return match.group(0)
        graph = payload.get("@graph")
        if not isinstance(graph, list):
            return match.group(0)
        filtered = []
        changed = False
        for node in graph:
            if isinstance(node, dict) and node.get("@type") == "BreadcrumbList":
                items = node.get("itemListElement", [])
                if not isinstance(items, list) or len(items) < 2:
                    changed = True
                    continue
            filtered.append(node)
        if not changed:
            return match.group(0)
        payload["@graph"] = filtered
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return f'<script id="site-discovery-schema" type="application/ld+json">{encoded}</script>'

    return SITE_DISCOVERY_SCHEMA_RE.sub(replace, text, count=1)


def restore_canonical_world_route() -> None:
    """Finalize canonical homepage route and valid structured data before upload."""
    path = SITE / "index.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace('href="world-map/"><strong>World</strong>', 'href="world/"><strong>World</strong>')
    text = normalize_home_structured_data(text)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not SITE.exists():
        errors.append("_site does not exist; build_site.py must run first")
        pages: list[Path] = []
    else:
        restore_canonical_world_route()
        pages = sorted(SITE.rglob("*.html"))

        for rel in (
            "index.html",
            "tim-dooley/index.html",
            "religion/index.html",
            "religion/jesus-tim/index.html",
            "traditions/bible/index.html",
            "timeline/index.html",
            "philosophy/index.html",
            "science/index.html",
            "world/index.html",
            "politics/index.html",
            "north/index.html",
            "world-systems/index.html",
            "shadow-farm/index.html",
            "below/index.html",
            "world-map/index.html",
            "world-map/3d.html",
            "sitemap.xml",
            "llms.txt",
            "machine-index.json",
        ):
            if not (SITE / rel).exists():
                errors.append(f"missing required site file: {rel}")

        index = read("index.html", errors)
        require(index, ("POTATO", "Main sections"), "index.html", errors)
        for href in CANONICAL_HOME_LINKS:
            if f'href="{href}"' not in index:
                errors.append(f"index.html missing canonical reader entrance: {href}")
        forbid(index, ('id="rootbtn"', 'id="branches"', 'id="reader"', "app/app.js", "explore/#root", "<iframe"), "index.html", errors)

        primary_nav = re.search(r'<nav class="sections"[^>]*>(.*?)</nav>', index, flags=re.I | re.S)
        if not primary_nav:
            errors.append("index.html missing canonical sections navigation")
        else:
            hrefs = re.findall(r'href="([^"]+)"', primary_nav.group(1))
            if tuple(hrefs) != CANONICAL_HOME_LINKS:
                errors.append(f"homepage primary navigation must contain exactly five canonical entrances; found {hrefs}")

        religion = read("religion/index.html", errors)
        require(religion, ("RELIGION", 'href="../traditions/bible/"', 'href="../timeline/', 'href="../world-map/"'), "religion/index.html", errors)
        forbid(religion, ("explore/#branch=spirit", "Jesus / Son research index", "<iframe"), "religion/index.html", errors)

        comparison = read("religion/jesus-tim/index.html", errors)
        require(comparison, ('name="robots" content="noindex,follow"', "location.replace('../../traditions/bible/')"), "religion/jesus-tim/index.html", errors)

        tim = read("tim-dooley/index.html", errors)
        require(tim, ('href="../timeline/"', 'href="../traditions/bible/"', "Public record", "Evidence"), "tim-dooley/index.html", errors)

        bible = read("traditions/bible/index.html", errors)
        require(bible, ("TIM &amp; THE BIBLE", 'id="search"', 'id="relations"', 'href="../../religion/"', 'href="../../timeline/'), "traditions/bible/index.html", errors)
        forbid(bible, ('class="focus-links"', "Source authority", ">FAQ<"), "traditions/bible/index.html", errors)

        timeline = read("timeline/index.html", errors)
        require(timeline, ("THE LONG", 'class="timeline-explorer-standalone"', 'src="../app/timeline.js"', 'href="../religion/"'), "timeline/index.html", errors)
        forbid(timeline, ('class="source-note"', 'class="roadmap-note"', 'class="formula"', "Open Timeline in the complete archive", 'href="../corporium/"'), "timeline/index.html", errors)

        world = read("world/index.html", errors)
        require(world, ("WORLD", 'href="../world-map/"', 'href="../politics/"', 'href="../north/"', 'href="../world-systems/"'), "world/index.html", errors)

        politics = read("politics/index.html", errors)
        require(politics, ("Politics &amp; Geopolitics", 'href="../world/"', 'href="../world-map/"', 'href="../north/"', 'href="../world-systems/"'), "politics/index.html", errors)

        systems = read("world-systems/index.html", errors)
        require(systems, ("WORLD", "SYSTEMS", 'href="../world/"', 'href="../world-map/"', 'href="../politics/"', 'href="../north/"'), "world-systems/index.html", errors)

        north = read("north/index.html", errors)
        require(north, ('href="../world/"', 'href="../world-map/"', 'href="../politics/"', 'href="./"', 'href="../world-systems/"'), "north/index.html", errors)
        forbid(north, ("<title>North Axis — World Map</title>", 'class="maplink"', "Open North Axis in the World Map"), "north/index.html", errors)

        shadow = read("shadow-farm/index.html", errors)
        require(
            shadow,
            (
                'id="shadow-farm-tts"',
                'data-tts-longform',
                'data-tts-root=".page"',
                'data-tts-all-label="Whole deep reader"',
                'data-tts-exclude="#shadow-farm-tts,.nav"',
                'href="../app/tts-drawer.css"',
                'src="../app/tts-reader.js"',
                'src="../app/tts-drawer.js"',
                'src="../app/longform-tts-adapter.js"',
            ),
            "shadow-farm/index.html",
            errors,
        )
        if shadow.count('id="shadow-farm-tts"') != 1:
            errors.append("shadow-farm/index.html must contain exactly one generated TTS host")
        reader_pos = shadow.find('src="../app/tts-reader.js"')
        drawer_pos = shadow.find('src="../app/tts-drawer.js"')
        adapter_pos = shadow.find('src="../app/longform-tts-adapter.js"')
        if not (0 <= reader_pos < drawer_pos < adapter_pos):
            errors.append("shadow-farm/index.html TTS dependencies must load engine -> drawer -> longform adapter")
        forbid(shadow, ('data-tts-item=',), "shadow-farm/index.html", errors)

        learn = read("learn/index.html", errors)
        require(learn, ('name="robots" content="noindex,follow"', "location.replace('../')"), "learn/index.html", errors)

        chronology = read("chronology/index.html", errors)
        require(chronology, ('name="robots" content="noindex,follow"', "../timeline/"), "chronology/index.html", errors)

        world_map = read("world-map/index.html", errors)
        require(world_map, ("World Map", 'id="map"', 'id="compare"', 'id="relationType"', 'id="traceDepth"', 'id="timeMode"', 'src="./3d-bootstrap.js"', 'href="../world/"', 'href="../politics/"', 'href="../north/"', 'href="../world-systems/"'), "world-map/index.html", errors)
        forbid(world_map, ('href="../explore/#branch=world">World systems</a>',), "world-map/index.html", errors)

        legacy_map = read("world-map/3d.html", errors)
        require(legacy_map, ('name="robots" content="noindex,follow"', 'href="./"'), "world-map/3d.html", errors)
        forbid(legacy_map, ('id="map"', 'src="./3d-bootstrap.js"'), "world-map/3d.html", errors)

        machine_path = SITE / "machine-index.json"
        if machine_path.exists():
            try:
                machine = json.loads(machine_path.read_text(encoding="utf-8"))
                reader_urls = {
                    row.get("topic"): row.get("url")
                    for row in machine.get("primary_reader_urls", [])
                    if isinstance(row, dict)
                }
                for topic, url in WORLD_MACHINE_ROUTES.items():
                    if reader_urls.get(topic) != url:
                        errors.append(f"machine-index.json missing World route {topic}: expected {url}")
            except Exception as exc:
                errors.append(f"machine-index.json is invalid: {exc}")

        public_roots = (
            "index.html", "tim-dooley/index.html", "religion/index.html", "religion/jesus-tim/index.html",
            "traditions/bible/index.html", "timeline/index.html", "philosophy/index.html", "science/index.html",
            "world/index.html", "politics/index.html", "north/index.html", "world-systems/index.html", "shadow-farm/index.html",
            "world-map/index.html",
        )
        for rel in public_roots:
            text = read(rel, errors)
            if "<iframe" in text.lower():
                errors.append(f"{rel} contains iframe dependency")

        ref = re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''', re.I)
        base_ref = re.compile(r'''<base\s+[^>]*href=["']([^"'#?]+)["']''', re.I)
        bad: list[str] = []
        site_root = SITE.resolve()
        for html_path in pages:
            html_text = html_path.read_text(encoding="utf-8", errors="replace")
            base_dir = html_path.parent.resolve()
            base_match = base_ref.search(html_text)
            if base_match:
                base_raw = base_match.group(1)
                if not base_raw.startswith(("http:", "https:", "mailto:", "javascript:", "data:")):
                    candidate = (html_path.parent / base_raw).resolve()
                    try:
                        candidate.relative_to(site_root)
                        base_dir = candidate
                    except ValueError:
                        pass
            for raw in ref.findall(html_text):
                if raw.startswith(("http:", "https:", "mailto:", "javascript:", "data:")):
                    continue
                target = (base_dir / raw).resolve()
                try:
                    target.relative_to(site_root)
                except ValueError:
                    continue
                if not target.exists() and not deploy_generated(target):
                    bad.append(f"{html_path.relative_to(SITE)} -> {raw}")
        validate_house_bridges(errors)

        if bad:
            errors.append(f"broken local references in built site: {len(bad)}; examples: {bad[:8]}")
        if not pages:
            errors.append("Pages artifact contains no HTML documents")

    lines = [f"Built HTML pages checked: {len(pages)}", f"Errors: {len(errors)} · Warnings: {len(warnings)}"]
    if errors:
        lines.append("SITE SHELL VALIDATION FAILED")
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("SITE SHELL VALIDATION PASSED")
    report = "\n".join(lines) + "\n"
    REPORT.write_text(report, encoding="utf-8")
    print(report, end="")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())