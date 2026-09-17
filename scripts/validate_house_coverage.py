#!/usr/bin/env python3
"""Require every deployable authored HTML document to have House route ownership and shell behavior."""
from __future__ import annotations

import json
import re
from pathlib import Path

from house_shell import relative_href

ROOT = Path(__file__).resolve().parents[1]
SURFACES = ROOT / "data" / "house" / "public-surfaces.json"
EXCLUDED_PARTS = {
    ".git",
    ".github",
    "_site",
    "archive",
    "node_modules",
    "vendor",
    "components",
    "__pycache__",
}
ROBOTS_NOINDEX_RE = re.compile(
    r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*\bnoindex\b[^"\']*["\'][^>]*>',
    re.I,
)


def route_for_path(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def path_for_route(route: str) -> Path:
    normalized = route if route.startswith("/") else "/" + route
    stripped = normalized.strip("/")
    if not stripped:
        return ROOT / "index.html"
    if normalized.endswith("/"):
        return ROOT / stripped / "index.html"
    return ROOT / stripped


def authored_html_documents() -> list[Path]:
    docs: list[Path] = []
    for path in ROOT.rglob("*.html"):
        rel_parts = set(path.relative_to(ROOT).parts)
        if rel_parts & EXCLUDED_PARTS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "<!doctype html" not in text.lower():
            continue
        docs.append(path)
    return sorted(docs)


def surface_rows() -> list[dict]:
    data = json.loads(SURFACES.read_text(encoding="utf-8"))
    return [row for row in data.get("surfaces", []) if isinstance(row, dict)]


def owned_routes() -> tuple[set[str], dict[str, str]]:
    routes: set[str] = set()
    owners: dict[str, str] = {}
    for row in surface_rows():
        sid = row.get("id")
        canonical = row.get("canonical_route")
        if canonical:
            routes.add(canonical)
            owners[canonical] = sid
        for legacy in row.get("legacy_routes", []):
            routes.add(legacy)
            owners[legacy] = sid
    return routes, owners


def require_href(text: str, href: str) -> bool:
    return f'href="{href}"' in text or f"href='{href}'" in text


def nonreader_shell_errors() -> list[str]:
    """Protect utility ownership and diagnostic indexing without imposing editorial chrome."""
    errors: list[str] = []
    rows = {row.get("id"): row for row in surface_rows() if row.get("id")}

    for row in rows.values():
        if row.get("status") != "active":
            continue
        shell_type = row.get("shell_type")
        if shell_type not in {"utility", "diagnostic"}:
            continue
        route = row.get("canonical_route", "")
        path = path_for_route(route)
        if not path.exists():
            errors.append(f"{shell_type} surface source missing: {row.get('id')} -> {route}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()

        if shell_type == "utility":
            # Utilities own dense application geometry. At source-governance time we
            # require explicit House ownership/parentage, while visible escape chrome
            # is a deployment/presentation concern rather than a reason to rewrite a
            # self-contained tool file.
            if row.get("navigation_group") != "utility":
                errors.append(f"{rel} utility must use navigation_group=utility")
            if row.get("primary_parent") != "home":
                errors.append(f"{rel} utility must declare Home as its primary parent")
            if row.get("is_view") is not True:
                errors.append(f"{rel} utility must be classified as a view")
            if "site-housebar" in text:
                errors.append(f"{rel} utility must not inherit editorial House chrome")

        if shell_type == "diagnostic":
            marker = f'data-house-surface="{row.get("id")}"'
            if marker not in text:
                errors.append(f"{rel} missing diagnostic House surface marker {row.get('id')}")
            if not ROBOTS_NOINDEX_RE.search(text):
                errors.append(f"{rel} diagnostic surface must declare robots noindex")
            if 'data-house-escape="diagnostic"' not in text:
                errors.append(f"{rel} diagnostic has no return path to its owning surface")
            parent_id = row.get("primary_parent")
            parent = rows.get(parent_id, {}) if parent_id else {}
            parent_route = parent.get("canonical_route")
            if parent_route:
                parent_href = relative_href(route, parent_route)
                if not require_href(text, parent_href):
                    errors.append(f"{rel} diagnostic return path does not link owner {parent_route} ({parent_href})")
            if "site-housebar" in text:
                errors.append(f"{rel} diagnostic must not inherit editorial House chrome")

    return errors


def coverage_errors() -> list[str]:
    routes, _owners = owned_routes()
    errors: list[str] = []
    for path in authored_html_documents():
        route = route_for_path(path)
        if route not in routes:
            errors.append(
                f"unowned public HTML: {path.relative_to(ROOT).as_posix()} -> {route}"
            )
    errors.extend(nonreader_shell_errors())
    return errors


def main() -> int:
    docs = authored_html_documents()
    errors = coverage_errors()
    if errors:
        print("POTATO HOUSE HTML COVERAGE FAILED")
        print(f"Authored deployable HTML documents scanned: {len(docs)}")
        for error in errors:
            print("-", error)
        return 1
    print(
        f"POTATO HOUSE HTML COVERAGE PASSED: {len(docs)} authored deployable HTML documents have "
        "House route ownership; utilities have explicit House parentage; diagnostics are noindex and return to their owner"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
