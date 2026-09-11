#!/usr/bin/env python3
"""Validate the built GitHub Pages shell and canonical public ownership.

Deep applications have dedicated validators. This gate protects the reader
surface: exactly five homepage entrances, Bible as the one public Tim/Son ↔
Jesus comparator owner, one shared timeline, compatibility redirects instead
of duplicate Bible pages, North -> World Map routing, and local-link integrity.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
REPORT = ROOT / "site-shell-report.txt"
CANONICAL_HOME_LINKS = ("tim-dooley/", "religion/", "philosophy/", "science/", "world-map/3d.html")
BIBLE_VIEW = "traditions/bible/?view=jesus"
TIMELINE_VIEW = "chronology/?view=bible"


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
            errors.append(f"{owner} contains retired/duplicate marker: {marker}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    pages: list[Path] = []
    if not SITE.exists():
        errors.append("_site does not exist; build_site.py must run first")
    else:
        pages = sorted(SITE.rglob("*.html"))
        required = (
            "index.html", "tim-dooley/index.html", "religion/index.html",
            "religion/jesus-tim/index.html", "tim-dooley/biblical-case/index.html",
            "traditions/bible/index.html", "chronology/index.html", "philosophy/index.html",
            "science/index.html", "north/index.html", "world-map/3d.html", "sitemap.xml", "llms.txt",
        )
        for rel in required:
            if not (SITE / rel).exists(): errors.append(f"missing required site file: {rel}")

        index = read("index.html", errors)
        require(index, ("POTATO", "Main sections"), "index.html", errors)
        for href in CANONICAL_HOME_LINKS:
            if f'href="{href}"' not in index: errors.append(f"index.html missing canonical reader entrance: {href}")
        forbid(index, ('id="rootbtn"','id="branches"','id="reader"',"app/app.js","explore/#root","<iframe"), "index.html", errors)
        nav = re.search(r'<nav class="sections"[^>]*>(.*?)</nav>', index, flags=re.I|re.S)
        if not nav:
            errors.append("index.html missing canonical sections navigation")
        else:
            hrefs = re.findall(r'href="([^"]+)"', nav.group(1))
            if tuple(hrefs) != CANONICAL_HOME_LINKS: errors.append(f"homepage primary navigation must contain exactly five canonical entrances; found {hrefs}")

        religion = read("religion/index.html", errors)
        require(religion, (f'href="../{BIBLE_VIEW}"', f'href="../{TIMELINE_VIEW}"'), "religion/index.html", errors)
        forbid(religion, ('id="jesus-tim"', "../chronology/?tl_layers=", "Research</h2>", "Jesus / Son research index"), "religion/index.html", errors)
        comparator_rows = len(re.findall(r'class="row"', religion))
        if comparator_rows > 3: errors.append(f"religion/index.html must not duplicate the Bible comparator; found {comparator_rows} comparison rows")

        old_compare = read("religion/jesus-tim/index.html", errors)
        require(old_compare, ('name="robots" content="noindex,follow"', "../../traditions/bible/?view=jesus"), "religion/jesus-tim/index.html", errors)
        forbid(old_compare, ("../#jesus-tim", "religion/#jesus-tim"), "religion/jesus-tim/index.html", errors)

        old_biblical_case = read("tim-dooley/biblical-case/index.html", errors)
        require(old_biblical_case, ('name="robots" content="noindex,follow"', "../../traditions/bible/?view=jesus"), "tim-dooley/biblical-case/index.html", errors)
        forbid(old_biblical_case, ("Jacob's Ladder and the Son of Man", "Does this prove Tim is God?"), "tim-dooley/biblical-case/index.html", errors)

        tim = read("tim-dooley/index.html", errors)
        require(tim, (f'href="../{BIBLE_VIEW}"', "Jesus ↔ Tim / Son", "Chronology", "Public record"), "tim-dooley/index.html", errors)
        forbid(tim, ('href="../religion/#jesus-tim"',), "tim-dooley/index.html", errors)

        bible = read("traditions/bible/index.html", errors)
        require(bible, (
            "TIM &amp; THE BIBLE", 'id="study-modes"', 'data-view="jesus"', 'id="search"', 'id="relations"',
            'href="../../chronology/?view=bible"', 'src="../../app/bible-study.js"', 'href="../../app/bible-study.css"',
        ), "traditions/bible/index.html", errors)
        forbid(bible, ("../../religion/#jesus-tim", "?tl_layers=", "deepMatches("), "traditions/bible/index.html", errors)

        chronology = read("chronology/index.html", errors)
        require(chronology, ("THE LONG", 'class="timeline-explorer-standalone"', 'src="../app/timeline.js"', 'href="../religion/"'), "chronology/index.html", errors)
        forbid(chronology, ('<iframe',), "chronology/index.html", errors)

        north = read("north/index.html", errors)
        require(north, ('class="map-action" href="../world-map/3d.html"', ">WORLD MAP<"), "north/index.html", errors)
        learn = read("learn/index.html", errors)
        require(learn, ('name="robots" content="noindex,follow"', "location.replace('../')"), "learn/index.html", errors)
        atlas = read("world-map/3d.html", errors)
        require(atlas, ("World Relational Atlas", 'id="map"', 'id="compare"', 'id="relationType"', 'id="traceDepth"', 'id="timeMode"', 'src="./3d-bootstrap.js"'), "world-map/3d.html", errors)

        sitemap = read("sitemap.xml", errors)
        require(sitemap, ("https://thepotatooflife.github.io/TimDooley/traditions/bible/",), "sitemap.xml", errors)
        forbid(sitemap, ("/religion/jesus-tim/", "/tim-dooley/biblical-case/"), "sitemap.xml", errors)
        llms = read("llms.txt", errors)
        require(llms, ("https://thepotatooflife.github.io/TimDooley/traditions/bible/",), "llms.txt", errors)
        forbid(llms, ("https://thepotatooflife.github.io/TimDooley/tim-dooley/biblical-case/",), "llms.txt", errors)

        public_roots = (
            "index.html", "tim-dooley/index.html", "religion/index.html", "religion/jesus-tim/index.html",
            "tim-dooley/biblical-case/index.html", "traditions/bible/index.html", "chronology/index.html",
            "philosophy/index.html", "science/index.html", "north/index.html",
        )
        for rel in public_roots:
            text = read(rel, errors)
            if "<iframe" in text.lower(): errors.append(f"{rel} contains iframe dependency")
            if "tl_layers=" in text: errors.append(f"{rel} contains retired long timeline state URL")
            if "religion/#jesus-tim" in text: errors.append(f"{rel} points at retired Religion comparator owner")

        ref = re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''', re.I)
        base_ref = re.compile(r'''<base\s+[^>]*href=["']([^"'#?]+)["']''', re.I)
        bad: list[str] = []
        site_root = SITE.resolve()
        for html in pages:
            html_text = html.read_text(encoding="utf-8", errors="replace")
            base_dir = html.parent.resolve()
            base_match = base_ref.search(html_text)
            if base_match:
                base_raw = base_match.group(1)
                if not base_raw.startswith(("http:","https:","mailto:","javascript:","data:")):
                    candidate = (html.parent / base_raw).resolve()
                    try:
                        candidate.relative_to(site_root); base_dir = candidate
                    except ValueError: pass
            for raw in ref.findall(html_text):
                if raw.startswith(("http:","https:","mailto:","javascript:","data:")): continue
                target = (base_dir / raw).resolve()
                try: target.relative_to(site_root)
                except ValueError: continue
                if not target.exists(): bad.append(f"{html.relative_to(SITE)} -> {raw}")
        if bad: errors.append(f"broken local references in built site: {len(bad)}; examples: {bad[:8]}")
        if not pages: errors.append("Pages artifact contains no HTML documents")

    lines = [f"Built HTML pages checked: {len(pages)}", f"Errors: {len(errors)} · Warnings: {len(warnings)}"]
    if errors:
        lines.append("SITE SHELL VALIDATION FAILED")
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("SITE SHELL VALIDATION PASSED")
    report = "\n".join(lines)+"\n"
    REPORT.write_text(report, encoding="utf-8")
    print(report, end="")
    return 1 if errors else 0

if __name__ == "__main__": raise SystemExit(main())
