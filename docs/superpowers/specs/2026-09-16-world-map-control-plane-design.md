# World Map Control Plane — Design

**Date:** 2026-09-16  
**Status:** approved governing direction  
**Scope:** World Map runtime, cartographic mathematics, interaction, UI coordination, rendering ownership, behavioral verification and roadmap convergence.

## 1. Purpose

The World Map is now a modular analytical application rather than a single map page. Its next quality step is not another isolated feature wave. It is a control plane that makes existing and future modules obey one shared grammar for geography, scale, rendering, interaction, tooltip ownership, inspector state, URL state, lifecycle, provenance and performance.

The control plane must reduce accidental overlap without collapsing domain modules into a monolith. Domain modules continue to own domain semantics; shared infrastructure owns shared mechanics.

## 2. Governing principle

A map feature is not complete merely because it renders. Every map capability must be able to answer:

1. Who owns its canonical data and runtime state?
2. Which mathematical plane does it occupy: geography, topology, hierarchy, time or declared flow?
3. At which camera scales may it load, render, label and accept interaction?
4. Which visual channel does it own: fill, pattern, outline, line, point, height, card, timeline or scene?
5. What may overlap it, and how is overlap explained?
6. Which object wins hover/click when multiple rendered features occupy one screen point?
7. How does it behave across the antimeridian, repeated world copies and projection changes?
8. How is transient hover different from persistent inspection?
9. Which state is represented in the URL and how is it restored?
10. How does it restore after style changes?
11. What is its runtime cost and cache/load budget?
12. Which behavioral regression proves the user-visible behavior?

If these questions cannot be answered, the feature is not ready for permanent promotion.

## 3. Architecture

```text
                  WORLD MAP CONTROL PLANE
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   Lifecycle Registry   State Registry   Data Catalog
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ACTIVE VIEW MODEL
                           │
     ┌────────────┬────────┼───────────┬────────────┐
     │            │        │           │            │
Geospatial     Scale    Rendering  Interaction   Inspector
 Kernel      Controller   Stack       Router       Router
     │            │        │           │            │
     └────────────┴────────┼───────────┴────────────┘
                           │
                    MapLibre renderer
                           │
                  canonical project data
```

Supporting coordinators:

- Transient Tooltip Service
- Style Lifecycle Coordinator
- UI Surface Registry / shared design tokens
- Evidence and coverage surfaces
- Runtime diagnostics / performance budgets
- Architecture auditor
- Behavioral test harness

## 4. Spatial mathematics contract

### 4.1 Canonical Earth identity

Repeated visual world copies must never create repeated semantic entities. One ISO country, place, subdivision, facility or sourced geographic feature has one canonical identity even when MapLibre renders wrapped copies.

### 4.2 Longitude and antimeridian

The shared geospatial kernel owns:

- `normalizeLongitude(lng)` → canonical longitude in `[-180, 180)`;
- `shortestLongitudeDelta(fromLng, toLng)` → signed shortest delta in `[-180, 180)`;
- `unwrapLongitude(lng, referenceLng)` → equivalent longitude nearest the reference;
- `antimeridianAwareBounds(points, referenceLng?)` → smallest useful longitudinal span for the input coordinates;
- `viewportIntersects(bounds, viewport)` → intersection that understands wrapped longitudes;
- `haversineDistanceKm(a, b)` → geographic distance for prioritization where real-world distance matters.

Raw `max(lng)-min(lng)` must not be the default for geometry that can cross ±180°.

### 4.3 World-copy policy

The renderer may retain visual world copies for navigation, but logical selection, hover, URL state, evidence lookup, place identity and canonical feature state use normalized identity and coordinates. No module may treat a wrapped copy as a second object.

### 4.4 Geographic versus schematic lines

Every line-like feature must declare a geometry meaning, such as:

- `relationship_chord`
- `great_circle_relation`
- `observed_physical_route`
- `approximate_corridor`
- `symbolic_route`
- `reconstructed_route`

A schematic relationship line must not visually imply a surveyed route.

### 4.5 Projection discipline

Earth geography remains geographic. Nonspatial semantic layout remains nonspatial or screen/local-layout based. Navigation constellations may use mathematical packing, but raw degree offsets must not be treated as uniform physical distances, especially near the poles.

## 5. Scale contract

The camera scale vocabulary is:

- `world`
- `macro-region`
- `region`
- `country`
- `subnational`
- `local`

Each capability may define four independent thresholds:

- **load** — data may be fetched/cached;
- **render** — geometry may appear;
- **label** — text may appear;
- **interact** — feature may become a hover/click target.

Thresholds are centralized, named and versioned. Modules may consume them but do not invent new numeric thresholds without extending the contract.

Scale transitions use hysteresis where toggling near a boundary would cause repeated load/render churn.

Zoom is camera scale only. It does not redefine graph distance, Axis depth, time, evidence strength or epistemic class.

## 6. Render and visual-channel contract

The Render Stack owns layer ordering. Visual channels have distinct jobs:

- fill: one scalar surface;
- pattern: categorical/set memberships;
- outline: hover/selection/focus;
- line: typed relationship/route/flow semantics;
- point: honestly located entities/events;
- height: one explicitly declared scalar only;
- card: nonspatial context;
- timeline: temporal state;
- scene: explicitly non-geographic topology/hierarchy.

A compatibility matrix must reject combinations that assign contradictory semantic ownership to the same channel.

Direct paint mutation outside the declared owner is compatibility debt and must be migrated incrementally.

## 7. Interaction Router

Render z-order does not automatically define semantic interaction priority.

Modules register interactive targets with:

- layer ids;
- semantic object type;
- hover priority;
- click priority;
- cursor;
- scale range;
- enabled predicate;
- hover/click handlers.

One router queries rendered features and selects the winning semantic target. The existing cooperative `__potatoAtlasOverlayHandled` convention is transitional and should disappear after registered consumers migrate.

Default intent priority should favor explicit UI/selected real objects, then real places/assets, subdivisions, interactive overlays/relations, countries and finally background. The exact matrix is a data contract, not scattered listener order.

## 8. Transient Tooltip Service

One service owns transient hover popups across country, Axis, Fields, Networks, infrastructure and other modules.

It owns:

- exactly one transient popup;
- HTML/sanitization path;
- maximum width and offset policy;
- async generation/stale-result suppression;
- pointer/cursor relationship;
- motion invalidation.

Transient tooltips are suppressed/cleared on meaningful drag, zoom start, rotation, pitch, projection change, style generation change, owner deactivation and a newer hover generation. Persistent click/inspection surfaces are separate.

The existing pointer-drag CSS guard remains a compatibility fallback until all transient popup owners migrate.

## 9. Inspector Router

The right inspector represents semantic application state, not raw HTML history.

Place and subdivision modules must eventually stop restoring `panel.innerHTML` snapshots. Instead they open typed inspector frames such as:

```js
{
  type: 'place',
  id: 'gn:2618425',
  parent: { type: 'country', id: 'DNK' }
}
```

The router supports deterministic back/close behavior, deep-link restoration and nested context. Closing a child returns to the correct semantic parent rather than stale HTML.

## 10. Style lifecycle

Only one style lifecycle coordinator should own global restoration generations. Modules register restore/reconcile callbacks instead of independently accumulating `styledata` orchestration.

A generation has deterministic phases:

1. style generation begins;
2. required sources restored;
3. active domain layers restored;
4. Render Stack reconciled;
5. interaction registration validated;
6. generation marked ready.

Independent module listeners may remain during migration but are compatibility debt.

## 11. UI system

Shared World Map UI owns design tokens for:

- z-index bands;
- spacing;
- radii;
- typography;
- surfaces;
- focus outlines;
- transitions;
- tooltip/card/menu/legend primitives.

Domain modules may retain domain-specific CSS, but global placement and common component styling should not be redefined independently.

The public control vocabulary should trend toward user questions rather than backend modules:

- Browse
- Compare
- Connections
- Evidence
- Time
- View

Advanced/specialized layers remain progressively disclosed.

## 12. Accessibility and motion

The map must not require precise hover or color perception to understand state. Work includes keyboard navigation, visible focus, focus restoration, semantic labels, non-color selection encodings, concise active-view descriptions and reduced-motion camera behavior.

## 13. Behavioral verification

Contract/token tests remain useful but are not sufficient. A small browser/fake-runtime behavioral tier should cover combined behaviors:

1. hover country → drag;
2. hover country → zoom;
3. Mercator → globe → Mercator;
4. pan/fit through ±180°;
5. select a wrapped world-copy feature;
6. country → subdivision → place → back;
7. overlapping interactive layers at one point;
8. Evidence while country context is visible;
9. slow crossing of every named scale band;
10. style generation with physical layers enabled;
11. mobile menu + inspector + search;
12. reduced-motion camera navigation.

Tests should assert observable behavior, not merely implementation strings, whenever practical.

## 14. Performance contract

Existing bounded partitions/caches remain. The control plane adds diagnostics for:

- active sources/layers;
- registered interaction targets;
- transient tooltip generations/stale suppressions;
- style restoration generations/work;
- scale transitions;
- lazy module loads;
- cache bytes/partitions;
- first-interaction latency where measurable.

A richer map must not make visited-history growth unbounded.

## 15. Compatibility retirement

Compatibility modules are drained, not abruptly deleted.

For each legacy owner:

1. inventory unique behavior;
2. move each behavior to its canonical owner;
3. add a regression proving the owner;
4. prove no active consumer depends on legacy behavior;
5. retire/archive/delete only after unique behavior is preserved.

Priority compatibility targets include `3d-ui.js`, `3d-selection-ui.js`, old Lens ownership and old Atlas naming/routing remnants.

## 16. Implementation order

1. Governing roadmap/spec + architectural inventory.
2. Spatial Kernel + world-wrap/antimeridian tests.
3. Scale Contract + hysteresis tests.
4. Interaction Router + overlap-priority tests.
5. Transient Tooltip Service + drag/zoom/projection tests.
6. Inspector Router + typed navigation tests.
7. Visual-channel compatibility + render ownership audit.
8. Style lifecycle convergence.
9. UI token/component convergence + accessibility/reduced motion.
10. Behavioral browser scenario tier + performance budgets.
11. Compatibility retirement.
12. Deeper empirical data expansion and advanced non-geographic mathematical views.

## 17. Non-goals

This design does **not**:

- replace the canonical data model;
- collapse empirical, historical, interpretive or project-symbolic layers;
- turn Axis depth into physical dimensions;
- turn zoom into ontology;
- give abstract concepts fake geographic coordinates;
- force spectral/hyperbolic/Hodge mathematics into Earth geography;
- add another public map product;
- remove proven fallback behavior before a tested replacement exists.

## 18. Definition of success

The map is improved when adding a new capability becomes safer and more predictable: there is one obvious place to register its scale, visual channel, interaction, tooltip, inspector state, style lifecycle, provenance and tests. User-visible behavior remains stable through zoom, pan, wrap, projection changes, overlapping layers and progressive loading, while the codebase accumulates fewer duplicate mechanics.