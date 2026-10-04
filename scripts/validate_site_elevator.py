#!/usr/bin/env python3
"""Validate the three-floor universal site elevator data contract."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTION = ROOT / "data" / "house" / "elevator-spatial-projection.json"
ROOMS = ROOT / "data" / "house" / "rooms.json"
PUBLIC_SURFACES = ROOT / "data" / "house" / "public-surfaces.json"
SUBROOMS = ROOT / "data" / "house" / "subrooms.json"
ELEVATOR_CSS = ROOT / "app" / "site-elevator.css"
ELEVATOR_JS = ROOT / "app" / "site-elevator.js"
PATCHER = ROOT / "scripts" / "patch_public_navigation.py"
OUT = ROOT / "_site"
WORLD_MAP_SOURCE = ROOT / "world-map" / "index.html"
SITE_SYSTEM_CSS = ROOT / "app" / "site-system.css"
COMPARATIVE_COSMOLOGY = ROOT / "traditions" / "comparative-cosmology" / "index.html"
DEDICATED_ELEVATOR = ROOT / "elevator" / "index.html"
HOUSE_JOURNEY_JS = ROOT / "app" / "house-journey.js"

EXPECTED_LEVELS = ["heaven", "plane", "below"]
REPRESENTATIVE_CONTEXTS = {
    "/": ("plane", None),
    "/tim-dooley/": ("plane", None),
    "/potato-of-life/": ("heaven", "potatoverse-canon"),
    "/potatoism/": ("heaven", "potatoverse-canon"),
    "/religion/": ("heaven", "traditions-texts"),
    "/science/": ("plane", "science-formal-models"),
    "/politics/": ("plane", "world-systems"),
    "/economy/": ("plane", "world-systems"),
    "/context/culture/": ("plane", "culture-information"),
    "/shadow-farm/": ("below", None),
    "/context/source-authority/": ("below", "archive-sources"),
    "/research-lab/": ("below", "research-lab"),
    "/works/": ("heaven", "works"),
    "/timeline/": ("plane", "time-history"),
    "/below/": ("below", None),
}


def load_json(path: Path, errors: list[str]) -> dict:
    if not path.exists():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)} must contain a JSON object")
        return {}
    return value


def main() -> int:
    errors: list[str] = []
    projection = load_json(PROJECTION, errors)
    css = ELEVATOR_CSS.read_text(encoding="utf-8", errors="replace") if ELEVATOR_CSS.exists() else ""
    js = ELEVATOR_JS.read_text(encoding="utf-8", errors="replace") if ELEVATOR_JS.exists() else ""
    patcher = PATCHER.read_text(encoding="utf-8", errors="replace") if PATCHER.exists() else ""
    world_map_source = WORLD_MAP_SOURCE.read_text(encoding="utf-8", errors="replace") if WORLD_MAP_SOURCE.exists() else ""
    site_system_css = SITE_SYSTEM_CSS.read_text(encoding="utf-8", errors="replace") if SITE_SYSTEM_CSS.exists() else ""
    comparative_cosmology = COMPARATIVE_COSMOLOGY.read_text(encoding="utf-8", errors="replace") if COMPARATIVE_COSMOLOGY.exists() else ""
    dedicated_elevator = DEDICATED_ELEVATOR.read_text(encoding="utf-8", errors="replace") if DEDICATED_ELEVATOR.exists() else ""
    house_journey_js = HOUSE_JOURNEY_JS.read_text(encoding="utf-8", errors="replace") if HOUSE_JOURNEY_JS.exists() else ""
    room_contract = load_json(ROOMS, errors)
    public_surfaces = load_json(PUBLIC_SURFACES, errors)
    subroom_contract = load_json(SUBROOMS, errors)

    active_rooms = {
        row.get("id"): row
        for row in room_contract.get("rooms", [])
        if isinstance(row, dict) and row.get("status") == "active" and row.get("id")
    }
    if not js:
        errors.append("missing app/site-elevator.js")
    else:
        for token in (
            "publishClearance",
            "ResizeObserver",
            "site-elevator-stage",
        ):
            if token not in js:
                errors.append(f"site elevator JS missing clearance/header marker: {token}")

    if ".app{height:calc(100%-var(--site-elevator-clearance,0px))" not in world_map_source.replace(" ",""):
        errors.append("World Map full-screen app must reserve measured site-elevator top clearance")

    compact_world = re.sub(r"\s+", "", world_map_source)
    for token in (
        "top:calc(var(--site-elevator-clearance,0px)+8px)",
        "max-height:calc(100dvh-var(--site-elevator-clearance,0px)-var(--site-access-clearance,0px)-16px)",
    ):
        if token not in compact_world:
            errors.append(f"World Map fixed overlays must honor measured elevator clearance: {token}")

    if ".page [id]" not in site_system_css or "--site-elevator-clearance" not in site_system_css:
        errors.append("shared page deep links must reserve measured elevator clearance")

    compact_comparative = re.sub(r"\s+", "", comparative_cosmology)
    if ".cross-head{position:sticky;top:var(--site-elevator-clearance,0px)" not in compact_comparative:
        errors.append("Comparative Cosmology sticky matrix header must stay below measured elevator clearance")

    for token in (
        "inject_site_floor",
        "patch_site_floors",
        "_site_floor_for_route",
        "inject_site_elevator",
        "patch_site_elevator",
        "app/site-elevator.css",
        "app/site-elevator.js",
    ):
        if token not in patcher:
            errors.append(f"public navigation projection missing elevator marker: {token}")

    if not css:
        errors.append("missing app/site-elevator.css")
    else:
        css_tokens = (
            ".site-elevator",
            ".site-elevator-controls",
            ".site-elevator-main",
            ".site-elevator-reel",
            ".site-elevator-stage",
            '[data-elevator-level="heaven"]',
            '[data-elevator-level="plane"]',
            '[data-elevator-level="below"]',
            "rotateX(",
            "420ms",
            "cubic-bezier(.2,.8,.2,1)",
            "@media (prefers-reduced-motion: reduce)",
            ".site-elevator-room.is-active",
            "--elevator-slot-count:5",
            "flex:0 0 calc((100% - (var(--elevator-room-gap) * (var(--elevator-slot-count) - 1))) / var(--elevator-slot-count))",
            "@media (max-width:760px)",
            "display:flex;",
            "overflow:visible",
            ".site-elevator-floor-code",
            '[data-elevator-level="heaven"] .site-elevator-stage::before',
            '[data-elevator-level="plane"] .site-elevator-stage::before',
            '[data-elevator-level="below"] .site-elevator-stage::before',
            "border-radius:0",
            "background:transparent",
            ".site-elevator-room-rail{",
            "margin:0;",
            "home-heaven.avif",
            "home-plane.avif",
            "home-below.avif",
            "header-heaven.svg",
            "header-plane.svg",
            "header-below.svg",
            "body:not(.home-body)::before",
            "--site-realm-art-size",
        )
        for token in css_tokens:
            if token not in css:
                errors.append(f"site elevator CSS missing required marker: {token}")

        # Geometry values may evolve; the invariant is shared ownership.
        for shared_geometry_token in (
            "--elevator-shell-height:",
            "--elevator-control-width:",
            "--elevator-board-width:",
            "--elevator-room-height:",
            "--elevator-room-gap:",
            "--elevator-slot-count:",
        ):
            if shared_geometry_token not in css:
                errors.append(
                    f"site elevator CSS missing shared geometry token: {shared_geometry_token}"
                )

        main_shell = re.search(r"\.site-elevator-main\s*\{([^}]*)\}", css, re.S)
        if not main_shell:
            errors.append("site elevator CSS missing .site-elevator-main geometry owner")
        else:
            shell_block = main_shell.group(1)
            for token in (
                "height:var(--elevator-shell-height)",
                "min-height:var(--elevator-shell-height)",
                "max-height:var(--elevator-shell-height)",
            ):
                if token not in re.sub(r"\s+", "", shell_block):
                    errors.append(f"site elevator main shell must use exact shared height: {token}")

        for retired_art in ("site-tree-perspective.svg","site-plane-organic-field.svg","site-below-root-field.svg"):
            if retired_art in css:
                errors.append(f"site elevator CSS must not reference retired floor art: {retired_art}")

        # Uniform-header contract: floor-specific rules may change only skin/art.
        # Geometry belongs to the shared elevator component and must be identical
        # across Heaven, Plane and Below.
        floor_geometry_pattern = re.compile(
            r'\.site-elevator\[data-elevator-level="(?:heaven|plane|below)"\][^{]*\{([^}]*)\}',
            re.S,
        )
        forbidden_geometry = re.compile(
            r'\b(?:width|height|min-height|max-height|padding|margin|gap|'
            r'grid-template-columns|grid-template-rows|flex|flex-basis|'
            r'inset|left|right|top|bottom)\s*:',
            re.I,
        )
        for block in floor_geometry_pattern.findall(css):
            if forbidden_geometry.search(block):
                errors.append(
                    "floor-specific site-elevator CSS must not change geometry; "
                    "Heaven, Plane and Below share one header measurement system"
                )

        header_art_viewboxes = {}
        for art_name in ("header-heaven.svg", "header-plane.svg", "header-below.svg"):
            art_path = ROOT / "app" / art_name
            if not art_path.exists():
                errors.append(f"missing dedicated header panorama: {art_name}")
                continue
            art_text = art_path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r'viewBox=["\']([^"\']+)["\']', art_text)
            if not match:
                errors.append(f"header panorama missing viewBox: {art_name}")
                continue
            header_art_viewboxes[art_name] = match.group(1).strip()
        if header_art_viewboxes and len(set(header_art_viewboxes.values())) != 1:
            errors.append(
                "Heaven, Plane and Below header panoramas must share one viewBox "
                f"for uniform composition: {header_art_viewboxes}"
            )
        if "installSceneParallax" in js or "--site-scene-y" in js:
            errors.append("site elevator runtime must not restore retired scene parallax")
        if "overflow-x:auto" in css:
            errors.append("site elevator Room rail must wrap instead of horizontally scrolling")
        if "scrollbar-width" in css or "scrollbar-color" in css:
            errors.append("site elevator Room rail must not expose scrollbar styling")

    if len(active_rooms) != 10:
        errors.append(f"expected exactly 10 active governed Rooms, got {len(active_rooms)}")

    levels = [row for row in projection.get("levels", []) if isinstance(row, dict)]
    level_ids = [row.get("id") for row in levels]
    if level_ids != EXPECTED_LEVELS:
        errors.append(f"elevator levels must equal {EXPECTED_LEVELS}, got {level_ids}")
    if "world" in level_ids:
        errors.append("legacy world elevator level must be renamed to plane")

    if not dedicated_elevator:
        errors.append("missing dedicated elevator/index.html")
    else:
        dedicated_tokens = (
            "app/elevator-page.css",
            "app/elevator-page.js",
            "page-nav elevator-nav",
            "elevator-console",
            "viewport-shell",
        )
        for token in dedicated_tokens:
            if token not in dedicated_elevator:
                errors.append(f"dedicated elevator missing floor-boundary marker: {token}")
        if "projections.includes(level)" in dedicated_elevator:
            errors.append("dedicated elevator must not expose cross-floor projected Rooms as local doors")
        dedicated_runtime = (ROOT / "app" / "elevator-page.js").read_text(encoding="utf-8", errors="replace") if (ROOT / "app" / "elevator-page.js").exists() else ""
        dedicated_style = (ROOT / "app" / "elevator-page.css").read_text(encoding="utf-8", errors="replace") if (ROOT / "app" / "elevator-page.css").exists() else ""
        for token in (
            "params.get('level')||'plane'",
            "validLevelIds",
            "initialDwelling?.primary_level",
            ".filter(r=>(r.primary_level||'plane')===level)",
            ".filter(R=>(R.primary_level||'plane')===level)",
            "function stepFloor(direction)",
            "moveFloor('up')",
            "moveFloor('down')",
            "if(destination?.primary_level)level=destination.primary_level",
            "'wormhole-elevator'",
            "moved the elevator to the destination Room",
            "async function loadJson(path,fallback,required=false)",
            "Spatial orientation unavailable",
            "Reduced detail",
            "Core floor/Room navigation is available",
            "document.documentElement.dataset.siteFloor=level",
            "journeyReplay.disabled=journey.length<2",
            "centerBtn.disabled=atCenter",
        ):
            if token not in dedicated_runtime:
                errors.append(f"dedicated elevator runtime missing marker: {token}")
        for token in (
            "body.elevator-page-shell",
            ".elevator-console",
            ".viewport-shell",
            ".door-center",
            ".journey > summary",
            "[data-elevator-level=\"heaven\"]",
            "[data-elevator-level=\"plane\"]",
            "[data-elevator-level=\"below\"]",
        ):
            if token not in dedicated_style:
                errors.append(f"dedicated elevator stylesheet missing marker: {token}")
        if "<style>" in dedicated_elevator or "(async()=>{" in dedicated_elevator:
            errors.append("dedicated elevator must keep structural CSS/runtime out of inline HTML")
        if "elevator-shaft" in dedicated_elevator:
            errors.append("dedicated elevator must not duplicate floor controls inside the viewport")
        if "else{level='plane'}" in dedicated_runtime:
            errors.append("Return to center must not silently change the active floor to Plane")
        if "public-surfaces.json" in dedicated_elevator:
            errors.append("dedicated elevator must not depend on unused public-surfaces data")
        if "if(!eRes.ok||!sRes.ok" in dedicated_elevator:
            errors.append("dedicated elevator must isolate optional data failures instead of all-or-nothing fetch gating")
        if "level='world'" in dedicated_elevator or "||'world'" in dedicated_elevator:
            errors.append("dedicated elevator must not restore the retired world floor")

    if not house_journey_js:
        errors.append("missing app/house-journey.js")
    else:
        if "st.level==='world'?'plane':st.level" not in house_journey_js:
            errors.append("House journey links must normalize legacy world states to Plane")

    dwellings = [row for row in projection.get("dwellings", []) if isinstance(row, dict)]
    dwelling_by_id = {row.get("id"): row for row in dwellings if row.get("id")}
    if set(dwelling_by_id) != set(active_rooms):
        missing = sorted(set(active_rooms) - set(dwelling_by_id))
        extra = sorted(set(dwelling_by_id) - set(active_rooms))
        errors.append(f"elevator dwellings must match active Rooms exactly; missing={missing}, extra={extra}")

    allowed = set(EXPECTED_LEVELS)
    for room_id in sorted(active_rooms):
        row = dwelling_by_id.get(room_id)
        if not row:
            continue
        primary = row.get("primary_level")
        projections = row.get("projections")
        if primary not in allowed:
            errors.append(f"{room_id}: primary_level must be one of {EXPECTED_LEVELS}, got {primary!r}")
        if not isinstance(projections, list) or not projections:
            errors.append(f"{room_id}: projections must be a non-empty list")
            continue
        if projections != [primary]:
            errors.append(
                f"{room_id}: governed Room must belong to exactly one floor; "
                f"expected projections={[primary]!r}, got {projections!r}"
            )
        bad = sorted(set(projections) - allowed)
        if bad:
            errors.append(f"{room_id}: unsupported projections {bad}")
        if primary and primary not in projections:
            errors.append(f"{room_id}: primary_level {primary!r} must also appear in projections")
        expected_homepage = f"/rooms/{room_id}/"
        if row.get("homepage") != expected_homepage:
            errors.append(f"{room_id}: homepage must be {expected_homepage!r}, got {row.get('homepage')!r}")
        notes = row.get("projection_notes")
        if not isinstance(notes, dict):
            errors.append(f"{room_id}: projection_notes must map every declared floor to a short explanation")
        else:
            note_keys = set(notes)
            expected_keys = set(projections)
            if note_keys != expected_keys:
                errors.append(
                    f"{room_id}: projection_notes keys must equal declared projections; "
                    f"expected={sorted(expected_keys)}, got={sorted(note_keys)}"
                )
            for floor_id, note in notes.items():
                if not isinstance(note, str) or len(note.strip()) < 28:
                    errors.append(f"{room_id}: projection note for {floor_id!r} is too thin")

        room_home = ROOT / "rooms" / room_id / "index.html"
        if not room_home.exists():
            errors.append(f"{room_id}: canonical Room homepage missing at rooms/{room_id}/index.html")
        else:
            room_html = room_home.read_text(encoding="utf-8", errors="replace")
            if primary in {"heaven","plane"}:
                if "app/room-home.css" not in room_html:
                    errors.append(f"{room_id}: ordinary governed Room must load shared app/room-home.css")
                if "<style>" in room_html:
                    errors.append(f"{room_id}: ordinary governed Room must not keep duplicated inline layout CSS")
            if 'class="room-floor-nav"' in room_html or 'class="page-nav room-floor-nav"' in room_html:
                errors.append(f"{room_id}: retired in-page floor Room rail must not duplicate the universal elevator")
            if '<a href="../">All Rooms</a>' not in room_html or '<a href="../../house/">House</a>' not in room_html:
                errors.append(f"{room_id}: Room homepage must preserve All Rooms + House fallback navigation")

    active_subrooms = [
        row for row in subroom_contract.get("subrooms", [])
        if isinstance(row, dict) and row.get("status") == "active" and row.get("id")
    ]
    seen_subroom_routes: set[str] = set()
    for subroom in active_subrooms:
        subroom_id = subroom.get("id")
        parent_room_id = subroom.get("parent_room_id")
        route_id = subroom.get("route_id") or subroom_id
        if parent_room_id not in active_rooms:
            errors.append(f"{subroom_id}: nested Room references unknown parent {parent_room_id!r}")
        if not isinstance(route_id, str) or not route_id.strip():
            errors.append(f"{subroom_id}: route_id must be a non-empty string when supplied")
            continue
        if route_id in seen_subroom_routes:
            errors.append(f"duplicate nested Room route id: {route_id}")
        seen_subroom_routes.add(route_id)
        subroom_home = ROOT / "rooms" / "inside" / route_id / "index.html"
        if not subroom_home.exists():
            errors.append(
                f"{subroom_id}: nested Room page missing at rooms/inside/{route_id}/index.html"
            )

    contexts = [row for row in projection.get("route_contexts", []) if isinstance(row, dict)]
    by_match = {row.get("match"): row for row in contexts if row.get("match")}
    for row in contexts:
        match = row.get("match")
        level_id = row.get("level_id")
        room_id = row.get("room_id")
        if not isinstance(match, str) or not match.startswith("/"):
            errors.append(f"route context has invalid match {match!r}")
        if level_id not in allowed:
            errors.append(f"{match}: route context level_id must be one of {EXPECTED_LEVELS}, got {level_id!r}")
        if room_id is not None and room_id not in active_rooms:
            errors.append(f"{match}: route context references unknown Room {room_id!r}")
        if room_id is not None and room_id in dwelling_by_id and level_id in allowed:
            primary_level = dwelling_by_id[room_id].get("primary_level") or "plane"
            if level_id != primary_level:
                errors.append(
                    f"{match}: route context Room/floor mismatch; "
                    f"{room_id!r} belongs to {primary_level!r}, not {level_id!r}"
                )

    active_surfaces = [
        row for row in public_surfaces.get("surfaces", [])
        if isinstance(row, dict) and row.get("status") == "active" and row.get("route")
    ]
    direct_room_prefixes = {f"/rooms/{room_id}/" for room_id in active_rooms}
    uncovered_surfaces = []
    for surface in active_surfaces:
        route = surface.get("route")
        direct_room = any(route == prefix or route.startswith(prefix) for prefix in direct_room_prefixes)
        if direct_room:
            continue
        matched = any(
            (ctx.get("match") == "/" and route == "/")
            or (
                isinstance(ctx.get("match"), str)
                and ctx.get("match") != "/"
                and (route == ctx.get("match") or route.startswith(ctx.get("match")))
            )
            for ctx in contexts
        )
        if not matched:
            uncovered_surfaces.append(f"{surface.get('id')}:{route}")
    if uncovered_surfaces:
        errors.append(
            "active public surfaces missing elevator context: "
            + ", ".join(sorted(uncovered_surfaces))
        )

    for route, (level_id, room_id) in REPRESENTATIVE_CONTEXTS.items():
        row = by_match.get(route)
        if not row:
            errors.append(f"missing representative route context: {route}")
            continue
        if row.get("level_id") != level_id or row.get("room_id") != room_id:
            errors.append(
                f"{route}: expected ({level_id!r}, {room_id!r}), "
                f"got ({row.get('level_id')!r}, {row.get('room_id')!r})"
            )

    patcher = (ROOT / "scripts" / "patch_public_navigation.py").read_text(encoding="utf-8", errors="replace")
    if '_has_asset_reference(text, "site-elevator.css")' not in patcher or '_has_asset_reference(text, "site-elevator.js")' not in patcher:
        errors.append("site elevator injector must repair partial CSS/JS coverage using real asset references")

    if OUT.exists():
        standalone_pages = []
        for path in OUT.rglob("*.html"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if "<html" not in text.lower() or "<body" not in text.lower():
                continue
            standalone_pages.append((path, text))
        for path, text in standalone_pages:
            rel = path.relative_to(OUT).as_posix()
            quiet = rel.startswith("tools/tts/") or rel == "elevator/index.html"
            elevator_css_count = text.count("site-elevator.css")
            elevator_js_count = text.count("site-elevator.js")
            if rel == "elevator/index.html":
                if elevator_css_count != 1 or elevator_js_count:
                    errors.append(f"{rel}: dedicated Elevator must reuse realm CSS but not mount the universal elevator runtime")
            elif quiet:
                if elevator_css_count or elevator_js_count:
                    errors.append(f"{rel}: quiet tool must not receive the universal elevator")
            elif elevator_css_count != 1 or elevator_js_count != 1:
                errors.append(
                    f"{rel}: expected exactly one universal elevator CSS + JS asset, "
                    f"got css={elevator_css_count}, js={elevator_js_count}"
                )

        # Every governed Room and active nested Room must ship with its canonical floor.
        for room_id,row in sorted(dwelling_by_id.items()):
            floor=row.get("primary_level") or "plane"
            path=OUT/"rooms"/room_id/"index.html"
            if path.exists():
                built=path.read_text(encoding="utf-8",errors="replace")
                if f'data-site-floor="{floor}"' not in built:
                    errors.append(f"rooms/{room_id}/index.html: expected first-paint floor {floor!r}")
        for subroom in active_subrooms:
            route_id=subroom.get("route_id") or subroom.get("id")
            parent=dwelling_by_id.get(subroom.get("parent_room_id")) or {}
            floor=parent.get("primary_level") or "plane"
            path=OUT/"rooms"/"inside"/str(route_id)/"index.html"
            if path.exists():
                built=path.read_text(encoding="utf-8",errors="replace")
                if f'data-site-floor="{floor}"' not in built:
                    errors.append(f"rooms/inside/{route_id}/index.html: expected inherited floor {floor!r}")

        representative = [
            "index.html",
            "house/index.html",
            "rooms/index.html",
            "religion/index.html",
            "science/index.html",
            "world/index.html",
            "north/index.html",
            "below/index.html",
            "shadow-farm/index.html",
            "research-lab/index.html",
            "world-map/index.html",
            "news/index.html",
            "tim-dooley/index.html",
        ]
        for rel in representative:
            path = OUT / rel
            if not path.exists():
                errors.append(f"built representative missing: {rel}")
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if text.count("site-elevator.css") != 1 or text.count("site-elevator.js") != 1:
                errors.append(f"{rel}: expected exactly one elevator CSS + JS asset")
            if "site-access.css" not in text or "site-access.js" not in text:
                errors.append(f"{rel}: elevator rollout must preserve the bottom site-access dock")
            route = "/" if rel == "index.html" else "/" + rel.removesuffix("index.html")
            if route == "/":
                if "data-site-floor=" in text:
                    errors.append("index.html: Home spans all three realms and must not carry a single-floor canvas")
            else:
                expected_floor = REPRESENTATIVE_CONTEXTS.get(route, ("plane", None))[0]
                if f'data-site-floor="{expected_floor}"' not in text:
                    errors.append(f"{rel}: built HTML must carry first-paint floor {expected_floor!r}")

    if errors:
        print(f"SITE ELEVATOR DATA VALIDATION FAILED: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SITE ELEVATOR DATA VALIDATION PASSED")
    print("3 floors · 10 Rooms · representative route contexts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
