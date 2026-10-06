#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED_KINDS = {'relations', 'fragments', 'scenes', 'source', 'annotations', 'research'}
ALLOWED_STATUSES = {'canonical', 'additive', 'research', 'quarantined'}
ACTIVE_STATUSES = {'canonical', 'additive'}


def validate_manifest(root: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    layers = manifest.get('layers')
    if not isinstance(layers, list) or not layers:
        return ['manifest layers must be a non-empty list']

    ids: set[str] = set()
    active_paths: dict[str, str] = {}
    for index, layer in enumerate(layers):
        prefix = f'layer[{index}]'
        layer_id = layer.get('id')
        kind = layer.get('kind')
        path = layer.get('path')
        status = layer.get('status')
        precedence = layer.get('precedence')

        if not isinstance(layer_id, str) or not layer_id.strip():
            errors.append(f'{prefix}: missing id')
        elif layer_id in ids:
            errors.append(f'{prefix}: duplicate layer id {layer_id}')
        else:
            ids.add(layer_id)

        if kind not in ALLOWED_KINDS:
            errors.append(f'{prefix}: invalid kind {kind!r}')
        if status not in ALLOWED_STATUSES:
            errors.append(f'{prefix}: invalid status {status!r}')
        if not isinstance(precedence, int):
            errors.append(f'{prefix}: precedence must be an integer')

        if not isinstance(path, str) or not path.strip():
            errors.append(f'{prefix}: missing path')
            continue
        resolved = root / path
        if not resolved.exists():
            errors.append(f'{prefix}: missing path {path}')
        if status in ACTIVE_STATUSES:
            other = active_paths.get(path)
            if other:
                errors.append(f'{prefix}: duplicate active path {path} also registered by {other}')
            else:
                active_paths[path] = layer_id or prefix

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / 'knowledge' / 'traditions' / 'bible-layer-manifest.json'
    if not path.exists():
        print('BIBLE LAYER MANIFEST VALIDATION FAILED')
        print(f' - missing manifest: {path.relative_to(root)}')
        return 1
    try:
        manifest = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        print('BIBLE LAYER MANIFEST VALIDATION FAILED')
        print(f' - could not parse manifest: {exc}')
        return 1
    errors = validate_manifest(root, manifest)
    if errors:
        print('BIBLE LAYER MANIFEST VALIDATION FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print(f"BIBLE LAYER MANIFEST VALIDATION PASSED ({len(manifest['layers'])} layers)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
