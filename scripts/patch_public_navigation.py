#!/usr/bin/env python3
"""Normalize visitor-facing navigation in the generated Pages artifact.

The repository intentionally preserves historical/internal names and research strata.
This pass only cleans the deployed visitor surface: retired homepage branch hashes,
parent-hub continuity, duplicate navigation choices, visitor-facing vocabulary, and
small public-only capability projections that should not mutate legacy source strata.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

SHARED_ASSET_NAMES = (
    "site-system.css",
    "site-access.css",
    "site-access.js",
    "site-elevator.css",
    "site-elevator.js",
    "house-journey.js",
    "body-relational-lens.js",
    "tts-drawer.css",
    "tts-reader.js",
    "tts-drawer.js",
    "longform-tts-adapter.js",
    "site-tts.js",
)


def _shared_asset_version(asset: str) -> str:
    # During Pages finalization, hash the exact built bytes. Earlier build passes may
    # rewrite nested asset URLs (for example the tree SVG fingerprint inside
    # site-elevator.css), so hashing ROOT here could give HTML a stale CSS cache key.
    built = OUT / "app" / asset
    source = ROOT / "app" / asset
    path = built if built.is_file() else source
    if not path.is_file():
        raise FileNotFoundError(f"shared UI asset missing: {source.relative_to(ROOT)}")
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


SHARED_ASSET_VERSIONS = {
    asset: _shared_asset_version(asset)
    for asset in SHARED_ASSET_NAMES
}

ROOT_BRANCH_HREF = re.compile(
    r'''href=(?P<quote>["'])(?P<prefix>(?:\.\./|\./)*)#branch=(?P<branch>[^"']+)(?P=quote)''',
    re.I,
)
ABSOLUTE_ROOT_BRANCH = "https://thepotatooflife.github.io/TimDooley/#branch="
ABSOLUTE_EXPLORE_BRANCH = "https://thepotatooflife.github.io/TimDooley/explore/#branch="
PUBLIC_LABEL_REPLACEMENTS = (
    (">Timeline</a>", ">Timeline</a>"),
    (">Corporium</a>", ">Collection</a>"),
    (">Source authority</a>", ">Sources</a>"),
    (">Tim dossier</a>", ">Tim Dooley</a>"),
    ("← Potato of Life archive</a>", "← Home</a>"),
)
LEGACY_TTS_READERS = {
    "rooms/index.html": {
        "id": "rooms",
        "root": ".rooms-page",
        "label": "Rooms",
        "all_label": "Whole Rooms directory",
        "exclude": "#rooms-tts,.page-nav,.deep",
        "asset_prefix": "../",
    },
    "history/index.html": {
        "id": "history",
        "root": ".page",
        "label": "History & Time",
        "all_label": "Whole History & Time room",
        "exclude": "#history-tts,.page-nav,.deep",
        "asset_prefix": "../",
    },
    "law/index.html": {
        "id": "law",
        "root": ".page",
        "label": "Law & Justice",
        "all_label": "Whole Law & Justice room",
        "exclude": "#law-tts,.page-nav,.deep",
        "asset_prefix": "../",
    },
    "economy/index.html": {
        "id": "economy",
        "root": ".page",
        "label": "Economy & Finance",
        "all_label": "Whole Economy & Finance room",
        "exclude": "#economy-tts,.page-nav,.deep",
        "asset_prefix": "../",
    },
    "world-systems/index.html": {
        "id": "world-systems",
        "root": ".wrap",
        "label": "World Systems",
        "all_label": "Whole World Systems room",
        "exclude": "#world-systems-tts,.family,.deep",
        "asset_prefix": "../",
    },
    "politics/index.html": {
        "id": "politics",
        "root": ".longform-doc",
        "label": "Politics & Geopolitics",
        "all_label": "Whole politics reader",
        "exclude": "#politics-tts,.status",
        "asset_prefix": "../",
    },
    "timeline/index.html": {
        "id": "timeline",
        "root": ".page",
        "label": "Timeline",
        "all_label": "Whole timeline",
        "exclude": "#timeline-tts,.nav,.paths",
        "asset_prefix": "../",
    },
    "works/index.html": {
        "id": "works",
        "root": ".works-page",
        "label": "Works",
        "all_label": "Whole Works room",
        "exclude": "#works-tts,.page-nav,.deep",
        "asset_prefix": "../",
    },
    "science/index.html": {
        "id": "science",
        "root": ".science-page",
        "label": "Science",
        "all_label": "Whole Science room",
        "exclude": "#science-tts,.page-nav,.science-controls,.science-library-status,.science-empty,.science-deep",
        "asset_prefix": "../",
    },
    "context/source-authority/index.html": {
        "id": "source-authority",
        "root": ".wrap",
        "label": "Sources & Evidence",
        "all_label": "Whole Sources & Evidence reader",
        "exclude": "#source-authority-tts,.nav,.small",
        "asset_prefix": "../../",
    },
    "philosophy/interpretive-justice.html": {
        "id": "interpretive-justice",
        "root": ".philosophy-page",
        "label": "Interpretive Justice",
        "all_label": "Whole Interpretive Justice reader",
        "exclude": "#interpretive-justice-tts,.page-nav,.deep-source",
        "asset_prefix": "../",
    },
}


SITE_ACCESS_QUIET_PREFIXES = (
    "tools/tts/",
)

def inject_site_access(text: str, page: Path) -> str:
    """Add the universal fixed quick-access dock without adding content-flow height."""
    rel = page.relative_to(OUT).as_posix()
    if any(rel.startswith(prefix) for prefix in SITE_ACCESS_QUIET_PREFIXES):
        return text
    if not re.search(r"<html\\b", text, flags=re.I):
        return text
    if not re.search(r"</head\\s*>", text, flags=re.I) or not re.search(r"</body\\s*>", text, flags=re.I):
        return text

    prefix = _relative_asset_prefix(page)
    if not _has_asset_reference(text, "site-access.css"):
        css = f'<link rel="stylesheet" href="{prefix}app/site-access.css?v={SHARED_ASSET_VERSIONS["site-access.css"]}">'
        text = re.sub(r"</head\\s*>", css + "</head>", text, count=1, flags=re.I)
    if not _has_asset_reference(text, "site-access.js"):
        js = f'<script src="{prefix}app/site-access.js?v={SHARED_ASSET_VERSIONS["site-access.js"]}" defer></script>'
        text = re.sub(r"</body\\s*>", js + "</body>", text, count=1, flags=re.I)
    return text

def patch_site_access(out: Path = OUT) -> set[Path]:
    changed: set[Path] = set()
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8", errors="replace")
        projected = inject_site_access(text, page)
        if projected != text:
            page.write_text(projected, encoding="utf-8")
            changed.add(page)
    return changed


SITE_ELEVATOR_QUIET_PREFIXES = (
    "tools/tts/",
)

_ELEVATOR_PROJECTION = json.loads((ROOT / "data" / "house" / "elevator-spatial-projection.json").read_text(encoding="utf-8"))
_ELEVATOR_SUBROOMS = json.loads((ROOT / "data" / "house" / "subrooms.json").read_text(encoding="utf-8"))
_ELEVATOR_DWELLING_LEVEL = {
    str(row.get("id")): str(row.get("primary_level") or "plane")
    for row in _ELEVATOR_PROJECTION.get("dwellings", [])
    if isinstance(row, dict) and row.get("id")
}
_ELEVATOR_SUBROOM_PARENT = {
    str(row.get("route_id") or row.get("id")): str(row.get("parent_room_id"))
    for row in _ELEVATOR_SUBROOMS.get("subrooms", [])
    if isinstance(row, dict) and row.get("status") == "active" and row.get("id") and row.get("parent_room_id")
}
_ELEVATOR_ROUTE_CONTEXTS = sorted(
    [
        row for row in _ELEVATOR_PROJECTION.get("route_contexts", [])
        if isinstance(row, dict) and isinstance(row.get("match"), str) and row.get("level_id") in {"heaven", "plane", "below"}
    ],
    key=lambda row: len(str(row.get("match") or "")),
    reverse=True,
)

def _public_route_for_page(page: Path) -> str:
    rel = page.relative_to(OUT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-10]
    return "/" + rel

def _site_floor_for_route(route: str) -> str:
    normalized = "/" + str(route or "/").lstrip("/")
    if not normalized.endswith("/") and "." not in normalized.rsplit("/", 1)[-1]:
        normalized += "/"

    inside = re.match(r"^/rooms/inside/([^/]+)(?:/|$)", normalized)
    if inside:
        parent = _ELEVATOR_SUBROOM_PARENT.get(inside.group(1))
        if parent:
            return _ELEVATOR_DWELLING_LEVEL.get(parent, "plane")

    room = re.match(r"^/rooms/([^/]+)(?:/|$)", normalized)
    if room and room.group(1) != "inside":
        return _ELEVATOR_DWELLING_LEVEL.get(room.group(1), "plane")

    for row in _ELEVATOR_ROUTE_CONTEXTS:
        match = str(row.get("match") or "")
        if match == "/":
            if normalized == "/":
                return str(row.get("level_id") or "plane")
            continue
        if normalized == match or normalized.startswith(match):
            return str(row.get("level_id") or "plane")
    return "plane"

def inject_site_floor(text: str, page: Path) -> str:
    """Stamp the canonical floor into built HTML so scenery exists at first paint."""
    if not re.search(r"<html\b", text, flags=re.I):
        return text
    floor = _site_floor_for_route(_public_route_for_page(page))
    html_open = re.search(r"<html\b[^>]*>", text, flags=re.I)
    if not html_open:
        return text
    tag = html_open.group(0)
    if re.search(r"\bdata-site-floor\s*=", tag, flags=re.I):
        tag = re.sub(r'\bdata-site-floor\s*=\s*["\'][^"\']*["\']', f'data-site-floor="{floor}"', tag, count=1, flags=re.I)
    else:
        tag = tag[:-1] + f' data-site-floor="{floor}">'
    return text[:html_open.start()] + tag + text[html_open.end():]

def patch_site_floors(out: Path = OUT) -> set[Path]:
    changed: set[Path] = set()
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8", errors="replace")
        projected = inject_site_floor(text, page)
        if projected != text:
            page.write_text(projected, encoding="utf-8")
            changed.add(page)
    return changed

def inject_site_elevator(text: str, page: Path) -> str:
    """Add the universal three-floor House orientation header."""
    rel = page.relative_to(OUT).as_posix()
    if any(rel.startswith(prefix) for prefix in SITE_ELEVATOR_QUIET_PREFIXES):
        return text
    if not re.search(r"<html\b", text, flags=re.I):
        return text
    if not re.search(r"</head\s*>", text, flags=re.I) or not re.search(r"</body\s*>", text, flags=re.I):
        return text

    prefix = _relative_asset_prefix(page)
    if not _has_asset_reference(text, "site-elevator.css"):
        css = f'<link rel="stylesheet" href="{prefix}app/site-elevator.css?v={SHARED_ASSET_VERSIONS["site-elevator.css"]}">'
        text = re.sub(r"</head\s*>", css + "</head>", text, count=1, flags=re.I)
    if not _has_asset_reference(text, "site-elevator.js"):
        js = f'<script src="{prefix}app/site-elevator.js?v={SHARED_ASSET_VERSIONS["site-elevator.js"]}" defer></script>'
        text = re.sub(r"</body\s*>", js + "</body>", text, count=1, flags=re.I)
    return text

def patch_site_elevator(out: Path = OUT) -> set[Path]:
    changed: set[Path] = set()
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8", errors="replace")
        projected = inject_site_elevator(text, page)
        if projected != text:
            page.write_text(projected, encoding="utf-8")
            changed.add(page)
    return changed


PROJECT_COMPASS_QUIET_PREFIXES = (
    "world-map/",
    "elevator/",
    "rooms/objects/",
    "index-a-z/",
    "tools/tts/",
)

def inject_project_compass(text: str, page: Path) -> str:
    """Add the compact project orientation layer to ordinary generated reader pages."""
    rel = page.relative_to(OUT).as_posix()
    if rel == "index.html" or any(rel.startswith(prefix) for prefix in PROJECT_COMPASS_QUIET_PREFIXES):
        return text
    if "project-compass.js" in text or "project-compass.css" in text:
        return text
    if not re.search(r"<html\\b", text, flags=re.I):
        return text
    if not re.search(r"<main\\b", text, flags=re.I):
        return text
    if not re.search(r"</head\\s*>", text, flags=re.I) or not re.search(r"</body\\s*>", text, flags=re.I):
        return text

    prefix = _relative_asset_prefix(page)
    css = f'<link rel="stylesheet" href="{prefix}app/project-compass.css?v=20260920a">'
    js = f'<script src="{prefix}app/project-compass.js?v=20260920a" defer></script>'
    text = re.sub(r"</head\\s*>", css + "</head>", text, count=1, flags=re.I)
    text = re.sub(r"</body\\s*>", js + "</body>", text, count=1, flags=re.I)
    return text

def patch_project_compass(out: Path = OUT) -> set[Path]:
    changed: set[Path] = set()
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8", errors="replace")
        projected = inject_project_compass(text, page)
        if projected != text:
            page.write_text(projected, encoding="utf-8")
            changed.add(page)
    return changed


UNIVERSAL_TTS_QUIET_PREFIXES = (
    "world-map/",
    "rooms/objects/",
    "index-a-z/",
    "tools/tts/",
)

def _relative_asset_prefix(page: Path) -> str:
    rel = page.relative_to(OUT)
    depth = max(0, len(rel.parts) - 1)
    return "../" * depth

def _has_asset_reference(text: str, asset: str) -> bool:
    pattern = rf'''(?:href|src)\s*=\s*["'][^"']*app/{re.escape(asset)}(?:\?[^"']*)?["']'''
    return re.search(pattern, text, flags=re.I) is not None


def normalize_shared_asset_versions(text: str) -> str:
    """Stamp shared UI asset attributes with deterministic content-derived versions."""
    for asset, version in SHARED_ASSET_VERSIONS.items():
        pattern = rf'''(?P<head>\b(?:href|src)\s*=\s*["'][^"']*app/{re.escape(asset)})(?:\?v=[A-Za-z0-9._-]+)?(?P<tail>["'])'''
        text = re.sub(
            pattern,
            lambda match: f'{match.group("head")}?v={version}{match.group("tail")}',
            text,
            flags=re.I,
        )
    return text


def patch_shared_asset_versions(out: Path = OUT) -> set[Path]:
    changed: set[Path] = set()
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8", errors="replace")
        projected = normalize_shared_asset_versions(text)
        if projected != text:
            page.write_text(projected, encoding="utf-8")
            changed.add(page)
    return changed


def inject_universal_tts(text: str, page: Path) -> str:
    """Ensure every deployed prose HTML document has shared TTS coverage.

    Existing specialist/declarative readers are preserved. Full-page TTS is not
    projected into deliberately control-heavy explorers; those remain scoped to
    selected/active-object reading. Fragments without a full document shell are
    ignored.
    """
    rel = page.relative_to(OUT).as_posix()
    quiet = any(rel.startswith(prefix) for prefix in UNIVERSAL_TTS_QUIET_PREFIXES)
    if "site-tts.js" in text or "tts-drawer.js" in text:
        return text
    if not re.search(r"<html\b", text, flags=re.I):
        return text
    if not quiet and not re.search(r"<main\b", text, flags=re.I):
        return text
    if not re.search(r"</body\s*>", text, flags=re.I):
        return text

    prefix = _relative_asset_prefix(page)
    tag = f'<script src="{prefix}app/site-tts.js" defer></script>'
    return re.sub(r"</body\s*>", tag + "</body>", text, count=1, flags=re.I)

def patch_universal_tts(out: Path) -> set[Path]:
    changed: set[Path] = set()
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8", errors="replace")
        projected = inject_universal_tts(text, page)
        if projected != text:
            page.write_text(projected, encoding="utf-8")
            changed.add(page)
    return changed

def patch_text(path: Path, replacements: tuple[tuple[str, str], ...] = ()) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def normalize_public_surface(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text

    def route(match: re.Match[str]) -> str:
        quote = match.group("quote")
        prefix = match.group("prefix")
        branch = match.group("branch")
        return f"href={quote}{prefix}explore/#branch={branch}{quote}"

    text = ROOT_BRANCH_HREF.sub(route, text)
    text = text.replace(ABSOLUTE_ROOT_BRANCH, ABSOLUTE_EXPLORE_BRANCH)
    for old, new in PUBLIC_LABEL_REPLACEMENTS:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def inject_legacy_tts_reader(text: str, config: dict[str, str]) -> str:
    """Project the shared long-form TTS reader into generated public HTML.

    This is intentionally a generated-artifact transform. It keeps source pages
    stable while giving mature public readers the same shared speech capability.
    The transform is fail-closed and idempotent.
    """
    reader_id = str(config.get("id", "")).strip()
    root_selector = str(config.get("root", "")).strip()
    if not reader_id or not root_selector:
        return text

    host_id = f"{reader_id}-tts"
    if f'id="{host_id}"' in text or f"id='{host_id}'" in text:
        return text

    if not re.search(r"</head\s*>", text, flags=re.I) or not re.search(r"</body\s*>", text, flags=re.I):
        return text
    if not re.search(r"<main\b[^>]*>", text, flags=re.I):
        return text

    prefix = str(config.get("asset_prefix", ""))
    label = html.escape(str(config.get("label", "Read aloud")), quote=True)
    all_label = html.escape(str(config.get("all_label", "Whole reader")), quote=True)
    exclude = html.escape(str(config.get("exclude", f"#{host_id}")), quote=True)
    root_attr = html.escape(root_selector, quote=True)
    id_attr = html.escape(reader_id, quote=True)

    stylesheet = f'<link rel="stylesheet" href="{prefix}app/tts-drawer.css">'
    host = (
        f'<div id="{html.escape(host_id, quote=True)}" data-tts-longform '
        f'data-tts-root="{root_attr}" data-tts-id="{id_attr}" data-tts-label="{label}" '
        f'data-tts-all-label="{all_label}" data-tts-selection-label="Selection" '
        f'data-tts-exclude="{exclude}"></div>'
    )
    scripts = (
        f'<script src="{prefix}app/tts-reader.js"></script>'
        f'<script src="{prefix}app/tts-drawer.js"></script>'
        f'<script src="{prefix}app/longform-tts-adapter.js"></script>'
    )

    text = re.sub(r"</head\s*>", stylesheet + "</head>", text, count=1, flags=re.I)

    # The head mutation changes character offsets, so resolve main again before
    # choosing a placement inside the transformed document.
    main_match = re.search(r"<main\b[^>]*>", text, flags=re.I)
    if not main_match:
        return text

    # Prefer placing the reader immediately after the page's first navigation row.
    # Falling back to the main opening tag still keeps the player close to the
    # readable content while allowing the configured root to be narrower than main.
    nav_match = re.search(r"<nav\b[^>]*>.*?</nav\s*>", text[main_match.end():], flags=re.I | re.S)
    if nav_match:
        insert_at = main_match.end() + nav_match.end()
    else:
        insert_at = main_match.end()
    text = text[:insert_at] + host + text[insert_at:]
    text = re.sub(r"</body\s*>", scripts + "</body>", text, count=1, flags=re.I)
    return text


def patch_legacy_tts_readers(out: Path = OUT) -> set[Path]:
    changed: set[Path] = set()
    for rel, config in LEGACY_TTS_READERS.items():
        path = out / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        projected = inject_legacy_tts_reader(text, config)
        if projected == text:
            continue
        path.write_text(projected, encoding="utf-8")
        changed.add(path)
    return changed


def main() -> None:
    if not OUT.exists():
        raise SystemExit("_site does not exist; build_site.py must run first")

    changed: set[Path] = set()
    for page in OUT.rglob("*.html"):
        if page == OUT / "explore" / "index.html":
            continue
        if normalize_public_surface(page):
            changed.add(page)

    changed.update(patch_shared_asset_versions(OUT))
    changed.update(patch_legacy_tts_readers(OUT))
    changed.update(patch_site_floors(OUT))
    changed.update(patch_site_elevator(OUT))
    changed.update(patch_site_access(OUT))
    changed.update(patch_universal_tts(OUT))

    religion = OUT / "religion" / "index.html"
    if patch_text(
        religion,
        (
            (
                '<div class="deep" aria-label="Deeper religion routes"><a href="../context/source-authority/">Sources & evidence</a><a href="../explore/#branch=traditions">Deep traditions archive</a><a href="../explore/#branch=spirit">Spirit & theology archive</a><a href="../index-a-z/">A–Z</a></div>',
                '<div class="deep" aria-label="Deeper religion routes"><a href="../context/source-authority/">Sources & evidence</a><a href="../index-a-z/">A–Z</a><a href="../explore/">Explore relationships</a></div>',
            ),
        ),
    ):
        changed.add(religion)

    bible = OUT / "traditions" / "bible" / "index.html"
    if patch_text(
        bible,
        (
            (
                '<nav class="page-nav" aria-label="Page navigation"><a href="../../">← Home</a><a href="../../tim-dooley/">Tim Dooley</a><a href="../../timeline/">Timeline</a><a href="../../context/source-authority/">Sources</a><a href="../../faq/">FAQ</a></nav>',
                '<nav class="page-nav" aria-label="Page navigation"><a href="../../religion/">← Religion</a><a href="../../">Home</a><a href="../../tim-dooley/">Tim Dooley</a><a href="../../timeline/">Timeline</a><a href="../../context/source-authority/">Sources</a></nav>',
            ),
        ),
    ):
        changed.add(bible)

    vesica = OUT / "traditions" / "vesica" / "index.html"
    if patch_text(
        vesica,
        (
            (
                '<nav class="nav"><a href="../../">← Home</a><a href="../../context/">Context &amp; evidence</a><a href="../../tim-dooley/">Tim Dooley</a><a href="../../science/spudlight/">Spudlight</a></nav>',
                '<nav class="nav"><a href="../../religion/">← Religion</a><a href="../../">Home</a><a href="../bible/">Bible</a><a href="../../science/">Science</a><a href="../../context/source-authority/">Sources</a></nav>',
            ),
            (
                '"name":"Traditions","item":"https://thepotatooflife.github.io/TimDooley/explore/#branch=traditions"',
                '"name":"Religion","item":"https://thepotatooflife.github.io/TimDooley/religion/"',
            ),
        ),
    ):
        changed.add(vesica)

    print(f"Applied public navigation cleanup to {len(changed)} generated page(s).")


if __name__ == "__main__":
    main()
