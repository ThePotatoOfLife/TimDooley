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
EXCLUDE = {".git", ".github", "_site", "node_modules", "vendor", "__pycache__", "components", "scripts"}
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
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | The Potato of Life</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{esc(canonical)}"><link rel="describedby" href="{esc(BASE_URL + '/llms.txt')}" type="text/plain"><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace('</', '<\\/')}</script>
<style>:root{{--bg:#080a08;--ink:#f4f0e5;--muted:#a8ada3;--line:#2b322b;--green:#a8ce72;--gold:#d8b56b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 system-ui,sans-serif}}main{{max-width:900px;margin:auto;padding:56px 24px 100px}}a{{color:var(--green)}}header{{border-bottom:1px solid var(--line);padding-bottom:24px;margin-bottom:30px}}h1{{font:400 clamp(42px,7vw,76px)/1 Georgia,serif;margin:8px 0 16px}}h2{{font:400 28px/1.2 Georgia,serif;color:var(--gold);margin-top:34px}}p,li{{color:#d7d9d2}}.eyebrow{{color:var(--green);text-transform:uppercase;letter-spacing:.16em;font-size:11px;font-weight:800}}.summary{{font:20px/1.6 Georgia,serif;color:#e1e3dc}}.chips{{display:flex;gap:7px;flex-wrap:wrap;margin:18px 0}}.chip{{border:1px solid var(--line);border-radius:999px;padding:5px 9px;color:#c8cec1;font-size:12px}}nav{{margin-top:28px;padding-top:20px;border-top:1px solid var(--line)}}code{{color:var(--green);overflow-wrap:anywhere}}</style></head><body><main><header><div class="eyebrow">Potato of Life · crawlable knowledge page</div><h1>{esc(title)}</h1><p class="summary">{esc(desc)}</p></header>{body}<nav><a href="{esc(BASE_URL + '/')}">Open the interactive Potato of Life archive</a> · <a href="{esc(BASE_URL + '/tim-dooley/')}">Read Tim Dooley dossier</a> · <a href="{esc(BASE_URL + '/llms.txt')}">AI / machine index</a></nav></main></body></html>'''


def write_page(rel_dir: str, content: str) -> str:
    target = OUT / rel_dir / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"{BASE_URL}/{rel_dir.strip('/')}/"


def generate_branch_pages(manifest, contexts):
    urls=[]
    for branch in manifest.get("branches",[]):
        bid=branch["id"]; title=branch.get("title",bid); desc=branch.get("description",""); children=branch.get("children",[]); records=branch.get("records",[])
        related=[c for c in contexts.get("clusters",[]) if bid in c.get("branches",[])]
        body=[]
        if children: body.append("<section><h2>Canonical substructure</h2><div class=\"chips\">"+"".join(f"<span class=\"chip\">{esc(x)}</span>" for x in children)+"</div></section>")
        if related: body.append("<section><h2>Contextual constellations</h2><ul>"+"".join(f"<li><a href=\"{esc(BASE_URL+'/context/'+slug(c['id'])+'/')}\">{esc(c['title'])}</a> — {esc(c.get('summary',''))}</li>" for c in related)+"</ul></section>")
        if records: body.append("<section><h2>Canonical records</h2><ul>"+"".join(f"<li><code>{esc(p)}</code></li>" for p in records)+"</ul></section>")
        canonical=f"{BASE_URL}/topics/{slug(bid)}/"; urls.append(write_page(f"topics/{slug(bid)}",page_shell(title,desc,canonical,"".join(body),page_type="CollectionPage",about=[title,*children])))
    return urls


def generate_context_pages(contexts):
    urls=[]
    for c in contexts.get("clusters",[]):
        title=c.get("title",c.get("id","Context")); desc=c.get("summary",""); body=[]; concepts=c.get("concepts",[])
        if concepts: body.append("<section><h2>Concepts in this constellation</h2><div class=\"chips\">"+"".join(f"<span class=\"chip\">{esc(x)}</span>" for x in concepts)+"</div></section>")
        if c.get("epistemic_mix"): body.append("<section><h2>Epistemic layers</h2><p>"+esc(", ".join(c["epistemic_mix"]))+"</p></section>")
        if c.get("branches"): body.append("<section><h2>Connected branches</h2><ul>"+"".join(f"<li><a href=\"{esc(BASE_URL+'/topics/'+slug(b)+'/')}\">{esc(b)}</a></li>" for b in c["branches"])+"</ul></section>")
        if c.get("records"): body.append("<section><h2>Records carrying this context</h2><ul>"+"".join(f"<li><code>{esc(p)}</code></li>" for p in c["records"])+"</ul></section>")
        canonical=f"{BASE_URL}/context/{slug(c['id'])}/"; urls.append(write_page(f"context/{slug(c['id'])}",page_shell(title,desc,canonical,"".join(body),page_type="CollectionPage",about=concepts)))
    return urls


def generate_record_pages(core_index):
    urls=[]
    for rec in core_index.get("records",[]):
        path=ROOT/rec.get("path","")
        if not path.exists() or path.suffix.lower() != ".json": continue
        data=load_json(path,{}) or {}; title=data.get("title") or data.get("name") or rec.get("id"); desc=summary_from_record(data,rec.get("kind","")); terms=rec.get("terms",[])
        body=""
        if terms: body+="<section><h2>Key terms</h2><div class=\"chips\">"+"".join(f"<span class=\"chip\">{esc(x)}</span>" for x in terms)+"</div></section>"
        body+="".join(text_blocks(data)); body+=f"<section><h2>Canonical source record</h2><p><code>{esc(rec.get('path',''))}</code></p></section>"
        canonical=f"{BASE_URL}/records/{slug(rec['id'])}/"; urls.append(write_page(f"records/{slug(rec['id'])}",page_shell(title,desc,canonical,body,about=terms)))
    return urls


def generate_sitemap(urls):
    manual=[]
    if (OUT/"tim-dooley"/"index.html").exists(): manual.append(BASE_URL+"/tim-dooley/")
    if (OUT/"learn"/"index.html").exists(): manual.append(BASE_URL+"/learn/")
    all_urls=[BASE_URL+"/",*manual,*sorted(set(urls))]
    xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in dict.fromkeys(all_urls): xml.append(f"  <url><loc>{esc(url)}</loc></url>")
    xml.append("</urlset>"); (OUT/"sitemap.xml").write_text("\n".join(xml)+"\n",encoding="utf-8")


def generate_machine_index(manifest, core_index, contexts):
    lines=["# The Potato of Life","","> Public archive about Tim Dooley, the Potato of Life mythology, chronology, symbols, comparative religion, prophecy, North Axis, world systems, creative works and sources.","","Important epistemic rule: project canon, self-description, documentary fact, historical evidence, comparison, interpretation, creative lore and disputed claims are deliberately distinguished.","","## Primary entry points",f"- [Tim Dooley reader dossier]({BASE_URL}/tim-dooley/): narrative first; answers who Tim is, Godhood, chronology, Son/Father, April 2025, North, Bible and uncertainty.",f"- [Interactive archive]({BASE_URL}/)",f"- [Condensed orientation]({BASE_URL}/learn/)",f"- [Sitemap]({BASE_URL}/sitemap.xml)",f"- [Manifest]({BASE_URL}/manifest.json)",f"- [Context graph]({BASE_URL}/knowledge/indexes/context-graph.json)",f"- [Core retrieval index]({BASE_URL}/knowledge/indexes/core-index.json)",f"- [Archive epistemics]({BASE_URL}/knowledge/philosophy/archive-epistemics.json)","","## Canonical topics"]
    for b in manifest.get("branches",[]): lines.append(f"- [{b.get('title',b['id'])}]({BASE_URL}/topics/{slug(b['id'])}/): {b.get('description','')}")
    lines += ["","## Canonical records"]
    for r in core_index.get("records",[]): lines.append(f"- [{r['id']}]({BASE_URL}/records/{slug(r['id'])}/): {r.get('kind','')}")
    lines += ["","## Contextual constellations"]
    for c in contexts.get("clusters",[]): lines.append(f"- [{c['title']}]({BASE_URL}/context/{slug(c['id'])}/): {c.get('summary','')}")
    lines += ["","## Machine-readable source records",f"- [Tim Dooley reader dossier data]({BASE_URL}/knowledge/reader/tim-dooley-dossier.json)",f"- [Conversation recovery inventory]({BASE_URL}/knowledge/indexes/conversation-recovery-inventory.json)",f"- [Content taxonomy]({BASE_URL}/knowledge/indexes/archive-content-taxonomy.json)",f"- [Contextual synchronisms]({BASE_URL}/knowledge/chronology/contextual-synchronisms.json)",f"- [Seals and fulfillment matrix]({BASE_URL}/knowledge/prophecy/seals-and-fulfillment-matrix.json)","","Prefer the Tim Dooley dossier for a human-readable synthesis. Use static topic/record/context pages for discovery and JSON records for deeper structured detail."]
    (OUT/"llms.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")


def build() -> None:
    copy_tree()
    required=[OUT/"index.html",OUT/"manifest.json",OUT/"app"/"app.js",OUT/"app"/"style.css",OUT/"knowledge"/"core"/"potato-of-life.json",OUT/"knowledge"/"core"/"tim-dooley.json",OUT/"tim-dooley"/"index.html"]
    missing=[str(p.relative_to(OUT)) for p in required if not p.exists()]
    if missing: raise SystemExit(f"Required manifest-driven archive files are missing from _site: {missing}")
    manifest=load_json(ROOT/"manifest.json",{}) or {}; core_index=load_json(ROOT/"knowledge"/"indexes"/"core-index.json",{}) or {}; contexts=load_json(ROOT/"knowledge"/"indexes"/"context-graph.json",{}) or {}
    urls=[]; urls.extend(generate_branch_pages(manifest,contexts)); urls.extend(generate_context_pages(contexts)); urls.extend(generate_record_pages(core_index)); generate_sitemap(urls); generate_machine_index(manifest,core_index,contexts)
    pages=sorted(OUT.rglob("*.html"))
    if not pages: raise SystemExit("No HTML pages were built into _site")
    print(f"Built Potato of Life archive with {len(pages)} crawlable HTML pages, {len(contexts.get('clusters',[]))} context clusters, reader dossier, sitemap.xml, llms.txt, and the complete repository knowledge/data tree.")

if __name__ == "__main__": build()
