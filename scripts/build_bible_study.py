#!/usr/bin/env python3
"""Compile a compact no-JS Bible comparison index from the canonical manifest corpus."""
from __future__ import annotations

import html
from pathlib import Path

from bible_corpus import assemble_fragments, assemble_relations, load_manifest

ROOT = Path(__file__).resolve().parents[1]
SITE_PAGE = ROOT / "_site" / "traditions" / "bible" / "index.html"
MARKER = "<!-- BIBLE_RELATIONS_STATIC -->"
# Generated disclosures are inserted into the page container with class="static-index".


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def arr(value: object) -> list:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def fragment_index(fragments: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for fragment in fragments:
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
    source_wording = []
    for value in (
        *arr(row.get("project_quote")),
        *arr(row.get("exact_wording")),
        *arr(row.get("public_wording")),
        *arr(row.get("recovered_wording")),
        row.get("quote"),
    ):
        text = str(value or "").strip()
        if text and text not in source_wording:
            source_wording.append(text)
    wording_label = row.get("wording_status") or row.get("discovery_mode") or row.get("evidence_kind") or "project-side wording"
    wording_html = "".join(
        f'<blockquote class="project-quote source-wording">{esc(text)}<cite>{esc(wording_label)}</cite></blockquote>'
        for text in source_wording[:3]
    )
    if not wording_html:
        wording_html = '<div class="source-gap"><strong>Source-near wording:</strong> No direct/public/recovered Tim-side wording is attached yet. Treat the project-side text below as synthesis until a closer source is recovered.</div>'
    project_context = row.get("project_context") or row.get("project_anchor")
    project_development = row.get("project_development")
    reader_scene = row.get("reader_scene") or {}
    reader_sequence = row.get("reader_sequence") or {}
    project_sequence = [str(x).strip() for x in arr((argument or {}).get("project_sequence")) if str(x).strip()]
    if not project_development:
        project_development = (argument or {}).get("why_it_matters") or (argument or {}).get("why_dense")
    project_sequence_html = (
        '<ol class="project-sequence">' + ''.join(f'<li>{esc(step)}</li>' for step in project_sequence) + '</ol>'
        if project_sequence else ''
    )
    boundary = f'<p><strong>Where it breaks:</strong> {esc(mismatch)}</p>' if mismatch else ""
    direction_html = f'<p><strong>Source direction:</strong> {esc(direction)}</p>' if direction else ""
    scene_parts = []
    for key, label in (
        ("opening", "At that time"),
        ("movement", "And it came to pass"),
        ("speech", "And the words were"),
        ("response", "And those present / what followed"),
        ("turn", "And from there"),
        ("scripture_bridge", "Under the biblical light"),
    ):
        value = reader_scene.get(key)
        if value:
            scene_parts.append(f'<p><strong>{esc(label)}:</strong> {esc(value)}</p>')
    scene_html = (
        '<section class="static-chronicle"><h4>The scene</h4>' + ''.join(scene_parts) + '</section>'
        if scene_parts else (f'<p><strong>What was happening:</strong> {esc(scene.get("summary"))}</p>' if scene.get("summary") else "")
    )
    sequence_steps = []
    for step in arr(reader_sequence.get("steps")):
        if not isinstance(step, dict):
            continue
        label = step.get("source_label") or step.get("source_type") or "Sequence"
        heading = step.get("heading") or ""
        text = step.get("text") or ""
        quote = step.get("quote") or ""
        ref = step.get("ref") or ""
        body = ''.join(
            part for part in (
                f'<strong>{esc(heading)}</strong>' if heading else '',
                f'<p>{esc(text)}</p>' if text else '',
                f'<blockquote>{esc(quote)}</blockquote>' if quote else '',
                f'<p><em>{esc(ref)}</em></p>' if ref else '',
            ) if part
        )
        sequence_steps.append(f'<li><span>{esc(label)}</span>{body}</li>')
    reader_sequence_html = (
        '<section class="static-continuous-sequence"><h4>' + esc(reader_sequence.get("title") or "Continuous reading") + '</h4>'
        + (f'<p>{esc(reader_sequence.get("intro"))}</p>' if reader_sequence.get("intro") else '')
        + '<ol>' + ''.join(sequence_steps) + '</ol>'
        + (f'<p><strong>Reading result:</strong> {esc(reader_sequence.get("conclusion"))}</p>' if reader_sequence.get("conclusion") else '')
        + '</section>'
        if sequence_steps else ''
    )
    why = argument.get("why_dense") or argument.get("why_it_matters")
    why_html = f'<p><strong>Why these connect:</strong> {esc(why)}</p>' if why else ""
    max_html = f'<p><strong>Maximum defensible claim:</strong> {esc(argument.get("maximum_claim"))}</p>' if argument.get("maximum_claim") else ""

    return f'''<details class="static-relation" data-static-relation="{esc(row.get('id'))}">
<summary><strong>{esc(title)}</strong> <span>{esc(meta)}</span></summary>
<div class="static-relation-body">
{scene_html}
{wording_html}
{reader_sequence_html}
<p><strong>Archive grounding:</strong> {esc(project_context)}</p>
{project_sequence_html}
{f'<p><strong>Why this matters / what it later becomes:</strong> {esc(project_development)}</p>' if project_development else ''}
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
    manifest = load_manifest(ROOT)
    rows = assemble_relations(ROOT, manifest)
    fragments = fragment_index(assemble_fragments(ROOT, manifest))
    if not rows:
        raise SystemExit("Canonical Bible relation field is empty")
    source = SITE_PAGE.read_text(encoding="utf-8")
    if source.count(MARKER) != 1:
        raise SystemExit(f"Expected exactly one {MARKER}")
    source = source.replace(MARKER, "\n".join(render(row, fragments) for row in rows))
    SITE_PAGE.write_text(source, encoding="utf-8")
    print(f"Bible comparator compact fallback compiled: {len(rows)} manifest-defined active relations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
