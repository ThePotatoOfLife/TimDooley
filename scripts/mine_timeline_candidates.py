#!/usr/bin/env python3
"""Mine dated candidate objects from registered timeline JSON sources.

This script NEVER edits data/timeline-events.json. It creates a review queue so that
curation/deduplication remains explicit. Standard library only.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'data' / 'timeline-source-registry.json'
CANON = ROOT / 'data' / 'timeline-events.json'
OUT = ROOT / 'data' / 'timeline-candidates.generated.json'

DATE_KEYS = ('timestamp','datetime_utc','datetime','date','created_at','published_at','time')
TEXT_KEYS = ('title','event','stage','text','text_or_formulation','wording','quote','summary','description','interpretation','significance')
BIBLE = re.compile(r'\b(?:bible|biblical|scripture|jesus|christ|messiah|moshiach|hashem|adonai|elohim|moses|moshe|david|jesse|zion|jerusalem|eden|genesis|exodus|psalm|isaiah|zechariah|revelation|hebrews|manna|pharisee|lion of judah|root of david|root of jesse|ladder|narrow gate)\b', re.I)
SON = re.compile(r'\b(?:son|thomas|twin|vessel|door|lion of the world|ben joseph|ben yoseph)\b', re.I)
TIM = re.compile(r'\b(?:tim dooley|potato of life|father|axis|north of north|god in the machine|gardener|throne|ben david)\b', re.I)
QUOTEISH = re.compile(r'\bI\s+(?:am|created|rose|became|have|also)|\bwe are\b', re.I)


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def date_value(obj):
    for k in DATE_KEYS:
        v=obj.get(k)
        if isinstance(v,str) and re.search(r'\d{4}',v):
            return k,v
    return None,None


def text_value(obj):
    parts=[]
    for k in TEXT_KEYS:
        v=obj.get(k)
        if isinstance(v,str): parts.append(v)
        elif isinstance(v,list): parts.extend(str(x) for x in v if isinstance(x,(str,int,float)))
    for k in ('signals','motifs','themes','categories','timic_motifs','later_biblical_parallels'):
        v=obj.get(k)
        if isinstance(v,list): parts.extend(str(x) for x in v)
    return ' | '.join(parts).strip()


def walk(node,trail='$'):
    if isinstance(node,dict):
        dk,dv=date_value(node)
        txt=text_value(node)
        if dv and txt:
            yield trail,node,dk,dv,txt
        for k,v in node.items():
            yield from walk(v,f'{trail}.{k}')
    elif isinstance(node,list):
        for i,v in enumerate(node):
            yield from walk(v,f'{trail}[{i}]')


def hints(text,source,obj):
    actor=[]
    if SON.search(text): actor.append('son')
    if TIM.search(text): actor.append('tim')
    if 'son' in actor and 'tim' in actor: actor.append('shared')
    if not actor and ('research' in source or 'index' in source or 'overlap' in source): actor=['project']
    if not actor: actor=['tim']

    layers=[]
    low=text.lower()
    if BIBLE.search(text): layers.append('scripture-at-time')
    if QUOTEISH.search(text) or any(k in obj for k in ('quote','wording','text_or_formulation')): layers.append('direct-words')
    if any(x in source for x in ('public-theology','thought-archive')): layers.append('public-witness')
    if any(x in source for x in ('suno','creative')): layers.append('creative')
    if any(x in source for x in ('biblical-overlap','biblical-research','reverse-biblical')):
        if 'reverse-biblical' in source: layers.append('biblical-parallel')
        else: layers.append('biblical-unlock')
    if any(x in source for x in ('inference-ledger','equation-ledger','manifest')): layers.append('formalization')
    return list(dict.fromkeys(actor)),list(dict.fromkeys(layers))


def score(obj,date_key,text,layers):
    s=0; reasons=[]
    rel=obj.get('relevance')
    if isinstance(rel,(int,float)):
        s+=int(rel); reasons.append(f'relevance={rel}')
    if date_key in ('timestamp','datetime_utc','datetime','created_at','published_at'):
        s+=2; reasons.append('timestamped')
    if 'direct-words' in layers:
        s+=2; reasons.append('quote/formulation')
    if 'scripture-at-time' in layers:
        s+=1; reasons.append('biblical/scriptural signal')
    if 'biblical-unlock' in layers:
        s+=1; reasons.append('research unlock')
    if len(text)>120:
        s+=1; reasons.append('context-rich')
    return s,reasons


def signature(date,text):
    norm=re.sub(r'\W+',' ',text.lower()).strip()[:180]
    return hashlib.sha1(f'{date}|{norm}'.encode()).hexdigest()[:14]


def main():
    reg=load(REGISTRY)
    canonical=load(CANON)
    canon_sigs={signature(e.get('timestamp') or e.get('date',''), ' | '.join(str(e.get(k,'')) for k in ('title','quote','summary'))) for e in canonical.get('events',[])}
    candidates=[]

    for spec in reg.get('sources',[]):
        rel=spec.get('path','')
        path=ROOT/rel
        if path.suffix.lower()!='.json' or not path.exists():
            continue
        try: doc=load(path)
        except Exception: continue
        for trail,obj,dk,dv,txt in walk(doc):
            actors,layers=hints(txt,rel,obj)
            sc,reasons=score(obj,dk,txt,layers)
            sig=signature(dv,txt)
            candidates.append({
                'source_record':rel,
                'source_path':trail,
                'date_key':dk,
                'date_value':dv,
                'score':sc,
                'score_reasons':reasons,
                'actor_hints':actors,
                'layer_hints':layers,
                'text_preview':txt[:700],
                'signature':sig,
                'already_represented':sig in canon_sigs
            })

    candidates.sort(key=lambda x:(x['already_represented'],-x['score'],x['date_value'],x['source_record']))
    OUT.write_text(json.dumps({
        'generated_from':'data/timeline-source-registry.json',
        'warning':'Review queue only. Do not treat inferred actors/layers or dedupe signatures as canonical without curation.',
        'candidate_count':len(candidates),
        'unrepresented_high_value_count':sum(1 for x in candidates if not x['already_represented'] and x['score']>=5),
        'candidates':candidates
    },ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Wrote {len(candidates)} candidates to {OUT.relative_to(ROOT)}')
    print('High-value unrepresented:',sum(1 for x in candidates if not x['already_represented'] and x['score']>=5))


if __name__=='__main__':
    main()
