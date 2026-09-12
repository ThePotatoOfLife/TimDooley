#!/usr/bin/env python3
"""Compile a compact no-JS Bible comparison index into the deployed page."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_PAGE = ROOT / "_site" / "traditions" / "bible" / "index.html"
FIELD_PATH = ROOT / "knowledge" / "traditions" / "biblical-syncretism-field.json"
FRAGMENTS_PATH = ROOT / "knowledge" / "traditions" / "biblical-passage-fragments.json"
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


def fragment_index(data: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for fragment in data.get("fragments", []):
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
    mismatch = row.get("counter_text") or row.get("source_correction") or (arr(row.get("weaknesses"))[0] if arr(row.get("weaknesses")) else None)
    direction = row.get("source_direction")
    boundary = f'<p><strong>Where it breaks:</strong> {esc(mismatch)}</p>' if mismatch else ""
    direction_html = f'<p><strong>Source direction:</strong> {esc(direction)}</p>' if direction else ""

    return f'''<details class="static-relation" data-static-relation="{esc(row.get('id'))}">
<summary><strong>{esc(title)}</strong> <span>{esc(meta)}</span></summary>
<div class="static-relation-body">
<p><strong>Project anchor:</strong> {esc(row.get('project_anchor'))}</p>
<p><strong>Scripture scope:</strong> {esc(scope)}</p>
{scripture}
{boundary}
{direction_html}
</div>
</details>'''


def main() -> int:
    if not SITE_PAGE.exists():
        raise SystemExit("Run scripts/build_site.py before build_bible_study.py")
    field = load(FIELD_PATH)
    fragment_data = load(FRAGMENTS_PATH)
    rows = field.get("relations", [])
    if not isinstance(rows, list) or not rows:
        raise SystemExit("Canonical Bible relation field is empty")
    fragments = fragment_index(fragment_data)
    source = SITE_PAGE.read_text(encoding="utf-8")
    if source.count(MARKER) != 1:
        raise SystemExit(f"Expected exactly one {MARKER}")
    source = source.replace(MARKER, "\n".join(render(row, fragments) for row in rows))
    SITE_PAGE.write_text(source, encoding="utf-8")
    print(f"Bible comparator compact fallback compiled: {len(rows)} canonical relations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
