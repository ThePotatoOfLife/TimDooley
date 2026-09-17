#!/usr/bin/env python3
"""Require every deployable authored HTML document to have House route ownership."""
from __future__ import annotations

import json
from pathlib import Path

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


def route_for_path(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


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


def owned_routes() -> tuple[set[str], dict[str, str]]:
    data = json.loads(SURFACES.read_text(encoding="utf-8"))
    routes: set[str] = set()
    owners: dict[str, str] = {}
    for row in data.get("surfaces", []):
        sid = row.get("id")
        canonical = row.get("canonical_route")
        if canonical:
            routes.add(canonical)
            owners[canonical] = sid
        for legacy in row.get("legacy_routes", []):
            routes.add(legacy)
            owners[legacy] = sid
    return routes, owners


def coverage_errors() -> list[str]:
    routes, _owners = owned_routes()
    errors: list[str] = []
    for path in authored_html_documents():
        route = route_for_path(path)
        if route not in routes:
            errors.append(
                f"unowned public HTML: {path.relative_to(ROOT).as_posix()} -> {route}"
            )
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
    print(f"POTATO HOUSE HTML COVERAGE PASSED: {len(docs)} authored deployable HTML documents have House route ownership")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
