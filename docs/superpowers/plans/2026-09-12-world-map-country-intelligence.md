# World Map Country Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ordinary multi-country exploration materially more useful without adding another panel, nested toolbox, or competing map mode.

**Architecture:** Keep `3d-country-selection.js` as the owner of selected-country state and bounded relation ranking, and keep `3d-country-card.js` as the upper-left contextual information surface. The card consumes the existing selection API plus canonical country dossiers: when several countries are selected it compares the currently meaningful scalar (population by default, active population/area/religion layer when present), and it previews the active country's strongest currently filtered relation edges. Validation protects the one-card/one-toolbar layout and the quality workflow runs that validation on every PR.

**Tech Stack:** Browser ES modules, MapLibre state already owned by the atlas runtime, JSON country dossiers, Python repository validators, GitHub Actions.

**Spec:** `docs/superpowers/plans/2026-09-12-world-map-unification-implementation.md` and the current registry/compositor architecture on `project-consolidation-2026-09-12`.

## Global Constraints

- Preserve the upper-left country card as the single ordinary country information surface.
- Preserve the centered shallow world toolbar; do not restore nested Tools/Lens interfaces.
- Preserve lower-left map context as passive readout rather than a second control panel.
- Use canonical country dossiers and current selection/registry APIs; do not create a duplicate country database.
- Never compare non-normalized local-currency GDP values as if they shared a unit.
- Missing data remains unavailable rather than inferred.
- Country selection outline remains visually independent from analytical fill/pattern/query channels.

---

### Task 1: Protect the country-intelligence contract

**Files:**
- Modify: `scripts/validate_world_map_ui_shell.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: current `3d-country-card.js`, `3d-world-bar.js`, and `3d-compositor.js` source text.
- Produces: CI-enforced checks for the selected-country comparison, relation preview, area fallback, and existing collision-free shell.

- [ ] **Step 1: Write the failing validation assertions**

Require `3d-country-card.js` to contain `Selected comparison`, `Connections`, `comparisonRows`, `connectionRows`, `land_area_km2`, and a listener for `potato-atlas-relation-mode-change`.

- [ ] **Step 2: Wire the validator into the quality workflow**

Add:

```yaml
      - name: Validate World Map UI shell
        run: python scripts/validate_world_map_ui_shell.py
```

immediately after canonical World Map runtime validation.

- [ ] **Step 3: Run validation to verify it fails before implementation**

Run: `python scripts/validate_world_map_ui_shell.py`
Expected: FAIL because country-intelligence markers are not yet present.

- [ ] **Step 4: Commit the failing guardrail**

Commit message: `test(world-map): require country intelligence surface`

---

### Task 2: Add context-driven multi-country comparison

**Files:**
- Modify: `world-map/3d-country-card.js`

**Interfaces:**
- Consumes: `window.__potatoAtlasSelection.current.selectedCodes`, `window.__potatoAtlasLayers.active()`, canonical country dossier observations, and religion demography.
- Produces: `comparisonRows(codes)` returning compact rows for the currently meaningful scalar; defaults to population when no scalar is active.

- [ ] **Step 1: Add scalar-value resolution without duplicating data ownership**

Resolve `stat.population`, `stat.area`, and active `religion.*` layers. Area must accept both `geography.area_km2` and `geography.land_area_km2`.

- [ ] **Step 2: Render selected-country comparison only when two or more countries are selected**

Render at most six countries. Each row contains country name and formatted value for the current comparison metric. Extra selections are summarized as `+N more` rather than expanding the card indefinitely.

- [ ] **Step 3: Make comparison rows switch the active country**

Clicking a comparison row calls `selection.activate(code, { add: false })`; it must not remove the country from the working set.

- [ ] **Step 4: Keep the card compact**

Use the existing country-section/row visual grammar; do not add tabs, accordions, nested menus, or another floating panel.

---

### Task 3: Preview filtered country connections in the same card

**Files:**
- Modify: `world-map/3d-country-card.js`

**Interfaces:**
- Consumes: `selection.connectionsFor(code, 4)`, `selection.countryName(code)`, and `selection.getRelationMode()`.
- Produces: `connectionRows(code)` with partner name and typed relation summary reflecting the current Relations filter.

- [ ] **Step 1: Resolve the opposite endpoint of each ranked edge**

For each edge, partner is `edge.a === code ? edge.b : edge.a`.

- [ ] **Step 2: Render at most four strongest current connections**

Show partner name and a compact joined type label. When a relation filter is active, label the section with that mode through the existing selection API state.

- [ ] **Step 3: Keep Trace as the deeper action**

The preview remains bounded; the existing `Trace connections` button still promotes the specialist entity-trace module for deeper investigation.

- [ ] **Step 4: Re-render on relation-mode changes**

Listen for `potato-atlas-relation-mode-change` so Money/Systems/Institutions/Project/Other changes immediately alter the preview.

---

### Task 4: Verify the integrated map slice

**Files:**
- Verify: `scripts/validate_world_map_ui_shell.py`
- Verify: `scripts/validate_world_map_source.py`
- Verify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: final branch head.
- Produces: evidence that the new ordinary surface preserves the map architecture and repository build.

- [ ] **Step 1: Run the UI-shell validator**

Run: `python scripts/validate_world_map_ui_shell.py`
Expected: `World Map UI shell validation passed.`

- [ ] **Step 2: Run canonical World Map validation**

Run: `python scripts/validate_world_map_source.py`
Expected: exit 0.

- [ ] **Step 3: Verify JavaScript syntax for the changed modules**

Run: `node --check world-map/3d-country-card.js && node --check world-map/3d-country-selection.js && node --check world-map/3d-world-bar.js`
Expected: exit 0.

- [ ] **Step 4: Verify the exact final commit in GitHub Actions**

The `Repository quality checks` run for the exact final head must complete with conclusion `success` before claiming completion.
