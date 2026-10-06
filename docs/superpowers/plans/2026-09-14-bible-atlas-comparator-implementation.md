# Bible Atlas Comparator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the atlas-first Bible comparator architecture without breaking the existing public reader, while unifying the corpus, adding reusable biblical scenes/full-text source support, improving navigation and creating a quality/coverage-driven research pipeline.

**Architecture:** Migrate incrementally. First create one manifest and deterministic corpus assembly contract while existing loaders remain functional. Then add scene/source owners, switch static/runtime assembly to the unified loader, layer atlas navigation and story-first reading over the same relation IDs, and finally generate quality/coverage reports that drive further enrichment.

**Tech Stack:** Static HTML/CSS/JavaScript, JSON knowledge/data owners, Python build/validation scripts, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-14-bible-atlas-comparator-architecture-design.md`

## Global Constraints

- Search is secondary; primary navigation works through routes, buttons, breadcrumbs and native selects.
- Preserve existing canonical relation IDs and evidence distinctions.
- Keep exact Bible source text separate from summaries and project interpretation.
- Do not invent modern-scene detail under `date-only` or `unknown` source status.
- Countertexts, mismatch and source direction remain first-class.
- Runtime and static fallback expose the same manifest-defined active corpus.
- Research/quarantined layers do not enter the default public corpus.
- Existing public reader remains usable throughout migration.

---

### Task 1: Add the canonical Bible layer manifest

**Files:**
- Create: `knowledge/traditions/bible-layer-manifest.json`
- Create: `scripts/validate_bible_layer_manifest.py`
- Modify: `scripts/validate_bible_reader.py`

**Interfaces:**
- Produces `layers[]` entries with `id`, `kind`, `path`, `status`, `precedence`.
- Later tasks consume this manifest for relations/fragments/scenes.

- [ ] Write failing validation for manifest existence, unique layer IDs, allowed status/kind values, existing paths, integer precedence and duplicate active paths.
- [ ] Run `python scripts/validate_bible_layer_manifest.py`; expect failure before the manifest exists.
- [ ] Create the manifest registering current active relation/fragment owners and future scene/source slots.
- [ ] Run manifest validation; expect PASS.
- [ ] Wire manifest validation into `scripts/validate_bible_reader.py`.
- [ ] Commit as `feat: add canonical Bible layer manifest`.

### Task 2: Create shared deterministic corpus assembly

**Files:**
- Create: `scripts/bible_corpus.py`
- Create: `app/bible-corpus-loader.js`
- Create: `scripts/test_bible_corpus.py`
- Modify: `scripts/audit_bible_witness_coverage.py`

**Interfaces:**
- Python: `load_manifest(root)`, `assemble_relations(root, manifest)`, `assemble_fragments(root, manifest)`, `assemble_scenes(root, manifest)`.
- Browser: `window.BibleCorpus.load()` returns `{relations, fragments, scenes, manifest}`.

- [ ] Write failing tests for precedence enrichment, insertion, duplicate rejection, quarantine exclusion and fragment dedupe.
- [ ] Run `python scripts/test_bible_corpus.py`; expect failure before implementation.
- [ ] Implement Python assembly from the manifest.
- [ ] Implement browser loader with matching semantics and no UI rendering.
- [ ] Update witness audit to remove its hard-coded layer list.
- [ ] Run corpus tests and existing Bible validation; expect PASS.
- [ ] Commit as `feat: unify Bible corpus assembly`.

### Task 3: Make static build use the canonical corpus

**Files:**
- Modify: `scripts/build_bible_study.py`
- Modify: `scripts/validate_bible_reader.py`
- Create: `scripts/check_bible_static_dynamic_parity.py`

- [ ] Add a parity check comparing manifest-assembled relation IDs with the static rendered IDs.
- [ ] Run it against the current builder; expect drift/failure if active layers differ.
- [ ] Refactor `build_bible_study.py` to consume `scripts/bible_corpus.py` and remove wave-specific build globs from the active corpus path.
- [ ] Rebuild the site/Bible fallback.
- [ ] Run parity validation; expect PASS.
- [ ] Commit as `fix: unify Bible static and runtime corpus`.

### Task 4: Add the first reusable Biblical Scene registry

**Files:**
- Create: `knowledge/traditions/biblical-scenes.json`
- Create: `scripts/validate_biblical_scenes.py`
- Modify: `knowledge/traditions/bible-layer-manifest.json`

**Interfaces:** stable scene IDs linked from relations by `biblical_scene_ids` and `primary_biblical_scene_id`.

- [ ] Write validation for scene ID, title, book, canonical span, summary, sequence, roles/operators, source refs and cross-scene links.
- [ ] Add initial scenes for Jacob's ladder; Joseph rejection; Joseph prison; Joseph elevation/grain; Eden guarded way; John 10 Door/Shepherd; John 14 House/Way/Thomas/Father; Passion; Thomas resurrection recognition; Daniel cloud/Son-of-Man; Revelation Lion/Lamb/scroll; Ezekiel throne/wheel; New Jerusalem/river/Tree.
- [ ] Run scene validation; expect PASS.
- [ ] Register the scene layer in the manifest.
- [ ] Commit as `feat: add reusable biblical scene registry`.

### Task 5: Link high-value relations to Biblical Scenes

**Files:**
- Modify: active dossier/enrichment owners
- Create: `scripts/validate_bible_scene_links.py`

- [ ] Write failing validation that all supplied scene IDs exist and major authored-scene relations resolve correctly.
- [ ] Link Joseph, Door/Shepherd, House/Way, Passion, Thomas, cloud-coming, Lion/Lamb, wheel/throne and city/river relations first.
- [ ] Run scene-link validation and corpus tests; expect PASS.
- [ ] Commit as `data: connect Bible relations to scenes`.

### Task 6: Add atlas route/navigation model

**Files:**
- Create: `app/bible-atlas-navigation.js`
- Modify: `traditions/bible/index.html`
- Modify: `app/bible-study.css`
- Modify: `scripts/validate_bible_reader.py`

**Interfaces:** `window.BibleAtlas.routes`, `resolveRoute(corpus,state)`, `relatedPaths(row,corpus)`; URL state uses `route`, `topic`, `scene`, `id`, `order`, optional `q`.

- [ ] Add validator markers for the six primary routes and breadcrumbs.
- [ ] Implement routes: stories, roles, symbols, actions, books, timeline.
- [ ] Add compact route UI above existing comparator controls; keep search visually secondary.
- [ ] Add breadcrumb rendering and URL-state round trip.
- [ ] Validate keyboard/mobile semantics.
- [ ] Commit as `feat: add atlas-first Bible navigation`.

### Task 7: Make relation reading story-first

**Files:**
- Modify: `app/bible-study.js`
- Modify: `app/bible-witness-loader.js`
- Modify: `app/bible-dossier-loader.js`
- Modify: Bible reader CSS owners

- [ ] Add validation for required story-first sections.
- [ ] Render the supported modern/project situation first.
- [ ] Render reusable biblical scene summary when linked, with current dossier fallback.
- [ ] Render correspondences, roles, sequences and operators as one readable comparison section.
- [ ] Keep mismatch/countertext and maximum claim visibly separate.
- [ ] Add related-path buttons from `BibleAtlas.relatedPaths`.
- [ ] Run reader validation; expect PASS.
- [ ] Commit as `feat: make Bible comparisons story-first`.

### Task 8: Add local WEB source projection and Scripture zoom

**Files:**
- Create: `scripts/vendor_web_bible.py`
- Create: `data/sources/bible/web/index.json`
- Create: `app/bible-scripture-reader.js`
- Modify: `traditions/bible/index.html`
- Modify: `app/bible-study.css`
- Create: `scripts/validate_web_bible_source.py`

**Interfaces:**
- `window.BibleScripture.getRange(book,startChapter,startVerse,endChapter,endVerse)`
- `window.BibleScripture.getChapter(book,chapter)`

- [ ] Implement source validation first for book index, chapter/verse identity and source metadata.
- [ ] Implement vendoring/import from the existing WEB source manifest/upstream while preserving exact wording.
- [ ] Populate local book data.
- [ ] Implement Scripture reader.
- [ ] Add `Fragment → Whole scene → Chapter → Story/Intertext` controls.
- [ ] Validate every scene span against local WEB.
- [ ] Commit as `feat: add local WEB scripture zoom`.

### Task 9: Generate machine-readable quality and coverage reports

**Files:**
- Modify: `scripts/audit_bible_witness_coverage.py`
- Create: `scripts/build_bible_comparator_coverage.py`
- Create: `knowledge/indexes/bible-comparator-quality-report.json`
- Create: `knowledge/indexes/bible-comparator-coverage.json`

- [ ] Add JSON-output validation.
- [ ] Extend witness audit to emit per-relation quality dimensions and `recommended_action`.
- [ ] Build coverage generator from the manifest corpus and scene registry.
- [ ] Generate committed baseline reports.
- [ ] Validate strength-5/Level-A quality gates.
- [ ] Commit as `feat: map Bible comparator quality and coverage`.

### Task 10: Enrich the highest-priority thin relations

**Files:** manifest-active dossier/enrichment/scene/fragment owners selected by the quality report.

- [ ] Select strength-5 rows with `recommended_action=enrich`.
- [ ] Add missing project context without exceeding source status.
- [ ] Add biblical scene/literary/historical context.
- [ ] Add sequence, role mapping, mismatch, maximum claim and why-it-matters where missing.
- [ ] Re-run quality report and verify the high-priority gap count falls without integrity violations.
- [ ] Commit coherent families as `data: enrich Bible comparator <family>`.

### Task 11: Track reviewed/no-relation coverage

**Files:**
- Create: `knowledge/indexes/bible-scene-review-status.json`
- Create: `scripts/validate_bible_scene_review_status.py`
- Modify: `scripts/build_bible_comparator_coverage.py`

**Interface statuses:** `unreviewed`, `reviewed-relations`, `reviewed-no-meaningful-relation`, `reviewed-weak-only`, `reviewed-duplicate-only`.

- [ ] Add schema validation.
- [ ] Seed statuses for initial authored scenes.
- [ ] Surface review status in the coverage report, never as theological authority.
- [ ] Commit as `feat: track Bible scene review coverage`.

### Task 12: Begin Bible-wide expansion from coverage gaps

**Files:** extend scenes, active enrichment owners and review status.

- [ ] Work through Father/parent; burden/yoke/release; throne/source; emptying; mediation; cultivation; inheritance/adoption; exile/return; priest/king/prophet; temple/body/house.
- [ ] Deepen Joseph, David, John 10, John 14, Daniel/cloud-coming, Passion, Thomas/resurrection, Ezekiel and Revelation city/river/Tree corridors.
- [ ] Record weak/no-relation outcomes explicitly instead of forcing promotion.
- [ ] Regenerate quality/coverage reports after each coherent batch.
- [ ] Commit batches as `research: deepen Bible atlas <book-or-family>`.

### Task 13: Retire redundant wave-specific runtime loaders after parity

**Files:**
- Modify: `traditions/bible/index.html`
- Modify/remove compatibility logic in `app/bible-mining-wave19-loader.js`, `app/bible-mining-wave20-loader.js`, `app/bible-mining-wave22-loader.js`, `app/bible-mining-wave23-loader.js`
- Modify: `scripts/validate_bible_reader.py`

- [ ] Add exact active-ID parity validation before loader removal.
- [ ] Switch the page to `app/bible-corpus-loader.js`.
- [ ] Remove redundant wrappers only after parity passes.
- [ ] Run the full repository quality workflow.
- [ ] Commit as `refactor: retire Bible wave loader chain`.

### Task 14: Final verification and public usability pass

- [ ] Run all Bible manifest/corpus/scene/source/reader/parity validators.
- [ ] Run the repository's full site/quality workflow.
- [ ] Manually verify Joseph, Door/Shepherd, Thomas, Lion/Lamb, Cloud/Coming and New Jerusalem are reachable without search.
- [ ] Verify whole-scene/chapter zoom, breadcrumbs and visible countertexts.
- [ ] Verify mobile and keyboard behavior.
- [ ] Commit final fixes as `fix: complete Bible atlas usability verification`.

## Plan self-review

- Spec coverage includes manifest, scenes, full WEB source, atlas routes, breadcrumbs, story-first view, Scripture zoom, quality audit, coverage map, book-by-book expansion, countertexts and loader retirement.
- No placeholder/TODO instructions remain.
- Stable interface names: `BibleCorpus`, `BibleAtlas`, `BibleScripture`, `biblical_scene_ids`, `primary_biblical_scene_id`.
- Live reader stays usable and destructive loader retirement is deferred until parity is demonstrated.
