#!/usr/bin/env python3
"""Patch deployed homepage with durable discovery entry points.

This script deliberately anchors on the quicknav element itself instead of on an
exact previous list of links. The homepage grows over time, so matching a whole
old navigation tail made Pages deployment fail whenever a new link was added.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "_site" / "index.html"

if not PAGE.exists():
    raise SystemExit("_site/index.html missing")

text = PAGE.read_text(encoding="utf-8")


def ensure_quicknav_link(href: str, label: str, detail: str) -> None:
    global text
    if f'href="{href}"' in text:
        return
    start = text.find('<nav class="quicknav"')
    if start < 0:
        raise SystemExit("Homepage quicknav not found")
    end = text.find("</nav>", start)
    if end < 0:
        raise SystemExit("Homepage quicknav closing tag not found")
    link = f'      <a href="{href}"><strong>{label}</strong><span>{detail}</span></a>\n    '
    text = text[:end] + link + text[end:]


ensure_quicknav_link("questions/", "Questions", "Who · What · Why · How")
ensure_quicknav_link("index-a-z/", "A–Z Index", "Entities · aliases · concepts")

# Keep the discovery surfaces visible in the footer even when its wording evolves.
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

# Prefer the sitemap index and expose the generated discovery resources.
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
print("Patched deployed homepage with durable crawlable discovery entry points")
