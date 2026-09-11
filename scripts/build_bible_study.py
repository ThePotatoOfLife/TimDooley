#!/usr/bin/env python3
"""Compile the canonical Tim/Scripture relation field into the built Bible page.

The JSON relation field remains the source of truth. This script creates a
reader-visible static baseline in _site so the Bible study is useful even when
JavaScript or a secondary fetch fails. app/bible-study.js progressively enhances
this same material with search, filtering, roll and richer evidence context.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_PAGE = ROOT / "_site" / "traditions" / "bible" / "index.html"
FIELD_PATH = ROOT / "knowledge" / "traditions" / "biblical-syncretism-field.json"
FRAGMENTS_PATH = ROOT / "knowledge" / "traditions" / "biblical-passage-fragments.json"
MARKER = "<!-- BIBLE_RELATIONS_STATIC -->"


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


def fragment_index(fragment_data: dict) -> dict[str, list[dict]]:
    index: dict[str, list[dict]] = {}
    for fragment in fragment_data.get("fragments", []):
        keys = set(arr(fragment.get("matches"))) | {fragment.get("reference")}
        for key in filter(None, keys):
            index.setdefault(str(key), []).append(fragment)
    return index


def render_relation(row: dict, fragments: dict[str, list[dict]], class_labels: dict[str, str], discovery_labels: dict[str, str]) -> str:
    refs = [str(ref) for ref in arr(row.get("biblical_refs")) if ref]
    seen: set[str] = set()
    matched: list[dict] = []
    for ref in refs:
        for fragment in fragments.get(ref, []):
            key = str(fragment.get("id") or fragment.get("reference"))
            if key not in seen:
                seen.add(key)
                matched.append(fragment)

    relation_class = str(row.get("relation_class") or "unclassified")
    discovery_mode = str(row.get("discovery_mode") or "")
    prophecy_status = str(row.get("prophecy_status") or "")
    relation_explanation = class_labels.get(relation_class, relation_class.replace("-", " "))

    chips = [
        row.get("date"),
        row.get("actor"),
        discovery_labels.get(discovery_mode, discovery_mode.replace("-", " ")) if discovery_mode else None,
        relation_class.replace("-", " "),
    ]
    chip_html = "".join(f'<span class="chip">{esc(value)}</span>' for value in chips if value)
    if row.get("strength") is not None:
        chip_html += f'<span class="chip strength">strength {esc(row.get("strength"))}/5</span>'
    if prophecy_status:
        chip_html += f'<span class="chip exact">prophecy: {esc(prophecy_status.replace("-", " "))}</span>'

    scripture = "".join(
        f'<blockquote class="bible-quote">{esc(fragment.get("text"))}'
        f'<cite>{esc(fragment.get("reference"))} · World English Bible</cite></blockquote>'
        for fragment in matched[:4]
    )
    if not scripture:
        scripture = (
            '<p class="no-fragment"><strong>References:</strong> '
            + esc(", ".join(refs) if refs else "No verse reference attached")
            + "</p>"
        )

    motifs = ", ".join(str(value) for value in arr(row.get("motifs")) if value)
    boundary = row.get("counter_text") or row.get("source_correction")
    provenance = row.get("provenance")
    owners = [str(owner) for owner in arr(row.get("owners")) if owner]
    owner_links = "".join(
        f'<a href="../../{esc(owner)}"><code>{esc(owner)}</code></a>'
        for owner in owners
    )

    interpretive = (
        f'<div class="context-card"><h4>Why the relation is here</h4><p>{esc(relation_explanation)}</p>'
        + (
            f'<p><strong>Prophecy classification:</strong> {esc(prophecy_status.replace("-", " "))}. '
            'This is the project/archive classification; it is not presented as independent proof of supernatural prophecy.</p>'
            if prophecy_status
            else '<p>This row is a scripture parallel or attestation unless the record explicitly carries a prophecy/foresight classification.</p>'
        )
        + "</div>"
    )

    extra = ""
    if provenance:
        extra += f'<div class="context-card"><h4>Provenance</h4><p>{esc(provenance)}</p></div>'
    if boundary:
        extra += f'<div class="context-card boundary"><h4>Boundary / counter-text</h4><p>{esc(boundary)}</p></div>'
    if owner_links:
        extra += f'<div class="context-card sources full"><h4>Canonical owners</h4><div class="owner-links">{owner_links}</div></div>'

    title = row.get("title") or " · ".join(filter(None, [str(row.get("date") or ""), str(row.get("actor") or ""), refs[0] if refs else "Scripture relation"]))
    return f'''<article class="relation" data-static-relation="{esc(row.get('id'))}">
<div class="relation-head"><div><h2 class="relation-title">{esc(title)}</h2><div class="relation-meta">{chip_html}</div></div><code class="relation-id">{esc(row.get('id'))}</code></div>
<div class="parallel">
<section class="side"><h3>Tim / project anchor</h3><p class="project-anchor">{esc(row.get('project_anchor'))}</p>{f'<p class="motifs"><strong>Motifs:</strong> {esc(motifs)}</p>' if motifs else ''}</section>
<section class="side scripture"><h3>Scripture beside it</h3>{scripture}<p class="scope">{esc(', '.join(refs))}</p></section>
</div>
<div class="context-grid">{interpretive}{extra}</div>
</article>'''


def main() -> int:
    if not SITE_PAGE.exists():
        raise SystemExit("Bible build requires scripts/build_site.py first")

    field = load(FIELD_PATH)
    fragment_data = load(FRAGMENTS_PATH)
    rows = field.get("relations", [])
    if not isinstance(rows, list) or not rows:
        raise SystemExit("canonical Bible relation field contains no relations")

    fragments = fragment_index(fragment_data)
    class_labels = {str(item.get("id")): str(item.get("meaning") or item.get("id")) for item in field.get("relation_classes", [])}
    discovery_labels = {str(item.get("id")): str(item.get("label") or item.get("id")) for item in field.get("discovery_modes", [])}

    rendered = "\n".join(render_relation(row, fragments, class_labels, discovery_labels) for row in rows)
    source = SITE_PAGE.read_text(encoding="utf-8")
    if source.count(MARKER) != 1:
        raise SystemExit(f"expected exactly one {MARKER} in {SITE_PAGE.relative_to(ROOT)}")
    source = source.replace(MARKER, rendered)
    SITE_PAGE.write_text(source, encoding="utf-8")

    print(f"Bible comparator compiled: {len(rows)} canonical relations -> {SITE_PAGE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
