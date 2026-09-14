#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from bible_corpus import CorpusError, assemble_fragments, assemble_relations, assemble_scenes


def dump(root: Path, rel: str, data: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding='utf-8')


def layer(layer_id: str, kind: str, path: str, precedence: int, status: str = 'additive') -> dict:
    return {'id': layer_id, 'kind': kind, 'path': path, 'status': status, 'precedence': precedence}


def run_tests() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        dump(root, 'base.json', {'relations':[{'id':'r1','title':'base'}]})
        dump(root, 'late.json', {'enrichments':[{'relation_id':'r1','title':'late'}], 'new_relations':[{'id':'r2'}]})
        manifest = {'layers':[layer('late','relations','late.json',20), layer('base','relations','base.json',0,'canonical')]}
        rows = assemble_relations(root, manifest)
        assert [row['id'] for row in rows] == ['r1','r2']
        assert rows[0]['title'] == 'late'

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        dump(root, 'base.json', {'relations':[{'id':'r1'}]})
        dump(root, 'research.json', {'new_relations':[{'id':'research-only'}]})
        manifest = {'layers':[layer('base','relations','base.json',0,'canonical'), layer('research','relations','research.json',1,'research')]}
        assert [row['id'] for row in assemble_relations(root, manifest)] == ['r1']

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        dump(root, 'base.json', {'relations':[{'id':'r1'}]})
        dump(root, 'dup.json', {'new_relations':[{'id':'r1'}]})
        manifest = {'layers':[layer('base','relations','base.json',0,'canonical'), layer('dup','relations','dup.json',1)]}
        try:
            assemble_relations(root, manifest)
        except CorpusError as exc:
            assert 'duplicate relation id r1' in str(exc)
        else:
            raise AssertionError('expected duplicate relation failure')

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        dump(root, 'base.json', {'relations':[{'id':'r1'}]})
        dump(root, 'bad.json', {'enrichments':[{'relation_id':'missing','title':'x'}]})
        manifest = {'layers':[layer('base','relations','base.json',0,'canonical'), layer('bad','relations','bad.json',1)]}
        try:
            assemble_relations(root, manifest)
        except CorpusError as exc:
            assert 'missing enrichment target missing' in str(exc)
        else:
            raise AssertionError('expected missing enrichment failure')

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        dump(root, 'a.json', {'fragments':[{'id':'f1','text':'first'}]})
        dump(root, 'b.json', {'fragments':[{'id':'f1','text':'second'},{'id':'f2','text':'new'}]})
        manifest = {'layers':[layer('a','fragments','a.json',0,'canonical'), layer('b','fragments','b.json',1)]}
        assert [(row['id'], row['text']) for row in assemble_fragments(root, manifest)] == [('f1','first'),('f2','new')]

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        dump(root, 'a.json', {'scenes':[{'id':'s1'}]})
        dump(root, 'b.json', {'scenes':[{'id':'s1'}]})
        manifest = {'layers':[layer('a','scenes','a.json',0,'canonical'), layer('b','scenes','b.json',1)]}
        try:
            assemble_scenes(root, manifest)
        except CorpusError as exc:
            assert 'duplicate scene id s1' in str(exc)
        else:
            raise AssertionError('expected duplicate scene failure')


def main() -> int:
    run_tests()
    print('BIBLE CORPUS TESTS PASSED (6 behaviors)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
