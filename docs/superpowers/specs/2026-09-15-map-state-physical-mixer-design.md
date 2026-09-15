# World Map — Map State + Physical Mixer Design

Date: 2026-09-15
Status: Approved direction; implementation pending
Base: `bd33c08e0b134ff018dcd50541a86376b312136f`

## Purpose

Promote the World Map from a collection of independently toggleable layers into a coherent map-state surface without making the UI heavier or coupling unrelated subsystems together.

This slice has two goals:

1. make the top-bar reset mean “clear the current map state” rather than only “clear analytical layers”; and
2. turn the Physical menu into a lightweight layer mixer with useful state, opacity, and recovery behavior.

This is intentionally narrower than the later render-stack contract and Physical Inspector work. It should establish clean state ownership for those later slices.

## Design principles

- Domain modules continue to own their own data, rendering, and provider behavior.
- A neutral coordinator may invoke public subsystem APIs, but it must not reach into subsystem internals.
- Reset clears semantic/user state, not camera context.
- Camera center, zoom, bearing, pitch, and flat/globe projection survive reset.
- Physical provider failure is nonfatal and never blocks ordinary map boot or other Physical layers.
- Expensive providers stay lazy/on-demand.
- Opacity changes do not reload providers or recreate already-loaded sources.
- Physical opacity is presentation state, not provider identity and not canonical data.
- URL state stays compact: active Physical layer IDs may remain in `physical=`, but per-layer opacity is not serialized into the URL.
- Sacred/textual/current Geography overlays remain epistemically independent from Physical layers.

## Current gap

The current top-bar reset calls only the analytical/compositor reset. Physical layers, Geography overlays, pins/active country, relation filtering, and non-current Time state remain behind even though the UI presents the control as a general reset.

The current Physical menu exposes on/off only. It does not expose loading state, provider failure, zoom-needed state, or opacity. Individual modules also use fixed opacity values internally.

The current Physical runtime marks a layer active after `enable()` resolves, regardless of whether a module explicitly returns `false`. This design requires a failed `enable()` to remain inactive and surface an error state.

## Architecture

### 1. Map State coordinator

Add `world-map/3d-map-state.js` and expose:

```js
window.__potatoAtlasMapState = {
  reset(options?),
  snapshot(),
};
```

`reset()` is orchestration only. It calls public subsystem APIs and does not directly manipulate MapLibre layers, GeoJSON sources, feature state, or provider URLs.

The coordinator should be loaded through the existing panel/module lifecycle before the World Bar reset button is bound, or the World Bar should tolerate its API becoming available after startup.

### 2. Reset contract

Default `reset()` clears:

- analytical/compositor layers via `window.__potatoAtlasCompositor?.reset?.()`;
- Physical layers via `window.__potatoAtlasPhysicalLayers?.reset?.()`;
- Geography/spatial overlays via `window.__potatoAtlasSpatialOverlays?.reset?.()`;
- active country and retained pins via `window.__potatoAtlasSelection?.clearAll?.({ keepView:true })`;
- relation filter back to `all` via the selection API if needed;
- non-current Time state via `window.__potatoAtlasTime?.setState?.({ mode:'current', time:'', time2:'' })` when Time is loaded.

Reset preserves:

- camera center;
- zoom;
- bearing;
- pitch;
- current projection (`flat` or `globe`);
- loaded-but-disabled provider sources that modules intentionally retain for reuse;
- ordinary basemap/country rendering.

The coordinator must snapshot camera/projection before reset and assert that it did not intentionally change them. It should not force a map jump merely to restore unchanged values.

If Time has never been loaded, reset must still remove stale Time URL parameters using the Time contract’s known parameter names without loading the whole Time module solely for reset. If Time is loaded, its public `setState()` API remains authoritative.

### 3. Reset ordering

Use deterministic orchestration:

1. analytical/compositor reset;
2. Physical reset;
3. spatial/Geography reset;
4. selection and pins reset;
5. relation mode normalization;
6. Time normalization;
7. one `potato-atlas-map-state-reset` event;
8. one World Bar/UI refresh request.

Subsystem failures are collected and reported but do not stop later reset steps. One broken optional subsystem must not prevent the others from clearing.

The reset result should be structured:

```js
{
  ok: true|false,
  cleared: ['analytical', 'physical', ...],
  failed: [{ subsystem, message }],
  preserved: { camera:true, projection:true }
}
```

### 4. Physical runtime state model

Extend `window.__potatoAtlasPhysicalLayers` with:

```js
reset(),
status(id),
setOpacity(id, value),
getOpacity(id),
```

The runtime owns generic lifecycle state per manifest entry:

- `idle` — current but inactive;
- `loading` — module/provider activation in progress;
- `active` — enabled successfully;
- `zoom-needed` — active, but meaningful provider rendering requires a closer zoom;
- `error` — activation/provider operation failed;
- `partial` — active with degraded optional provider data where a module explicitly reports it.

The runtime remains the owner of whether an entry is considered active. A module returning `false` from `enable()` must not be added to the active set.

`status(id)` should return a stable object such as:

```js
{
  id,
  phase,
  message,
  active,
  opacity,
  updatedAt,
}
```

### 5. Module-to-runtime status reporting

Physical modules may report richer state through one event:

`potato-atlas-physical-layer-status`

with detail:

```js
{
  id: 'physical.water.hydrology',
  phase: 'zoom-needed'|'loading'|'active'|'partial'|'error',
  message: 'Zoom in to regional scale'
}
```

The Physical runtime consumes this event only for known manifest IDs.

Initial module requirements:

- Hydrology reports `zoom-needed` below zoom 4, `loading` during viewport requests, `active` on a complete regional result, `partial` when one provider fails, and `error` if no usable regional provider result is available.
- Land cover reports activation failure as `error` and successful activation as `active`.
- Water may report `loading` only while its first requested detail tier is being loaded; ordinary overview activation is `active`.
- Deserts/xeric reports provider activation failure as `error` and successful activation as `active`.
- Terrain may remain generic `loading` → `active`/`error` for this slice.

### 6. Physical reset

`window.__potatoAtlasPhysicalLayers.reset()`:

- disables all active Physical entries through their public controllers;
- clears the active set;
- clears `physical=` from the URL;
- restores each entry’s presentation opacity to its manifest default in runtime state;
- does not destroy reusable sources unless the owning module already does so by design;
- emits one aggregate Physical change after the reset rather than a noisy cascade where practical.

A provider failure during disable should be logged and collected but must not leave the runtime’s active set permanently stuck.

## Physical mixer UI

### 7. Physical menu structure

Keep `Physical` as the existing first-class top-level World Bar menu. Do not add a second floating panel.

The popup becomes:

- header: `Physical world` + concise state summary;
- one row per current Physical layer;
- optional compact opacity control beneath eligible active rows;
- footer action: `Clear physical` when one or more Physical layers are active.

Each layer row shows its current state in text, not color alone.

Examples:

- `Hydrology` — `zoom in`
- `Hydrology` — `loading`
- `Hydrology` — `active`
- `Hydrology` — `partial`
- `Land cover` — `provider unavailable`

Disabled/planned entries remain disabled as today.

### 8. Opacity eligibility

Opacity controls are available for:

- `physical.water.base`;
- `physical.water.hydrology`;
- `physical.land-cover`;
- `physical.aridity`.

Terrain does not receive an opacity slider in this slice because terrain elevation is not a single-opacity visual layer and should not be forced into a misleading control model.

### 9. Opacity semantics

The Physical runtime stores a normalized value in `[0, 1]` for each eligible entry.

The manifest’s `default_opacity` remains the initial/default value.

Each eligible controller implements:

```js
setOpacity(value)
getOpacity()
```

Controller behavior:

- Land cover sets raster opacity directly.
- Water applies the requested value as a master multiplier over its internally differentiated lake/river/coastline baseline opacities.
- Hydrology applies the requested value as a master multiplier over basin fill, basin line, and river-line baseline opacities.
- Deserts/xeric applies the requested value as a master multiplier over its fill/line baseline opacities.

This preserves visual hierarchy within a layer while giving the user one understandable slider per Physical product.

Changing opacity must not:

- refetch provider data;
- recreate MapLibre sources;
- reactivate a disabled layer;
- change active Physical URL state.

Opacity is session presentation state. It is intentionally omitted from the URL in this slice.

### 10. Mixer interaction details

- Clicking a layer row toggles activation as today.
- Dragging/clicking the opacity control must not bubble into the row toggle.
- Opacity controls appear only for active eligible layers.
- The slider should expose an accessible percentage label/value.
- `Clear physical` calls the Physical runtime’s `reset()`.
- The menu summary remains visually active whenever at least one Physical layer is active.
- A loading or error state must not cause menus to close unexpectedly.
- Mobile keeps the existing full-width popup behavior; controls must fit without horizontal scrolling.

## URL and state behavior

### 11. Physical URL state

Continue using:

`physical=id1,id2,...`

Only successfully active layers are persisted.

Activation sequence:

1. set phase `loading`;
2. lazy-load module if needed;
3. call controller `enable()`;
4. if `enable()` returns `false` or throws: phase `error`, do not add to active set, do not write it to `physical=`;
5. otherwise add to active set, persist compact IDs, phase `active` unless the module has reported a more specific valid phase such as `zoom-needed`.

Restore sequence follows the same success rule. A stale/broken Physical ID in a shared URL must fail nonfatally and be removed when state is normalized.

### 12. Reset URL cleanup

A successful full map-state reset removes or normalizes semantic-state parameters owned by the cleared subsystems, including as applicable:

- `physical`;
- spatial overlay active-state parameter;
- `pins`;
- `country`;
- `relation`;
- legacy `selected`/`compare` state where selection cleanup already owns it;
- non-current Time parameters;
- analytical/query state owned by the compositor/layer registry.

Reset explicitly preserves projection parameters and any camera/view representation already used by the map.

## Events

Add:

- `potato-atlas-map-state-reset` — one event after coordinator reset completes;
- `potato-atlas-physical-layer-status` — module → Physical runtime status updates;
- existing `potato-atlas-physical-change` continues to represent active-layer state changes.

Avoid new `MutationObserver` or polling loops. Use existing map/UI events and direct API calls.

## Failure handling

- Optional provider failures stay nonfatal.
- Physical runtime must distinguish an activation error from an inactive layer.
- If opacity application fails, retain the previous valid opacity in runtime state and surface `error` without disabling unrelated layers.
- If one subsystem reset fails, continue resetting all others and return `ok:false` with the failure list.
- Reset never reloads the page as an error-recovery mechanism.
- Reset never destroys the map instance.

## Files expected in implementation

Likely create:

- `world-map/3d-map-state.js`
- `scripts/validate_world_map_map_state.py`

Likely modify:

- `world-map/3d-panel-lifecycle.js`
- `world-map/3d-world-bar.js`
- `world-map/3d-physical-layers.js`
- `world-map/3d-physical-water.js`
- `world-map/3d-physical-hydrology.js`
- `world-map/3d-physical-land-cover.js`
- `world-map/3d-physical-deserts.js`
- `data/world-map-physical-layers.json` only if metadata needs a small control-capability field
- `scripts/validate_world_map_ui_layout.py`
- `.github/workflows/quality-checks.yml` only if the new validator is not chained through an existing World Map validation step

Terrain should not need behavioral changes unless implementation reveals a generic status-reporting compatibility issue.

## Validation contract

The implementation must add automated checks for at least the following.

### Map reset

- The World Bar reset delegates to `__potatoAtlasMapState.reset()` rather than only the compositor.
- Reset invokes analytical, Physical, Geography/spatial, selection, relation, and Time cleanup through public APIs.
- Reset uses `clearAll({keepView:true})` for selection.
- Reset does not call `jumpTo`, `flyTo`, `fitBounds`, `easeTo`, or change projection as part of ordinary reset.
- One failing optional subsystem does not prevent later reset steps.
- `potato-atlas-map-state-reset` is emitted.

### Physical runtime

- Exposes `reset`, `status`, `setOpacity`, and `getOpacity`.
- `enable() === false` does not produce an active layer.
- Failed activation is not persisted in `physical=`.
- reset clears active Physical URL state.
- opacity defaults come from the manifest.

### Physical modules

- Water, Hydrology, Land cover, and Deserts/xeric expose `setOpacity` and `getOpacity`.
- Opacity setters clamp to `[0,1]`.
- Opacity changes modify paint properties only; validators should reject opacity implementations that refetch provider URLs.
- Hydrology exposes/report states for zoom-needed/loading/partial/error.

### UI

- Physical rows expose meaningful state text.
- Eligible active Physical rows expose an accessible opacity control.
- Terrain has no opacity control.
- `Clear physical` exists and calls the Physical runtime reset.
- No new floating control panel is introduced.
- Existing mobile menu behavior remains intact.

### Existing regression gates

The full repository quality suite must remain green, including:

- World Map UI layout validation;
- Terrain validation;
- Water validation;
- Land-cover validation;
- Deserts/xeric validation;
- Hydrology validation;
- ordinary World Map runtime/UI/spatial-overlay checks.

## Non-goals for this slice

Do not include:

- the shared render-stack/ordered-slot system;
- clickable Physical Inspector cards;
- provider replacement or data-source migration;
- live weather;
- tactical conflict tracking;
- user-reorderable arbitrary layer z-order;
- per-provider advanced settings;
- opacity serialization into shared URLs;
- a new settings drawer or floating layer-control window.

## Follow-on sequence

After this slice is merged and deployed:

1. implement a shared render-stack contract so modules stop independently guessing insertion positions;
2. implement Physical Inspector interaction for HydroBASINS/HydroRIVERS and ecological desert features, using the canonical right inspector and preserving sacred-overlay click priority.

This ordering keeps state semantics stable before changing render ownership or click behavior.
