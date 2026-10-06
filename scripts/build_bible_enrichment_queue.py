#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from bible_corpus import assemble_relations, assemble_scenes, load_manifest
from build_bible_comparator_quality import build_report
from bible_enrichment_queue import build_enrichment_queue

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'knowledge'/'indexes'/'bible-comparator-enrichment-queue.json'


def main()->int:
    manifest=load_manifest(ROOT)
    rows=assemble_relations(ROOT,manifest)
    scenes=assemble_scenes(ROOT,manifest)
    report=build_report(rows,scenes)
    queue=build_enrichment_queue(report,rows)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(queue,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"BIBLE COMPARATOR ENRICHMENT QUEUE BUILT: {queue['enrichment_relation_count']} relations")
    for item in queue['items'][:10]:
        print(f"- {item['priority']}: {item['relation_id']} -> {', '.join(item['missing'])}")
    return 0


if __name__=='__main__':
    raise SystemExit(main())
