#!/usr/bin/env python3
"""Validate the canonical public ownership contract for the World Map.

This validator intentionally focuses on public ownership before the broader
Atlas-to-precise-nouns migration. It should fail against the pre-migration
state and pass only once /world-map/ is the single canonical application.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

# Reader-facing navigation and machine-discovery owners only. Migration plans,
# historical design prose and internal source records are handled by the later
# naming/inventory phase; merely documenting the old URL is not a public owner.
CANONICAL_SURFACES = (
    "index.html",
    "manifest.json",
    "sitemap.xml",
    "llms.txt",
    "tim-dooley/index.html",
    "religion/index.html",
    "philosophy/index.html",
    "science/index.html",
    "north/index.html",
    "context/index.html",
)


def read(path: str) -> str:
    file_path = ROOT / path
    if not file_path.is_file():
        # Some machine-discovery surfaces are generated rather than committed.
        if path in {"manifest.json", "llms.txt"}:
            return ""
        ERRORS.append(f"missing required file: {path}")
        return ""
    return file_path.read_text(encoding="utf-8", errors="replace")


def fail(message: str) -> None:
    ERRORS.append(message)


def validate_canonical_index() -> None:
    html = read("world-map/index.html")
    if not html:
        return

    lower = html.lower()
    if "world map" not in lower:
        fail("world-map/index.html must identify the canonical application as 'World Map'")

    if re.search(r'<meta[^>]+http-equiv=["\']refresh["\']', html, re.I):
        fail("world-map/index.html must contain the real World Map application, not a redirect")

    if re.search(r'>\s*2D\s+map\s*<', html, re.I) or re.search(r'\b2D\s+map\b', html, re.I):
        fail("canonical World Map UI must not link to a competing '2D map' product")


def validate_legacy_3d_route() -> None:
    html = read("world-map/3d.html")
    if not html:
        return

    lower = html.lower()
    if "noindex" not in lower:
        fail("world-map/3d.html must be compatibility-only and contain robots noindex")

    has_refresh = bool(re.search(r'<meta[^>]+http-equiv=["\']refresh["\'][^>]+>', html, re.I))
    has_script_redirect = bool(re.search(r'(?:location\.(?:replace|assign)|location\.href)\s*\(', html, re.I))
    if not (has_refresh or has_script_redirect):
        fail("world-map/3d.html must redirect to the canonical /world-map/ route")

    canonical_target = bool(
        re.search(r'url\s*=\s*(?:\./|index\.html|/world-map/)', html, re.I)
        or re.search(r'location\.(?:replace|assign)\s*\(\s*["\'](?:\./|index\.html|/world-map/)["\']', html, re.I)
        or re.search(r'href\s*=\s*["\'](?:\./|index\.html|/world-map/)["\']', html, re.I)
    )
    if not canonical_target:
        fail("world-map/3d.html redirect/fallback must target the canonical /world-map/ route")

    implementation_signals = (
        "maplibregl",
        "leaflet",
        "world-map-runtime.json",
        "atlasapp",
        "worldmapapp",
    )
    if any(signal in lower for signal in implementation_signals):
        fail("world-map/3d.html must not contain a competing map implementation")


def validate_discovery_targets() -> None:
    offenders: list[str] = []
    for relative in CANONICAL_SURFACES:
        path = ROOT / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "world-map/3d.html" in text or "/world-map/3d.html" in text:
            offenders.append(relative)

    if offenders:
        fail(
            "canonical public/discovery surfaces must not prefer world-map/3d.html: "
            + ", ".join(sorted(offenders))
        )


def main() -> int:
    validate_canonical_index()
    validate_legacy_3d_route()
    validate_discovery_targets()

    if ERRORS:
        print("World Map ownership validation FAILED:")
        for error in ERRORS:
            print(f" - {error}")
        return 1

    print("World Map ownership validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
