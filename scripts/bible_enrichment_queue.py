from __future__ import annotations

WEIGHTS={
  'why_it_matters':100,
  'supported_conclusion':90,
  'counterpressure':85,
  'project_sequence':75,
  'biblical_sequence':75,
  'source_direction':70,
  'bible_refs':65,
  'project_side':60,
}


def score_missing(missing):
    return sum(WEIGHTS.get(key,40) for key in missing)


def build_enrichment_queue(report:dict, rows:list[dict])->dict:
    by_id={row.get('id'):row for row in rows}
    items=[]
    for assessment in report.get('relations',[]):
        if assessment.get('recommended_action')!='enrich':
            continue
        rid=assessment.get('id')
        row=by_id.get(rid,{})
        missing=list(assessment.get('missing') or [])
        score=score_missing(missing)
        items.append({
          'relation_id':rid,
          'strength':assessment.get('strength'),
          'dossier_level':assessment.get('dossier_level'),
          'owners':row.get('owners',[]),
          'missing':missing,
          'priority_score':score,
          'priority':'high' if score>=150 else 'medium' if score>=80 else 'low',
          'status':'reader-enrichment',
        })
    items.sort(key=lambda item:(-item['priority_score'],-int(item.get('strength') or 0),str(item.get('relation_id') or '')))
    return {
      'id':'bible-comparator-enrichment-queue',
      'version':'1.0.0',
      'updated':'2026-09-14',
      'purpose':'Deterministic reader-enrichment queue for already-strong comparator relations with incomplete reader-critical fields.',
      'enrichment_relation_count':len(items),
      'items':items,
    }
