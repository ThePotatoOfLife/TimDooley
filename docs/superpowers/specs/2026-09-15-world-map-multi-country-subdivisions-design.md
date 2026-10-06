# World Map Multi-Country Subdivisions Design

## Goal

Turn the existing U.S.-only subdivision renderer into a country-partition runtime that can load real first-order administrative geography for multiple countries without adding a second map, second inspector, or eager global payload. Denmark is the second production partition and proves the generic contract.

## Canonical architecture

The existing `world-map/3d-subdivisions.js` remains the single subdivision renderer. `data/world-subdivisions/index.json` becomes the routing registry: each country partition declares its same-origin GeoJSON path, stable id prefix, viewport bounds, parent name, feature count, provenance/status metadata, and lightweight search records where available. The runtime derives the relevant partition from this registry instead of hard-coding `US-` and `USA_BOUNDS`.

Subdivision detail stays lazy. The module may load a partition when a deep-linked subdivision belongs to it or when the viewport overlaps that partition at regional zoom. Loaded partitions continue to use the existing canonical MapLibre source/layer pattern, canonical right inspector, render/click precedence markers, and `subdivision=` URL state.

## Denmark baseline

The Denmark partition is the existing five-region GeoJSON produced from the official DAWA/Dataforsyningen region endpoint and already proven on the earlier map feature branch. It is copied byte-for-byte by Git blob identity rather than regenerated from an unverifiable snapshot. The data explicitly keeps population unknown rather than treating missing population as zero.

The five stable ids are `DK-1084`, `DK-1082`, `DK-1081`, `DK-1085`, and `DK-1083`. The index records Denmark as parent `DNK`, source Danish Agency for Climate Data (DAWA/Dataforsyningen), and provides a Denmark viewport envelope.

## Runtime contract

`3d-subdivisions.js` must:

- load descriptors from the partition index once;
- resolve a subdivision id to a partition using each descriptor's `id_prefix`;
- determine viewport relevance from descriptor `viewport_bounds`;
- load all relevant available partitions at regional scale, not only USA;
- preserve one-shot deep-link camera intent so `fitBounds -> moveend` cannot loop;
- keep `select(id)` generic for every registered prefix;
- keep selection inspection in `#panel` and preserve panel restoration;
- preserve overlay click precedence and current source/layer naming;
- fail one unavailable partition without breaking the others.

## Validation

The canonical subdivision validator must validate both USA and Denmark. USA remains 51 first-wave units with positive 2025 population. Denmark must contain exactly five unique `DK-*` region features, explicit geometry provenance, and must not invent numeric population. A Node regression test must prove a Denmark deep link loads the DNK partition, fits once, and does not refit on the resulting `moveend`.

Repository quality remains the merge gate. No production branch reaches `main` until the exact PR head passes the full repository workflow.

## Out of scope for this slice

This slice does not add every European subdivision, municipality-level detail, or a new search UI. Those become later country/data waves on top of this generic partition contract.