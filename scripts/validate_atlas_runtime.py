#!/usr/bin/env python3
from __future__ import annotations

from atlas_runtime import build_runtime
from atlas_model import by_id

ALLOWED_ORIENTATIONS={'lateral','structural_down','archival'}


def main()->int:
    runtime=build_runtime();nodes=by_id(runtime)
    if runtime.get('schema_version')!='1.1.0':raise SystemExit('ATLAS RUNTIME FAILED: schema version')
    artifact_ids={str(a.get('id')) for a in runtime.get('artifacts',[]) if isinstance(a,dict)}
    if len(artifact_ids)!=len(runtime.get('artifacts',[])):raise SystemExit('ATLAS RUNTIME FAILED: artifact IDs')
    relation_ids={str(r.get('id')) for r in runtime.get('relation_types',[]) if isinstance(r,dict)}
    if not relation_ids:raise SystemExit('ATLAS RUNTIME FAILED: no relation types')
    for node_id,node in nodes.items():
        views=node.get('view_details',[])
        if len(views)!=len(node.get('views',[])):raise SystemExit(f'ATLAS RUNTIME FAILED: unresolved view on {node_id}')
        attached={str(a.get('id')) for a in node.get('artifacts',[]) if isinstance(a,dict)}
        if not attached<=artifact_ids:raise SystemExit(f'ATLAS RUNTIME FAILED: unknown artifact on {node_id}')
        for rel in node.get('relations',[]):
            orientation=rel.get('orientation')
            if orientation not in ALLOWED_ORIENTATIONS:raise SystemExit(f'ATLAS RUNTIME FAILED: bad orientation {node_id}: {orientation}')
            if rel.get('canonical_type') is not None and rel['canonical_type'] not in relation_ids:raise SystemExit(f'ATLAS RUNTIME FAILED: unknown canonical road type {node_id}')
            if rel.get('canonical_type') is None and rel.get('provisional_type') is not True:raise SystemExit(f'ATLAS RUNTIME FAILED: unmapped road not provisional {node_id}')
    print(f'ATLAS RUNTIME PASSED: {len(nodes)} nodes, {len(artifact_ids)} artifacts, {len(relation_ids)} road types')
    return 0

if __name__=='__main__':raise SystemExit(main())
