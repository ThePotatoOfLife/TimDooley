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
