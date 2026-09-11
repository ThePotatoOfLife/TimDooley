#!/usr/bin/env python3
"""Expose machine discovery in metadata without expanding reader navigation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "_site" / "index.html"

if not PAGE.exists():
    raise SystemExit("_site/index.html missing")

text = PAGE.read_text(encoding="utf-8")

old_sitemap = '<link rel="sitemap" type="application/xml" href="https://thepotatooflife.github.io/TimDooley/sitemap.xml">'
new_sitemap = '<link rel="sitemap" type="application/xml" href="https://thepotatooflife.github.io/TimDooley/sitemap-index.xml">'
text = text.replace(old_sitemap, new_sitemap)

head_close = text.find("</head>")
if head_close >= 0:
    head = text[:head_close]
    alternates = []
    if 'href="https://thepotatooflife.github.io/TimDooley/discovery.json"' not in head:
        alternates.append('  <link rel="alternate" type="application/json" href="https://thepotatooflife.github.io/TimDooley/discovery.json" title="Archive discovery index">')
    if 'href="https://thepotatooflife.github.io/TimDooley/llms-full.txt"' not in head:
        alternates.append('  <link rel="alternate" type="text/plain" href="https://thepotatooflife.github.io/TimDooley/llms-full.txt" title="Full machine retrieval index">')
    if alternates:
        text = text[:head_close] + "\n" + "\n".join(alternates) + "\n" + text[head_close:]

PAGE.write_text(text, encoding="utf-8")
print("Patched deployed homepage metadata without changing reader navigation")
