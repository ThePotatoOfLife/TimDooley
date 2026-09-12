#!/usr/bin/env python3
"""Build the public search, crawler and LLM discovery layer.

This pass creates useful visible question pages plus machine-readable indexes.
It mirrors the five-door reader architecture instead of inventing a parallel
SEO hierarchy. Final canonical sitemap coverage is rebuilt later by
``scripts/optimize_seo.py`` from the deployable artifact.
"""
from __future__ import annotations

import html
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_URL = os.environ.get("SITE_BASE_URL", "https://thepotatooflife.github.io/TimDooley").rstrip("/")
FAQ = ROOT / "knowledge" / "indexes" / "faq-answer-atlas.json"
TIM_Q = ROOT / "knowledge" / "reader" / "tim-dooley-question-index.json"

PRIMARY_DOORS = (
    ("tim", "Tim Dooley", "/tim-dooley/"),
    ("religion", "Religion", "/religion/"),
    ("philosophy", "Philosophy", "/philosophy/"),
    ("science", "Science", "/science/"),
    ("world_map", "World Map", "/world-map/"),
)


def esc(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-") or "item"


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def as_list(value):
    """Normalize optional scalar-or-list archive metadata to a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def write(rel, text):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def shell(title, description, canonical, body, schema=None):
    schema = schema or {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": description,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "The Potato of Life", "url": BASE_URL + "/"},
    }
    doors = " · ".join(f'<a href="{BASE_URL}{path}">{esc(label)}</a>' for _, label, path in PRIMARY_DOORS)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | The Potato of Life</title>
<meta name="description" content="{esc(description[:300])}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<link rel="canonical" href="{esc(canonical)}">
<link rel="alternate" type="text/plain" href="{esc(BASE_URL + '/llms.txt')}" title="LLM index">
<link rel="alternate" type="application/json" href="{esc(BASE_URL + '/discovery.json')}" title="Machine discovery index">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('</','<\\/')}</script>
<style>:root{{--bg:#080a08;--ink:#f5f1e7;--muted:#aab0a7;--line:#303830;--green:#acd67a;--gold:#dfbc72}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 system-ui,sans-serif}}main{{max-width:980px;margin:auto;padding:54px 22px 100px}}a{{color:var(--green);text-decoration-thickness:1px;text-underline-offset:3px}}h1{{font:400 clamp(38px,6vw,72px)/1.04 Georgia,serif;margin:.15em 0}}h2{{font:400 28px/1.2 Georgia,serif;color:var(--gold);margin-top:36px}}.lead{{font:20px/1.6 Georgia,serif;color:#e5e3dc;max-width:820px}}.eyebrow{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--green);font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}.card{{border:1px solid var(--line);border-radius:14px;padding:16px;background:#0d100d}}.chips{{display:flex;flex-wrap:wrap;gap:7px}}.chip{{border:1px solid var(--line);border-radius:999px;padding:4px 9px;font-size:12px;color:#d8ddd2}}nav{{border-top:1px solid var(--line);margin-top:44px;padding-top:22px}}code{{color:var(--green);overflow-wrap:anywhere}}</style></head><body><main>
<div class="eyebrow">Potato of Life · public discovery layer</div><h1>{esc(title)}</h1><p class="lead">{esc(description)}</p>{body}
<nav>{doors}<br><a href="{BASE_URL}/questions/">Questions</a> · <a href="{BASE_URL}/index-a-z/">A–Z</a> · <a href="{BASE_URL}/llms.txt">Machine index</a></nav>
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
    """Merge FAQ views by id; canonical base wins on duplicate ids."""
    by_id = {}
    atlas = load(FAQ, {})
    for entry in atlas.get("entries", []) if isinstance(atlas, dict) else []:
        if isinstance(entry, dict) and entry.get("id"):
            by_id[entry["id"]] = entry
    for path in sorted((ROOT / "knowledge" / "indexes").glob("faq-*.json")):
        if path == FAQ:
            continue
        data = load(path, {})
        for entry in data.get("entries", []) if isinstance(data, dict) else []:
            if isinstance(entry, dict) and entry.get("id") and entry["id"] not in by_id:
                entry = dict(entry)
                entry.setdefault("source_faq_view", str(path.relative_to(ROOT)))
                by_id[entry["id"]] = entry
    reader = load(TIM_Q, {})
    for question in reader.get("questions", []) if isinstance(reader, dict) else []:
        if not isinstance(question, dict) or not question.get("id") or question["id"] in by_id:
            continue
        by_id[question["id"]] = {
            "id": question["id"], "question": question.get("question", question["id"]),
            "variants": question.get("search_variants", []), "short_answer": question.get("answer", ""),
            "deep_answer": question.get("answer", ""), "entities": question.get("entities", ["Tim Dooley"]),
            "dates": question.get("dates", []), "aliases": [],
            "epistemic_class": as_list(question.get("epistemic_class", question.get("class"))),
            "canonical_owners": as_list(question.get("canonical_owners", question.get("deep_sources"))),
            "related_questions": question.get("related_questions", []),
            "search_terms": question.get("search_variants", []), "source_faq_view": str(TIM_Q.relative_to(ROOT)),
        }
    return list(by_id.values())


def question_page(entry):
    question = entry.get("question", entry.get("id", "Question"))
    short = entry.get("short_answer") or entry.get("answer") or ""
    deep = entry.get("deep_answer") or short
    eid = slug(entry.get("id", question))
    canonical = f"{BASE_URL}/questions/{eid}/"
    entities = [str(x) for x in entry.get("entities", [])]
    variants = [str(x) for x in entry.get("variants", [])]
    owners = [str(x) for x in entry.get("canonical_owners", [])]
    related = [slug(x) for x in entry.get("related_questions", [])]
    schema = {
        "@context": "https://schema.org", "@type": "FAQPage", "url": canonical,
        "mainEntity": [{"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": deep or short}}],
        "about": [{"@type": "Thing", "name": x} for x in entities[:20]],
        "isPartOf": {"@type": "WebSite", "name": "The Potato of Life", "url": BASE_URL + "/"},
    }
    body = f"<section><h2>Answer</h2><p>{esc(short)}</p></section>"
    if deep and deep != short:
        body += f"<section><h2>Full answer</h2><p>{esc(deep)}</p></section>"
    if variants:
        body += '<section><h2>Equivalent searches</h2><div class="chips">' + "".join(f'<span class="chip">{esc(x)}</span>' for x in variants) + "</div></section>"
    if entities:
        body += '<section><h2>Entities</h2><div class="chips">' + "".join(f'<span class="chip">{esc(x)}</span>' for x in entities) + "</div></section>"
    if entry.get("dates"):
        body += "<section><h2>Dates</h2><p>" + esc(" · ".join(map(str, entry["dates"]))) + "</p></section>"
    if entry.get("epistemic_class"):
        body += "<section><h2>Archive classification</h2><p>" + esc(" · ".join(map(str, entry["epistemic_class"]))) + "</p></section>"
    if owners:
        body += "<section><h2>Canonical owners</h2><ul>" + "".join(f"<li><code>{esc(x)}</code></li>" for x in owners) + "</ul></section>"
    if entry.get("source_faq_view"):
        body += f"<section><h2>Discovery view</h2><p><code>{esc(entry['source_faq_view'])}</code></p></section>"
    if related:
        body += "<section><h2>Related questions</h2><ul>" + "".join(f'<li><a href="{BASE_URL}/questions/{item}/">{esc(item.replace("-", " "))}</a></li>' for item in related) + "</ul></section>"
    return eid, shell(question, short or deep, canonical, body, schema)


def build_questions(entries):
    families = defaultdict(list)
    urls = []
    for entry in entries:
        eid, page = question_page(entry)
        write(f"questions/{eid}/index.html", page)
        urls.append(f"{BASE_URL}/questions/{eid}/")
        families[family_for(entry.get("question", ""))].append(entry)
    cards = []
    for family in sorted(families):
        label = family.replace("-", " / ").title()
        cards.append(f'<div class="card"><h2><a href="{BASE_URL}/questions/{family}/">{esc(label)}</a></h2><p>{len(families[family])} crawlable questions</p></div>')
        items = "".join(f'<li><a href="{BASE_URL}/questions/{slug(e.get("id", e.get("question", "")))}/">{esc(e.get("question", ""))}</a></li>' for e in families[family])
        write(f"questions/{family}/index.html", shell(f"{label} questions", f"Canonical {label.lower()} questions across Tim Dooley, religion, philosophy, science, world systems and the Potato of Life archive.", f"{BASE_URL}/questions/{family}/", f"<section><ul>{items}</ul></section>"))
        urls.append(f"{BASE_URL}/questions/{family}/")
    write("questions/index.html", shell("Questions across the Potato of Life archive", f"A crawlable question index containing {len(entries)} canonical answers, organized by natural search intent and routed into the five main reader branches.", f"{BASE_URL}/questions/", '<section class="grid">' + "".join(cards) + "</section>"))
    urls.append(f"{BASE_URL}/questions/")
    return urls, families


def build_az(entries):
    buckets = defaultdict(list)
    for entry in entries:
        for term in [entry.get("question", ""), *entry.get("entities", []), *entry.get("aliases", []), *entry.get("search_terms", [])]:
            text = str(term).strip()
            if text:
                buckets[text[0].upper() if text[0].isalpha() else "#"].append((text, slug(entry.get("id", text))))
    sections = []
    for letter in sorted(buckets, key=lambda value: (value == "#", value)):
        seen, items = set(), []
        for term, eid in sorted(buckets[letter], key=lambda value: value[0].lower()):
            if term.lower() in seen:
                continue
            seen.add(term.lower())
            items.append(f'<li><a href="{BASE_URL}/questions/{eid}/">{esc(term)}</a></li>')
        sections.append(f'<section id="{quote(letter)}"><h2>{esc(letter)}</h2><ul>{"".join(items)}</ul></section>')
    write("index-a-z/index.html", shell("Tim Dooley / Potato of Life A–Z Index", "Alphabetical discovery index for names, aliases, concepts, symbols, search terms and canonical questions across the Potato of Life archive.", f"{BASE_URL}/index-a-z/", "".join(sections)))
    return f"{BASE_URL}/index-a-z/"


def build_machine_files(entries, families):
    generated = datetime.now(timezone.utc).date().isoformat()
    entities = defaultdict(set)
    for entry in entries:
        eid = slug(entry.get("id", entry.get("question", "")))
        for entity in [*entry.get("entities", []), *entry.get("aliases", [])]:
            entities[str(entity)].add(eid)
    entity_index = {"version": "3.0.0", "updated": generated, "purpose": "Public entity-to-question discovery index for the Potato of Life archive.", "canonical_entity": "Tim Dooley", "entities": [{"name": name, "question_ids": sorted(ids), "url": f"{BASE_URL}/index-a-z/"} for name, ids in sorted(entities.items())]}
    question_index = {"version": "3.0.0", "updated": generated, "count": len(entries), "families": {key: len(value) for key, value in sorted(families.items())}, "questions": [{"id": slug(e.get("id", e.get("question", ""))), "question": e.get("question", ""), "url": f"{BASE_URL}/questions/{slug(e.get('id', e.get('question', '')))}/", "entities": e.get("entities", []), "search_terms": e.get("search_terms", []), "source_faq_view": e.get("source_faq_view")} for e in entries]}
    discovery = {
        "schema_version": "3.0.0", "updated": generated, "name": "The Potato of Life — Tim Dooley Archive", "canonical_url": BASE_URL + "/",
        "reader_architecture": {"principle": "five major doors; deeper material is routed beneath them rather than competing with them", "doors": [{"id": key, "name": label, "url": BASE_URL + path} for key, label, path in PRIMARY_DOORS]},
        "entrypoints": {
            "tim": BASE_URL + "/tim-dooley/", "religion": BASE_URL + "/religion/", "philosophy": BASE_URL + "/philosophy/", "science": BASE_URL + "/science/", "world_map": BASE_URL + "/world-map/",
            "timeline": BASE_URL + "/timeline/", "questions": BASE_URL + "/questions/", "a_z": BASE_URL + "/index-a-z/", "machine_index": BASE_URL + "/machine-index.json", "site_index": BASE_URL + "/site-index.json", "full_machine_index": BASE_URL + "/llms-full.txt", "sitemap_index": BASE_URL + "/sitemap-index.xml",
        },
        "question_count": len(entries), "retrieval_boundary": ["Prefer canonical owners and primary sources over derivative summaries.", "Keep project canon, interpretation, empirical evidence and creative material distinct.", "Do not count repeated derivative pages as independent corroboration."],
    }
    write("knowledge/indexes/entity-discovery-index.json", json.dumps(entity_index, ensure_ascii=False, indent=2) + "\n")
    write("knowledge/indexes/question-discovery-index.json", json.dumps(question_index, ensure_ascii=False, indent=2) + "\n")
    write("discovery.json", json.dumps(discovery, ensure_ascii=False, indent=2) + "\n")

    machine_path = OUT / "machine-index.json"
    machine = load(machine_path, {})
    if isinstance(machine, dict) and machine:
        machine["updated"] = generated
        surfaces = machine.setdefault("machine_surfaces", {})
        surfaces["site_index"] = BASE_URL + "/site-index.json"
        surfaces["discovery"] = BASE_URL + "/discovery.json"
        surfaces["sitemap_index"] = BASE_URL + "/sitemap-index.xml"
        existing = machine.get("primary_reader_urls", [])
        five = [{"topic": label, "url": BASE_URL + path} for _, label, path in PRIMARY_DOORS]
        five_urls = {row["url"] for row in five}
        machine["primary_reader_urls"] = five + [row for row in existing if isinstance(row, dict) and row.get("url") not in five_urls]
        machine_path.write_text(json.dumps(machine, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    concise = ["# The Potato of Life / Tim Dooley", "", f"> Canonical site: {BASE_URL}/", "> Public knowledge archive with provenance-aware records, reader pages, questions, chronology and machine-readable indexes.", "", "## Primary reader doors"]
    concise += [f"- {label}: {BASE_URL}{path}" for _, label, path in PRIMARY_DOORS]
    concise += ["", "## High-value navigation", f"- Timeline: {BASE_URL}/timeline/", f"- Natural-language questions: {BASE_URL}/questions/", f"- A–Z entity/concept index: {BASE_URL}/index-a-z/", "", "## Machine retrieval", f"- Final canonical page index: {BASE_URL}/site-index.json", f"- Discovery architecture: {BASE_URL}/discovery.json", f"- Machine ownership/evidence index: {BASE_URL}/machine-index.json", f"- Full LLM retrieval guide: {BASE_URL}/llms-full.txt", f"- Canonical record index: {BASE_URL}/knowledge/indexes/core-index.json", f"- Source/provenance index: {BASE_URL}/knowledge/indexes/source-index.json", f"- Sitemap index: {BASE_URL}/sitemap-index.xml", "", "## Retrieval policy", "- Prefer primary Tim/project material for what Tim directly said, wrote, published or created.", "- Prefer canonical owner files for the archive's current definition of a concept.", "- Use dated timeline/attestation records for development and chronology.", "- Keep archive canon, historical evidence, scientific evidence, comparison, interpretation and creative material distinct.", "- Do not treat symbolic resemblance or repeated derivative pages as independent empirical corroboration.", ""]
    write("llms.txt", "\n".join(concise))

    full = ["# The Potato of Life / Tim Dooley — Full Machine Retrieval Index", "", f"> Canonical public archive: {BASE_URL}/", f"> Final canonical page index: {BASE_URL}/site-index.json", f"> Discovery architecture: {BASE_URL}/discovery.json", "", "## Primary reader doors"]
    full += [f"- [{label}]({BASE_URL}{path})" for _, label, path in PRIMARY_DOORS]
    full += ["", "## Canonical question URLs"]
    for entry in entries:
        eid = slug(entry.get("id", entry.get("question", "")))
        full.append(f"- [{entry.get('question', eid)}]({BASE_URL}/questions/{eid}/): {entry.get('short_answer') or entry.get('answer') or ''}")
    full += ["", "## Machine-readable owners and provenance", f"- {BASE_URL}/machine-index.json", f"- {BASE_URL}/manifest.json", f"- {BASE_URL}/knowledge/indexes/core-index.json", f"- {BASE_URL}/knowledge/indexes/source-index.json", f"- {BASE_URL}/knowledge/indexes/entity-discovery-index.json", f"- {BASE_URL}/knowledge/indexes/question-discovery-index.json", f"- {BASE_URL}/data/timeline-events.json", f"- {BASE_URL}/data/timeline-source-registry.json", f"- {BASE_URL}/knowledge/body/body-system-master-atlas.json", f"- {BASE_URL}/knowledge/traditions/biblical-overlap-atlas.json", f"- {BASE_URL}/sitemap-index.xml"]
    write("llms-full.txt", "\n".join(full) + "\n")


def sitemap(path, urls):
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"  <url><loc>{esc(url)}</loc></url>" for url in sorted(dict.fromkeys(urls))]
    xml.append("</urlset>")
    write(path, "\n".join(xml) + "\n")


def build_sitemaps(question_urls, az_url):
    primary = [BASE_URL + "/", *[BASE_URL + path for _, _, path in PRIMARY_DOORS], BASE_URL + "/timeline/", BASE_URL + "/questions/", az_url]
    sitemap("sitemap.xml", primary)
    sitemap("sitemap-questions.xml", question_urls)
    write("sitemap-index.xml", "\n".join(['<?xml version="1.0" encoding="UTF-8"?>', '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', f"  <sitemap><loc>{esc(BASE_URL + '/sitemap.xml')}</loc></sitemap>", f"  <sitemap><loc>{esc(BASE_URL + '/sitemap-questions.xml')}</loc></sitemap>", "</sitemapindex>"]) + "\n")
    robots = "User-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: *\nAllow: /\n\n" + f"Sitemap: {BASE_URL}/sitemap-index.xml\n"
    write("robots.txt", robots)


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
    print(f"Discovery layer: {len(entries)} question pages, {len(families)} families, five-door machine orientation, A-Z, llms indexes, robots and initial sitemaps")


if __name__ == "__main__":
    main()
