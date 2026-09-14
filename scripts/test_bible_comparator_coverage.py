#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_bible_comparator_coverage import build_report


def dump(root: Path, rel: str, data: dict) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding='utf-8')
    return path


def run_tests() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        dump(root, 'relations.json', {
            'relations': [
                {
                    'id': 'r1',
                    'exact_wording': 'I am the door',
                    'source_url': 'https://x.com/Rational_Potato/status/100',
                    'biblical_refs': ['John 10:7-9', 'Revelation 3:20'],
                    'reader_reading': 'Tim speaks first; the passages then gather around the claim.',
                    'source_direction': 'project_to_bible',
                    'relation_type': 'direct_echo',
                    'strength': 5,
                },
                {
                    'id': 'r2',
                    'project_wording': 'garden language',
                    'biblical_refs': ['Genesis 2:15'],
                    'source_direction': 'bible_to_project',
                    'relation_type': 'structural_parallel',
                    'strength': 3,
                },
            ]
        })
        dump(root, 'scenes.json', {'scenes': [{'id': 's1'}]})
        dump(root, 'fragments.json', {'fragments': [{'id': 'f1', 'text': 'door'}]})
        manifest = {
            'layers': [
                {'id': 'relations', 'kind': 'relations', 'path': 'relations.json', 'status': 'canonical', 'precedence': 0},
                {'id': 'scenes', 'kind': 'scenes', 'path': 'scenes.json', 'status': 'canonical', 'precedence': 0},
                {'id': 'fragments', 'kind': 'fragments', 'path': 'fragments.json', 'status': 'canonical', 'precedence': 0},
            ]
        }
        september = {
            'records': [
                {'n': 1, 'status': '100', 'class': 'direct'},
                {'n': 2, 'status': '101', 'class': 'strong'},
                {'n': 3, 'status': '102', 'class': 'weak'},
            ]
        }
        public_x = {
            'records': [
                {'status_id': '100'},
                {'status_id': '103'},
                {'status_id': '103'},
            ]
        }

        report = build_report(root, manifest, september, public_x)
        assert report['active_relation_count'] == 2
        assert report['active_scene_count'] == 1
        assert report['active_fragment_count'] == 1
        assert report['relations_with_exact_wording'] == 1
        assert report['relations_with_public_x_source'] == 1
        assert report['expressive_reading_count'] == 1
        assert report['september_status_count'] == 3
        assert report['september_class_counts'] == {'direct': 1, 'strong': 1, 'weak': 1}
        assert report['september_promotable_count'] == 2
        assert report['public_x_unique_status_count'] == 2
        assert report['public_x_duplicate_status_ids'] == ['103']
        assert report['bible_book_counts']['John'] == 1
        assert report['bible_book_counts']['Revelation'] == 1
        assert report['bible_book_counts']['Genesis'] == 1
        assert report['source_direction_counts'] == {'bible_to_project': 1, 'project_to_bible': 1}
        assert report['relation_type_counts'] == {'direct_echo': 1, 'structural_parallel': 1}
        assert report['strength_counts'] == {'3': 1, '5': 1}


def main() -> int:
    run_tests()
    print('BIBLE COMPARATOR COVERAGE TESTS PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
