# World Atlas Composable Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the ordinary single-Lens bootstrap path with a registry-driven composable layer foundation that supports one scalar fill, multiple categorical memberships, ANY/ALL query state, and a compact adaptive top bar.

**Architecture:** Add a browser-facing registry projection over existing canonical data owners, then load it through focused registry/compositor/query/UI modules. Keep the existing MapLibre renderer and selection subsystem authoritative; the new compositor only owns analytical fill/pattern layers and never selection outlines.

**Tech Stack:** Static JSON, ES modules, MapLibre GL JS, Python validation scripts.

**Spec:** `docs/superpowers/specs/2026-09-11-world-atlas-composable-registry-design.md`

## Global Constraints

- Core geography must remain usable if optional registry data fails.
- Selection remains an outline/state concern and must never be encoded as analytical fill.
- Exactly one scalar layer may own base country fill at a time.
- Multiple set layers may coexist through pattern composition.
- Observed, derived and project-interpretive entries retain explicit epistemic classes.
- Missing scalar data is unknown, never zero.
- Browser data remains same-origin; no mandatory live external API dependency.
- Existing Time, Evidence, Trace and Axis specialist modules remain available during migration.

---

### Task 1: Registry projection and schema

**Files:**
- Create: `data/world-atlas-layer-registry.json`
- Create: `scripts/validate_world_atlas_layer_registry.py`

**Interfaces:**
- Produces registry JSON with `families`, `entries`, `relation_families`, `query_rules`, and `visual_channels`.
- Validator exits non-zero on duplicate ids, unknown family/kind/channel, invalid scalar/pattern channel use, or missing epistemic/source metadata.

- [ ] Write registry JSON containing implemented Axis/groups/religion/basic metrics plus wider discovered families as `planned` entries.
- [ ] Write validation script with explicit allowed enum sets and channel/kind rules.
- [ ] Run `python scripts/validate_world_atlas_layer_registry.py` and require PASS.
- [ ] Commit registry + validator.

### Task 2: Browser registry API

**Files:**
- Create: `world-map/3d-layer-registry.js`

**Interfaces:**
- Produces `window.__potatoAtlasLayers` with `ready`, `registry`, `get(id)`, `family(id)`, `entries(family,{availableOnly})`, `activate(id)`, `deactivate(id)`, `toggle(id)`, `active()`, `reset()`.
- Emits `potato-atlas-layer-change`.

- [ ] Implement same-origin registry fetch with graceful failure state.
- [ ] Normalize and index entries/families without duplicating canonical values.
- [ ] Implement active-state API and custom event.
- [ ] Add URL `layers=` round-trip for valid available ids.
- [ ] Verify module syntax with a parser/static check.
- [ ] Commit registry API.

### Task 3: Compositor and query engine foundation

**Files:**
- Create: `world-map/3d-compositor.js`

**Interfaces:**
- Consumes `window.__potatoAtlasLayers`, `data/world-relational-map.json`, `data/world-country-demography.json`.
- Produces `window.__potatoAtlasCompositor` with `render()`, `state()`, `reset()`.
- Produces `window.__potatoAtlasQuery` with `setMode()`, `getMode()`, `matches(iso3)`, `matchedCountries()`.
- Emits `potato-atlas-query-change` and `potato-atlas-composition-change`.

- [ ] Implement project Axis and empirical membership set resolution from existing canonical world data.
- [ ] Implement religion share feature-state loading from existing demography runtime.
- [ ] Implement one scalar-fill owner with neutral fallback.
- [ ] Add a separate MapLibre `atlas-composition-fill` layer so categorical pattern membership does not overwrite scalar fill.
- [ ] Generate/caches deterministic 1–3 color stripe images and map ISO3 combinations to `fill-pattern`.
- [ ] Use overlap-count fallback for >3 active categorical sets.
- [ ] Implement ANY/ALL matching for available set layers and preserve room for scalar predicates.
- [ ] Commit compositor/query foundation.

### Task 4: Compact registry-driven world bar

**Files:**
- Create: `world-map/3d-world-bar.js`

**Interfaces:**
- Consumes layer registry API + query API.
- Injects one ordinary map control surface into `.mapwrap`.
- Direct controls: `N W E S`; generated menus: `Groups`, `Religion`, `Stats`, `Relations`; contextual `ANY/ALL`; `Reset`.

- [ ] Build controls from registry families, not hard-coded option lists except direct Axis shortcut ids.
- [ ] Hide planned/unavailable entries from ordinary menus.
- [ ] Keep menus mutually exclusive and keyboard-focusable.
- [ ] Show active layer count and contextual ANY/ALL only when two or more queryable layers are active.
- [ ] Add responsive CSS inside the module without introducing another permanent panel.
- [ ] Commit compact world bar.

### Task 5: Bootstrap migration

**Files:**
- Modify: `world-map/3d-bootstrap.js`

**Interfaces:**
- Immediate lightweight modules become: Progressive UI, Selection UI, Country selection, Layer Registry, Compositor, World Bar.
- `3d-lenses.js` is no longer booted as an ordinary fill owner.

- [ ] Load registry after country selection.
- [ ] Load compositor after registry.
- [ ] Load world bar after compositor.
- [ ] Remove immediate `Lenses` boot to prevent conflicting fill ownership.
- [ ] Keep legacy/deeper modules dormant and compatible.
- [ ] Commit bootstrap migration.

### Task 6: Validation and branch review

**Files:**
- Modify if necessary: `scripts/validate_world_map_3d.py`
- Inspect: changed files on `atlas-composable-registry`.

**Interfaces:**
- Validation asserts registry/bootstrap contracts and no ordinary immediate Lens boot.

- [ ] Extend existing validator only where it can make deterministic source assertions.
- [ ] Run registry validator and existing 3D map validator.
- [ ] Inspect branch diff for accidental UI duplication or semantic conflicts.
- [ ] Confirm `main` is untouched and branch contains only the intended first slice.
- [ ] Open PR for review rather than force-updating `main`.