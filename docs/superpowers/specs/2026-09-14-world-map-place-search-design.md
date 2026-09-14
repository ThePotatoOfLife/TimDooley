# World Map Place Search Design

## Goal
Turn the existing `Find country…` control into one quiet `Find place…` entry point for countries, supported subdivisions, and the populated places the map already knows, without adding another toolbar, renderer, dataset, or live geocoder.

## Architecture
- `world-map/3d-country-selection.js` remains the canonical owner of country selection. The place-search controller calls its existing `window.__potatoAtlasSelection.activate(...)` API rather than rewriting the large core app.
- `world-map/3d-subdivisions.js` remains the canonical owner of subdivision data and selection. It exposes a compact `search(query)` method; no other module parses subdivision GeoJSON.
- `world-map/3d-hover.js` remains the canonical owner of the existing Natural Earth populated-place display layer backed by `data/world-capitals.geo.json`. The file contains 150+ pinned places, including primary capitals and selected non-primary cities.
- `world-map/3d-place-search.js` owns cross-class search orchestration and datalist enrichment. It reuses the existing header input and takes Enter in capture phase only after the country datalist is ready, preserving the original core handler as an early-startup fallback. It reads the existing populated-place snapshot rather than creating a second city dataset.
- A searched city receives a small transient `atlas-place-selection` marker/label so selected non-primary cities remain visible even though the existing broad city display intentionally emphasizes primary capitals.
- `world-map/3d-panel-lifecycle.js` loads the tiny place-search controller after core paint. Subdivision/place data itself remains dormant until search, zoom, or a deep link needs it.
- The canonical `scripts/validate_world_map_source.py` gate imports the focused place-search validator, so no extra workflow is needed.

## Search behavior
1. Exact ISO3/name country matches retain current behavior.
2. Exact subdivision ID/code/name matches route through `window.__potatoAtlasSubdivisions.select(...)`.
3. Exact populated-place name or stable place ID matches focus the existing Natural Earth point, retain its parent-country context, and persist `?place=CITY-…`.
4. Ambiguous free text preserves exact country interpretation first; for example plain `Georgia` remains the country while `GA`, `US-GA`, or `Georgia (US-GA)` identifies the U.S. state.
5. Prefix/substring matching is a fallback after exact matches.
6. Country, subdivision, and city detail are mutually clean: selecting a later country/state removes an older city marker/deep link, while city focus may retain its parent country as context.

## UI
- Reuse the existing header search input and datalist.
- Upgrade the visible copy at runtime to `Find place…` / `Find a country, state, or city`.
- No permanent new button, menu, search box, or duplicate city panel.
- `/` continues to focus the same input.

## Data and semantics
- Countries keep their canonical country data path.
- Subdivisions keep the existing official Census snapshot path.
- Populated-place search reuses `data/world-capitals.geo.json`, whose features identify their source as pinned Natural Earth 1:110m populated places. No second city source is introduced in this slice.
- Place points are geographic/navigation context. They do not become canonical demographic observations and remain separate from analytical layer-registry state.

## Performance and failure handling
- Search orchestration is tiny and loads after core paint.
- Subdivision data is loaded only when subdivision search/interaction needs it or the existing camera trigger fires.
- Populated-place search reads the already-small same-origin city snapshot and does not call a live geocoder.
- The existing capital renderer remains unchanged; search only adds a one-feature selection source when a city is chosen.
- If optional subdivision/place data fails, country selection remains available through the canonical country selection API and original early-startup search fallback.

## Validation
- The focused validator syntax-checks place-search/subdivision JavaScript, verifies the existing populated-place snapshot remains a valid 150+ feature GeoJSON with both primary and selected non-primary places, checks country/subdivision/place ownership and deep-link contracts, and forbids live geocoder dependencies.
- `validate_world_map_source.py` runs that focused validator inside the existing repository quality workflow; no new workflow is created.
