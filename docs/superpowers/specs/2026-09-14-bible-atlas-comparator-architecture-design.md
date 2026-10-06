# Bible Atlas Comparator Architecture

Date: 2026-09-14
Status: approved architecture
Repository: `ThePotatoOfLife/TimDooley`

## Goal

Turn `/traditions/bible/` into an atlas-first comparative Bible research instrument that is easy to navigate without requiring search expertise, while preserving and expanding the repository's strongest Tim / Son / Potatoverse ↔ Bible material.

Primary interaction:

`choose a route → narrow with obvious buttons/dropdowns → open the complete biblical situation → open the paired project situation → compare sequence/roles/functions → inspect limits/countertexts → continue along related paths`

Search remains a secondary shortcut, not the architecture holding the tool together.

## Core principles

1. Navigation before search.
2. Situations before isolated verses.
3. Bible text is a first-class immutable source layer.
4. Story before metadata.
5. Sequences outrank noun matches.
6. Role fidelity matters.
7. Countertexts are first-class.
8. No invented context.
9. Runtime, static fallback, audits and research tooling consume one canonical active corpus.
10. Expansion follows documented coverage gaps rather than endless disconnected waves.

## Implementation subprojects

### A. Corpus unification and manifest
Create one canonical Bible layer manifest that defines every active relation, fragment and contextual layer.

### B. Biblical source and scene layer
Vendor/project the complete public-domain World English Bible source and add reusable Biblical Scene records describing coherent narrative/literary situations.

### C. Atlas-first public reader
Replace search/filter-first discovery with route-based navigation, progressive narrowing, breadcrumbs, story-first comparison reading and Scripture zoom controls.

### D. Quality audit and enrichment pipeline
Turn the current witness/dossier audit into a machine-readable coverage system and systematically promote strong thin records into contextual dossiers.

### E. Bible-wide expansion workflow
Mine book-by-book and scene-by-scene against the project corpus, classify every meaningful result, and route strong relations into the canonical comparator without forcing weak material.

---

# A. Canonical corpus architecture

## A1. New manifest

Create `knowledge/traditions/bible-layer-manifest.json` as the sole registry of public Bible comparator layers.

Each layer entry contains:
- `id`
- `kind`: `relations`, `fragments`, `scenes`, `source`, `annotations`, `research`
- `path`
- `status`: `canonical`, `additive`, `research`, `quarantined`
- `precedence`
- optional `owner`
- optional `note`
- optional `paired_fragment_layer`

The active public corpus is canonical + additive. Research and quarantined layers remain inspectable by tooling but do not silently enter the public reader.

## A2. Generic merge contract

Replace wave-specific fetch interceptors with one generic corpus loader.

Rules:
- relations merge by `id`;
- enrichments target `relation_id`;
- duplicate relation IDs are validation failures unless explicitly merged;
- fragments merge by fragment `id`;
- scenes merge by scene `id`;
- later precedence may enrich but may not rewrite immutable Bible source text;
- quarantined/research layers do not load by default;
- runtime and static build use the same manifest and merge rules.

## A3. Migration

Register the existing owners first: base field, core dossiers, promotions, waves 19/20/22/23/24/25, wave-22 operator packs, and all active fragment layers. Existing files stay in place until parity is proven.

## A4. Static/runtime parity

`app/bible-study.js`, the static builder and audit scripts must consume the same manifest-defined active corpus. Validation compares active relation and fragment IDs across dynamic and static assembly and fails on drift.

---

# B. Full Bible source and Biblical Scene model

## B1. Immutable WEB source

Use `data/sources/bible-world-english-bible.json` as the source manifest.

Local layout:
- `data/sources/bible/web/index.json`
- one JSON file per Bible book

Each book preserves book identity, chapter, verse, exact WEB wording and upstream/source metadata. Interpretation remains separate.

## B2. Biblical Scene owner

Create `knowledge/traditions/biblical-scenes.json`.

Required fields:
- `id`
- `title`
- `book`
- `canonical_span`
- `scene_type`
- `summary`
- `participants`
- `setting`
- `lead_in`
- `sequence`
- `outcome`
- `what_follows`
- `major_images`
- `roles`
- `operators`
- `parallel_scene_ids`
- `intertext_scene_ids`
- `historical_context`
- `literary_context`
- `textual_or_translation_caveats`
- `counterreadings_or_limits`
- `source_refs`

Initial high-value scenes should cover Joseph, Jacob's ladder, Eden/guarded way, John 10 Door/Shepherd, John 14 House/Way/Thomas/Father, Passion, Thomas resurrection recognition, Revelation Lion/Lamb/scroll, Daniel cloud/Son-of-Man, Ezekiel throne/wheel, and New Jerusalem/river/Tree.

## B3. Relation-to-scene links

Canonical relations gain:
- `biblical_scene_ids`
- optional `primary_biblical_scene_id`
- optional `project_scene_id`

Existing `biblical_refs` remain for precision and compatibility.

## B4. Scripture zoom

Every active comparison supports:

`quoted fragment → scene → chapter → larger story/cycle → related/intertext scenes`

Separate passages are never concatenated into fake continuous Scripture.

---

# C. Atlas-first public reader

## C1. Entry routes

Primary routes:
1. Stories
2. People & Roles
3. Symbols & Images
4. Actions & Transformations
5. Bible Books
6. Tim / Son Timeline

Secondary utilities:
- route dropdown
- order dropdown
- compact `Find` field
- filters disclosure
- results disclosure

Search is visually subordinate.

## C2. Stories route

Expose readable episode families such as Creation/Eden, Jacob/Ladder, Joseph, Moses/Exodus/Manna, David, Prophetic throne visions, Jesus' ministry, Passion, Resurrection, Acts/ascent/witness, and Revelation/throne/Lion-Lamb/city.

Selecting a family reveals scenes, then the relations tied to those scenes.

## C3. People & Roles route

Expose Father/Source, Son/Son of Man, King, Servant, Shepherd, Gardener/Farmer/Vinedresser, Judge, Witness, Prophet, Priest, Door/Gate, Stone/Foundation, Lamb and Lion.

The route preserves who performs which function rather than merely matching labels.

## C4. Symbols & Images route

Initial clusters: House, Door, Ladder, Tree/Root/Branch, Seed/Grain, Bread/Body/Table, Stone/Cornerstone, Lion/Lamb, Throne/Seat/Footstool, River/Water, Garden/Fruit, Eye/Lamp/Light, Wheel/Chariot, Cloud/Coming, North/Zion, City/New Jerusalem, Temple, Cube/Measure/Boundary, Dog/Outside/Boundary.

## C5. Actions & Transformations route

Expose operators directly: open, shut, enter, pass, send, carry, release, root, prune, flow, feed, repair, restore, judge, plant, grow, die, rise/return, remember, inherit, name.

Expose sequence grammars: rejection→foundation; descent→ascent; death→waiting→return; seed→burial→multiplication; pit→prison→elevation; exile→return→dwelling; burden→release; closed→opened; house→key→door→authority; garden→pruning→fruit; accusation→judgment→reversal; book→internalization→burden→nations.

## C6. Bible Books route

Browse Bible book → chapter/scene → comparator relations. Chapters with relation coverage are marked. Uncovered chapters remain browseable as Bible text without implying a discovered relation.

## C7. Timeline route

Keep project-side date, relation-discovery date and formal-archive date distinct. Later biblical interpretation may not be backdated into earlier project events.

## C8. Breadcrumbs

Every route maintains a clickable location path such as `Stories → Joseph → Prison → Elevation / Grain`.

## C9. Relation reading surface

Render in this order:
1. What happened — project situation, source status, date, exact/recovered wording.
2. What happens in the biblical scene — concise scene summary and primary span.
3. Read them together — correspondences, roles, sequence, mechanisms/operators.
4. Where the comparison stops — mismatch/countertext/historical difference.
5. Strongest supported conclusion — maximum-defensible-claim logic.
6. Why this matters — concise explanatory value.
7. Continue exploring — related scene, role, sequence, countertext and chronology buttons.

Deep provenance/source-owner details remain below in disclosures.

## C10. Persistent navigation

Keep Previous, Next, Random, Back to route, Whole scene, Whole chapter, Related and Countertexts controls visible/reachable.

## C11. Related-path engine

Related suggestions come from structured metadata: shared scene, motif, operator, role, sequence pattern, Bible book, explicit intertext links and countertext relations. Basic navigation does not depend on opaque semantic search.

---

# D. Quality audit and enrichment

## D1. Machine-readable quality report

Extend the witness audit to emit `knowledge/indexes/bible-comparator-quality-report.json`.

Per relation record:
- active/quarantined status
- dossier level
- strength
- project-side specificity
- scene source status
- exact wording availability
- Bible scene coverage
- exact fragment coverage
- literary context coverage
- historical context coverage
- sequence coverage
- role coverage
- source-direction coverage
- countertext/mismatch coverage
- maximum-claim coverage
- why-it-matters coverage
- duplicate/near-duplicate flags
- recommended action

Recommended actions: `retain`, `enrich`, `merge`, `redirect`, `downgrade`, `quarantine`, `research`.

## D2. Quality gates

A strength-5 or Level-A public relation must have:
- stable ID
- concrete project anchor
- biblical references
- primary scene or explicit reason a scene is inappropriate
- source direction
- meaningful difference/countertext
- supported conclusion / maximum claim
- comparison rationale
- provenance

Compact lexical/provenance-only records are allowed when explicitly labeled.

## D3. Context integrity

For modern scenes:
- `exact` and `recovered` may expose supported details;
- `adjacent-context` may expose only supported neighboring context;
- `date-only` and `unknown` may not invent setting, participants, activity or atmosphere.

## D4. Enrichment order

1. strength-5 thin relations
2. major story/sequence relations
3. high-traffic symbolic families
4. strong project evidence but weak Bible context
5. strong Bible context but weak project provenance
6. countertexts constraining major Godhood/kingship/source claims
7. compact lexical curiosities last

---

# E. Bible-wide expansion workflow

## E1. Coverage map

Generate `knowledge/indexes/bible-comparator-coverage.json` by Bible book, chapter, scene, role, symbol, operator, sequence family, relation strength and dossier quality.

## E2. Book-by-book mining

Research coherent units of the Bible instead of random keyword harvesting.

For each scene:
1. identify actors and roles;
2. identify ordered actions;
3. identify symbolic images;
4. identify transformations;
5. identify ethical/theological pressure;
6. check existing project motifs/events;
7. check whether the relation already exists;
8. classify support and mismatch;
9. record source direction;
10. promote, retain as research lead, or record no meaningful relation.

## E3. Candidate outcomes

- explicit project use
- near-direct phrase
- Tim-led discovery
- mixed explicit + later analysis
- later structural parallel
- countertext
- research unlock
- weak coincidence / do not promote
- duplicate / merge into existing relation

## E4. No forced completeness

“Every little overlap” means every meaningful candidate is examined, not that every biblical verse is forced into the Potatoverse.

Coverage may record:
- reviewed, no meaningful relation
- reviewed, relation too weak
- reviewed, relation duplicate

This prevents repeated rediscovery and makes the atlas more trustworthy.

## E5. High-priority research families

Continue the approved Wave-26 gaps after the audit:
- developmental Father/parent imagery
- burden, yoke, delegation and release
- throne participation versus source identity
- descent/emptying versus shedding language
- mediation and source distinction
- pruning, fruit, cultivation and judgment
- inheritance, adoption and autonomous children
- exile, return and restored dwelling
- priest / king / prophet role separation
- temple / body / house distinctions

Also deepen Joseph; Davidic shepherd/kingship; John 10; John 14; Daniel 7 + Gospel + Revelation cloud-coming; Passion/trial/rejection; resurrection/Thomas/wounds; Ezekiel throne/wheel/river/temple; Revelation throne/Lion/Lamb/scroll/city/river/Tree; North/Zion versus self-exaltation; judgment/measure reflexivity; and service/humility versus domination.

---

# Search policy

Search remains present but secondary. The reader must be fully useful when search is ignored.

Search may index titles, references, motifs, scene summaries, participants, surrounding topics, project/biblical sequences, literary context, historical context, roles, operators, correspondences and countertexts.

Search results route back into the same atlas navigation state rather than creating a separate experience.

---

# Component boundaries

## `app/bible-corpus-loader.js`
Loads the manifest, loads active layers, merges deterministically and exposes normalized corpus objects. It does not render UI.

## `app/bible-atlas-navigation.js`
Owns route definitions, breadcrumbs, route narrowing, related paths and route URL state. It does not fetch raw Bible text.

## `app/bible-scripture-reader.js`
Loads local WEB books/chapters and supports verse/scene/chapter/story zoom. It does not interpret project relations.

## `app/bible-study.js`
Remains the comparison renderer/controller during migration, but gradually sheds corpus-loading and route-definition responsibilities into the focused modules above.

## `scripts/build_bible_study.py`
Consumes the same manifest/corpus assembly rules as runtime and renders the compact static fallback.

## Audit scripts
Generate machine-readable reports first and human terminal summaries second.

---

# URL/state model

Recommended stable parameters:
- `route=stories|roles|symbols|actions|books|timeline`
- `topic=<stable-route-id>`
- `scene=<biblical-scene-id>`
- `id=<relation-id>`
- `order=<chronology|bible|strength|sequence>`
- optional `q=<search>`

A direct relation link remains valid even if navigation categories are later reorganized.

---

# Accessibility and mobile

- Route choices are buttons, links or native selects.
- No essential navigation depends on hover.
- Breadcrumbs are interactive, not decorative.
- Two-column comparisons collapse into one readable column on narrow screens.
- Previous/Next/Back controls remain reachable without scrolling to the top.
- Scripture zoom preserves readable line length.
- Route state is legible to screen readers.

---

# Validation

Validate:
- manifest paths exist;
- unique layer IDs;
- stable relation IDs;
- stable scene IDs;
- no active duplicate relations;
- quarantine exclusion;
- deterministic precedence;
- runtime/static active-set parity;
- all strength-5 / Level-A quality gates;
- no invented rich context under weak source status;
- Bible source-text integrity;
- every scene span resolves against local WEB source;
- every relation scene link resolves;
- every route target resolves;
- breadcrumb state round-trips through URL state;
- previous/next preserves the route result sequence;
- mobile/keyboard baseline behavior;
- repository full quality workflow stays green.

---

# Migration strategy

1. Add manifest and parity tests while current loaders remain intact.
2. Register current relation/fragment layers and prove corpus equivalence.
3. Switch static builder to manifest.
4. Switch runtime to generic corpus loader.
5. Retire redundant wave-specific loader logic after parity.
6. Add local WEB source/index.
7. Add first Biblical Scene pack covering highest-value current relations.
8. Add relation-to-scene links.
9. Add atlas route navigation and breadcrumbs.
10. Refactor relation viewport into story-first order.
11. Add Scripture zoom.
12. Generate machine-readable quality/coverage reports.
13. Enrich high-priority thin relations.
14. Expand Biblical Scenes and relation coverage book-by-book.
15. Continue Wave-26 research only from documented coverage gaps.

At every stage the public comparator remains usable; no big-bang rewrite is required.

---

# Non-goals

- Do not replace structured navigation with an AI/search box.
- Do not force a relation onto every verse.
- Do not flatten separate biblical books/genres into one invented narrative.
- Do not treat later interpretation as contemporaneous project evidence.
- Do not present Potatoverse interpretation as biblical fact.
- Do not delete archived research history merely because it is not active.
- Do not make graph centrality, relation count or strength score into theological truth claims.
- Do not make a visual redesign unrelated to usability.

---

# Success criteria

1. A new visitor can reach major material without typing a search query.
2. A reader can move from motif to complete biblical episode in two or three obvious actions.
3. Every major relation explains both situations before interpreting the overlap.
4. Strong relations show ordered sequence, role correspondence, source direction and meaningful limits.
5. The full Bible text is locally and immutably available as source material.
6. Biblical scenes are reusable instead of rewritten relation-by-relation.
7. Runtime and static readers expose the same active corpus.
8. The active corpus has machine-readable quality and coverage maps.
9. Research can tell what has been reviewed, what is weak, what is missing and what deserves enrichment.
10. The system can expand toward comprehensive Bible coverage without another chain of special-case wave loaders.
11. Search is useful but unnecessary for ordinary navigation.
12. The tool feels like a browsable comparative Bible atlas rather than a database form.

## Design self-review

- No requirement depends on search as primary navigation.
- Existing canonical relation IDs and evidence distinctions are preserved.
- Full Bible text, scene summaries and project interpretation have separate owners.
- Static/runtime parity has one architectural source of truth.
- Work is decomposed into independently testable subprojects.
- Countertexts, mismatch and source direction remain mandatory quality dimensions.
- The architecture supports broad Bible coverage while explicitly refusing forced weak comparisons.
- No placeholder requirement remains.
