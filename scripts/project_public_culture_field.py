#!/usr/bin/env python3
"""Render the canonical concrete Culture field into the built public Culture page."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "knowledge" / "culture" / "concrete-culture-field-atlas.json"
LEDGER_PATH = ROOT / "knowledge" / "culture" / "concrete-culture-source-ledger.json"
SITE_CULTURE = ROOT / "_site" / "context" / "culture" / "index.html"
ANCHOR = "<h2>Culture is multidimensional</h2>"
FIELD_MARKER = 'data-culture-field="concrete-culture-field"'


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Concrete Culture projection missing canonical file: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Concrete Culture projection invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Concrete Culture projection expected an object in {path.relative_to(ROOT)}")
    return value


def load_atlas() -> dict:
    return _load_json(ATLAS_PATH)


def load_sources() -> dict[str, dict]:
    ledger = _load_json(LEDGER_PATH)
    result: dict[str, dict] = {}
    for source in ledger.get("sources", []):
        if isinstance(source, dict) and isinstance(source.get("id"), str):
            result[source["id"]] = source
    if not result:
        raise SystemExit("Concrete Culture projection source ledger is empty")
    return result


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _source_links(source_refs: list[str], sources: dict[str, dict]) -> str:
    links: list[str] = []
    for ref in source_refs:
        source = sources.get(ref)
        if not source:
            continue
        title = _esc(source.get("title", ref))
        publisher = _esc(source.get("publisher", "source"))
        url = _esc(source.get("url", ""))
        if url:
            links.append(f'<a href="{url}" rel="noopener noreferrer">{title}</a> <span class="mini">({publisher})</span>')
    if not links:
        return ""
    return '<p class="mini"><strong>Sources:</strong> ' + " · ".join(links) + "</p>"


def _formation_card(record: dict, sources: dict[str, dict]) -> str:
    types = ", ".join(record.get("formation_types", []))
    status = record.get("status", "")
    return (
        '<article class="card">'
        f'<strong>{_esc(record.get("name", record.get("id", "Formation")))}</strong>'
        f'<p class="mini">{_esc(types)}' + (f' · {_esc(status)}' if status else '') + '</p>'
        f'<p>{_esc(record.get("description", ""))}</p>'
        + _source_links(record.get("source_refs", []), sources)
        + '</article>'
    )


def _flow_card(record: dict, sources: dict[str, dict]) -> str:
    amount = ""
    if "amount" in record:
        amount = f' · {_esc(record.get("currency", ""))} {_esc(record.get("amount"))}'
    return (
        '<article class="card">'
        f'<strong>{_esc(record.get("from", "?"))} → {_esc(record.get("to", "?"))}</strong>'
        f'<p class="mini">{_esc(record.get("flow_type", "flow"))} · {_esc(record.get("period", ""))}{amount}</p>'
        f'<p>{_esc(record.get("description", ""))}</p>'
        + _source_links(record.get("source_refs", []), sources)
        + '</article>'
    )


def _relationship_card(record: dict, sources: dict[str, dict]) -> str:
    return (
        '<article class="card">'
        f'<strong>{_esc(record.get("from", "?"))} → {_esc(record.get("relationship", "relation"))} → {_esc(record.get("to", "?"))}</strong>'
        f'<p class="mini">{_esc(record.get("period", ""))} · {_esc(record.get("evidence_status", ""))}</p>'
        f'<p>{_esc(record.get("description", ""))}</p>'
        + _source_links(record.get("source_refs", []), sources)
        + '</article>'
    )


def _pathway_card(record: dict, sources: dict[str, dict]) -> str:
    steps = " → ".join(_esc(step) for step in record.get("steps", []))
    return (
        '<article class="card">'
        f'<strong>{_esc(record.get("name", record.get("id", "Pathway")))}</strong>'
        f'<div class="chain">{steps}</div>'
        f'<p>{_esc(record.get("description", ""))}</p>'
        + _source_links(record.get("source_refs", []), sources)
        + '</article>'
    )


def render_concrete_culture_field(atlas: dict, sources: dict[str, dict]) -> str:
    formations = atlas.get("formations", []) if isinstance(atlas, dict) else []
    human_cases = atlas.get("human_cases", []) if isinstance(atlas, dict) else []
    flows = atlas.get("flows", []) if isinstance(atlas, dict) else []
    relationships = atlas.get("relationships", []) if isinstance(atlas, dict) else []
    pathways = atlas.get("pathways", []) if isinstance(atlas, dict) else []
    projection = atlas.get("public_projection", {}) if isinstance(atlas, dict) else {}

    by_id = {item.get("id"): item for item in formations if isinstance(item, dict)}
    featured_ids = [
        "loyal-to-familia",
        "otf-grimm-violence-as-a-service",
        "nxivm",
        "kiwi-farms",
        "online-snark-communities",
        "hip-hop",
        "medecins-sans-frontieres",
        "icrc",
    ]
    featured = [by_id[item_id] for item_id in featured_ids if item_id in by_id]

    violence_relationships = [
        item for item in relationships
        if isinstance(item, dict) and item.get("relationship") == "IN_CONFLICT_WITH"
    ]
    money_flows = [
        item for item in flows
        if isinstance(item, dict) and item.get("flow_type") in {"money", "grant", "donation", "membership_fee", "commercial_revenue", "illicit_proceeds"}
    ]
    other_flows = [
        item for item in flows
        if isinstance(item, dict) and item not in money_flows
    ]

    human_html = ""
    for case in human_cases:
        if not isinstance(case, dict):
            continue
        path = " → ".join(_esc(step) for step in case.get("network_path", []))
        human_html += (
            '<article class="card">'
            f'<strong>{_esc(case.get("display_name", case.get("id", "Human case")))}</strong>'
            f'<p>{_esc(case.get("summary", ""))}</p>'
            f'<div class="chain">{path}</div>'
            f'<p>{_esc(case.get("reply_or_reclamation", ""))}</p>'
            f'<p class="mini"><strong>Privacy rule:</strong> {_esc(case.get("privacy_notes", ""))}</p>'
            + _source_links(case.get("source_refs", []), sources)
            + '</article>'
        )

    pathway_html = "".join(_pathway_card(item, sources) for item in pathways if isinstance(item, dict))
    featured_html = "".join(_formation_card(item, sources) for item in featured)
    violence_html = "".join(_relationship_card(item, sources) for item in violence_relationships)
    flow_html = "".join(_flow_card(item, sources) for item in money_flows + other_flows)

    intro = _esc(projection.get("intro", "These examples are contrastive rather than equivalent."))
    legal_notice = _esc(projection.get("legal_notice", "Named conflict edges and aggregate statistics must remain separate."))
    source_notice = _esc(projection.get("source_notice", "Claims are sourced through the canonical ledger."))

    return (
        f'<section {FIELD_MARKER}>'
        '<h2>Who is actually here?</h2>'
        f'<p>{intro}</p>'
        f'<p class="mini"><strong>Evidence rule:</strong> {source_notice}</p>'
        f'<div class="cards">{featured_html}</div>'
        '<h2>Where violence actually appears</h2>'
        f'<p>{legal_notice}</p>'
        f'<div class="cards">{violence_html}</div>'
        '<h2>Follow the flows</h2>'
        '<p>Culture becomes more concrete when the model records what actually moves: money, attention, recruitment, information, tasks and people.</p>'
        f'<div class="cards">{flow_html}</div>'
        '<h2>People behind the labels</h2>'
        '<p>A public label can become more durable than the event that created it. Human cases restore sequence, authorship and later reply without rebuilding a hostile dossier.</p>'
        f'<div class="cards">{human_html}</div>'
        '<h2>How a formation changes type</h2>'
        '<p>These pathways are not a moral ladder. They show changes in reach, structure, infrastructure and institutional treatment.</p>'
        f'<div class="cards">{pathway_html}</div>'
        '<h2>Concrete Tree of Strife</h2>'
        '<p>The concrete field treats conflict as a graph of dated relations, events and flows rather than a single all-explaining category. A conflict edge can coexist with uncertainty, legal process, platform action, cultural mainstreaming, humanitarian funding and human reclamation elsewhere in the same field.</p>'
        '</section>'
    )


def inject_concrete_culture_field(page_html: str, rendered: str) -> str:
    if FIELD_MARKER in page_html:
        return page_html
    if ANCHOR not in page_html:
        raise SystemExit("Concrete Culture projection anchor missing from built Culture page")
    return page_html.replace(ANCHOR, rendered + ANCHOR, 1)


def project_culture_field() -> None:
    if not SITE_CULTURE.exists():
        raise SystemExit("Concrete Culture projection target missing: _site/context/culture/index.html")
    atlas = load_atlas()
    sources = load_sources()
    page = SITE_CULTURE.read_text(encoding="utf-8", errors="replace")
    rendered = render_concrete_culture_field(atlas, sources)
    updated = inject_concrete_culture_field(page, rendered)
    if updated != page:
        SITE_CULTURE.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    project_culture_field()
    print("Projected concrete Culture field into public reader.")
