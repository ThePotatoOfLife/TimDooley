#!/usr/bin/env python3
"""Validate that generated and curated public pages return readers through the shared House."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from house_public_surfaces import child_rows, parent_chain, surface_by_id, surface_rows, surfaces_by_id
from house_shell import relative_href

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_HREF_RE = re.compile(r'<base\b[^>]*href=["\']([^"\']+)["\']', re.I)
LEGACY_STYLE_RE = re.compile(r'<link\b[^>]*href=["\'][^"\']*\bapp/style\.css["\']', re.I)
READER_CSS_RE = re.compile(r'<link\b[^>]*href=["\'][^"\']*\breader\.css["\']', re.I)
SITE_RELATED_RE = re.compile(r'<aside\b[^>]*class=["\'][^"\']*\bsite-related\b[^"\']*["\'][^>]*>.*?</aside>', re.I | re.S)

REPRESENTATIVE_BRANCHES = {
    "tim": "tim",
    "traditions": "religion",
    "science": "science",
    "world": "world",
}


def require_href(text: str, href: str, label: str, errors: list[str]) -> None:
    if f'href="{href}"' not in text and f"href='{href}'" not in text:
        errors.append(label)


def path_for_route(root: Path, route: str) -> Path:
    normalized = route if route.startswith("/") else "/" + route
    stripped = normalized.strip("/")
    if not stripped:
        return root / "index.html"
    if normalized.endswith("/"):
        return root / stripped / "index.html"
    return root / stripped


def effective_document_route(route: str, source_text: str) -> str:
    """Return the route relative URLs resolve against after any HTML <base href>."""
    match = BASE_HREF_RE.search(source_text)
    if not match:
        return route
    resolved = urljoin("https://house.invalid" + route, match.group(1))
    path = urlparse(resolved).path or "/"
    return path if path.startswith("/") else "/" + path


def source_backed_shell_surfaces() -> list[dict]:
    eligible = []
    for surface in surface_rows(ROOT):
        if surface.get("status") != "active":
            continue
        if surface.get("shell_type") not in {"editorial", "longform"}:
            continue
        if path_for_route(ROOT, surface["canonical_route"]).exists():
            eligible.append(surface)
    return eligible


def source_backed_specialist_surfaces() -> list[dict]:
    eligible = []
    for surface in surface_rows(ROOT):
        if surface.get("status") != "active" or surface.get("shell_type") != "specialist":
            continue
        if path_for_route(ROOT, surface["canonical_route"]).exists():
            eligible.append(surface)
    return eligible


def source_backed_utility_surfaces() -> list[dict]:
    eligible = []
    for surface in surface_rows(ROOT):
        if surface.get("status") != "active" or surface.get("shell_type") != "utility":
            continue
        if path_for_route(ROOT, surface["canonical_route"]).exists():
            eligible.append(surface)
    return eligible


def continuation_eligible(row: dict) -> bool:
    return (
        row.get("status") == "active"
        and row.get("shell_type") not in {"redirect", "diagnostic", "utility"}
        and row.get("visibility") != "compatibility"
    )


def branch_anchor(surface_id: str) -> str:
    chain = [row for row in parent_chain(ROOT, surface_id) if row["id"] != "home"]
    return chain[0]["id"] if chain else "home"


def expected_across(surface: dict) -> dict | None:
    rooms = set(surface.get("primary_room_ids", []))
    if not rooms:
        return None
    own_branch = branch_anchor(surface["id"])
    candidates = []
    for index, row in enumerate(surface_rows(ROOT)):
        if row["id"] == surface["id"] or not continuation_eligible(row):
            continue
        if branch_anchor(row["id"]) == own_branch:
            continue
        shared = rooms & set(row.get("primary_room_ids", []))
        if not shared:
            continue
        candidates.append((
            -len(shared),
            0 if row.get("navigation_group") == surface.get("navigation_group") else 1,
            index,
            row["canonical_route"],
            row,
        ))
    return sorted(candidates, key=lambda item: item[:4])[0][-1] if candidates else None


def validate_continuation(surface: dict, route: str, text: str, rel: Path, errors: list[str]) -> None:
    match = SITE_RELATED_RE.search(text)
    if not match:
        errors.append(f"{rel} missing shared House continuation routes")
        return

    fragment = match.group(0)
    if 'aria-label="Continue exploring"' not in fragment:
        errors.append(f"{rel} continuation layer lacks accessible label")

    parent_id = surface.get("primary_parent")
    if parent_id:
        parent = surface_by_id(ROOT, parent_id)
        if "Up" not in fragment:
            errors.append(f"{rel} continuation layer missing Up direction")
        require_href(fragment, relative_href(route, parent["canonical_route"]), f"{rel} Up route does not resolve to {parent['canonical_route']}", errors)

    children = [row for row in child_rows(ROOT, surface["id"]) if continuation_eligible(row)]
    if children:
        if "Deeper" not in fragment:
            errors.append(f"{rel} continuation layer missing Deeper direction despite active children")
        if not any(f'href="{relative_href(route, row["canonical_route"])}"' in fragment for row in children):
            errors.append(f"{rel} Deeper direction does not reach an active child")

    across = expected_across(surface)
    if across:
        if "Across" not in fragment:
            errors.append(f"{rel} continuation layer missing Room-derived Across direction")
        require_href(fragment, relative_href(route, across["canonical_route"]), f"{rel} Across route does not reach strongest shared-Room surface {across['canonical_route']}", errors)

    self_href = relative_href(route, route)
    if self_href != "./" and f'href="{self_href}"' in fragment:
        errors.append(f"{rel} continuation layer links back to itself")


def validate_curated_shell_policy(errors: list[str]) -> None:
    eligible = source_backed_shell_surfaces()
    if len(eligible) < 10:
        errors.append(f"shell-policy test discovered unexpectedly few authored surfaces: {len(eligible)}")

    for surface in eligible:
        route = surface["canonical_route"]
        rel = path_for_route(Path("."), route)
        source_page = path_for_route(ROOT, route)
        source_text = source_page.read_text(encoding="utf-8", errors="replace")
        page = path_for_route(OUT, route)
        if not page.exists():
            errors.append(f"missing registered authored House surface after build: {rel}")
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        shell_type = surface["shell_type"]
        if shell_type == "longform":
            if 'class="site-housebar site-housebar--compact"' not in text:
                errors.append(f"{rel} missing compact shared House bar")
        elif 'class="site-housebar' not in text:
            errors.append(f"{rel} missing projected shared House bar")

        if 'class="site-breadcrumbs' not in text:
            errors.append(f"{rel} missing projected House breadcrumb")
        if 'class="page-nav"' in text:
            errors.append(f"{rel} still contains duplicate authored page-nav after House projection")
        if "site-system.css" not in text:
            errors.append(f"{rel} does not load the shared House stylesheet")
        if f'data-house-surface="{surface["id"]}"' not in text:
            errors.append(f"{rel} House projection does not identify surface {surface['id']}")

        if LEGACY_STYLE_RE.search(source_text) and not READER_CSS_RE.search(source_text) and "reader-v2.css" not in text:
            errors.append(f"{rel} uses legacy app/style.css without a Reader v2 convergence path")

        validate_continuation(surface, route, text, rel, errors)

    great_book = path_for_route(OUT, "/great-book/")
    if great_book.exists():
        text = great_book.read_text(encoding="utf-8", errors="replace")
        if 'class="world-family"' not in text:
            errors.append("great-book/index.html lost its reader-local Great Book navigation")


def validate_specialist_escape_policy(errors: list[str]) -> None:
    specialists = source_backed_specialist_surfaces()
    expected_ids = {"timeline", "explore", "world-map", "bible"}
    actual_ids = {surface["id"] for surface in specialists}
    if actual_ids != expected_ids:
        errors.append(f"specialist shell registry drift: expected {sorted(expected_ids)}, got {sorted(actual_ids)}")

    for surface in specialists:
        route = surface["canonical_route"]
        rel = path_for_route(Path("."), route)
        source = path_for_route(ROOT, route).read_text(encoding="utf-8", errors="replace")
        link_route = effective_document_route(route, source)
        mount = surface.get("specialist_mount")
        if mount not in {"header", "main"}:
            errors.append(f"{rel} has no valid specialist_mount policy in public-surfaces.json")
        elif f"<{mount}" not in source.lower():
            errors.append(f"{rel} specialist_mount={mount} has no matching semantic source element")

        page = path_for_route(OUT, route)
        if not page.exists():
            errors.append(f"missing specialist House surface after build: {rel}")
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        if 'class="site-housebar' in text:
            errors.append(f"{rel} incorrectly received editorial House chrome")
        if 'class="site-specialist-house"' not in text:
            errors.append(f"{rel} missing compact specialist House escape")
        expected_css = relative_href(link_route, "/app/specialist-house.css")
        require_href(text, expected_css, f"{rel} specialist stylesheet does not respect document base", errors)
        if f'data-house-surface="{surface["id"]}"' not in text:
            errors.append(f"{rel} specialist House escape does not identify surface {surface['id']}")

        home = surface_by_id(ROOT, "home")
        home_href = relative_href(link_route, home["canonical_route"])
        require_href(text, home_href, f"{rel} specialist House escape does not link Home through document base", errors)

        parent_id = surface.get("primary_parent")
        if parent_id and parent_id != "home":
            parent = surface_by_id(ROOT, parent_id)
            parent_href = relative_href(link_route, parent["canonical_route"])
            require_href(text, parent_href, f"{rel} specialist House escape does not link parent {parent['canonical_route']} through document base", errors)


def validate_utility_escape_policy(errors: list[str]) -> None:
    utilities = source_backed_utility_surfaces()
    if not utilities:
        errors.append("utility shell registry has no source-backed active utility surfaces")
        return

    for surface in utilities:
        route = surface["canonical_route"]
        rel = path_for_route(Path("."), route)
        page = path_for_route(OUT, route)
        if not page.exists():
            errors.append(f"missing utility House surface after build: {rel}")
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        if 'class="site-housebar' in text or "site-system.css" in text:
            errors.append(f"{rel} utility surface incorrectly received editorial House chrome")
        if 'class="site-utility-house"' not in text:
            errors.append(f"{rel} missing compact utility House escape")
        if f'data-house-surface="{surface["id"]}"' not in text:
            errors.append(f"{rel} utility House escape does not identify surface {surface['id']}")
        expected_css = relative_href(route, "/app/utility-house.css")
        require_href(text, expected_css, f"{rel} missing namespaced utility House stylesheet", errors)
        home = surface_by_id(ROOT, "home")
        require_href(text, relative_href(route, home["canonical_route"]), f"{rel} utility House escape does not link Home", errors)

        if surface["id"] == "tts":
            for marker in ('id="app"', 'id="play"', 'id="text"', 'role="toolbar"'):
                if marker not in text:
                    errors.append(f"{rel} lost TTS application contract marker {marker}")


def main() -> int:
    errors: list[str] = []
    try:
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py")], cwd=ROOT, text=True, capture_output=True)
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr)
            print("Generated navigation validation FAILED")
            print(" - build_site.py failed")
            return 1

        validate_curated_shell_policy(errors)
        validate_specialist_escape_policy(errors)
        validate_utility_escape_policy(errors)

        for branch_id, parent_surface_id in REPRESENTATIVE_BRANCHES.items():
            page = OUT / "topics" / branch_id / "index.html"
            if not page.exists():
                errors.append(f"missing generated topic page: {page.relative_to(ROOT)}")
                continue
            text = page.read_text(encoding="utf-8", errors="replace")
            parent = surface_by_id(ROOT, parent_surface_id)
            expected = relative_href(f"/topics/{branch_id}/", parent["canonical_route"])
            require_href(text, expected, f"topics/{branch_id}/ does not link back to {parent['canonical_route']} through the House route resolver", errors)
            if "site-housebar" not in text:
                errors.append(f"topics/{branch_id}/ missing shared House bar")

        contexts = json.loads((ROOT / "knowledge" / "indexes" / "context-graph.json").read_text(encoding="utf-8"))
        clusters = contexts.get("clusters", [])
        if clusters:
            cid = str(clusters[0].get("id", "")).strip()
            if cid:
                page = OUT / "context" / cid / "index.html"
                if page.exists():
                    text = page.read_text(encoding="utf-8", errors="replace")
                    route = f"/context/{cid}/"
                    context_surface = surface_by_id(ROOT, "context")
                    explore_surface = surface_by_id(ROOT, "explore")
                    require_href(text, relative_href(route, context_surface["canonical_route"]), f"context/{cid}/ does not route up to {context_surface['canonical_route']}", errors)
                    require_href(text, relative_href(route, explore_surface["canonical_route"]), f"context/{cid}/ does not retain Explore in shared House navigation", errors)
                    if "site-housebar" not in text or "site-breadcrumbs" not in text:
                        errors.append(f"context/{cid}/ missing shared House orientation")

        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        record_branch = next((b for b in manifest.get("branches", []) if b.get("records")), None)
        if record_branch:
            page = OUT / "topics" / str(record_branch["id"]) / "index.html"
            text = page.read_text(encoding="utf-8", errors="replace") if page.exists() else ""
            if "/records/" not in text:
                errors.append(f"topics/{record_branch['id']}/ still renders canonical records as path-only text")

        if errors:
            print("Generated navigation validation FAILED")
            for error in errors:
                print(f" - {error}")
            return 1

        print("Generated navigation validation passed: editorial/long-form readers, specialist apps, utility tools and generated topic/record/context pages all use their declared House orientation contract.")
        return 0
    finally:
        if OUT.exists():
            shutil.rmtree(OUT)


if __name__ == "__main__":
    raise SystemExit(main())
