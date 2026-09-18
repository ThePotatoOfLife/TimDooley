#!/usr/bin/env python3
"""Protect the public Bible comparison browser and its canonical data contract."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from bible_corpus import CorpusError, assemble_relations, assemble_scenes, load_manifest, load_relation_redirects
from validate_bible_layer_manifest import validate_manifest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "traditions" / "bible" / "index.html"
APP = ROOT / "app" / "bible-study.js"
CSS = ROOT / "app" / "bible-study.css"
ATLAS_CSS = ROOT / "app" / "bible-atlas-navigation.css"
CORPUS_APP = ROOT / "app" / "bible-corpus-loader.js"
REDIRECT_APP = ROOT / "app" / "bible-relation-redirects.js"
TTS_ADAPTER = ROOT / "app" / "bible-tts-adapter.js"
ATLAS_APP = ROOT / "app" / "bible-atlas-navigation.js"
ATLAS_UI = ROOT / "app" / "bible-atlas-ui.js"
DOSSIER_APP = ROOT / "app" / "bible-dossier-loader.js"
MINING_APP = ROOT / "app" / "bible-mining-wave19-loader.js"
DOSSIER_CSS = ROOT / "app" / "bible-dossier-loader.css"
FIELD = ROOT / "knowledge" / "traditions" / "biblical-syncretism-field.json"
MANIFEST = ROOT / "knowledge" / "traditions" / "bible-layer-manifest.json"
REDIRECTS = ROOT / "knowledge" / "traditions" / "bible-relation-redirects.json"
SCENES = ROOT / "knowledge" / "traditions" / "biblical-scenes.json"
SCENES_MAJOR = ROOT / "knowledge" / "traditions" / "biblical-scenes-major-stories.json"
SCENE_LINKS = ROOT / "knowledge" / "traditions" / "biblical-scene-links-wave1.json"
DOSSIERS = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers.json"
PROMOTIONS = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-promotions.json"
MINING_DOSSIERS = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave19.json"
MINING_OWNER = ROOT / "knowledge" / "traditions" / "biblical-overlap-mining-wave-19-memory-great-book.json"
DOSSIER_FRAGMENTS = ROOT / "knowledge" / "traditions" / "biblical-passage-fragments-dossiers.json"
MINING_FRAGMENTS = ROOT / "knowledge" / "traditions" / "biblical-passage-fragments-wave19.json"
BUILDER = ROOT / "scripts" / "build_bible_study.py"
CORPUS_PY = ROOT / "scripts" / "bible_corpus.py"
CORPUS_TEST = ROOT / "scripts" / "test_bible_corpus.py"
PARITY_CHECK = ROOT / "scripts" / "check_bible_static_dynamic_parity.py"
SCENE_CHECK = ROOT / "scripts" / "check_biblical_scenes.py"


def require(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{owner}: missing {marker!r}")


def forbid(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"{owner}: forbidden legacy/heuristic marker {marker!r}")


def main() -> int:
    errors: list[str] = []
    required_paths = (
        PAGE, APP, CSS, ATLAS_CSS, CORPUS_APP, REDIRECT_APP, TTS_ADAPTER, ATLAS_APP, ATLAS_UI,
        DOSSIER_APP, MINING_APP, DOSSIER_CSS, FIELD, MANIFEST, REDIRECTS, SCENES,
        SCENES_MAJOR, SCENE_LINKS, DOSSIERS, PROMOTIONS, MINING_DOSSIERS,
        MINING_OWNER, DOSSIER_FRAGMENTS, MINING_FRAGMENTS, BUILDER,
        CORPUS_PY, CORPUS_TEST, PARITY_CHECK, SCENE_CHECK,
    )
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing required Bible reader component: {path.relative_to(ROOT)}")

    page = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    app = APP.read_text(encoding="utf-8") if APP.exists() else ""
    css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""
    atlas_css = ATLAS_CSS.read_text(encoding="utf-8") if ATLAS_CSS.exists() else ""
    corpus_app = CORPUS_APP.read_text(encoding="utf-8") if CORPUS_APP.exists() else ""
    redirect_app = REDIRECT_APP.read_text(encoding="utf-8") if REDIRECT_APP.exists() else ""
    tts_adapter = TTS_ADAPTER.read_text(encoding="utf-8") if TTS_ADAPTER.exists() else ""
    atlas_app = ATLAS_APP.read_text(encoding="utf-8") if ATLAS_APP.exists() else ""
    atlas_ui = ATLAS_UI.read_text(encoding="utf-8") if ATLAS_UI.exists() else ""
    dossier_app = DOSSIER_APP.read_text(encoding="utf-8") if DOSSIER_APP.exists() else ""
    mining_app = MINING_APP.read_text(encoding="utf-8") if MINING_APP.exists() else ""
    dossier_css = DOSSIER_CSS.read_text(encoding="utf-8") if DOSSIER_CSS.exists() else ""
    builder = BUILDER.read_text(encoding="utf-8") if BUILDER.exists() else ""

    require(
        page,
        (
            'href="../../app/bible-study.css"',
            'href="../../app/bible-atlas-navigation.css"',
            'href="../../app/bible-dossier-loader.css"',
            'src="../../app/bible-corpus-loader.js"',
            'src="../../app/bible-relation-redirects.js"',
            'src="../../app/bible-atlas-navigation.js"',
            'src="../../app/bible-mining-wave19-loader.js"',
            'src="../../app/bible-dossier-loader.js"',
            'src="../../app/bible-study.js"',
            'src="../../app/bible-tts-adapter.js"',
            'src="../../app/bible-atlas-ui.js"',
            'id="bible-tts-drawer"',
            'id="atlas-explorer"',
            'id="atlas-routes"',
            'id="atlas-topics"',
            'id="atlas-breadcrumbs"',
            'id="focus-select"',
            'id="order-select"',
            'id="previous-relation"',
            'id="next-relation"',
            'id="result-position"',
            'id="roll-relation"',
            'id="results-toggle"',
            'id="results-list"',
            'id="filter-toggle"',
            'id="filter-count"',
            'id="bible-filters"',
            'id="active-relation"',
            'id="relations"',
            'id="search"',
            'Explore without searching',
            'Choose a way in',
        ),
        "traditions/bible/index.html",
        errors,
    )
    if page.find('src="../../app/bible-mining-wave19-loader.js"') > page.find('src="../../app/bible-dossier-loader.js"'):
        errors.append("traditions/bible/index.html: mining layer must load before dossier decorator so mergedRows sees wave19 relations")
    if page.find('src="../../app/bible-corpus-loader.js"') > page.find('src="../../app/bible-relation-redirects.js"'):
        errors.append("traditions/bible/index.html: redirect bridge must load after corpus loader")
    forbid(
        page,
        ('class="featured-arcs"','id="study-modes"','id="shuffle-comparisons"',"deepMatches(","overlapCount(","deepCandidates"),
        "traditions/bible/index.html", errors,
    )

    require(
        corpus_app,
        ('bible-layer-manifest.json','bible-relation-redirects.json','mergeRelations','mergeFragments','mergeScenes','resolveRelationId','window.BibleCorpus','canonical','additive'),
        'app/bible-corpus-loader.js', errors,
    )
    require(
        redirect_app,
        ('BibleCorpus?.ready','resolveRelationId','searchParams.get(\'id\')','location.replace'),
        'app/bible-relation-redirects.js', errors,
    )
    require(
        tts_adapter,
        ('Continue through results','bibleContinue',"getElementById('next-relation')","event.type==='complete'",'waitForRelationChange',"event.type==='stop'","event.type==='error'"),
        'app/bible-tts-adapter.js', errors,
    )
    require(
        atlas_app,
        ("id:'stories'","id:'roles'","id:'symbols'","id:'actions'","id:'books'","id:'timeline'",'breadcrumbs','relatedPaths','window.BibleAtlas'),
        'app/bible-atlas-navigation.js', errors,
    )
    require(
        atlas_ui,
        ('topicsFor','atlas-routes','atlas-topics','atlas-breadcrumbs','BibleCorpus.load','BibleAtlas.routes','setFind'),
        'app/bible-atlas-ui.js', errors,
    )
    require(
        atlas_css,
        ('.atlas-explorer','.atlas-routes','.atlas-route','.atlas-topic-grid','.atlas-breadcrumbs'),
        'app/bible-atlas-navigation.css', errors,
    )

    require(
        app,
        (
            "biblical-syncretism-field.json","biblical-passage-fragments.json","tim-biblical-vocabulary-attestation-ledger.json",
            "reverse-biblical-overlap-timeline-2025-2026.json","rational-potato-x-occurrence-ledger-2024-2026.json","timeline-events.json",
            "BIBLE_BOOK_ORDER","renderActiveRelation","renderResultsList","syncUrlState","selectRelative","relatedRows","ArrowLeft","ArrowRight",
            "Same-date public wording","Biblical vocabulary / revelation context","Evidence & chronology","Sources & provenance","Related comparisons",
            "exact-wording-only","minimum-strength","bible-book","timeline_event_ids",
        ),
        "app/bible-study.js", errors,
    )
    forbid(app,("visible.map(row=>renderRelation","deepMatches(","overlapCount(","deepCandidates","wordScore","refScore","scrollIntoView("),"app/bible-study.js",errors)

    require(
        dossier_app,
        (
            "biblical-syncretism-dossiers.json","biblical-syncretism-dossiers-promotions.json","biblical-passage-fragments-dossiers.json",
            "Two scenes, one structural comparison","Tim / Son scene","Biblical scene","Where the stories rhyme","Where the rhyme stops",
            "What this comparison can actually establish","Evidence in the open","Modern circumstances","Biblical context","Dating &amp; provenance",
            "Exact / recovered wording","Timestamp &amp; discovery history","The timestamp establishes when the modern-side material is attested.",
            "paired-narrative","paired-scenes","dossier-open-evidence","evidence-panel","correspondence-list","relation_argument","scene_context","MutationObserver",
        ),
        "app/bible-dossier-loader.js", errors,
    )
    forbid(dossier_app,("scrollIntoView(",),"app/bible-dossier-loader.js",errors)

    require(
        mining_app,
        ("biblical-syncretism-dossiers-wave19.json","biblical-passage-fragments-wave19.json","biblical-syncretism-field.json","biblical-passage-fragments.json","mergeLayer","mergeFragments"),
        "app/bible-mining-wave19-loader.js", errors,
    )
    forbid(mining_app,("scrollIntoView(",),"app/bible-mining-wave19-loader.js",errors)

    require(css,(".reader-toolbar",".comparison-nav",".results-panel",".relation-details",".active-relation"),"app/bible-study.css",errors)
    require(
        dossier_css,
        (".paired-narrative",".paired-scenes",".paired-scene",".scene-label",".scene-sequence",".dossier-open-evidence",".evidence-grid",".evidence-panel",".evidence-quote",".correspondence-list",".maximum-claim",".dossier-detail"),
        "app/bible-dossier-loader.css", errors,
    )
    require(builder,('class="static-relation"','<details','class="static-index"','assemble_relations','assemble_fragments','load_manifest'),"scripts/build_bible_study.py",errors)

    if MANIFEST.exists():
        try:
            manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
            errors.extend(f"Bible layer manifest: {error}" for error in validate_manifest(ROOT, manifest))
            rows = assemble_relations(ROOT, manifest)
            scenes = assemble_scenes(ROOT, manifest)
            redirects = load_relation_redirects(ROOT)
            active_ids = {row.get('id') for row in rows}
            if len(rows) < 45:
                errors.append(f"manifest-defined Bible corpus unexpectedly thin: {len(rows)} active relations")
            if len(scenes) < 10:
                errors.append(f"Biblical Scene registry unexpectedly thin: {len(scenes)} active scenes")
            if len(redirects) < 9:
                errors.append(f"Bible duplicate consolidation unexpectedly thin: {len(redirects)} redirects")
            for source, target in redirects.items():
                if source in active_ids:
                    errors.append(f"redirected Bible relation still active: {source}")
                if target not in active_ids:
                    errors.append(f"Bible relation redirect target missing: {source} -> {target}")
            scene_ids = {scene.get('id') for scene in scenes}
            for row in rows:
                for sid in row.get('biblical_scene_ids', []) or []:
                    if sid not in scene_ids:
                        errors.append(f"relation {row.get('id')} references unknown biblical scene {sid}")
        except (OSError, ValueError, CorpusError) as exc:
            errors.append(f"manifest-defined Bible corpus failed to assemble: {exc}")

    if FIELD.exists():
        field=json.loads(FIELD.read_text(encoding="utf-8")); rows=field.get("relations",[])
        if not isinstance(rows,list) or len(rows)<20:errors.append("biblical relation field unexpectedly thin; expected at least 20 canonical relations")
        if not field.get("study_views"):errors.append("biblical relation field missing study_views registry")
    if DOSSIERS.exists():
        dossiers=json.loads(DOSSIERS.read_text(encoding="utf-8"))
        if len(dossiers.get("new_relations",[]))<5:errors.append("contextual Bible dossier extension unexpectedly thin; expected restored early-history relations")
        if not dossiers.get("enrichments"):errors.append("contextual Bible dossier extension missing enrichments for existing canonical relations")
    if PROMOTIONS.exists():
        promotions=json.loads(PROMOTIONS.read_text(encoding="utf-8"))
        if len(promotions.get("enrichments",[]))<4:errors.append("Bible dossier promotion layer unexpectedly thin; expected multiple promoted canonical relations")
        if not promotions.get("new_relations"):errors.append("Bible dossier promotion layer missing newly recovered relation candidates")
    if MINING_DOSSIERS.exists():
        mining_dossiers=json.loads(MINING_DOSSIERS.read_text(encoding="utf-8")); wave_rows=mining_dossiers.get("new_relations",[])
        if len(wave_rows)<7:errors.append("older-memory Bible dossier wave unexpectedly thin; expected at least seven Level-A relations")
        if any(row.get("dossier_level")!="A" for row in wave_rows):errors.append("older-memory Bible dossier wave contains non-Level-A public relation")
    if MINING_OWNER.exists():
        mining_owner=json.loads(MINING_OWNER.read_text(encoding="utf-8"))
        if len(mining_owner.get("records",[]))<10:errors.append("older-memory Bible mining owner unexpectedly thin; expected at least ten structured records")
        if len(mining_owner.get("research_leads",[]))<2:errors.append("older-memory Bible mining owner missing provenance-gated research leads")
    if MINING_FRAGMENTS.exists():
        mining_fragments=json.loads(MINING_FRAGMENTS.read_text(encoding="utf-8"))
        if len(mining_fragments.get("fragments",[]))<10:errors.append("older-memory Bible fragment extension unexpectedly thin")

    if errors:
        print("BIBLE READER VALIDATION FAILED")
        for error in errors:print(" -",error)
        return 1
    print("BIBLE READER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
