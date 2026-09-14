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
