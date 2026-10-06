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
LIBRARY_CSS = ROOT / "app" / "bible-library.css"
LIBRARY_APP = ROOT / "app" / "bible-library.js"
CORPUS_APP = ROOT / "app" / "bible-corpus-loader.js"
REDIRECT_APP = ROOT / "app" / "bible-relation-redirects.js"
TTS_ADAPTER = ROOT / "app" / "bible-tts-adapter.js"
ATLAS_APP = ROOT / "app" / "bible-atlas-navigation.js"
ATLAS_UI = ROOT / "app" / "bible-atlas-ui.js"
DOSSIER_APP = ROOT / "app" / "bible-dossier-loader.js"
MINING_APP = ROOT / "app" / "bible-mining-wave19-loader.js"
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
CHRISTIANITY_INDEX = ROOT / "data" / "christianity" / "index.json"
KJV_CATALOG = ROOT / "data" / "christianity" / "bible-kjv.json"
WEB_BOOK_INDEX = ROOT / "data" / "sources" / "bible-web-book-index.json"
NARRATIVE_WAVE = ROOT / "knowledge" / "traditions" / "biblical-syncretism-dossiers-wave41.json"


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
        PAGE, APP, CSS, ATLAS_CSS, LIBRARY_CSS, LIBRARY_APP, CORPUS_APP, REDIRECT_APP, TTS_ADAPTER, ATLAS_APP, ATLAS_UI,
        DOSSIER_APP, MINING_APP, FIELD, MANIFEST, REDIRECTS, SCENES,
        SCENES_MAJOR, SCENE_LINKS, DOSSIERS, PROMOTIONS, MINING_DOSSIERS,
        MINING_OWNER, DOSSIER_FRAGMENTS, MINING_FRAGMENTS, BUILDER,
        CORPUS_PY, CORPUS_TEST, PARITY_CHECK, SCENE_CHECK, CHRISTIANITY_INDEX, KJV_CATALOG, WEB_BOOK_INDEX, NARRATIVE_WAVE,
    )
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing required Bible reader component: {path.relative_to(ROOT)}")

    page = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    app = APP.read_text(encoding="utf-8") if APP.exists() else ""
    css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""
    atlas_css = ATLAS_CSS.read_text(encoding="utf-8") if ATLAS_CSS.exists() else ""
    library_css = LIBRARY_CSS.read_text(encoding="utf-8") if LIBRARY_CSS.exists() else ""
    library_app = LIBRARY_APP.read_text(encoding="utf-8") if LIBRARY_APP.exists() else ""
    corpus_app = CORPUS_APP.read_text(encoding="utf-8") if CORPUS_APP.exists() else ""
    redirect_app = REDIRECT_APP.read_text(encoding="utf-8") if REDIRECT_APP.exists() else ""
    tts_adapter = TTS_ADAPTER.read_text(encoding="utf-8") if TTS_ADAPTER.exists() else ""
    atlas_app = ATLAS_APP.read_text(encoding="utf-8") if ATLAS_APP.exists() else ""
    atlas_ui = ATLAS_UI.read_text(encoding="utf-8") if ATLAS_UI.exists() else ""
    dossier_app = DOSSIER_APP.read_text(encoding="utf-8") if DOSSIER_APP.exists() else ""
    mining_app = MINING_APP.read_text(encoding="utf-8") if MINING_APP.exists() else ""
    builder = BUILDER.read_text(encoding="utf-8") if BUILDER.exists() else ""

    require(
        page,
        (
            'href="../../app/bible-study.css"',
            'href="../../app/bible-library.css"',
            'href="../../app/bible-atlas-navigation.css"',
            'src="../../app/bible-corpus-loader.js"',
            'src="../../app/bible-relation-redirects.js"',
            'src="../../app/bible-atlas-navigation.js"',
            'src="../../app/bible-mining-wave19-loader.js"',
            'src="../../app/bible-dossier-loader.js"',
            'src="../../app/bible-study.js"',
            'src="../../app/bible-tts-adapter.js"',
            'src="../../app/bible-atlas-ui.js"',
            'src="../../app/bible-scripture-reader.js"',
            'src="../../app/bible-library.js"',
            'id="bible-tts-drawer"',
            'id="bible-library"',
            'id="bible-library-groups"',
            'id="bible-book-grid"',
            'id="bible-library-reader"',
            'id="bible-reference-form"',
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
            'class="reader-toolbar"',
            'id="tim-son-story"',
            'id="story-arcs"',
            'class="identity-keys"',
            'The Son / human vessel',
            'Persona death → meme death → Tim / Potato',
            'Father / Ladder realization',
            '1999 · age 12</time><strong>Jesus enters the conscious vocabulary',
            '2003 · age 16</time><strong>Collapse → light → return',
            '2005 · age 18</time><strong>Crash &amp; reconstruction',
            '2016</time><strong>Prison recognition',
            '2017</time><strong>Crucifixion declaration',
            'jesus-son-research-index.json',
            'son-jesus-longitudinal-christology-atlas.json',
            'son-jesus-passion-detention-overlap-atlas.json',
            'chapter-24-jesus-parallel-atlas.json',
            '2019–20</time><strong>Meme death &amp; seed',
            '2021–2024</time><strong>Hidden Potato → public identity',
            'Return becomes staged recognition',
            'Four hinges prevent the story from collapsing into one biography',
            'Seven arcs carry the Tim / Son Bible story',
            '6 Oct 2024 · public Potato identity',
            'focus=view:core&order=story&id=christian-vocabulary-enters-age12-1999',
            'focus=view:core&order=story&id=potato-birth-hidden-life-2020-12-25',
            'focus=view:core&order=story&id=emmaus-return-before-recognition-bread',
        ),
        "traditions/bible/index.html",
        errors,
    )
    compare_pos = page.find('id="compare"')
    study_pos = page.find('id="study-tool"')
    toolbar_pos = page.find('class="reader-toolbar"')
    chronology_pos = page.find('id="tim-son-story"')
    if not (0 <= study_pos < compare_pos < toolbar_pos < chronology_pos):
        errors.append("traditions/bible/index.html: comparator must flow directly into Tim/Son chronology")
    story_slice = page[chronology_pos:page.find('id="prophetic-unity"', chronology_pos)] if chronology_pos >= 0 else ""
    if "order=story&q=" in story_slice:
        errors.append("traditions/bible/index.html: Tim/Son story spine must use stable relation ids, not AND-query navigation")
    if page.find('src="../../app/bible-mining-wave19-loader.js"') > page.find('src="../../app/bible-dossier-loader.js"'):
        errors.append("traditions/bible/index.html: mining layer must load before dossier decorator so mergedRows sees wave19 relations")
    if page.find('src="../../app/bible-corpus-loader.js"') > page.find('src="../../app/bible-relation-redirects.js"'):
        errors.append("traditions/bible/index.html: redirect bridge must load after corpus loader")
    if page.find('src="../../app/bible-scripture-reader.js"') > page.find('src="../../app/bible-library.js"'):
        errors.append("traditions/bible/index.html: scripture reader must load before Bible library adapter")
    forbid(
        page,
        ('class="featured-arcs"','id="study-modes"','id="shuffle-comparisons"','class="comparison-masthead"','class="story-first"',
         'bible-witness-loader.js','bible-scene-reader.js','bible-dossier-loader.css',
         "deepMatches(","overlapCount(","deepCandidates"),
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
        library_app,
        (
            "data/christianity/bible-kjv.json","bible-web-book-index.json","libraryBook","libraryChapter",
            "Torah / Pentateuch","KJV Apocrypha","Hebrews & General Letters","BibleScriptureReader",
            "bible-reference-form","WEB text unavailable",
        ),
        "app/bible-library.js", errors,
    )
    require(
        library_css,
        ('.bible-library','.bible-library-groups','.bible-book-grid','.bible-library-reader','.scripture-dialog','.scripture-verse'),
        'app/bible-library.css', errors,
    )

    forbid(
        library_app,
        ("bible:relation-reference", "function relationReference", "relationReference("),
        "app/bible-library.js",
        errors,
    )

    require(
        app,
        (
            "biblical-syncretism-field.json","biblical-passage-fragments.json","tim-biblical-vocabulary-attestation-ledger.json",
            "reverse-biblical-overlap-timeline-2025-2026.json","rational-potato-x-occurrence-ledger-2024-2026.json","timeline-events.json",
            "BIBLE_BOOK_ORDER","renderActiveRelation","renderResultsList","syncUrlState","selectRelative","relatedRows","ArrowLeft","ArrowRight",
            "Same-date public wording","Biblical vocabulary / revelation context","Evidence, chronology & open gaps","Technical detail & provenance","Related comparisons",
            "Tim / Son source","Bible source","Archive grounding","What it later becomes","project_sequence",
            "exact-wording-only","minimum-strength","bible-book","timeline_event_ids","TIM_LIVED_ACTORS",
            "view==='tim-lived'","childhood-cultivation-gardener-precursor-1992","christian-vocabulary-enters-age12-1999",
            "potato-birth-hidden-life-2020-12-25","emmaus-return-before-recognition-bread","john21-shore-recognition-feeding-after-return",
            "biblicalSequence","correspondences","maximumClaim","scriptureContextItems","comparison-sequences","Points of contact","How far this comparison can go",
            "readerNarrative","readerResonance","Spudlight reading","data-scripture-ref","BibleScriptureReader?.openReference","reading-rail","source-pair","technical-grid",
            "readerScene","chronicle-scene","The scene","source-grounded narrative reconstruction","Under the biblical light",
            "readerSequence","continuous-sequence","Continuous reading","Reading result","sequence-ref",
            "result-preview","result-tags","hasScene","hasSequence",
        ),
        "app/bible-study.js", errors,
    )
    forbid(
        app,
        (
            "visible.map(row=>renderRelation","deepMatches(","overlapCount(","deepCandidates","wordScore","refScore","scrollIntoView(",
            "url.searchParams.set('libraryBook'","url.searchParams.set('libraryChapter'","state.focus='view:all'","bible:relation-reference",
            '<section class="side project-side"><h3>Tim / Son / project</h3></section>',
        ),
        "app/bible-study.js",
        errors,
    )

    require(
        dossier_app,
        (
            "biblical-syncretism-dossiers.json","biblical-syncretism-dossiers-promotions.json","biblical-passage-fragments-dossiers.json",
            "relation_argument","mergeField","mergeFragments","window.fetch",
        ),
        "app/bible-dossier-loader.js", errors,
    )
    forbid(
        dossier_app,
        ("MutationObserver","active-relation","paired-narrative","dossier-open-evidence","scrollIntoView("),
        "app/bible-dossier-loader.js",
        errors,
    )

    require(
        mining_app,
        ("biblical-syncretism-dossiers-wave19.json","biblical-passage-fragments-wave19.json","biblical-syncretism-field.json","biblical-passage-fragments.json","mergeLayer","mergeFragments"),
        "app/bible-mining-wave19-loader.js", errors,
    )
    forbid(mining_app,("scrollIntoView(",),"app/bible-mining-wave19-loader.js",errors)

    require(css,(".reader-toolbar",".comparison-nav",".results-panel",".relation-details",".active-relation",".comparison-sequences",".comparison-sequence",".contact-points",".maximum-claim",".scripture-context",".spudlight-reading",".source-pair",".reading-rail",".story-pair",".interpretation-pair",".technical-grid",".scripture-ref-button",".chronicle-scene",".chronicle-beat",".continuous-sequence",".continuous-step",".continuous-sequence-conclusion"),"app/bible-study.css",errors)
    require(builder,('class="static-relation"','<details','class="static-index"','assemble_relations','assemble_fragments','load_manifest','Archive grounding','Why this matters / what it later becomes','project_sequence_html','reader_scene','reader_sequence','static-chronicle','static-continuous-sequence','project_quote','public_wording'),"scripts/build_bible_study.py",errors)

    if MANIFEST.exists():
        try:
            manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
            errors.extend(f"Bible layer manifest: {error}" for error in validate_manifest(ROOT, manifest))
            rows = assemble_relations(ROOT, manifest)
            scenes = assemble_scenes(ROOT, manifest)
            redirects = load_relation_redirects(ROOT)
            active_ids = {row.get('id') for row in rows}
            core_story_ids = {
                'childhood-cultivation-gardener-precursor-1992',
                'christian-vocabulary-enters-age12-1999',
                'light-collapse-return-2003',
                'motorcycle-blood-unbroken-bones-2005',
                'care-home-rise-walk-witness-2009-era',
                'tree-ordeal-hanging-curse-redemption-2011',
                'yahya-john-lamb-recognition-2016',
                'crucify-me-hesitation-trial-neighbor-2017',
                'persona-death-old-new-self-2018',
                'son-meme-crucifixion-burial-2019-2020',
                'potato-birth-hidden-life-2020-12-25',
                'chosen-gentile-potato-2024-10-02',
                'potatoes-die-for-sins-2024-10-03',
                'potato-axis-turning-ladder-2025-04-21',
                'self-resurrection-witnesses-2025-09-30',
                'father-after-crucified-son-2025-12-17',
                'bread-door-tomb-resurrection-2026-04-23',
                'ladder-door-specialization-2026-05-19',
                'john14-15-house-thomas-way-gardener-vine-sequence-2026-07-23',
                'passover-house-door-lamb-threshold-2026-07-24',
                'son-cornerstone-2026-08-17',
                'psalm82-gods-sons-mosthigh-justice-test-2026-09-13',
                'emmaus-return-before-recognition-bread',
                'mary-gardener-misrecognition-return',
                'acts-forty-days-resurrection-to-ascension',
                'john21-shore-recognition-feeding-after-return',
                'oct1-father-internet-ladder-swamp',
                'oct1-prophetic-name-witness-deaf-blind',
                'oct1-jesus-dead-countertext',
            }
            missing_core = sorted(core_story_ids - active_ids)
            if missing_core:
                errors.append(f"curated Tim/Son core story is missing active relations: {missing_core}")
            core_start = app.find("const CORE_RELATION_ORDER=[")
            core_end = app.find("];", core_start)
            core_block = app[core_start:core_end] if core_start >= 0 and core_end > core_start else ""
            missing_from_runtime_core = sorted(rid for rid in core_story_ids if f"'{rid}'" not in core_block)
            if missing_from_runtime_core:
                errors.append(f"runtime Core Tim/Son order drifted from curated story: {missing_from_runtime_core}")
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

    if KJV_CATALOG.exists() and WEB_BOOK_INDEX.exists() and CHRISTIANITY_INDEX.exists():
        try:
            kjv = json.loads(KJV_CATALOG.read_text(encoding="utf-8"))
            web = json.loads(WEB_BOOK_INDEX.read_text(encoding="utf-8"))
            christianity = json.loads(CHRISTIANITY_INDEX.read_text(encoding="utf-8"))
            books = kjv.get("books", [])
            section_counts = {
                section: sum(1 for book in books if book.get("section") == section)
                for section in ("old", "apocrypha", "new")
            }
            if len(books) != 80:
                errors.append(f"KJV catalogue must contain 80 books; found {len(books)}")
            if section_counts != {"old": 39, "apocrypha": 14, "new": 27}:
                errors.append(f"KJV catalogue section counts drifted: {section_counts}")
            web_books = web.get("books", {})
            if len(web_books) != 66:
                errors.append(f"WEB reader index must contain 66 books; found {len(web_books)}")
            canonical_names = {book.get("name") for book in books if book.get("section") in {"old", "new"}}
            if canonical_names != set(web_books):
                missing = sorted(canonical_names - set(web_books))
                extra = sorted(set(web_books) - canonical_names)
                errors.append(f"KJV 66-book names and WEB reader index differ; missing={missing}, extra={extra}")
            index_text = CHRISTIANITY_INDEX.read_text(encoding="utf-8")
            if "bible.html" in index_text:
                errors.append("Christianity scripture index still references retired bible.html route")
            canonical_ids = {item.get("id") for item in christianity.get("canonical_texts", [])}
            if not {"bible-kjv", "bible-web"} <= canonical_ids:
                errors.append("Christianity scripture index must expose distinct KJV catalogue and WEB reader sources")
            routes = christianity.get("reading_routes", [])
            if not routes or any(not route.startswith("traditions/bible/") for route in routes):
                errors.append("Christianity scripture reading routes must point to traditions/bible/")
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"Bible scripture library metadata failed validation: {exc}")

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

    if NARRATIVE_WAVE.exists():
        narrative_wave=json.loads(NARRATIVE_WAVE.read_text(encoding="utf-8"))
        narrative_ids={row.get("id") for row in narrative_wave.get("new_relations",[])}
        required_narrative_ids={"christian-vocabulary-enters-age12-1999","potato-birth-hidden-life-2020-12-25"}
        if not required_narrative_ids <= narrative_ids:
            errors.append(f"Tim/Son narrative wave missing hinge relations: {sorted(required_narrative_ids - narrative_ids)}")
        enriched_ids={row.get("relation_id") for row in narrative_wave.get("enrichments",[])}
        for rid in ("light-collapse-return-2003","father-after-crucified-son-2025-12-17","oct1-jesus-dead-countertext"):
            if rid not in enriched_ids:
                errors.append(f"Tim/Son narrative wave missing core enrichment: {rid}")
        reader_voice_count=sum(1 for row in [*narrative_wave.get("new_relations",[]),*narrative_wave.get("enrichments",[])] if row.get("reader_narrative"))
        if reader_voice_count < 8:
            errors.append(f"Tim/Son narrative wave lost reverent reader voice coverage: {reader_voice_count}")
        reader_scene_count=sum(1 for row in [*narrative_wave.get("new_relations",[]),*narrative_wave.get("enrichments",[])] if row.get("reader_scene"))
        if reader_scene_count < 20:
            errors.append(f"Tim/Son narrative wave lost chronicle-scene coverage: {reader_scene_count}")
        john_sequence=next((row.get("reader_sequence") for row in [*narrative_wave.get("new_relations",[]),*narrative_wave.get("enrichments",[])] if (row.get("id") or row.get("relation_id"))=="john14-15-house-thomas-way-gardener-vine-sequence-2026-07-23"),None)
        if not john_sequence or len(john_sequence.get("steps",[])) < 10:
            errors.append("John 14-15 continuous House/Thomas/Way/Gardener sequence is missing or too thin")
        elif not any(step.get("source_type")=="limit" for step in john_sequence.get("steps",[])):
            errors.append("John 14-15 continuous sequence must retain an explicit non-overclaiming limit")
        return_sequence=next((row.get("reader_sequence") for row in [*narrative_wave.get("new_relations",[]),*narrative_wave.get("enrichments",[])] if (row.get("id") or row.get("relation_id"))=="emmaus-return-before-recognition-bread"),None)
        if not return_sequence or len(return_sequence.get("steps",[])) < 10:
            errors.append("Return/recognition sequence is missing or too thin")
        elif not any(step.get("source_type")=="limit" for step in return_sequence.get("steps",[])):
            errors.append("Return/recognition sequence must retain explicit non-overclaiming limits")
        thomas_sequence=next((row.get("reader_sequence") for row in [*narrative_wave.get("new_relations",[]),*narrative_wave.get("enrichments",[])] if (row.get("id") or row.get("relation_id"))=="thomas-twin-way-wounds-recognition"),None)
        if not thomas_sequence or len(thomas_sequence.get("steps",[])) < 15:
            errors.append("Thomas/Twin John 11-20 sequence is missing or too thin")
        else:
            refs=" ".join(step.get("ref","") for step in thomas_sequence.get("steps",[]))
            for required_ref in ("John 11:16","John 14:5-6","John 20:24-25","John 20:28"):
                if required_ref not in refs:
                    errors.append(f"Thomas/Twin continuous sequence missing required Gospel anchor: {required_ref}")
            if not any(step.get("source_type")=="project" for step in thomas_sequence.get("steps",[])):
                errors.append("Thomas/Twin sequence must retain project-source steps")
            if not any(step.get("source_type")=="limit" for step in thomas_sequence.get("steps",[])):
                errors.append("Thomas/Twin sequence must retain explicit non-overclaiming limits")
            if not any(step.get("source_type")=="reception" for step in thomas_sequence.get("steps",[])):
                errors.append("Thomas/Twin sequence must retain a clearly labeled later reception layer")
            if not any("Canonical John ends" in step.get("source_label","") for step in thomas_sequence.get("steps",[])):
                errors.append("Thomas/Twin sequence must visibly separate canonical John from later Thomasine reception")
            if not any("touch itself is not" in step.get("heading","").lower() for step in thomas_sequence.get("steps",[])):
                errors.append("Thomas/Twin sequence must preserve the John 20 touch-text precision note")
        tammuz_sequence=next((row.get("reader_sequence") for row in [*narrative_wave.get("new_relations",[]),*narrative_wave.get("enrichments",[])] if (row.get("id") or row.get("relation_id"))=="tammuz-north-gate-2026-07-31"),None)
        if not tammuz_sequence or len(tammuz_sequence.get("steps",[])) < 10:
            errors.append("Thomas/Tammuz/North-Gate source-direction sequence is missing or too thin")
        else:
            if not any(step.get("ref")=="Ezekiel 8:14" for step in tammuz_sequence.get("steps",[])):
                errors.append("Thomas/Tammuz/North-Gate sequence must retain Ezekiel 8:14")
            if not any(step.get("source_type")=="limit" for step in tammuz_sequence.get("steps",[])):
                errors.append("Thomas/Tammuz/North-Gate sequence must retain historical/geographical limits")

    if errors:
        print("BIBLE READER VALIDATION FAILED")
        for error in errors:print(" -",error)
        return 1
    print("BIBLE READER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
