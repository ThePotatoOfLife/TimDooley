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
    "style.css",
    "reader.css",
    "house-page.css",
    "house-page.js",
    "potato-of-life-page.css",
    "axis-page.css",
    "axis-page.js",
    "quantum-page.css",
    "foundation-timeline-page.css",
    "foundation-timeline-page.js",
    "research-lab-page.css",
    "house-inhabitants-page.css",
    "house-inhabitants-page.js",
    "bible-study.css",
    "bible-library.css",
    "bible-atlas-navigation.css",
    "generated-knowledge.css",
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
    if not re.search(r"<html\b", text, flags=re.I):
        return text
    if not re.search(r"</head\s*>", text, flags=re.I) or not re.search(r"</body\s*>", text, flags=re.I):
        return text

    prefix = _relative_asset_prefix(page)
    if not _has_asset_reference(text, "site-access.css"):
        css = f'<link rel="stylesheet" href="{prefix}app/site-access.css?v={SHARED_ASSET_VERSIONS["site-access.css"]}">'
        text = re.sub(r"</head\s*>", css + "</head>", text, count=1, flags=re.I)
    if not _has_asset_reference(text, "site-access.js"):
        js = f'<script src="{prefix}app/site-access.js?v={SHARED_ASSET_VERSIONS["site-access.js"]}" defer></script>'
        text = re.sub(r"</body\s*>", js + "</body>", text, count=1, flags=re.I)
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
    "elevator/",
)

_ELEVATOR_PROJECTION = json.loads((ROOT / "data" / "house" / "elevator-spatial-projection.json").read_text(encoding="utf-8"))
_ELEVATOR_SUBROOMS = json.loads((ROOT / "data" / "house" / "subrooms.json").read_text(encoding="utf-8"))
_HOUSE_ROOMS = json.loads((ROOT / "data" / "house" / "rooms.json").read_text(encoding="utf-8"))
_ROOM_TITLE_BY_ID = {
    str(row.get("id")): str(row.get("title") or row.get("id"))
    for row in _HOUSE_ROOMS.get("rooms", [])
    if isinstance(row, dict) and row.get("status") == "active" and row.get("id")
}
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

_ACTIVE_SUBROOM_ROWS = [
    row for row in _ELEVATOR_SUBROOMS.get("subrooms", [])
    if isinstance(row, dict) and row.get("status") == "active" and row.get("id") and row.get("parent_room_id")
]
_SUBROOM_BY_ID = {str(row["id"]): row for row in _ACTIVE_SUBROOM_ROWS}
_SUBROOM_BY_ROUTE = {str(row.get("route_id") or row["id"]): row for row in _ACTIVE_SUBROOM_ROWS}
_SUBROOMS_BY_PARENT: dict[str, list[dict]] = {}
for _row in _ACTIVE_SUBROOM_ROWS:
    _SUBROOMS_BY_PARENT.setdefault(str(_row["parent_room_id"]), []).append(_row)

_SUBROOM_NAV_LABELS = {
    "canon-identities": "Core Identities & Roles",
    "theology-god-language": "Theology & God-language",
    "symbolic-architecture": "Symbolic Architecture & Cosmology",
    "practice-ethics": "Practice & Ethics",
    "provenance-evidence": "Provenance & Evidence",
    "memory-recovery": "Memory & Recovery",
    "witness-attestation": "Witness & Attestation",
    "chronology-events": "Events & Development",
    "developmental-genealogy": "Developmental Genealogy",
    "prediction-revelation-time": "Prediction & Revelation Time",
    "bible-christianity": "Bible & Christianity",
    "comparative-mythology": "Comparative Mythology",
    "esoteric-sacred-geometry": "Esoteric & Sacred Geometry",
    "other-traditions": "Other Traditions & Philosophies",
    "math-geometry": "Mathematics & Geometry",
    "physics-cosmology": "Physics & Cosmology",
    "systems-dynamics": "Systems & Dynamics",
    "model-testing": "Testing & Falsifiability",
    "potato-biology": "Potato Biology",
    "neurobiology": "Neurobiology",
    "whole-body": "Whole-body Physiology",
    "symbolic-body-comparison": "Symbolic Body Crosswalk",
    "politics-governance": "Politics & Governance",
    "law-justice": "Law & Justice",
    "economy-finance": "Economy & Finance",
    "infrastructure-capability": "Infrastructure & Capability",
    "geography-countries": "Geography",
    "internet-platforms": "Internet & Platforms",
    "subculture-group-formation": "Subculture & Group Formation",
    "information-ecology": "Information Ecology & Memory",
    "great-book-literature": "Great Book & Literature",
    "music-sound": "Music & Sound",
    "visual-art": "Visual Art & Composition",
    "games-simulations": "Games & Simulations",
    "house-architecture": "House Architecture",
    "open-questions": "Open Questions & Hypotheses",
    "experiments-formalization": "Experiments & Formalization",
    "research-programmes": "Research Programmes",
}
_PHILOSOPHY_FAMILY = (
    ("Philosophy", "philosophy/"),
    ("Knowledge & Belief", "philosophy/knowledge-belief.html"),
    ("Trust & Repair", "philosophy/trust-repair.html"),
    ("Attention & Agency", "philosophy/attention-agency.html"),
    ("Interpretive Justice", "philosophy/interpretive-justice.html"),
)

_PHILOSOPHY_CONTEXTS = {
    "philosophy/index.html",
    "philosophy/knowledge-belief.html",
    "philosophy/trust-repair.html",
    "philosophy/attention-agency.html",
    "philosophy/interpretive-justice.html",
    "rooms/inside/practice-ethics/index.html",
    "rooms/inside/other-traditions/index.html",
    "rooms/inside/great-book-literature/index.html",
    "rooms/inside/symbolic-architecture/index.html",
}

_PHILOSOPHY_ENTRY_CONTEXTS = {
    "potato-of-life/index.html",
    "tim-dooley/index.html",
    "religion/index.html",
    "science/index.html",
    "context/culture/index.html",
    "great-book/index.html",
    "works/index.html",
    "house/index.html",
    "rooms/potatoverse-canon/index.html",
    "rooms/traditions-texts/index.html",
    "rooms/science-formal-models/index.html",
    "rooms/works/index.html",
    "rooms/research-lab/index.html",
    "rooms/index.html",
}


_METAPHYSICS_ENTRY_CONTEXTS = {
    "philosophy/index.html",
    "philosophy/knowledge-belief.html",
    "philosophy/trust-repair.html",
    "philosophy/attention-agency.html",
    "philosophy/interpretive-justice.html",
    "potato-of-life/index.html",
    "religion/index.html",
    "house/index.html",
    "rooms/index.html",
    "rooms/potatoverse-canon/index.html",
    "rooms/traditions-texts/index.html",
    "rooms/inside/symbolic-architecture/index.html",
    "rooms/inside/practice-ethics/index.html",
    "rooms/inside/other-traditions/index.html",
}

_CONTEXT_SUBROOM_IDS = {
    "potato-of-life/index.html": ("canon-identities", "theology-god-language", "symbolic-architecture", "practice-ethics"),
    "tim-dooley/index.html": ("canon-identities", "chronology-events", "witness-attestation", "developmental-genealogy"),
    "religion/index.html": ("theology-god-language", "bible-christianity", "comparative-mythology", "other-traditions"),
    "philosophy/index.html": ("practice-ethics", "symbolic-architecture", "other-traditions"),
    "science/index.html": ("math-geometry", "physics-cosmology", "systems-dynamics", "model-testing"),
    "life-body/index.html": ("potato-biology", "neurobiology", "whole-body", "symbolic-body-comparison"),
    "world/index.html": ("geography-countries", "infrastructure-capability", "economy-finance", "politics-governance"),
    "politics/index.html": ("politics-governance", "law-justice", "economy-finance"),
    "economy/index.html": ("economy-finance", "infrastructure-capability", "geography-countries"),
    "law/index.html": ("law-justice", "politics-governance", "provenance-evidence"),
    "context/culture/index.html": ("internet-platforms", "subculture-group-formation", "information-ecology"),
    "timeline/index.html": ("chronology-events", "developmental-genealogy", "prediction-revelation-time"),
    "works/index.html": ("great-book-literature", "music-sound", "visual-art", "games-simulations"),
    "great-book/index.html": ("great-book-literature", "developmental-genealogy", "symbolic-architecture"),
    "house/index.html": ("house-architecture", "open-questions", "experiments-formalization", "research-programmes"),
    "context/source-authority/index.html": ("provenance-evidence", "memory-recovery", "witness-attestation"),
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
    """Stamp a canonical floor into single-floor pages for first paint.

    Home is deliberately exempt: it is the vertical Heaven → Plane → Below journey
    and owns a dedicated multi-realm compositor instead of one floor wallpaper.
    """
    if not re.search(r"<html\b", text, flags=re.I):
        return text
    route = _public_route_for_page(page)
    html_open = re.search(r"<html\b[^>]*>", text, flags=re.I)
    if not html_open:
        return text
    tag = html_open.group(0)
    if route == "/":
        tag = re.sub(r"\s+data-site-floor\s*=\s*[\"'][^\"']*[\"']", "", tag, count=1, flags=re.I)
        return text[:html_open.start()] + tag + text[html_open.end():]
    floor = _site_floor_for_route(route)
    if re.search(r"\bdata-site-floor\s*=", tag, flags=re.I):
        tag = re.sub(r"\bdata-site-floor\s*=\s*[\"'][^\"']*[\"']", f'data-site-floor="{floor}"', tag, count=1, flags=re.I)
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



PAGE_NAV_RE = re.compile(
    r'''<nav\b(?P<attrs>[^>]*\bclass=["'][^"']*\bpage-nav\b[^"']*["'][^>]*)>(?P<body>.*?)</nav\s*>''',
    re.I | re.S,
)
PAGE_NAV_ANCHOR_RE = re.compile(r'''<a\b[^>]*href=["'][^"']+["'][^>]*>.*?</a\s*>''', re.I | re.S)
PAGE_NAV_HREF_RE = re.compile(r'''href=["']([^"']+)["']''', re.I)
MAX_PAGE_NAV_LINKS = 12

PAGE_NAV_CLASS_RE = re.compile(r'''\bclass=["']([^"']*)["']''', re.I)

# The visual shell is universal; the destinations are not.  These families are
# deliberately visitor-facing and use the nouns a reader actually sees on pages.
_CONTEXT_NAV_FAMILIES = (
    (
        ("tim-dooley/",),
        (
            ("Tim Dooley", "tim-dooley/"),
            ("Story", "tim-dooley/story/"),
            ("Timeline", "timeline/"),
            ("Public Witness", "tim-dooley/public-witness/"),
            ("Claims", "tim-dooley/claims/"),
            ("Evidence", "tim-dooley/evidence/"),
            ("100,000 Hours", "tim-dooley/100000-hours/"),
            ("Works", "works/"),
        ),
    ),
    (
        ("potatoism/", "potato-of-life/", "axis/", "metaphysics/"),
        (
            ("Potatoism", "potatoism/"),
            ("Potato of Life", "potato-of-life/"),
            ("Grow", "potatoism/grow/"),
            ("Philosophy", "philosophy/"),
            ("Metaphysics", "metaphysics/"),
            ("Religion", "religion/"),
            ("Great Book", "great-book/"),
            ("Axis", "axis/"),
            ("FAQ", "faq/"),
        ),
    ),
    (
        ("religion/", "traditions/", "theology/"),
        (
            ("Religion", "religion/"),
            ("Bible", "traditions/bible/"),
            ("Christianity", "traditions/christianity/"),
            ("Judaism", "traditions/judaism/"),
            ("Islam", "traditions/islam/"),
            ("Comparative Cosmology", "traditions/comparative-cosmology/"),
            ("Trinity", "religion/trinity/"),
            ("Jesus & Tim", "traditions/bible/#compare"),
            ("God's Character", "religion/gods-character/"),
            ("Timeline", "timeline/"),
            ("Sources", "context/source-authority/"),
        ),
    ),
    (
        ("philosophy/",),
        (
            ("Philosophy", "philosophy/"),
            ("Knowledge & Belief", "philosophy/knowledge-belief.html"),
            ("Trust & Repair", "philosophy/trust-repair.html"),
            ("Attention & Agency", "philosophy/attention-agency.html"),
            ("Interpretive Justice", "philosophy/interpretive-justice.html"),
            ("Metaphysics", "metaphysics/"),
            ("Potatoism", "potatoism/"),
            ("Religion", "religion/"),
            ("Science", "science/"),
        ),
    ),
    (
        ("science/", "life-body/", "research-lab/"),
        (
            ("Science", "science/"),
            ("Research Map", "science/research-map/"),
            ("Spudlight", "science/spudlight/"),
            ("Quantum", "science/quantum/"),
            ("Celestial Particles", "science/celestial-particles/"),
            ("Vibe Gates", "science/vibe-gates/"),
            ("Life & Body", "life-body/"),
            ("Research Lab", "research-lab/"),
            ("Sources", "context/source-authority/"),
        ),
    ),
    (
        ("news/",),
        (
            ("News", "news/"),
            ("World", "world/"),
            ("World Map", "world-map/"),
            ("Politics", "politics/"),
            ("Economy", "economy/"),
            ("North", "north/"),
            ("Culture", "context/culture/"),
            ("Sources", "context/source-authority/"),
        ),
    ),
    (
        ("world/", "world-map/", "politics/", "economy/", "law/", "north/", "world-systems/", "israel-mesopotamia/"),
        (
            ("World", "world/"),
            ("World Map", "world-map/"),
            ("Politics", "politics/"),
            ("Economy", "economy/"),
            ("Law", "law/"),
            ("North", "north/"),
            ("World Systems", "world-systems/"),
            ("Israel / Mesopotamia", "israel-mesopotamia/"),
            ("Culture", "context/culture/"),
            ("Sources", "context/source-authority/"),
        ),
    ),
    (
        ("context/source-authority/",),
        (
            ("Sources", "context/source-authority/"),
            ("Tim Evidence", "tim-dooley/evidence/"),
            ("Public Witness", "tim-dooley/public-witness/"),
            ("Timeline", "timeline/"),
            ("Story", "tim-dooley/story/"),
            ("Research Lab", "research-lab/"),
            ("FAQ", "faq/"),
            ("A–Z", "index-a-z/"),
        ),
    ),
    (
        ("context/culture/",),
        (
            ("Culture", "context/culture/"),
            ("Turbles", "context/culture/turbles/"),
            ("World", "world/"),
            ("Politics", "politics/"),
            ("Philosophy", "philosophy/"),
            ("Religion", "religion/"),
            ("Sources", "context/source-authority/"),
            ("Research Lab", "research-lab/"),
        ),
    ),
    (
        ("context/",),
        (
            ("Context", "context/"),
            ("Sources", "context/source-authority/"),
            ("Culture", "context/culture/"),
            ("Timeline", "timeline/"),
            ("History", "history/"),
            ("Research Lab", "research-lab/"),
            ("Explore", "explore/"),
            ("A–Z", "index-a-z/"),
        ),
    ),
    (
        ("corporium/",),
        (
            ("Collection", "corporium/"),
            ("Tim Dooley", "tim-dooley/"),
            ("Potatoism", "potatoism/"),
            ("Philosophy", "philosophy/"),
            ("Life & Body", "life-body/"),
            ("Research Lab", "research-lab/"),
            ("Sources", "context/source-authority/"),
            ("Timeline", "timeline/"),
        ),
    ),
    (
        ("works/", "great-book/", "music/"),
        (
            ("Works", "works/"),
            ("Great Book", "great-book/"),
            ("Music", "music/"),
            ("Story", "tim-dooley/story/"),
            ("Timeline", "timeline/"),
            ("Tim Dooley", "tim-dooley/"),
            ("Visual Art", "rooms/inside/visual-art/"),
            ("Games", "rooms/inside/games-simulations/"),
        ),
    ),
    (
        ("timeline/", "chronology/", "history/"),
        (
            ("Timeline", "timeline/"),
            ("Story", "tim-dooley/story/"),
            ("History", "history/"),
            ("Chronology", "chronology/"),
            ("Foundations", "timeline/foundations/"),
            ("Tim Dooley", "tim-dooley/"),
            ("Religion", "religion/"),
            ("Sources", "context/source-authority/"),
        ),
    ),
    (
        ("house/", "elevator/"),
        (
            ("House", "house/"),
            ("Elevator", "elevator/"),
            ("Rooms", "rooms/"),
            ("Explore", "explore/"),
            ("Axis", "axis/"),
            ("Potatoism", "potatoism/"),
            ("Timeline", "timeline/"),
            ("Sources", "context/source-authority/"),
        ),
    ),
    (
        ("below/", "shadow-farm/"),
        (
            ("Below", "below/"),
            ("Hall of Shame", "below/dogs/"),
            ("Shadow Farm", "shadow-farm/"),
            ("TXT", "shadow-farm/txt/"),
            ("Culture", "context/culture/"),
            ("Sources", "context/source-authority/"),
            ("Hall of Heroes", "rooms/potatoverse-canon/beings/potatoes/"),
        ),
    ),
    (
        ("paths/",),
        (
            ("Paths", "paths/"),
            ("Explore", "explore/"),
            ("Questions", "questions/"),
            ("A–Z", "index-a-z/"),
            ("Story", "tim-dooley/story/"),
            ("Timeline", "timeline/"),
            ("Sources", "context/source-authority/"),
            ("Research Lab", "research-lab/"),
        ),
    ),
    (
        ("faq/", "learn/", "questions/", "explore/", "index-a-z/"),
        (
            ("Explore", "explore/"),
            ("FAQ", "faq/"),
            ("Learn", "learn/"),
            ("Questions", "questions/"),
            ("A–Z", "index-a-z/"),
            ("Tim Dooley", "tim-dooley/"),
            ("Potatoism", "potatoism/"),
            ("Religion", "religion/"),
            ("Science", "science/"),
            ("World", "world/"),
        ),
    ),
)

_ROOM_PUBLIC_HUBS = {
    "potatoverse-canon": ("Potatoism", "potatoism/"),
    "archive-sources": ("Sources", "context/source-authority/"),
    "time-history": ("Timeline", "timeline/"),
    "traditions-texts": ("Religion", "religion/"),
    "science-formal-models": ("Science", "science/"),
    "life-body": ("Life & Body", "life-body/"),
    "world-systems": ("World", "world/"),
    "culture-information": ("Culture", "context/culture/"),
    "works": ("Works", "works/"),
    "research-lab": ("Research Lab", "research-lab/"),
}


def _nav_anchor(page: Path, label: str, target: str, *, current: bool = False, cls: str = "") -> str:
    href = f"{_relative_asset_prefix(page)}{target}"
    classes = " ".join(part for part in (cls, "page-nav-current" if current else "") if part)
    class_attr = f' class="{classes}"' if classes else ""
    current_attr = ' aria-current="page"' if current else ""
    return f'<a{class_attr}{current_attr} href="{href}">{html.escape(label)}</a>'


def _route_matches(rel: str, target: str) -> bool:
    if target.endswith("/"):
        return rel == target + "index.html" or rel.startswith(target)
    return rel == target


def _contextual_nav_anchors(page: Path) -> list[str]:
    rel = page.relative_to(OUT).as_posix()
    for prefixes, entries in _CONTEXT_NAV_FAMILIES:
        if not any(rel.startswith(prefix) for prefix in prefixes):
            continue
        matching = [
            (label, target)
            for label, target in entries
            if _route_matches(rel, target)
        ]
        current_target = max(
            (target for _, target in matching),
            key=len,
            default=None,
        )
        return [
            _nav_anchor(page, label, target, current=(target == current_target), cls="page-nav-subject")
            for label, target in entries
        ]
    return []



def _subroom_nav_label(row: dict) -> str:
    subroom_id = str(row.get("id") or "")
    return _SUBROOM_NAV_LABELS.get(subroom_id, str(row.get("title") or subroom_id))


def _subroom_href(page: Path, row: dict) -> str:
    route_id = str(row.get("route_id") or row.get("id") or "")
    return f"{_relative_asset_prefix(page)}rooms/inside/{route_id}/"


def _anchor_href(anchor: str) -> str:
    match = PAGE_NAV_HREF_RE.search(anchor)
    return match.group(1) if match else ""


def _is_home_href(href: str, page: Path) -> bool:
    prefix = _relative_asset_prefix(page)
    normalized = href.strip()
    return normalized in {
        prefix,
        "./" if not prefix else prefix,
        prefix + "index.html",
        "/",
        "https://thepotatooflife.github.io/TimDooley/",
    }


def _home_anchor(page: Path) -> str:
    prefix = _relative_asset_prefix(page)
    href = prefix if prefix else "./"
    return f'<a class="page-nav-home" href="{href}">Home</a>'


def _rooms_anchor(page: Path) -> str:
    return f'<a class="page-nav-directory" href="{_relative_asset_prefix(page)}rooms/">Rooms</a>'


def _dwelling_context(page: Path) -> str | None:
    rel = page.relative_to(OUT).as_posix()
    nested = re.fullmatch(r"rooms/inside/([^/]+)/index\.html", rel)
    if nested:
        row = _SUBROOM_BY_ROUTE.get(nested.group(1))
        return str(row.get("parent_room_id")) if row else None

    parts = rel.split("/")
    if len(parts) >= 3 and parts[0] == "rooms" and parts[1] in _ROOM_TITLE_BY_ID:
        return parts[1]
    return None


def _dwelling_anchor(page: Path) -> str:
    dwelling_id = _dwelling_context(page)
    if not dwelling_id:
        return ""
    title = html.escape(_ROOM_TITLE_BY_ID.get(dwelling_id, dwelling_id))
    href = f"{_relative_asset_prefix(page)}rooms/{dwelling_id}/"
    return f'<a class="page-nav-dwelling" href="{href}">{title}</a>'


def _current_subroom_anchor(page: Path) -> str:
    rel = page.relative_to(OUT).as_posix()
    nested = re.fullmatch(r"rooms/inside/([^/]+)/index\.html", rel)
    if not nested:
        return ""
    row = _SUBROOM_BY_ROUTE.get(nested.group(1))
    if not row:
        return ""
    label = html.escape(_subroom_nav_label(row))
    href = _subroom_href(page, row)
    return f'<a class="page-nav-current" href="{href}" aria-current="page">{label}</a>'


def _room_candidate_anchor(page: Path, row: dict) -> str:
    label = html.escape(_subroom_nav_label(row))
    href = _subroom_href(page, row)
    return f'<a class="page-nav-room" href="{href}">{label}</a>'


def _anchor_label(anchor: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", anchor)).strip()


def _clean_nav_label(anchor: str) -> str:
    return _anchor_label(anchor).lstrip("←").strip()


def _is_rooms_anchor(anchor: str) -> bool:
    return _clean_nav_label(anchor) in {"Rooms", "All Rooms"}


def _is_redundant_architecture_anchor(anchor: str, page: Path) -> bool:
    label = _clean_nav_label(anchor)
    if label in {"All Rooms", "Rooms", "Spatial Room", "Parent Dwelling"}:
        return True
    dwelling_id = _dwelling_context(page)
    if dwelling_id and label == _ROOM_TITLE_BY_ID.get(dwelling_id):
        return True
    return False


def _room_nav_candidates(page: Path) -> list[dict]:
    """Return the useful Room neighborhood without artificially hiding siblings."""
    rel = page.relative_to(OUT).as_posix()

    contextual = _CONTEXT_SUBROOM_IDS.get(rel)
    if contextual:
        return [row for sid in contextual if (row := _SUBROOM_BY_ID.get(sid))]

    top = re.fullmatch(r"rooms/([^/]+)/index\.html", rel)
    if top and top.group(1) != "inside":
        # Dwellings are intentionally small (3–5 Rooms). Show the whole family.
        return list(_SUBROOMS_BY_PARENT.get(top.group(1), []))

    nested = re.fullmatch(r"rooms/inside/([^/]+)/index\.html", rel)
    if not nested:
        return []

    current = _SUBROOM_BY_ROUTE.get(nested.group(1))
    if not current:
        return []

    current_id = str(current.get("id") or "")
    parent_id = str(current.get("parent_room_id") or "")
    siblings = [
        row for row in _SUBROOMS_BY_PARENT.get(parent_id, [])
        if str(row.get("id") or "") != current_id
    ]

    # Add up to two cross-family adjacent Rooms after the complete sibling family.
    seen = {current_id, *(str(row.get("id") or "") for row in siblings)}
    cross_adjacent: list[dict] = []
    for adjacent_id in current.get("adjacent_subroom_ids", []):
        row = _SUBROOM_BY_ID.get(str(adjacent_id))
        if not row:
            continue
        row_id = str(row.get("id") or "")
        if row_id in seen:
            continue
        seen.add(row_id)
        cross_adjacent.append(row)
        if len(cross_adjacent) >= 2:
            break

    return siblings + cross_adjacent


def _philosophy_family_anchors(page: Path) -> str:
    rel = page.relative_to(OUT).as_posix()
    if rel not in _PHILOSOPHY_CONTEXTS:
        return ""
    prefix = _relative_asset_prefix(page)
    out: list[str] = []
    for label, target in _PHILOSOPHY_FAMILY:
        href = prefix + target
        current = ""
        if rel == target.rstrip("/"):
            current = ' aria-current="page" class="page-nav-current"'
        elif rel == target + "index.html":
            current = ' aria-current="page" class="page-nav-current"'
        out.append(f'<a href="{href}"{current}>{html.escape(label)}</a>')
    return "".join(out)


def _philosophy_entry_anchor(page: Path) -> str:
    rel = page.relative_to(OUT).as_posix()
    if rel in _PHILOSOPHY_CONTEXTS:
        return ""
    if rel not in _PHILOSOPHY_ENTRY_CONTEXTS:
        return ""
    return f'<a class="page-nav-subject" href="{_relative_asset_prefix(page)}philosophy/">Philosophy</a>'


def _metaphysics_entry_anchor(page: Path) -> str:
    rel = page.relative_to(OUT).as_posix()
    if rel == "metaphysics/index.html" or rel not in _METAPHYSICS_ENTRY_CONTEXTS:
        return ""
    return f'<a class="page-nav-subject" href="{_relative_asset_prefix(page)}metaphysics/">Potato Metaphysics</a>'


def _is_philosophy_family_anchor(anchor: str, page: Path) -> bool:
    rel = page.relative_to(OUT).as_posix()
    if rel not in _PHILOSOPHY_CONTEXTS:
        return False
    label = _clean_nav_label(anchor)
    return label in {label for label, _ in _PHILOSOPHY_FAMILY}


def _is_current_subroom_anchor(anchor: str, page: Path) -> bool:
    rel = page.relative_to(OUT).as_posix()
    nested = re.fullmatch(r"rooms/inside/([^/]+)/index\.html", rel)
    if not nested:
        return False
    current = _SUBROOM_BY_ROUTE.get(nested.group(1))
    if not current:
        return False
    return _anchor_href(anchor) == _subroom_href(page, current)


def normalize_page_nav(text: str, page: Path) -> str:
    """Normalize only the first, top-of-page sub-header.

    Geometry and interaction are universal; destinations are contextual.  The
    sub-header should reveal the subject neighborhood a reader can actually use,
    while House topology stays inside House/Room pages instead of colonizing the
    whole site.
    """

    if page == OUT / "index.html":
        return text

    rel = page.relative_to(OUT).as_posix()

    def rewrite(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        body = match.group("body")
        authored = PAGE_NAV_ANCHOR_RE.findall(body)
        pieces: list[str] = []
        seen_hrefs: set[str] = set()
        seen_labels: set[str] = set()

        def add(anchor: str) -> None:
            if not anchor or len(pieces) >= MAX_PAGE_NAV_LINKS:
                return
            href = _anchor_href(anchor)
            label = _clean_nav_label(anchor)
            if not href or href in seen_hrefs or label in seen_labels:
                return
            seen_hrefs.add(href)
            seen_labels.add(label)
            pieces.append(anchor)

        add(_home_anchor(page))

        nested = re.fullmatch(r"rooms/inside/([^/]+)/index\.html", rel)
        dwelling = re.fullmatch(r"rooms/([^/]+)/index\.html", rel)

        if nested:
            current = _SUBROOM_BY_ROUTE.get(nested.group(1))
            if current:
                parent_id = str(current.get("parent_room_id") or "")
                hub = _ROOM_PUBLIC_HUBS.get(parent_id)
                if hub:
                    add(_nav_anchor(page, hub[0], hub[1], cls="page-nav-subject"))
                add(_dwelling_anchor(page))
                for row in _room_nav_candidates(page):
                    add(_room_candidate_anchor(page, row))
        elif dwelling and dwelling.group(1) != "inside":
            room_id = dwelling.group(1)
            hub = _ROOM_PUBLIC_HUBS.get(room_id)
            if hub:
                add(_nav_anchor(page, hub[0], hub[1], cls="page-nav-subject"))
            for row in _room_nav_candidates(page):
                add(_room_candidate_anchor(page, row))
        else:
            for anchor in _contextual_nav_anchors(page):
                add(anchor)

        # Authored local links are useful when they describe this exact page. Keep
        # them after the contextual family, but discard old generated architecture.
        for anchor in authored:
            href = _anchor_href(anchor)
            classes_match = PAGE_NAV_CLASS_RE.search(anchor)
            classes = set(classes_match.group(1).split()) if classes_match else set()
            label = _clean_nav_label(anchor)
            if (
                _is_home_href(href, page)
                or _is_rooms_anchor(anchor)
                or _is_redundant_architecture_anchor(anchor, page)
                or classes.intersection({
                    "page-nav-home",
                    "page-nav-directory",
                    "page-nav-dwelling",
                    "page-nav-current",
                    "page-nav-room",
                    "page-nav-subject",
                })
                or label in {"House", "All Rooms", "Parent Dwelling", "Spatial Room"}
            ):
                continue
            add(anchor)

        return f"<nav{attrs}>{''.join(pieces)}</nav>"

    # Pages sometimes reuse .page-nav for source trails farther down. Only the
    # first instance is the actual site sub-header.
    return PAGE_NAV_RE.sub(rewrite, text, count=1)


def patch_page_navs(out: Path = OUT) -> set[Path]:
    changed: set[Path] = set()
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8", errors="replace")
        projected = normalize_page_nav(text, page)
        if projected != text:
            page.write_text(projected, encoding="utf-8")
            changed.add(page)
    return changed


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

    changed.update(patch_page_navs(OUT))
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

    # Special public-page rewrites above may touch page-nav markup. Re-apply the
    # canonical subheader contract last so Home-first order cannot drift.
    changed.update(patch_page_navs(OUT))

    print(f"Applied public navigation cleanup to {len(changed)} generated page(s).")


if __name__ == "__main__":
    main()
