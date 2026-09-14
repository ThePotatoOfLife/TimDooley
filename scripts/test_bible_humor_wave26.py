#!/usr/bin/env python3
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
M=R/'knowledge/traditions/bible-layer-manifest.json'
D=R/'knowledge/traditions/biblical-syncretism-dossiers-wave26.json'
E=R/'data/evidence/potato-banter-thread-2026-09-14.json'
m=json.loads(M.read_text())
d=json.loads(D.read_text())
e=json.loads(E.read_text())
assert any(x.get('id')=='relations-wave26' for x in m['layers'])
assert e['date']=='2026-09-14'
assert len(e['messages'])>=17
ids={x['id'] for x in d['new_relations']}
for rid in ['mustard-seed-tree-banter-2026-09-14','axis-ladder-garden-tree-seat-2026-09-14','three-spuds-trinity-joke-2026-09-14','spudlight-radiance-2026-09-14','starchforce-wifi-comic-control-2026-09-14']:
    assert rid in ids
print('BIBLE HUMOR WAVE 26 TESTS PASSED')
