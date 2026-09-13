#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/'.github/workflows/pages.yml'


def fail(message:str)->None:
    raise SystemExit(f'PAGES DEPLOY CONTRACT FAILED: {message}')


def main()->int:
    text=WORKFLOW.read_text(encoding='utf-8')
    if 'run: python scripts/build_public_site.py' not in text:
        fail('Pages must use composed public-site builder so Atlas is deployed')
    if 'run: python scripts/build_site.py' in text:
        fail('legacy-only builder must not be the Pages artifact builder')
    expected="new_bootstrap = f'src=\"./3d-bootstrap.js?v={version}\"'"
    if expected not in text:
        fail('3d-bootstrap cache-busted src must retain closing quote')
    for marker in (
        'test -f _site/atlas/index.html',
        'test -f _site/data/atlas-index.json',
        "grep -q 'href=\"world/\"' _site/index.html",
    ):
        if marker not in text:
            fail(f'missing deployment smoke check: {marker}')
    print('PAGES DEPLOY CONTRACT PASSED: composed build + Atlas artifact + canonical World route + valid bootstrap src')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
