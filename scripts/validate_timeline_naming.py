#!/usr/bin/env python3
"""Validate that Timeline is the single canonical temporal-system name."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".html", ".htm", ".md", ".json", ".txt", ".py", ".js", ".mjs", ".css",
    ".yml", ".yaml", ".xml", ".csv", ".ts", ".tsx", ".jsx", ".toml",
}
SKIP_DIRS = {".git", ".github", "node_modules", "vendor", "_site", "__pycache__", "archive"}
SELF = Path(__file__).resolve()


def fail(message: str) -> None:
    print(f"TIMELINE NAMING ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    timeline_page = ROOT / "timeline" / "index.html"
    if not timeline_page.exists():
        fail("timeline/index.html is missing")
    if not (ROOT / "knowledge" / "timeline").is_dir():
        fail("knowledge/timeline/ is missing")
    if (ROOT / "knowledge" / "chronology").exists():
        fail("knowledge/chronology/ still exists")

    legacy = ROOT / "chronology" / "index.html"
    if not legacy.exists():
        fail("chronology/index.html compatibility redirect is missing")
    legacy_text = legacy.read_text(encoding="utf-8")
    for required in ('noindex', '../timeline/'):
        if required not in legacy_text:
            fail(f"legacy chronology redirect is missing {required!r}")
    if "app/timeline.js" in legacy_text or "id=\"timeline\"" in legacy_text:
        fail("legacy chronology route still contains the Timeline application")

    canonical = timeline_page.read_text(encoding="utf-8")
    if "Tim Dooley Timeline" not in canonical and "TIMELINE" not in canonical.upper():
        fail("canonical Timeline page does not identify itself as Timeline")
    if "TimDooley/chronology/" in canonical:
        fail("canonical Timeline page still declares chronology as canonical URL")

    forbidden_hits: list[str] = []
    visible_product_hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.resolve() == SELF:
            continue
        if rel == Path("chronology/index.html"):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "CNAME":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if "knowledge/chronology/" in text or "/chronology/" in text or "../chronology/" in text:
            forbidden_hits.append(str(rel))
        if "Chronology" in text or "CHRONOLOGY" in text:
            visible_product_hits.append(str(rel))

    if forbidden_hits:
        fail("active legacy chronology paths remain in: " + ", ".join(sorted(set(forbidden_hits))[:20]))
    if visible_product_hits:
        fail("active Chronology product naming remains in: " + ", ".join(sorted(set(visible_product_hits))[:20]))

    bad_names = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.resolve() == SELF:
            continue
        if rel == Path("chronology") or (rel.parts and rel.parts[0] == "chronology"):
            continue
        if "chronology" in path.name.lower():
            bad_names.append(str(rel))
    if bad_names:
        fail("active filenames/directories still use chronology: " + ", ".join(sorted(bad_names)[:20]))

    print("Timeline naming contract: PASS")


if __name__ == "__main__":
    main()
