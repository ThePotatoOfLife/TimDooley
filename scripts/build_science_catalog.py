#!/usr/bin/env python3
"""Compile knowledge/science into the deployed public science record layer."""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "knowledge" / "science"
OUT = ROOT / "_site" / "science"
CATALOG_JSON = OUT / "catalog.json"
CATALOG_PAGE = OUT / "catalog" / "index.html"
SCIENCE_PAGE = OUT / "index.html"
MARKER = "<!-- SCIENCE_CATALOG_STATIC -->"

TEXT_KEYS = ("abstract", "summary", "purpose", "importance", "core_thesis", "description", "scope")
PROVENANCE_KEYS = ("provenance_classes", "epistemic_classes", "source_class", "origin_class", "provenance")
EQUATION_KEYS = (
    "equation", "formula", "lagrangian", "differential", "curvature", "action",
    "operator", "formalism", "formal_core", "metric", "mapping", "coupling",
    "symmetry_breaking", "rg_", "field_equation", "dynamics",
)
FINDING_KEYS = ("conclusion", "finding", "result", "implication", "interpretation", "lesson", "takeaway")
MATH_HINT = re.compile(r"(=|→|↔|∂|∇|Σ|∫|√|ℒ|□|μ|ν|θ|φ|ψ|alpha|beta|gamma|SU\(|SO\(|Spin\(|U\(1\)|d[A-Za-z_].*/d)")


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def first_text(data: dict) -> str:
    for key in TEXT_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())
    return ""


def flatten_strings(value, limit=24):
    out = []
    if isinstance(value, str):
        if value.strip():
            out.append(" ".join(value.split()))
    elif isinstance(value, (list, tuple)):
        for item in value:
            if len(out) >= limit:
                break
            out.extend(flatten_strings(item, limit - len(out)))
    elif isinstance(value, dict):
        for item in value.values():
            if len(out) >= limit:
                break
            out.extend(flatten_strings(item, limit - len(out)))
    return out[:limit]


def get_provenance(data: dict) -> list[str]:
    values = []
    for key in PROVENANCE_KEYS:
        if key in data:
            values.extend(flatten_strings(data[key], 12))
    return list(dict.fromkeys(values))[:12]


def walk_candidates(obj, equations=None, findings=None):
    equations = equations if equations is not None else []
    findings = findings if findings is not None else []
    if isinstance(obj, dict):
        for key, value in obj.items():
            low = key.lower()
            if any(token in low for token in EQUATION_KEYS):
                for text in flatten_strings(value, 18):
                    if MATH_HINT.search(text) and text not in equations:
                        equations.append(text)
            if any(token in low for token in FINDING_KEYS):
                for text in flatten_strings(value, 12):
                    if len(text) >= 18 and text not in findings:
                        findings.append(text)
            walk_candidates(value, equations, findings)
    elif isinstance(obj, list):
        for value in obj:
            walk_candidates(value, equations, findings)
    return equations[:18], findings[:10]


def record_from(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "file": path.name, "id": path.stem,
            "title": path.stem.replace("-", " ").title(), "status": "parse error",
            "abstract": f"Could not parse record: {exc}", "provenance": [],
            "equations": [], "findings": [], "updated": "", "human_readable": "",
        }
    equations, findings = walk_candidates(data)
    title = data.get("title") or data.get("name") or data.get("id") or path.stem
    return {
        "file": path.name,
        "id": data.get("id") or path.stem,
        "title": title,
        "updated": data.get("updated") or data.get("date") or "",
        "status": data.get("status") or "",
        "abstract": first_text(data) or f"Canonical science record for {title}.",
        "provenance": get_provenance(data),
        "equations": equations,
        "findings": findings,
        "human_readable": data.get("human_readable") or "",
    }


def render_cards(records: list[dict], record_prefix: str) -> str:
    cards = []
    for rec in records:
        search_blob = " ".join([
            rec["title"], rec["file"], rec["status"], rec["abstract"],
            *rec["provenance"], *rec["equations"], *rec["findings"],
        ]).lower()
        prov = "".join(f'<span>{esc(x)}</span>' for x in rec["provenance"][:3])
        details = []
        if rec["equations"]:
            eqs = "".join(f"<code>{esc(eq)}</code>" for eq in rec["equations"][:3])
            details.append(f'<div class="catalog-equations"><b>Equation sample</b>{eqs}</div>')
        if rec["findings"]:
            items = "".join(f"<li>{esc(x)}</li>" for x in rec["findings"][:2])
            details.append(f'<div class="catalog-findings"><b>Findings / conclusions</b><ul>{items}</ul></div>')
        detail_html = ""
        if details:
            detail_html = '<details class="catalog-details"><summary>Technical detail</summary>' + "".join(details) + '</details>'
        status = f'<span class="catalog-status">{esc(rec["status"])}</span>' if rec["status"] else ""
        cards.append(
            '<article class="catalog-card" data-search="{search}">\n'
            '  <div class="catalog-meta"><span>{updated}</span>{status}</div>\n'
            '  <h3>{title}</h3>\n'
            '  <p>{abstract}</p>\n'
            '  <div class="catalog-provenance">{prov}</div>\n'
            '  {detail_html}\n'
            '  <div class="catalog-links"><a href="{prefix}{file}">Open source record →</a></div>\n'
            '</article>'.format(
                search=esc(search_blob), updated=esc(rec["updated"] or "undated"), status=status,
                title=esc(rec["title"]), abstract=esc(rec["abstract"]), prov=prov,
                detail_html=detail_html, prefix=record_prefix, file=esc(rec["file"]),
            )
        )
    return "\n".join(cards)


def render_catalog_page(records: list[dict]) -> str:
    cards = render_cards(records, "../../knowledge/science/")
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Science Source Records — Tim Dooley</title>'
        '<meta name="description" content="Generated source-record view for the canonical Tim Dooley / Potato of Life science data.">'
        '<link rel="canonical" href="https://thepotatooflife.github.io/TimDooley/science/catalog/">'
        '<link rel="stylesheet" href="../../app/style.css">'
        '</head><body><main class="science-page"><nav class="topnav"><a href="../">← Science</a><a href="../../">Home</a></nav>'
        '<header class="section-block"><p class="section-kicker">Generated source layer</p><h1>SCIENCE RECORDS</h1>'
        f'<p class="hero-lede">{len(records)} canonical science records. The JSON records remain the source of truth.</p></header>'
        f'<section class="section-block"><div class="catalog-grid">{cards}</div></section></main></body></html>'
    )


def patch_science_page(cards: str, count: int) -> None:
    if not SCIENCE_PAGE.exists():
        raise SystemExit("_site/science/index.html missing")
    text = SCIENCE_PAGE.read_text(encoding="utf-8")
    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing from science/index.html")
    text = text.replace(MARKER, cards, 1)
    text = text.replace('data-science-record-count="0"', f'data-science-record-count="{count}"')
    text = re.sub(r'(<strong id="metric-records">)\d+(</strong>)', rf'\g<1>{count}\g<2>', text, count=1)
    SCIENCE_PAGE.write_text(text, encoding="utf-8")


def patch_legacy_readers() -> None:
    replacements = {
        OUT / "research-map" / "index.html": [
            ('the exact Spiral formula remains unrecovered.', 'the exact Spiral formula is now recovered: r=a exp(bθ), with b=ln(φ)/(π/2)≈0.30635; a quarter-turn scales radius by φ.'),
            ('<li>Exact April 21, 2025 Spiral Equation.</li>', '<li>Earliest primary variable meanings for a, r and θ in the recovered April 21, 2025 Spiral Equation.</li>'),
        ],
        OUT / "axis-11d-sun-spiral" / "index.html": [
            ('This is a genuine Sun + rotation + outward-flow + Spiral system. It is an external physics neighbor, not the missing April 2025 Spiral Equation.', 'This is a genuine Sun + rotation + outward-flow + Spiral system. It is an external physics neighbor to the recovered April 2025 Potato Axis logarithmic spiral, not the same physical model.'),
            ('<li>Exact April 21, 2025 Spiral Equation.</li>', '<li>Earliest primary variable meanings for a, r and θ in the recovered April 21, 2025 Spiral Equation.</li>'),
        ],
    }
    for path, pairs in replacements.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for old, new in pairs:
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = [record_from(path) for path in sorted(SRC.glob("*.json"))]
    payload = {
        "generated": date.today().isoformat(),
        "source_directory": "knowledge/science/",
        "count": len(records),
        "records": records,
    }
    CATALOG_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CATALOG_PAGE.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PAGE.write_text(render_catalog_page(records), encoding="utf-8")
    patch_science_page(render_cards(records, "../knowledge/science/"), len(records))
    patch_legacy_readers()
    print(f"Built science source layer: {len(records)} records")


if __name__ == "__main__":
    main()
