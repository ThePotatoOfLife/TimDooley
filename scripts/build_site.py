#!/usr/bin/env python3
"""Build the GitHub Pages artifact for the manifest-driven Potato of Life archive."""
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
    required = [
        OUT / "index.html",
        OUT / "manifest.json",
        OUT / "app" / "app.js",
        OUT / "app" / "style.css",
        OUT / "knowledge" / "core" / "potato-of-life.json",
        OUT / "knowledge" / "core" / "tim-dooley.json",
    ]
    missing = [str(p.relative_to(OUT)) for p in required if not p.exists()]
    if missing:
        raise SystemExit(f"Required manifest-driven archive files are missing from _site: {missing}")

    pages = sorted(OUT.rglob("*.html"))
    if not pages:
        raise SystemExit("No HTML pages were copied into _site")

    print(
        f"Built manifest-driven Potato of Life archive with {len(pages)} HTML pages "
        "and the complete repository knowledge/data tree."
    )


if __name__ == "__main__":
    build()
