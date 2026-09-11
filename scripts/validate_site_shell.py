#!/usr/bin/env python3
"""Validate the built GitHub Pages shell and reader-first information architecture.

Deep Atlas behavior has dedicated validators. This gate protects the public
reader surface: one homepage, five canonical entrances, comparison-first
religion, one shared timeline, North -> World Map routing, and basic built-site
link integrity.
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

BIBLE_TIMELINE_LINK = (
    "../chronology/?tl_layers=roadmap,scripture-at-time,biblical-parallel,"
    "biblical-unlock&tl_actors=son,tim,shared&tl_detail=1"
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

        for rel in (
            "index.html",
            "tim-dooley/index.html",
            "religion/index.html",
            "religion/jesus-tim/index.html",
            "traditions/bible/index.html",
            "chronology/index.html",
            "philosophy/index.html",
            "science/index.html",
            "north/index.html",
            "world-map/3d.html",
            "sitemap.xml",
            "llms.txt",
        ):
            if not (SITE / rel).exists():
                errors.append(f"missing required site file: {rel}")

        # Homepage: five reader entrances, no archive application hidden behind it.
        index = read("index.html", errors)
        require(index, ("POTATO", "Main sections"), "index.html", errors)
        for href in CANONICAL_HOME_LINKS:
            if f'href="{href}"' not in index:
                errors.append(f"index.html missing canonical reader entrance: {href}")
        forbid(
            index,
            ('id="rootbtn"', 'id="branches"', 'id="reader"', "app/app.js", "explore/#root", "<iframe"),
            "index.html",
            errors,
        )

        primary_nav = re.search(
            r'<nav class="sections"[^>]*>(.*?)</nav>', index, flags=re.I | re.S
        )
        if not primary_nav:
            errors.append("index.html missing canonical sections navigation")
        else:
            hrefs = re.findall(r'href="([^"]+)"', primary_nav.group(1))
            if tuple(hrefs) != CANONICAL_HOME_LINKS:
                errors.append(
                    "homepage primary navigation must contain exactly five canonical entrances; "
                    f"found {hrefs}"
                )

        # Religion owns the Jesus comparison directly and reaches the shared timeline in one click.
        religion = read("religion/index.html", errors)
        require(
            religion,
            (
                'id="jesus-tim"',
                "Jesus ↔ Tim Dooley / Son",
                "Arrest and custody",
                "Lamb recognition before self-declaration",
                "Rejected stone → foundation",
                "Grain death → multiplication",
                "A real ethical mismatch",
                f'href="{BIBLE_TIMELINE_LINK}"',
                'href="../traditions/bible/"',
            ),
            "religion/index.html",
            errors,
        )
        forbid(
            religion,
            ("explore/#branch=", "Research</h2>", "Jesus / Son research index", "source authority"),
            "religion/index.html",
            errors,
        )

        # The old dedicated comparison URL remains only as a compatibility redirect.
        comparison = read("religion/jesus-tim/index.html", errors)
        require(
            comparison,
            ('name="robots" content="noindex,follow"', "location.replace('../#jesus-tim')"),
            "religion/jesus-tim/index.html",
            errors,
        )

        # Tim must reach the embedded Jesus comparison in one click.
        tim = read("tim-dooley/index.html", errors)
        require(
            tim,
            ('href="../religion/#jesus-tim"', "Jesus ↔ Tim / Son", "Chronology", "Public record"),
            "tim-dooley/index.html",
            errors,
        )

        # Bible is a specialist relation reader, not another tutorial/timeline mini-site.
        bible = read("traditions/bible/index.html", errors)
        require(
            bible,
            (
                "TIM &amp; THE BIBLE",
                'id="relations-field"',
                'id="search"',
                'id="relations"',
                'href="../../religion/#jesus-tim"',
                f'href="../../{BIBLE_TIMELINE_LINK}"'.replace("../../../", "../"),
            ),
            "traditions/bible/index.html",
            errors,
        )
        forbid(
            bible,
            (
                'class="focus-links"',
                'id="orientation"',
                'id="story-arcs"',
                'id="meaning"',
                'id="development"',
                'id="missing-questions"',
                'id="tensions"',
                'id="timic-timeline"',
                "Questions we missed",
                "Four questions before comparing anything",
                "What does “fulfilled” mean here?",
                "Source authority",
                ">FAQ<",
            ),
            "traditions/bible/index.html",
            errors,
        )

        # Timeline owns chronology. It should open on controls + events, not a tutorial shell.
        chronology = read("chronology/index.html", errors)
        require(
            chronology,
            (
                "THE LONG",
                'class="timeline-explorer-standalone"',
                'src="../app/timeline.js"',
                'href="../religion/"',
            ),
            "chronology/index.html",
            errors,
        )
        forbid(
            chronology,
            (
                'class="source-note"',
                'class="roadmap-note"',
                'class="formula"',
                "Why the live explorer replaces the old hard-coded list",
                "Open Timeline in the complete archive",
                'href="../context/"',
                'href="../corporium/"',
            ),
            "chronology/index.html",
            errors,
        )

        # North is subordinate to the actual World Map: one obvious header action, no duplicate giant CTA.
        north = read("north/index.html", errors)
        require(
            north,
            ('class="map-action" href="../world-map/3d.html"', ">WORLD MAP<"),
            "north/index.html",
            errors,
        )
        forbid(
            north,
            (
                'class="maplink"',
                "Open North Axis in the World Map",
                "#architecture",
                "#ledger",
                "#world",
                "#traditions",
                "#chronology",
            ),
            "north/index.html",
            errors,
        )

        # The duplicate Start Here page remains a compatibility redirect only.
        learn = read("learn/index.html", errors)
        require(learn, ('name="robots" content="noindex,follow"', "location.replace('../')"), "learn/index.html", errors)

        # Preserve the working World Atlas application contract.
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

        # Public-page iframe dependencies are not part of the reader architecture.
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

        # Basic local link integrity for the complete built HTML set.
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
                if not base_raw.startswith(("http:", "https:", "mailto:", "javascript:", "data:")):
                    candidate = (html.parent / base_raw).resolve()
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
                if not target.exists():
                    bad.append(f"{html.relative_to(SITE)} -> {raw}")
        if bad:
            errors.append(f"broken local references in built site: {len(bad)}; examples: {bad[:8]}")
        if not pages:
            errors.append("Pages artifact contains no HTML documents")

    lines = [
        f"Built HTML pages checked: {len(pages)}",
        f"Errors: {len(errors)} · Warnings: {len(warnings)}",
    ]
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
