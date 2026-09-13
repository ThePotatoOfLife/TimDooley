#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/'knowledge/science/potato-biology-source-ledger.json'
ARTIFACTS=ROOT/'data/atlas-artifacts.json'
REQUIRED={'tuber_identity','dormancy_sprouting','tuberization','starch_source_sink','genetics_ploidy','late_blight','domestication_propagation'}

def fail(msg:str)->None: raise SystemExit(f'POTATO BIOLOGY SOURCES FAILED: {msg}')
def load(path:Path)->dict:
    if not path.exists(): fail(f'missing {path.relative_to(ROOT)}')
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict): fail(f'{path.relative_to(ROOT)} must be object')
    return value

def main()->int:
    doc=load(LEDGER)
    if doc.get('id')!='potato-biology-source-ledger': fail('ledger id')
    sources=doc.get('sources')
    if not isinstance(sources,list) or len(sources)<7: fail('need at least seven sources')
    coverage=set()
    scholarly=0
    for row in sources:
        if not isinstance(row,dict): fail('source row')
        url=str(row.get('url') or '')
        parsed=urlparse(url)
        if parsed.scheme!='https' or not parsed.netloc: fail('source url')
        supports=row.get('supports')
        if not isinstance(supports,list) or not supports: fail('source supports')
        coverage.update(str(x) for x in supports)
        if row.get('class') in {'peer_reviewed','research_center'}: scholarly+=1
    missing=sorted(REQUIRED-coverage)
    if missing: fail(f'missing coverage {missing}')
    if scholarly<7: fail('all seed sources must be peer-reviewed or research-center sources')
    artifacts=load(ARTIFACTS).get('artifacts',[])
    matches=[a for a in artifacts if isinstance(a,dict) and a.get('source_path')=='knowledge/science/potato-biology-source-ledger.json' and 'potato-biology-ecology-development-canon' in a.get('node_refs',[])]
    if len(matches)!=1: fail('ledger must be one Atlas Depth Artifact')
    print(f'POTATO BIOLOGY SOURCES PASSED: {len(sources)} sources, {len(coverage)} coverage tags')
    return 0

if __name__=='__main__': raise SystemExit(main())
