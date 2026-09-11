#!/usr/bin/env python3
"""Build the public discovery layer after scripts/build_site.py.

This pass makes the archive easy to crawl without JavaScript by generating one
stable HTML URL per canonical FAQ entry, question-family indexes, an A-Z index,
AI-oriented retrieval files, permissive robots rules, and segmented sitemaps.

FAQ discovery is intentionally extensible: every knowledge/indexes/faq-*.json file
with an ``entries`` array is treated as a view over canonical knowledge. This lets
new research branches add search-language questions without editing one giant FAQ
owner or duplicating the underlying canonical records.
"""
from __future__ import annotations

import html
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_URL = os.environ.get("SITE_BASE_URL", "https://thepotatooflife.github.io/TimDooley").rstrip("/")
FAQ = ROOT / "knowledge" / "indexes" / "faq-answer-atlas.json"
TIM_Q = ROOT / "knowledge" / "reader" / "tim-dooley-question-index.json"


def esc(v):
    return html.escape(str(v if v is not None else ""), quote=True)


def slug(v):
    s = re.sub(r"[^a-z0-9]+", "-", str(v).lower()).strip("-")
    return s or "item"


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def shell(title, description, canonical, body, schema=None):
    schema = schema or {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": description,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "The Potato of Life", "url": BASE_URL + "/"},
    }
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | The Potato of Life</title>
<meta name="description" content="{esc(description[:300])}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<link rel="canonical" href="{esc(canonical)}">
<link rel="alternate" type="text/plain" href="{esc(BASE_URL + '/llms.txt')}" title="LLM index">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('</','<\\/')}</script>
<style>:root{{--bg:#080a08;--ink:#f5f1e7;--muted:#aab0a7;--line:#303830;--green:#acd67a;--gold:#dfbc72}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 system-ui,sans-serif}}main{{max-width:980px;margin:auto;padding:54px 22px 100px}}a{{color:var(--green);text-decoration-thickness:1px;text-underline-offset:3px}}h1{{font:400 clamp(38px,6vw,72px)/1.04 Georgia,serif;margin:.15em 0}}h2{{font:400 28px/1.2 Georgia,serif;color:var(--gold);margin-top:36px}}.lead{{font:20px/1.6 Georgia,serif;color:#e5e3dc;max-width:820px}}.eyebrow{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--green);font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}.card{{border:1px solid var(--line);border-radius:14px;padding:16px;background:#0d100d}}.meta,.muted{{color:var(--muted)}}.chips{{display:flex;flex-wrap:wrap;gap:7px}}.chip{{border:1px solid var(--line);border-radius:999px;padding:4px 9px;font-size:12px;color:#d8ddd2}}nav{{border-top:1px solid var(--line);margin-top:44px;padding-top:22px}}code{{color:var(--green);overflow-wrap:anywhere}}</style></head><body><main>
<div class="eyebrow">Potato of Life · public discovery layer</div><h1>{esc(title)}</h1><p class="lead">{esc(description)}</p>{body}
<nav><a href="{BASE_URL}/">Home</a> · <a href="{BASE_URL}/tim-dooley/">Tim Dooley</a> · <a href="{BASE_URL}/faq/">FAQ</a> · <a href="{BASE_URL}/questions/">Question index</a> · <a href="{BASE_URL}/index-a-z/">A–Z</a> · <a href="{BASE_URL}/llms.txt">Machine index</a></nav>
</main></body></html>'''


def family_for(question):
    q = question.strip().lower()
    for family in ("who", "what", "where", "when", "which", "why", "how"):
        if q.startswith(family + " "):
            return family
    if q.startswith(("is ", "are ", "was ", "were ", "does ", "do ", "did ", "can ", "could ", "will ")):
        return "is-does-can"
    return "other"


def faq_entries():
    """Merge all FAQ views by id; canonical base wins on duplicate ids."""
    by_id = {}
    atlas = load(FAQ, {})
    for e in atlas.get("entries", []) if isinstance(atlas, dict) else []:
        if isinstance(e, dict) and e.get("id"):
            by_id[e["id"]] = e

    faq_dir = ROOT / "knowledge" / "indexes"
    for path in sorted(faq_dir.glob("faq-*.json")):
        if path == FAQ:
            continue
        data = load(path, {})
        for e in data.get("entries", []) if isinstance(data, dict) else []:
            if isinstance(e, dict) and e.get("id") and e["id"] not in by_id:
                e = dict(e)
                e.setdefault("source_faq_view", str(path.relative_to(ROOT)))
                by_id[e["id"]] = e

    reader = load(TIM_Q, {})
    for q in reader.get("questions", []) if isinstance(reader, dict) else []:
        if not isinstance(q, dict) or not q.get("id") or q.get("id") in by_id:
            continue
        by_id[q["id"]] = {
            "id": q["id"],
            "question": q.get("question", q["id"]),
            "variants": q.get("search_variants", []),
            "short_answer": q.get("answer", ""),
            "deep_answer": q.get("answer", ""),
            "entities": q.get("entities", ["Tim Dooley"]),
            "dates": q.get("dates", []),
            "aliases": [],
            "epistemic_class": q.get("epistemic_class", []),
            "canonical_owners": q.get("canonical_owners", []),
            "related_questions": q.get("related_questions", []),
            "search_terms": q.get("search_variants", []),
            "source_faq_view": str(TIM_Q.relative_to(ROOT)),
        }
    return list(by_id.values())


def question_page(e):
    q = e.get("question", e.get("id", "Question"))
    short = e.get("short_answer") or e.get("answer") or ""
    deep = e.get("deep_answer") or short
    eid = slug(e.get("id", q))
    canonical = f"{BASE_URL}/questions/{eid}/"
    entities = [str(x) for x in e.get("entities", [])]
    variants = [str(x) for x in e.get("variants", [])]
    owners = [str(x) for x in e.get("canonical_owners", [])]
    related = [slug(x) for x in e.get("related_questions", [])]
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "url": canonical,
        "mainEntity": [{
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": deep or short},
        }],
        "about": [{"@type": "Thing", "name": x} for x in entities[:20]],
        "isPartOf": {"@type": "WebSite", "name": "The Potato of Life", "url": BASE_URL + "/"},
    }
    body = f"<section><h2>Answer</h2><p>{esc(short)}</p></section>"
    if deep and deep != short:
        body += f"<section><h2>Full answer</h2><p>{esc(deep)}</p></section>"
    if variants:
        body += "<section><h2>Equivalent searches</h2><div class=\"chips\">" + "".join(f"<span class=\"chip\">{esc(x)}</span>" for x in variants) + "</div></section>"
    if entities:
        body += "<section><h2>Entities</h2><div class=\"chips\">" + "".join(f"<span class=\"chip\">{esc(x)}</span>" for x in entities) + "</div></section>"
    if e.get("dates"):
        body += "<section><h2>Dates</h2><p>" + esc(" · ".join(map(str, e["dates"]))) + "</p></section>"
    if e.get("epistemic_class"):
        body += "<section><h2>Archive classification</h2><p>" + esc(" · ".join(map(str, e["epistemic_class"]))) + "</p></section>"
    if owners:
        body += "<section><h2>Canonical owners</h2><ul>" + "".join(f"<li><code>{esc(x)}</code></li>" for x in owners) + "</ul></section>"
    if e.get("source_faq_view"):
        body += f"<section><h2>Discovery view</h2><p><code>{esc(e['source_faq_view'])}</code></p></section>"
    if related:
        body += "<section><h2>Related questions</h2><ul>" + "".join(f"<li><a href=\"{BASE_URL}/questions/{x}/\">{esc(x.replace('-', ' '))}</a></li>" for x in related) + "</ul></section>"
    return eid, shell(q, short or deep, canonical, body, schema)


def build_questions(entries):
    families = defaultdict(list)
    urls = []
    for e in entries:
        eid, page = question_page(e)
        write(f"questions/{eid}/index.html", page)
        urls.append(f"{BASE_URL}/questions/{eid}/")
        families[family_for(e.get("question", ""))].append(e)

    cards = []
    for family in sorted(families):
        label = family.replace("-", " / ").title()
        cards.append(f'<div class="card"><h2><a href="{BASE_URL}/questions/{family}/">{esc(label)}</a></h2><p>{len(families[family])} crawlable questions</p></div>')
        items = "".join(f'<li><a href="{BASE_URL}/questions/{slug(e.get("id",e.get("question","")))}/">{esc(e.get("question",""))}</a></li>' for e in families[family])
        page = shell(f"{label} questions", f"Canonical {label.lower()} questions about Tim Dooley, the Potato of Life, the Son, Father, timeline, symbols and the wider archive.", f"{BASE_URL}/questions/{family}/", f"<section><ul>{items}</ul></section>")
        write(f"questions/{family}/index.html", page)
        urls.append(f"{BASE_URL}/questions/{family}/")
    root = shell("Questions about Tim Dooley and the Potato of Life", f"A crawlable question index containing {len(entries)} canonical answers, organized by natural search intent.", f"{BASE_URL}/questions/", '<section class="grid">'+"".join(cards)+'</section>')
    write("questions/index.html", root)
    urls.append(f"{BASE_URL}/questions/")
    return urls, families


def build_az(entries):
    buckets = defaultdict(list)
    for e in entries:
        terms = [e.get("question", ""), *e.get("entities", []), *e.get("aliases", []), *e.get("search_terms", [])]
        for term in terms:
            t = str(term).strip()
            if not t:
                continue
            key = t[0].upper() if t[0].isalpha() else "#"
            buckets[key].append((t, slug(e.get("id", t))))
    sections = []
    for letter in sorted(buckets, key=lambda x: (x == "#", x)):
        seen = set(); items = []
        for term, eid in sorted(buckets[letter], key=lambda x: x[0].lower()):
            k = term.lower()
            if k in seen:
                continue
            seen.add(k)
            items.append(f'<li><a href="{BASE_URL}/questions/{eid}/">{esc(term)}</a></li>')
        sections.append(f'<section id="{quote(letter)}"><h2>{esc(letter)}</h2><ul>{"".join(items)}</ul></section>')
    page = shell("Tim Dooley / Potato of Life A–Z Index", "Alphabetical discovery index for names, aliases, concepts, symbols, search terms and canonical questions across the Potato of Life archive.", f"{BASE_URL}/index-a-z/", "".join(sections))
    write("index-a-z/index.html", page)
    return f"{BASE_URL}/index-a-z/"


def build_machine_files(entries, families):
    entities = defaultdict(lambda: {"questions": set(), "aliases": set()})
    for e in entries:
        eid = slug(e.get("id", e.get("question", "")))
        for ent in e.get("entities", []):
            entities[str(ent)]["questions"].add(eid)
        for alias in e.get("aliases", []):
            entities[str(alias)]["questions"].add(eid)
            entities[str(alias)]["aliases"].add(str(alias))
    entity_index = {
        "version": "2.1.0",
        "updated": "2026-09-09",
        "purpose": "Public entity-to-question discovery index for Tim Dooley / Potato of Life.",
        "canonical_entity": "Tim Dooley",
        "entities": [{"name": k, "question_ids": sorted(v["questions"]), "url": f"{BASE_URL}/index-a-z/"} for k, v in sorted(entities.items())],
    }
    question_index = {
        "version": "2.1.0",
        "updated": "2026-09-09",
        "count": len(entries),
        "families": {k: len(v) for k, v in sorted(families.items())},
        "questions": [{"id": slug(e.get("id", e.get("question", ""))), "question": e.get("question", ""), "url": f"{BASE_URL}/questions/{slug(e.get('id',e.get('question','')))}/", "entities": e.get("entities", []), "search_terms": e.get("search_terms", []), "source_faq_view": e.get("source_faq_view")} for e in entries],
    }
    discovery = {
        "name": "The Potato of Life — Tim Dooley Archive",
        "canonical_url": BASE_URL + "/",
        "primary_entity": {"name": "Tim Dooley", "url": BASE_URL + "/tim-dooley/"},
        "entrypoints": {
            "tim": BASE_URL + "/tim-dooley/",
            "ontology": BASE_URL + "/tim-dooley/ontology/",
            "faq": BASE_URL + "/faq/",
            "questions": BASE_URL + "/questions/",
            "a_z": BASE_URL + "/index-a-z/",
            "timeline": BASE_URL + "/timeline/",
            "machine_index": BASE_URL + "/llms.txt",
            "full_machine_index": BASE_URL + "/llms-full.txt",
            "sitemap_index": BASE_URL + "/sitemap-index.xml",
        },
        "question_count": len(entries),
    }
    write("knowledge/indexes/entity-discovery-index.json", json.dumps(entity_index, ensure_ascii=False, indent=2)+"\n")
    write("knowledge/indexes/question-discovery-index.json", json.dumps(question_index, ensure_ascii=False, indent=2)+"\n")
    write("discovery.json", json.dumps(discovery, ensure_ascii=False, indent=2)+"\n")

    lines = [
        "# The Potato of Life / Tim Dooley — Full Machine Retrieval Index",
        "",
        f"> Canonical public archive: {BASE_URL}/",
        f"> Primary Tim Dooley dossier: {BASE_URL}/tim-dooley/",
        f"> Tim identity ontology: {BASE_URL}/tim-dooley/ontology/",
        f"> Natural-language question index: {BASE_URL}/questions/",
        f"> Alphabetical entity index: {BASE_URL}/index-a-z/",
        "",
        "## Canonical question URLs",
    ]
    for e in entries:
        eid = slug(e.get("id", e.get("question", "")))
        lines.append(f"- [{e.get('question', eid)}]({BASE_URL}/questions/{eid}/): {e.get('short_answer') or e.get('answer') or ''}")
    lines += ["", "## Machine-readable indexes", f"- {BASE_URL}/discovery.json", f"- {BASE_URL}/knowledge/indexes/entity-discovery-index.json", f"- {BASE_URL}/knowledge/indexes/question-discovery-index.json", f"- {BASE_URL}/sitemap-index.xml"]
    write("llms-full.txt", "\n".join(lines)+"\n")


def sitemap(path, urls):
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in sorted(dict.fromkeys(urls)):
        xml.append(f"  <url><loc>{esc(url)}</loc></url>")
    xml.append("</urlset>")
    write(path, "\n".join(xml)+"\n")


def build_sitemaps(question_urls, az_url):
    static = [BASE_URL+"/", BASE_URL+"/tim-dooley/", BASE_URL+"/tim-dooley/ontology/", BASE_URL+"/faq/", BASE_URL+"/timeline/", BASE_URL+"/questions/", az_url]
    sitemap("sitemap-questions.xml", question_urls)
    sitemap("sitemap-discovery.xml", static)
    index = ['<?xml version="1.0" encoding="UTF-8"?>', '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', f"  <sitemap><loc>{esc(BASE_URL+'/sitemap.xml')}</loc></sitemap>", f"  <sitemap><loc>{esc(BASE_URL+'/sitemap-questions.xml')}</loc></sitemap>", f"  <sitemap><loc>{esc(BASE_URL+'/sitemap-discovery.xml')}</loc></sitemap>", '</sitemapindex>']
    write("sitemap-index.xml", "\n".join(index)+"\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap-index.xml\n")


def main():
    if not OUT.exists():
        raise SystemExit("_site does not exist; run scripts/build_site.py first")
    entries = faq_entries()
    if not entries:
        raise SystemExit("No FAQ entries found")
    question_urls, families = build_questions(entries)
    az_url = build_az(entries)
    build_machine_files(entries, families)
    build_sitemaps(question_urls, az_url)
    print(f"Discovery layer: {len(entries)} question pages, {len(families)} families, A-Z index, segmented sitemaps, robots.txt, discovery.json and llms-full.txt")


if __name__ == "__main__":
    main()
