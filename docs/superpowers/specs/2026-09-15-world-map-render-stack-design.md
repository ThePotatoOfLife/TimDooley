# World Map — Shared Render Stack Design

Date: 2026-09-15
Status: Approved direction; implementation pending
Stacked base: `6fcf107dfc300d357b99d5c5f2c1d8e214f59c22` (PR #156 exact green head)

## Purpose

Replace load-order-dependent optional MapLibre layer placement with one explicit semantic render-stack contract.

Today, optional World Map modules independently choose insertion anchors such as `countries-fill`, `countries-line`, or `country-labels`. That works while the layer set is small, but it means final z-order can depend on which optional module happened to load first. As Physical, sacred/spatial, infrastructure, relationship, and future contextual layers grow, this becomes fragile.

This slice creates one shared ordering service while preserving existing ownership boundaries:

- modules still own their own sources, data, visibility, opacity, click behavior, and epistemic meaning;
- the render-stack coordinator owns only z-order registration and reconciliation;
- no provider, dataset, or semantic layer is merged;
- no new user-facing control is introduced.

## Scope

### In scope

- add a shared render-stack coordinator;
- define named semantic slots and stable bottom-to-top ordering;
- migrate current optional Physical layers to register their rendered layer IDs;
- migrate sacred/spatial overlays to register their rendered layer IDs;
- migrate infrastructure context points to register their rendered layer ID;
- reconcile ordering after optional modules add layers and after style restoration;
- add validation that rejects new ad-hoc placement in migrated modules;
- preserve all existing opacity, activation, URL, provider, and click semantics.

### Out of scope

- user drag-and-drop layer ordering;
- arbitrary user z-index controls;
- source/data migrations;
- new provider integrations;
- Physical Inspector behavior;
- changing sacred/current/historical epistemic classifications;
- changing country selection semantics;
- replacing MapLibre styles;
- synthetic invisible anchor layers;
- global refactoring of every historical/legacy renderer in one pass.

## Current problem

Current modules make their own placement decisions:

- Terrain hillshade targets `countries-fill`;
- Water independently targets `countries-fill` and `countries-line`;
- Hydrology independently targets `countries-fill` and `countries-line`;
- Land cover targets `countries-fill`;
- Deserts/xeric targets `countries-fill` / `countries-line`;
- spatial overlays target `country-labels`;
- infrastructure points are appended with no shared ordering contract.

This creates two failure classes:

1. **semantic drift** — a later module can accidentally appear above a more important contextual or boundary layer;
2. **load-order drift** — two modules targeting the same anchor can swap relative order depending on activation timing.

The fix must make z-order deterministic from meaning, not activation sequence.

## Architecture

### 1. Render-stack coordinator

Add:

`world-map/3d-render-stack.js`

Expose:

```js
window.__potatoAtlasRenderStack = {
  register(layerId, options),
  unregister(layerId),
  reconcile(reason?),
  state(),
  slotOrder(),
};
```

`register(layerId, options)` accepts:

```js
{
  slot: 'physical-surface',
  priority: 20,
  owner: 'physical.water.base'
}
```

Rules:

- `layerId` must be a non-empty MapLibre layer ID.
- `slot` must be one of the declared slots.
- `priority` is numeric; default `0`.
- `owner` is a stable diagnostic string naming the subsystem/module.
- re-registering an existing `layerId` replaces its metadata and triggers reconciliation.
- registering before the MapLibre layer exists is allowed; reconciliation skips it until the layer exists.
- unregister removes only render-stack metadata; it does not remove the MapLibre layer.

The coordinator owns no sources and never calls `removeLayer()` or `removeSource()`.

### 2. No mandatory add-layer wrapper

Modules continue using ordinary `map.addLayer(...)`.

After creating a rendered layer, the owning module calls:

```js
window.__potatoAtlasRenderStack?.register?.(LAYER_ID, {
  slot:'physical-surface',
  priority:20,
  owner:'physical.land-cover',
});
```

The coordinator then uses `map.moveLayer()` during `reconcile()`.

This migration pattern is intentional. It avoids making the render-stack service a new source/layer factory and preserves module ownership.

### 3. Canonical anchor layers

The existing core country/label layers remain structural anchors rather than becoming managed optional entries.

Expected anchors:

- `countries-fill`
- `countries-line`
- `country-hubs`
- `country-labels`

The coordinator must tolerate one or more anchors being temporarily absent during style restoration.

It must not create synthetic/invisible anchor layers.

## Slot model

### 4. Semantic order

Bottom → top:

1. `physical-surface`
2. core `countries-fill` anchor
3. `physical-line`
4. `geography-context`
5. `context-network`
6. core `countries-line` anchor
7. `selection-emphasis` reserved slot
8. core `country-hubs` / `country-labels` anchors

This preserves the intended visual logic:

- broad terrain/raster/ecological fills sit beneath the political country fill;
- physical linework remains visible above the country fill;
- sacred, historical, textual, and current contextual geography can be seen above the base country fill without overtaking country boundaries;
- bounded infrastructure/relationship context sits above geography context but below the canonical country boundary;
- labels remain topmost among the currently managed map-context layers.

`selection-emphasis` is reserved for future dedicated selection/highlight layers. Current selection remains feature-state-driven on core country layers and is not migrated in this slice.

### 5. Slot anchors

Reconciliation uses existing core anchors:

- `physical-surface` entries are placed immediately before `countries-fill`.
- `physical-line`, `geography-context`, and `context-network` entries are ordered as a combined managed region immediately before `countries-line`.
- `selection-emphasis` entries, if any, are placed immediately before the first available label anchor (`country-hubs`, then `country-labels`).

If a preferred anchor is missing:

- fall forward to the next higher known anchor where safe;
- otherwise leave current placement unchanged and retry on the next reconcile trigger;
- never throw in a way that breaks ordinary map operation.

### 6. Priority semantics

Within a slot:

- lower `priority` renders lower;
- higher `priority` renders higher;
- ties are resolved by stable lexical `layerId` ordering.

Priority is not a user preference. It is an internal deterministic contract.

Recommended initial priorities:

#### `physical-surface`

- Terrain hillshade: `10`
- Land cover raster: `20`
- Water lake fill: `30`
- Deserts/xeric fill: `40`
- Hydrology basin fill: `50`

#### `physical-line`

- Water coast/lake/river linework: `20–29`
- Deserts/xeric boundary: `40`
- Hydrology basin boundary: `50`
- Hydrology rivers: `60`

#### `geography-context`

- all spatial overlay polygon/fill/line layers: base priority `100 + overlay-local-order`

The render stack must not use epistemic type as a hidden ranking. A `historical_reconstruction`, `textual_reconstruction`, `current_observed`, and `project_interpretive` overlay remain semantically distinct but share the same visual slot unless the overlay module explicitly supplies a local priority.

#### `context-network`

- Infrastructure points: `20`
- future bounded relationship/network layers may use later priorities.

## Reconciliation algorithm

### 7. Deterministic ordering

`reconcile(reason)`:

1. read registered entries whose `layerId` currently exists;
2. group by slot;
3. sort each slot by `(priority, layerId)`;
4. compute the desired bottom-to-top managed order around canonical anchors;
5. call `map.moveLayer(layerId, beforeId)` only when necessary;
6. emit one diagnostic event after the pass.

The coordinator should avoid unnecessary `moveLayer()` churn when the current order already matches the desired order.

The contract should remain correct when modules activate in any sequence.

### 8. Reconcile triggers

Reconciliation occurs on:

- registration;
- unregistration;
- explicit `reconcile()` calls by modules after style restoration;
- `styledata`, debounced through `queueMicrotask` or equivalent one-shot scheduling;
- `potato-atlas-module-ready`, also one-shot scheduled.

Do not use:

- `MutationObserver`;
- `setInterval`;
- recurring timers;
- map polling loops.

One scheduled reconciliation may coalesce multiple same-turn registrations.

### 9. Style reload behavior

Optional modules already restore their own sources/layers after style reload.

After restoring its MapLibre layers, each migrated module must re-register or call the stack reconcile API. Re-registration is idempotent.

The render-stack coordinator must tolerate registered layer IDs disappearing temporarily during style reload and becoming available again later.

## Migration contracts

### 10. Physical modules

Migrate these modules:

- `3d-physical-terrain.js`
- `3d-physical-water.js`
- `3d-physical-hydrology.js`
- `3d-physical-land-cover.js`
- `3d-physical-deserts.js`

After migration, these modules may use a harmless fallback `beforeId` only for first insertion if the render-stack coordinator is unavailable during partial/legacy boot. The fallback must not remain the primary ordering mechanism.

The production path is:

1. create layer if missing;
2. register semantic slot/priority;
3. let render-stack reconciliation establish final order.

Existing Physical mixer opacity/status behavior from PR #156 must remain unchanged.

### 11. Spatial overlays

Migrate `world-map/3d-spatial-overlays.js`.

Every rendered overlay layer is registered in `geography-context`.

Important invariants:

- Father’s Land remains separate from Chosen Children’s Land;
- historical/textual/current/political/project overlay classifications remain unchanged;
- activation, reset, fit, click-claiming, and inspector behavior remain unchanged;
- render-stack priority never changes epistemic meaning.

The current direct `country-labels` placement helper should cease being the primary ordering contract after migration.

### 12. Infrastructure

Migrate `world-map/3d-infrastructure.js`.

`atlas-infrastructure-points` registers in `context-network`.

All existing bounded-context, popup, source, and Impact behavior remains unchanged.

## Diagnostics and events

### 13. Public state

`state()` returns a stable diagnostic snapshot:

```js
{
  entries:[
    { layerId, slot, priority, owner, exists }
  ],
  lastReason:'register',
  reconcileCount:12
}
```

`slotOrder()` returns the declared slot ordering as an immutable/copy array.

### 14. Event

Emit:

`potato-atlas-render-stack-change`

with detail:

```js
{
  reason,
  moved,
  registered,
  missing,
}
```

This is diagnostic/integration state only. It does not imply data activation.

## Failure behavior

- Missing anchors are nonfatal.
- Missing registered layers are nonfatal.
- `moveLayer()` failure for one layer is logged and does not stop reconciliation of remaining layers.
- Invalid slot registration returns `false` and logs a concise warning.
- A failed reconciliation never disables a provider or removes data.
- The coordinator never changes layer visibility, paint, filters, source data, or click handlers.

## Loading

Load the render-stack coordinator through the existing always-on panel/module lifecycle before Physical World where practical:

1. UI Layout
2. Render Stack
3. Map State
4. Physical World

The service is tiny and contains no provider/data fetch.

Because this work is stacked on PR #156, `Map State` remains part of the lifecycle sequence.

## Testing and validation

Add:

`scripts/validate_world_map_render_stack.py`

Chain it through the existing World Map UI-layout architecture validator so one quality step covers the structural contract.

### Required validation

#### Coordinator

- `world-map/3d-render-stack.js` exists and passes `node --check`;
- exposes `__potatoAtlasRenderStack`;
- exposes `register`, `unregister`, `reconcile`, `state`, and `slotOrder`;
- declares all five managed slots;
- uses `map.moveLayer`;
- uses deterministic priority and layer-ID sorting;
- contains no `MutationObserver` or `setInterval`;
- does not call `removeLayer`, `removeSource`, change visibility, or change paint properties.

#### Lifecycle

- `3d-panel-lifecycle.js` loads `Render Stack` / `./3d-render-stack.js` before `Physical World`;
- Map State from PR #156 remains loaded.

#### Physical migration

Each migrated Physical module:

- references `__potatoAtlasRenderStack`;
- registers every visual layer it creates;
- assigns the expected semantic slot;
- preserves existing enable/disable/opacity/status controller APIs;
- still passes its existing dedicated validator.

Validators should stop requiring `countries-fill` merely as proof of ordering once the module has migrated; instead they should require the render-stack registration contract.

#### Spatial overlays

- registers rendered layers in `geography-context`;
- preserves overlay click handling and reset API;
- no longer relies on `country-labels` as the primary semantic ordering mechanism.

#### Infrastructure

- registers `atlas-infrastructure-points` in `context-network`;
- preserves existing context/Impact behavior.

#### Load-order independence

The validator must encode at least one static contract proving that ordering metadata is independent from module activation order: priorities and slot names are declared in module registrations rather than inferred from insertion timing.

### Regression gates

Run the existing repository quality workflow. At minimum, the following must stay green:

- World Map source/runtime validation;
- World Map UI shell;
- World Map UI layout;
- Map State / Physical mixer validation;
- Terrain;
- Water;
- Hydrology;
- Land cover;
- Deserts/xeric;
- spatial overlays;
- infrastructure and infrastructure integration.

## Rollout strategy

Implement on a stacked feature branch based on PR #156 head.

TDD sequence:

1. add the failing render-stack validator and chain it into UI-layout validation;
2. prove RED on the stacked PR head;
3. add the coordinator + lifecycle loader;
4. migrate Physical modules;
5. migrate spatial overlays;
6. migrate infrastructure;
7. run focused validators;
8. run full repository quality on the exact head.

Do not merge this work independently into `main` before PR #156 unless the branch is explicitly rebased/retargeted and verified against the resulting base.

## Follow-on

After the render-stack contract is green and deployed, the next planned map slice is the **Physical Inspector**:

- HydroBASINS / HydroRIVERS feature inspection;
- desert/ecoregion inspection where source attributes support it;
- canonical right-inspector integration;
- sacred/spatial overlay click priority preserved through the existing click-claim mechanism.
