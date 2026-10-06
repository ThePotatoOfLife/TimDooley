# Physical World + UI Coordinator — World Map Design

Date: 2026-09-15
Status: approved direction, design specification for review
Scope: physical/environment layers, efficient loading, and collision-free map UI placement

## 1. Goal

Extend the canonical World Map with a coherent physical-world layer family (terrain, water, land cover, vegetation/aridity context) while replacing ad-hoc floating panel coordinates with a small layout coordinator that reserves stable screen zones.

The design must improve information density without making startup heavier or allowing panels to overlap unpredictably.

## 2. Existing foundations to preserve

The existing `world-map/3d-physical-terrain.js` already uses the correct performance pattern: the terrain control loads with the core, but DEM/hillshade tile sources remain dormant until Terrain is enabled.

The map already has separate systems for:

- country/base geometry;
- analytical layers;
- independent spatial overlays;
- optional physical terrain;
- a right-side inspector panel;
- top toolbar/menu surfaces;
- time/status HUD elements;
- Axis navigation.

The new work should coordinate these systems rather than replace them.

## 3. Physical-world architecture

Create one conceptual family called `Physical World` / `Environment` with independently toggleable children.

### 3.1 Terrain

Keep `3d-physical-terrain.js` as the terrain/elevation owner.

Responsibilities:

- raster DEM;
- hillshade;
- optional MapLibre terrain extrusion;
- no DEM network load before explicit enablement;
- failure remains nonfatal and falls back to the ordinary map.

### 3.2 Water

Water has two distinct jobs and must not be collapsed into one layer:

1. `physical.water.base`
   - ocean/coastline/major lake/major river cartographic context;
   - lightweight global physical vectors or tiles;
   - visual context rather than legal or hydrological authority.

2. `physical.water.hydrology`
   - measured river/catchment/lake data when the user is investigating physical drainage systems;
   - suitable sources include HydroSHEDS/HydroBASINS/HydroRIVERS/HydroLAKES;
   - physical hydrology remains independent from sacred Four-Rivers interpretations.

A river may therefore appear in both a physical hydrology layer and a textual/sacred overlay without those meanings being merged.

### 3.3 Land cover

Add a land-cover surface suitable for global web use.

Canonical classes should preserve the source taxonomy rather than inventing informal labels. Expected user-facing grouping includes:

- trees / forest;
- shrubland;
- grassland;
- cropland;
- built-up;
- bare / sparse vegetation;
- permanent water;
- herbaceous wetland;
- moss / lichen where supported;
- snow / ice.

Do not equate `bare / sparse vegetation` with `desert`.

Dense global land-cover data must be consumed as raster/vector tiles or another tiled web service. The repository must not ship a planet-scale 10 m GeoJSON/raster dump.

### 3.4 Desert / aridity

If a `Deserts / arid regions` layer is added, it must use an explicit climatic/ecoregional/aridity source and remain independent from satellite land-cover classes.

The map may display both simultaneously:

- land cover answers “what covers this surface?”;
- aridity/desert answers “what climatic/ecological regime is this?”

### 3.5 Physical layer data contract

Physical layers should register through a small manifest rather than each UI control hard-coding remote sources.

Recommended owner:

`data/world-map-physical-layers.json`

Each entry should carry at minimum:

```json
{
  "id": "physical.land-cover",
  "label": "Land cover",
  "kind": "raster_tiles",
  "availability": "current",
  "load_policy": "on_demand",
  "source": {
    "provider": "...",
    "dataset": "...",
    "version": "...",
    "url": "...",
    "attribution": "..."
  },
  "mutual_exclusion_group": null,
  "default_opacity": 0.65,
  "min_zoom": 0,
  "max_zoom": 14,
  "status_note": "..."
}
```

The manifest stores metadata and loading policy. It must not become a duplicate MapLibre style specification if the runtime can derive the style from a small type-specific adapter.

## 4. Efficiency rules

The World Map must follow these rules consistently:

1. Small semantic datasets may use repository-owned GeoJSON.
2. Dense global physical data uses tiles, not giant GeoJSON.
3. Optional expensive layers load on first activation, never at startup.
4. Once loaded, sources/layers should normally be hidden/shown rather than repeatedly destroyed and downloaded.
5. Layer modules must reuse one source when several visual layers can share it.
6. Zoom-dependent detail must be delegated to tiled sources or MapLibre min/max zooms rather than loading full-resolution geometry globally.
7. Remote physical sources must carry attribution and version/provenance metadata.
8. A failed optional provider must never prevent the core map from booting.
9. Physical rendering must preserve country selection, spatial overlays, labels, and inspector interaction.
10. URL state should store enabled physical layer IDs compactly, without serializing provider internals.

## 5. Rendering order

Establish a stable rendering stack so new physical data cannot accidentally hide semantic overlays.

Recommended bottom-to-top order:

1. base ocean / background;
2. basemap or land-cover raster;
3. hillshade / terrain shading;
4. country fills;
5. physical rivers/lakes/coastlines where appropriate;
6. analytical country fills/fields;
7. sacred/historical/textual/current spatial overlays;
8. infrastructure/networks/routes;
9. country and place boundaries;
10. labels/points;
11. transient hover/selection rendering.

Terrain elevation is a map transform rather than a simple z-layer and should continue to be controlled independently.

## 6. UI layout coordinator

Create one lightweight layout owner for application-controlled floating surfaces.

Recommended runtime:

`world-map/3d-ui-layout.js`

It does not render domain content. It assigns registered surfaces to reserved zones and publishes layout state.

### 6.1 Desktop zones

#### Top command zone

Contains:

- World Bar;
- search;
- dropdown menus.

Menus may temporarily overlay map content but should not compete with persistent panels.

#### Right inspector zone

Contains exactly one primary persistent inspector surface at a time.

Examples:

- country inspector;
- spatial-overlay inspector;
- infrastructure/entity details;
- Axis detail view.

Domain modules replace inspector content rather than creating another right-side card.

#### Left status zone

Contains compact passive surfaces stacked by the coordinator:

- current map context;
- time state;
- legend/status summaries.

No module in this zone should independently declare `left:10px; bottom:10px`.

#### Canvas-control zone

Reserved for truly map-native/transient controls:

- MapLibre navigation controls;
- scale/attribution;
- hover popups;
- small transient toggle buttons where unavoidable.

Application panels must not claim arbitrary corners in this zone.

### 6.2 Axis navigator

The D1–D11 Axis navigator currently occupies the same right-side area as the inspector.

It should become one of these two states:

- compact map control when closed;
- content hosted by the right inspector zone when expanded.

The expanded Axis navigator must not remain an independently positioned 170×476 px floating panel behind or on top of the inspector.

### 6.3 Mobile zones

Below the mobile breakpoint, collapse the application layout to:

1. top command bar;
2. one open menu/popover surface;
3. one bottom-sheet inspector;
4. map-native controls.

Passive status items should collapse into a compact status strip or into inspector/menu content when vertical space is constrained.

A menu and bottom inspector may coexist only if enough viewport remains for useful map interaction; otherwise opening the menu temporarily suppresses/collapses passive status content.

## 7. Coordinator API

The coordinator should stay deliberately small.

Proposed public API:

```js
window.__potatoAtlasUILayout = {
  register({ id, zone, element, priority = 0, mode = 'persistent' }),
  unregister(id),
  setVisible(id, visible),
  getState(),
  refresh(),
};
```

Supported zones initially:

- `top`
- `right-inspector`
- `left-status`
- `canvas-control`

`register()` owns placement but not the surface's content lifecycle.

For `left-status`, the coordinator should render registered elements in one stack container ordered by priority.

For `right-inspector`, only one primary inspector container exists; existing domain code continues writing into `#panel` rather than registering multiple competing cards.

## 8. Physical World UI

Add `Physical` as a first-class top-level World Bar menu, parallel to Geography rather than hiding environment controls inside a legacy menu.

Suggested compact contents:

- Terrain
- Water
- Land cover
- Hydrology
- Deserts / aridity (only when sourced and available)

Each item shows active state and can be toggled off by clicking again.

Advanced provider/version details belong in the inspector or an information affordance, not in the toolbar label.

The Physical menu must preserve stackability where semantically valid. Terrain + land cover + rivers, for example, may coexist.

## 9. Interaction rules

- Turning on a physical layer must not clear Geography overlays.
- Turning on Geography must not clear physical layers.
- Reset behavior should distinguish `clear analytical view` from a future `reset everything` action; current reset semantics must be audited before Physical hooks into it.
- Map clicks prioritize explicit semantic overlays/points over passive raster surfaces.
- Raster land-cover layers are inspectable only if the provider/API supports meaningful pixel/class lookup; otherwise they remain visual context.
- Physical source failures surface a small nonblocking status, not a red boot failure.

## 10. Visual density and accessibility

- Avoid using high-opacity land-cover colors beneath already-dense analytical fills.
- Physical raster opacity should have sensible defaults and may later expose an opacity control if evidence shows it is needed.
- Active menu items require both color/state styling and text/check state; color alone is insufficient.
- Inspector/status surfaces need predictable keyboard focus order.
- All menu buttons must be actual buttons with `aria-pressed` where appropriate.
- Layout changes must not move focused controls unexpectedly while a keyboard interaction is in progress.

## 11. Testing / acceptance criteria

The change is complete only when automated tests demonstrate:

1. no optional physical source is fetched during ordinary startup;
2. Terrain remains on-demand and nonfatal on source failure;
3. Physical menu toggles can activate and deactivate current layers;
4. Geography and Physical layers can be active simultaneously;
5. rendering order keeps country labels and sacred/textual overlay outlines legible;
6. the inspector and Axis expanded UI never occupy independent overlapping right-side rectangles;
7. current map context and time/status surfaces no longer independently claim the same bottom-left coordinates;
8. desktop and mobile layout rules are represented in regression checks;
9. URL state round-trips physical-layer activation;
10. full repository quality checks and Pages build succeed.

## 12. Delivery sequence

Implement as two independently reviewable slices on one architectural programme:

### Slice A — UI layout coordinator

First remove known panel collisions and provide the stable zone API. Migrate existing inspector/status/Axis placement before adding another family of controls.

### Slice B — Physical World

Then add the Physical menu/manifest and migrate Terrain into that menu before adding Water/Land cover/Hydrology sources.

This order ensures environment expansion consumes a clean UI architecture rather than increasing existing layout debt.

## 13. Non-goals for this programme

- no live weather system;
- no tactical military tracking;
- no huge raw satellite dataset committed to GitHub;
- no attempt to make all environmental layers inspectable at pixel precision immediately;
- no replacement of the existing sacred-spatial overlay epistemic model;
- no wholesale rewrite of the World Map.

## 14. Design decision

Proceed with a shared `Physical World + UI Coordinator` programme, but implement UI coordination first and environment sources second. Preserve lazy loading and independent layer semantics throughout.