#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

ACTIVE_STATUSES = {'canonical', 'additive'}


class CorpusError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def load_manifest(root: Path) -> dict:
    return load_json(root / 'knowledge' / 'traditions' / 'bible-layer-manifest.json')


def active_layers(manifest: dict, kind: str) -> list[dict]:
    return sorted(
        (layer for layer in manifest.get('layers', []) if layer.get('kind') == kind and layer.get('status') in ACTIVE_STATUSES),
        key=lambda layer: (int(layer.get('precedence', 0)), str(layer.get('id', ''))),
    )


def merge_value(old, new):
    if isinstance(old, dict) and isinstance(new, dict):
        result = copy.deepcopy(old)
        for key, value in new.items():
            result[key] = merge_value(result[key], value) if key in result else copy.deepcopy(value)
        return result
    return copy.deepcopy(new)


def assemble_relations(root: Path, manifest: dict) -> list[dict]:
    rows = []
    by_id = {}
    for layer_meta in active_layers(manifest, 'relations'):
        data = load_json(root / layer_meta['path'])
        for row in data.get('relations', []) or []:
            rid = row.get('id')
            if not rid:
                raise CorpusError(f"relation without id in {layer_meta['id']}")
            if rid in by_id:
                raise CorpusError(f"duplicate relation id {rid} in {layer_meta['id']}")
            item = copy.deepcopy(row)
            rows.append(item)
            by_id[rid] = item
        for enrichment in data.get('enrichments', []) or []:
            rid = enrichment.get('relation_id')
            target = by_id.get(rid)
            if target is None:
                raise CorpusError(f"missing enrichment target {rid} in {layer_meta['id']}")
            for key, value in enrichment.items():
                if key == 'relation_id':
                    continue
                target[key] = merge_value(target[key], value) if key in target else copy.deepcopy(value)
        for row in data.get('new_relations', []) or []:
            rid = row.get('id')
            if not rid:
                raise CorpusError(f"new relation without id in {layer_meta['id']}")
            if rid in by_id:
                raise CorpusError(f"duplicate relation id {rid} in {layer_meta['id']}")
            item = copy.deepcopy(row)
            rows.append(item)
            by_id[rid] = item
    return rows


def assemble_fragments(root: Path, manifest: dict) -> list[dict]:
    rows = []
    seen = set()
    for layer_meta in active_layers(manifest, 'fragments'):
        data = load_json(root / layer_meta['path'])
        for fragment in data.get('fragments', []) or []:
            fid = fragment.get('id')
            if not fid:
                raise CorpusError(f"fragment without id in {layer_meta['id']}")
            if fid in seen:
                continue
            seen.add(fid)
            rows.append(copy.deepcopy(fragment))
    return rows


def assemble_scenes(root: Path, manifest: dict) -> list[dict]:
    rows = []
    seen = set()
    for layer_meta in active_layers(manifest, 'scenes'):
        data = load_json(root / layer_meta['path'])
        for scene in data.get('scenes', []) or []:
            sid = scene.get('id')
            if not sid:
                raise CorpusError(f"scene without id in {layer_meta['id']}")
            if sid in seen:
                raise CorpusError(f"duplicate scene id {sid} in {layer_meta['id']}")
            seen.add(sid)
            rows.append(copy.deepcopy(scene))
    return rows
