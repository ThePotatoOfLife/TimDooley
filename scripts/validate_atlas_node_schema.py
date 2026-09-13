#!/usr/bin/env python3
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'knowledge/schema/atlas-node.schema.json'
if not p.exists(): raise SystemExit('missing atlas-node.schema.json')
d=json.loads(p.read_text())
need={'id','title','kind','status','owner_path','north_parent','summary','epistemic_classes','relations','archive_refs','views','route'}
if not need<=set(d.get('required',[])): raise SystemExit('missing required fields')
print('ATLAS NODE SCHEMA PASSED')
