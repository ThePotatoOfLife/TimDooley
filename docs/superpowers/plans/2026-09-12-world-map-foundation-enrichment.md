# World Map Foundation Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix scalar correctness and entity parity, derive truthful coverage, repair duplicate country ownership, make the intended Eastern European countries visibly participate in the North overlay, expose already-owned comparable Stats, and consolidate core empirical group ownership before infrastructure enrichment begins.

**Architecture:** Wave A strengthens the existing data/runtime substrate without adding a new top-level UI. A focused scalar resolver in the generated World Map runtime becomes the canonical browser-facing source for population, area, and comparable metrics across countries and first-class territories; a generated coverage ledger derives completeness from actual records; canonical country ownership and institutional ownership are repaired at their sources; Axis profiles are updated explicitly so pressing **N** changes the actual rendered polygon membership. Wave B infrastructure work remains separate and starts only after this foundation is green.

**Tech Stack:** Python JSON builders/validators, canonical repository JSON owners, MapLibre browser runtime, existing World Map layer registry/compositor/card/hover, GitHub Actions quality gates.

**Spec:** `docs/superpowers/specs/2026-09-12-world-map-coverage-enrichment-design.md` and `docs/superpowers/specs/2026-09-12-world-map-scalar-integrity-addendum.md`

## Global Constraints

- Canonical sovereign-country count remains exactly 195.
- Greenland remains a first-class non-sovereign entity and must not be counted as a 196th country.
- Missing numeric data renders as unknown/`—`, never `0` solely because resolution failed.
- Population/area/card/hover/Stats must resolve the same entity to the same scalar observation.
- North/West/East/South remain project-interpretive overlays, separate from empirical membership.
- Pressing **N** must visibly include every profile whose North role is an ordinary membership role (`primary`, `secondary`, `bridge`, `shared`).
- Empirical group membership does not automatically create Axis membership.
- No synthetic geopolitical importance, completion, risk, resilience, or power score.
- Do not add a permanent Coverage, Infrastructure, or extra Axis control to the top bar.
- Existing Impact causal guardrails remain unchanged.

---

### Task 1: Define the failing foundation-enrichment contract

**Files:**
- Create: `scripts/validate_world_map_foundation_enrichment.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Imports pure helpers from `scripts/world_map_scalars.py` and `scripts/build_world_map_coverage.py` once implemented.
- Validates generated in-memory runtime via `scripts/build_world_map_runtime.py`.
- CI gate name: `Validate World Map foundation enrichment`.

- [ ] **Step 1: Add scalar regression assertions**

Require:

```python
assert scalar_population("GRL")["value"] == 56740
assert scalar_area("GRL")["value"] == 2166086
assert scalar_area("GRL")["definition"] == "total area"
```

Use a fixture country whose population is present only in a legacy/top-level `population` object and assert the resolver still returns it, proving ordinary countries do not depend solely on `observations.population`.

Require missing scalar fixture returns `None`, not `0`.

- [ ] **Step 2: Add cross-surface source-contract assertions**

Require browser code paths to use shared runtime helpers:

```text
populationObservation
areaObservation
scalarObservation
```

Require `3d-country-card.js`, `3d-entity-runtime.js`, and `3d-hover.js` to reference the shared scalar API for population/area rather than separate schema guesses.

- [ ] **Step 3: Add coverage-ledger assertions**

Require generated ledger:

```text
policy.country_count == 195
policy.missing_is_zero == false
entities includes all 195 country codes
GRL appears as a registered non-country entity
```

Create a synthetic record with stale stored counters but real relationships/sources and assert derived counts follow the actual content.

Create a synthetic duplicate-ISO3 fixture and assert the audit reports it.

- [ ] **Step 4: Add canonical ownership assertions**

Require exactly one active canonical `TUR` owner and require `data/countries/turkiye.json` to contain recovered Turkish-Straits, NATO/G20 and EU-trade context with explicit migration provenance.

The legacy `data/countries/turkey.json` must no longer be an active country owner.

- [ ] **Step 5: Add North-overlay behavior assertions**

Require runtime `axis.memberships.north` to include:

```text
EST UKR TUR LVA LTU POL ROU CZE SVK
```

and require the first-cohort profiles `LVA`, `LTU`, `POL`, `ROU`, `CZE`, `SVK` to carry `axis`, `role`, `basis`, `confidence`, `note`.

Require the layer registry still maps `axis.north` to runtime axis `north`, proving these memberships feed the existing **N** control rather than a new UI.

- [ ] **Step 6: Add Stats-expansion assertions**

Require runtime metric metadata and registry entries for:

```text
gdp_per_capita_ppp
labour_force_participation
life_expectancy
fertility
urbanization
internet_use
co2_per_capita
```

Require current availability only when runtime coverage is greater than zero and each cell preserves unit/period/source.

Poverty may remain planned unless definition metadata proves comparability.

- [ ] **Step 7: Add membership-authority assertions**

Require `nato`, `brics`, `aukus`, `five-eyes` in `data/world-institution-memberships.json` and require corresponding layer-registry entries to point there rather than `world-relational-map.json`.

Compatibility data may remain in the relational map only if marked/projected rather than treated as the browser authority.

- [ ] **Step 8: Wire CI and verify RED**

Add:

```yaml
- name: Validate World Map foundation enrichment
  run: python scripts/validate_world_map_foundation_enrichment.py
```

after existing World Map data/entity/impact contracts. Open a PR and verify all older gates pass before this new gate fails for the missing behavior.

- [ ] **Step 9: Commit**

Commit message:

```text
test(world-map): define foundation enrichment contract
```

---

### Task 2: Build unified population/area scalar resolution

**Files:**
- Create: `scripts/world_map_scalars.py`
- Modify: `data/world-map-entities.json`
- Modify: `scripts/build_world_map_runtime.py`
- Modify: `world-map/3d-entity-runtime.js`
- Modify: `world-map/3d-country-card.js`
- Modify: `world-map/3d-hover.js`

**Interfaces:**

Python:

```python
resolve_population(record: dict, fallback: dict | None = None) -> dict | None
resolve_area(record: dict, fallback: dict | None = None) -> dict | None
```

Browser runtime:

```js
scalarObservation(code, metricId)
populationObservation(code)
areaObservation(code)
```

- [ ] **Step 1: Define scalar precedence**

Population precedence for canonical countries:

```text
observations.population
population object/value
runtime demography fallback
unknown
```

Area precedence:

```text
explicit entity area observation
canonical geography.land_area_km2 / geography.area_km2 / area_km2 with exact definition
generated country-facts fallback
unknown
```

Never reinterpret millions as persons without explicit unit conversion logic.

- [ ] **Step 2: Add Greenland area ownership**

Add to `GRL`:

```json
"area": {
  "value": 2166086,
  "unit": "km²",
  "definition": "total area",
  "source": "Statistics Greenland",
  "source_url": "https://stat.gl/..."
}
```

Population remains 56,740 with its existing 2026-01-01 reference date.

- [ ] **Step 3: Project scalar observations for every renderable entity**

In generated runtime add a scalar plane such as:

```json
"scalars": {
  "by_entity": {
    "GRL": {
      "population": {...},
      "area": {...}
    }
  }
}
```

Countries and territories share one lookup contract; country count remains 195.

- [ ] **Step 4: Extend shared browser runtime**

Implement exact code lookup and expose `scalarObservation`, `populationObservation`, `areaObservation` from the central data runtime or entity extension without duplicating selection logic.

- [ ] **Step 5: Make card and hover consume shared values**

Country card default Population and `stat.population`/`stat.area` comparison rows must prefer the shared scalar runtime.

Hover must prefer shared population/area and use fact/property fallback only if the shared runtime has no observation.

For unknown values display `—`; never display `0` unless zero is an actual sourced value.

- [ ] **Step 6: Verify GREEN for scalar section**

Run the new foundation validator and existing entity/data-runtime validators.

- [ ] **Step 7: Commit**

```text
fix(world-map): unify country and territory scalars
```

---

### Task 3: Generate truthful coverage ledger

**Files:**
- Create: `scripts/build_world_map_coverage.py`
- Generate: `data/world-map-coverage-ledger.json`
- Modify: `scripts/build_site.py`

**Interfaces:**

```python
derive_record_coverage(record: dict) -> dict
audit_country_owners(index_rows: list[dict], country_files: list[Path]) -> dict
build_coverage_ledger() -> dict
```

- [ ] **Step 1: Derive counts from actual content**

Count non-empty observations, relationships, provenance/source references and system domains by inspecting real fields rather than `coverage.*` counters.

- [ ] **Step 2: Derive domain states**

Return `represented`, `partial`, `missing`, `unknown`, or `not-applicable` for the approved coverage dimensions. Do not compute a percentage completion score.

- [ ] **Step 3: Audit ownership and quality flags**

Detect duplicate ISO3 files, canonical-index/record-id disagreement, empty canonical owner with richer duplicate, and registered territories omitted from scalar presentation.

- [ ] **Step 4: Add operational priority reasons**

Expose deterministic reasons in order:

```text
integrity defect
gateway adjacency
multi-chain connector
missing dependency/infrastructure domains
general descriptive gaps
```

Do not expose a geopolitical numeric score.

- [ ] **Step 5: Build during site generation**

`build_site.py` generates the ledger before public-tree copy/validation.

- [ ] **Step 6: Verify**

New validator must prove Egypt-like stale counters do not override actual relationships/sources.

- [ ] **Step 7: Commit**

```text
feat(world-map): derive truthful coverage ledger
```

---

### Task 4: Repair Türkiye canonical ownership

**Files:**
- Modify: `data/countries/turkiye.json`
- Delete or demote: `data/countries/turkey.json`
- Modify if needed: country maintenance/consolidation validator scripts

**Interfaces:**
- Canonical index continues to resolve `TUR -> turkiye`.
- No second active country record may claim ISO3 `TUR`.

- [ ] **Step 1: Migrate structural/context fields**

Recover non-conflicting useful legacy fields from `turkey.json`, including:

```text
Republic of Türkiye identity context
Ankara
Turkish Straits strategic asset/relationship
NATO and G20 membership relationships
EU trade/customs relationship
Black Sea/Aegean/Mediterranean geography
energy/transit/industrial context
```

- [ ] **Step 2: Treat old numeric values as stale/history**

Do not promote the legacy population/GDP point estimates as current 2026 observations merely because they exist. Preserve them only with stale/historical provenance if retained.

- [ ] **Step 3: Record migration provenance**

Add explicit migration provenance pointing to `data/countries/turkey.json` and date `2026-09-12`.

- [ ] **Step 4: Retire duplicate owner**

Delete `turkey.json` if no runtime/API route depends on it; otherwise replace it with a clearly non-authoritative alias structure that cannot be mistaken for a country record. Prefer deletion if canonical index resolves `turkiye.json` everywhere.

- [ ] **Step 5: Verify**

Coverage ledger duplicate flag for `TUR` disappears and all existing country-index validators pass.

- [ ] **Step 6: Commit**

```text
fix(countries): consolidate Türkiye canonical ownership
```

---

### Task 5: Make Eastern European North membership visible under N

**Files:**
- Modify: `data/world-axis-profiles.json`
- Modify if needed: `scripts/validate_world_axis_systems.py`

**Interfaces:**
- Existing runtime builder derives `axis.memberships.north` from ordinary roles.
- Existing `axis.north` layer and **N** control consume that runtime membership; no new browser module is required.

- [ ] **Step 1: Add first-cohort profiles**

Add explicit project-interpretive North orientations:

```text
LVA — primary, project-synthesis, high
LTU — primary, project-synthesis, high
POL — primary, project-synthesis, high
ROU — secondary, project-synthesis, medium
CZE — secondary, project-synthesis, medium
SVK — secondary, project-synthesis, medium
```

Notes must explain their role in the user's broader Canada→Europe→Ukraine→Türkiye North field and distinguish project interpretation from empirical sovereignty/alliance claims.

- [ ] **Step 2: Preserve overlap and frontier semantics**

Do not remove any existing East/West/South orientation where one exists. Do not change Russia/UK frontier semantics.

- [ ] **Step 3: Record second review cohort without auto-classifying**

Do not add ordinary North membership yet for `BGR`, `HUN`, `HRV`, `SVN`, `MDA`. Keep them as the next explicit review cohort in the design/coverage backlog unless project-specific evidence already exists in current profiles.

- [ ] **Step 4: Verify actual rendered membership contract**

Build runtime and assert `axis.memberships.north` contains `LVA`, `LTU`, `POL`, `ROU`, `CZE`, `SVK`.

This is the direct automated proof that pressing **N** will include those polygons because the existing registry points `axis.north` at runtime axis `north`.

- [ ] **Step 5: Commit**

```text
feat(world-map): extend North overlay through eastern Europe
```

---

### Task 6: Expose already-owned comparable Stats

**Files:**
- Modify: `scripts/build_world_map_runtime.py`
- Modify: `data/world-map-layer-registry.json`
- Modify: `scripts/validate_world_map_data_runtime.py`

**Interfaces:**
- Runtime metrics:

```text
gdp_per_capita_ppp
labour_force_participation
life_expectancy
fertility
urbanization
internet_use
co2_per_capita
```

- [ ] **Step 1: Add metric definitions and aliases**

Map canonical World Bank observation keys/indicators with explicit comparable units.

- [ ] **Step 2: Promote only covered metrics**

Registry entries become `current` only when generated runtime coverage is non-zero and cell metadata has value/unit/period/source.

- [ ] **Step 3: Keep poverty gated**

Leave poverty planned unless the specific poverty-line definition and comparability metadata are explicit enough to avoid misleading cross-country comparison.

- [ ] **Step 4: Reuse existing Stats UI**

Do not create a new menu family. These entries appear through the current Stats registry/navigation.

- [ ] **Step 5: Verify**

Data-runtime validator checks real coverage and missing-as-unknown semantics for every newly current metric.

- [ ] **Step 6: Commit**

```text
feat(world-map): expose richer comparable stats
```

---

### Task 7: Consolidate NATO/BRICS/AUKUS/Five Eyes empirical ownership

**Files:**
- Modify: `data/world-institution-memberships.json`
- Modify: `data/world-map-layer-registry.json`
- Modify: `scripts/build_world_map_runtime.py` if metadata needs normalization
- Modify: compatibility consumers only as required

**Interfaces:**
- Canonical group ids:

```text
nato
brics
aukus
five-eyes
```

- [ ] **Step 1: Move canonical membership metadata**

Add member lists, source, source_url, as_of, partner/observer metadata where applicable to the institutional owner.

- [ ] **Step 2: Repoint registry**

All four layer entries use `data/world-institution-memberships.json` as `source_owner` and `groups.<id>.members` as source path.

- [ ] **Step 3: Preserve compatibility without dual authority**

If older modules still read `world-relational-map.json`, update them to prefer shared runtime/institutional groups or clearly mark any remaining list as compatibility-only.

- [ ] **Step 4: Verify**

Validator ensures browser membership and canonical owner agree exactly and no divergent manual list controls the live layer.

- [ ] **Step 5: Commit**

```text
refactor(world-map): consolidate empirical group ownership
```

---

### Task 8: Full integration verification and merge

**Files:**
- No production changes unless a concrete regression is found.

- [ ] **Step 1: Run exact-head repository quality checks**

Require green for all prior World Map validators plus `Validate World Map foundation enrichment`.

- [ ] **Step 2: Verify key generated facts**

Exact-head generated/runtime checks:

```text
GRL population = 56,740
GRL area = 2,166,086 km² total area
ordinary country population works when stored outside observations.population
missing scalar -> unknown, not 0
TUR has one canonical active owner
N membership includes LVA/LTU/POL/ROU/CZE/SVK
new Stats have real coverage and provenance
NATO/BRICS/AUKUS/Five Eyes registry owners are institutional memberships
```

- [ ] **Step 3: Verify PR head has not moved after green CI**

- [ ] **Step 4: Merge with expected exact head SHA**

- [ ] **Step 5: Confirm `main` points to the resulting merge commit**

Do not claim the wave complete before this check.

---

## Deferred Wave B

After Wave A merges, write and execute a separate infrastructure plan implementing:

```text
ports/terminals
power grids/interconnectors
subsea cables/landings/IXPs
pipelines/LNG/storage
rail/freight/border nodes
explicit infrastructure dependencies into Impact
```

Start with Türkiye, Egypt, Indonesia, South Africa, Iran, Panama and Djibouti, then China, India, Kenya, Nigeria and Morocco. Infrastructure facts must be canonical typed nodes with provenance rather than duplicated country prose.

## Self-review

- Every approved Wave A requirement has an implementation task.
- Greenland scalar correctness is tested across shared runtime/card/hover rather than hard-coded in one UI.
- The user's specific **press N → eastern European polygons appear** intent is directly validated through runtime North membership.
- Coverage accounting is derived from actual content rather than stale counters.
- Türkiye duplicate ownership is repaired before fresh enrichment.
- Stats reuse the existing UI.
- Institutional consolidation removes split live authority.
- Infrastructure remains a separate follow-on plan so this PR stays reviewable and testable.
