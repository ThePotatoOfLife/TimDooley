#!/usr/bin/env python3
"""Build the GitHub Pages artifact from repository source.

Source pages contain content; shared chrome comes from components/header.html.
The build produces a clean _site directory and normalizes every HTML page to one
canonical header without requiring browser-side JavaScript.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
HEADER = ROOT / "components" / "header.html"
EXCLUDE = {".git", ".github", "_site", "node_modules", "vendor", "__pycache__"}
HEADER_RE = re.compile(r"<header\b[^>]*>.*?</header>", re.I | re.S)
MARKER_RE = re.compile(r'<div\s+data-site-header(?:="[^"]*")?\s*></div>', re.I)
BODY_RE = re.compile(r"<body\b[^>]*>", re.I)


def relative_root(page: Path) -> str:
    return "../" * len(page.relative_to(ROOT).parent.parts)


def canonical_header(page: Path) -> str:
    return HEADER.read_text(encoding="utf-8").replace("{{ROOT}}", relative_root(page))


def transform_html(page: Path, text: str) -> str:
    header = canonical_header(page)
    markers = list(MARKER_RE.finditer(text))
    headers = list(HEADER_RE.finditer(text))
    if markers:
        start, end = markers[0].span()
        text = text[:start] + header + text[end:]
        # Remove any additional legacy headers after the canonical insertion.
        text = HEADER_RE.sub(lambda m: "" if 'data-site-header="canonical"' not in m.group(0) else m.group(0), text)
        return text
    if headers:
        first = headers[0]
        return text[:first.start()] + header + text[first.end():]
    body = BODY_RE.search(text)
    if body:
        return text[:body.end()] + "\n" + header + text[body.end():]
    raise ValueError(f"No <body> or existing <header> in HTML page: {page.relative_to(ROOT)}")


def copy_tree() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
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
    for page in sorted(OUT.rglob("*.html")):
        source_page = ROOT / page.relative_to(OUT)
        text = page.read_text(encoding="utf-8")
        updated = transform_html(source_page, text)
        page.write_text(updated, encoding="utf-8")
        count += 1
    print(f"Built {OUT.name} with {count} standardized HTML headers.")


if __name__ == "__main__":
    build()
