#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'data/atlas-deprecations.json'
ALLOWED={'live_legacy','compatibility_only','retire_when_covered','retired'}


def main()->int:
    doc=json.loads(PATH.read_text(encoding='utf-8'))
    entries=doc.get('entries',[])
    if not isinstance(entries,list) or not entries:raise SystemExit('ATLAS DEPRECATIONS FAILED: no entries')
    paths=[]
    for entry in entries:
        if not isinstance(entry,dict):raise SystemExit('ATLAS DEPRECATIONS FAILED: entry must be object')
        rel=str(entry.get('path',''));paths.append(rel)
        state=entry.get('state')
        if state not in ALLOWED:raise SystemExit(f'ATLAS DEPRECATIONS FAILED: invalid state {rel}')
        if state!='retired' and not (ROOT/rel).exists():raise SystemExit(f'ATLAS DEPRECATIONS FAILED: live legacy path missing {rel}')
        replacements=entry.get('replacement',[])
        if not isinstance(replacements,list) or not replacements:raise SystemExit(f'ATLAS DEPRECATIONS FAILED: replacement missing {rel}')
        for replacement in replacements:
            if str(replacement).startswith('future '):continue
            if not (ROOT/str(replacement)).exists():raise SystemExit(f'ATLAS DEPRECATIONS FAILED: replacement path missing {rel} -> {replacement}')
        conditions=entry.get('removal_conditions',[])
        if not isinstance(conditions,list) or len(conditions)<2:raise SystemExit(f'ATLAS DEPRECATIONS FAILED: removal conditions weak {rel}')
    if len(paths)!=len(set(paths)):raise SystemExit('ATLAS DEPRECATIONS FAILED: duplicate path')
    print(f'ATLAS DEPRECATIONS PASSED: {len(entries)} legacy contracts tracked')
    return 0

if __name__=='__main__':raise SystemExit(main())
