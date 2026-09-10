#!/usr/bin/env python3
"""Compile knowledge/science into the single deployed /science/ page."""
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
SCIENCE_PAGE = OUT / "index.html"
MARKER = "<!-- SCIENCE_CATALOG_STATIC -->"

TEXT_KEYS = ("abstract", "summary", "purpose", "importance", "core_thesis", "description", "scope")
PROVENANCE_KEYS = ("provenance_classes", "epistemic_classes", "source_class", "origin_class", "provenance")
EQUATION_KEYS = (
    "equation", "formula", "lagrangian", "differential", "curvature", "action",
    "operator", "formalism", "formal_core", "metric", "mapping", "coupling", "symmetry_breaking",
    "rg_", "field_equation", "dynamics",
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
            "equations": [], "findings": [], "updated": "",
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
    }


def render_cards(records: list[dict], record_prefix: str) -> str:
    cards = []
    for rec in records:
        search_blob = " ".join([
            rec["title"], rec["file"], rec["status"], rec["abstract"],
            *rec["provenance"], *rec["equations"], *rec["findings"],
        ]).lower()
        prov = "".join(f'<span>{esc(x)}</span>' for x in rec["provenance"][:3])
        details_parts = []
        if rec["equations"]:
            eqs = "".join(f"<code>{esc(eq)}</code>" for eq in rec["equations"][:4])
            details_parts.append(f'<div class="catalog-equations"><b>Equation sample</b>{eqs}</div>')
        if rec["findings"]:
            items = "".join(f"<li>{esc(x)}</li>" for x in rec["findings"][:3])
            details_parts.append(f'<div class="catalog-findings"><b>Findings / conclusions</b><ul>{items}</ul></div>')
        details_html = ""
        if details_parts:
            details_html = '<details class="catalog-details"><summary>Equations & findings</summary>' + "".join(details_parts) + '</details>'
        status = f'<span class="catalog-status">{esc(rec["status"])}</span>' if rec["status"] else ""
        cards.append(
            '<article class="catalog-card" data-search="{search}">\n'
            '  <div class="catalog-meta"><span>{updated}</span>{status}</div>\n'
            '  <h3>{title}</h3>\n'
            '  <p>{abstract}</p>\n'
            '  <div class="catalog-provenance">{prov}</div>\n'
            '  {details_html}\n'
            '  <div class="catalog-links"><a href="{prefix}{file}">Open source JSON →</a></div>\n'
            '</article>'.format(
                search=esc(search_blob), updated=esc(rec["updated"] or "undated"), status=status,
                title=esc(rec["title"]), abstract=esc(rec["abstract"]), prov=prov,
                details_html=details_html, prefix=record_prefix, file=esc(rec["file"]),
            )
        )
    return "\n".join(cards)


def patch_science_page(cards: str, count: int) -> None:
    if not SCIENCE_PAGE.exists():
        raise SystemExit("_site/science/index.html missing")
    text = SCIENCE_PAGE.read_text(encoding="utf-8")
    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing from science/index.html")
    text = text.replace(MARKER, cards, 1)
    SCIENCE_PAGE.write_text(text, encoding="utf-8")


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
    patch_science_page(render_cards(records, "../knowledge/science/"), len(records))
    print(f"Built /science/ index: {len(records)} records")


if __name__ == "__main__":
    main()
