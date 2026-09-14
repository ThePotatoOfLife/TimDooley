# Bible Evidence-First Reader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current navigation-heavy Bible comparator with one evidence-first active-relation reader that shows the fullest recoverable project evidence beside the precise relevant World English Bible passage, while keeping Browse/filters secondary and preserving the manifest-defined corpus.

**Architecture:** Keep `knowledge/traditions/bible-layer-manifest.json` and `BibleCorpus` as the data authority. Add a deterministic local WEB source projection, a precise scripture-range parser, a normalized `BibleRelationModel`, and one `BibleRelationReader` visual authority. `bible-study.js` retains sequence/filter/navigation state but delegates active-relation normalization/rendering; atlas code becomes Browse-only instead of decorating the evidence surface.

**Tech Stack:** static HTML/CSS, browser JavaScript (IIFE/global modules, no bundler), Node for pure-JS tests/syntax checks, Python 3 standard library for corpus/build/validation tooling, JSON source files, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-14-bible-evidence-first-excavation-design.md`

## Global Constraints

- Evidence first; navigation second; interpretation after both.
- `knowledge/traditions/bible-layer-manifest.json` remains the sole active-corpus registry.
- Do not create a second Bible canon or relation owner.
- Project wording must remain visibly typed as exact/public/recovered/paraphrase/summary/reconstructed/unknown.
- Full scripture means the smallest complete literary unit required by the relation/linked scene, not an arbitrary full chapter.
- A whole chapter is shown by default only when the canonical scene itself explicitly spans the whole chapter.
- Provide `Expand chapter` as an optional reader action; do not make chapter expansion the default.
- World English Bible text is public-domain primary text and must remain separate from project interpretation.
- Local WEB files are the primary runtime source; upstream GitHub is fallback only.
- No network dependency in CI.
- Low evidence quality must be represented honestly; richer prose must never upgrade evidentiary strength.
- The first implementation tranche changes reader/runtime architecture; it does not attempt to complete all 109+ relations.
- Preserve existing Browse routes: Stories, People & Roles, Symbols & Images, Actions & Transformations, Bible Books, Tim / Son Timeline.

---

## File Structure Locked by This Plan

### New runtime units

- `app/bible-scripture-range.js` — pure reference parsing and verse selection; no DOM, no fetch.
- `app/bible-relation-model.js` — normalize one merged relation into a reader view-model; no DOM.
- `app/bible-relation-reader.js` — render/hydrate one active relation; owns the active evidence hierarchy.
- `app/bible-relation-reader.css` — only active-relation/evidence presentation.

### New source/tooling units

- `scripts/vendor_web_bible.py` — convert upstream WEB book JSON into deterministic local book files.
- `scripts/validate_web_bible_source.py` — validate local 66-book source projection without network.
- `scripts/test_vendor_web_bible.py` — unit-test upstream parsing/normalization.
- `scripts/test_bible_scripture_range.mjs` — Node tests for precise scripture reference parsing.
- `scripts/test_bible_relation_model.mjs` — Node tests for evidence hierarchy/model normalization.
- `scripts/test_bible_relation_reader.mjs` — Node string-render tests for visual ordering/contracts.
- `data/sources/bible/web/index.json` — local WEB index.
- `data/sources/bible/web/<book-slug>.json` — one normalized local source file per book.

### Existing runtime units retained but narrowed

- `app/bible-corpus-loader.js` — corpus merge only; no reader decoration.
- `app/bible-scripture-reader.js` — source loading, passage/chapter expansion and hydration.
- `app/bible-study.js` — filter/order/active-id state and sequence navigation.
- `app/bible-atlas-navigation.js` — Browse taxonomy/routing.
- `app/bible-atlas-ui.js` — collapsed Browse UI only.
- `traditions/bible/index.html` — compact shell and script ordering.
- `app/bible-study.css` — page shell/navigation/filters only.

### Existing decorators removed from runtime after parity is proven

- `app/bible-dossier-loader.js`
- `app/bible-witness-loader.js`
- `app/bible-scene-reader.js`
- `app/bible-mining-wave19-loader.js`
- `app/bible-mining-wave20-loader.js`
- `app/bible-mining-wave22-loader.js`
- `app/bible-mining-wave23-loader.js`

Do not delete these files in the same commit that removes their script tags. First prove the manifest corpus contains their data and the new reader preserves required output; deletion can happen only after repo-wide reference checks are green.

---

### Task 1: Vendor the World English Bible Locally and Validate It

**Files:**
- Create: `scripts/vendor_web_bible.py`
- Create: `scripts/test_vendor_web_bible.py`
- Create: `scripts/validate_web_bible_source.py`
- Create/generated: `data/sources/bible/web/index.json`
- Create/generated: `data/sources/bible/web/*.json`
- Modify: `data/sources/bible-world-english-bible.json`

**Interfaces:**
- Consumes: `data/sources/bible-web-book-index.json` and its `upstream_template`/book-number mapping.
- Produces: local book files with schema `{"book": str, "book_no": str, "translation": "World English Bible", "source_url": str, "verses": [{"chapter": int, "verse": int, "text": str}]}` and `data/sources/bible/web/index.json` mapping canonical book names to local paths.
- Later tasks rely on: deterministic local paths and verse records sorted by `(chapter, verse)`.

- [ ] **Step 1: Write the failing parser test**

Create `scripts/test_vendor_web_bible.py` with a synthetic upstream fixture so tests require no network:

```python
from vendor_web_bible import normalize_book_items


def test_normalize_book_items_strips_html_and_preserves_coordinates():
    items = [
        {"title": "John 10:7", "content": "<p>Jesus therefore said...</p>"},
        {"title": "John 10:9", "content": "I am the door."},
    ]
    result = normalize_book_items("John", "43", items, "fixture://john")
    assert result["book"] == "John"
    assert result["book_no"] == "43"
    assert result["verses"] == [
        {"chapter": 10, "verse": 7, "text": "Jesus therefore said..."},
        {"chapter": 10, "verse": 9, "text": "I am the door."},
    ]
```

Also test malformed titles are rejected rather than silently dropped.

- [ ] **Step 2: Run the test and confirm failure**

Run:

```bash
python scripts/test_vendor_web_bible.py
```

Expected: import/function failure because `vendor_web_bible.py` does not exist.

- [ ] **Step 3: Implement the normalizer and vendoring command**

`vendor_web_bible.py` must use only the Python standard library. Implement these functions exactly:

```python
def clean_html(value: str) -> str: ...
def parse_title(title: str, expected_book: str) -> tuple[int, int]: ...
def normalize_book_items(book: str, book_no: str, items: list[dict], source_url: str) -> dict: ...
def vendor_book(book: str, book_no: str, upstream_template: str, out_root: Path) -> dict: ...
def build_index(book_entries: list[dict], upstream_template: str) -> dict: ...
```

Use `urllib.request.urlopen` only in `vendor_book`; parsing/normalization remains pure and testable. Reject duplicate `(chapter, verse)` coordinates. Normalize whitespace but do not paraphrase text.

Use stable filename slugs such as `john.json`, `1-corinthians.json`, `song-of-solomon.json`.

- [ ] **Step 4: Make the parser test pass**

Run:

```bash
python scripts/test_vendor_web_bible.py
```

Expected: `WEB VENDOR TESTS PASSED`.

- [ ] **Step 5: Generate the local source projection once**

Run with network access:

```bash
python scripts/vendor_web_bible.py
```

Expected: 66 book files plus `data/sources/bible/web/index.json`.

Index shape:

```json
{
  "id": "bible-web-local-index",
  "translation": "World English Bible",
  "book_count": 66,
  "books": {
    "Genesis": "data/sources/bible/web/genesis.json",
    "John": "data/sources/bible/web/john.json"
  }
}
```

- [ ] **Step 6: Write the local-source validator**

`validate_web_bible_source.py` must verify:

```python
assert index["book_count"] == 66
assert set(index["books"]) == set(source_manifest["books"])
```

For every book file verify: canonical name matches index, `translation == "World English Bible"`, verse list is non-empty, coordinates are unique and strictly increasing, every text is non-empty.

Add sentinel assertions for at least `Genesis 1:1`, `John 10:7`, `John 12:24`, `Revelation 21:1` so accidental malformed imports are caught.

- [ ] **Step 7: Validate local source with no network**

Run:

```bash
python scripts/validate_web_bible_source.py
```

Expected: `WEB LOCAL SOURCE VALIDATION PASSED (66 books)`.

- [ ] **Step 8: Update source manifest status**

In `data/sources/bible-world-english-bible.json`, change `planned_local_layout` into a current `local_layout` (or add `local_status: "vendored"`) while preserving license, source and canon warnings. Do not remove upstream metadata.

- [ ] **Step 9: Commit Task 1**

```bash
git add scripts/vendor_web_bible.py scripts/test_vendor_web_bible.py scripts/validate_web_bible_source.py data/sources/bible-world-english-bible.json data/sources/bible/web/
git commit -m "feat: vendor local WEB source for Bible reader"
```

---

### Task 2: Add a Precise Scripture Reference/Range Parser

**Files:**
- Create: `app/bible-scripture-range.js`
- Create: `scripts/test_bible_scripture_range.mjs`

**Interfaces:**
- Consumes: canonical book names from the local index.
- Produces:
  - `BibleScriptureRange.parseReference(reference, bookNames)`
  - `BibleScriptureRange.selectVerses(verses, parsed)`
  - `BibleScriptureRange.chapterSpan(parsed)`
- `parseReference` returns `{book, selectors}` where each selector is `{start:{chapter,verse}, end:{chapter,verse}}`.

- [ ] **Step 1: Write the failing Node tests**

`test_bible_scripture_range.mjs` must cover these exact cases:

```js
assert.deepEqual(parseReference('John 10:7', books), {
  book:'John', selectors:[{start:{chapter:10,verse:7},end:{chapter:10,verse:7}}]
});
assert.deepEqual(parseReference('John 10:7, 9', books).selectors, [
  {start:{chapter:10,verse:7},end:{chapter:10,verse:7}},
  {start:{chapter:10,verse:9},end:{chapter:10,verse:9}}
]);
assert.deepEqual(parseReference('Genesis 28:10-22', books).selectors[0], {
  start:{chapter:28,verse:10},end:{chapter:28,verse:22}
});
assert.deepEqual(parseReference('Revelation 21:1-22:5', books).selectors[0], {
  start:{chapter:21,verse:1},end:{chapter:22,verse:5}
});
```

Also require malformed references and unknown books to throw explicit errors.

- [ ] **Step 2: Run test to verify failure**

```bash
node scripts/test_bible_scripture_range.mjs
```

Expected: module missing.

- [ ] **Step 3: Implement the pure parser**

Use a UMD-style export so the same file works in browser and Node:

```js
const api={parseReference,selectVerses,chapterSpan};
if(typeof module!=='undefined'&&module.exports)module.exports=api;
globalThis.BibleScriptureRange=api;
```

Do not infer the book with a naive `split`; match the longest canonical book name prefix from `bookNames` so numbered/multi-word books work.

For comma-separated continuations, inherit the previous chapter only within the same reference string. For cross-chapter ranges, include all verses between endpoints inclusive.

- [ ] **Step 4: Add verse selection tests**

Use a synthetic verse array and assert `selectVerses` returns only requested verses, including cross-chapter spans. Assert no whole chapter leaks into `John 10:7, 9`.

- [ ] **Step 5: Run Node tests**

```bash
node scripts/test_bible_scripture_range.mjs
node --check app/bible-scripture-range.js
```

Expected: pass.

- [ ] **Step 6: Commit Task 2**

```bash
git add app/bible-scripture-range.js scripts/test_bible_scripture_range.mjs
git commit -m "feat: parse precise Bible passage ranges"
```

---

### Task 3: Build the Normalized Active Relation Model

**Files:**
- Create: `app/bible-relation-model.js`
- Create: `scripts/test_bible_relation_model.mjs`

**Interfaces:**
- Consumes: one merged relation row, scene map, occurrence/timeline evidence maps, and the full relation sequence.
- Produces: `BibleRelationModel.build(row, context)` with stable shape:

```js
{
  id, title, meta,
  projectEvidence: [{text,status,sourceId,date}],
  scripture: {primaryRef, secondaryRefs, primarySceneId, scene},
  argument: {why, projectSequence, biblicalSequence, correspondences},
  limits: [],
  maximumClaim,
  chronology: [{label,date,text}],
  provenance: [{label,value,href}],
  related: [{id,title,date,reason,score}],
  circumstances: {...}
}
```

- [ ] **Step 1: Write failing evidence-priority tests**

Test that exact/public/recovered wording is deduplicated but never truncated:

```js
const row={
  id:'r1', project_anchor:'summary',
  exact_wording:['exact A','exact B','exact C','exact D'],
  recovered_wording:['recovered E']
};
const model=build(row, emptyContext());
assert.deepEqual(model.projectEvidence.map(x=>x.text),
  ['exact A','exact B','exact C','exact D','recovered E']);
assert.equal(model.projectEvidence[0].status,'exact');
```

Test that when no exact/recovered/public wording exists, the model emits one summary item with `status:'summary'` and `hasExactProjectWording:false`.

- [ ] **Step 2: Run test and verify failure**

```bash
node scripts/test_bible_relation_model.mjs
```

Expected: missing module/function.

- [ ] **Step 3: Implement project evidence normalization**

Use source precedence:

1. `project_quote` / `quote` / `exact_wording` → `exact`
2. occurrence-ledger quote resolved from `occurrence_ids` → `public`
3. `public_wording` → `public`
4. `recovered_wording` → `recovered`
5. `project_anchor` → `summary`

Deduplicate by normalized text while keeping first/highest-status occurrence.

- [ ] **Step 4: Implement scripture selection contract**

Primary scripture precedence:

1. linked `primary_biblical_scene_id` with a parseable `canonical_span`;
2. first linked `biblical_scene_id` with a parseable `canonical_span`;
3. explicit `primary_biblical_ref` if present;
4. first parseable `biblical_refs` entry.

Secondary refs are remaining parseable `biblical_refs`, deduplicated.

**Smallest-complete-unit rule:** do not widen a verse reference to a chapter automatically. A linked scene may define a wider complete literary unit. Chapter expansion is a separate action in the reader.

- [ ] **Step 5: Implement argument, limits, chronology and provenance**

Argument precedence:

```js
why = relation_argument.why_dense
   || relation_argument.why_it_matters
   || relation_arguments.join(' ')
   || overlap
   || project_value
```

Limits aggregate/deduplicate: `mismatch`, `weaknesses`, `counter_text`, `source_correction`, `difference`, `boundary`, linked scene `counterreadings_or_limits`.

Chronology must preserve separate labels for event/project date, first comparison and formal archive date. Never collapse them into one date.

- [ ] **Step 6: Implement structural related-ranking**

Use deterministic weights:

- same primary scene: +8
- any shared biblical scene: +5
- shared timeline event ID: +5
- same relation class: +2
- shared operator: +2 each, cap +6
- shared motif: +1 each, cap +4
- same first Bible book: +1

Return top 6 with a human-readable `reason` assembled from the strongest shared structures. Do not use raw full-text similarity.

- [ ] **Step 7: Run model tests**

```bash
node scripts/test_bible_relation_model.mjs
node --check app/bible-relation-model.js
```

Expected: pass.

- [ ] **Step 8: Commit Task 3**

```bash
git add app/bible-relation-model.js scripts/test_bible_relation_model.mjs
git commit -m "feat: normalize Bible relation reader model"
```

---

### Task 4: Build One Evidence-First Active Relation Renderer

**Files:**
- Create: `app/bible-relation-reader.js`
- Create: `app/bible-relation-reader.css`
- Create: `scripts/test_bible_relation_reader.mjs`

**Interfaces:**
- Consumes: model from `BibleRelationModel.build` plus resolved primary/secondary scripture blocks.
- Produces:
  - `BibleRelationReader.renderHTML(model, scripture)` — pure string renderer.
  - `BibleRelationReader.render(container, model, services)` — DOM hydration and async scripture loading.

- [ ] **Step 1: Write failing HTML-order tests**

Construct a model fixture and assert ordering by index positions:

```js
const html=renderHTML(model, scripture);
assert(html.indexOf('relation-evidence-grid') < html.indexOf('relation-argument'));
assert(html.indexOf('relation-argument') < html.indexOf('relation-context-depth'));
assert(html.includes('What this comparison can actually establish'));
assert(html.includes('Where the comparison breaks'));
```

Assert all four exact project quotations appear; no `.slice(0,3)` behavior is allowed.

Assert an honest no-exact state contains `No exact project-side wording has been recovered for this relation yet.`.

- [ ] **Step 2: Run test and verify failure**

```bash
node scripts/test_bible_relation_reader.mjs
```

- [ ] **Step 3: Implement the renderer in this exact hierarchy**

HTML order:

1. `.relation-reader-header`
2. `.relation-evidence-grid`
   - `.project-evidence`
   - `.scripture-evidence`
3. `.relation-argument`
4. `.relation-limits`
5. `.relation-maximum-claim`
6. `.relation-context-depth`
   - project circumstances
   - whole biblical situation
7. chronology/source direction
8. provenance
9. related comparisons

Keep chronology/provenance/details collapsible; do not hide primary evidence, why, limits, or maximum claim behind `<details>`.

- [ ] **Step 4: Implement long-evidence collapsing without truncation**

If project evidence has more than 6 items, render first 6 plus a native `<details>` containing the remainder. The data remains present and user-accessible; this is presentation collapsing, not data truncation.

If primary scripture exceeds 35 verses, render the full selected literary unit inside a scrollable/expandable passage container with an explicit verse count. Do not change the selected passage boundaries.

- [ ] **Step 5: Implement CSS hierarchy**

Desktop: two balanced evidence columns; mobile: project evidence first, scripture second. Make evidence typography visually stronger than chips/metadata. Keep atlas/filter styles out of this file.

- [ ] **Step 6: Run reader tests and syntax check**

```bash
node scripts/test_bible_relation_reader.mjs
node --check app/bible-relation-reader.js
```

- [ ] **Step 7: Commit Task 4**

```bash
git add app/bible-relation-reader.js app/bible-relation-reader.css scripts/test_bible_relation_reader.mjs
git commit -m "feat: add evidence-first Bible relation reader"
```

---

### Task 5: Make Scripture Reader Local-First and Range-Precise

**Files:**
- Modify: `app/bible-scripture-reader.js`
- Modify: `traditions/bible/index.html`

**Interfaces:**
- Consumes: `BibleScriptureRange`, `data/sources/bible/web/index.json`, local book files.
- Produces:
  - `BibleScriptureReader.loadBook(book)` local-first.
  - `BibleScriptureReader.loadReference(reference)` exact selected verses.
  - `BibleScriptureReader.loadChapter(book, chapter)` optional expansion.
  - `BibleScriptureReader.loadScene(scene)` exact `canonical_span`.

- [ ] **Step 1: Add scripts in dependency order**

Before `bible-scripture-reader.js`, load:

```html
<script src="../../app/bible-scripture-range.js"></script>
```

Do not add new runtime dependencies.

- [ ] **Step 2: Replace current chapter-only `spanParts` behavior**

`loadReference` must:

```js
const parsed=BibleScriptureRange.parseReference(reference,Object.keys(index.books));
const book=await loadBook(parsed.book);
return BibleScriptureRange.selectVerses(book.verses,parsed);
```

`loadScene(scene)` calls `loadReference(scene.canonical_span)`.

- [ ] **Step 3: Make local source primary**

Read `data/sources/bible/web/index.json`; fetch the indexed local book JSON. Only if that local fetch fails may the reader use the older upstream URL template. Emit a console warning on fallback.

- [ ] **Step 4: Preserve optional expanded reading**

Add `loadChapter(book, chapter)` and wire `Expand chapter` in the reader service. Expansion must never replace the primary selected passage in the model.

- [ ] **Step 5: Verify syntax and range tests**

```bash
node --check app/bible-scripture-reader.js
node scripts/test_bible_scripture_range.mjs
```

- [ ] **Step 6: Commit Task 5**

```bash
git add app/bible-scripture-reader.js traditions/bible/index.html
git commit -m "feat: read precise WEB passages from local source"
```

---

### Task 6: Invert the Page Shell and Collapse Browse by Default

**Files:**
- Modify: `traditions/bible/index.html`
- Modify: `app/bible-study.css`
- Modify: `app/bible-atlas-navigation.css`
- Modify: `app/bible-atlas-ui.js`

**Interfaces:**
- Consumes: existing atlas routes/topics and study filter controls.
- Produces: compact shell with `#browse-toggle` controlling `#atlas-explorer`.

- [ ] **Step 1: Replace the large header with compact orientation markup**

Target semantic skeleton:

```html
<header class="bible-compact-header">
  <div>
    <div class="eyebrow">Comparison atlas</div>
    <h1>TIM &amp; THE BIBLE</h1>
  </div>
  <details class="method-note">
    <summary>Method</summary>
    <!-- current evidence-boundary copy -->
  </details>
</header>
```

Reduce heading scale substantially; preserve title/canonical metadata.

- [ ] **Step 2: Add Browse control to the toolbar**

```html
<button class="toolbar-button" id="browse-toggle" type="button" aria-expanded="false">Browse</button>
```

Keep atlas markup `hidden` initially.

- [ ] **Step 3: Stop atlas UI from auto-opening**

In `bible-atlas-ui.js`, `start()` may populate routes/topics but must leave the shell hidden. Add:

```js
function setBrowseOpen(open){
  shell.hidden=!open;
  $('browse-toggle').setAttribute('aria-expanded',String(open));
}
```

Click toggles it. Topic selection closes Browse after applying the topic on screens below 1000px; desktop may keep it open until toggled.

- [ ] **Step 4: Reduce atlas visual weight**

Change atlas from a large standalone intro card to a compact drawer. Remove the large `Choose a way in` title from the default visible surface; it may remain inside the opened Browse panel in smaller typography.

- [ ] **Step 5: Keep search optional**

Do not remove search, but reduce its visual priority relative to Browse/focus/order and evidence. On mobile, controls may wrap; active evidence must follow immediately after navigation controls.

- [ ] **Step 6: Run syntax check**

```bash
node --check app/bible-atlas-ui.js
```

- [ ] **Step 7: Commit Task 6**

```bash
git add traditions/bible/index.html app/bible-study.css app/bible-atlas-navigation.css app/bible-atlas-ui.js
git commit -m "refactor: make Bible browse secondary to evidence"
```

---

### Task 7: Integrate the Model/Reader and Remove Competing Runtime Decorators

**Files:**
- Modify: `app/bible-study.js`
- Modify: `traditions/bible/index.html`
- Modify: `app/bible-corpus-loader.js` only if a small explicit helper is needed; do not change merge semantics.
- Modify: `scripts/validate_bible_reader.py`

**Interfaces:**
- Consumes: `BibleCorpus.load()`, `BibleRelationModel.build`, `BibleRelationReader.render`, evidence ledgers currently loaded by `bible-study.js`.
- Produces: one active relation rendering path.

- [ ] **Step 1: Change `bible-study.js` to load the manifest corpus directly**

Replace base field/fragment fetch dependence with:

```js
const corpus=await window.BibleCorpus.load();
const rows=corpus.relations.map(window.BibleCorpus.readerRelation);
const scenes=corpus.scenes;
```

Continue loading attestation/reverse/public-occurrence/timeline ledgers as evidence context.

- [ ] **Step 2: Replace `renderActiveRelation` internals**

Keep filter/order/navigation state functions, but change active rendering to:

```js
const model=window.BibleRelationModel.build(row,context);
await window.BibleRelationReader.render(activeEl,model,{
  scripture:window.BibleScriptureReader,
  onSelectRelation:id=>{state.activeId=id;render();}
});
```

Because scripture loading is async, use a monotonically increasing render token so a slow previous relation cannot overwrite a newer selection.

- [ ] **Step 3: Remove major decorator script tags from the page**

After the new reader passes tests, remove runtime includes for dossier/witness/scene/mining decorator loaders. Keep their data layers in the manifest.

The page should load in this broad order:

```text
bible-corpus-loader
bible-atlas-navigation
bible-scripture-range
bible-relation-model
bible-scripture-reader
bible-relation-reader
bible-study
bible-atlas-ui
```

- [ ] **Step 4: Update `validate_bible_reader.py` contracts**

Remove requirements that force legacy decorators onto the page. Add required markers for:

- `bible-relation-model.js`
- `bible-relation-reader.js`
- `bible-relation-reader.css`
- `bible-scripture-range.js`
- `browse-toggle`
- `BibleRelationModel.build`
- `BibleRelationReader.render`
- no legacy major decorator script tags

Add forbids for `slice(0,3)` on project evidence rendering and for auto-opening atlas logic.

- [ ] **Step 5: Prove manifest parity before considering deletion**

Run:

```bash
python scripts/test_bible_corpus.py
python scripts/check_bible_static_dynamic_parity.py
python scripts/validate_bible_reader.py
```

Do not delete legacy loader files in this task if any repo reference still depends on them.

- [ ] **Step 6: Commit Task 7**

```bash
git add app/bible-study.js traditions/bible/index.html scripts/validate_bible_reader.py app/bible-corpus-loader.js
git commit -m "refactor: unify Bible active relation rendering"
```

---

### Task 8: Update Static Fallback, CI, and Whole-Project Verification

**Files:**
- Modify: `scripts/build_bible_study.py`
- Modify: `.github/workflows/quality-checks.yml`
- Modify if needed: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: local WEB validator/tests and unified reader runtime.
- Produces: CI protection and a compact no-JS fallback that remains honest about source status.

- [ ] **Step 1: Update static fallback copy without pretending it is the deep reader**

Keep static fallback compact, but render all directly stored exact/recovered project wording up to a reasonable disclosure and label it. Continue using fragments for no-JS fallback if necessary; add copy stating that the interactive reader provides the full selected WEB passage.

Do not duplicate the entire browser reader implementation in Python.

- [ ] **Step 2: Add CI commands**

Under `Validate JavaScript syntax`, add:

```bash
node --check app/bible-scripture-range.js
node --check app/bible-relation-model.js
node --check app/bible-scripture-reader.js
node --check app/bible-relation-reader.js
```

Under `Validate Bible atlas corpus`, add:

```bash
python scripts/test_vendor_web_bible.py
python scripts/validate_web_bible_source.py
node scripts/test_bible_scripture_range.mjs
node scripts/test_bible_relation_model.mjs
node scripts/test_bible_relation_reader.mjs
```

No CI step may run `vendor_web_bible.py` against the network.

- [ ] **Step 3: Run focused validation**

```bash
python scripts/test_vendor_web_bible.py
python scripts/validate_web_bible_source.py
node scripts/test_bible_scripture_range.mjs
node scripts/test_bible_relation_model.mjs
node scripts/test_bible_relation_reader.mjs
python scripts/test_bible_corpus.py
python scripts/validate_bible_reader.py
python scripts/check_biblical_scenes.py
python scripts/check_bible_static_dynamic_parity.py
```

All must pass.

- [ ] **Step 4: Run full repository quality chain locally where supported**

At minimum:

```bash
python scripts/build_site.py
python scripts/validate_reader_surfaces.py
python scripts/validate_public_navigation.py
python scripts/check_machine_discoverability.py
```

Then rely on the PR `Repository quality checks` workflow for the full chain.

- [ ] **Step 5: Manually inspect the built comparator**

Acceptance checks:

1. `/traditions/bible/` opens with the atlas closed.
2. Active comparison evidence is visible before any large navigation panel.
3. A relation with 4+ project quotes exposes all of them (possibly after an explicit `More evidence` disclosure), not only 3.
4. `John 10:7, 9` shows verses 7 and 9 only.
5. `Genesis 28:10-22` shows 10 through 22, not all of Genesis 28 unless expanded.
6. Whole biblical situation appears under direct evidence/argument.
7. Why / breaks / maximum claim are visibly distinct.
8. Source direction and later-vs-earlier dates remain distinct.
9. Browse still reaches Stories/Roles/Symbols/Actions/Books/Timeline.
10. Mobile stacks project evidence before Bible evidence.

- [ ] **Step 6: Commit Task 8**

```bash
git add scripts/build_bible_study.py .github/workflows/quality-checks.yml scripts/validate_reader_surfaces.py
git commit -m "test: protect evidence-first Bible reader"
```

---

## Completion Gate

Before opening/merging the implementation PR:

```bash
python scripts/validate_web_bible_source.py
node scripts/test_bible_scripture_range.mjs
node scripts/test_bible_relation_model.mjs
node scripts/test_bible_relation_reader.mjs
python scripts/test_bible_corpus.py
python scripts/validate_bible_reader.py
python scripts/build_site.py
```

Then require the GitHub `Repository quality checks` workflow to pass on the implementation branch.

Do not merge if the comparator still needs any legacy DOM decorator to produce its primary evidence/argument/context blocks. Data may remain in legacy-named JSON layers; visual authority must be singular.
