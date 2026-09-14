#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from bible_corpus import assemble_relations, load_manifest

ROOT = Path(__file__).resolve().parents[1]
SITE_PAGE = ROOT / '_site' / 'traditions' / 'bible' / 'index.html'


def static_relation_ids(html: str) -> list[str]:
    return re.findall(r'data-static-relation="([^"]+)"', html)


def parity_errors(active_ids: list[str], static_ids: list[str]) -> list[str]:
    active = set(active_ids)
    static = set(static_ids)
    return [
        *[f'static build missing active relation: {rid}' for rid in sorted(active - static)],
        *[f'static build has non-active relation: {rid}' for rid in sorted(static - active)],
    ]


def main() -> int:
    if not SITE_PAGE.exists():
        print('BIBLE STATIC/DYNAMIC PARITY FAILED')
        print(' - deployed Bible page not built')
        return 1
    manifest = load_manifest(ROOT)
    active_ids = [row['id'] for row in assemble_relations(ROOT, manifest)]
    static_ids = static_relation_ids(SITE_PAGE.read_text(encoding='utf-8'))
    errors = parity_errors(active_ids, static_ids)
    if errors:
        print('BIBLE STATIC/DYNAMIC PARITY FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print(f'BIBLE STATIC/DYNAMIC PARITY PASSED ({len(active_ids)} relations)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
