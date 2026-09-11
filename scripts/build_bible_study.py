#!/usr/bin/env python3
"""Compile the canonical Tim/Scripture relation field into the deployed Bible page."""
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


def fragment_index(data: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for fragment in data.get("fragments", []):
        keys = set(arr(fragment.get("matches")))
        if fragment.get("reference"):
            keys.add(fragment["reference"])
        for key in keys:
            out.setdefault(str(key), []).append(fragment)
    return out


def render(row: dict, fragments: dict[str, list[dict]], class_labels: dict[str, str], discovery_labels: dict[str, str]) -> str:
    refs = [str(x) for x in arr(row.get("biblical_refs")) if x]
    matched: list[dict] = []
    seen: set[str] = set()
    for ref in refs:
        for fragment in fragments.get(ref, []):
            key = str(fragment.get("id") or fragment.get("reference") or fragment.get("text"))
            if key not in seen:
                seen.add(key)
                matched.append(fragment)

    klass = str(row.get("relation_class") or "unclassified")
    mode = str(row.get("discovery_mode") or "")
    prophecy = str(row.get("prophecy_status") or "")
    chips = [row.get("date"), row.get("actor"), discovery_labels.get(mode, mode.replace("-", " ")) if mode else None, klass.replace("-", " ")]
    chip_html = "".join(f'<span class="chip">{esc(x)}</span>' for x in chips if x)
    if row.get("strength") is not None:
        chip_html += f'<span class="chip strength">strength {esc(row.get("strength"))}/5</span>'
    if prophecy:
        chip_html += f'<span class="chip exact">prophecy: {esc(prophecy.replace("-", " "))}</span>'

    scripture = "".join(
        f'<blockquote class="bible-quote">{esc(f.get("text"))}<cite>{esc(f.get("reference"))} · {esc(f.get("translation") or "World English Bible")}</cite></blockquote>'
        for f in matched[:5]
    ) or f'<p class="no-fragment"><strong>Scripture scope:</strong> {esc(", ".join(refs) or "broader biblical tradition")}</p>'

    relation_meaning = class_labels.get(klass, klass.replace("-", " "))
    why = f'<section class="context-card"><h4>Why this relation is here</h4><p>{esc(relation_meaning)}</p>'
    if prophecy:
        why += f'<p><strong>Prophecy / foresight classification:</strong> {esc(prophecy.replace("-", " "))}. This is the archive classification and is not presented as independent proof of supernatural prophecy.</p>'
    else:
        why += '<p>This is a scripture parallel or attestation unless the record explicitly carries a prophecy/foresight classification.</p>'
    why += '</section>'

    extra = ""
    if row.get("source_direction"):
        extra += f'<section class="context-card"><h4>Which came first?</h4><p>{esc(row.get("source_direction"))}</p></section>'
    boundary = row.get("counter_text") or row.get("source_correction")
    if boundary:
        extra += f'<section class="context-card boundary"><h4>Mismatch / correction</h4><p>{esc(boundary)}</p></section>'
    provenance = row.get("provenance")
    if provenance:
        extra += f'<section class="context-card"><h4>Provenance</h4><p>{esc(provenance)}</p></section>'
    owners = [str(x) for x in arr(row.get("owners")) if x]
    if owners:
        extra += '<section class="context-card sources full"><h4>Canonical source owners</h4><p>' + ' · '.join(f'<code>{esc(x)}</code>' for x in owners) + '</p></section>'

    motifs = " · ".join(str(x) for x in arr(row.get("motifs")) if x)
    title = row.get("title") or row.get("project_anchor") or (refs[0] if refs else row.get("id"))
    return f'''<article class="relation" data-static-relation="{esc(row.get('id'))}">
<div class="relation-head"><div><h2 class="relation-title">{esc(title)}</h2><div class="relation-meta">{chip_html}</div></div><code class="relation-id">{esc(row.get('id'))}</code></div>
<div class="parallel"><section class="side"><h3>Tim / Son / project</h3><span class="summary-label">Canonical relation anchor</span><p class="project-anchor">{esc(row.get('project_anchor'))}</p></section><section class="side scripture"><h3>Scripture beside it</h3>{scripture}</section></div>
<p class="scope"><strong>Scripture scope:</strong> {esc(' · '.join(refs) or 'broader biblical tradition')}</p>
{f'<p class="motifs"><strong>Motifs:</strong> {esc(motifs)}</p>' if motifs else ''}
<div class="context-grid">{why}{extra}</div>
</article>'''


def main() -> int:
    if not SITE_PAGE.exists():
        raise SystemExit("Run scripts/build_site.py before build_bible_study.py")
    field = load(FIELD_PATH)
    fragment_data = load(FRAGMENTS_PATH)
    rows = field.get("relations", [])
    if not isinstance(rows, list) or not rows:
        raise SystemExit("Canonical Bible relation field is empty")
    fragments = fragment_index(fragment_data)
    class_labels = {str(x.get("id")): str(x.get("meaning") or x.get("id")) for x in field.get("relation_classes", [])}
    discovery_labels = {str(x.get("id")): str(x.get("label") or x.get("id")) for x in field.get("discovery_modes", [])}
    source = SITE_PAGE.read_text(encoding="utf-8")
    if source.count(MARKER) != 1:
        raise SystemExit(f"Expected exactly one {MARKER}")
    source = source.replace(MARKER, "\n".join(render(row, fragments, class_labels, discovery_labels) for row in rows))
    SITE_PAGE.write_text(source, encoding="utf-8")
    print(f"Bible comparator compiled: {len(rows)} canonical relations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
