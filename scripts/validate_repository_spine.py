#!/usr/bin/env python3
"""Validate the canonical Root -> Spirit -> Door -> Matter navigation model."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def load(rel):
    p=ROOT/rel
    if not p.exists(): errors.append(f"Missing: {rel}"); return {}
    try:return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:errors.append(f"Invalid JSON: {rel}: {exc}");return {}
def main():
    spine=load("data/repository-spine.json")
    layers=spine.get("layers",[])
    expected=["spirit","door","matter"]
    if [x.get("id") for x in layers]!=expected:errors.append("Spine layers must be ordered Spirit, Door, Matter")
    if spine.get("temporal_model")!={"spirit":"future","door":"present","matter":"past"}:errors.append("Temporal model must be future/present/past")
    for layer in layers:
        if not layer.get("sections"):errors.append(f"Layer has no sections: {layer.get('id')}")
        if not layer.get("question"):errors.append(f"Layer has no guiding question: {layer.get('id')}")
    tree=load("data/tree.json")
    legacy=spine.get("legacy_tree_mapping",{})
    tree_ids={x.get("id") for x in tree.get("levels",[]) if isinstance(x,dict)}
    for key in legacy:
        if key not in tree_ids:errors.append(f"Legacy tree mapping references missing level: {key}")
    manifest=load("data/atlas-manifest.json")
    if "architecture" not in manifest.get("layers",{}):errors.append("Manifest architecture layer missing")
    print(f"Spine layers: {len(layers)}")
    print(f"Sections: {sum(len(x.get('sections',[])) for x in layers)}")
    print(f"Legacy tree levels mapped: {len(legacy)}")
    print(f"Errors: {len(errors)}")
    for e in errors:print("ERROR:",e)
    return 1 if errors else 0
if __name__=="__main__":raise SystemExit(main())
