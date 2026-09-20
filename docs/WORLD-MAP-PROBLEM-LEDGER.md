# World Map Problem Ledger

**Updated:** 2026-09-21  
**Authority:** active defect / architecture queue for the World Map.  
**Rule:** fix the highest-leverage shared owner first; do not patch the same symptom independently in multiple modules.

## Severity model

- **P0** — map unusable / corrupt state / serious data or interaction failure.
- **P1** — visible feature disappears, wrong layer wins, state/lifecycle race, broken navigation, repeated requests.
- **P2** — architectural duplication likely to create future regressions, accessibility failure, mobile occlusion, inconsistent semantics.
- **P3** — polish, wording, cleanup, compatibility retirement after parity is proven.

## Active queue

### WM-001 · Shared subdivision retention can be released by the wrong overlay — P1
**Status:** fixed on main (2026-09-20).  
**Cause:** U.S. subdivision retention used one Set instead of owner-aware leases.  
**Resolution:** owner-aware retain/release; ADL and project overlays cannot evict each other.

### WM-002 · ADL feature-state can disappear after subdivision source refresh — P1
**Status:** fixed on main (2026-09-20).  
**Cause:** shared GeoJSON source replacement invalidated rendered feature-state timing.  
**Resolution:** source-change lifecycle + ADL repaint; load de-duplication; regression coverage.

### WM-003 · Physical Water owns a private 3.4 detail threshold — P2
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** `data/world-map-scale-contract.json` owns `physical-water-detail`; Water consumes the shared threshold and keeps only cartographic interpolation locally.  
**Guard:** scale-classification validation requires the shared capability marker and rejects return of the old private behavioral gate.

### WM-004 · Hydrology owns private 4 / 5.2 / 6.7 / 8.2 thresholds — P2
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** the Scale contract owns regional/medium/fine/detailed thresholds and Hydrology consumes them through one `riverRegime()` owner shared by provider filtering and request-key identity.  
**Guard:** scale-classification validation checks every shared hydrology capability marker.

### WM-005 · Remaining raw zoom-magic inventory — P2
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** behavioral gates live in `data/world-map-scale-contract.json`; `data/world-map-scale-classification.json` classifies remaining values as capability, cartographic interpolation, camera intent or fixture. The core HUD no longer owns private 3/5/7 bands and consumes `scale.bandForZoom()`.  
**Guard:** `scripts/validate_world_map_scale_classification.py` verifies the shared capability consumers and prevents the old HUD classifier from returning.  
**Rule retained:** visual interpolation and camera framing remain local unless they begin governing data/loading/interaction behavior.

### WM-006 · Country visual-channel ownership not fully closed — P1/P2
**Status:** fixed / governed on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** Compositor owns country fill/extrusion color, Country Selection owns outlines, Physical World owns country fill opacity, and the core extrusion controller owns height/visibility. Progressive UI is retired from normal boot. Legacy Lens URLs/API calls now translate into Layer Registry state only; the Lens compatibility adapter owns no country paint, feature-state, legend or control surface.  
**Guard:** visual-channel validation rejects canonical country paint writes from legacy UI/Lens compatibility modules and enforces one owner per channel. Lens ownership regression rejects return of the retired legend/control renderer.  
**Rule retained:** any newly promoted renderer that wants a canonical country channel must declare ownership instead of writing around the compositor.

### WM-007 · Duplicate style/lifecycle writers remain — P2
**Status:** fixed for direct Style Lifecycle ownership on main (2026-09-20).  
**Evidence:** only `3d-style-lifecycle.js` owns the MapLibre `styledata` listener; Render Stack and physical restorers register as participants.  
**Remaining visual-channel conflicts:** tracked separately under WM-006/WM-008 rather than reopening style lifecycle ownership.

### WM-008 · Legacy UI ownership remains split — P2
**Status:** fixed for normal boot on main (2026-09-20).  
**Resolution:** Progressive UI (`3d-ui.js`) and Selection UI (`3d-selection-ui.js`) are rejected from the live bootstrap; World Bar, Country Selection, Compositor, UI Layout and Panel Lifecycle own their former responsibilities. Legacy `3d-lenses.js` remains as source compatibility/reference code but is no longer registered as a live dormant bootstrap module.  
**Guard:** core/browse/inspector validators reject reintroduction of Progressive/Selection UI into normal boot; visual-channel validation prevents legacy UI paint ownership from returning.

### WM-009 · Interaction compatibility marker still exists — P3
**Status:** intentional governed compatibility on main (2026-09-20).  
**Owner:** Interaction Router + core fallback boundary.  
**Resolution:** normal routed interaction claims handled pointer events inside the shared Router. The legacy `__potatoAtlasOverlayHandled` marker remains only for explicitly supported degraded/direct fallback handlers so the core country fallback cannot double-handle the same pointer event when the Router is unavailable.  
**Guard:** `test_world_map_interaction_compatibility.mjs` fixes the allowed marker counts/modules and requires each specialist claim to remain inside its degraded fallback region.  
**Retirement condition:** remove the marker only if degraded standalone interaction is removed entirely or gains a replacement canonical ownership signal; do not delete it merely for cleanup.

### WM-010 · Mobile occlusion / keyboard / focus-return audit incomplete — P2
**Status:** fixed / governed for current shared surfaces on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** shared Accessibility owner synchronizes menu ARIA state, Escape closes the active menu and returns focus, opening a map menu closes any already-open sibling without stealing focus, and Inspector Router captures/restores focus across typed inspector transitions. On narrow screens, either World Bar or top-menu expansion suppresses background status, pinned context and inspector surfaces so they cannot compete for pointer/focus space.  
**Guard:** keyboard regression covers Escape/focus and single-open-menu behavior; UI-layout validation requires both mobile menu families in the occlusion policy.

### WM-011 · Reduced-motion behavior incomplete — P2
**Status:** fixed for known user-visible camera consumers on main (2026-09-20).  
**Resolution:** shared Motion policy owns major country/place/subdivision/ADL/Axis transitions plus capital focus and Spatial Overlay fit; reduced-motion CSS and regression coverage exist.  
**Guard:** validator rejects raw `map.easeTo(` / `map.fitBounds(` calls in governed camera consumers outside the Motion owner.

### WM-012 · Color-only semantics remain possible — P2
**Status:** fixed for canonical analytical country layers (2026-09-20).  
**Resolution:** scalar layers use color plus exact numeric/value text; set layers use pattern plus explicit membership text; layer controls expose type/state through accessible labels and the visual-channel validator enforces these redundancies.  
**Remaining:** apply the same review standard to future Evidence/Physical renderers before promotion.

### WM-013 · Active-view accessibility summary incomplete — P2
**Status:** fixed / superseded by current presentation architecture on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** the mixed hover/selection Context Status surface is intentionally retired from Panel Lifecycle. Global analytical state now lives in World Bar's `atlasWorldContext`, a polite atomic status region covering active analytical, Physical, Geography, Evidence, projection, relation and time context; selected-country detail belongs to Country Card/Presentation instead of the global status surface. Identical context markup is not rewritten, reducing repeated live-region announcements.  
**Guard:** context-status regression requires the old mixed surface to stay unloaded and verifies the accessible World Bar successor plus duplicate-announcement suppression.

### WM-014 · Route-geometry behavioral coverage incomplete — P2
**Status:** fixed for current route families / governed on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** relationship chords and symbolic interior routes use the shared wrap-safe longitude kernel; regressions cover dateline crossings in eastern and western world copies; route features carry explicit `geometry_meaning`; stored spatial-overlay lines remain stored/reference geometry rather than being silently converted into schematic chords. Shared Interaction Router tests cover click/hover priority.  
**Future rule:** any surveyed physical-route renderer must preserve source geometry and add its own behavioral test rather than reusing schematic chord semantics.

### WM-015 · Legacy interaction fallback scenarios under-tested — P2
**Status:** fixed / governed on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** Country Selection, Spatial Overlays, Places and Subdivisions resolve Router ownership dynamically and promote from bounded fallbacks. Places, Subdivisions, ADL, Mud/Below, Spatial Overlay UI, Axis and Axis Depth resolve Inspector availability dynamically while retaining direct panel fallbacks. Places, Subdivisions and Spatial Overlays restore sources/layers/interaction ownership through the shared Style Lifecycle after style generations.  
**Guard:** dedicated degraded-Inspector regression rejects module-boot Inspector caching and verifies fallback + typed promotion; interaction and Style Lifecycle validators cover Router and style-generation recovery.

### WM-016 · State/subdivision national-context readability — P2
**Status:** fixed / governed for current subdivision coverage on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** canonical USA partition is validator-checked at 50 states + DC including Alaska, Hawaii and DC; generic labels defer on narrow screens and receive an additional modest delay in globe projection where surface compression increases crowding. The selected subdivision retains its own overlap-tolerant label at the normal render threshold, so the user's chosen state/region remains readable while ambient labels thin out. Projection and resize changes resynchronize the policy.  
**Guard:** readability validator requires narrow/globe density controls, selected-label lifecycle, AK/HI/DC coverage and bounded subdivision runtime behavior.

### WM-017 · Evidence-layer source refresh contract should be generic — P2
**Status:** fixed on main (2026-09-20).  
**Cause:** ADL owned direct subdivision custom-event and MapLibre sourcedata listeners.  
**Resolution:** the subdivision runtime now owns one source-refresh observer contract; ADL registers through it, and future evidence fills can reuse the same lifecycle hook without owning geography refresh listeners.

### WM-018 · Provider-failure UX is inconsistent across Physical layers — P2
**Status:** fixed; see combined WM-018/019 reliability resolution below.

### WM-019 · Physical layer request budgeting lacks one shared network budget — P2
**Status:** fixed for explicit provider fetches; see combined WM-018/019 reliability resolution below.

### WM-020 · Architecture audit should emit actionable queue IDs — P3
**Status:** fixed on main (2026-09-20).  
**Resolution:** recurring architecture-audit finding codes now project to owning `WM-xxx` queue IDs plus remediation owner in both JSON reports and console output.  
**Guard:** `scripts/test_world_map_auditor.py` verifies queue projection for ownership collisions.


### WM-021 · URL state ownership is fragmented — P1
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** `3d-url-state.js` is the sole direct `history.replaceState` owner. Domain/specialist state and the formerly coupled selection/Inspector family now use shared parameter claims and atomic patches; Places, Subdivisions and map-reset fallbacks no longer bypass ownership.  
**Guard:** `validate_world_map_url_state.py` scans every live `world-map/*.js` file and rejects direct history writers outside the canonical owner; URL regression covers shared-owner overlapping claims.  
**Compatibility:** legacy `selected=` remains read-compatible but is cleared by the working-selection owner on writes.

### WM-022 · Specialist inspectors bypass typed Inspector Router — P1
**Status:** fixed for known main-panel specialist surfaces on main (2026-09-20).  
**Resolution:** Places, Subdivisions, ADL dataset/state/incident evidence, Mud/Below, Spatial Overlay inspection, Axis and Axis Depth all project through typed Inspector nodes. Raw panel HTML remains an implementation detail inside node render callbacks rather than owning semantic history.  
**Accessibility:** Inspector open/back already focuses rendered headings and restores the invoking control.  
**Guard:** Inspector URL and router validators cover the migrated node types and hierarchy.

### WM-023 · Degraded interaction fallback can become permanent by boot order — P1
**Status:** fixed on main (2026-09-20).  
**Cause:** Spatial Overlays, Country Selection, Places and Subdivisions could capture Router availability too early and leave direct listeners installed forever.  
**Resolution:** all four resolve Router ownership dynamically, listen for `potato-atlas-interaction-ready`, remove degraded listeners with `map.off`, and promote to canonical Router registrations.  
**Guard:** interaction validator/regression requires the ready listener and teardown markers.

### WM-024 · Canonical subdivision evidence integration lacks generic search/badge projection — P2
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** subdivision runtime exposes provider-agnostic `evidenceSummaries(id)`; inspector cards and unified subdivision search consume the generic summaries. Search displays active evidence count context without naming or depending on ADL.  
**Guard:** `validate_world_map_subdivision_evidence_projection.py` requires the generic provider/search bridge and explicitly rejects ADL hard-coding in unified search.

### WM-026 · Aggregate map views do not disclose projection loss — P2
**Status:** fixed / governed on branch `world-map-projection-loss-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** the shared Atlas projection contract required `information_loss` and `source_path_back`, but the live World Map Active View did not project those semantics into runtime state or reader UI.  
**Resolution:** `data/world-map-view-projections.json` declares preservation, loss and reconstructability for country scalar, set-membership, active-country relation and pinned-country comparison views. `3d-active-view.js` composes the active contracts and `3d-world-bar.js` exposes a compact “View omits” + reconstructability disclosure.  
**Guard:** `scripts/validate_world_map_view_projections.py` enforces the contract, runtime markers and reader disclosure through the World Map quality group.  
**Rule retained:** a choropleth, set, relation filter or comparison is a lossy View, never a substitute for the canonical country/relationship/source owner.

### WM-027 · Ukraine first-order region partition — P2
**Status:** implemented on branch `world-map-ukraine-regions-2026-09-20`, pending exact-head CI confirmation.  
**Resolution:** Ukraine now enters through the canonical generic subdivision registry as a bounded geometry-first partition with 26 source-represented first-order features, stable `UA-*` IDs, local + English names, generic search records, and no invented population values.  
**Epistemic boundary:** the partition is administrative reference geometry only. It is not a current occupation, control, sovereignty, or front-line layer. The source transform combines Sevastopol into the Crimea geometry; that transformation is preserved as explicit source metadata rather than adopted as a project claim.  
**Guard:** the generic subdivision validator checks feature count, IDs, provenance, unknown-population semantics, the Crimea/Sevastopol representation note, runtime byte budgets and multi-country loader behavior.  
**Next:** add Russia through the same contract once a compact reproducible ADM1 geometry source is pinned; model war/control snapshots separately as dated conflict-context overlays.

### WM-028 · ADM1 ingestion remains manual and country-specific — P2
**Status:** fixed / governed on branch `world-map-adm1-importer-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** the renderer and partition registry were generic, but adding another first-order country partition still required manual canonicalization of IDs, provenance, unknown-population semantics, byte accounting and search records.  
**Resolution:** `scripts/import_world_adm1.py` now normalizes a reviewed local GeoJSON into the canonical geometry-first partition schema plus a review-only descriptor sidecar. It never downloads sources or silently mutates the live registry. Operators must explicitly map name/code/type fields and supply source label/ref/vintage, representation note, expected count and optional viewport.  
**Guards:** importer fails closed on duplicate IDs, missing names/codes, non-polygon geometry, feature-count drift and hard byte-budget overflow; it SHA-256 fingerprints the exact source bytes, preserves unknown population as `unknown-not-zero`, and emits geometry-free search records. `test_world_map_adm1_importer.py` runs in the World Map quality group.  
**Rule retained:** acquisition, normalization and registry promotion remain separate review steps; external geometry does not become authoritative merely because it can be normalized.

### WM-029 · Conflict-context geography lacks a dated snapshot contract — P2
**Status:** fixed / governed on branch `world-map-conflict-snapshot-contract-rebased-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** the Spatial Overlay system reserved a conflict family, but it did not yet define the minimum time/source/meaning metadata needed to show historical or delayed control/front-line context without contaminating administrative geography.  
**Resolution:** `data/world-map-conflict-snapshot-contract.json` defines allowed snapshot meanings, required observation/publication fields, source attribution, confidence, explicit not-live semantics, Time-dimension ownership and administrative-independence rules. The live `conflict.context` manifest row points to this contract and remains planned/dormant with no geometry.  
**Guard:** `scripts/validate_world_map_conflict_snapshots.py` requires the conflict family to remain dormant until reviewed geometry exists, binds snapshots to the canonical Time owner, rejects activation without source/not-live/administrative-independence guarantees, and preserves the explicit no-live-tactical-tracking boundary.  
**Next:** ingest reviewed delayed/historical source snapshots as separate geometry owners; compare exact snapshots through Time without interpolating invented front lines.

### WM-030 · Geometry-first subdivision inspectors hide uncertainty/provenance — P2
**Status:** fixed / governed on branch `world-map-subdivision-inspector-richness-rebased-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** generic subdivision cards displayed bare dashes for missing population/area/density and only a one-line boundary source, so newer geometry-first partitions could look incomplete without explaining what was intentionally unknown or source-specific.  
**Resolution:** subdivision inspection now distinguishes known vs unknown population/area/density, explicitly states that unknown population is not zero, shows local names, source reference/vintage, boundary provenance and representation notes, and keeps city/place hydration plus evidence context intact.  
**Guard:** the canonical subdivision validator requires the richer inspector helpers and explicit unknown/provenance/representation language.  
**Rule retained:** missing statistics are never inferred from geometry, and source-specific boundary transforms remain visible to the reader.

### WM-031 · Russia regional partition needs a neutral base-geography contract — P2
**Status:** implemented on branch `world-map-russia-regions-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** available Russia regional sources may bundle disputed Ukrainian territories and unrelated political/demographic attributes into the same GeoJSON, which would silently turn a base administrative partition into a geopolitical claim surface.  
**Resolution:** the canonical Russia partition contains 83 source-derived federal-subject geometries only. Crimea, Sevastopol, Donetsk, Luhansk, Zaporizhzhia and Kherson are excluded from Russia base geography and remain eligible only for separately typed disputed/conflict overlays. All source election/demographic attributes are stripped; only geometry, names, region type and provenance remain. UN General Assembly resolutions A/RES/68/262 and A/RES/ES-11/4 are recorded as the territorial-integrity references for the exclusion rule.  
**Guard:** subdivision validation enforces 83 unique `RU-*` features, exact federal-subject type counts, the six-feature exclusion set, source scope, source SHA, no imported population/political fields, byte budget and generic loader compatibility.  
**Rule retained:** base geography represents the ordinary administrative partition; disputed territory and dated control belong to independent epistemically typed overlays.

### WM-032 · Country-card Regions doorway can load invisible subdivisions — P1
**Status:** fixed / governed on branch `world-map-region-doorway-focus-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** the country card retained and refreshed a subdivision partition but did not hand camera intent to the subdivision owner. From world/macro zoom, a user could click “regions” and see no obvious change because the partition remained below its shared render/interact threshold.  
**Resolution:** the subdivision runtime now owns `focusPartition()`, derives canonical descriptor bounds, unwraps antimeridian-crossing extents, computes the MapLibre camera from those bounds, floors the destination at the shared subdivision render threshold, and executes through the reduced-motion-aware Motion owner. The country card calls this after acquiring its partition lease.  
**Guard:** a behavioral regression covers Russia’s 19°E→170°W descriptor, proves unwrapping to 190°E, and requires a visible-scale floor; UI-shell validation requires the country-card handoff marker.  
**Rule retained:** feature entry points may request focus, but camera semantics and subdivision scale thresholds stay with shared owners.

### WM-033 · Selectable subdivisions have no transient hover identity — P2
**Status:** fixed / governed on branch `world-map-subdivision-hover-preview-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** subdivision interaction registered hover priority but only implemented click behavior, so dense regional browsing lacked fast identity feedback before opening the Inspector.  
**Resolution:** subdivisions now reuse the shared Tooltip Service and Interaction Router for region-name/local-name/type/country previews, with semantic hover-key reuse and leave invalidation. The degraded direct-listener fallback mirrors the same tooltip behavior without constructing a private popup.  
**Guard:** specialist-tooltip regression now requires shared subdivision tooltip ownership, routed hover, leave invalidation, degraded fallback parity and zero private Popup construction.

### WM-034 · Regions doorway active state is one-way / optimistic — P2
**Status:** fixed / governed on branch `world-map-regions-toggle-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** once a country-card partition was retained, clicking the active Regions control only refocused it; the same control could not release the lease. Local retained state was also cleared before release completed.  
**Resolution:** the Regions action now toggles the country-card partition lease on/off, updates `aria-pressed` and the “regions · shown” state from the actual retained partition, emits a bounded regions-change event, and only clears local lease state after the release path returns without error.  
**Guard:** UI-shell validation requires the toggle branch, shared action-state helper and region-state event.

### WM-037 · World Map top bar is functionally sound but visually over-weighted — P2
**Status:** fixed / governed on branch `world-map-topbar-density-audit-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** the unified header correctly consolidated many old surfaces, but every persistent control retained near-equal visual weight. N/W/E/S behaved like four full toolbar actions, icon-only projection/reset controls used ordinary button width, and relation-context filters duplicated the Analyze relationship surface as a separate top-level Relations menu.  
**Resolution:** relation-context filters now live inside Analyze; N/W/E/S render as one compact four-button axis group with full accessible names; projection/reset use compact icon widths; registry buttons lose a small amount of height/padding; Search/Compare/Inspect/Home spacing is tightened; and the fixed result slot is reduced while remaining width-stable.  
**Justification rule:** a persistent top-level control must be either a frequent direct action, a distinct map dimension, or global navigation/reset. Deeper or overlapping capability belongs inside the relevant menu.  
**Guard:** UI-shell validation rejects a standalone Relations registry family, requires compact axis/icon markers, compact fixed result width and compact first-paint header geometry.  
**Rule retained:** this is density reduction, not capability removal or a new toolbar design.

### WM-035 · Subdivision local names are searchable but invisible on-map — P2
**Status:** fixed / governed on branch `world-map-local-region-labels-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** Ukraine/Russia/Denmark partitions retain local names and unified search can match them, but ambient subdivision labels always projected only code/English name.  
**Resolution:** generic subdivision labels now use the shared scale vocabulary: code at early regional scale, canonical name at subnational scale, and canonical + local name at the shared local scale when the names differ. Narrow-screen and globe density delays apply to the local-name threshold too.  
**Guard:** subdivision readability validation requires local-scale ownership, local-name presence/inequality guards and the bilingual label expression.

### WM-036 · Region → Places handoff is panel-only — P2
**Status:** fixed / governed on branch `world-map-region-places-handoff-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** subdivision inspectors could list mapped places and open one place at a time, but had no explicit path to reveal the region's place context on the map.  
**Resolution:** the canonical Places runtime now exposes `showSubdivision()`, which reuses the existing bounded country place partition, turns the shared Places layers on, preserves the selected region/camera, and emits one bounded subdivision-show event. The region inspector exposes a “Show mapped places on map” action and updates it to a pressed/shown state after success.  
**Guard:** Places ownership validation and the bounded-runtime regression require the shared handoff, bounded country load and canonical visibility owner.  
**Rule retained:** regions do not create their own city source or renderer; place geometry remains owned by Places.

### WM-038 · Regional countries can exist without place depth — P2
**Status:** fixed / governed on branch `world-map-ukr-rus-places-current-2026-09-20`, pending exact-head CI confirmation.  
**Cause:** Ukraine and Russia had first-order subdivision partitions but no same-origin Places country partitions, so region inspectors could not reveal mapped cities/towns and unified place search had no detailed country geometry behind those regions.  
**Resolution:** the exact pinned GeoNames cities15000 seed already used by the project now supplies 256 Ukraine places and 1,089 Russia places. Both stay below the canonical 2 MiB country-partition budget. The global-major layer is extended with their national capitals/large cities, compact search ranks are recomputed across all place-enabled countries, and the existing historical-seed provenance/refresh limitation remains explicit.  
**Guard:** Places validation now requires every promoted subdivision country to have a place partition and requires each partition's national capital to survive into `global-major.geo.json`. Existing byte/search/provenance checks remain active.  
**Rule retained:** regional depth and place depth share the canonical Places owner and same-origin bounded partitions; no second city renderer or unbounded global dataset is introduced.


### WM-039 · Visual-channel compatibility contract is incomplete — P2
**Status:** fixed / governed on branch `world-map-visual-matrix-20260920`, pending exact-head CI confirmation.  
**Cause:** the visual-channel contract declared canonical channels and several important pair policies, but it did not provide a complete machine-checkable matrix. That left future combinations vulnerable to ad-hoc assumptions even though country-surface ownership was already centralized.  
**Resolution:** the contract now contains a complete symmetric 9×9 compatibility matrix covering fill, pattern, outline, line, point, height, card, timeline and scene. Matrix values distinguish same-channel ownership, direct composition, conditional composition and deliberately separate presentation spaces. The current renderer’s only conditional pair, pattern + height, remains bound to the information-preserving `prefer-pattern-flatten-height` fallback.  
**Guard:** `scripts/validate_world_map_visual_channels.py` now requires complete rows, symmetry, valid matrix values, self diagonals and the canonical pattern + height fallback.  
**Rule retained:** the matrix describes whether channels may coexist; it does not grant paint ownership. Canonical owners remain declared separately in `country_surface_owners`.


### WM-040 · Retired UI compatibility modules remain as misleading live source — P2
**Status:** fixed / governed on branch `world-map-retire-legacy-ui-20260920`, pending exact-head CI confirmation.  
**Cause:** `3d-ui.js` and `3d-selection-ui.js` had already been removed from normal bootstrap ownership, but their large implementations remained in the runtime tree. That made obsolete panel/menu/selection behavior look reusable and left a path for accidental reintroduction.  
**Resolution:** both compatibility modules are deleted. Their surviving responsibilities are already owned by World Bar, Panel Lifecycle, Country Selection, Layer Registry, Country Card, Accessibility/UI Layout and the typed Inspector stack.  
**Guard:** UI-shell validation now requires both retired files to stay absent and rejects either filename if it reappears in bootstrap. Visual-channel validation also rejects restoration of `3d-ui.js`.  
**Rule retained:** retire only compatibility code whose unique behavior has a tested canonical owner; this change does not remove core country selection, inspector, layer or panel capability.


### WM-041 · Dead Lens compatibility adapter remains in runtime source — P3
**Status:** fixed / governed on branch `world-map-retire-legacy-lenses-current-20260920`, pending exact-head CI confirmation.  
**Cause:** the old Lens module had already been removed from bootstrap and reduced to a compatibility translator, but the source file remained beside canonical runtime modules. Because it was never loaded, its promised legacy URL translation was not an actual supported runtime path and the file primarily preserved architectural ambiguity.  
**Resolution:** `3d-lenses.js` is deleted. Analytical state is owned by Layer Registry, Compositor and their URL/state owners; no paint, legend or control behavior is removed from the normal map.  
**Guard:** runtime, URL-state, layout and visual-channel validators now require the Lens adapter to remain absent.  
**Rule retained:** legacy query compatibility is only claimed when an actual loaded canonical owner implements it; dead adapters are not documentation.


### WM-044 · Published quality audit is stale against current main — P2
**Status:** fixed on branch `world-map-audit-backlog-20260921`; pending exact-head CI.  
**Evidence:** the 2026-09-20 audit still reports decentralized URL ownership, Inspector bypass, raw Motion bypass, fragmented provider budgeting and live Progressive/Selection/Lens compatibility even though those areas were subsequently migrated or retired.  
**Risk:** engineers can spend time “fixing” already-resolved defects while real current gaps remain under-described.  
**Resolution:** published `docs/WORLD-MAP-QUALITY-AUDIT-2026-09-21.md` with base-main SHA and current ownership findings; the 2026-09-20 audit is explicitly marked superseded while remaining available as historical diagnosis.  
**Completion guard:** audit, ledger and roadmap must agree on current ownership and no high-severity current audit finding may describe code already removed from main.

### WM-045 · Dormant Fields / Networks compatibility modules remain in source — P2
**Status:** fixed on branch `world-map-retire-fields-networks-20260921`, pending exact-head CI.  
**Evidence:** `3d-fields.js` and `3d-networks.js` still contain their own control injection, URL/time/tooltip behavior and are referenced by validators/contracts, but current bootstrap contains no direct load/import path for either module.  
**Risk:** dead source keeps duplicate ownership concepts alive and validators may accidentally preserve obsolete architecture.  
**Resolution:** parity review confirmed current bootstrap does not load either module; current Axis state is owned by `axis.*` registry entries and institutional membership by `group.*` registry entries plus relation/context systems. Ten of the twelve institutional choices exposed by the old Networks control already exist as canonical registry groups; Nordic/APEC remain source data rather than pretending dormant UI is live functionality. Symbolic Operators were migrated off `axisFieldView` / `empiricalNetworkView` before retirement. Both compatibility modules are deleted and validators/tests now guard their absence.  
**Completion guard:** neither module may return to runtime, manifests or tests without explicit canonical promotion; underlying source datasets remain available for future reviewed registry expansion.

### WM-046 · Regional browsing is still limited to five promoted countries — P2
**Status:** verified functionality gap (2026-09-21).  
**Evidence:** `data/world-subdivisions/` currently contains USA, CAN, DNK, UKR and RUS partitions only.  
**Risk:** the generic region engine looks global but most countries have no selectable first-order geography or region→Places path.  
**TODO:** prioritize additional ADM1 countries using source quality, byte budget, reader value and place-depth readiness; promote only through the generic importer/validator.  
**Completion:** expansion wave adds reviewed partitions without country-specific renderer code and every promoted country gets bounded Places/search coverage.

### WM-047 · Places data freshness and country depth are seed-limited — P2
**Status:** verified data/functionality gap (2026-09-21).  
**Evidence:** `data/world-places/index.json` identifies a GeoNames `cities15000` mirror seed with unknown exact upstream refresh date; detailed partitions exist only for USA, DNK, CAN, UKR and RUS, with 95 global-major features.  
**Risk:** technically polished place search can appear more current/global than its provenance supports.  
**TODO:** add a reviewed canonical GeoNames build pipeline with explicit upstream date/retrieval date/build date, then expand detailed country partitions under existing byte/cache budgets.  
**Completion:** exact freshness is known or explicitly unavailable per build, and country/place coverage expansion is reproducible from pinned input.

### WM-048 · Conflict/history functionality is schema-only — P2
**Status:** verified functionality gap (2026-09-21).  
**Evidence:** `world-map-conflict-snapshot-contract.json` is `active-schema-dormant-data` and explicitly says no reviewed conflict snapshot geometry is committed yet.  
**Risk:** the map advertises a conflict-context architecture without an actual dated historical/delayed snapshot to exercise Time, Inspector, source and render contracts together.  
**TODO:** ingest one reviewed historical/delayed snapshot set with source bundle, observation period, geometry meaning, confidence and not-live boundary; validate exact-snapshot comparison without interpolating front lines.  
**Completion:** at least one conflict dataset can be inspected and time-selected end-to-end while administrative geography remains untouched.

### WM-049 · Region/globe/mobile behavior lacks broad end-to-end scenario coverage — P2
**Status:** in progress on branch `world-map-combined-region-scenario-20260921`.  
**Evidence:** current regressions cover antimeridian, overlap, tooltip and inspector transitions, but there is no single behavioral suite covering globe + narrow viewport + dense regional labels + detached territories + region→Places transitions.  
**Risk:** individually-correct systems can still occlude, over-label or lose selection when combined in real browsing.  
**Progress:** added a combined runtime-contract regression for narrow viewport + globe projection + subdivision selection + region→Places handoff. Subdivision status now exposes the effective label policy so the test can verify that ambient labels are delayed in narrow/globe mode while the selected-region label remains available from the shared render threshold. The test also guards the Places handoff against clearing regional selection and requires bounded partition reuse.  
**Remaining:** add a true browser-level visual scenario for dense labels, detached/non-contiguous geography and focus/occlusion behavior before closing the item.

### WM-050 · Architecture auditor findings are not first-class ledger work items — P2
**Status:** verified observability gap (2026-09-21).  
**Evidence:** the architecture auditor inventories ownership hazards, but recurring finding types do not consistently resolve to ledger ID, canonical owner and severity in CI output.  
**Risk:** diagnosis and execution queues can drift; the same issue may be rediscovered without a stable remediation identity.  
**TODO:** add a finding-code mapping contract (finding code → ledger ID → owner → severity/status) and include it in quality-group summaries.  
**Completion:** every promoted auditor finding either maps to an existing ledger item or is explicitly marked informational/ignored with rationale.

### WM-051 · Geometry-first regional statistics remain uneven — P3
**Status:** verified functionality-depth gap (2026-09-21).  
**Evidence:** newer partitions intentionally preserve unknown population/area/density instead of fabricating values; this is correct but leaves regional comparison depth uneven.  
**Risk:** users can select a region but receive mostly identity/provenance while other regions expose richer statistics.  
**TODO:** define an optional sourced ADM1 statistics enrichment contract independent from boundary geometry, including period/source/missingness and join confidence.  
**Completion:** at least one geometry-first partition can accept sourced statistics without mutating or pretending they came from the boundary source.

### WM-052 · Shared UI token convergence stops at layering — P3
**Status:** verified architecture/polish gap (2026-09-21).  
**Evidence:** semantic z-index bands are being centralized, but many map surfaces still repeat local background, border, radius, padding and shadow literals.  
**Risk:** visual drift returns as new controls and inspectors are added, making density/mobile tuning harder.  
**TODO:** introduce a small semantic surface token set for panel/menu/context/control states and migrate common surfaces gradually; avoid a giant generic design system.  
**Completion:** common surfaces consume named tokens, while special semantic colors/encodings remain owned by their data/render domains.

### WM-053 · Data freshness semantics are inconsistent across map families — P2
**Status:** verified functionality/reader-trust gap (2026-09-21).  
**Evidence:** ADL has an explicit historical-snapshot freshness model and Places records unknown upstream refresh, while other empirical/physical/relationship layers expose date/status in different forms or not at the same UI level.  
**Risk:** “current”, “latest available”, “historical”, “delayed”, and “unknown vintage” can look equivalent to readers.  
**TODO:** define one compact freshness/status vocabulary and projection into Current Map / Inspector context, without forcing unlike datasets into the same update cadence.  
**Completion:** every reader-facing empirical dataset declares observation/reference period plus freshness status or explicit unknown-vintage state.



### WM-054 · Garden symbolic operator targets retired Fields/Networks controls — P1
**Status:** fixed on branch `world-map-retire-fields-networks-20260921`, pending exact-head CI.  
**Cause:** `3d-symbolic-operators.js` still read `axisFieldView` / `empiricalNetworkView` and the Garden action called `setSelect('axisFieldView','all')`, even though the Fields/Networks compatibility modules are not loaded by current bootstrap.  
**Failure:** Garden could change Axis depth but fail to activate the intended project-field view; operator state reported field/network as `n/a`.  
**Resolution:** symbolic operators now read active `axis.*` and `group.*` state from the canonical Layer Registry; Garden activates the four current Axis lenses through the registry API.  
**Guard:** retirement regressions require symbolic operators to contain no references to retired control IDs.


### WM-025 · ADL state evidence is structurally integrated but snapshot freshness is historical — P2
**Status:** integration and refresh pipeline fixed; external source acquisition remains open.  
**Current:** 335-record historical `Extremist murders` seed, 2005–2023; the Evidence manifest declares `data_status: historical-snapshot`, active controls compute snapshot age from the latest record (2023-10-11), and state/dataset inspectors repeat the freshness boundary. ADL's official page was re-verified on 2026-09-20 as monthly-updated with downloadable raw data.  
**Refresh pipeline:** `scripts/import_adl_heat.py` accepts only an explicitly confirmed official export, hashes the input, validates exact/retrieval-date sanity, duplicate source IDs and coordinate bounds, preserves unsupported/missing-geometry diagnostics, and writes reproducible metadata/GeoJSON/state summaries. Its end-to-end regression uses a temporary output directory and fails closed on malformed/future/duplicate inputs.  
**Guard:** ADL validation runs the importer regression, requires source verification metadata, `snapshotFreshness()`, persistent `data-adl-freshness` UI and the explicit boundary that the committed seed is not current monthly ADL coverage.  
**Remaining:** obtain a reviewed current official H.E.A.T. raw-data export, import it through the guarded pipeline, review the generated diff, then replace the historical seed. Keep ADL/FBI methodologies separate.

### WM-018/019 · Physical provider status + request reliability — P1/P2
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** Terrain, Water, Hydrology, Land Cover and Aridity report a common `potato-atlas-physical-layer-status` schema into the Physical mixer, which records provider, phase, attempts, retryability, last success and last error. `3d-request-budget.js` owns explicit provider-request concurrency, in-flight de-duplication, abort handling, short-lived cache and telemetry; Hydrology is the first explicit-fetch consumer.  
**Scope boundary:** MapLibre-managed raster/vector/tile source scheduling remains under MapLibre and is not wrapped in a second scheduler.  
**Guard:** `validate_world_map_physical_provider_reliability.py` + `test_world_map_request_budget.mjs` run in the World Map quality group.

## Work order

1. **State/control ownership wave** — WM-021/022/023.
2. **Scale ownership wave** — WM-003/004/005.
3. **Render/visual ownership wave** — WM-006/008/014.
4. **Accessibility/mobile/motion wave** — WM-010/011/012/013/016.
5. **Physical provider reliability wave** — WM-018/019.
6. **Evidence/subdivision projection wave** — WM-024/025.
7. **Compatibility + audit retirement** — WM-009/015/020 and remaining legacy surfaces.

## Completion rule

A problem is not complete because code changed. Close it only when:
- canonical ownership is explicit;
- regression/validator coverage exists;
- exact-head CI proves the relevant subsystem;
- any compatibility behavior is documented;
- the live roadmap and this ledger agree.
