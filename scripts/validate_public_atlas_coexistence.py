#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'
LEGACY=(
    'index.html',
    'tim-dooley/index.html',
    'religion/index.html',
    'philosophy/index.html',
    'science/index.html',
    'world/index.html',
    'timeline/index.html',
    'world-map/index.html',
)
ATLAS=(
    'atlas/index.html',
    'atlas/potato-of-life/index.html',
    'atlas/tim-dooley/index.html',
    'atlas/root-system/index.html',
)

def main()->int:
    missing=[rel for rel in (*LEGACY,*ATLAS) if not (OUT/rel).exists()]
    if missing:raise SystemExit(f'PUBLIC ATLAS COEXISTENCE FAILED: missing {missing}')
    home=(OUT/'index.html').read_text(encoding='utf-8',errors='replace')
    if 'tim-dooley/' not in home or 'religion/' not in home:
        raise SystemExit('PUBLIC ATLAS COEXISTENCE FAILED: legacy home was replaced')
    atlas=(OUT/'atlas/index.html').read_text(encoding='utf-8',errors='replace')
    if 'Current knowledge plane' not in atlas:
        raise SystemExit('PUBLIC ATLAS COEXISTENCE FAILED: Atlas landing not generated')
    if not (OUT/'app/design-system.css').exists():
        raise SystemExit('PUBLIC ATLAS COEXISTENCE FAILED: shared Atlas CSS missing')
    print(f'PUBLIC ATLAS COEXISTENCE PASSED: {len(LEGACY)} legacy sentinels + {len(ATLAS)} Atlas sentinels')
    return 0

if __name__=='__main__':raise SystemExit(main())
