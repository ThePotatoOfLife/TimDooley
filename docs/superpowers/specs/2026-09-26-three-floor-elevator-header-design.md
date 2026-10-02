# Three-Floor Universal Elevator Header — Design Spec

Status: active architecture + visual-world contract  
Date: 2026-09-26  
Scope: universal public-site orientation shell

## Intent

Give every public reader the same spatial grammar without turning the header into another directory.

The universal header answers two questions at a glance:

1. **Which vertical House layer am I viewing?**
2. **Which governed Room owns or best contextualizes this page?**

The interaction must feel physical and smooth: a small elevator rather than a dropdown menu. The user moves vertically with plain metallic arrows. The center reel flips between exactly three floors:

- **Heaven**
- **Plane**
- **Below**

The active Room is visibly illuminated. Global retrieval remains the job of the existing Find / quick-access system.

## Non-goals

- Do not create a fourth Center/Door floor.
- Do not duplicate the complete site hierarchy in the header.
- Do not replace canonical Room ownership.
- Do not make the spatial projection a new knowledge owner.
- Do not remove the existing Find/search workflow.
- Do not add continuous decorative animation or sound.
- Do not force every subject into exactly one permanent floor.

## Core model

A page resolves to two independent coordinates:

```
Floor × Room
```

A Room may have interpretive projections onto more than one floor, but the universal header treats floors as real navigation boundaries. The route has one canonical floor entrance. Flipping the elevator shows only Rooms canonically entered from the selected floor; cross-floor projections remain explanatory metadata inside Room content rather than clickable header doors.

### Floors

#### Heaven

Meaning, integration, canopy, crown, theology, symbolic synthesis, ideals and fruit/expression.

Visual language:

- deep violet / indigo starlit crown-space at the highest edge
- a large low-resolution world-tree canopy, not a generic fantasy wallpaper
- ivory cloud shelves and small star-pixels behind the crown
- warm rose / peach / gold increasing toward lower Heaven
- garden terraces, tiny lights and a continuing trunk/root axis near the Plane handoff
- low-resolution 16/32-bit RPG vocabulary; sacred and cozy rather than glossy or photoreal

#### Plane

Manifest ordinary reality: people, institutions, science, body, politics, economy, culture, history, geography and practical activity.

This is the default / fallback orientation and contains the site's ordinary Home/Door experience.

Visual language:

- the clearest blue daylight of the three floors
- stepped mountain silhouettes, snow caps and cloud bands
- a lived-in village / tower / river / bridge / field / orchard middle world
- moss and grass green, warm roofs, stone grey and muted earth/tan
- looping paths and field spirals that retain the project's organic / relational geometry
- the lower edge visibly becomes grass, soil and first roots so Plane hands off to Below

#### Below

Roots, provenance, archives, raw history, hidden structure, subculture, shadow, conflict, failure, repair, swamp/ash and deep research.

Visual language:

- begin directly beneath the grass with light topsoil / mud, not an open cavern
- descend through visible sediment bands, compact earth, pebbles, root curtains and tangled roots
- wet seams, swamp pockets and occasional small buried voids/chambers may interrupt the soil
- deeper strata become steamier, hotter and more compressed, with rust / oxblood / ember mineral seams
- small fire vents / forge pressure appear near the deepest readable zone
- tiny under-earth inhabitants may appear as incidental silhouettes (rats, goblin-like workers), never as the dominant motif
- charcoal and near-black belong mainly to the deepest layer; Below should not begin as a black wall

"Deep" remains a region or depth inside Below, not a fourth floor.

## Primary Room floor map

Primary floor is the canonical header entrance for a Room. Projection membership may remain broader for interpretation and Room content, but it does not create additional header doors.

| Room | Primary floor |
| --- | --- |
| Potatoverse / Canon | Heaven |
| Archive & Sources | Below |
| Time & History | Plane |
| Traditions & Texts | Heaven |
| Science & Formal Models | Plane |
| Life & Body | Plane |
| World Systems | Plane |
| Culture & Information | Plane |
| Works | Heaven |
| Research Lab | Below |

Examples of cross-floor projection:

- Culture & Information: Heaven = art/meaning; Plane = media/public discourse; Below = subculture/shadow/archives.
- Traditions & Texts: Heaven = theology/sacred interpretation; Plane = institutions/history/practice; Below = manuscripts/source criticism/provenance.
- Potatoverse / Canon: Heaven = cosmology/symbol; Plane = public identity/practical canon; Below = developmental history/raw provenance.

## UI architecture

Add a new universal component:

- `app/site-elevator.js`
- `app/site-elevator.css`

Keep `app/site-access.js` / `app/site-access.css` as the retrieval layer.

The public shell injector loads both systems.

### Header anatomy

Desktop conceptual structure:

```
┌─────────────────────────────────────────────────────────────┐
│  ↑   [ HEAVEN / PLANE / BELOW reel ]   ↓                  │
│      [ Room ] [ Room ] [ ACTIVE ROOM ] [ Room ] ...       │
└─────────────────────────────────────────────────────────────┘
```

The arrows are intentionally minimal:

- no text
- no dropdown caret
- metallic white / grey
- clear pressed/focus state
- large enough for touch targets

The center reel shows the selected floor name. A smaller secondary line may show the current Room label when space allows.

The Room rail only shows Rooms whose `primary_level` equals the selected floor. The active Room is illuminated. A header Room click must never change floors; vertical movement belongs only to the Elevator controls or an explicit in-page gate/door.

### Mobile

- arrows stay fixed at the left/right edges of the reel
- floor name remains visible
- Room rail becomes horizontally scrollable
- active Room auto-scrolls into view on hydration
- no multi-row Room wall
- header height remains stable during floor flips

## Reel / slot-machine motion

Use one directional 3D reel animation.

Down press:

1. current floor face translates upward and rotates away
2. next floor face rises from below
3. floor palette crossfades during the motion
4. Room rail updates after the midpoint

Up press reverses the direction.

Target duration: approximately 420 ms.

Suggested easing:

```
cubic-bezier(.2,.8,.2,1)
```

The animation should feel mechanical but not cartoonish.

No bounce loop. No idle movement.

### Reduced motion

When `prefers-reduced-motion: reduce`:

- no 3D rotation
- no slot-machine motion
- floor swaps immediately or with a very short opacity transition
- all navigation remains fully usable

## Three-floor pixel world

The background system is no longer treated as three decorative biome skins. It is one **continuous vertical world** rendered as inexpensive low-resolution scene plates plus CSS atmosphere.

Canonical scene assets:

- `app/site-tree-perspective.svg` — Heaven / crown / garden / descending trunk
- `app/site-plane-organic-field.svg` — Plane / mountain / village / river / field / soil edge
- `app/site-below-root-field.svg` — Below / topsoil / sediment / roots / swamp / heat / lower basin

### Continuity rule

The floor boundaries must visually hand material to one another:

```
violet stars / crown
        ↓
world-tree canopy
        ↓
peach-gold lower Heaven / garden
        ↓
blue daylight / mountain / village / field
        ↓
grass edge
        ↓
light topsoil / mud
        ↓
sediment / pebbles / roots
        ↓
wet swamp pockets / steam
        ↓
ember seams / fire vents
        ↓
near-black depth
```

The reader should feel that scrolling moves through different depths of one mythic body rather than swapping wallpaper packs.

### Scroll framing rule

Each canonical scene plate is a **tall vertical strip**. The site should fit that strip by scene height (`background-size: auto 100%`) inside a floor-specific scroll-stage box, then translate the whole box upward as the document scrolls. Do not fit the artwork primarily by viewport width: doing so can leave most of the vertical world permanently below the viewport on long, narrow scene plates.

At the end of the ordinary scroll range, retain roughly one viewport of scene material rather than scrolling the art completely away. Current desktop staging is intentionally simple:

- Heaven: about `300vh` scene box / `190vh` travel
- Plane: about `290vh` scene box / `180vh` travel
- Below: about `320vh` scene box / `210vh` travel

This is not a cinematic timeline engine. It is one compositor transform, with floor-specific constants, so the implementation remains cheap and understandable.

### Style rule

Use the supplied fantasy-pixel references for **resolution, warmth and old-RPG readability**, not for literal composition. Project cosmology and the existing House / Axis / Tree / Root / Swamp / Forge structure outrank any reference image.

Prefer:

- broad pixel blocks and stepped silhouettes
- a small number of legible landmarks
- atmospheric negative space behind prose
- scene plates that can scale cheaply
- symbolic details discovered gradually while scrolling

Avoid:

- photorealism
- modern glossy concept-art rendering
- a generic open cave as the primary Below composition
- full-screen decorative noise
- literal Minecraft imitation
- unrelated palettes for the three floors
- turning the page into a game HUD

The backgrounds are environmental storytelling. The document remains the foreground.

## Data ownership

The existing `data/house/elevator-spatial-projection.json` remains the spatial authority.

Upgrade it to a new version with exactly three level IDs:

```
heaven
plane
below
```

The existing `world` elevator level is renamed to `plane`.

Each Dwelling gains:

```json
{
  "primary_level": "plane",
  "projections": ["heaven", "plane", "below"]
}
```

Add a route-context projection section for public routes that are not direct `/rooms/<id>/` pages:

```json
{
  "route_contexts": [
    {
      "match": "/religion/",
      "level_id": "heaven",
      "room_id": "traditions-texts"
    }
  ]
}
```

This is UI/spatial projection only. It does not change Room ownership.

`data/house/rooms.json` remains the source for canonical Room identity/title/purpose.

## Route resolution

`site-elevator.js` exposes a pure resolver.

Resolution order:

1. exact or longest-prefix `route_contexts` match
2. direct `/rooms/<room-id>/...` path match
3. public-surface/known route fallback
4. default to:
   - floor: `plane`
   - room: none

Representative defaults:

- `/` → Plane / Potatoverse Canon
- `/tim-dooley/` → Plane / Potatoverse Canon
- `/potato-of-life/` → Heaven / Potatoverse Canon
- `/religion/` → Heaven / Traditions & Texts
- `/science/` → Plane / Science & Formal Models
- `/economy/` → Plane / World Systems
- `/politics/` → Plane / World Systems
- `/context/culture/` → Plane / Culture & Information
- `/shadow-farm/` → Below / Culture & Information
- `/context/source-authority/` → Below / Archive & Sources
- `/research-lab/` → Below / Research Lab
- `/works/` → Heaven / Works
- `/timeline/` → Plane / Time & History
- `/below/` → Below / no forced Room unless route context is more specific

## Floor switching behavior

Pressing ↑ or ↓ changes the **header orientation**, not the current page URL.

Floor order:

```
Heaven
Plane
Below
```

No wrap-around:

- ↑ is disabled on Heaven
- ↓ is disabled on Below

When the selected floor changes:

- render only Rooms projected to that floor
- if the current Room projects there, keep it illuminated
- otherwise show no false active Room
- page content does not jump
- browser history does not change

Selecting a Room navigates to its canonical Room homepage.

A later enhancement may preserve floor orientation across navigation, but v1 does not alter canonical URLs or add query parameters.

## Room illumination

The active Room button uses:

- brighter border
- floor-accent glow
- slightly raised/pressed-metal contrast
- `aria-current="location"`

Do not rely on color alone. Include an indicator such as a lit top edge / inner bar.

If the page does not resolve to a governed Room, no Room is falsely highlighted.

## Accessibility

- semantic `<header>` + `<nav>`
- ↑ and ↓ are buttons with descriptive `aria-label`
- floor label uses `aria-live="polite"`
- Room buttons/links remain keyboard reachable
- disabled arrow state uses `disabled`
- visible focus ring independent of floor palette
- floor colors meet contrast requirements
- active Room uses non-color state
- reduced-motion path is first-class

Keyboard:

- Up Arrow key while header focused: previous floor
- Down Arrow key: next floor
- Home key: Plane
- Left/Right: optional Room-rail traversal only if it does not conflict with native scrolling

## Loading / failure behavior

The shell appears immediately with a neutral Plane fallback.

Async hydration loads:

- `data/house/elevator-spatial-projection.json`
- `data/house/rooms.json`

If data loading fails:

- keep Plane displayed
- keep ↑/↓ disabled if floor contract is unavailable
- hide Room rail rather than inventing ownership
- existing site navigation remains usable

## Injection and coexistence

Update `scripts/patch_public_navigation.py` to inject:

- `app/site-elevator.css`
- `app/site-elevator.js`

The elevator sits at the top of the viewport.

The existing `site-access` dock remains at the bottom and keeps Find/retrieval responsibility.

Both components publish layout clearance variables so they never cover content:

- `--site-elevator-clearance`
- existing `--site-access-clearance`

Pages with sticky controls can consume both.

## CSS scope

All rules are namespaced under `.site-elevator*`.

No generic `.header`, `.button`, `.room`, `.floor` selectors.

Floor state is expressed with a data attribute:

```
data-elevator-level="heaven|plane|below"
```

Biome palettes use CSS custom properties scoped to the component.

## Validation

Add:

- `scripts/validate_site_elevator.py`
- `scripts/test_site_elevator.mjs`

Validation contract:

1. exactly three floors exist: Heaven / Plane / Below
2. no `world` floor remains in the elevator projection
3. all 10 active Rooms have a `primary_level`
4. every Room projects to at least one of the three floors
5. every primary level is included in that Room's projections
6. every route context references a valid Room and floor
7. universal shell injection includes elevator CSS + JS
8. current Room resolution works for representative routes
9. ↑/↓ stop at Heaven/Below; no wrap
10. floor switch does not mutate URL/history
11. active Room only lights when projected on selected floor
12. reduced-motion CSS disables reel rotation
13. header publishes `--site-elevator-clearance`
14. existing site-access dock remains available

## Initial representative route tests

At minimum:

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
- a direct Room route resolves its Room correctly

## Rollout

1. migrate spatial projection from `world` to `plane`
2. add primary levels + route contexts
3. add pure resolver tests
4. add universal elevator component
5. inject into built public pages
6. verify desktop/mobile/reduced-motion states
7. validate coexistence with bottom quick access, TTS controls and World Map
8. only after the universal header is stable, begin the separate Room decluttering/expansion programme

## Success criteria

The implementation is successful when:

- every normal public page has the same elevator grammar
- the header always resolves to Heaven, Plane or Below
- governed Room pages illuminate the correct Room
- floor flipping is smooth and directional
- floor palettes visibly change without harming readability
- no dropdown is required
- no fourth floor appears
- no page needs to duplicate global navigation to explain where the reader is
- Find remains fast and independent
- the entire interaction remains usable with reduced motion and keyboard-only navigation
