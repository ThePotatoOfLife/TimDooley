#!/usr/bin/env python3
"""Collapse generated country layers into one canonical record per country."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COUNTRIES=ROOT/'data/countries'; LAYER=ROOT/'data/country-layer-manifest.json'; INDEX=ROOT/'data/country-enrichment-index.json'
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def merge(a,b):
    if isinstance(a,dict) and isinstance(b,dict):
        out=dict(a)
        for k,v in b.items(): out[k]=merge(out[k],v) if k in out else v
        return out
    return b
def strip_nulls(v):
    if isinstance(v,dict): return {k:strip_nulls(x) for k,x in v.items() if x is not None}
    if isinstance(v,list): return [strip_nulls(x) for x in v if x is not None]
    return v
def substantive(v):
    if v is None:return False
    if isinstance(v,dict):return any(substantive(x) for x in v.values())
    if isinstance(v,list):return any(substantive(x) for x in v)
    return True
def main():
    merged=0; removed=[]
    for enrichment in sorted(COUNTRIES.glob('*-enrichment.json')):
        cid=enrichment.name.removesuffix('-enrichment.json'); base=COUNTRIES/f'{cid}.json'; enriched=load(enrichment)
        record=merge(load(base),enriched) if base.exists() else enriched
        record=strip_nulls(record); record.setdefault('record_type','country'); record.setdefault('identity',{'id':cid})
        if 'deepening' in record and not substantive(record['deepening'].get('layers',{})):record.pop('deepening',None)
        record['status']='sourced-enriched'; provenance=record.setdefault('provenance',{}); provenance.pop('enrichment_file',None); provenance['enrichment_merged']=True; provenance['enrichment_layer']='retired overlay merged into canonical country record'
        base.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); enrichment.unlink(); merged+=1
    for pattern in ('country-enrichment-batch-*.json','country-nodes-batch-*.json','country-refresh-state.json','country-static.json','repository-audit-*.json','population-pass-*.json'):
        for path in sorted((ROOT/'data').glob(pattern)):
            path.unlink(); removed.append(str(path.relative_to(ROOT)))
    for path in (COUNTRIES/'deepening-state.json',COUNTRIES/'instantiation-state.json'):
        if path.exists():path.unlink();removed.append(str(path.relative_to(ROOT)))
    layer=load(LAYER); layer.update({'version':'2.0.0','purpose':'Canonical country library manifest. Each country owns one substantive record; reusable schema lives in the blueprints.','batch_count':0,'batch_manifests':[],'node_manifests':['data/country-nodes.json'],'record_pattern':'data/countries/<country-id>.json','enrichment_pattern':None,'page_pattern':None}); layer.pop('enriched_ids',None); LAYER.write_text(json.dumps(layer,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    idx=load(INDEX); idx.update({'version':'3.0.0','purpose':'Compatibility country index. The canonical country record is data/countries/<country-id>.json; enrichment overlays have been merged.','remaining_count':0,'record_pattern':'data/countries/<country-id>.json','enrichment_pattern':None,'page_pattern':None,'layer_manifest':'data/country-layer-manifest.json','batch_manifests':[],'node_manifests':['data/country-nodes.json'],'legacy_nodes':'data/country-nodes.json'}); idx.pop('enrichment_overlay_count',None); INDEX.write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'countries_merged':merged,'artifacts_removed':removed},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
