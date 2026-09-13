#!/usr/bin/env python3
"""Generate additive canonical Atlas pages from the derived Atlas model."""
from __future__ import annotations

import html
import json
import os
from pathlib import Path

from atlas_model import build_model, by_id

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_URL = os.environ.get("SITE_BASE_URL", "https://thepotatooflife.github.io/TimDooley").rstrip("/")


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def href_for(route: str, *, depth: int) -> str:
    if route == "/":
        return "../" * depth
    rel = route.strip("/") + "/"
    return "../" * depth + rel


def page_shell(title: str, description: str, body: str, *, canonical: str, depth: int) -> str:
    css = "../" * depth + "app/design-system.css"
    home = "../" * depth
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | The Potato of Life</title>
<meta name="description" content="{esc(description[:300])}">
<link rel="canonical" href="{esc(canonical)}">
<link rel="stylesheet" href="{esc(css)}">
</head>
<body class="site-shell">
<a class="site-skip-link" href="#main">Skip to content</a>
<header class="site-header"><a href="{esc(home)}">Potato of Life</a></header>
<main id="main" class="site-main">{body}</main>
<footer class="site-footer"><a href="{esc(home)}">Potato of Life</a></footer>
</body>
</html>'''


def crumbs(node: dict, nodes: dict[str, dict]) -> str:
    items = []
    for node_id in node.get("north_path", []):
        target = nodes[node_id]
        if node_id == node["id"]:
            items.append(f'<span aria-current="page">{esc(target["title"])}</span>')
        else:
            items.append(f'<a href="{esc(href_for(target["route"], depth=2))}">{esc(target["title"])}</a>')
    return '<nav class="record-breadcrumbs" aria-label="Canonical position">' + " <span aria-hidden=\"true\">›</span> ".join(items) + "</nav>"


def render_node(node: dict, nodes: dict[str, dict]) -> str:
    parent = nodes.get(node.get("north_parent")) if node.get("north_parent") else None
    north = ""
    if parent:
        north = f'''<nav class="record-north" aria-label="Broader context">
<p class="record-junction-label">Broader context</p>
<a class="record-north-link" href="{esc(href_for(parent['route'], depth=2))}">↑ {esc(parent['title'])}</a>
</nav>'''

    badges = "".join(f'<span class="record-badge">{esc(x)}</span>' for x in node.get("epistemic_classes", []))
    sections = "".join(
        f'<section class="record-section" id="{esc(section["id"])}"><h2>{esc(section["title"])}</h2><p>{esc(section["text"])}</p></section>'
        for section in node.get("sections", [])
    )

    relation_rows = []
    for rel in node.get("relations", []):
        label = rel.get("type") or "Related"
        target = nodes.get(rel.get("target"))
        target_html = esc(rel.get("target"))
        if target:
            target_html = f'<a href="{esc(href_for(target["route"], depth=2))}">{esc(target["title"])}</a>'
        desc = f'<span>{esc(rel.get("description"))}</span>' if rel.get("description") else ""
        relation_rows.append(f'<li><strong>{esc(label)}</strong> · {target_html}{desc}</li>')
    relations = ""
    if relation_rows:
        relations = '<section class="record-relations"><h2>Connections</h2><ul>' + "".join(relation_rows) + "</ul></section>"

    child_rows = []
    for child_id in node.get("children", []):
        child = nodes[child_id]
        child_rows.append(f'<li><a href="{esc(href_for(child["route"], depth=2))}">{esc(child["title"])}</a><span>{esc(child["summary"])}</span></li>')
    children = ""
    if child_rows:
        children = '<section class="record-children"><h2>Within this</h2><ul>' + "".join(child_rows) + "</ul></section>"

    archive = '''<section class="record-archive">
<h2>Depth</h2>
<nav aria-label="Archive depth"><a href="../../archive/">History · Sources · Research · Archive</a></nav>
<p>The unified Archive projection is being introduced during the Atlas migration; canonical source material remains in its current owners meanwhile.</p>
</section>'''

    return f'''<article class="record-page">
{crumbs(node, nodes)}
{north}
<header class="page-header">
<p class="record-kind">{esc(node.get('kind'))}</p>
<h1>{esc(node['title'])}</h1>
<p class="page-summary">{esc(node['summary'])}</p>
<div class="record-badges">{badges}</div>
</header>
<div class="page-content u-reading">{sections}</div>
{relations}
{children}
{archive}
</article>'''


def render_landing(model: dict, nodes: dict[str, dict]) -> str:
    root = nodes[model["root_id"]]
    children = [nodes[x] for x in root.get("children", [])]
    cards = "".join(
        f'<li><a href="{esc(href_for(node["route"], depth=1))}"><strong>{esc(node["title"])}</strong><span>{esc(node["summary"])}</span></a></li>'
        for node in children
    )
    return f'''<article class="page-atlas">
<header class="page-header"><p class="record-kind">Current knowledge plane</p><h1>Atlas</h1><p class="page-summary">Canonical current subjects arranged by one North orientation, typed roads, and recoverable depth.</p></header>
<section><h2>Current root</h2><p><a href="{esc(href_for(root["route"], depth=1))}">{esc(root["title"])}</a></p></section>
<section><h2>First branches</h2><ul class="record-children">{cards}</ul></section>
</article>'''


def write(rel: str, text: str) -> None:
    path = OUT / rel / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    model = build_model()
    nodes = by_id(model)

    landing = render_landing(model, nodes)
    write("atlas", page_shell("Atlas", "Canonical current knowledge plane for the Potato of Life archive.", landing, canonical=f"{BASE_URL}/atlas/", depth=1))

    for node in nodes.values():
        body = render_node(node, nodes)
        write(f"atlas/{node['id']}", page_shell(node["title"], node["summary"], body, canonical=f"{BASE_URL}{node['route']}", depth=2))

    print(f"ATLAS PAGES BUILT: {len(nodes)} nodes + landing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
