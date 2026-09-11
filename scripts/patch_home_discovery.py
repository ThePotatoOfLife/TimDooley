#!/usr/bin/env python3
"""Patch deployed homepage with durable discovery entry points.

The primary homepage gateway row is intentionally curated in source. Generated
search/discovery destinations stay in the footer and metadata so build-time
patching cannot silently re-expand the main navigation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "_site" / "index.html"

if not PAGE.exists():
    raise SystemExit("_site/index.html missing")

text = PAGE.read_text(encoding="utf-8")

# Keep discovery surfaces crawlable without turning them into first-tier cards.
footer_pos = text.find('<footer class="footer">')
if footer_pos >= 0:
    footer_end = text.find("</footer>", footer_pos)
    if footer_end >= 0:
        footer = text[footer_pos:footer_end]
        additions = []
        if 'href="questions/"' not in footer:
            additions.append('<a href="questions/">Questions</a>')
        if 'href="index-a-z/"' not in footer:
            additions.append('<a href="index-a-z/">A–Z</a>')
        if 'href="sitemap-index.xml"' not in footer:
            additions.append('<a href="sitemap-index.xml">Sitemap index</a>')
        if additions:
            insert = " · " + " · ".join(additions) + "."
            text = text[:footer_end] + insert + text[footer_end:]

# Prefer the sitemap index and expose generated discovery resources in metadata.
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
print("Patched deployed homepage with footer/metadata discovery entry points")
