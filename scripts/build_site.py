#!/usr/bin/env python3
"""Build the GitHub Pages artifact from the repository source.

The source HTML is content; shared chrome is a component. The build replaces any
legacy page header with the canonical component so navigation has one source of truth.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
HEADER = ROOT / "components" / "header.html"

EXCLUDE = {".git", ".github", "_site", "node_modules", "vendor"}
HEADER_RE = re.compile(r"<header\b[^>]*>.*?</header>", re.I | re.S)
MARKER_RE = re.compile(r'<div\s+data-site-header(?:="[^"]*")?\s*></div>', re.I)


def relative_root(page: Path) -> str:
    depth = len(page.relative_to(ROOT).parent.parts)
    return "../" * depth


def canonical_header(page: Path) -> str:
    return HEADER.read_text(encoding="utf-8").replace("{{ROOT}}", relative_root(page))


def transform_html(page: Path, text: str) -> str:
    header = canonical_header(page)
    if MARKER_RE.search(text):
        return MARKER_RE.sub(header, text, count=1)
    if HEADER_RE.search(text):
        return HEADER_RE.sub(header, text, count=1)
    body = re.search(r"<body\b[^>]*>", text, re.I)
    if body:
        return text[: body.end()] + "\n" + header + text[body.end() :]
    return text


def copy_tree() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for src in ROOT.iterdir():
        if src.name in EXCLUDE or src.name.startswith("."):
            continue
        dest = OUT / src.name
        if src.is_dir():
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*EXCLUDE))
        else:
            shutil.copy2(src, dest)


def build() -> None:
    if not HEADER.exists():
        raise SystemExit("Missing canonical header: components/header.html")
    copy_tree()
    count = 0
    for page in OUT.rglob("*.html"):
        # Resolve the source-relative path because OUT has the same public structure.
        source_page = ROOT / page.relative_to(OUT)
        text = page.read_text(encoding="utf-8")
        updated = transform_html(source_page, text)
        if updated != text:
            page.write_text(updated, encoding="utf-8")
            count += 1
    print(f"Built {_site_label(OUT)} with {count} standardized HTML headers.")


def _site_label(path: Path) -> str:
    return path.name


if __name__ == "__main__":
    build()
