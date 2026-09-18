#!/usr/bin/env python3
"""Guard the public House navigation and deployed reader capability contract."""
from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path

from house_public_surfaces import (
    EXPECTED_PRIMARY_GATEWAY_IDS,
    parent_chain,
    primary_gateway_rows,
    secondary_global_rows,
    surface_by_route,
    surface_rows,
)
from house_shell import render_house_bar, relative_href

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"

ROOT_BRANCH_PATTERNS = (
    re.compile(r'''href=["'](?:\.{1,2}/)*#branch=''', re.I),
    re.compile(r'''https://thepotatooflife\.github\.io/TimDooley/#branch=''', re.I),
)
NAV = re.compile(r"<nav\b[^>]*>(.*?)</nav>", re.I | re.S)
DEEP = re.compile(r'<div\b[^>]*class=["\'][^"\']*\bdeep\b[^"\']*["\'][^>]*>(.*?)</div>', re.I | re.S)
HREF = re.compile(r'''href=["']([^"']+)["']''', re.I)
LEGACY_NAV_LABELS = (">Corporium</a>", ">Source authority</a>", ">Tim dossier</a>")

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

GENERATED_REPRESENTATIVES = (
    "questions/index.html",
    "index-a-z/index.html",
)


def duplicate_hrefs(fragment: str) -> list[str]:
    counts = Counter(HREF.findall(fragment))
    return sorted(href for href, count in counts.items() if count > 1)


def primary_nav_fragment(text: str) -> str:
    match = re.search(
        r'<nav\b[^>]*class=["\'][^"\']*\bsite-primary-nav\b[^"\']*["\'][^>]*>(.*?)</nav>',
        text,
        re.I | re.S,
    )
    return match.group(1) if match else ""


def validate_source_architecture(errors: list[str]) -> None:
    build_site = (ROOT / "scripts" / "build_site.py").read_text(encoding="utf-8", errors="replace")
    discovery = (ROOT / "scripts" / "build_discovery.py").read_text(encoding="utf-8", errors="replace")
    site_css = (ROOT / "app" / "site-system.css").read_text(encoding="utf-8", errors="replace")

    if '"archive"' not in build_site.split("EXCLUDE", 1)[1].split("}", 1)[0]:
        errors.append("build_site.py does not exclude archive from the public copy boundary")
    if "DOOR_LABELS" in build_site:
        errors.append("build_site.py still owns a duplicate DOOR_LABELS taxonomy")
    if "from house_shell import" not in build_site or "render_house_bar_for_route" not in build_site:
        errors.append("build_site.py does not consume the shared House renderer")
    if "<style>:root" in build_site:
        errors.append("build_site.py still embeds a second global :root theme")

    if "from house_public_surfaces import primary_gateway_rows" not in discovery:
        errors.append("build_discovery.py does not derive primary Doors from House authority")
    if "from house_shell import" not in discovery or "render_house_bar_for_route" not in discovery:
        errors.append("build_discovery.py does not consume the shared House renderer")
    if "<style>:root" in discovery:
        errors.append("build_discovery.py still embeds a second global :root theme")

    for marker in (
        ".site-housebar",
        ".site-primary-nav",
        ".site-breadcrumbs",
        ".site-local-nav",
        ".site-related",
        ".site-footer",
    ):
        if marker not in site_css:
            errors.append(f"shared site system missing House primitive: {marker}")


def validate_house_authority(errors: list[str]) -> None:
    try:
        rows = surface_rows(ROOT)
        primary = primary_gateway_rows(ROOT)
        secondary = secondary_global_rows(ROOT)
        ids = tuple(row["id"] for row in primary)
        if ids != EXPECTED_PRIMARY_GATEWAY_IDS:
            errors.append(f"primary gateway order mismatch: {ids!r}")

        great_book = surface_by_route(ROOT, "/great-book/")
        if not great_book or great_book.get("id") != "great-book":
            errors.append("Great Book is not registered at /great-book/")
        elif great_book.get("shell_type") != "longform":
            errors.append("Great Book must use the longform shell")

        secondary_ids = {row["id"] for row in secondary}
        if "great-book" not in secondary_ids:
            errors.append("Great Book is not globally discoverable")

        for row in rows:
            if row.get("status") != "active":
                continue
            try:
                parent_chain(ROOT, row["id"])
            except ValueError as exc:
                errors.append(str(exc))

        housebar = render_house_bar(ROOT, "world")
        for label in ("Tim Dooley", "Religion", "Philosophy", "Science", "World"):
            if label not in housebar:
                errors.append(f"House renderer missing primary Door label: {label}")
        primary_fragment = primary_nav_fragment(housebar)
        if "World Map" in re.sub(r"\s+", " ", primary_fragment):
            errors.append("House primary navigation still exposes World Map as a primary Door")
        if 'aria-current="page"' not in housebar:
            errors.append("House renderer does not mark the current Door")
        if relative_href("/tim-dooley/story/", "/tim-dooley/") != "../":
            errors.append("House relative route resolver returned an unexpected Tim parent href")
    except ValueError as exc:
        errors.append(f"House public-surface authority invalid: {exc}")


def validate_generated_house_pages(errors: list[str]) -> None:
    if not SITE.exists():
        return

    representatives = list(GENERATED_REPRESENTATIVES)
    topics = sorted((SITE / "topics").glob("*/index.html")) if (SITE / "topics").exists() else []
    records = sorted((SITE / "records").glob("*/index.html")) if (SITE / "records").exists() else []
    contexts = sorted((SITE / "context").glob("*/index.html")) if (SITE / "context").exists() else []
    for collection in (topics, records, contexts):
        if collection:
            representatives.append(str(collection[0].relative_to(SITE)))

    expected_labels = [row["title"] for row in primary_gateway_rows(ROOT)]
    for rel in representatives:
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing generated House representative: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "site-housebar" not in text:
            errors.append(f"generated page lacks shared House bar: {rel}")
        if "app/site-system.css" not in text and "../app/site-system.css" not in text:
            if "site-system.css" not in text:
                errors.append(f"generated page does not load shared site system: {rel}")
        primary = primary_nav_fragment(text)
        if not primary:
            errors.append(f"generated page lacks primary Door nav: {rel}")
            continue
        for label in expected_labels:
            if label not in primary:
                errors.append(f"generated primary nav missing {label!r}: {rel}")
        if "World Map" in primary:
            errors.append(f"generated primary nav incorrectly exposes World Map as a Door: {rel}")


def main() -> int:
    errors: list[str] = []
    validate_source_architecture(errors)
    validate_house_authority(errors)

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
        archive_html = sorted((SITE / "archive").rglob("*.html")) if (SITE / "archive").exists() else []
        if archive_html:
            preview = ", ".join(str(path.relative_to(SITE)) for path in archive_html[:10])
            errors.append(f"historical archive HTML leaked into _site: {preview}")

    validate_generated_house_pages(errors)

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

    legacy_book = SITE / "great-book.html"
    if legacy_book.exists():
        book_text = legacy_book.read_text(encoding="utf-8", errors="replace")
        if 'content="noindex,follow"' not in book_text:
            errors.append("great-book.html compatibility route must be noindex,follow")
        if "./great-book/" not in book_text:
            errors.append("great-book.html compatibility route does not redirect to /great-book/")

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
        f"{len(CANONICAL_READER_SURFACES)} canonical reader IDs; shared generated House shell; concrete Culture field)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
