#!/usr/bin/env python3
"""Validate public tradition routes, local HTML structure and internal links."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TRADITIONS = ROOT / "traditions"
REGISTRY = ROOT / "data" / "tradition-route-registry.json"
BALANCED_TAGS = ("div", "section", "article", "main", "nav")
BANNED_UI_PHRASES = ("study chambers", "enter chamber", "open chamber")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def route_to_file(route: str) -> Path:
    clean = route.split("#", 1)[0].split("?", 1)[0].lstrip("/")
    p = ROOT / clean
    if route.endswith("/") or p.is_dir():
        p = p / "index.html"
    return p


def local_target(page: Path, href: str) -> Path | None:
    raw = href.strip()
    if not raw or raw.startswith(("#", "mailto:", "javascript:", "tel:")):
        return None
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return None
    path = parsed.path
    if not path:
        return None
    target = (ROOT / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target.resolve()


def main() -> int:
    errors: list[str] = []
    registry = load_json(REGISTRY)
    routes = registry.get("routes", [])
    ids = [r.get("id") for r in routes]
    route_values = [r.get("route") for r in routes]

    if len(ids) != len(set(ids)):
        errors.append("duplicate tradition route IDs")
    if len(route_values) != len(set(route_values)):
        errors.append("duplicate tradition route paths")

    registered_files: set[Path] = set()
    for rec in routes:
        route = rec.get("route")
        title = rec.get("title")
        kind = rec.get("kind")
        if not route or not title or not kind:
            errors.append(f"incomplete route record: {rec!r}")
            continue
        target = route_to_file(route).resolve()
        registered_files.add(target)
        if not target.is_file():
            errors.append(f"registered route does not resolve: {route} -> {target.relative_to(ROOT)}")

    html_pages = sorted(TRADITIONS.rglob("*.html"))
    for page in html_pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for phrase in BANNED_UI_PHRASES:
            if phrase in lower:
                errors.append(f"{page.relative_to(ROOT)} still contains rejected UI phrase: {phrase!r}")
        for tag in BALANCED_TAGS:
            opens = len(re.findall(rf"<{tag}(?:\s|>)", text, flags=re.I))
            closes = len(re.findall(rf"</{tag}>", text, flags=re.I))
            if opens != closes:
                errors.append(f"{page.relative_to(ROOT)} unbalanced <{tag}>: {opens} open / {closes} close")
        for href in re.findall(r'href=["\']([^"\']+)["\']', text, flags=re.I):
            target = local_target(page, href)
            if target is not None and not target.exists():
                try:
                    shown = target.relative_to(ROOT)
                except ValueError:
                    shown = target
                errors.append(f"{page.relative_to(ROOT)} broken internal href {href!r} -> {shown}")

    index_pages = {p.resolve() for p in html_pages if p.name == "index.html"}
    unregistered = sorted(index_pages - registered_files)
    for p in unregistered:
        errors.append(f"unregistered public tradition page: /{p.relative_to(ROOT).as_posix()[:-10]}")

    print(f"Tradition HTML pages: {len(html_pages)}")
    print(f"Registered tradition routes: {len(routes)}")
    if errors:
        print("\nTRADITION ROUTE VALIDATION FAILED")
        for e in errors:
            print(f"- {e}")
        return 1
    print("\nTRADITION ROUTE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
