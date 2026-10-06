#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / 'app' / 'bible-corpus-loader.js'


def main() -> int:
    text = LOADER.read_text(encoding='utf-8')
    required = (
        'const nativeFetch=',
        'reader_reading',
        'project_concept',
        'relation_type',
        'public-occurrence',
        'biblical-syncretism-field.json',
        'biblical-passage-fragments.json',
        'new Response',
        'corpusPromise',
    )
    missing = [marker for marker in required if marker not in text]
    if missing:
        print('BIBLE CORPUS READER BRIDGE TEST FAILED')
        for marker in missing:
            print(' - missing', repr(marker))
        return 1
    print('BIBLE CORPUS READER BRIDGE TEST PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
