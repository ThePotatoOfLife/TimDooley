#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from bible_corpus import assemble_relations, assemble_scenes, load_manifest
from bible_excavation import build_report

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'knowledge'/'indexes'/'bible-comparator-excavation.json'

def main()->int:
    manifest=load_manifest(ROOT)
    report=build_report(assemble_relations(ROOT,manifest),assemble_scenes(ROOT,manifest),str(manifest.get('version') or ''))
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"BIBLE COMPARATOR EXCAVATION BUILT: {report['relation_count']} relations; mine_next={len(report['mine_next'])}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
