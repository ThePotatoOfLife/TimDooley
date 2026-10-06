#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from bible_corpus import assemble_relations, load_manifest

ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = ROOT / 'knowledge' / 'traditions' / 'bible-relation-redirects.json'


def main() -> int:
    data = json.loads(REDIRECTS.read_text(encoding='utf-8'))
    redirects = data.get('redirects') or {}
    assert isinstance(redirects, dict), 'redirects must be an object'
    assert redirects, 'expected at least one consolidated Bible relation redirect'
    assert all(source and target and source != target for source, target in redirects.items())

    rows = assemble_relations(ROOT, load_manifest(ROOT))
    active_ids = {row.get('id') for row in rows}
    for source, target in redirects.items():
        assert source not in active_ids, f'redirected duplicate still active: {source}'
        assert target in active_ids, f'redirect target missing from active corpus: {target}'
        seen = {source}
        cursor = target
        while cursor in redirects:
            assert cursor not in seen, f'redirect cycle involving {cursor}'
            seen.add(cursor)
            cursor = redirects[cursor]
        assert cursor in active_ids, f'redirect chain does not end at active relation: {source}'

    print(f'bible relation redirects: ok ({len(redirects)} consolidated ids)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
