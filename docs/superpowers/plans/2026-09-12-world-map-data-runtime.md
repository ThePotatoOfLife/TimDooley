# World Map Empirical Data Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the ordinary World Map with trustworthy institutional groups and reusable economic scalar layers without adding UI complexity or duplicating country data in presentation code.

**Architecture:** Add one canonical institutional-membership source and generate one compact `world-map-data-runtime.json` from that source plus canonical country dossiers. The registry declares only supported layers; the compositor resolves all runtime-backed sets/scalars generically; the country card and lower-left context read the same runtime metadata so comparison values, coverage and map shading agree.

**Tech Stack:** Python 3 data projection, JSON canonical/runtime records, browser ES modules, MapLibre feature-state, GitHub Actions validators.

**Spec:** Approved in-chat design on 2026-09-12: generated runtime + richer empirical groups/stats, no extra toolbox or panel.

## Global Constraints

- Keep one centered top toolbar, one upper-left country card and one passive lower-left context surface.
- Missing remains unknown, never zero.
- Cross-country scalars must have comparable units; local-currency GDP must never be ranked as though it were USD GDP.
- Institutional groups must use explicit ISO3 membership and source provenance.
- G20 country polygons represent the 19 country members; EU and African Union remain recorded as non-country members rather than fabricated polygons.
- Bulgaria is a euro-area member from 2026-01-01; 2026 runtime must reflect 21 euro-area countries.
- Generated runtime must retain value, unit, period, source and source URL when available.
- The existing Axis/project-interpretive layers remain epistemically distinct from empirical memberships.

---

### Task 1: Add a failing runtime contract

**Files:**
- Create: `scripts/validate_world_map_data_runtime.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Requires `scripts/build_world_map_runtime.py`, `data/world-institution-memberships.json`, registry-backed runtime group/stat IDs, compositor runtime resolver markers and build integration.
- Produces a CI gate that fails before implementation and passes only when the runtime can be generated from canonical sources.

- [ ] Create validator assertions for six empirical groups: EU, OECD, G7, G20, Schengen, Euro Area.
- [ ] Require runtime-backed stats: GDP/person, real growth, inflation, unemployment and debt/GDP.
- [ ] Require provenance/coverage metadata and unknown-not-zero behavior.
- [ ] Wire validator into repository quality checks before canonical World Map source validation.
- [ ] Verify the exact head fails because the generator/source/runtime integration is missing.

### Task 2: Add canonical institutional memberships and runtime generator

**Files:**
- Create: `data/world-institution-memberships.json`
- Create: `scripts/build_world_map_runtime.py`
- Modify: `scripts/build_site.py`

**Interfaces:**
- `build_runtime()` returns `{version, generated_from, country_count, groups, metrics, countries}`.
- `build_runtime_file(path)` writes the compact browser runtime.
- Group entries expose `members`, `member_count`, `source`, `source_url`, `as_of`; G20 additionally exposes `non_country_members`.
- Metric entries expose metadata/coverage; country metric cells expose normalized `value`, `unit`, `period`, `source`, `source_url`.

- [ ] Encode official 2026 memberships with ISO3 codes and authoritative source URLs.
- [ ] Normalize country dossier observations first, then safe structured fallbacks (`economy`, `public_finance`, `population`, `geography`).
- [ ] Reject non-comparable GDP currency fallbacks from cross-country scalar output.
- [ ] Generate runtime during `build_site.py` before the repository tree is copied to `_site`.
- [ ] Keep generator deterministic except for source-derived freshness metadata; do not fetch external APIs during build.

### Task 3: Promote runtime-backed layers and render them generically

**Files:**
- Modify: `data/world-map-layer-registry.json`
- Modify: `world-map/3d-compositor.js`

**Interfaces:**
- Registry group entries use `source_owner: data/world-institution-memberships.json` and `source_path: groups.<id>.members`.
- Runtime scalar entries use `source_owner: data/world-map-data-runtime.json` and `runtime_metric` keys.
- Compositor exposes `window.__potatoAtlasDataRuntime` with `ready`, `metric`, `metricMeta`, `members`, `coverage`.

- [ ] Promote EU, OECD, G7, G20, Schengen and Euro Area to `current`.
- [ ] Promote GDP/person, real growth, inflation, unemployment and debt/GDP to `current`.
- [ ] Use runtime memberships in the existing pattern/query engine.
- [ ] Use feature-state for runtime scalars and choose scale logic from the registry transform (`log1p`, `diverging-zero`, bounded/linear).
- [ ] Preserve unknown countries as the existing neutral unknown fill.

### Task 4: Make ordinary information surfaces consume the same runtime

**Files:**
- Modify: `world-map/3d-country-card.js`
- Modify: `world-map/3d-world-bar.js`

**Interfaces:**
- Country-card comparison resolves any active runtime scalar through `__potatoAtlasDataRuntime.metric(code, runtimeMetric)`.
- Lower-left context shows compact coverage such as `142/195 countries` plus the metric reference-period range when useful.

- [ ] Extend selected-country comparison to all newly promoted stats.
- [ ] Show active-country runtime scalar in `Current map question`.
- [ ] Show empirical runtime group memberships without replacing dossier memberships.
- [ ] Add compact coverage to lower-left context, not a second legend panel.

### Task 5: Verify exact final head

**Files:**
- Verify generator/validator, JS syntax, canonical World Map validators and full repository workflow.

- [ ] `python scripts/validate_world_map_data_runtime.py` passes.
- [ ] `python scripts/validate_world_map_ui_shell.py` passes.
- [ ] `python scripts/validate_world_map_source.py` passes.
- [ ] Modified World Map JS passes `node --check` through CI.
- [ ] `python scripts/build_site.py` emits `_site/data/world-map-data-runtime.json`.
- [ ] Repository quality checks for the exact final commit conclude `success` before completion is claimed.
