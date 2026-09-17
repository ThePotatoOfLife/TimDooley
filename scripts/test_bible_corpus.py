#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from bible_corpus import CorpusError, assemble_fragments, assemble_relations, assemble_scenes, load_manifest, load_relation_redirects
from build_bible_comparator_quality import research_reasons
from build_bible_research_queue import SPECIFIC, generic_task
from test_bible_compact_dossiers import main as compact_dossiers_main

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = '11928304ecbde5290cac5fca818bdb449a25f3c6'
BASELINE_RELATION_COUNT = 145
GAPFILL_LAYER_ID = 'relations-gapfill-wave27'


def dump(root: Path, rel: str, data: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding='utf-8')


def layer(layer_id: str, kind: str, path: str, precedence: int, status: str = 'additive') -> dict:
    return {'id': layer_id, 'kind': kind, 'path': path, 'status': status, 'precedence': precedence}


def git_json(commit: str, path: str) -> dict:
    proc = subprocess.run(
        ['git', 'show', f'{commit}:{path}'],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def relation_ids_from_snapshot(commit: str) -> list[str]:
    manifest = git_json(commit, 'knowledge/traditions/bible-layer-manifest.json')
    active = {'canonical', 'additive'}
    relation_layers = sorted(
        (
            item for item in manifest.get('layers', [])
            if item.get('kind') == 'relations' and item.get('status') in active
        ),
        key=lambda item: (int(item.get('precedence', 0)), str(item.get('id', ''))),
    )
    ids: list[str] = []
    seen: set[str] = set()
    for meta in relation_layers:
        data = git_json(commit, meta['path'])
        for key in ('relations', 'new_relations'):
            for row in data.get(key, []) or []:
                rid = str(row.get('id') or '')
                assert rid, f"baseline relation without id in {meta['id']}"
                assert rid not in seen, f'duplicate baseline relation id {rid}'
                seen.add(rid)
                ids.append(rid)
        for enrichment in data.get('enrichments', []) or []:
            target = str(enrichment.get('relation_id') or '')
            assert target in seen, f"baseline enrichment target missing before merge: {target}"
    return ids


def test_additive_gapfill_baseline() -> None:
    baseline_ids = relation_ids_from_snapshot(BASELINE_COMMIT)
    assert len(baseline_ids) == BASELINE_RELATION_COUNT, (
        f'expected locked Bible baseline of {BASELINE_RELATION_COUNT}, got {len(baseline_ids)}'
    )

    manifest = load_manifest(ROOT)
    current_rows = assemble_relations(ROOT, manifest)
    current_ids = {row['id'] for row in current_rows}
    missing = sorted(set(baseline_ids) - current_ids)
    assert not missing, f'Bible baseline relation loss: {missing[:12]}'
    assert any(layer.get('id') == GAPFILL_LAYER_ID for layer in manifest.get('layers', [])), (
        'additive Bible gap-fill layer is not registered'
    )


def test_current_redirect_contract() -> None:
    redirects = load_relation_redirects(ROOT)
    assert len(redirects) >= 9, 'expected duplicate public-X projections to be consolidated'
    rows = assemble_relations(ROOT, load_manifest(ROOT))
    ids = {row['id'] for row in rows}
    for source, target in redirects.items():
        assert source not in ids, f'redirected duplicate still active: {source}'
        assert target in ids, f'redirect target missing from active corpus: {target}'


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
        dump(root, 'base.json', {'relations':[{'id':'r1','relation_argument':{'project_sequence':['a'],'biblical_sequence':['b'],'why_dense':'dense'}}]})
        dump(root, 'late.json', {'enrichments':[{'relation_id':'r1','relation_argument':{'why_it_matters':'matters'}}]})
        manifest = {'layers':[layer('base','relations','base.json',0,'canonical'), layer('late','relations','late.json',1)]}
        row = assemble_relations(root, manifest)[0]
        assert row['relation_argument'] == {
            'project_sequence':['a'],
            'biblical_sequence':['b'],
            'why_dense':'dense',
            'why_it_matters':'matters',
        }

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        dump(root, 'base.json', {'relations':[{'id':'r1'},{'id':'legacy'}]})
        dump(root, 'knowledge/traditions/bible-relation-redirects.json', {'redirects':{'legacy':'r1'}})
        manifest = {'layers':[layer('base','relations','base.json',0,'canonical')]}
        rows = assemble_relations(root, manifest)
        assert [row['id'] for row in rows] == ['r1']

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

    assert research_reasons({'strength':2}, ['why_it_matters']) == ['low-strength','interpretation-gap']
    assert research_reasons({}, ['project_side','source_direction']) == ['project-evidence-gap','unscored-provisional']
    assert research_reasons({'dossier_level':'A'}, ['biblical_sequence']) == ['biblical-context-gap']
    assert research_reasons({'dossier_level':'B'}, ['counterpressure','supported_conclusion']) == ['boundary-gap','unscored-provisional']
    assert research_reasons({'strength':4}, ['why_it_matters']) == ['interpretation-gap']

    plan = generic_task({'strength':2}, {'research_reasons':['low-strength','interpretation-gap']})
    assert plan['status'] == 'recover-project-evidence'
    assert plan['priority'] == 'high'
    assert 'solely because contextual prose becomes more complete' in plan['upgrade_rule']
    assert SPECIFIC['crucify-me-hesitation-trial-neighbor-2017']['status'] == 'recover-original-message'
    assert SPECIFIC['son-death-shore-bones-deep-water-2018-2019']['status'] == 'recover-primary-artifact'

    test_additive_gapfill_baseline()
    test_current_redirect_contract()


def main() -> int:
    run_tests()
    if compact_dossiers_main() != 0:
        return 1
    print('BIBLE CORPUS TESTS PASSED (21 behaviors)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
