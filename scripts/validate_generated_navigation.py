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

from house_public_surfaces import surface_by_id, surface_rows
from house_shell import relative_href

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_HREF_RE = re.compile(r'<base\b[^>]*href=["\']([^"\']+)["\']', re.I)
READER_CSS_RE = re.compile(r'<link\b[^>]*href=["\'][^"\']*\breader\.css["\']', re.I)

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
    """Return registered authored readers whose shell policy belongs to build_site."""
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
    """Return registered authored specialist apps that own their local chrome."""
    eligible = []
    for surface in surface_rows(ROOT):
        if surface.get("status") != "active" or surface.get("shell_type") != "specialist":
            continue
        if path_for_route(ROOT, surface["canonical_route"]).exists():
            eligible.append(surface)
    return eligible


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

        # Legacy readers already loading app/reader.css receive Reader v2 through
        # that shared integration point. Self-themed editorial readers must receive
        # reader-v2.css directly from the build so every authored House reader gets
        # the same convergence layer without maintaining a page-ID allowlist.
        if not READER_CSS_RE.search(source_text) and "reader-v2.css" not in text:
            errors.append(f"{rel} has no Reader v2 convergence path")

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
            require_href(
                text,
                parent_href,
                f"{rel} specialist House escape does not link parent {parent['canonical_route']} through document base",
                errors,
            )


def main() -> int:
    errors: list[str] = []
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_site.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr)
            print("Generated navigation validation FAILED")
            print(" - build_site.py failed")
            return 1

        validate_curated_shell_policy(errors)
        validate_specialist_escape_policy(errors)

        for branch_id, parent_surface_id in REPRESENTATIVE_BRANCHES.items():
            page = OUT / "topics" / branch_id / "index.html"
            if not page.exists():
                errors.append(f"missing generated topic page: {page.relative_to(ROOT)}")
                continue
            text = page.read_text(encoding="utf-8", errors="replace")
            parent = surface_by_id(ROOT, parent_surface_id)
            expected = relative_href(f"/topics/{branch_id}/", parent["canonical_route"])
            require_href(
                text,
                expected,
                f"topics/{branch_id}/ does not link back to {parent['canonical_route']} through the House route resolver",
                errors,
            )
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
                    context_href = relative_href(route, context_surface["canonical_route"])
                    explore_href = relative_href(route, explore_surface["canonical_route"])
                    require_href(
                        text,
                        context_href,
                        f"context/{cid}/ does not route up to {context_surface['canonical_route']}",
                        errors,
                    )
                    require_href(
                        text,
                        explore_href,
                        f"context/{cid}/ does not retain Explore in shared House navigation",
                        errors,
                    )
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

        print("Generated navigation validation passed: editorial/long-form readers, specialist apps and generated topic/record/context pages all use their declared House orientation contract.")
        return 0
    finally:
        if OUT.exists():
            shutil.rmtree(OUT)


if __name__ == "__main__":
    raise SystemExit(main())
