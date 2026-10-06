# Physical World + UI Coordinator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the World Map’s known floating-panel collisions, establish one small layout coordinator, and add a first-class lazy-loaded Physical menu without making ordinary startup heavier.

**Architecture:** `world-map/3d-ui-layout.js` owns placement only: top command, one right inspector, a stacked left-status container, and map-native controls. `data/world-map-physical-layers.json` is metadata/loading policy; `world-map/3d-physical-layers.js` adapts manifest entries to existing modules such as Terrain. Dense global environmental data stays tiled/on-demand and is not committed as giant GeoJSON.

**Tech Stack:** Vanilla JavaScript, MapLibre GL JS, JSON manifests, Python repository validators, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-15-physical-world-ui-coordinator-design.md`

## Global Constraints

- UI coordination is implemented before environment expansion.
- Optional physical sources must not fetch during ordinary startup.
- Existing `#panel` remains the single primary inspector surface.
- Sacred/textual/current spatial overlays remain independent from physical layers.
- Dense global physical data uses tiles/on-demand services, not giant committed GeoJSON.
- Optional provider failure is nonfatal.
- Mobile resolves to top controls + one popover + one bottom-sheet inspector + map-native controls.
- No live weather and no tactical military tracking.

---

### Task 1: Regression gates for layout ownership and Physical runtime

**Files:**
- Create: `scripts/validate_world_map_ui_layout.py`
- Modify: `.github/workflows/quality-checks.yml`
- Modify: `scripts/validate_world_map_terrain.py`

**Interfaces:**
- Consumes: existing `#panel`, `#atlasWorldContext`, `#atlasTimeState`, `#axisDepthNavigator`, Terrain API.
- Produces: a CI gate requiring `window.__potatoAtlasUILayout`, stable zone names, Physical manifest/runtime, on-demand loading markers, and removal of independent bottom-left/right-panel positioning from migrated modules.

- [ ] **Step 1: Write the failing validator**

```python
LAYOUT = ROOT / "world-map" / "3d-ui-layout.js"
PHYSICAL = ROOT / "world-map" / "3d-physical-layers.js"
MANIFEST = ROOT / "data" / "world-map-physical-layers.json"

for path in (LAYOUT, PHYSICAL, MANIFEST):
    if not path.exists():
        errors.append(f"missing required World Map architecture file: {path.relative_to(ROOT)}")

if LAYOUT.exists():
    text = LAYOUT.read_text(encoding="utf-8")
    for token in ("__potatoAtlasUILayout", "right-inspector", "left-status", "canvas-control", "register", "setVisible", "getState", "refresh"):
        if token not in text:
            errors.append(f"UI layout coordinator missing {token}")

if PHYSICAL.exists():
    text = PHYSICAL.read_text(encoding="utf-8")
    for token in ("world-map-physical-layers.json", "load_policy", "on_demand", "potato-atlas-physical-change", "physicalLayers"):
        if token not in text:
            errors.append(f"Physical runtime missing {token}")
```

Also assert that `3d-axis-depth.js` no longer owns an independent `right:12px;top:62px;width:170px;height:476px` expanded panel and that migrated left-status surfaces register with the coordinator instead of each claiming `left/bottom` coordinates.

- [ ] **Step 2: Run CI/validator and verify RED**

Run: `python scripts/validate_world_map_ui_layout.py`

Expected: FAIL because the coordinator, physical runtime, and manifest do not exist yet.

- [ ] **Step 3: Register the validator in quality checks**

Add `python scripts/validate_world_map_ui_layout.py` adjacent to the other World Map validators.

- [ ] **Step 4: Keep Terrain’s existing lazy-load assertions**

Extend `validate_world_map_terrain.py` so it requires Terrain to be registered through the Physical runtime/menu while retaining `raster-dem`, `hillshade`, `setTerrain`, and nonfatal behavior.

- [ ] **Step 5: Commit the red gate**

```bash
git add scripts/validate_world_map_ui_layout.py scripts/validate_world_map_terrain.py .github/workflows/quality-checks.yml
git commit -m "test(world-map): gate coordinated UI and physical layers"
```

### Task 2: UI layout coordinator and collision migration

**Files:**
- Create: `world-map/3d-ui-layout.js`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `world-map/3d-ui.js`
- Modify: `world-map/3d-world-bar.js`
- Modify: `world-map/3d-axis-depth.js`
- Modify: `world-map/index.html`

**Interfaces:**
- Produces `window.__potatoAtlasUILayout = { register, unregister, setVisible, getState, refresh }`.
- `register({id, zone, element, priority, mode})` accepts zones `top`, `right-inspector`, `left-status`, `canvas-control`.
- Existing domain modules continue writing inspector content to `#panel`.

- [ ] **Step 1: Add failing layout expectations to Task 1 validator**

Require:

```text
#atlasUILeftStatus
#panel registered as right-inspector
#atlasWorldContext registered as left-status
#atlasTimeState registered as left-status
axisDepthNavigator hosted inside #panel when expanded
mobile bottom-sheet rule
```

Run validator; expected FAIL.

- [ ] **Step 2: Implement the minimal coordinator**

`3d-ui-layout.js` creates one `#atlasUILeftStatus` container inside `.mapwrap`, stores registrations in a `Map`, moves left-status elements into that container ordered by priority, records the single `#panel` right-inspector registration, and emits `potato-atlas-ui-layout-change` after `refresh()`.

The public API is exactly:

```js
window.__potatoAtlasUILayout = {
  register({id, zone, element, priority = 0, mode = 'persistent'}),
  unregister(id),
  setVisible(id, visible),
  getState(),
  refresh,
};
```

- [ ] **Step 3: Load coordinator before progressive/domain placement**

Register `3d-ui-layout.js` from `3d-panel-lifecycle.js` before Terrain/Axis/UI modules that depend on placement.

- [ ] **Step 4: Migrate left status surfaces**

`3d-world-bar.js` registers `#atlasWorldContext` with `left-status`, priority 30.
`3d-ui.js` registers `#atlasTimeState` with `left-status`, priority 20 when present.
Remove independent bottom-left positioning from those migrated surfaces; the stack container owns the corner.

- [ ] **Step 5: Migrate Axis expanded UI**

Keep `#axisCompactToggle` as a small canvas control. When expanded, move `#axisDepthNavigator` into `#panel`, open the inspector through existing panel lifecycle, and remove the navigator’s independent fixed rectangle styling. Closing Axis returns to compact state without leaving a hidden right-side floating rectangle.

- [ ] **Step 6: Add desktop/mobile layout CSS**

Desktop: top bar; `#panel` right; `#atlasUILeftStatus` bottom-left vertical stack.
Mobile: `#panel` bottom sheet; menu popovers top-fixed; `#atlasUILeftStatus` compact and suppressed while a menu is open if necessary.

- [ ] **Step 7: Verify GREEN**

Run:

```bash
python scripts/validate_world_map_ui_layout.py
python scripts/validate_world_map_3d.py
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add world-map/3d-ui-layout.js world-map/3d-panel-lifecycle.js world-map/3d-ui.js world-map/3d-world-bar.js world-map/3d-axis-depth.js world-map/index.html scripts/validate_world_map_ui_layout.py
git commit -m "feat(world-map): coordinate floating UI zones"
```

### Task 3: Physical manifest/runtime and first-class menu

**Files:**
- Create: `data/world-map-physical-layers.json`
- Create: `world-map/3d-physical-layers.js`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `world-map/3d-world-bar.js`
- Modify: `world-map/3d-physical-terrain.js`
- Test: `scripts/validate_world_map_ui_layout.py`
- Test: `scripts/validate_world_map_terrain.py`

**Interfaces:**
- Produces `window.__potatoAtlasPhysicalLayers` with `ready`, `entries()`, `get(id)`, `isActive(id)`, `activate(id)`, `deactivate(id)`, `toggle(id)`, `active()`.
- Emits `potato-atlas-physical-change`.
- URL state uses repeated/compact physical IDs via one `physical=` parameter; provider URLs never enter URL state.

- [ ] **Step 1: Add failing manifest/runtime assertions**

Require manifest entry `physical.terrain` with `kind: "module"`, `load_policy: "on_demand"`, current availability, attribution/provider metadata, and no network source fetch in module initialization.

Run validator; expected FAIL.

- [ ] **Step 2: Create manifest**

Initial current entry:

```json
{
  "id": "physical.terrain",
  "label": "Terrain",
  "kind": "module",
  "availability": "current",
  "load_policy": "on_demand",
  "module": "./3d-physical-terrain.js",
  "source": {
    "provider": "Mapterhorn",
    "dataset": "Terrain DEM",
    "version": "live TileJSON endpoint",
    "attribution": "Terrain © Mapterhorn"
  },
  "default_opacity": 0.55,
  "status_note": "Elevation and hillshade load only after activation."
}
```

Add planned metadata-only entries for water base, hydrology, land cover and aridity; planned entries are disabled until a provider/version is pinned.

- [ ] **Step 3: Implement runtime**

Fetch the manifest JSON only. Do not import Terrain on startup. `activate('physical.terrain')` lazily imports/loads the module through `window.__potatoAtlasLoadModule`, then calls `window.__potatoAtlasTerrain.enable()`; deactivation calls `.disable()` without destroying downloaded MapLibre sources.

- [ ] **Step 4: Add Physical top-level menu**

In `3d-world-bar.js`, add `Physical` parallel to `Geography`. Current entries are buttons with `aria-pressed`; planned entries are visibly disabled. Clicking an active entry deactivates it.

- [ ] **Step 5: Remove Terrain’s legacy menu injection**

`3d-physical-terrain.js` stops creating `#atlasTerrainToggle` inside `View`; it only owns terrain behavior/API. Physical menu owns the control surface.

- [ ] **Step 6: Verify Terrain remains lazy**

Run:

```bash
python scripts/validate_world_map_ui_layout.py
python scripts/validate_world_map_terrain.py
```

Expected: PASS. Confirm ordinary startup only fetches the small manifest; DEM TileJSON is referenced/fetched only inside Terrain activation path.

- [ ] **Step 7: Commit**

```bash
git add data/world-map-physical-layers.json world-map/3d-physical-layers.js world-map/3d-panel-lifecycle.js world-map/3d-world-bar.js world-map/3d-physical-terrain.js scripts/validate_world_map_ui_layout.py scripts/validate_world_map_terrain.py
git commit -m "feat(world-map): add lazy Physical World menu"
```

### Task 4: Verification, deployment contract, and provider-ready environmental slots

**Files:**
- Modify: `data/world-map-physical-layers.json`
- Modify: `data/world-map-3d-runtime.json`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Runtime contract documents the UI layout coordinator and Physical family.
- Planned environmental entries carry explicit semantics so later provider activation cannot conflate land cover with deserts or physical hydrology with sacred rivers.

- [ ] **Step 1: Encode provider-ready planned slots**

Ensure the manifest contains distinct planned entries:

```text
physical.water.base      — cartographic ocean/coast/major water context
physical.water.hydrology — measured basin/river/lake data
physical.land-cover      — source taxonomy preserving grassland/cropland/bare/wetland/etc.
physical.aridity         — climatic/ecological desert/aridity regime
```

Their `status_note` fields explicitly state that bare/sparse vegetation is not synonymous with desert and physical hydrology is independent from sacred Four-Rivers interpretation.

- [ ] **Step 2: Update runtime architecture documentation**

Add `ui_layout: "world-map/3d-ui-layout.js"` and `physical_world: "world-map/3d-physical-layers.js + data/world-map-physical-layers.json"` under `renderer_architecture`.

- [ ] **Step 3: Run focused verification**

```bash
python scripts/validate_world_map_ui_layout.py
python scripts/validate_world_map_terrain.py
python scripts/validate_world_map_3d.py
python scripts/validate_world_map_spatial_overlays.py
```

Expected: all PASS.

- [ ] **Step 4: Run the full repository quality workflow through PR CI**

Create a PR, verify the exact head SHA’s `Repository quality checks` workflow concludes `success`, then merge.

- [ ] **Step 5: Verify Pages deployment**

After merge, verify the Pages workflow for the exact merge SHA concludes `success`. Confirm the deployed artifact contains `3d-ui-layout.js`, `3d-physical-layers.js`, the Physical menu, and the new manifest.

- [ ] **Step 6: Commit runtime docs if changed after verification**

```bash
git add data/world-map-physical-layers.json data/world-map-3d-runtime.json scripts/validate_world_map_3d.py
git commit -m "docs(world-map): record physical world runtime contract"
```
