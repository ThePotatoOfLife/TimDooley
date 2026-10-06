# World Map Entity, Greenland & Africa Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix population-label misplacement, make Greenland a first-class non-sovereign map entity, and deepen Africa through current regional systems plus selective evidence-backed Axis overlays.

**Architecture:** Preserve `data/countries/index.json` as the 195-sovereign-country owner and add a separate entity owner for Greenland/territories. Generate one runtime projection that resolves countries and territories, then make population labels and selection/card behavior consume that resolver. Add a dedicated African regional-systems owner and project it into runtime/chains without inferring Axis membership from REC membership.

**Tech Stack:** Python runtime builders/validators, JSON canonical data owners, MapLibre GL JS browser modules, GitHub Actions quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-12-world-map-entity-africa-repair-design.md`

## Global Constraints

- Sovereign-country count remains exactly 195.
- Greenland must never be described as a sovereign country.
- Population label placement must resolve from the same map entity as the population observation; REST `latlng` is not authoritative.
- Geometry-wide bounding-box midpoints are forbidden for population/entity label anchors.
- African REC membership never automatically creates an Axis orientation.
- Missing/unknown stays unknown; do not invent alignment, capability or resilience scores.
- No new permanent Africa/territory toolbox or top-bar clutter.

---

### Task 1: Add the failing entity/population/Africa contract

**Files:**
- Create: `scripts/validate_world_map_entity_africa_repair.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: current country index, axis profiles, memberships, runtime builder, demography module.
- Produces: one CI gate named `Validate World Map entity and Africa repair`.

- [ ] **Step 1: Write the failing validator**

The validator must assert:

```python
assert len(country_index["countries"]) == 195
assert entities["entities"]["GRL"]["canonical_country"] is False
assert entities["entities"]["GRL"]["constitutional_parent"] == "DNK"
assert entities["entities"]["GRL"]["population"]["source_url"].startswith("https://stat.gl/")
assert len(africa["systems"]["eac"]["members"]) == 8
assert len(africa["systems"]["sadc"]["members"]) == 16
assert set(africa["systems"]["ecowas"]["members"]).isdisjoint({"BFA","MLI","NER"})
assert set(africa["systems"]["eac"]["members"]) & set(africa["systems"]["sadc"]["members"]) >= {"COD","TZA"}
```

It must also scan browser/runtime source for these required behaviors:

```text
entity(code)
labelAnchor(code)
populationObservation(code)
world-map-entities.json
world-africa-regional-systems.json
population-label-anchor
```

And reject these old patterns for population-label placement:

```text
geometry-wide bbox midpoint used as label anchor
REST `latlng` consumed directly by `addPopulationLabels`
```

Include an antimeridian fixture representing a Russia-like multi-part geometry and require the helper used by the builder/resolver to return an anchor inside the selected component rather than near longitude 0.

- [ ] **Step 2: Wire the validator into the canonical quality workflow**

Add immediately after the existing World Map functional-chain/system-intelligence gates:

```yaml
      - name: Validate World Map entity and Africa repair
        run: python scripts/validate_world_map_entity_africa_repair.py
```

- [ ] **Step 3: Run CI and verify RED**

Expected: all earlier World Map gates pass and this new gate fails because `world-map-entities.json` / Africa systems / entity APIs do not yet exist.

- [ ] **Step 4: Commit the red contract**

Commit message:

```text
test(world-map): define entity and Africa repair contract
```

---

### Task 2: Add first-class map entities and safe label anchors

**Files:**
- Create: `data/world-map-entities.json`
- Create: `scripts/world_map_entity_utils.py`
- Modify: `scripts/build_world_demography.py`
- Modify: `world-map/3d-demography.js`
- Modify: `world-map/3d-hover.js`

**Interfaces:**
- Produces Python `representative_component_anchor(feature: dict) -> list[float] | None` where output is `[lon, lat]`.
- Produces entity records keyed by ISO3-like map code.
- Browser population labels consume entity-owned `label_anchor` or a geometry-derived safe anchor from the same entity.

- [ ] **Step 1: Add Greenland entity data**

`data/world-map-entities.json` must begin with:

```json
{
  "version":"1.0.0",
  "updated":"2026-09-12",
  "entities":{
    "GRL":{
      "id":"greenland",
      "iso3":"GRL",
      "name":"Greenland",
      "entity_type":"self-governing-territory",
      "canonical_country":false,
      "sovereignty_context":"Kingdom of Denmark",
      "constitutional_parent":"DNK",
      "capital":"Nuuk",
      "render_status":"current",
      "label_anchor":{"coordinates":[-51.7216,64.1835],"kind":"display-anchor","place":"Nuuk"},
      "population":{"value":56740,"reference_date":"2026-01-01","source":"Statistics Greenland","source_url":"https://stat.gl/publ/en/BE/202601/contents/Population%20estimates.htm"}
    }
  }
}
```

- [ ] **Step 2: Implement antimeridian-safe geometry fallback**

In `scripts/world_map_entity_utils.py`, implement `representative_component_anchor` by extracting polygon components, computing planar ring area for each outer ring, selecting the largest component, and returning a point derived from that component only. If its polygon centroid falls outside the ring, fall back to an actual ring vertex or segment midpoint verified against that component. Never average longitude extremes across multiple components.

- [ ] **Step 3: Project Greenland into demography runtime**

`build_world_demography.py` loads `world-map-entities.json` and adds non-country renderable entities to a separate top-level `entities` object in `world-country-demography.json`; do not increment the 195-country coverage counters.

- [ ] **Step 4: Replace label coordinate authority**

`3d-demography.js` must stop fetching REST Countries solely to position population labels. It should read the geometry source already owned by the map plus runtime/entity anchors, build one point per resolvable entity, and attach `iso3`, `name`, `population`, `population_label`, `population_year`, and `anchor_kind` to the same feature.

- [ ] **Step 5: Remove unsafe browser bbox synthesis**

`3d-hover.js` may retain a resilient country fallback, but its `representativePoint` implementation must become antimeridian/component safe or defer to entity anchors. No geometry-wide min/max midpoint may remain.

- [ ] **Step 6: Run validator locally through CI and make the population-anchor portion GREEN**

Expected: antimeridian fixture passes; Greenland entity checks pass; Africa checks remain red until Task 4.

- [ ] **Step 7: Commit**

```text
fix(world-map): anchor population labels to map entities
```

---

### Task 3: Extend the World Map runtime and browser resolver to Greenland

**Files:**
- Modify: `scripts/build_world_map_runtime.py`
- Modify: `world-map/3d-compositor.js`
- Modify: `world-map/3d-country-selection.js`
- Modify: `world-map/3d-country-card.js`
- Modify: `data/world-axis-profiles.json`
- Modify: `data/world-system-chains.json`
- Modify: `data/world-relational-map.json`

**Interfaces:**
- Runtime adds `entities.by_id` / `entities.territories` while retaining `country_count: 195`.
- Browser runtime API adds `entity(code)`, `entityName(code)`, `entityType(code)`, `populationObservation(code)`, `labelAnchor(code)`.

- [ ] **Step 1: Load and project map entities in the runtime builder**

Add `ENTITIES = ROOT / "data" / "world-map-entities.json"`. Build `runtime_entities` from country index plus territory owner without duplicating country records.

For `GRL`, runtime projection must include:

```json
{
  "code":"GRL",
  "name":"Greenland",
  "entity_type":"self-governing-territory",
  "canonical_country":false,
  "population":{...},
  "label_anchor":{...},
  "constitutional_parent":"DNK",
  "systems":{"chains":["arctic","north-atlantic"]}
}
```

- [ ] **Step 2: Extend Axis projection to supported territories**

Add `GRL` to `world-axis-profiles.json` as North `primary`, basis `explicit-tim`, confidence `high`, with wording that it is a project North anchor and not a sovereignty claim.

Axis runtime should expose a territory profile without adding `GRL` to sovereign `country_count`.

- [ ] **Step 3: Add Greenland to functional chains and relation graph**

Add `GRL` to Arctic and North Atlantic chain member arrays. Add a curated DNK↔GRL empirical constitutional/fiscal/infrastructure/security/culture edge in `world-relational-map.json`.

- [ ] **Step 4: Add browser entity APIs**

Extend `window.__potatoAtlasDataRuntime` with the five entity methods. Existing country methods continue to work.

- [ ] **Step 5: Make selection entity-aware**

`3d-country-selection.js` should accept codes known either through country names/REST or the entity runtime. `GRL` becomes selectable even though absent from `data/countries/index.json`.

- [ ] **Step 6: Make the country card entity-aware**

When selected code is `GRL`, card eyebrow/header must read `Self-governing territory · GRL`, show population/source date, capital Nuuk, constitutional relationship to Denmark, Axis context and chains. It must not show `Canonical country`.

- [ ] **Step 7: Run CI and verify Greenland/runtime gates GREEN**

Expected: `GRL` resolves through runtime, card and selection source contracts; `country_count` remains 195.

- [ ] **Step 8: Commit**

```text
feat(world-map): make Greenland a first-class map entity
```

---

### Task 4: Add Africa regional systems as empirical substrate

**Files:**
- Create: `data/world-africa-regional-systems.json`
- Modify: `scripts/build_world_map_runtime.py`
- Modify: `data/world-institution-memberships.json`
- Modify: `data/world-system-chains.json`
- Modify: `world-map/3d-country-card.js`

**Interfaces:**
- Canonical Africa owner exposes `systems` keyed by REC id and historical/current status.
- Runtime exposes `africa.systems` and `africa.for_country`.
- Country card shows compact African regional memberships when present.

- [ ] **Step 1: Encode current official Africa systems**

Use current official sources verified on 2026-09-12:

- AU RECs: `https://au.int/en/recs`
- EAC: `https://www.eac.int/overview-of-eac`
- SADC: `https://www.sadc.int/member-states`
- ECOWAS current members: `https://www.ecowas.int/?page_id=40`
- ECOWAS withdrawal transition: `https://www.ecowas.int/press-statement-2/`

At minimum encode EAC 8, SADC 16, ECOWAS 12 current members and former/current-transition status for `BFA`, `MLI`, `NER` effective `2025-01-29`. Also record that the AU recognises eight RECs, with provenance for the REC list.

- [ ] **Step 2: Prevent duplicate membership authority**

Keep `world-africa-regional-systems.json` as detailed owner. In `world-institution-memberships.json`, either project/summarize current EAC/ECOWAS groups from this owner through the runtime builder or add only source pointers; do not maintain divergent hand-copied status histories.

- [ ] **Step 3: Add African functional chains**

Add:

```text
east-african-integration
west-african-integration
sahel-transition
north-african-mediterranean
african-continental-integration
```

Deepen `southern-african` with SADC as its empirical membership spine. Each chain must have `epistemic_type`, `systems`, `description`, `source_note` and members.

- [ ] **Step 4: Project regional memberships into runtime**

For each African sovereign country, runtime `systems.regional` gets current systems plus status metadata. `COD` and `TZA` must each resolve to both EAC and SADC.

- [ ] **Step 5: Surface compact membership context in the card**

African country cards show up to three regional-system tags plus `+N` overflow. No new permanent menu.

- [ ] **Step 6: Run validator and verify Africa regional-system contracts GREEN**

- [ ] **Step 7: Commit**

```text
feat(world-map): integrate African regional systems
```

---

### Task 5: Add selective African Axis refinements without forced classification

**Files:**
- Modify: `data/world-axis-profiles.json`
- Modify: `scripts/validate_world_axis_systems.py`

**Interfaces:**
- Axis orientations retain `{axis, role, basis, confidence, note}`.
- REC membership never generates orientations automatically.

- [ ] **Step 1: Add only the approved profiles**

Add/refine:

- `EGY`: East secondary retained + West bridge (`empirical-correspondence`, MNNA).
- `ETH`: East secondary retained.
- `NGA`: East bridge (`empirical-correspondence`, BRICS partner), with West African regional context separate.
- `UGA`: East bridge (`empirical-correspondence`, BRICS partner), EAC context separate.
- `MAR`: North bridge + West secondary/bridge based on EU strategic partnership + MNNA.
- `TUN`: North bridge + West secondary based on Euro-Mediterranean context + MNNA.
- `DZA`: North frontier, low/medium confidence; do not mark primary.
- `KEN`: West secondary/bridge via MNNA; EAC stays separate.
- `TZA`: South secondary/bridge; preserve EAC+SADC overlap separately.
- `AGO`: South secondary.
- `COD`: remain unresolved directionally.

Current official evidence sources:

- U.S. MNNA list: `https://samm.dsca.mil/glossary/major-non-nato-allies`
- BRICS partner status for Nigeria/Uganda: `https://brics.br/en/about-the-brics/frequently-asked-questions-about-the-brics`
- EU-Morocco strategic partnership, 2026-01-29: `https://www.consilium.europa.eu/en/press/press-releases/2026/01/29/communique-conjoint-de-la-haute-representante-kaja-kallas-et-du-ministre-des-affaires-etrangeres-du-maroc-nasser-bourita-suite-a-la-tenue-du-quinzieme-conseil-d-association-ue-maroc/`

- [ ] **Step 2: Strengthen the Axis validator**

Require `COD` unresolved, forbid any code path that derives Axis from REC membership, and require basis/confidence/note on every new African orientation.

- [ ] **Step 3: Run Axis + repair validators**

Expected: both pass.

- [ ] **Step 4: Commit**

```text
feat(world-map): deepen selective African axis context
```

---

### Task 6: Full verification, PR, and integration

**Files:**
- No new production files unless verification reveals a real defect.

**Interfaces:**
- Exact branch head must have a successful canonical `Repository quality checks` run.

- [ ] **Step 1: Verify syntax/build locally through CI contracts**

Required gates include:

```text
Validate JavaScript syntax
Validate World Map data runtime
Validate World Map Axis and systems
Validate World Map system intelligence
Validate World Map functional chain explorer
Validate World Map entity and Africa repair
Validate canonical World Map runtime
Validate World Map UI shell
Build public site
```

- [ ] **Step 2: Open/update PR from `world-map-entity-africa-repair-2026-09-12` to `main`**

PR description must summarize the root cause, entity model, Greenland behavior, Africa regional substrate and selective Axis changes.

- [ ] **Step 3: Verify exact-head full CI GREEN**

Do not claim completion from a previous commit's run.

- [ ] **Step 4: Merge to `main` only after exact-head green**

- [ ] **Step 5: Confirm `main` points at the merge commit**

---

## Self-review

- Spec coverage: population anchor repair, Greenland entity semantics, Africa regional substrate, selective Axis profiles, UI restraint and validation are all mapped to tasks.
- Placeholder scan: no TBD/TODO placeholders.
- Type consistency: entity code is ISO3-like uppercase string; label anchors are `[lon, lat]`; country count remains a separate 195 sovereign count; regional systems are not Axis orientations.
