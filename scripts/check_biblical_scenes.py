#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from bible_corpus import CorpusError, assemble_scenes, load_manifest

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ('id','title','book','canonical_span','scene_type','summary','sequence','roles','operators','source_refs')


def main() -> int:
    try:
        scenes = assemble_scenes(ROOT, load_manifest(ROOT))
    except (OSError, ValueError, CorpusError) as exc:
        print('BIBLICAL SCENE CHECK FAILED')
        print(' -', exc)
        return 1
    errors: list[str] = []
    ids = {scene.get('id') for scene in scenes}
    for scene in scenes:
        sid = scene.get('id', '<missing>')
        for key in REQUIRED:
            value = scene.get(key)
            if value is None or value == '' or value == []:
                errors.append(f'{sid}: missing {key}')
        for key in ('parallel_scene_ids','intertext_scene_ids'):
            for target in scene.get(key, []) or []:
                if target not in ids:
                    errors.append(f'{sid}: unresolved scene link {target}')
    if errors:
        print('BIBLICAL SCENE CHECK FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print(f'BIBLICAL SCENE CHECK PASSED ({len(scenes)} scenes)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
