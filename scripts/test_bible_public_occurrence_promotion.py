#!/usr/bin/env python3
from __future__ import annotations

from build_bible_public_occurrence_relations import build_relations


def run_tests() -> None:
    occurrence_index = {
        'occurrences': [
            {
                'source_id': 'x-1',
                'date': '2026-09-07',
                'biblical_relation': 'near-direct-scriptural-phrase',
                'timic_motifs': ['Door', 'Garden'],
                'biblical_texts': ['John 10:7-9', 'Genesis 3:23-24'],
                'significance': 'Door and Garden language occur together in the public wording.',
                'mismatch': 'The passages come from different biblical contexts.',
            },
            {
                'source_id': 'x-2',
                'date': '2026-09-08',
                'biblical_relation': 'later-structural-comparator',
                'timic_motifs': ['service'],
                'biblical_texts': ['Mark 10:42-45'],
                'significance': 'Service language is a strong structural neighbor.',
            },
        ]
    }
    source_ledger = {
        'occurrences': [
            {'id': 'x-1', 'quote': 'I am the door in the garden', 'source_url': 'https://x.com/Rational_Potato/status/1'},
            {'id': 'x-2', 'quote': 'Power is for protection', 'source_url': 'https://x.com/Rational_Potato/status/2'},
        ]
    }

    rows = build_relations(occurrence_index, source_ledger)
    assert len(rows) == 2
    first = rows[0]
    assert first['id'] == 'public-x-bible-x-1'
    assert first['exact_wording'] == 'I am the door in the garden'
    assert first['source_url'] == 'https://x.com/Rational_Potato/status/1'
    assert first['source_direction'] == 'project_to_bible'
    assert first['biblical_refs'] == ['John 10:7-9', 'Genesis 3:23-24']
    assert first['project_concept'] == 'Door · Garden'
    assert first['reader_reading'].startswith('The closest biblical neighbors are John 10:7-9 and Genesis 3:23-24.')
    assert 'Door and Garden language occur together' in first['reader_reading']
    assert 'The passages come from different biblical contexts.' in first['reader_reading']
    assert first['counterpoint'] == 'The passages come from different biblical contexts.'
    assert first['occurrence_ids'] == ['x-1']

    second = rows[1]
    assert second['relation_type'] == 'later_structural_comparator'
    assert 'Mark 10:42-45' in second['reader_reading']


def main() -> int:
    run_tests()
    print('BIBLE PUBLIC OCCURRENCE PROMOTION TESTS PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
