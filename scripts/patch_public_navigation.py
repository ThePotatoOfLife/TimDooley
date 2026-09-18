#!/usr/bin/env python3
"""Normalize visitor-facing navigation in the generated Pages artifact.

The repository intentionally preserves historical/internal names and research strata.
This pass only cleans the deployed visitor surface: retired homepage branch hashes,
parent-hub continuity, duplicate navigation choices, visitor-facing vocabulary, and
small public-only capability projections that should not mutate legacy source strata.
"""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
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
HOUSE_BRIDGE_EXCLUDED = {"home", "potato-of-life", "house", "rooms", "explore", "world-map", "questions", "index-a-z"}
HOUSE_BRIDGE_STYLE = """<style data-house-bridge-style>
.house-bridge{margin:18px 0 34px;padding:14px 16px;border:1px solid var(--site-line,#30382f);border-radius:12px;background:color-mix(in srgb,var(--site-panel,#0f130f) 88%,transparent);font-family:var(--site-font-sans,system-ui,sans-serif)}
.house-bridge__top{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}.house-bridge__trail{display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px}.house-bridge__trail a{color:var(--site-green,#b8dc82);text-decoration:none}.house-bridge__trail span{color:var(--site-faint,#727a70)}
.house-bridge__kind{color:var(--site-gold,#d8b56b);font-size:10px;font-weight:800;letter-spacing:.11em;text-transform:uppercase}.house-bridge__body{display:grid;grid-template-columns:minmax(180px,.7fr) 1.3fr;gap:16px;margin-top:10px;padding-top:10px;border-top:1px solid var(--site-line,#30382f)}
.house-bridge__body p{margin:0;color:var(--site-muted,#9fa79d);font-size:11px;line-height:1.45}.house-bridge__chips{display:flex;flex-wrap:wrap;gap:6px}.house-bridge__chip{border:1px solid var(--site-line,#30382f);border-radius:999px;padding:3px 7px;color:var(--site-muted,#9fa79d);font-size:10px}.house-bridge__rooms-link{color:var(--site-green,#b8dc82);font-size:11px;text-decoration:none;white-space:nowrap}
@media(max-width:700px){.house-bridge__body{grid-template-columns:1fr}.house-bridge{margin-bottom:24px}}
</style>"""

LEGACY_TTS_READERS = {
    "shadow-farm/index.html": {
        "id": "shadow-farm",
        "root": ".page",
        "label": "The Farm & Trees of Strife",
        "all_label": "Whole deep reader",
        "exclude": "#shadow-farm-tts,.nav",
        "asset_prefix": "../",
    },
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



def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def public_route_to_rel(route: str) -> Path:
    raw = str(route or "/").strip()
    if raw == "/":
        return Path("index.html")
    clean = raw.strip("/")
    if raw.endswith("/"):
        return Path(clean) / "index.html"
    return Path(clean)


def relative_public_href(from_rel: Path, route: str) -> str:
    target = public_route_to_rel(route)
    start = from_rel.parent
    rel = os.path.relpath(target, start=start).replace(os.sep, "/")
    if rel.endswith("/index.html"):
        rel = rel[:-len("index.html")]
    elif rel == "index.html":
        rel = "./"
    return rel


def build_house_bridge(surface: dict, surface_by_id: dict, dwellings: dict, local_rooms: list[dict], rel: Path) -> str:
    sid = str(surface.get("id", ""))
    title = str(surface.get("title", sid))
    parent_id = surface.get("primary_parent")
    parent = surface_by_id.get(parent_id) if parent_id else None
    potato_href = relative_public_href(rel, "/potato-of-life/")
    house_href = relative_public_href(rel, "/house/")
    rooms_href = relative_public_href(rel, "/rooms/")
    trail = [
        f'<a href="{html.escape(potato_href, quote=True)}">Potato of Life</a>',
        '<span aria-hidden="true">→</span>',
        f'<a href="{html.escape(house_href, quote=True)}">House</a>',
    ]
    if parent and parent.get("id") not in {"home", "house"}:
        trail += [
            '<span aria-hidden="true">→</span>',
            f'<a href="{html.escape(relative_public_href(rel, parent.get("canonical_route", "/")), quote=True)}">{html.escape(str(parent.get("title", parent_id)))}</a>',
        ]
    trail += ['<span aria-hidden="true">→</span>', f'<strong>{html.escape(title)}</strong>']

    dwelling_chips = []
    for rid in surface.get("primary_room_ids", []):
        label = dwellings.get(rid, rid)
        dwelling_chips.append(f'<span class="house-bridge__chip">{html.escape(str(label))}</span>')
    local_chips = [
        f'<span class="house-bridge__chip">{html.escape(str(x.get("title", x.get("room_id", ""))))}</span>'
        for x in local_rooms[:6]
    ]
    chips = "".join(local_chips or dwelling_chips)
    scope_text = (
        "Local Rooms on this surface" if local_chips
        else "Dwellings feeding this surface"
    )
    view_label = "House view" if surface.get("is_view") else ("Gateway" if surface.get("surface_type") == "hub" else "Reader surface")
    return (
        '<aside class="house-bridge" data-house-bridge="' + html.escape(sid, quote=True) + '" aria-label="Potato House context">'
        '<div class="house-bridge__top"><div class="house-bridge__trail">' + "".join(trail) + '</div>'
        '<span class="house-bridge__kind">' + html.escape(view_label) + '</span></div>'
        '<div class="house-bridge__body"><p><strong>' + html.escape(scope_text) + '.</strong> '
        'This page keeps its own subject and evidence rules while participating in the shared Potato House.</p>'
        '<div class="house-bridge__chips">' + chips + '</div></div>'
        '<a class="house-bridge__rooms-link" href="' + html.escape(rooms_href, quote=True) + '">See all Dwellings &amp; Rooms →</a>'
        '</aside>'
    )


def inject_house_bridge(text: str, bridge: str) -> str:
    if "data-house-bridge=" in text:
        return text
    if not re.search(r"</head\s*>", text, flags=re.I) or not re.search(r"<main\b[^>]*>", text, flags=re.I):
        return text
    if "data-house-bridge-style" not in text:
        text = re.sub(r"</head\s*>", HOUSE_BRIDGE_STYLE + "</head>", text, count=1, flags=re.I)
    main = re.search(r"<main\b[^>]*>", text, flags=re.I)
    if not main:
        return text
    nav = re.search(r"<nav\b[^>]*>.*?</nav\s*>", text[main.end():], flags=re.I | re.S)
    insert_at = main.end() + nav.end() if nav else main.end()
    return text[:insert_at] + bridge + text[insert_at:]


def patch_house_bridges(out: Path = OUT) -> set[Path]:
    surfaces_doc = load_json(ROOT / "data" / "house" / "public-surfaces.json", {}) or {}
    rooms_doc = load_json(ROOT / "data" / "house" / "rooms.json", {}) or {}
    dossiers_doc = load_json(ROOT / "data" / "house" / "room-dossiers.json", {}) or {}
    surfaces = [x for x in surfaces_doc.get("surfaces", []) if isinstance(x, dict) and x.get("status") == "active"]
    surface_by_id = {x.get("id"): x for x in surfaces if x.get("id")}
    dwellings = {x.get("id"): x.get("title", x.get("id")) for x in rooms_doc.get("rooms", []) if isinstance(x, dict) and x.get("id")}
    local_by_surface: dict[str, list[dict]] = {}
    for dossier in dossiers_doc.get("dossiers", []):
        if not isinstance(dossier, dict):
            continue
        for public in dossier.get("public_surfaces", []):
            sid = public.get("id") if isinstance(public, dict) else None
            if sid:
                local_by_surface.setdefault(sid, []).append(dossier)

    changed: set[Path] = set()
    for surface in surfaces:
        sid = surface.get("id")
        if sid in HOUSE_BRIDGE_EXCLUDED:
            continue
        rel = public_route_to_rel(surface.get("canonical_route", "/"))
        path = out / rel
        if not path.exists() or path.suffix.lower() != ".html":
            continue
        page = path.read_text(encoding="utf-8", errors="replace")
        bridge = build_house_bridge(surface, surface_by_id, dwellings, local_by_surface.get(sid, []), rel)
        projected = inject_house_bridge(page, bridge)
        if projected == page:
            continue
        path.write_text(projected, encoding="utf-8")
        changed.add(path)
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

    changed.update(patch_legacy_tts_readers(OUT))
    changed.update(patch_house_bridges(OUT))

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
