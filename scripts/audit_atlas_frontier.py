#!/usr/bin/env python3
"""Report what the active Atlas cannot yet resolve without treating it as failure."""
from __future__ import annotations
import json
from collections import Counter,defaultdict
from pathlib import Path

from atlas_runtime import build_runtime
from atlas_model import by_id

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'atlas-frontier-report.json'


def main()->int:
    runtime=build_runtime();nodes=by_id(runtime)
    unresolved=Counter();provisional=Counter();sources=defaultdict(list);no_artifacts=[];no_children=[]
    for node_id,node in nodes.items():
        if not node.get('artifacts'):no_artifacts.append(node_id)
        if not node.get('children'):no_children.append(node_id)
        for rel in node.get('relations',[]):
            if not rel.get('resolved'):
                target=str(rel.get('target') or '')
                unresolved[target]+=1;sources[target].append(node_id)
            if rel.get('provisional_type'):
                provisional[str(rel.get('type') or 'related')]+=1
    result={
        'schema_version':'1.0.0',
        'active_node_count':len(nodes),
        'unresolved_relation_targets':[{'target':target,'count':count,'from_nodes':sorted(set(sources[target]))} for target,count in unresolved.most_common()],
        'provisional_relation_types':[{'type':label,'count':count} for label,count in provisional.most_common()],
        'nodes_without_seed_artifacts':sorted(no_artifacts),
        'leaf_nodes':sorted(no_children),
        'policy':{
            'unresolved_is_not_automatically_error':True,
            'promotion_rule':'Promote a target to an active Node only after durable subject identity, canonical ownership and one justified North parent are established.',
            'mapping_rule':'Map provisional road wording only after semantic review; never infer North from a lateral owner relation.'
        }
    }
    REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"ATLAS FRONTIER: {len(nodes)} active nodes; {len(unresolved)} unresolved targets; {len(provisional)} provisional road labels; {len(no_artifacts)} nodes without seed Artifacts")
    for row in result['unresolved_relation_targets'][:10]:print(f"  target {row['target']}: {row['count']} from {', '.join(row['from_nodes'])}")
    for row in result['provisional_relation_types'][:10]:print(f"  road {row['type']}: {row['count']}")
    return 0

if __name__=='__main__':raise SystemExit(main())
