# World Map Unification Design

Date: 2026-09-12
Status: approved architectural direction; migration design pending implementation plan

## 1. Goal

The project will use **World Map** as the single public and architectural name for its geographic, country, relationship, network, geopolitical and spatial exploration system.

The generic term **Atlas** will be retired from the active architecture. It currently names too many unrelated things and makes ownership ambiguous: the World Map, country records, relationship vocabularies, religious research, specialist comparison corpora, validators and design documents all use the same vague noun. That ambiguity makes it easier to create duplicate systems, route data to the wrong owner, or mistake an internal research corpus for a public product.

After this migration, active project language should answer what an object actually is: a **map, registry, layer, model, research document, index, method, comparison, ledger, programme, or source**.

The intended reader-level definition is simple:

> **World Map** is the project's single geographic interface for countries, relationships, networks, institutions, demographics, religion, economics, time, evidence, North/East/West/South fields and other spatially useful project data.

There is no separate World Atlas product behind it.

---

## 2. Canonical public owner

### 2.1 One public route

The canonical public route is:

`/world-map/`

The current 3D application at `world-map/3d.html` becomes the implementation of `world-map/index.html`.

`/world-map/3d.html` becomes a compatibility-only, `noindex` redirect to `/world-map/`.

The homepage and every canonical navigation surface link to `/world-map/`, never directly to `3d.html`.

### 2.2 Retire the duplicate 2D public product

The current `world-map/index.html` is an older 2D Leaflet renderer. It must not remain as a second public map after the 3D application becomes canonical.

Before removal, implementation must inventory any useful behavior that exists only in the 2D renderer. Unique capabilities should be either:

1. transferred into the canonical World Map where they still add value; or
2. explicitly judged obsolete and archived with a short reason.

The old renderer may be preserved under `archive/legacy/` for implementation history, but it must not remain a public alternate product.

### 2.3 Public naming

Reader-facing copy uses only:

- **World Map**
- **Map** where context is already obvious

Reader-facing copy must not introduce:

- World Atlas
- World Relational Atlas
- Atlas
- Country Atlas
- map/atlas dual terminology

The title, metadata, UI brand, homepage card, site navigation, sitemap and machine-readable discovery all use **World Map**.

---

## 3. One system does not mean one giant file

Unification is conceptual and architectural, not monolithic.

The World Map remains internally modular because countries, relationships, time, demographics, religion, evidence and rendering are different concerns. The simplification is that all of those modules have explicit roles and one owning product.

Canonical conceptual structure:

```text
World Map
├── application / rendering
├── country registry
├── relationship registry
├── layers
├── country statistics and dimensions
├── religion and society data
├── institutions and organizations
├── economics and value chains
├── alliances and memberships
├── North / East / West / South fields
├── time and historical state
├── evidence and provenance
├── comparison
├── network trace / pathfinding
├── search and selection
└── research queues / unresolved coverage
```

A module is part of World Map if the map renders it, queries it, compares it, routes through it, or uses it to explain a spatial relationship. Its canonical data may still be owned by another domain when appropriate. The World Map should reference those owners rather than duplicate their data.

Example: religious composition belongs to its canonical religion/demography data owner, while the World Map provides a geographic projection of it.

---

## 4. Vocabulary contract

The project will replace the generic `Atlas` noun with nouns that communicate function.

### Map
A spatial interface or spatial projection. Use only when geography is materially part of the object.

Examples: `World Map`, a rendered infrastructure map, a route map.

### Registry
Structured reusable canonical records, identifiers, memberships or definitions.

Examples: country registry, relationship registry, symbol registry, programme registry.

### Layer
A renderable or queryable projection placed over another owner, especially in World Map.

Examples: religion layer, alliance layer, axis field layer, economic layer.

### Model
A formal, derived, mathematical, structural or analytical representation.

Examples: sector model, dimension model, relationship scoring model.

### Research
Authored investigation, synthesis, interpretive reference material or a research corpus that is not itself canonical structured state.

Examples: Christianity research, Religious Systems research, Swamp research.

### Index
Lookup, discovery, navigation or mapping between canonical objects.

Examples: country index, source index, document index.

### Method
Rules or procedures governing how data or comparisons are created.

Examples: country relational method, source authority method.

### Comparison
An explicit cross-domain or cross-tradition relation corpus whose purpose is to compare claims, texts, motifs, events or structures.

### Ledger
Dated/accounting-like records, obligations or project-defined balances where the ledger metaphor is actually functional.

### Programme
A proposed or active coordinated body of work, policy, capability building or intervention.

These nouns are not interchangeable. New files should be named according to what they do.

---

## 5. Primary rename map

The implementation plan must generate a complete repository inventory before modifying paths. The following mappings establish the intended naming semantics.

### 5.1 World Map system

| Current | Canonical replacement |
|---|---|
| `World Relational Atlas` | `World Map` |
| `world-map/3d.html` | compatibility redirect to `/world-map/` |
| old `world-map/index.html` 2D renderer | archive after useful capability migration |
| `atlasApp` | `worldMapApp` |
| `atlasTimeState` | `worldMapTimeState` |
| `Atlas Exploration / Tikkun Mode` | `World Map Research / Tikkun Mode` or a more specific feature name if retained |
| `knowledge/core/world-atlas-integrated-layer-stack.json` | `knowledge/core/world-map-layer-stack.json` |
| `knowledge/research/world-atlas-whole-project-synthesis-2026-09-11.md` | archive as historical design/research context or rename to `world-map-whole-project-synthesis-2026-09-11.md` if still actively referenced |
| `scripts/validate_atlas.py` | `scripts/validate_world_map.py` |
| `scripts/audit_atlas_links.py` | `scripts/audit_world_map_links.py` |
| `scripts/validate_atlas_view_contracts.py` | `scripts/validate_world_map_view_contracts.py` |
| `scripts/validate_atlas_math_calibration.py` | `scripts/validate_world_map_math_calibration.py` |

All JS variables, DOM IDs, CSS classes, test labels and runtime descriptions using `atlas` as the World Map application name should similarly migrate to `worldMap`, `world-map`, `map`, or a feature-specific term.

### 5.2 Country system

| Current | Canonical replacement |
|---|---|
| `data/country-atlas.json` | `data/country-registry.json` |
| `Global Country Atlas` | `Country Registry` |
| `scripts/refresh_country_atlas.py` | `scripts/refresh_country_registry.py` |

Country records remain under `data/countries/`. The registry is a parent/index/coverage structure, not a second country database.

### 5.3 Relationship system

| Current | Canonical replacement |
|---|---|
| `docs/KINGDOM-ATLAS.md` | `docs/RELATIONSHIP-SYSTEM.md` |
| `Kingdom Atlas` when describing the shared relation vocabulary | `Relationship System` |

If implementation discovers a distinct structured relation-record collection separate from the method/system document, that collection may be called `Relationship Registry`. Do not use both names for the same object.

### 5.4 Symbol system

| Current | Canonical replacement |
|---|---|
| `docs/SYMBOL-ATLAS.md` | `docs/SYMBOL-REGISTRY.md` |
| `Symbol Atlas` | `Symbol Registry` |

The symbol object is fundamentally a canonical vocabulary/record set rather than a spatial map.

### 5.5 Research documents

| Current | Canonical replacement |
|---|---|
| `docs/CHRISTIANITY-ATLAS.md` | `docs/CHRISTIANITY-RESEARCH.md` |
| `Christianity Atlas` | `Christianity Research` |
| `docs/RELIGIOUS-SYSTEMS-ATLAS.md` | `docs/RELIGIOUS-SYSTEMS-RESEARCH.md` |
| `Religious Systems Atlas` | `Religious Systems Research` |
| `docs/SWAMP-ATLAS.md` | `docs/SWAMP-RESEARCH.md` |
| `Swamp Atlas` | `Swamp Research` |
| `docs/SECTOR-ATLAS-READING-GUIDE.md` | `docs/SECTOR-MODEL-READING-GUIDE.md` |
| `European Sector Atlas` | `European Sector Model` |

The exact replacement noun for additional research documents must be determined from their current purpose, not from a global text substitution.

### 5.6 Programmes and structured domain data

| Current | Canonical replacement |
|---|---|
| `data/north-programme-atlas.json` | `data/north-programme-registry.json` |
| North Programme Atlas | North Programme Registry / North Programme, depending sentence context |

Other `*-atlas.json` files must be classified individually:

- reusable canonical records → `*-registry.json`
- renderable projection → `*-layer.json`
- formal structure → `*-model.json`
- comparison corpus → `*-comparison.json`
- authored analytical corpus → `*-research.json`
- lookup/navigation → `*-index.json`

There must be no blind `atlas → registry` substitution.

---

## 6. Specialist religious and biblical files

The repository contains many specialist files whose names end in `-atlas.json`. These are not all the same kind of object.

Migration must inspect each file's stated purpose and classify it by function.

Examples of the decision rule:

- a corpus that maps Tim/Son claims against biblical texts is usually a **comparison**;
- a reusable set of entities or motifs is a **registry**;
- a synthesized interpretive investigation is **research**;
- a formal structural representation is a **model**;
- a public/map-selectable projection is a **layer**.

This classification is itself part of the cleanup value. It forces ambiguous backend objects to acquire explicit ownership instead of preserving a catch-all category under another name.

No specialist religious file becomes a new public page merely because it is renamed.

---

## 7. Historical design documents

Previous implementation plans and specs legitimately describe the old architecture and use `Atlas` heavily.

They should not remain active architectural guidance after this migration.

Old Atlas-specific plans/specs should be moved into an internal design-history area such as:

`archive/legacy/design-history/`

The archive is already excluded from the Pages artifact. Historical filenames and wording may remain unchanged there because their purpose is provenance, not active architecture.

Git history also preserves the original terminology permanently; therefore there is no need to retain stale naming in active documentation merely for historical reasons.

The new World Map unification spec becomes the governing architecture for this area.

---

## 8. Runtime and data ownership

`data/world-map-runtime.json` remains a strong canonical runtime owner and keeps its filename.

Its wording and internal references should change from `World Relational Atlas` / `Atlas` to `World Map` or the precise module names established here.

The World Map runtime should express the following rule:

> Geography says where; canonical records say what; typed relationships say how things connect; time says when a record or relation applies; provenance says why it should be trusted; the World Map renders and routes across those owners without cloning them.

That principle already exists in the current runtime and should be preserved.

The migration must not collapse all country, religion, economics, institution, timeline or project data into one `world-map.json`. A single enormous data file would make the architecture harder to reason about and would undo the purpose of the cleanup.

### 8.1 `data/world-relational-map.json`

This file must be audited during migration. Its current title and role mix the former Atlas language with project-axis and membership data.

If it remains a reusable World Map-owned relationship/configuration object, rename it according to actual contents, preferably one of:

- `data/world-map-relations.json`
- `data/world-map-fields.json`
- split into existing precise owners if the file currently combines unrelated responsibilities.

The implementation plan should choose the smallest option that reduces duplication. It must not create another top-level system named “World Relational Map” alongside World Map.

---

## 9. UI consolidation

The canonical `/world-map/` application should preserve the current 3D map's useful architecture:

- direct country selection/deselection;
- multi-selection and comparison;
- relationship lines and typed relation filters;
- country inspector;
- search;
- demographic and religion views;
- time mode;
- network trace/pathfinding;
- evidence/provenance;
- country dimensions/statistics;
- North/East/West/South and related project fields;
- clean progressive disclosure rather than a giant tool dashboard.

This migration is not permission for another broad UI redesign. The objective is ownership and naming simplification first.

Before retiring the 2D map, compare its unique features with the 3D application. Candidate 2D-only functionality currently includes some direct layers for project axis, alliances, BRICS, archive coverage, neighbors, relations, ledger and tikkun. Preserve a feature only where it improves the canonical map and has a clear owner.

The 3D application's existing `More → 2D map` option must disappear when the duplicate renderer is retired.

The current `More → Archive home` wording should also be reviewed; the map should return to the canonical site Home rather than suggesting the whole public site is an archive.

---

## 10. Public navigation and discovery

All canonical public links must point to `/world-map/`:

- homepage
- Tim Dooley page
- Religion
- Philosophy
- Science
- North pages
- context/reader pages
- sitemap
- machine-readable discovery
- structured data where relevant

`/world-map/3d.html` must not appear as a canonical sitemap entry after migration.

No `/atlas/` route should be created.

The homepage continues to expose one item only:

**World Map**

No additional Atlas card, World Atlas card, Country Atlas card or backend research collection appears in top-level navigation.

---

## 11. Naming invariant

A permanent validator should enforce the new vocabulary.

Proposed validator:

`scripts/validate_world_map_naming.py`

The validator scans the active repository case-insensitively for `atlas` in:

- active filenames and directory names;
- public HTML/UI copy;
- data IDs and titles;
- scripts and validator names;
- JS identifiers and CSS classes used as architectural names;
- active Markdown architecture/research docs;
- manifests, sitemap and discovery files;
- workflow commands.

Allowed exclusions:

1. `archive/`, because it contains historical implementation/design provenance and is not deployed;
2. literal quoted historical/source text where the source itself used the word, if such a case genuinely exists and is narrowly documented;
3. third-party/vendor material that cannot reasonably be renamed and is not project architecture.

The validator must not contain a broad arbitrary allow-list that lets active project naming drift back in.

---

## 12. Migration mechanics

The migration should be performed atomically enough that the repository does not maintain permanent old/new aliases.

Temporary compatibility is acceptable only for public URLs where external links may exist:

- `/world-map/3d.html` → `/world-map/`

Internal JSON paths, Python scripts, JS imports, IDs and docs should be migrated to their new names and all consumers updated. Do not permanently keep both `country-atlas.json` and `country-registry.json`, for example.

Path migration should use Git moves where possible so history remains legible.

Every moved file must have all exact repository references rewritten and validated.

---

## 13. Migration waves

### Wave 1 — Complete inventory and classification

Build a machine-readable inventory of every active case-insensitive `atlas` occurrence outside `archive/`.

Classify each as:

- World Map system
- registry
- layer
- model
- research
- index
- method
- comparison
- programme
- historical design material
- quoted/external terminology

The classification becomes the rename map for later waves.

### Wave 2 — Canonical public World Map

- move the current 3D application into `world-map/index.html`;
- preserve useful 2D-only capabilities where justified;
- archive the old 2D renderer;
- make `world-map/3d.html` a noindex redirect;
- update canonical metadata and public links;
- remove duplicate renderer navigation.

### Wave 3 — Core World Map runtime and code

Rename World Map application identifiers, validators, runtime wording and core layer-stack paths.

Update all consumers and CI commands in the same wave.

### Wave 4 — Domain owners

Rename country, relationship, symbol, programme, religious, sector and specialist files according to the vocabulary contract.

This wave should prefer consolidation where two Atlas-named objects are discovered to serve the same real purpose.

### Wave 5 — Documentation and design history

Move superseded Atlas-specific specs/plans into internal design history; rename active docs; update README, project structure, TODO and source-authority guidance.

### Wave 6 — Discovery and CI

Update sitemap, manifest, llms/discovery content, navigation validators, quality workflow, Pages workflow and country refresh workflow.

### Wave 7 — Negative guard and final verification

Enable the no-Atlas naming validator only after migration, then require it in normal quality and Pages CI.

---

## 14. Verification contract

### Public route

- `/world-map/` contains the real application.
- `/world-map/3d.html` is redirect-only and `noindex`.
- old 2D renderer is not publicly reachable as a competing canonical application.
- sitemap contains `/world-map/`, not `/world-map/3d.html`.

### Functionality

- current World Map boot succeeds;
- country selection and deselection work;
- multi-selection/compare works;
- map layers load;
- relationship rendering works;
- time mode works;
- evidence/provenance paths resolve;
- religion/demographic projections load;
- World Map data dependencies resolve after path renames;
- JS syntax/module loading passes;
- existing World Map structural/math/pathfinding tests are migrated and pass under their new names.

### Naming

Outside permitted historical/vendor exclusions:

- no active path contains `atlas` case-insensitively;
- no project UI says Atlas;
- no active architecture document defines an Atlas system;
- no data title/id declares an Atlas;
- no validator/audit/refresh script uses Atlas as the project abstraction;
- no canonical discovery entry refers to World Relational Atlas.

### Sitewide

- homepage and primary branches link to `/world-map/`;
- no broken references from renamed files;
- normal Timeline/Bible/Science checks continue to pass;
- Pages artifact excludes `archive/`;
- public site shell validation passes.

---

## 15. Non-goals

This migration will not:

- turn all map-related data into one monolithic file;
- create a new `/atlas/` page;
- create a separate World Atlas product;
- add new public pages for renamed backend research;
- delete unique research merely because its old name contained Atlas;
- rewrite literal historical quotations unnecessarily;
- flatten empirical, interpretive and Potatoverse/project-canon data into one epistemic category;
- redesign the World Map UI for aesthetic reasons unrelated to consolidation;
- change Timeline, Religion, Philosophy, Science or Bible ownership except where their links/references must be updated;
- retain permanent duplicate old/new backend filenames for compatibility.

---

## 16. End state

A visitor sees one destination: **World Map**.

A developer sees one owning spatial product: **World Map**.

The World Map is built from clearly named modules and canonical data owners rather than from a vague family of Atlases.

Elsewhere in the repository, objects describe themselves by function: registries are registries, models are models, research is research, comparisons are comparisons, and layers are layers.

The term **Atlas** no longer acts as a project architecture primitive.