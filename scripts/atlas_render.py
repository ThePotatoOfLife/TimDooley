#!/usr/bin/env python3
"""Semantic HTML renderer for Atlas landing and canonical Node pages."""
from __future__ import annotations
import html


def esc(value:object)->str:return html.escape(str(value if value is not None else ''),quote=True)
def href_for(route:str,*,depth:int)->str:return '../'*depth if route=='/' else '../'*depth+route.strip('/')+'/'

def page_shell(title:str,description:str,body:str,*,canonical:str,depth:int)->str:
    css='../'*depth+'app/design-system.css';home='../'*depth;atlas_index='../'*depth+'data/atlas-index.json'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | The Potato of Life</title><meta name="description" content="{esc(description[:300])}"><link rel="canonical" href="{esc(canonical)}"><link rel="alternate" type="application/json" href="{esc(atlas_index)}" title="Atlas graph"><link rel="stylesheet" href="{esc(css)}"></head><body class="site-shell"><a class="site-skip-link" href="#main">Skip to content</a><header class="site-header"><a class="site-brand" href="{esc(home)}">Potato of Life</a></header><main id="main" class="site-main">{body}</main><footer class="site-footer"><a href="{esc(home)}">Potato of Life</a></footer></body></html>'''

def crumbs(node:dict,nodes:dict[str,dict])->str:
    items=[]
    for node_id in node.get('north_path',[]):
        target=nodes[node_id]
        items.append(f'<span aria-current="page">{esc(target["title"])}</span>' if node_id==node['id'] else f'<a href="{esc(href_for(target["route"],depth=2))}">{esc(target["title"])}</a>')
    return '<nav class="record-breadcrumbs" aria-label="Canonical position">'+' <span aria-hidden="true">›</span> '.join(items)+'</nav>'

def render_views(node:dict)->str:
    rows=[f'<a class="record-view-link" href="{esc(href_for(str(v["route"]),depth=2))}">{esc(v["title"])}</a>' for v in node.get('view_details',[])]
    return '' if not rows else '<nav class="record-views" aria-label="Ways through this subject"><p class="record-junction-label">Appears in</p>'+''.join(rows)+'</nav>'

def render_relations(node:dict,nodes:dict[str,dict])->str:
    rows=[]
    for rel in node.get('relations',[]):
        target=nodes.get(rel.get('target'))
        target_html=esc(rel.get('artifact_title') or rel.get('target'))
        if target:
            target_html=f'<a href="{esc(href_for(target["route"],depth=2))}">{esc(target["title"])}</a>'
        elif rel.get('resolved_kind')=='artifact' and isinstance(rel.get('route'),str) and rel.get('route'):
            target_html=f'<a href="{esc(href_for(rel["route"],depth=2))}">{esc(rel.get("artifact_title") or rel.get("target"))}</a>'
        provisional=' <small>provisional road type</small>' if rel.get('provisional_type') else ''
        desc=f'<span>{esc(rel.get("description"))}</span>' if rel.get('description') else ''
        rows.append(f'<li data-orientation="{esc(rel.get("orientation","lateral"))}"><strong>{esc(rel.get("label") or rel.get("type") or "Related")}</strong> · {target_html}{provisional}{desc}</li>')
    return '' if not rows else '<section class="record-relations"><h2>Connections</h2><ul>'+''.join(rows)+'</ul></section>'

def render_children(node:dict,nodes:dict[str,dict])->str:
    rows=[]
    for child_id in node.get('children',[]):
        child=nodes[child_id];rows.append(f'<li><a href="{esc(href_for(child["route"],depth=2))}">{esc(child["title"])}</a><span>{esc(child["summary"])}</span></li>')
    return '' if not rows else '<section class="record-children"><h2>Within this</h2><ul>'+''.join(rows)+'</ul></section>'

def render_depth(node:dict)->str:
    rows=[]
    for artifact in node.get('artifacts',[]):
        title=esc(artifact.get('title'))
        route=artifact.get('public_route')
        title_html=f'<a href="{esc(href_for(route,depth=2))}">{title}</a>' if isinstance(route,str) and route else title
        date=f'<span>{esc(artifact.get("date_or_period"))}</span>' if artifact.get('date_or_period') else ''
        rows.append(f'<li><strong>{title_html}</strong><span>{esc(artifact.get("kind"))}</span>{date}<p>{esc(artifact.get("summary"))}</p></li>')
    roots='' if not rows else '<h3>Archive roots</h3><ul class="record-artifacts">'+''.join(rows)+'</ul>'
    return f'''<section class="record-archive"><h2>Depth</h2><nav aria-label="Current depth routes"><a href="../../timeline/">History</a> · <a href="../../context/source-authority/">Sources</a> · <a href="../../explore/">Research</a></nav>{roots}<p class="record-migration-note">The unified public Archive projection is introduced later in the migration. Current material remains in canonical source owners until that route is safe to publish.</p></section>'''

def render_node(node:dict,nodes:dict[str,dict])->str:
    parent=nodes.get(node.get('north_parent')) if node.get('north_parent') else None;north=''
    if parent:north=f'<nav class="record-north" aria-label="Broader context"><p class="record-junction-label">Broader context</p><a class="record-north-link" href="{esc(href_for(parent["route"],depth=2))}">↑ {esc(parent["title"])}</a></nav>'
    badges=''.join(f'<span class="record-badge">{esc(x)}</span>' for x in node.get('epistemic_classes',[]))
    sections=''.join(f'<section class="record-section" id="{esc(s["id"])}"><h2>{esc(s["title"])}</h2><p>{esc(s["text"])}</p></section>' for s in node.get('sections',[]))
    return f'<article class="record-page">{crumbs(node,nodes)}{north}<header class="page-header"><p class="record-kind">{esc(node.get("kind"))}</p><h1>{esc(node["title"])}</h1><p class="page-summary">{esc(node["summary"])}</p><div class="record-badges">{badges}</div>{render_views(node)}</header><div class="page-content u-reading">{sections}</div>{render_relations(node,nodes)}{render_children(node,nodes)}{render_depth(node)}</article>'

def render_landing(model:dict,nodes:dict[str,dict])->str:
    root=nodes[model['root_id']];children=[nodes[x] for x in root.get('children',[])];views=[v for v in model.get('views',[]) if v.get('id')!='start']
    cards=''.join(f'<li><a href="{esc(href_for(n["route"],depth=1))}"><strong>{esc(n["title"])}</strong><span>{esc(n["summary"])}</span></a></li>' for n in children)
    view_links=''.join(f'<li><a href="{esc(href_for(v["route"],depth=1))}"><strong>{esc(v["title"])}</strong><span>{esc(v["description"])}</span></a></li>' for v in views)
    return f'<article class="page-atlas"><header class="page-header"><p class="record-kind">Current knowledge plane</p><h1>Atlas</h1><p class="page-summary">Canonical current subjects arranged by one North orientation, typed roads, public Rooms, and recoverable depth.</p></header><section><h2>Current root</h2><p><a href="{esc(href_for(root["route"],depth=1))}">{esc(root["title"])}</a></p></section><section><h2>First branches</h2><ul class="record-children">{cards}</ul></section><section><h2>Ways through</h2><ul class="record-views-list">{view_links}</ul></section></article>'
