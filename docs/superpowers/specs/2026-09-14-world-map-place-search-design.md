# World Map Place Search Design

## Goal
Turn the existing `Find country…` control into one quiet `Find place…` entry point for countries, supported subdivisions, and a later compact global city layer without adding another toolbar or live geocoder.

## Architecture
- `world-map/3d-app.js` remains the canonical owner of country lookup/selection and delegates non-country search to a small place-search module.
- `world-map/3d-subdivisions.js` remains the canonical owner of subdivision data and selection. It exposes a compact `search(query)` method; no other module parses subdivision GeoJSON.
- `world-map/3d-place-search.js` owns cross-class search orchestration and datalist enrichment. First slice: countries + U.S. states/D.C. Second slice: pinned Natural Earth v5.1.2 populated places.
- `world-map/3d-panel-lifecycle.js` lazy-loads place search after core paint. City data, when added, remains same-origin and lazy-loaded.

## Search behavior
1. Exact ISO3/name country matches retain current behavior.
2. Exact subdivision ID/code/name matches route through `window.__potatoAtlasSubdivisions.select(...)`.
3. Later city matches route through the place layer and preserve their own `?place=` URL state.
4. Ambiguous free text prefers exact matches over prefix/substring matches and preserves the existing country fallback.

## UI
- Reuse the existing header search input and datalist.
- Change visible copy to `Find place…` / `Find a country, state, or city`.
- No permanent new button, menu, or panel.
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
- If optional place data fails, country search remains functional.

## Validation
- Source validator checks the single-search-control contract, delegation hook, subdivision search API, lazy-loading markers, URL ownership, and absence of live geocoder dependencies.
- Existing repository quality workflow runs JavaScript syntax checks and the place-search validator; no new workflow is created.
