#!/usr/bin/env python3
"""Build the GitHub Pages artifact as one self-contained index.html."""
from __future__ import annotations

import base64
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
EXCLUDE = {".git", ".github", "_site", "node_modules", "vendor", "__pycache__", "components", "scripts"}
MARKER = '<script id="potato-data" type="application/json">null</script>'


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_embedded_data() -> str:
    navigation = load_json(ROOT / "data" / "root-navigation.json")
    record_index = load_json(ROOT / "data" / "root-record-index.json")
    payload = {
        "manifest": navigation,
        "records": record_index.get("records", []),
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")


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
    source = OUT / "index.html"
    text = source.read_text(encoding="utf-8")
    if MARKER not in text:
        raise SystemExit("index.html is missing the potato-data build marker")
    encoded = build_embedded_data()
    replacement = f'<script id="potato-data" type="application/json">{encoded}</script>'
    source.write_text(text.replace(MARKER, replacement, 1), encoding="utf-8")

    pages = sorted(OUT.rglob("*.html"))
    if pages != [OUT / "index.html"]:
        found = [str(p.relative_to(OUT)) for p in pages]
        raise SystemExit(f"Public site must contain exactly one HTML document: {found}")
    print(f"Built _site with 1 HTML document and embedded data ({len(encoded)} base64 characters).")


if __name__ == "__main__":
    build()
