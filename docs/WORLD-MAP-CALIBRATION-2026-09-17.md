# World Map calibration — 2026-09-17

This note records the September 17 calibration pass over the World Relational Atlas. The governing roadmap remains `docs/WORLD-MAP-ROADMAP.md`.

## Resulting model

The map should be read as several coordinated information planes, not as one undifferentiated stack of overlays:

1. **Base geography** — country polygons, boundaries, places, subdivisions and projection.
2. **Physical world** — terrain, water, hydrology, land cover and aridity context. These are provider-backed, optional and lazy.
3. **Analytical country layers** — one scalar fill at a time plus stackable categorical/set patterns, with explicit epistemic type and source ownership.
4. **Relationships** — typed lines/flows/dependencies that connect entities without pretending graph distance is geographic distance.
5. **Spatial overlays** — explicitly typed historical, textual, project-symbolic, disputed or physical geographies that may overlap without being merged.
6. **Time** — current, as-of and compare-date state; undated records remain unknown in historical views.
7. **Selection and investigation** — active/hover/pinned state, Country Card, Country Pulse, Evidence, Trace, Path and specialist inspectors.
8. **Coverage/provenance** — source, period, coverage, availability and missing-data semantics carried with the view rather than hidden in implementation details.

The visual-channel contract remains: fill = one scalar/ordered field; pattern = categorical/set overlap; outline = interaction/selection; line = relationships/flows/routes; point = geocoded entities/assets; height = optional scalar extrusion; card = contextual non-spatial data; timeline = dated state; scene = specialist non-geographic representation.

## Integrated control surfaces

The persistent user-controlled map planes now have one public controller each:

- **Analytical** — country scalar/set registry + compositor. One scalar fill at a time; set memberships remain stackable patterns.
- **Physical** — provider-backed terrain, water, hydrology, land cover and aridity through the Physical runtime.
- **Geography** — typed spatial overlays through the spatial-overlay registry. Historical/textual/project/disputed/current geometries may overlap but never merge epistemically.
- **Evidence** — specialist source-classified datasets through the Evidence controller. ADL H.E.A.T. is the first current adapter; FBI hate-crime data remains a separate planned adapter rather than being folded into one score.

Time, scale and projection remain dimensions rather than layer families. Places, subdivisions, infrastructure, Gateways, Chains, Impact and Axis-depth are contextual/application layers: they appear because the user enters a scale or investigation, not because every possible renderer belongs in one giant checkbox menu.

The machine-readable contract is `data/world-map-layer-surfaces.json`.

## Terrain calibration

Terrain remains explicitly opt-in and network-backed. The 3D terrain surface and hillshade now share a single Mapterhorn raster-DEM source rather than maintaining duplicate DEM sources for the same TileJSON endpoint. The source is capped at zoom 12, terrain and hillshade exaggeration are intentionally modest, and the ordinary raster basemap is only partially strengthened while terrain is active.

This keeps relief useful as physical context without making the optional terrain layer dominate the browser's tile workload or the country/data layers visually.

## Country and population calibration

Population is not a free-floating label or unsourced property. It resolves through the same canonical country/entity identity used by the map. The demography build contract requires complete positive, sourced population observations with explicit reference periods for all 195 canonical sovereign-country records. Missing values elsewhere remain missing rather than becoming zero.

Country inspection is intentionally progressive:

- the compact Country Card gives ordinary comparable context;
- the active map metric is surfaced near the top;
- Country Pulse expands population, economy and additional statistics with period/unit/source metadata;
- Evidence and deeper specialist modules remain available without forcing them into the first screenful.

## Layer disclosure calibration

A layer name alone is not enough. Every current analytical registry entry is now expected to declare at least:

- stable id and family;
- kind;
- visual channel;
- epistemic type;
- source owner;
- spatiality.

The World Bar now exposes semantic layer metadata directly in analytical menus and in the Current Map View summary. In ordinary use, a user should be able to distinguish an observed scalar fill from a project-interpretive pattern without opening source code. Source ownership is also surfaced for active scalar views, while coverage and period remain visible when the active-view runtime provides them.

## Physical-world disclosure

Physical-layer metadata remains separate from the analytical registry because physical providers have different runtime concerns: load policy, provider, zoom range, opacity, request strategy and provider availability. The physical manifest is authoritative for those declarations and must stay synchronized with runtime behavior.

## UI hierarchy

The UI should answer questions in this order:

- **What am I looking at?** Active layer/view semantics.
- **Where and at what scale?** Geography, projection and scale-dependent detail.
- **What value or membership does this country have?** Country Card / active map view.
- **How complete and current is it?** Coverage, period and source.
- **How is it connected?** Relations, Trace and Path.
- **What is the evidence?** Evidence inspector and source ownership.
- **What changes through time?** Time controls and dated relationship state.

Dense information belongs behind progressive disclosure; it should not all be painted simultaneously.

## Remaining calibration work

The architecture is strong enough to extend, but the following remain active work rather than completed claims:

- finish the visual-channel compatibility matrix and audit every remaining fill/pattern/outline/height writer;
- migrate remaining legacy tooltip paths to the shared tooltip service;
- audit remaining raw zoom thresholds against the shared scale runtime;
- finish shared UI tokens/z-index/surface consolidation and mobile/accessibility checks;
- continue converting specialist data families into sourced, typed registry/runtime entries instead of ad-hoc overlays;
- expand behavioral scenarios for route geometry, accessibility and remaining compatibility paths.

These items should be implemented by strengthening canonical owners and validators, not by adding parallel map systems.
