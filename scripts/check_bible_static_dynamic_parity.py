#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from bible_corpus import assemble_relations, load_manifest

ROOT = Path(__file__).resolve().parents[1]
SITE_PAGE = ROOT / '_site' / 'traditions' / 'bible' / 'index.html'

TTS_MARKERS = (
    'id="bible-tts-drawer"',
    'href="../../app/tts-drawer.css"',
    'src="../../app/tts-reader.js"',
    'src="../../app/tts-drawer.js"',
    'src="../../app/bible-tts-adapter.js"',
)


def static_relation_ids(html: str) -> list[str]:
    return re.findall(r'data-static-relation="([^"]+)"', html)


def parity_errors(active_ids: list[str], static_ids: list[str]) -> list[str]:
    active = set(active_ids)
    static = set(static_ids)
    return [
        *[f'static build missing active relation: {rid}' for rid in sorted(active - static)],
        *[f'static build has non-active relation: {rid}' for rid in sorted(static - active)],
    ]


def tts_errors(html: str) -> list[str]:
    errors = [f'built Bible comparator missing TTS marker: {marker}' for marker in TTS_MARKERS if marker not in html]
    mount_pos = html.find('id="bible-tts-drawer"')
    nav_pos = html.find('class="comparison-nav"')
    if mount_pos < 0 or nav_pos < 0 or mount_pos > nav_pos:
        errors.append('built Bible comparator must place the TTS reader before comparison navigation')
    reader_pos = html.find('src="../../app/tts-reader.js"')
    drawer_pos = html.find('src="../../app/tts-drawer.js"')
    adapter_pos = html.find('src="../../app/bible-tts-adapter.js"')
    if not (0 <= reader_pos < drawer_pos < adapter_pos):
        errors.append('built Bible TTS dependencies must load engine -> drawer -> Bible adapter')
    return errors


def main() -> int:
    if not SITE_PAGE.exists():
        print('BIBLE STATIC/DYNAMIC PARITY FAILED')
        print(' - deployed Bible page not built')
        return 1
    html = SITE_PAGE.read_text(encoding='utf-8')
    manifest = load_manifest(ROOT)
    active_ids = [row['id'] for row in assemble_relations(ROOT, manifest)]
    static_ids = static_relation_ids(html)
    errors = parity_errors(active_ids, static_ids)
    errors.extend(tts_errors(html))
    if errors:
        print('BIBLE STATIC/DYNAMIC PARITY FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print(f'BIBLE STATIC/DYNAMIC PARITY PASSED ({len(active_ids)} relations; TTS mount present)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
