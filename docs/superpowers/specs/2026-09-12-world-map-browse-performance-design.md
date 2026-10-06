# World Map Browse-First Interaction, Statistics Cohesion, and Performance Cleanup

Date: 2026-09-12
Status: Approved for implementation

## Purpose

Make the World Relational Atlas feel like a map a person can simply explore while preserving its investigation depth.

The default mental model is:

- **Map color = the question being asked.**
- **Clicked country = the thing currently being inspected.**
- **Pins = countries deliberately retained for comparison or multi-country investigation.**
- **Specialist tools = explicit investigations, not side effects of ordinary browsing.**

No feature is removed. Routine interface actions do not automatically zoom or refocus the map.

## Selected architecture

Use **Browse + Pins with shared active-view context**.

An ordinary country/entity click replaces `activeCode`, updates the compact card and any open inspector, updates the selected country's exact overlay value, and recenters bounded automatic relationships around that active country. It does not add/remove a retained selection and does not move the camera.

Retained multi-country state becomes explicit `pinnedCodes`. Pinning is deliberate through a Pin/Compare action or Shift-click shortcut. Comparison uses pins rather than browse history. Legacy `selected=` URLs remain safely recoverable.

Automatic connections follow the active country by default. Explicit Path, Compare, Trace, Impact, Chain, Gateway, and Infrastructure investigations may retain their own intended context without turning normal map clicks into persistent multi-selection.

## Active View Context

Add one presentation adapter derived from the existing registry/compositor/runtime. It exposes the current scalar or set query, active country, exact formatted observation, unit, period, source/provenance pointer, coverage/missingness, set membership/query match, and relation filter mode.

Consumers are the compact country card, deeper Country Pulse/inspector, lower-left context, legend, comparison views, and statistics browser. The compositor/runtime remain authoritative; the view context is not a competing data store.

## Country card and statistics

The upper-left card remains the default inspection surface. When an overlay or group query is active, a visually distinct **Map view** block immediately explains what the map color means for the active country, including exact value, period and concise source/coverage where available. Missing data remains Unknown/No comparable observation, never zero-filled.

Core metrics remain beneath it. Add clear Statistics and Pin/Unpin actions while preserving Connections/Trace, Path and Impact. Statistics opens the existing deeper inspector focused on statistics rather than adding another floating panel.

The deeper inspector highlights the active map metric first, then related measures with period/source/coverage/provenance. Empirical statistics remain distinct from project Axis interpretation. Metric definitions and formatting should increasingly share canonical/runtime helpers rather than duplicate logic.

## Toolbar and discoverability

Keep the registry-driven World Bar. Do not add another large toolbar or revive the legacy Lens UI. Make active state read explicitly like `Color: GDP / person`, keep lower-left context passive but clearer, and use the country card as the clickable bridge into full statistics.

## Performance cleanup

1. **Single scalar rendering owner:** `3d-compositor.js` remains canonical country-fill owner. Remove duplicate population/area repaint work from `3d-scalar-runtime-bridge.js` while preserving compatibility hooks.
2. **Explicit render lifecycle:** introduce `potato-atlas-country-card-rendered` and `potato-atlas-inspector-rendered`; migrate relevant enhancers away from independent MutationObserver passes where safe, leaving observers only as compatibility fallbacks.
3. **True lazy specialist modules:** move Gateway, Chain, Infrastructure and Impact implementations off the initial critical path where safe while preserving visible actions through lazy delegates.
4. **No accidental camera motion:** country browsing, pins, scalar changes, statistics, compare preparation and investigation-surface transitions do not fit/fly automatically.
5. **Diagnostics:** expose developer-facing counters/timings on `window.__potatoAtlasDiagnostics` for bootstrap-to-interactive, scalar compositions/state batches, card/inspector renders and enhancement passes, and specialist lazy loads.

## Compatibility and epistemic boundaries

Preserve existing public/runtime contracts where reasonable. Existing selection events may remain but must distinguish active browse state from pins. Add a pin-state event rather than overloading old semantics if needed. Registered/noncanonical entities remain supported and canonical data is not rewritten for UI state.

Preserve the separation between empirical/institutional facts, sourced observations, inferred/contextual associations, and project-specific Axis interpretation. A visual connection or shared chain/gateway is not promoted into causal dependency. No synthetic geopolitical/risk/resilience/completion score is introduced.

## Required behavior/tests

1. ordinary clicks replace active country without growing pins;
2. repeated click keeps a country active rather than deselecting it;
3. explicit pin/unpin mutates only retained pin state;
4. comparison set is derived from pins, not browse history;
5. automatic relation roots follow active country in browse mode;
6. explicit investigation modes preserve intended context;
7. active scalar value in the card equals the runtime value used by the map;
8. unknown observations remain unknown;
9. scalar rendering has one owner;
10. lifecycle events bound enhancement passes;
11. lazy loaders preserve visible specialist actions;
12. affected interactions do not trigger map zoom/focus;
13. legacy selection URLs remain recoverable;
14. repository quality checks pass.

## Likely implementation surface

- `world-map/3d-country-selection.js`
- `world-map/3d-country-card.js`
- `world-map/3d-country-pulse.js`
- `world-map/3d-world-bar.js`
- `world-map/3d-compositor.js`
- `world-map/3d-scalar-runtime-bridge.js`
- `world-map/3d-bootstrap.js`
- card/inspector enhancer modules currently coordinated through MutationObserver
- relevant validators/tests

New small focused modules are acceptable for active-view context, lazy loading, or diagnostics. Avoid unrelated refactors.
