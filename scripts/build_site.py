#!/usr/bin/env python3
"""Build the GitHub Pages artifact while preserving the repository's existing site material."""
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
        if src.is_dir():
            shutil.copytree(src, OUT / src.name, ignore=shutil.ignore_patterns(*EXCLUDE))
        else:
            shutil.copy2(src, OUT / src.name)


def build() -> None:
    copy_tree()
    required = [OUT / "index.html", OUT / "root.js", OUT / "data" / "root-navigation.json", OUT / "data" / "root-record-index.json"]
    missing = [str(p.relative_to(OUT)) for p in required if not p.exists()]
    if missing:
        raise SystemExit(f"Required reader files are missing from _site: {missing}")

    pages = sorted(OUT.rglob("*.html"))
    if not pages:
        raise SystemExit("No HTML pages were copied into _site")

    print(f"Built _site with {len(pages)} HTML pages and the complete repository data tree.")


if __name__ == "__main__":
    build()
