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
GROUNDING_MARKER_PREFIX = 'data-culture-grounding="'


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


def _mechanism_card(record: dict, fields: tuple[tuple[str, str], ...], sources: dict[str, dict]) -> str:
    body = [
        '<article class="card">',
        f'<strong>{_esc(record.get("name", record.get("id", "Formation")))}</strong>',
        f'<p>{_esc(record.get("description", ""))}</p>',
    ]
    for field, label in fields:
        value = record.get(field)
        if not value:
            continue
        if isinstance(value, list):
            value = " · ".join(str(item) for item in value)
        body.append(f'<p><strong>{_esc(label)}:</strong> {_esc(value)}</p>')
    body.append(_source_links(record.get("source_refs", []), sources))
    body.append('</article>')
    return "".join(body)


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


def _find_record(atlas: dict, object_type: str, object_id: str) -> dict:
    collection_map = {
        "formation": "formations",
        "human_case": "human_cases",
        "event": "events",
        "flow": "flows",
        "relationship": "relationships",
        "pathway": "pathways",
    }
    collection = collection_map.get(object_type)
    if not collection:
        return {}
    for record in atlas.get(collection, []):
        if isinstance(record, dict) and record.get("id") == object_id:
            return record
    return {}


def _grounding_card(card: dict, atlas: dict, sources: dict[str, dict]) -> str:
    record = _find_record(atlas, card.get("object_type", ""), card.get("object_id", ""))
    if not record:
        return ""
    label = card.get("label") or record.get("name") or record.get("display_name") or record.get("id")
    body = [
        '<article class="card culture-grounding-card">',
        f'<strong>{_esc(label)}</strong>',
        f'<p>{_esc(card.get("point", ""))}</p>',
    ]
    fields = card.get("fields", [])
    if isinstance(fields, list):
        for field in fields:
            value = record.get(field)
            if not value:
                continue
            if isinstance(value, dict):
                value = " · ".join(f"{key}: {val}" for key, val in value.items())
            elif isinstance(value, list):
                value = " · ".join(str(item) for item in value)
            field_label = str(field).replace("_", " ").title()
            body.append(f'<p class="mini"><strong>{_esc(field_label)}:</strong> {_esc(value)}</p>')
    if card.get("object_type") == "human_case":
        path = record.get("network_path", [])
        if isinstance(path, list) and path:
            body.append('<div class="chain">' + " → ".join(_esc(step) for step in path) + '</div>')
    elif card.get("object_type") == "pathway":
        steps = record.get("steps", [])
        if isinstance(steps, list) and steps:
            body.append('<div class="chain">' + " → ".join(_esc(step) for step in steps) + '</div>')
    body.append(_source_links(record.get("source_refs", []), sources))
    body.append('</article>')
    return "".join(body)


def render_topic_grounding(grounding: dict, atlas: dict, sources: dict[str, dict]) -> str:
    gid = grounding.get("id", "topic")
    cards = "".join(
        _grounding_card(card, atlas, sources)
        for card in grounding.get("cards", [])
        if isinstance(card, dict)
    )
    return (
        f'<section data-culture-grounding="{_esc(gid)}" class="culture-grounding">'
        f'<h2>{_esc(grounding.get("title", "Concrete cases"))}</h2>'
        f'<p>{_esc(grounding.get("summary", ""))}</p>'
        f'<div class="cards">{cards}</div>'
        '</section>'
    )


def inject_topic_groundings(page_html: str, atlas: dict, sources: dict[str, dict]) -> str:
    updated = page_html
    for grounding in atlas.get("topic_groundings", []):
        if not isinstance(grounding, dict):
            continue
        gid = grounding.get("id")
        anchor_title = grounding.get("anchor_before")
        if not gid or not anchor_title:
            continue
        marker = f'data-culture-grounding="{gid}"'
        if marker in updated:
            continue
        anchor = f"<h2>{anchor_title}</h2>"
        if anchor not in updated:
            raise SystemExit(f"Culture grounding anchor missing: {anchor_title}")
        rendered = render_topic_grounding(grounding, atlas, sources)
        updated = updated.replace(anchor, rendered + anchor, 1)
    return updated


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
        "organization-for-transformative-works-ao3",
        "burning-man",
        "skateboarding",
        "wikipedia",
        "mastodon-activitypub",
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
    other_flows = [item for item in flows if isinstance(item, dict) and item not in money_flows]

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

    infrastructure_ids = ("organization-for-transformative-works-ao3", "wikipedia", "mastodon-activitypub")
    infrastructure_html = "".join(
        _mechanism_card(by_id[item_id], (("governance_model", "Governance"), ("infrastructure_model", "Infrastructure"), ("exit_or_portability", "Exit / portability")), sources)
        for item_id in infrastructure_ids if item_id in by_id
    )
    correction_ids = ("wikipedia", "organization-for-transformative-works-ao3", "burning-man")
    correction_html = "".join(
        _mechanism_card(by_id[item_id], (("correction_mechanisms", "Correction / accountability"), ("governance_model", "Governance")), sources)
        for item_id in correction_ids if item_id in by_id
    )
    ritual_html = ""
    if "burning-man" in by_id:
        ritual_html = _mechanism_card(
            by_id["burning-man"],
            (("stated_purpose_or_beliefs", "Shared principles"), ("governance_model", "Institutional layer"), ("correction_mechanisms", "Accountability")),
            sources,
        )
    institution_ids = ("skateboarding", "organization-for-transformative-works-ao3", "hip-hop")
    institution_html = "".join(
        _mechanism_card(by_id[item_id], (("commercialization_tensions", "Commercialization tension"), ("governance_model", "Governance / institution"), ("infrastructure_model", "Infrastructure")), sources)
        for item_id in institution_ids if item_id in by_id
    )

    intro = _esc(projection.get("intro", "These examples are contrastive rather than equivalent."))
    legal_notice = _esc(projection.get("legal_notice", "Named conflict edges and aggregate statistics must remain separate."))
    source_notice = _esc(projection.get("source_notice", "Claims are sourced through the canonical ledger."))
    expansion_notice = _esc(projection.get("expansion_notice", "The added roads examine governance and cultural reproduction."))

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
        '<p>Culture becomes more concrete when the model records what actually moves: money, attention, recruitment, information, tasks, people and archive material.</p>'
        f'<div class="cards">{flow_html}</div>'
        '<h2>People behind the labels</h2>'
        '<p>A public label can become more durable than the event that created it. Human cases restore sequence, authorship and later reply without rebuilding a hostile dossier.</p>'
        f'<div class="cards">{human_html}</div>'
        '<h2>How a formation changes type</h2>'
        '<p>These pathways are not a moral ladder. They show changes in reach, structure, infrastructure and institutional treatment.</p>'
        f'<div class="cards">{pathway_html}</div>'
        '<h2>Who owns the infrastructure?</h2>'
        f'<p>{expansion_notice} Infrastructure decides who stores memory, who can change rules, whether one operator is a single point of dependency, and whether a community can reproduce itself outside a commercial host.</p>'
        f'<div class="cards">{infrastructure_html}</div>'
        '<h2>How correction works</h2>'
        '<p>Correction capacity is a cultural property. The useful questions are whether disagreement is visible, whether rules can be revised, whether outsiders can inspect decisions, and whether a mistaken claim can lose authority without the whole community collapsing.</p>'
        f'<div class="cards">{correction_html}</div>'
        '<h2>Ritual without captivity</h2>'
        '<p>Strong ritual, symbolism, shared vocabulary and intense participation do not by themselves establish high control. The control axis remains separate: look for concentrated authority, surveillance, dependency, punishment of dissent and costly exit rather than intensity alone.</p>'
        f'<div class="cards">{ritual_html}</div>'
        '<h2>When underground becomes institution</h2>'
        '<p>Mainstreaming creates trade-offs rather than a simple victory. A scene can gain money, preservation, professional roles and public legitimacy while arguing internally about authenticity, ownership, commercialization and who gets to define the culture.</p>'
        f'<div class="cards">{institution_html}</div>'
        '<h2>Concrete Tree of Strife</h2>'
        '<p>The concrete field treats conflict as a graph of dated relations, events and flows rather than a single all-explaining category. A conflict edge can coexist with uncertainty, legal process, platform action, cultural mainstreaming, humanitarian funding, community-owned infrastructure, correction systems and human reclamation elsewhere in the same field.</p>'
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
    updated = inject_topic_groundings(page, atlas, sources)
    updated = inject_concrete_culture_field(updated, rendered)
    if updated != page:
        SITE_CULTURE.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    project_culture_field()
    print("Projected concrete Culture field into public reader.")
