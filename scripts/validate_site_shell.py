#!/usr/bin/env python3
"""Validate the built GitHub Pages shell and reader-first information architecture.

Deep Atlas behavior has dedicated validators. This gate protects the public
reader surface: one homepage, five canonical entrances, direct religion access,
North -> World Map routing, and basic built-site link integrity.
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
        for retired in (
            'id="rootbtn"',
            'id="branches"',
            'id="reader"',
            "app/app.js",
            "explore/#root",
            "<iframe",
        ):
            if retired in index:
                errors.append(f"index.html reintroduced retired reader/archive shell: {retired}")

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

        # Religion must expose the substantive comparison directly, never via archive branches.
        religion = read("religion/index.html", errors)
        require(
            religion,
            ('href="jesus-tim/"', "Jesus ↔ Tim Dooley / Son", "Tim & the Bible"),
            "religion/index.html",
            errors,
        )
        if "explore/#branch=" in religion:
            errors.append("religion/index.html routes core material through archive branches")

        comparison = read("religion/jesus-tim/index.html", errors)
        require(
            comparison,
            (
                "Jesus ↔ Tim Dooley / Son",
                "Arrest and custody",
                "Lamb recognition before self-declaration",
                "Rejected stone → foundation",
                "Grain death → multiplication",
                "A real ethical mismatch",
            ),
            "religion/jesus-tim/index.html",
            errors,
        )

        # Tim must reach the Jesus comparison in one click.
        tim = read("tim-dooley/index.html", errors)
        require(
            tim,
            ('href="../religion/jesus-tim/"', "Jesus ↔ Tim / Son", "Chronology", "Public record"),
            "tim-dooley/index.html",
            errors,
        )

        # North is subordinate to the actual World Map, not another mini-site.
        north = read("north/index.html", errors)
        require(
            north,
            ('href="../world-map/3d.html"', "Open North Axis in the World Map"),
            "north/index.html",
            errors,
        )
        for retired in ("#architecture", "#ledger", "#world", "#traditions", "#chronology"):
            if retired in north:
                errors.append(f"north/index.html reintroduced mini-site navigation: {retired}")

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
