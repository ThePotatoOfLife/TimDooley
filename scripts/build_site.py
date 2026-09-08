#!/usr/bin/env python3
"""Build the GitHub Pages artifact from the existing site structure."""
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
    index = OUT / "index.html"
    root_js = OUT / "root.js"
    navigation = OUT / "data" / "root-navigation.json"
    records = OUT / "data" / "root-record-index.json"
    missing = [str(p.relative_to(OUT)) for p in (index, root_js, navigation, records) if not p.exists()]
    if missing:
        raise SystemExit(f"Required reader files are missing from _site: {missing}")

    pages = sorted(OUT.rglob("*.html"))
    if pages != [index]:
        found = [str(p.relative_to(OUT)) for p in pages]
        raise SystemExit(f"Public site must contain exactly one HTML document: {found}")

    print("Built _site from the existing index/root.js/data navigation stack.")


if __name__ == "__main__":
    build()
