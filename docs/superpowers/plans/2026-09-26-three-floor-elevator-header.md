# Three-Floor Universal Elevator Header Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a universal top-of-site elevator header that resolves every normal public route to Heaven / Plane / Below plus an active House Room, animates floor changes as a smooth reel, and coexists with the existing bottom quick-access dock.

**Architecture:** Keep canonical Room ownership in `data/house/rooms.json`; extend `data/house/elevator-spatial-projection.json` into the UI projection authority for three floors and route contexts. Add a focused `site-elevator` runtime/CSS pair with pure resolver functions, inject it through the existing public-shell patcher, and validate data, route resolution, motion/accessibility and built-site coverage independently of `site-access`.

**Tech Stack:** Static HTML/CSS/vanilla JavaScript, JSON registries, Python validators/build scripts, Node assertion tests, GitHub Actions quality groups.

**Spec:** `docs/superpowers/specs/2026-09-26-three-floor-elevator-header-design.md`

## Global Constraints

- Exactly three floors: `heaven`, `plane`, `below`.
- No fourth Center/Door/Deep floor.
- Center/Home belongs to Plane.
- `Deep` remains a region inside Below.
- Existing canonical Room identities stay in `data/house/rooms.json`.
- Spatial projection is UI/navigation state only; it never becomes a knowledge owner.
- Global retrieval remains in `site-access`; the elevator owns spatial orientation only.
- Floor switching never mutates URL/history.
- Room click navigates to the canonical Room homepage.
- No floor wrap: Heaven disables ↑; Below disables ↓.
- Active Room may remain illuminated across floors only when that Room projects onto the selected floor.
- `prefers-reduced-motion: reduce` removes reel rotation.
- Elevator publishes `--site-elevator-clearance`.
- All CSS selectors are namespaced under `.site-elevator*`.

## Review Focus

- A public route that matches both a broad route context and a direct `/rooms/<id>/` path must resolve to the direct Room without ambiguity.
- A page with no known Room must still show Plane safely without falsely lighting a Room.
- A Room projected onto multiple floors must retain active illumination when the user flips to another valid projection.
- Floor-data fetch failure must not hide page content, break Find, or create a false Room state.
- Mobile/reduced-motion layouts must keep arrow controls usable and must not introduce top-overlay collisions with existing sticky controls.

---

### Task 1: Migrate the elevator projection to the three-floor contract

**Files:**
- Modify: `data/house/elevator-spatial-projection.json`
- Create: `scripts/validate_site_elevator.py`

**Interfaces:**
- Consumes: canonical Room IDs/titles/homepages from `data/house/rooms.json`
- Produces: projection keys `levels[].id`, `dwellings[].primary_level`, `dwellings[].projections`, and `route_contexts[]`

- [ ] **Step 1: Write the failing projection validator**

Validate:
- level IDs equal exactly `["heaven","plane","below"]`
- no `world` level remains
- all 10 active Room IDs appear once in `dwellings`
- each Dwelling has `primary_level`
- every primary level exists in `projections`
- every projection uses one of the three floor IDs
- every route context points at a valid floor and optional valid Room
- representative routes from the spec exist in route contexts

- [ ] **Step 2: Run the validator and confirm it fails**

Run: `python scripts/validate_site_elevator.py`  
Expected: FAIL because the existing projection still uses `world` and lacks the new primary-level/route-context contract.

- [ ] **Step 3: Update the projection data**

Set:
- Potatoverse / Canon → primary `heaven`
- Archive & Sources → `below`
- Time & History → `plane`
- Traditions & Texts → `heaven`
- Science & Formal Models → `plane`
- Life & Body → `plane`
- World Systems → `plane`
- Culture & Information → `plane`
- Works → `heaven`
- Research Lab → `below`

Rename the current `world` level to `plane`. Preserve the existing landmark idea but update labels/descriptions to the three-floor vocabulary. Add route contexts for the representative public routes in the spec.

- [ ] **Step 4: Run the validator and confirm it passes**

Run: `python scripts/validate_site_elevator.py`  
Expected: `SITE ELEVATOR DATA VALIDATION PASSED`

- [ ] **Step 5: Commit**

Commit message: `Elevator: establish three-floor projection contract`

---

### Task 2: Add a pure route/floor/Room resolver

**Files:**
- Create: `app/site-elevator.js`
- Create: `scripts/test_site_elevator.mjs`

**Interfaces:**
- Consumes: projection JSON + Rooms JSON
- Produces:
  - `normalizeRoute(pathname, siteBasePath) -> string`
  - `resolveSpatialContext(route, projection, rooms) -> { levelId, roomId, room, source }`
  - `roomsForLevel(levelId, projection, rooms) -> Room[]`
  - `stepLevel(levelId, direction) -> "heaven"|"plane"|"below"`
  - browser bootstrap that mounts the visual component after data hydration

- [ ] **Step 1: Write failing Node resolver tests**

Assert:
- Home → Plane / Potatoverse Canon
- Religion → Heaven / Traditions & Texts
- Science → Plane / Science & Formal Models
- Politics → Plane / World Systems
- Culture → Plane / Culture & Information
- Shadow Farm → Below / Culture & Information
- Sources → Below / Archive & Sources
- Research Lab → Below / Research Lab
- Works → Heaven / Works
- Timeline → Plane / Time & History
- direct `/rooms/culture-information/...` resolves that Room before broad contexts
- unknown route → Plane / no Room
- Heaven ↑ stays Heaven
- Heaven ↓ → Plane
- Plane ↑ → Heaven
- Plane ↓ → Below
- Below ↓ stays Below
- multi-floor Room appears in every declared projection and active status only when valid

- [ ] **Step 2: Run tests and confirm failure**

Run: `node scripts/test_site_elevator.mjs`  
Expected: FAIL because resolver exports do not exist.

- [ ] **Step 3: Implement only the pure resolver/data helpers**

Keep DOM mounting behind a `typeof document !== "undefined"` guard so the same module can be required from Node tests.

- [ ] **Step 4: Run tests and confirm pass**

Run: `node scripts/test_site_elevator.mjs`  
Expected: PASS with representative route and floor-stepping assertions.

- [ ] **Step 5: Commit**

Commit message: `Elevator: add route and floor resolver`

---

### Task 3: Build the visual elevator header

**Files:**
- Modify: `app/site-elevator.js`
- Create: `app/site-elevator.css`
- Extend test: `scripts/test_site_elevator.mjs`

**Interfaces:**
- Consumes: Task 2 resolver helpers
- Produces:
  - one `.site-elevator` header
  - `data-elevator-level="heaven|plane|below"`
  - ↑ / ↓ buttons
  - floor reel with `aria-live="polite"`
  - Room rail with canonical links and `aria-current="location"`

- [ ] **Step 1: Add failing source/DOM-contract assertions**

Assert source contains:
- `site-elevator-up`
- `site-elevator-down`
- `site-elevator-reel`
- `site-elevator-room-rail`
- `aria-live="polite"`
- `aria-current`
- no floor URL/history mutation
- disabled arrow state at boundaries

- [ ] **Step 2: Implement initial neutral Plane shell + async hydration**

Before data loads:
- render Plane
- arrows disabled
- Room rail hidden
- page remains fully usable

After hydration:
- resolve route
- enable valid arrows
- render Room rail for selected floor
- illuminate current Room only if projected there

- [ ] **Step 3: Implement floor switching**

↑ / ↓ changes selected floor only.  
Do not call `history.pushState`, `history.replaceState`, or assign `location`.

- [ ] **Step 4: Add keyboard behavior**

When focus is inside the elevator:
- ArrowUp → previous floor
- ArrowDown → next floor
- Home → Plane

Do not hijack typing or page-global arrow keys.

- [ ] **Step 5: Run Node tests**

Run: `node scripts/test_site_elevator.mjs`  
Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `Elevator: render route-aware universal header`

---

### Task 4: Add the reel motion, floor palettes and biome texture

**Files:**
- Modify: `app/site-elevator.css`
- Extend: `scripts/validate_site_elevator.py`

**Interfaces:**
- Consumes: `data-elevator-level` and directional transition classes from Task 3
- Produces: stable-height three-floor visual treatment

- [ ] **Step 1: Add failing CSS validation markers**

Require:
- all main selectors start with `.site-elevator`
- Heaven palette variables
- Plane palette variables
- Below palette variables
- `transform: rotateX` or equivalent directional reel transform
- duration in the 350–500 ms range
- `prefers-reduced-motion:reduce`
- `--site-elevator-clearance` publication/consumer marker
- active Room uses a non-color indicator

- [ ] **Step 2: Implement component-scoped floor palettes**

Heaven:
- sky/ivory/gold/silver

Plane:
- moss/green/stone/earth

Below:
- charcoal/peat/rust/oxblood

Use CSS gradients/repeating gradients only; no new image dependency.

- [ ] **Step 3: Implement directional reel transition**

Use approximately 420 ms and `cubic-bezier(.2,.8,.2,1)`.

- [ ] **Step 4: Implement active Room illumination**

Use floor accent plus a visible lit edge/inner bar so state survives grayscale/color-vision differences.

- [ ] **Step 5: Implement mobile stability**

- stable header height
- Room rail horizontal overflow
- arrows remain fixed/large enough for touch
- active Room scrolls into view after hydration

- [ ] **Step 6: Implement reduced-motion fallback**

Remove 3D/slot rotation and use immediate or minimal opacity state swap.

- [ ] **Step 7: Run validation**

Run:
- `python scripts/validate_site_elevator.py`
- `node scripts/test_site_elevator.mjs`

Expected: PASS.

- [ ] **Step 8: Commit**

Commit message: `Elevator: add floor biomes and reel motion`

---

### Task 5: Inject the elevator into the universal public shell

**Files:**
- Modify: `scripts/patch_public_navigation.py`
- Modify: `scripts/validate_site_access.py`
- Modify: `scripts/run_quality_group.py`

**Interfaces:**
- Consumes: `app/site-elevator.css`, `app/site-elevator.js`
- Produces: built-site elevator assets on every normal public surface while preserving `site-access`

- [ ] **Step 1: Write failing injection validation**

Require built representative surfaces to contain:
- `site-elevator.css`
- `site-elevator.js`
- existing `site-access.css`
- existing `site-access.js`

Require patcher source to expose dedicated `patch_site_elevator` / injection markers rather than merging elevator logic into `site-access`.

- [ ] **Step 2: Update the shell patcher**

Inject elevator CSS/JS once, without duplicating existing head assets.

- [ ] **Step 3: Publish top clearance**

`site-elevator.js` measures the mounted header and writes:
- `--site-elevator-clearance`

Do not alter the existing bottom:
- `--site-access-clearance`

- [ ] **Step 4: Add elevator tests to the normal quality group**

Add:
- `python scripts/validate_site_elevator.py`
- `node scripts/test_site_elevator.mjs`

to the appropriate Core/Content quality group without duplicating execution.

- [ ] **Step 5: Run source validation**

Run:
- `python scripts/validate_site_access.py`
- `python scripts/validate_site_elevator.py`
- `node scripts/test_site_elevator.mjs`

Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `Elevator: integrate universal public shell`

---

### Task 6: Build-site collision and coverage verification

**Files:**
- Modify as needed: `scripts/validate_site_elevator.py`
- Modify only if demonstrated: `world-map/index.html`, `app/tts-drawer.js`, or other fixed-control consumers
- Modify: `TODO.md`

**Interfaces:**
- Consumes: full built `_site`
- Produces: verified site-wide rollout with no known fixed-header collision

- [ ] **Step 1: Build the public site**

Run the repository's existing public build command used by the quality workflow.

Expected: build succeeds and generated representative pages include the elevator.

- [ ] **Step 2: Validate representative surfaces**

At minimum inspect/validate:
- Home
- House
- Rooms
- Religion
- Science
- World
- North
- Below
- Shadow Farm
- Research Lab
- World Map
- Current World
- Tim Dooley
- one direct Room page

Require:
- exactly one elevator
- exactly one bottom site-access dock
- correct resolved default floor/Room where applicable
- no duplicate injected assets

- [ ] **Step 3: Check fixed-control coexistence**

Verify top elevator does not cover:
- native first heading/content
- World Map top controls
- sticky TTS drawers/selection controls
- page-local sticky headers

Add page-specific top offsets only for demonstrated collisions.

- [ ] **Step 4: Close the new elevator TODO programme**

Record:
- three-floor contract shipped
- universal header injected
- Room highlighting verified
- reduced-motion verified
- collision audit result

Do not begin Room decluttering in the same PR.

- [ ] **Step 5: Run full quality workflow locally where available**

Run the same quality-group commands as CI for Core, Content and World Map.

Expected: all PASS.

- [ ] **Step 6: Open PR and require full GitHub Actions green**

Merge only when:
- Core · House · Atlas = green
- Content · Research · Bible = green
- World Map = green
- Public build · SEO · Science = green
- final validate = green

- [ ] **Step 7: Commit/merge**

Final feature commit/PR title: `Elevator: ship three-floor universal header`

---

## Self-review result

- Spec coverage: all visual, data, resolver, accessibility, injection, collision and rollout requirements have an owning task.
- Type/interface consistency: projection keys and resolver names are defined once in Tasks 1–2 and reused by later tasks.
- Review-focus coverage: direct Room precedence, unknown routes, multi-floor active Rooms, data-load failure and mobile/reduced-motion behavior are explicitly exercised.
- Scope: Room-content decluttering is intentionally excluded and begins only after this header stabilizes.
