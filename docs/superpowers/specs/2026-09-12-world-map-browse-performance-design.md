# World Map Browse-First Interaction, Statistics Cohesion, and Performance Cleanup

Date: 2026-09-12
Status: Approved direction, implementation pending

## Purpose

Make the World Relational Atlas feel like a map a person can simply explore.

The current system is powerful, but ordinary clicks carry too much state: a country click both inspects a country and adds/removes it from a persistent working selection. At the same time, map color overlays, statistics, comparison state, relation state, and deeper analysis tools are technically connected but not visually or conceptually unified. Several modules also repeat rendering/enrichment work.

This redesign preserves the existing investigation capabilities while giving them a simpler default mental model:

- **Map color = the question being asked.**
- **Clicked country = the thing currently being inspected.**
- **Pins = countries deliberately retained for comparison or multi-country investigation.**
- **Specialist tools = explicit investigations, not side effects of ordinary browsing.**

No feature is removed. No routine UI action should automatically zoom or refocus the map.

## Approaches considered

### 1. Patch the existing persistent multi-select model

Keep ordinary clicks adding/removing countries, but improve chip labels, selection affordances, and instructions.

Rejected because the root ambiguity remains: the same click still means both “look at this country” and “modify my retained working set.” It would polish the confusing model rather than fix it.

### 2. Browse + Pins with shared active-view context — selected

Make ordinary clicks replace the active country. Retained multi-country state becomes explicit through Pin/Compare or a deliberate modifier gesture. Centralize the active map overlay/statistical context so the compact card, inspector, legend/context, comparisons, and map all describe the same active measure.

This changes the least while fixing the deepest interaction and information-flow problems.

### 3. Full workspace/state-machine rewrite

Rebuild the Atlas around explicit Browse, Compare, Path, Impact, and Analysis workspaces.

Rejected for now because it would be a high-risk rewrite, would create migration cost across many existing modules, and is not necessary to achieve the desired intuitive behavior.

## Interaction architecture

### Browse is the default

An ordinary country/entity click:

1. makes that entity the `activeCode`;
2. updates the compact country card;
3. updates the deeper inspector if it is open;
4. updates the exact active-overlay value shown for that country;
5. recenters the bounded automatic relationship context around that active country;
6. does **not** add/remove the country from a persistent multi-selection;
7. does **not** zoom or refocus the camera.

Clicking another country immediately replaces the active country. Clicking the same country again keeps it active; ordinary browsing never requires deselection.

### Pins are deliberate retained state

Introduce a distinct `pinnedCodes` state separate from `activeCode`.

Countries are pinned only by deliberate actions such as:

- `Pin` / `Compare` action in the country card;
- an explicit compare flow;
- Shift-click as an optional power-user shortcut.

Pinned countries are visually distinct but quieter than the active country. The retained strip, if shown, represents **pinned** countries only and should say so; it must no longer imply that every country ever clicked is “selected.”

Unpinning a country does not close or clear the currently active country unless the user explicitly closes the country view.

### Compare semantics

Comparison is built from pins, not browse history.

- one active country + zero pins: normal browse;
- multiple pins: comparison set available;
- Compare explicitly opens the comparison presentation;
- clicking around while Compare is not explicitly active continues to browse normally;
- comparison state is not silently mutated by ordinary clicks.

Backward-compatible URL parsing may continue to accept legacy `selected=` parameters, but new URLs should serialize retained countries as pins if feasible without breaking existing links.

### Relationship semantics

Automatic connection lines are contextual browse information.

By default:

- automatic relations are computed from the active country only;
- changing active country replaces that automatic relation context instead of accumulating relation roots;
- relation filters still apply.

Explicit investigation tools may retain multi-country context:

- Path;
- Compare;
- explicit Trace;
- Impact;
- Chain/Gateway/Infrastructure workflows when the user deliberately enters them.

These tools must not convert ordinary browse clicks into persistent selection implicitly.

## Active View Context

Create one shared presentation-level view of the current map question and selected-country answer. It should be derived from the existing registry/compositor/runtime rather than becoming another independent source of truth.

The context should expose at minimum:

- active scalar layer, if any;
- active set/category layers;
- active country code;
- active country observation for the scalar;
- formatted value;
- unit;
- period/year;
- source/provenance pointer where available;
- coverage state;
- epistemic/status notes where relevant;
- active set membership/query match;
- relation filter mode.

Consumers include:

- compact country card;
- deeper right inspector / Country Pulse;
- passive lower-left map context;
- scalar legend/context;
- comparison views;
- future statistics browser.

The compositor/runtime remain authoritative for actual map rendering and metric data. The active-view context is an adapter for consistent presentation, not a competing data store.

## Country card information hierarchy

The upper-left card remains the default inspection surface.

### Header

Show country/entity identity and compact state actions.

### Map view block

Immediately below identity, when a map overlay or group query is active, show a visually distinct block explaining what the map color means for this country.

Examples:

- `Map color · GDP / person` → `$54,300 · 2025`
- `Map color · Life expectancy` → `81.2 years · 2024`
- `Map view · Catholic share` → `62%`
- `Map view · North Axis` → `Primary · project interpretation`

Where available, include concise period/source/coverage information without making the card large.

Missing data is explicitly `Unknown` / `No comparable observation`; never zero-filled.

### Core metrics

Preserve the compact default metrics below the Map view block.

### Actions

Keep existing investigation actions and add/clarify:

- `Statistics` / `More statistics`;
- `Pin` / `Unpin` or equivalent retained-comparison action;
- Connections / Trace;
- Path;
- Impact.

The statistics action opens the existing deeper inspector focused on statistics rather than creating another floating panel.

## Deeper statistics and inspector

The deeper inspector should become the natural continuation of the active map color.

When opened from Statistics:

1. the active map metric appears first and is highlighted;
2. related measures follow in coherent groups;
3. period, source, coverage, provenance and missingness are visible;
4. empirical statistics stay distinct from project-specific Axis interpretation;
5. metrics use the same canonical/runtime registry and formatting as the map.

Existing Country Pulse functionality is preserved, but duplicate metric definitions and formatting should be migrated toward shared helpers/runtime definitions where practical.

## Toolbar and overlay discoverability

Do not add another large toolbar or revive the legacy Lens UI.

The existing registry-driven World Bar remains the ordinary overlay control.

Improve semantic clarity through small changes:

- active state should read like `Color: GDP / person` or equivalent;
- the Stats family remains available without hiding what it does visually;
- lower-left context remains passive, but its wording should explicitly connect overlay → meaning → current coverage;
- the country card supplies the clickable bridge into full statistics.

This makes the depth visible without turning the map into a dashboard wall.

## Performance cleanup

### 1. Single scalar rendering owner

`3d-compositor.js` remains the canonical country-fill owner.

The current population/area path can cause duplicate feature-state/fill work between the compositor and `3d-scalar-runtime-bridge.js`. Consolidate entity-aware population/area rendering into one compositor/shared-scalar path.

Keep public compatibility hooks from the scalar bridge where needed, but make them delegate/read rather than independently repainting the entire map on both layer and composition events.

### 2. Explicit render lifecycle events

Reduce reliance on many independent `MutationObserver`s for the same card/inspector DOM.

Introduce explicit lifecycle events, for example:

- `potato-atlas-country-card-rendered`;
- `potato-atlas-inspector-rendered`.

Country-card/inspector enrichers should use these events as the primary coordination mechanism. Mutation observers may remain only where required as compatibility fallbacks.

Goal: one country switch produces one coordinated render/enrichment cycle rather than multiple observers repeatedly discovering the same change.

### 3. True lazy specialist modules

The bootstrap currently labels deeper modules as dormant while eagerly loading several specialist investigation modules before `interactive`.

Preserve visible actions but move expensive specialist implementations off the initial map-interaction critical path where safe:

- Gateway/system intelligence;
- Chain explorer;
- Infrastructure context;
- Impact trace/actions.

Preferred behavior:

- lightweight action shells/hooks remain available;
- specialist module loads on first relevant action or bounded contextual need;
- first-country browsing and scalar coloring do not need to initialize every investigation subsystem.

Do not defer a module if doing so would cause a visible action to fail or produce race-prone behavior; use safe lazy delegates.

### 4. Avoid accidental map motion

UI actions, scalar changes, country switching, pins, statistics, compare preparation, and investigation-surface transitions do not call camera fit/fly automatically.

Camera movement occurs only from an explicit user navigation action designed to move the map.

## Diagnostics

Add lightweight internal diagnostics sufficient to prove that cleanup reduces duplicate work without inventing browser-performance claims.

Suggested `window.__potatoAtlasDiagnostics` counters/timings:

- bootstrap core-to-interactive duration;
- scalar compositions;
- scalar feature-state batches;
- country-card renders;
- inspector renders;
- card enhancement passes;
- inspector enhancement passes;
- specialist module lazy loads.

The diagnostics are developer-facing, not a new visible interface.

## Compatibility

Preserve existing public/runtime contracts where reasonable:

- existing selection events may remain but their semantics should clearly distinguish active browse state from pins;
- emit a new pin-state event if that avoids overloading old selection semantics;
- old `selected=` URLs should be interpreted safely;
- existing Compare, Path, Trace, Impact, Chain, Gateway and Infrastructure entry points continue to work;
- registered/noncanonical map entities remain supported;
- no canonical data is rewritten merely to support UI state.

## Epistemic boundaries

The cleanup must preserve the Atlas's existing distinctions:

- empirical/institutional facts;
- sourced observations;
- inferred/contextual associations;
- project-specific Axis interpretation.

A visual connection, shared chain, gateway, or contextual association must not be promoted into an explicit causal dependency.

No synthetic geopolitical/risk/resilience/completion score is introduced.

## Testing strategy

Implementation should be test-driven around observable semantics.

Required coverage includes:

1. ordinary clicks replace active country without growing pins;
2. repeated click keeps a country active rather than deselecting it;
3. explicit pin/unpin mutates only retained pin state;
4. comparison set is derived from pins, not browse history;
5. automatic relation roots follow active country in browse mode;
6. explicit investigation modes preserve their own intended multi-country context;
7. active scalar value shown in card equals the runtime value used for the map;
8. unknown observations remain unknown;
9. one scalar interaction has one rendering owner;
10. lifecycle events bound enhancement passes;
11. specialist lazy loaders preserve all visible actions;
12. no affected interaction triggers map zoom/focus;
13. legacy selection URLs remain recoverable;
14. full repository quality checks pass.

## Implementation boundaries

Likely touched modules include:

- `world-map/3d-country-selection.js`;
- `world-map/3d-country-card.js`;
- `world-map/3d-country-pulse.js`;
- `world-map/3d-world-bar.js`;
- `world-map/3d-compositor.js`;
- `world-map/3d-scalar-runtime-bridge.js`;
- `world-map/3d-bootstrap.js`;
- card/inspector enhancer modules currently coordinated through MutationObserver;
- relevant validators/tests.

New small modules are acceptable when they create a clear boundary, particularly for:

- active-view context;
- lazy specialist module loading;
- diagnostics.

Avoid unrelated refactors.

## Success criteria

A first-time user can click across the map naturally with no deselection ritual. Statistics visibly explain the current coloring. More detail is one obvious action away. Multi-country comparison is deliberate rather than accidental. Specialist investigation features remain available. The map performs less duplicate rendering/enrichment work, and the implementation has diagnostics/tests proving the new coordination semantics.
