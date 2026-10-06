#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from bible_corpus import assemble_relations, assemble_scenes, load_manifest
from build_bible_comparator_quality import build_report

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'knowledge' / 'indexes' / 'bible-comparator-research-queue.json'

SPECIFIC = {
    'son-death-shore-bones-deep-water-2018-2019': {
        'priority': 'high',
        'status': 'recover-primary-artifact',
        'evidence_needed': [
            'Recover the reported painting or a dated photograph/export of it.',
            'Establish the painting date/window independently of later interpretation.',
            'Transcribe visible route, bones/skeleton and dark-water elements before applying biblical comparison.'
        ],
        'upgrade_rule': 'Do not raise strength until the visual artifact and approximate date are independently recoverable.'
    },
    'motorcycle-blood-unbroken-bones-2005': {
        'priority': 'high',
        'status': 'recover-contemporaneous-record',
        'evidence_needed': [
            'Seek contemporaneous crash, hospital, dental/reconstruction, insurance, police or family documentation.',
            'Verify the no-broken-bones/major-fractures detail independently from later project retelling.',
            'Preserve the existing safety boundary: this was a dangerous crash, not evidence of invulnerability.'
        ],
        'upgrade_rule': 'Strength may rise only if the unusual medical detail is corroborated by near-contemporary evidence.'
    },
    'light-collapse-return-2003': {
        'priority': 'medium',
        'status': 'recover-earlier-attestation',
        'evidence_needed': [
            'Look for diary, message, witness recollection or other attestation closer to age sixteen.',
            'Separate the remembered sensory sequence from the later interpretation as meeting God.',
            'Keep blackout/alcohol context explicit when comparing to light/commission narratives.'
        ],
        'upgrade_rule': 'Retain as later autobiographical interpretation unless earlier attestation or corroboration is recovered.'
    },
    'earthly-father-judgment-measure-childhood': {
        'priority': 'medium',
        'status': 'recover-older-wording',
        'evidence_needed': [
            'Recover older family, diary, message or memoir wording for the father’s judgment/stone teaching.',
            'Clarify whether the remembered wording predates later biblical comparison.',
            'Keep the relation as ethical resemblance unless source direction becomes clearer.'
        ],
        'upgrade_rule': 'Do not infer biblical dependence from a later recollection of a common moral teaching.'
    },
    'son-does-what-father-would-do-childhood': {
        'priority': 'medium',
        'status': 'recover-older-wording',
        'evidence_needed': [
            'Recover an earlier source for the childhood decision rule about doing what the father would do.',
            'Distinguish ordinary parental imitation from the later Father/Son theological architecture.',
            'Document when the John-style Father/Son comparison was first made.'
        ],
        'upgrade_rule': 'Keep Level B unless earlier wording and later comparison chronology can be separated cleanly.'
    },
    'crucify-me-hesitation-trial-neighbor-2017': {
        'priority': 'high',
        'status': 'recover-original-message',
        'evidence_needed': [
            'Recover the original 2017 chat/message/log containing the crucify-me challenge and response if possible.',
            'Verify exact wording, participants and date before using trial/Passion sequencing strongly.',
            'Keep later lolcow/martyr interpretation separate from what the original exchange itself establishes.'
        ],
        'upgrade_rule': 'Original or near-contemporary message evidence is required before promoting this beyond later reconstructed narrative.'
    }
}


def generic_task(row: dict, assessment: dict) -> dict:
    reasons = assessment.get('research_reasons', [])
    needs = []
    status = 'hold-provisional'
    priority = 'low'
    if 'project-evidence-gap' in reasons or 'low-strength' in reasons:
        needs.append('Recover stronger project-side primary or near-contemporary evidence before promotion.')
        status = 'recover-project-evidence'
        priority = 'high' if row.get('strength') in (1, 2) else 'medium'
    if 'biblical-context-gap' in reasons:
        needs.append('Expand the full biblical passage/scene context before interpreting the comparison.')
    if 'boundary-gap' in reasons:
        needs.append('Add explicit counterpressure and a maximum defensible claim.')
    if 'interpretation-gap' in reasons:
        needs.append('Add why-it-matters only after the evidentiary status is clear; prose must not substitute for stronger evidence.')
    if not needs:
        needs.append('Hold provisional until a concrete evidence upgrade path is identified.')
    return {
        'priority': priority,
        'status': status,
        'evidence_needed': needs,
        'upgrade_rule': 'Do not upgrade evidentiary strength solely because contextual prose becomes more complete.'
    }


def build_queue(rows: list[dict], scenes: list[dict]) -> dict:
    report = build_report(rows, scenes)
    by_id = {row.get('id'): row for row in rows}
    queue = []
    for assessment in report['relations']:
        if assessment.get('recommended_action') != 'research':
            continue
        rid = assessment['id']
        row = by_id[rid]
        plan = SPECIFIC.get(rid, generic_task(row, assessment))
        queue.append({
            'relation_id': rid,
            'date': row.get('date'),
            'strength': row.get('strength'),
            'dossier_level': row.get('dossier_level'),
            'owners': row.get('owners', []),
            'research_reasons': assessment.get('research_reasons', []),
            'missing': assessment.get('missing', []),
            **plan,
        })
    rank = {'high': 0, 'medium': 1, 'low': 2}
    queue.sort(key=lambda item: (rank.get(item['priority'], 9), str(item.get('date') or ''), item['relation_id']))
    return {
        'id': 'bible-comparator-research-queue',
        'version': '1.0.0',
        'updated': '2026-09-14',
        'purpose': 'Evidence-recovery queue for comparator relations that should remain provisional until stronger project-side attestation is recovered.',
        'policy': 'Contextual completeness must never be used as a substitute for evidentiary strength. Low-strength autobiographical parallels remain provisional until their stated upgrade rule is satisfied.',
        'research_relation_count': len(queue),
        'items': queue,
    }


def main() -> int:
    manifest = load_manifest(ROOT)
    queue = build_queue(assemble_relations(ROOT, manifest), assemble_scenes(ROOT, manifest))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Bible comparator research queue: {queue['research_relation_count']} provisional relations")
    for item in queue:
        print(f"- {item['priority']}: {item['relation_id']} -> {item['status']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
