#!/usr/bin/env python3
"""Normalize public discovery metadata and World-family projection in the built artifact."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
PAGE = SITE / "index.html"
BASE = "https://thepotatooflife.github.io/TimDooley/"

if not PAGE.exists():
    raise SystemExit("_site/index.html missing")


def patch_text(path: Path, replacements: tuple[tuple[str, str], ...]) -> None:
    if not path.exists():
        raise SystemExit(f"missing built page: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


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

# The canonical homepage World entrance is /world/ in every environment.
# Deployment normalization must never temporarily rewrite it to /world-map/;
# validators are read-only and the public artifact is correct before they run.
PAGE.write_text(text, encoding="utf-8")

patch_text(
    SITE / "north" / "index.html",
    (
        ("<title>North Axis — World Map</title>", "<title>North Axis — The Potato of Life</title>"),
        (
            '<nav><a href="../">Home</a><a href="../tim-dooley/">Tim Dooley</a><a href="../world-map/">World Map</a></nav>',
            '<nav class="world-family" aria-label="World sections"><a href="../world/">World</a><a href="../world-map/">Map</a><a href="../politics/">Politics</a><a aria-current="page" href="./">North</a><a href="../world-systems/">Systems</a></nav>',
        ),
    ),
)

# The source map still contains compatibility controls consumed by 3d-app.js.
# In the public artifact they start hidden, then 3d-world-bar.js adopts the
# functional Analyze/Time/View controls into one stable header toolbar. This
# prevents the legacy header from flashing before the registry UI initializes.
patch_text(
    SITE / "world-map" / "index.html",
    (
        (
            '<div class="quick-actions"><button id="compare">Compare</button><button id="panelToggle" class="panel-toggle" title="Show or hide deeper inspector" aria-label="Show or hide deeper inspector">Inspect</button></div>',
            '<div class="quick-actions"><button id="compare">Compare</button><button id="panelToggle" class="panel-toggle" title="Show or hide deeper inspector" aria-label="Show or hide deeper inspector">Inspect</button></div><div id="atlasWorldBarHost" aria-label="World map controls"></div>',
        ),
        ('<details class="menu" id="layersMenu">', '<details class="menu" id="layersMenu" hidden>'),
        ('<details class="menu" id="traceMenu">', '<details class="menu" id="traceMenu" hidden>'),
        ('<details class="menu" id="timeMenu">', '<details class="menu" id="timeMenu" hidden>'),
        ('<details class="menu" id="viewMenu">', '<details class="menu" id="viewMenu" hidden>'),
        (
            '<a class="top-home" href="../">Home</a>',
            '<a class="top-home" href="../world/">World</a><a class="top-home" href="../politics/">Politics</a><a class="top-home" href="../north/">North</a><a class="top-home" href="../world-systems/">Systems</a><a class="top-home" href="../">Home</a>',
        ),
        ('href="../explore/#branch=world">World systems</a>', 'href="../world-systems/">World systems</a>'),
    ),
)

machine_path = SITE / "machine-index.json"
if not machine_path.exists():
    raise SystemExit("_site/machine-index.json missing")
machine = json.loads(machine_path.read_text(encoding="utf-8"))
rows = machine.setdefault("primary_reader_urls", [])
world_topics = {
    "World": BASE + "world/",
    "World Map": BASE + "world-map/",
    "Politics & Geopolitics": BASE + "politics/",
    "North Axis / North Programme": BASE + "north/",
    "World Systems": BASE + "world-systems/",
}
rows[:] = [row for row in rows if not (isinstance(row, dict) and row.get("topic") in world_topics)]
for topic, url in world_topics.items():
    rows.append({"topic": topic, "url": url})
machine_path.write_text(json.dumps(machine, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Patched public discovery metadata, World-family navigation, unified map header and machine routes")
