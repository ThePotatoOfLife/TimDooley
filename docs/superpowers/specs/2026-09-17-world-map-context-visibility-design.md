# World Map Context / Visibility Orchestration — Design

**Date:** 2026-09-17  
**Status:** approved implementation direction  
**Scope:** World Relational Atlas application state, country selection context, visibility budgeting, pinned-country summaries, time-aware presentation, and progressive disclosure.

## 1. Purpose

The World Relational Atlas already has strong low-level owners for geography, analytical layers, selection, time, relationships, evidence, spatial overlays, render ordering, interaction and inspectors. The next improvement is to coordinate those owners around the user's current question so the map reveals the most relevant information without accumulating overlapping controls, panels and visual clutter.

This design adds a small **Context / Visibility Orchestrator**. It does not own domain data, render geometry, or replace existing registries. It reads current application state and publishes a deterministic visibility/context policy that existing and future modules can consume.

The first implementation wave also adds a compact **Pinned Context Rail** so retained countries remain meaningfully visible while one active country keeps the main inspector.

## 2. Governing principles

1. **One map, many semantic planes.** Keep the established map planes separate: base geography, physical world, analytical country layers, relationships, typed spatial overlays, time, selection/investigation and provenance.
2. **One active country, many retained contexts.** Ordinary browsing has one deep active country. Pinned countries remain available as lighter comparison/context objects.
3. **Question drives disclosure.** Visibility depends on active country, pinned countries, scale, time, active analytical question, investigation mode and screen-space budget.
4. **Epistemic type survives orchestration.** Observed, derived, project-interpretive, scenario, historical/textual reconstruction and disputed/current layers are never merged because they overlap visually.
5. **Progressive disclosure beats maximum density.** Show enough to orient and compare, then let the inspector, Evidence, Trace, Path and specialist views reveal more.
6. **No new canonical database in the frontend.** The orchestrator reads public subsystem APIs and browser-facing registries; canonical values remain owned by existing data files.
7. **No new map product.** Predictions, culture, coinage and other future specialist domains must plug into this same control grammar rather than creating a separate map.

## 3. Existing owners preserved

The implementation must preserve these owners:

- `world-map/3d-country-selection.js` — active country + pinned countries + relation mode;
- `world-map/3d-active-view.js` — current country-level analytical answer;
- `world-map/3d-scale.js` — named scale bands and capability thresholds;
- `world-map/3d-time.js` / time API — current/as-of/changed-between state;
- `world-map/3d-layer-registry.js` + compositor — analytical layers and composition;
- `world-map/3d-spatial-overlays.js` — typed geographic overlays;
- `world-map/3d-interaction-router.js` — semantic hit-test priority;
- `world-map/3d-inspector-router.js` — persistent semantic inspector state;
- `world-map/3d-ui-layout.js` — application-surface placement;
- `world-map/3d-map-state.js` — semantic reset/snapshot;
- `world-map/3d-render-stack.js` — render ordering;
- evidence / Trace / Path modules — investigation semantics.

The orchestrator may consume these APIs but does not reach around them to mutate domain internals.

## 4. Context model

Add one browser runtime owner:

`world-map/3d-context-visibility.js`

It publishes a snapshot with this conceptual shape:

```js
{
  activeCountry: 'DNK',
  pinnedCountries: ['CAN', 'DEU'],
  scaleBand: 'region',
  time: { mode:'current', time:'', time2:'' },
  question: {
    analytical: 'stat.inflation',
    relationMode: 'systems',
    investigation: 'browse'
  },
  epistemic: {
    activeTypes: ['observed', 'project_interpretive']
  },
  budgets: {
    activeRelations: 8,
    pinnedRelations: 2,
    pinnedCards: 4,
    statusSurfaces: 3
  },
  visibility: {
    showActiveRelations: true,
    showPinnedContext: true,
    showPlaceDetail: false,
    showSubdivisionDetail: false,
    emphasizeEvidence: false,
    suppressDecorativeProjectOverlays: false
  }
}
```

Exact values may differ, but the public contract must be stable enough for consumers and tests.

## 5. Visibility inputs

The orchestrator reads:

- active country;
- pinned countries;
- current relation mode;
- active analytical scalar/set layers;
- current time mode/window;
- current scale band;
- inspector state when available;
- whether Evidence/Trace/Path or Compare-like investigation is active;
- viewport/screen class only as a coarse budget input, not domain meaning.

No input may silently redefine another plane. For example, zoom changes visual detail but not epistemic type; time changes valid records but not country identity.

## 6. Question modes

The first wave uses four lightweight modes derived from current state rather than adding a large new toolbar:

- `browse` — one active country, automatic major context;
- `compare` — multiple pinned countries are the explicit focus;
- `connections` — relation mode/Trace/Path is primary;
- `evidence` — provenance/source state is primary.

A future `predictions` or `culture` specialist view should be implemented as a typed investigation adapter that feeds this same model, not as an independent windowing system.

## 7. Budget rules

Budgets are deterministic and readable, not probabilistic.

### World / macro-region
- active country: 4–8 strongest country/institution relations;
- pinned countries: up to 2 lightweight relations each;
- pinned rail: up to 4 visible cards before horizontal/overflow navigation;
- detailed places/subdivisions hidden unless explicitly inspected.

### Region / country
- active country keeps 6–10 useful relations;
- pinned countries remain lighter than active;
- places and major assets may appear when their existing scale capability allows;
- subdivisions load/render according to the shared scale contract.

### Subnational / local
- real places/assets/facilities outrank abstract global relation clutter;
- country-level network lines are reduced unless explicitly in Connections/Trace mode.

The orchestrator does not itself draw or delete features. It publishes budgets and visibility intent for consumers.

## 8. Epistemic visibility rules

The first wave must preserve rather than over-automate epistemic display.

- `browse`: current observed/derived analytical layers stay ordinary; project-interpretive overlays remain available but do not gain extra emphasis merely because a country is selected.
- `evidence`: project-interpretive/scenario/historical overlays may remain visible, but evidence/source/status presentation becomes dominant and decorative emphasis is reduced.
- `compare`: only comparable country-level values/memberships should be promoted; unmatched specialist overlays remain background context.
- `connections`: relation lines/nodes receive the largest visual/context budget while scalar fills remain one background analytical question.

No orchestrator rule changes an overlay's declared `epistemic_type`.

## 9. Pinned Context Rail

Add a compact rail owned by a focused UI module:

`world-map/3d-pinned-context.js`

The rail appears only when there are pinned countries.

Each pinned country card shows a compact, sourced answer drawn from `3d-active-view.js` and selection/runtime APIs:

- country name/code;
- whether it is the active country;
- active scalar value/"Unknown" when applicable;
- active set-membership summary when applicable;
- current relation-mode context count when cheaply available;
- source/period only when they fit without turning the card into a second inspector.

Interactions:

- click card → activate that country;
- remove control → unpin country;
- cards update when layer, time, relation mode or active selection changes;
- active-country card is visually distinct but remains part of the same rail if pinned.

The rail must not duplicate the full Country Card or Country Pulse.

## 10. UI placement

The existing UI layout coordinator remains the placement owner.

Add a new layout zone:

- `bottom-context`

The pinned rail registers into that zone. The selection controller must stop directly owning a free-floating bottom strip once the rail reaches parity.

Desktop:
- compact bottom-center rail;
- right inspector remains the one deep persistent inspector;
- left status remains provenance/time/lens context.

Mobile:
- rail becomes horizontally scrollable above the bottom inspector sheet;
- it must not occlude primary map controls;
- when the inspector expands, the layout coordinator may reduce rail height or hide nonessential details while preserving the pinned set.

## 11. Time behavior

The orchestrator treats time as a first-class context input.

- current mode: use current observations/relationships as existing runtimes define them;
- as-of mode: pinned summaries and active-view answers must use the same as-of state;
- changed-between mode: the first wave may expose a compact "comparison window active" state even where individual domain runtimes do not yet provide change deltas.

Undated records remain unknown in historical views.

Future prediction integration will add separate forecast issue/target/outcome windows; those must not be collapsed into the map's ordinary observation time.

## 12. Events and refresh model

The orchestrator listens to existing public events such as:

- `potato-atlas-working-selection-change`;
- `potato-atlas-pin-change`;
- `potato-atlas-relation-mode-change`;
- `potato-atlas-layer-change`;
- `potato-atlas-composition-change`;
- `atlas-time-change`;
- scale change / map move-end through the shared scale API;
- inspector or evidence-mode events when available.

It publishes:

`potato-atlas-context-visibility-change`

Consumers subscribe to that event or read:

`window.__potatoAtlasContextVisibility.current`

Refreshes are microtask-coalesced and stale async work is discarded using a serial/generation counter, following the active-view pattern.

## 13. Integration with automatic relations

`3d-country-selection.js` remains the relation-data owner.

Add a public budget setter or budget-aware application path so relation rendering can consume orchestrator budgets without moving edge ranking logic out of selection.

Preferred interface:

```js
window.__potatoAtlasSelection.setAutomaticRelationBudget({
  active: 8,
  pinned: 2,
  total: 20
});
```

The selection module remains responsible for:

- ranking edges;
- diversity buckets;
- relation-mode filtering;
- generating relation GeoJSON.

The orchestrator only says how much context is appropriate now.

## 14. Reset and URL state

The first wave does not add new required URL parameters. Context mode is derived from existing state where possible.

Pinned countries, active country, relation mode and time already have URL/state owners.

`3d-map-state.js` should include the orchestrator snapshot in diagnostics but reset underlying semantic owners rather than resetting the orchestrator separately.

## 15. Diagnostics

Expose bounded diagnostics:

- orchestrator refresh count;
- last context mode;
- last scale band;
- active/pinned budgets;
- pinned rail card count;
- stale async suppressions.

The architecture auditor/validator should verify:

- only one context orchestrator exists;
- pinned rail registers through UI Layout;
- automatic relation budgets are consumed through the selection API;
- no new direct country-fill ownership is introduced;
- no new raw zoom thresholds are introduced.

## 16. Testing

Add behavioral/runtime tests for:

1. active country only → browse budgets;
2. active + pinned countries → lighter pinned budgets;
3. change active country → rail preserves pins and updates emphasis;
4. layer change → pinned summaries update;
5. time change → context and rail refresh;
6. scale change → budgets/detail flags change without changing ontology;
7. Connections mode → relation budget increases appropriately;
8. Evidence mode → evidence emphasis flag is active and project overlay type is not rewritten;
9. mobile/narrow viewport → rail remains bounded and scrollable;
10. reset → active/pinned/time owners reset and context derives neutral state.

## 17. Non-goals for this wave

This wave does not:

- implement the prediction archive adapter;
- create a separate culture map;
- create multiple free-floating inspector windows;
- change canonical country data;
- change sacred/project geography semantics;
- add live tactical conflict tracking;
- redesign the entire World Bar;
- replace Compare, Trace, Path or Evidence;
- add a second canonical relation-ranking engine.

## 18. Next extensions after this wave

Once the context/visibility foundation is stable, the meaningful order is:

1. richer time/window model;
2. prediction timeline/map adapter;
3. observed-event linking for prediction outcomes;
4. Compare workspace improvements using pinned context;
5. culture/coinage provenance adapter and non-geographic diffusion scene;
6. saved/deep-linked investigations;
7. broader economy/energy/infrastructure/ownership data expansion.

## 19. Definition of success

The map is better when a user can click through several countries, retain a few for comparison, change layers/time/relation modes and zoom in/out while the application automatically reveals the right amount of context without losing provenance or turning every subsystem into a competing panel. The new owner should make later specialist features simpler to add because they can declare context needs instead of inventing their own visibility logic.
