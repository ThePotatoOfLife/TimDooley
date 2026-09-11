#!/usr/bin/env python3
"""Build the GitHub Pages artifact for the manifest-driven Potato of Life archive.

The interactive site remains the primary human interface. This builder also emits
static crawlable HTML pages, a sitemap and machine-oriented discovery files so
search engines and AI agents can understand the archive without depending on
client-side JavaScript.
"""
from __future__ import annotations

import html
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
EXCLUDE = {".git", ".github", "_site", "node_modules", "vendor", "__pycache__", "components", "scripts", "archive"}
BASE_URL = os.environ.get("SITE_BASE_URL", "https://thepotatooflife.github.io/TimDooley").rstrip("/")


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


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def slug(value: str) -> str:
    value = value.strip().lower()
    out = []
    dash = False
    for ch in value:
        if ch.isalnum():
            out.append(ch)
            dash = False
        elif not dash:
            out.append("-")
            dash = True
    return "".join(out).strip("-") or "item"


def summary_from_record(data: dict, fallback: str = "") -> str:
    for key in ("summary", "purpose", "description", "core_thesis", "definition"):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    sections = data.get("sections")
    if isinstance(sections, dict):
        for section in sections.values():
            if isinstance(section, dict) and isinstance(section.get("text"), str):
                return section["text"].strip()
    return fallback


def text_blocks(data, depth=0, limit=80):
    blocks = []
    if len(blocks) >= limit:
        return blocks
    if isinstance(data, dict):
        for key, value in data.items():
            if key in {"title", "name", "id", "summary"}:
                continue
            label = esc(str(key).replace("_", " ").replace("-", " ").title())
            if isinstance(value, str):
                blocks.append(f"<section><h2>{label}</h2><p>{esc(value)}</p></section>")
            elif isinstance(value, (int, float, bool)):
                blocks.append(f"<section><h2>{label}</h2><p>{esc(value)}</p></section>")
            elif isinstance(value, list) and value and all(isinstance(x, (str, int, float, bool)) for x in value):
                items = "".join(f"<li>{esc(x)}</li>" for x in value)
                blocks.append(f"<section><h2>{label}</h2><ul>{items}</ul></section>")
            elif depth < 2 and isinstance(value, (dict, list)):
                nested = text_blocks(value, depth + 1, limit)
                if nested:
                    blocks.append(f"<section><h2>{label}</h2>{''.join(nested)}</section>")
            if len(blocks) >= limit:
                break
    elif isinstance(data, list):
        for item in data[:30]:
            if isinstance(item, str):
                blocks.append(f"<p>{esc(item)}</p>")
            elif depth < 2:
                blocks.extend(text_blocks(item, depth + 1, limit))
    return blocks[:limit]


def page_shell(title: str, description: str, canonical: str, body: str, *, page_type="Article", about=None) -> str:
    desc = " ".join(description.split())[:300]
    about = about or []
    ld = {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": title,
        "headline": title,
        "description": desc,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "The Potato of Life", "url": BASE_URL + "/"},
        "about": [{"@type": "Thing", "name": x} for x in about[:20]],
        "inLanguage": "en",
        "isAccessibleForFree": True,
    }
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="stylesheet" href="{BASE_URL}/app/style.css">
<style>
body{{background:#050805;color:#e9eee7;font-family:Inter,system-ui,sans-serif;margin:0}}main{{max-width:880px;margin:auto;padding:44px 22px 90px}}a{{color:#a9d875}}h1{{font-size:clamp(2.5rem,6vw,5rem);line-height:.95}}h2{{margin-top:36px}}p,li{{line-height:1.65}}.summary{{font:400 20px/1.6 Georgia,serif;color:#c8d0c4}}nav{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:34px}}code{{background:#101710;padding:.15em .35em;border-radius:4px}}
</style>
</head>
<body><main>
<nav><a href="{BASE_URL}/">Home</a><a href="{BASE_URL}/tim-dooley/">Tim Dooley</a><a href="{BASE_URL}/religion/">Religion</a><a href="{BASE_URL}/philosophy/">Philosophy</a><a href="{BASE_URL}/science/">Science</a><a href="{BASE_URL}/world-map/3d.html">World Map</a></nav>
<h1>{esc(title)}</h1>
<p class="summary">{esc(desc)}</p>
{body}
</main></body></html>'''


# Remaining builder functions are intentionally unchanged below this point.
