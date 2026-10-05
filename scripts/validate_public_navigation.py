#!/usr/bin/env python3
"""Guard the small public navigation and deployed reader capability contract."""
from __future__ import annotations

import html
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"

ROOT_BRANCH_PATTERNS = (
    re.compile(r'''href=["'](?:\.{1,2}/)*#branch=''', re.I),
    re.compile(r'''https://thepotatooflife\.github\.io/TimDooley/#branch=''', re.I),
)
NAV = re.compile(r"<nav\b[^>]*>(.*?)</nav>", re.I | re.S)
DEEP = re.compile(r'<div\b[^>]*class=["\'][^"\']*\bdeep\b[^"\']*["\'][^>]*>(.*?)</div>', re.I | re.S)
HREF = re.compile(r'''href=["']([^"']+)["']''', re.I)

PAGE_NAV_CLASS = re.compile(r'''<nav\b[^>]*class=["'][^"']*\bpage-nav\b[^"']*["'][^>]*>(.*?)</nav>''', re.I | re.S)
PAGE_NAV_ANCHOR = re.compile(r'''<a\b(?P<attrs>[^>]*)href=["'](?P<href>[^"']+)["'][^>]*>(?P<label>.*?)</a>''', re.I | re.S)
PAGE_NAV_ROOM_CLASS = re.compile(r'''\bclass=["'][^"']*\bpage-nav-room\b''', re.I)
MAX_PAGE_NAV_LINKS = 12
LEGACY_NAV_LABELS = (">Corporium</a>", ">Source authority</a>", ">Tim dossier</a>")
REDUNDANT_PAGE_NAV_LABELS = {"All Rooms", "Spatial Room", "Parent Dwelling"}

PROJECTED_TTS_PAGES = {
    "rooms/index.html": "rooms",
    "history/index.html": "history",
    "law/index.html": "law",
    "economy/index.html": "economy",
    "world-systems/index.html": "world-systems",
    "politics/index.html": "politics",
    "timeline/index.html": "timeline",
    "works/index.html": "works",
    "science/index.html": "science",
    "context/source-authority/index.html": "source-authority",
    "philosophy/interpretive-justice.html": "interpretive-justice",
}
TTS_ASSET_MARKERS = (
    "tts-drawer.css",
    "tts-reader.js",
    "tts-drawer.js",
    "longform-tts-adapter.js",
)

CANONICAL_READER_SURFACES = {
    "politics/index.html": "politics",
    "timeline/index.html": "timeline",
    "context/source-authority/index.html": "sources",
}

CULTURE_FIELD_MARKERS = (
    'data-culture-field="concrete-culture-field"',
    "Who is actually here?",
    "Where violence actually appears",
    "Follow the flows",
    "People behind the labels",
    "How a formation changes type",
    "Who owns the infrastructure?",
    "How correction works",
    "Ritual without captivity",
    "When underground becomes institution",
    "Concrete Tree of Strife",
)


def duplicate_hrefs(fragment: str) -> list[str]:
    counts = Counter(HREF.findall(fragment))
    return sorted(href for href, count in counts.items() if count > 1)


def main() -> int:
    errors: list[str] = []

    culture_contract = subprocess.run(
        ["python", str(ROOT / "scripts" / "test_concrete_culture_field.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if culture_contract.returncode != 0:
        detail = (culture_contract.stdout + "\n" + culture_contract.stderr).strip()
        errors.append(f"concrete Culture field contract failed: {detail}")

    if not SITE.exists():
        errors.append("_site does not exist; build_site.py must run first")
        pages: list[Path] = []
    else:
        pages = sorted(SITE.rglob("*.html"))

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        rel = page.relative_to(SITE)
        for pattern in ROOT_BRANCH_PATTERNS:
            if pattern.search(text):
                errors.append(
                    f"stale homepage branch route in {rel}; "
                    "route deep branches through /explore/#branch=... or a domain hub"
                )
                break

        for nav_index, nav in enumerate(NAV.findall(text), start=1):
            duplicates = duplicate_hrefs(nav)
            if duplicates:
                errors.append(f"duplicate href(s) inside nav {nav_index} of {rel}: {duplicates}")
            for label in LEGACY_NAV_LABELS:
                if label in nav:
                    errors.append(f"legacy visitor label {label[1:-4]!r} inside nav {nav_index} of {rel}")

        for page_nav_index, nav in enumerate(PAGE_NAV_CLASS.findall(text), start=1):
            anchors = list(PAGE_NAV_ANCHOR.finditer(nav))
            if rel.as_posix() != "index.html" and anchors:
                first = anchors[0]
                first_label = re.sub(r"<[^>]+>", "", first.group("label")).strip()
                if first_label != "Home":
                    errors.append(f"page-nav {page_nav_index} of {rel} must begin with Home; found {first_label!r}")
                if "page-nav-home" not in first.group("attrs"):
                    errors.append(f"page-nav {page_nav_index} of {rel} first link missing page-nav-home marker")
                if len(anchors) > MAX_PAGE_NAV_LINKS:
                    errors.append(
                        f"page-nav {page_nav_index} of {rel} has {len(anchors)} links; "
                        f"subheaders must stay at {MAX_PAGE_NAV_LINKS} choices or fewer"
                    )
            for anchor in anchors:
                label = html.unescape(re.sub(r"<[^>]+>", "", anchor.group("label"))).lstrip("←").strip()
                if label in REDUNDANT_PAGE_NAV_LABELS:
                    errors.append(f"page-nav {page_nav_index} of {rel} leaked redundant architecture label {label!r}")
            current_count = sum(
                1 for anchor in anchors
                if re.search(r'''\baria-current=["']page["']''', anchor.group("attrs"), flags=re.I)
            )
            if current_count > 1:
                errors.append(
                    f"page-nav {page_nav_index} of {rel} marks {current_count} links current; "
                    "only the most-specific destination may use aria-current=page"
                )
            if rel.as_posix() == "explore/index.html":
                for anchor in anchors:
                    if anchor.group("href").startswith("../"):
                        errors.append(
                            "Explore page-nav must respect <base href=\"../\"> and use base-rooted relative links"
                        )
            room_link_count = len(PAGE_NAV_ROOM_CLASS.findall(nav))
            if room_link_count > 8:
                errors.append(
                    f"page-nav {page_nav_index} of {rel} projects {room_link_count} Room-neighborhood links; "
                    "keep contextual navigation readable"
                )

        for deep_index, deep in enumerate(DEEP.findall(text), start=1):
            duplicates = duplicate_hrefs(deep)
            if duplicates:
                errors.append(f"duplicate href(s) inside deep-link group {deep_index} of {rel}: {duplicates}")

        if "← Potato of Life archive</a>" in text:
            errors.append(f"legacy home label remains in {rel}: use Home on the visitor surface")

    required_pages = (
        "religion/index.html",
        "traditions/bible/index.html",
        "traditions/vesica/index.html",
    )
    for rel in required_pages:
        if not (SITE / rel).exists():
            errors.append(f"missing public navigation page: {rel}")

    for rel in ("traditions/bible/index.html", "traditions/vesica/index.html"):
        path = SITE / rel
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            if '../../religion/' not in text:
                errors.append(f"{rel} does not link back to its Religion parent hub")

    science_path = SITE / "science" / "index.html"
    if not science_path.exists():
        errors.append("missing Science hub: science/index.html")
    else:
        science_text = science_path.read_text(encoding="utf-8", errors="replace")
        if "science/papers/" not in science_text and './papers/' not in science_text:
            errors.append("Science hub missing Science Papers entry")
        science_nav = PAGE_NAV_CLASS.search(science_text)
        if science_nav and "Research Papers" not in science_nav.group(1):
            errors.append("Science page-nav missing Research Papers destination after navigation projection")

    papers_path = SITE / "science" / "papers" / "index.html"
    if not papers_path.exists():
        errors.append("missing Science Papers reader: science/papers/index.html")
    else:
        papers_text = papers_path.read_text(encoding="utf-8", errors="replace")
        papers_nav = PAGE_NAV_CLASS.search(papers_text)
        if not papers_nav:
            errors.append("Science Papers reader missing canonical page-nav")
        else:
            nav_text = html.unescape(re.sub(r"<[^>]+>", " ", papers_nav.group(1)))
            for label in ("Science", "Research Papers", "Guide", "Physics", "Life & Mind", "Systems", "Mathematics", "Research", "Research Map", "Sources"):
                if label not in nav_text:
                    errors.append(f"Science Papers page-nav missing {label!r}")
        if "RESEARCH PAPERS" not in papers_text:
            errors.append("Research Papers reader missing reader heading")

    for rel, surface_id in CANONICAL_READER_SURFACES.items():
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing canonical reader surface: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        marker = f'data-reader-surface="{surface_id}"'
        if marker not in text:
            errors.append(f"{rel} missing canonical reader marker {marker}")

    for rel, reader_id in PROJECTED_TTS_PAGES.items():
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing TTS-covered public page: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        host_id = f'id="{reader_id}-tts"'
        if host_id not in text:
            errors.append(f"{rel} missing projected TTS host {host_id}")
        if "data-tts-longform" not in text:
            errors.append(f"{rel} missing data-tts-longform reader contract")
        for marker in TTS_ASSET_MARKERS:
            if marker not in text:
                errors.append(f"{rel} missing shared TTS asset {marker}")

    culture_path = SITE / "context" / "culture" / "index.html"
    if not culture_path.exists():
        errors.append("missing Culture reader for concrete field projection")
    else:
        culture_text = culture_path.read_text(encoding="utf-8", errors="replace")
        for marker in CULTURE_FIELD_MARKERS:
            if marker not in culture_text:
                errors.append(f"Culture reader missing concrete field marker: {marker}")
        if 'id="culture-tts"' not in culture_text or "data-tts-longform" not in culture_text:
            errors.append("Culture reader lost its shared TTS host after concrete field projection")
        field_start = culture_text.find('data-culture-field="concrete-culture-field"')
        field_end = culture_text.find("<h2>Culture is multidimensional</h2>", field_start)
        if field_start >= 0 and field_end > field_start:
            field_fragment = culture_text[field_start:field_end]
            if "href=" not in field_fragment or "<strong>Sources:</strong>" not in field_fragment:
                errors.append("Concrete Culture field must expose source links inside the public projection")
            if "aggregate environment figures are not assigned to a named group" not in field_fragment:
                errors.append("Concrete Culture field lost its aggregate-statistics legal/evidence boundary")
            if "comparative, not a claim of moral or organizational equivalence" not in field_fragment:
                errors.append("Concrete Culture field lost its contrastive-not-equivalent framing")
            for required_case in (
                "Organization for Transformative Works / Archive of Our Own",
                "Burning Man / Burning Man Project",
                "Skateboarding",
                "Wikipedia editing culture",
                "Mastodon / ActivityPub federation",
            ):
                if required_case not in field_fragment:
                    errors.append(f"Concrete Culture field missing expansion case: {required_case}")
            if "intensity alone" not in field_fragment:
                errors.append("Concrete Culture field lost ritual-versus-high-control distinction")
            if "single point of dependency" not in field_fragment:
                errors.append("Concrete Culture field lost infrastructure-ownership analysis")

    if errors:
        print("PUBLIC NAVIGATION VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"PUBLIC NAVIGATION VALIDATION PASSED ({len(pages)} HTML pages checked; "
        f"{len(PROJECTED_TTS_PAGES)} projected TTS surfaces; "
        f"{len(CANONICAL_READER_SURFACES)} canonical reader IDs; concrete Culture field)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
