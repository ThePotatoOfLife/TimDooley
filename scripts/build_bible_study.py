#!/usr/bin/env python3
"""Compile a compact no-JS Bible comparison index into the deployed page."""
from __future__ import annotations

import copy
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_PAGE = ROOT / "_site" / "traditions" / "bible" / "index.html"
FIELD_PATH = ROOT / "knowledge" / "traditions" / "biblical-syncretism-field.json"
DOSSIERS_PATH = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers.json"
FRAGMENTS_PATH = ROOT / "knowledge" / "traditions" / "biblical-passage-fragments.json"
DOSSIER_FRAGMENTS_PATH = ROOT / "knowledge" / "traditions" / "biblical-passage-fragments-dossiers.json"
MARKER = "<!-- BIBLE_RELATIONS_STATIC -->"
# The generated disclosures are inserted into the page container with class="static-index".


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def arr(value: object) -> list:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def merged_rows(field: dict, dossiers: dict) -> list[dict]:
    rows = [copy.deepcopy(row) for row in field.get("relations", [])]
    by_id = {row.get("id"): row for row in rows if row.get("id")}
    for enrichment in dossiers.get("enrichments", []):
        target = by_id.get(enrichment.get("relation_id"))
        if not target:
            continue
        for key, value in enrichment.items():
            if key != "relation_id":
                target[key] = copy.deepcopy(value)
    for row in dossiers.get("new_relations", []):
        if row.get("id") in by_id:
            continue
        item = copy.deepcopy(row)
        rows.append(item)
        by_id[item.get("id")] = item
    return rows


def fragment_index(*datasets: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    seen_ids: set[str] = set()
    for data in datasets:
        for fragment in data.get("fragments", []):
            fid = str(fragment.get("id") or "")
            if fid and fid in seen_ids:
                continue
            if fid:
                seen_ids.add(fid)
            keys = set(arr(fragment.get("matches")))
            if fragment.get("reference"):
                keys.add(fragment["reference"])
            for key in keys:
                out.setdefault(str(key), []).append(fragment)
    return out


def render(row: dict, fragments: dict[str, list[dict]]) -> str:
    refs = [str(x) for x in arr(row.get("biblical_refs")) if x]
    matched: list[dict] = []
    seen: set[str] = set()
    for ref in refs:
        for fragment in fragments.get(ref, []):
            key = str(fragment.get("id") or fragment.get("reference") or fragment.get("text"))
            if key not in seen:
                seen.add(key)
                matched.append(fragment)

    title = row.get("title") or row.get("project_anchor") or (refs[0] if refs else row.get("id"))
    meta = " · ".join(
        str(x)
        for x in (row.get("date"), row.get("actor"), f"strength {row.get('strength')}/5" if row.get("strength") is not None else None)
        if x
    )
    scope = " · ".join(refs) or "broader biblical tradition"
    scripture = "".join(
        f'<blockquote class="bible-quote">{esc(fragment.get("text"))}<cite>{esc(fragment.get("reference"))} · {esc(fragment.get("translation") or "World English Bible")}</cite></blockquote>'
        for fragment in matched[:2]
    ) or f'<p><strong>Scripture scope:</strong> {esc(scope)}</p>'
    mismatch = row.get("mismatch") or row.get("counter_text") or row.get("source_correction") or (arr(row.get("weaknesses"))[0] if arr(row.get("weaknesses")) else None)
    direction = row.get("source_direction") or (row.get("discovery_history") or {}).get("source_direction")
    scene = row.get("scene_context") or {}
    argument = row.get("relation_argument") or {}
    boundary = f'<p><strong>Where it breaks:</strong> {esc(mismatch)}</p>' if mismatch else ""
    direction_html = f'<p><strong>Source direction:</strong> {esc(direction)}</p>' if direction else ""
    scene_html = f'<p><strong>What was happening:</strong> {esc(scene.get("summary"))}</p>' if scene.get("summary") else ""
    why_html = f'<p><strong>Why these connect:</strong> {esc(argument.get("why_dense"))}</p>' if argument.get("why_dense") else ""
    max_html = f'<p><strong>Maximum defensible claim:</strong> {esc(argument.get("maximum_claim"))}</p>' if argument.get("maximum_claim") else ""

    return f'''<details class="static-relation" data-static-relation="{esc(row.get('id'))}">
<summary><strong>{esc(title)}</strong> <span>{esc(meta)}</span></summary>
<div class="static-relation-body">
{scene_html}
<p><strong>Project anchor:</strong> {esc(row.get('project_anchor'))}</p>
<p><strong>Scripture scope:</strong> {esc(scope)}</p>
{scripture}
{why_html}
{boundary}
{max_html}
{direction_html}
</div>
</details>'''


def main() -> int:
    if not SITE_PAGE.exists():
        raise SystemExit("Run scripts/build_site.py before build_bible_study.py")
    field = load(FIELD_PATH)
    dossiers = load(DOSSIERS_PATH)
    fragment_data = load(FRAGMENTS_PATH)
    dossier_fragment_data = load(DOSSIER_FRAGMENTS_PATH)
    rows = merged_rows(field, dossiers)
    if not rows:
        raise SystemExit("Canonical Bible relation field is empty")
    fragments = fragment_index(fragment_data, dossier_fragment_data)
    source = SITE_PAGE.read_text(encoding="utf-8")
    if source.count(MARKER) != 1:
        raise SystemExit(f"Expected exactly one {MARKER}")
    source = source.replace(MARKER, "\n".join(render(row, fragments) for row in rows))
    SITE_PAGE.write_text(source, encoding="utf-8")
    print(f"Bible comparator compact fallback compiled: {len(rows)} merged canonical relations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
