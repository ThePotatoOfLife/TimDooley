# World Map Place Search Design

## Goal
Turn the existing `Find country…` control into one quiet `Find place…` entry point for countries, supported subdivisions, and a later compact global city layer without adding another toolbar or live geocoder.

## Architecture
- `world-map/3d-country-selection.js` remains the canonical owner of country selection. The place-search controller calls its existing `window.__potatoAtlasSelection.activate(...)` API rather than rewriting the large core app.
- `world-map/3d-subdivisions.js` remains the canonical owner of subdivision data and selection. It exposes a compact `search(query)` method; no other module parses subdivision GeoJSON.
- `world-map/3d-place-search.js` owns cross-class search orchestration and datalist enrichment. It reuses the existing header input and takes Enter in capture phase only after the country datalist is ready, preserving the original core handler as an early-startup fallback.
- `world-map/3d-panel-lifecycle.js` loads the tiny place-search controller after core paint. Subdivision/city data itself remains dormant until search, zoom, or a deep link needs it.
- The canonical `scripts/validate_world_map_source.py` gate imports the focused place-search validator, so no extra workflow is needed.

## Search behavior
1. Exact ISO3/name country matches retain current behavior.
2. Exact subdivision ID/code/name matches route through `window.__potatoAtlasSubdivisions.select(...)`.
3. Later city matches route through the place layer and preserve their own `?place=` URL state.
4. Ambiguous free text preserves exact country interpretation first; for example plain `Georgia` remains the country while `GA`, `US-GA`, or `Georgia (US-GA)` identifies the U.S. state.
5. Prefix/substring matching is a fallback after exact matches.

## UI
- Reuse the existing header search input and datalist.
- Upgrade the visible copy at runtime to `Find place…` / `Find a country, state, or city`.
- No permanent new button, menu, search box, or panel.
- `/` continues to focus the same input.

## Data and semantics
- Countries keep their canonical country data path.
- Subdivisions keep the existing official Census snapshot path.
- Cities use a pinned Natural Earth v5.1.2 snapshot filtered to admin-0 capitals plus important populated places (`scalerank <= 4`). Natural Earth population values are contextual map estimates, not canonical demographic observations.
- Geographic context remains separate from analytical layer-registry state.

## Performance and failure handling
- Search orchestration is tiny and loads after core paint.
- Subdivision data is loaded only when subdivision search needs it or the existing camera trigger fires.
- City data is not fetched on initial map bootstrap; it loads only when place search or relevant zoom needs it.
- If optional subdivision/place data fails, country selection remains available through the canonical country selection API and original early-startup search fallback.

## Validation
- The focused validator checks the single-search-controller contract, subdivision search API, country selection ownership, lifecycle loading marker, and absence of live geocoder dependencies.
- `validate_world_map_source.py` runs that focused validator inside the existing repository quality workflow; no new workflow is created.
