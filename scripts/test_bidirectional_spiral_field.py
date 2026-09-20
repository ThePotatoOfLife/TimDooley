#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIELD=ROOT/'data/house/bidirectional-spiral-field.json'
RUNTIME=ROOT/'app/bidirectional-spiral-field.js'
PAGES=(
    ROOT/'house/index.html',
    ROOT/'below/index.html',
    ROOT/'axis/index.html',
    ROOT/'potato-of-life/index.html',
)

def main()->int:
    errors=[]
    try:
        field=json.loads(FIELD.read_text(encoding='utf-8'))
    except Exception as exc:
        print('SPIRAL REGRESSION TEST FAILED')
        print('-',exc)
        return 1

    ecology=field.get('section_ecology',{})
    rows=[ecology.get('center',{})]+ecology.get('upper',[])+ecology.get('lower',[])
    keys={row.get('key') for row in rows if isinstance(row,dict)}
    expected={'0','+1','+2','+3','+4','-1','-2','-3','-4'}
    if keys!=expected:
        errors.append(f'section keys drifted: {sorted(keys)}')
    if 'not stacked realms' not in ecology.get('rule','').casefold():
        errors.append('section ecology lost sampled-section/not-realm boundary')
    if 'movable analytical cuts' not in ecology.get('room_mapping_rule','').casefold():
        errors.append('Room projection grammar drifted')

    runtime=RUNTIME.read_text(encoding='utf-8',errors='replace')
    required=(
        "data-section-reader",
        "data-section-tabs",
        "data-section-card",
        "root.dataset.focusSection",
        "section_ecology",
        "selectSection",
        "aria-pressed",
        "is-selected",
        "section ecology unavailable",
        "root.dataset.spiralSource",
    )
    for marker in required:
        if marker not in runtime:
            errors.append(f'runtime missing marker: {marker}')

    for page in PAGES:
        text=page.read_text(encoding='utf-8',errors='replace')
        rel=page.relative_to(ROOT).as_posix()
        if 'data-bidirectional-spiral-field' not in text:
            errors.append(f'{rel} missing spiral mount')
        if '<script src="../app/bidirectional-spiral-field.js' not in text:
            errors.append(f'{rel} missing spiral runtime script')
        if 'bidirectional-spiral-field.css' not in text:
            errors.append(f'{rel} missing spiral stylesheet')
        if 'data/house/bidirectional-spiral-field.json' not in text:
            errors.append(f'{rel} missing canonical spiral source')

    house=(ROOT/'house/index.html').read_text(encoding='utf-8',errors='replace')
    below=(ROOT/'below/index.html').read_text(encoding='utf-8',errors='replace')
    if 'data-focus-section="+2"' not in house:
        errors.append('House must focus branching section +2')
    if 'data-focus-section="-3"' not in below:
        errors.append('Below must focus Swamp section -3')

    if errors:
        print('SPIRAL REGRESSION TEST FAILED')
        for error in errors:
            print('-',error)
        return 1
    print('SPIRAL REGRESSION TEST PASSED: canonical sections, runtime selection/fallback markers and four public mounts are intact.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
