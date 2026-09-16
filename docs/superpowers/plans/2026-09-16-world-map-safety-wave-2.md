# World Map Safety Wave 2

**Date:** 2026-09-16  
**Base:** merged World Map control-plane foundation on `main`  
**Goal:** remove duplicate interaction, tooltip, and inspector ownership now that the shared control-plane primitives exist.

## Anti-drift rule

Every new shared owner in this wave must migrate at least one real consumer and retire or demote the corresponding old owner. We do not add coordinators that merely sit beside legacy behavior.

## Order

### 1. Spatial-overlay interaction arbitration

Preserve the important semantic rule that multiple active spatial overlays may overlap and all matching claims must remain visible to inspection.

Implementation target:

- `3d-spatial-overlays.js` consumes `window.__potatoAtlasInteraction`;
- one dynamic registration owns all active rendered spatial-overlay layers;
- click priority remains below subdivision/place targets;
- the winning semantic target emits a single `feature-click` event whose `features` payload is still `featuresAt(event.point)` and therefore enumerates all active overlapping overlays;
- per-layer click listeners are removed from the normal routed path;
- degraded/direct boots may retain an explicit fallback only when the router is absent.

### 2. Places interaction migration

Move place point click ownership into the Interaction Router.

- place priority remains above subdivision/spatial/country targets;
- cursor and selection behavior stay unchanged;
- no parallel routed + direct click listener on normal boots;
- preserve direct-load fallback only if required by existing isolated tests.

### 3. Typed Inspector Router

Create one small semantic inspector coordinator before migrating Places/subdivisions.

Required model:

```js
{
  type,
  id,
  parent,
  owner,
  render,
  restore
}
```

The router owns a semantic stack/history, not `panel.innerHTML` snapshots.

Initial migrations:

- country context remains the parent baseline;
- subdivision may open over country;
- place may open over country or subdivision;
- closing/back returns to the correct semantic parent;
- URL parameters remain source-of-restoration truth for `country`, `subdivision`, and `place` during the migration.

Only after both consumers are migrated may their local `panelSnapshot` variables be removed.

### 4. Remaining transient tooltip owners

Migrate in low-risk order:

1. Axis
2. Fields
3. Networks
4. Infrastructure transient hover

Gateway/infrastructure click-detail popups are evaluated separately because persistent detail is not the same primitive as transient hover.

For each migration:

- shared `__potatoAtlasTooltip` owns the popup;
- owner token is unique;
- motion/projection invalidation comes from the service;
- direct `new maplibregl.Popup(...)` transient ownership is removed;
- the existing pointer-drag CSS guard remains until the last transient hover owner is migrated and regressions prove equivalence.

### 5. Control-plane validation

Extend the canonical World Map validation chain so it fails on:

- normal-path per-layer spatial click listeners after routed ownership exists;
- routed place interaction plus duplicate direct place click ownership;
- reintroduction of Places/subdivision raw HTML snapshots after inspector migration;
- new transient `maplibregl.Popup` owners in modules migrated to the Tooltip Service.

## Deliberately deferred

Do not mix these into this wave unless required by a regression:

- UI visual redesign;
- style lifecycle convergence;
- new empirical datasets;
- large Atlas→World Map internal renaming;
- Great Book files;
- advanced mathematical views.

## Verification cadence

For every slice:

1. add a failing regression or validator condition;
2. observe RED in GitHub Actions;
3. implement the minimum migration;
4. observe GREEN in the focused validator;
5. run the full repository workflow before merge.
