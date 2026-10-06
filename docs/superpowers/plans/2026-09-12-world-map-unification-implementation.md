# World Map Unification Implementation Plan

> Governing design: `docs/superpowers/specs/2026-09-12-world-map-unification-design.md`

**Goal:** Replace the active catch-all “Atlas” architecture with one canonical public **World Map** and precise internal owners such as registry, layer, model, research, comparison and method.

**Execution branch:** `world-map-unification-exec`

**Safety rule:** no blind global `atlas -> registry` replacement. Every active Atlas-named object must be classified by actual function before it moves.

---

## Phase 0 — Establish a measurable migration gate

### Task 0.1 — Add a World Map ownership validator

Create `scripts/validate_world_map_ownership.py` that initially checks only the first public-ownership invariants:

- `/world-map/index.html` is the canonical application and identifies itself as **World Map**.
- `/world-map/3d.html` is compatibility-only: `noindex` plus redirect to `./` / `index.html`.
- canonical public discovery must not prefer `world-map/3d.html`.
- the canonical map UI must not offer a link back to a competing “2D map”.

Add it to `quality-checks.yml` and `pages.yml`.

**Red requirement:** commit the validator before changing the current World Map files and observe the PR check fail for the expected reasons.

**Green requirement:** after Phase 1 implementation, the same validator passes without weakening its assertions.

---

## Phase 1 — Make `/world-map/` the one public map

### Task 1.1 — Inventory unique behavior in the old 2D renderer

Compare:

- `world-map/index.html` (old 2D Leaflet implementation)
- `world-map/3d.html` (current primary 3D application)

Record features present only in 2D and classify each:

- migrate now because it clearly improves the canonical map;
- already superseded in 3D;
- archive because it is stale/duplicate.

Do not redesign the control surface during this phase.

### Task 1.2 — Promote the 3D application

- preserve old 2D `world-map/index.html` under `archive/legacy/world-map/` if it contains unique implementation history worth keeping;
- replace `world-map/index.html` with the current 3D application;
- update title, metadata and visible brand from World Relational Atlas / Atlas to **World Map**;
- remove the “2D map” alternate-product navigation;
- change misleading “Archive home” map navigation to canonical site Home where appropriate.

### Task 1.3 — Convert `world-map/3d.html` to compatibility redirect

The redirect page must:

- contain `meta name="robots" content="noindex"`;
- redirect to `./`;
- provide a normal fallback link to `./`;
- contain no map implementation.

### Task 1.4 — Update canonical links and discovery

Find and replace active canonical references to `world-map/3d.html` with `world-map/` in:

- homepage and branch navigation;
- sitemap / discovery manifests;
- machine-readable project surfaces;
- active docs that instruct readers to open the map.

Do not rewrite archived historical design documents yet.

---

## Phase 2 — Build the complete Atlas inventory

### Task 2.1 — Generate active occurrence inventory

Create `scripts/inventory_atlas_terms.py` or an equivalent one-shot migration report that recursively inventories case-insensitive `atlas` occurrences outside exclusions:

- `.git/`
- `_site/`
- `archive/`
- vendored third-party code where unavoidable

For each occurrence record:

- path;
- occurrence type: filename / content / identifier;
- short context;
- proposed owner class.

### Task 2.2 — Classify every active Atlas owner

Classify active objects as one of:

- World Map
- registry
- layer
- model
- research
- comparison
- method
- index
- programme
- historical design material
- quoted/external terminology

Write the resulting migration table to:

`docs/superpowers/plans/2026-09-12-world-map-atlas-inventory.md`

This file is a migration working document, not a public knowledge page.

---

## Phase 3 — Rename core World Map runtime and validators

Perform path moves plus consumer updates atomically.

Expected primary moves:

- `scripts/validate_atlas.py` -> `scripts/validate_world_map.py`
- `scripts/audit_atlas_links.py` -> `scripts/audit_world_map_links.py`
- `scripts/validate_atlas_view_contracts.py` -> `scripts/validate_world_map_view_contracts.py`
- `scripts/validate_atlas_math_calibration.py` -> `scripts/validate_world_map_math_calibration.py`
- `knowledge/core/world-atlas-integrated-layer-stack.json` -> `knowledge/core/world-map-layer-stack.json`

Update:

- Python imports and literal paths;
- workflow command names and step labels;
- JS identifiers such as `atlasApp`, `atlasTimeState` where they denote the map application;
- runtime titles/descriptions in `data/world-map-runtime.json` and related active files.

Run all renamed validators after each coherent move set.

---

## Phase 4 — Rename precise domain owners

### Country

- `data/country-atlas.json` -> `data/country-registry.json`
- `scripts/refresh_country_atlas.py` -> `scripts/refresh_country_registry.py`
- update country refresh workflow and all consumers.

### Symbols

- `docs/SYMBOL-ATLAS.md` -> `docs/SYMBOL-REGISTRY.md`
- replace active “Symbol Atlas” references with “Symbol Registry”.

### Shared relationship vocabulary

- inspect `docs/KINGDOM-ATLAS.md` and its consumers;
- if it is the shared relationship vocabulary described by the design, move to `docs/RELATIONSHIP-SYSTEM.md`;
- use “Relationship Registry” only if a separate record collection actually exists.

### Research documents

Expected moves after content inspection:

- `docs/CHRISTIANITY-ATLAS.md` -> `docs/CHRISTIANITY-RESEARCH.md`
- `docs/RELIGIOUS-SYSTEMS-ATLAS.md` -> `docs/RELIGIOUS-SYSTEMS-RESEARCH.md`
- `docs/SWAMP-ATLAS.md` -> `docs/SWAMP-RESEARCH.md`
- `docs/SECTOR-ATLAS-READING-GUIDE.md` -> `docs/SECTOR-MODEL-READING-GUIDE.md`

### Programme data

- inspect `data/north-programme-atlas.json`;
- if it is a reusable structured programme record parent, move to `data/north-programme-registry.json`.

### Specialist `*-atlas.json`

Inspect each file independently and choose among `registry`, `layer`, `model`, `research`, `comparison`, `method`, `index`, or consolidation into an existing owner.

Do not create new public routes for these backend renames.

---

## Phase 5 — Retire stale active design guidance

Move superseded Atlas-specific implementation plans/specs to:

`archive/legacy/design-history/`

Preserve their historical wording there.

Update active architecture docs, especially:

- `README.md`
- `docs/PROJECT-STRUCTURE.md`
- active TODO/roadmap/source-authority material

so they point to World Map and precise domain owners.

---

## Phase 6 — Enforce the final naming invariant

Create `scripts/validate_world_map_naming.py`.

It must reject active project uses of case-insensitive `atlas` in:

- active project paths;
- public UI copy;
- project-defined JSON IDs/titles;
- active JS/CSS/Python architectural identifiers;
- active documentation;
- manifests/discovery/workflows.

Narrow exclusions only:

- `archive/`;
- external/vendor code;
- a specifically documented literal historical quotation when unavoidable.

Add this validator to both `quality-checks.yml` and `pages.yml` only after the active migration is complete.

---

## Phase 7 — Whole-project verification

Run/verify at minimum:

- repository hygiene;
- World Map ownership validator;
- final World Map naming validator;
- World Map structure/runtime validator;
- view/time contracts;
- mathematical calibration;
- pathfinder;
- entity trace;
- link/record coverage audit;
- web audit;
- site build;
- public navigation;
- machine discoverability;
- site shell;
- Timeline naming;
- Bible reader/build;
- Science build/validation;
- archive absent from Pages artifact.

Also verify manually from built/static content:

- `/world-map/` is the real application;
- `/world-map/3d.html` is redirect-only and `noindex`;
- no canonical nav/discovery entry points at `3d.html`;
- no competing 2D map control exists;
- old archived implementation is not deployed.

---

## Commit strategy

Keep migration commits reviewable and coherent:

1. `test: define canonical World Map ownership`
2. `refactor: make World Map the canonical public map`
3. `docs: inventory active Atlas architecture`
4. `refactor: rename World Map runtime and validators`
5. `refactor: rename country and domain owners`
6. `docs: archive superseded Atlas design guidance`
7. `test: forbid active Atlas architecture naming`
8. final fixes from full verification

Do not merge partial old/new backend aliases into `main` as a permanent state.
