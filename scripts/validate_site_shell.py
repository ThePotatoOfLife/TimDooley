#!/usr/bin/env python3
"""Validate the built reader surface and its canonical ownership boundaries.

Public architecture:
- Tim Dooley: subject / biography / evidence routes.
- Religion: lightweight traditions router; no duplicate scripture comparator.
- Bible: canonical scripture comparison laboratory, statically rendered then enhanced.
- Science: canonical paper library with abstracts, filters and full documents.
- World Atlas: one world-system product; world-map/3d.html is its geographic view.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
REPORT = ROOT / "site-shell-report.txt"

CANONICAL_HOME_LINKS = (
    "tim-dooley/",
    "religion/",
    "philosophy/",
    "science/",
    "world-map/3d.html",
)


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


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not SITE.exists():
        errors.append("_site does not exist; build_site.py must run first")
        pages: list[Path] = []
    else:
        pages = sorted(SITE.rglob("*.html"))

        required_files = (
            "index.html",
            "tim-dooley/index.html",
            "religion/index.html",
            "religion/jesus-tim/index.html",
            "traditions/bible/index.html",
            "chronology/index.html",
            "philosophy/index.html",
            "science/index.html",
            "science/catalog.json",
            "north/index.html",
            "world-map/3d.html",
            "sitemap.xml",
            "llms.txt",
        )
        for rel in required_files:
            if not (SITE / rel).exists():
                errors.append(f"missing required site file: {rel}")

        index = read("index.html", errors)
        require(index, ("POTATO", "Main sections"), "index.html", errors)
        primary_nav = re.search(r'<nav class="sections"[^>]*>(.*?)</nav>', index, flags=re.I | re.S)
        if not primary_nav:
            errors.append("index.html missing canonical sections navigation")
        else:
            hrefs = re.findall(r'href="([^"]+)"', primary_nav.group(1))
            if tuple(hrefs) != CANONICAL_HOME_LINKS:
                errors.append(f"homepage primary navigation must contain exactly five canonical entrances; found {hrefs}")
        forbid(index, ('id="rootbtn"', 'id="branches"', 'id="reader"', "app/app.js", "explore/#root", "<iframe"), "index.html", errors)

        # Religion is a router, not a second scripture comparison page.
        religion = read("religion/index.html", errors)
        require(
            religion,
            (
                "The traditions index for the archive",
                "It does not duplicate the Bible comparator",
                'href="../traditions/bible/"',
                "Tim &amp; the Bible",
                "Comparative religion",
                "Sacred geometry &amp; symbols",
                "Religious chronology",
            ),
            "religion/index.html",
            errors,
        )
        forbid(
            religion,
            (
                'id="jesus-tim"',
                "Arrest and custody",
                "Lamb recognition before self-declaration",
                "Rejected stone → foundation",
                "Grain death → multiplication",
                "A real ethical mismatch",
            ),
            "religion/index.html",
            errors,
        )

        comparison_redirect = read("religion/jesus-tim/index.html", errors)
        require(
            comparison_redirect,
            (
                'name="robots" content="noindex,follow"',
                "../../traditions/bible/?view=jesus",
            ),
            "religion/jesus-tim/index.html",
            errors,
        )

        tim = read("tim-dooley/index.html", errors)
        require(
            tim,
            (
                'href="../traditions/bible/?view=jesus"',
                "Jesus ↔ Tim / Son",
                "Chronology",
                "Public record",
            ),
            "tim-dooley/index.html",
            errors,
        )

        # Bible owns the scripture relation system and must be useful before JS.
        bible = read("traditions/bible/index.html", errors)
        require(
            bible,
            (
                "TIM &amp; THE BIBLE",
                "The scripture laboratory for the archive",
                'id="relations-field"',
                'id="search"',
                'id="relations"',
                'data-view="prophecy"',
                'data-view="counter-texts"',
                'data-static-relation=',
                "Why the relation is here",
                "Scripture beside it",
            ),
            "traditions/bible/index.html",
            errors,
        )
        if "<!-- BIBLE_RELATIONS_STATIC -->" in bible:
            errors.append("traditions/bible/index.html still contains uncompiled Bible marker")
        if bible.count('data-static-relation=') < 10:
            errors.append("traditions/bible/index.html must expose at least 10 static scripture relations")

        chronology = read("chronology/index.html", errors)
        require(chronology, ("THE LONG", 'class="timeline-explorer-standalone"', 'src="../app/timeline.js"', 'href="../religion/"'), "chronology/index.html", errors)

        # Science owns papers and must contain statically compiled records.
        science = read("science/index.html", errors)
        require(
            science,
            (
                "Research library",
                'id="science-search"',
                'id="science-field"',
                'id="science-type"',
                'class="science-record"',
                "Every result opens the complete document",
            ),
            "science/index.html",
            errors,
        )

        north = read("north/index.html", errors)
        require(north, ('class="map-action" href="../world-map/3d.html"',), "north/index.html", errors)

        atlas = read("world-map/3d.html", errors)
        require(
            atlas,
            (
                "World Relational Atlas",
                'id="map"',
                'id="compare"',
                'id="relationType"',
                'id="traceDepth"',
                'id="timeMode"',
                'src="./3d-bootstrap.js"',
            ),
            "world-map/3d.html",
            errors,
        )

        public_roots = (
            "index.html",
            "tim-dooley/index.html",
            "religion/index.html",
            "religion/jesus-tim/index.html",
            "traditions/bible/index.html",
            "chronology/index.html",
            "philosophy/index.html",
            "science/index.html",
            "north/index.html",
        )
        for rel in public_roots:
            text = read(rel, errors)
            if "<iframe" in text.lower():
                errors.append(f"{rel} contains iframe dependency")

        # Generic local-link integrity across the built HTML tree.
        ref = re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''', re.I)
        base_ref = re.compile(r'''<base\s+[^>]*href=["']([^"'#?]+)["']''', re.I)
        bad: list[str] = []
        site_root = SITE.resolve()
        for page in pages:
            page_text = page.read_text(encoding="utf-8", errors="replace")
            base_dir = page.parent.resolve()
            base_match = base_ref.search(page_text)
            if base_match:
                base_raw = base_match.group(1)
                if not base_raw.startswith(("http:", "https:", "mailto:", "javascript:", "data:")):
                    candidate = (page.parent / base_raw).resolve()
                    try:
                        candidate.relative_to(site_root)
                        base_dir = candidate
                    except ValueError:
                        pass
            for raw in ref.findall(page_text):
                if raw.startswith(("http:", "https:", "mailto:", "javascript:", "data:")):
                    continue
                target = (base_dir / raw).resolve()
                try:
                    target.relative_to(site_root)
                except ValueError:
                    continue
                if not target.exists():
                    bad.append(f"{page.relative_to(SITE)} -> {raw}")
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
