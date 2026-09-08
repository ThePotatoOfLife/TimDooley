#!/usr/bin/env python3
"""Build the GitHub Pages artifact from repository source."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
EXCLUDE = {".git", ".github", "_site", "node_modules", "vendor", "__pycache__", "components", "scripts"}


def copy_tree() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for src in ROOT.iterdir():
        if src.name in EXCLUDE or src.name.startswith("."):
            continue
        if src.is_file() and src.suffix.lower() == ".html" and src.name != "index.html":
            continue
        if src.is_dir():
            shutil.copytree(src, OUT / src.name, ignore=shutil.ignore_patterns(*EXCLUDE, "*.html"))
        else:
            shutil.copy2(src, OUT / src.name)


def build() -> None:
    copy_tree()
    pages = sorted(OUT.rglob("*.html"))
    expected = [OUT / "index.html"]
    if pages != expected:
        found = [str(p.relative_to(OUT)) for p in pages]
        raise SystemExit(f"Public site must contain exactly one HTML document: {found}")
    print("Built _site with 1 public HTML document: index.html")


if __name__ == "__main__":
    build()
