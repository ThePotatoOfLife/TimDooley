# World Map Consolidation Design

**Status:** approved working design
**Date:** 2026-09-16
**Target:** `main`
**Base observed:** `36cde4fed5b42e4fbc6e4b6ece2e5294288ed0fa`
**Governing architecture:** `docs/superpowers/specs/2026-09-16-world-map-control-plane-design.md`
**Live roadmap:** `docs/WORLD-MAP-ROADMAP.md`

## Purpose

Consolidate the remaining World Map work into the current authoritative map without replaying stale branch history or reintroducing superseded runtime owners.

The consolidation must preserve the strongest behavior already on `main`, salvage unique behavior from divergent map branches, complete the control-plane migration, restore reliable validation, and leave one clearly governed World Map rather than a collection of partially overlapping feature branches.

## Core rule

**Salvage behavior, contracts, data and verified fixes — not stale branch history.**

An old branch being ahead of its merge-base does not mean its commits should be merged wholesale. Every candidate change is evaluated against current `main` and classified as:

1. already represented on `main`;
2. superseded by a newer implementation;
3. uniquely additive and worth porting;
4. incompatible with the current architecture and retained only as history.

No branch is merged merely to reduce the number of outstanding branches.

## Architectural authority

Current `main` is the integration base. New work must conform to the control-plane direction:

`canonical data → active view → geospatial / scale / render / interaction / inspector control plane → MapLibre presentation`

The consolidation must preserve single-owner rules for interaction, transient tooltip state, inspector/history state, style restoration, render ordering, panel lifecycle, scale thresholds and bounded data loading.

Legacy compatibility paths may remain temporarily only when a still-unmigrated consumer requires them and a regression test records that boundary.

## Integration order

### Phase 1 — establish the current baseline

Before porting old work:

- read the current World Map roadmap and governing control-plane spec;
- record the current `main` SHA;
- inventory open World Map PRs and map-related branches;
- compare candidate branches against `main` by changed behavior and files rather than branch age or commit count;
- identify the current canonical validators that gate map behavior.

The baseline is refreshed whenever `main` advances materially during consolidation.

### Phase 2 — reconstruct Safety Wave 2 on current `main`

PR #191 is treated as a source branch, not as a merge candidate in its current historical form.

Reconstruct its completed behavior onto a fresh branch from current `main`, in bounded slices. Candidate capabilities include:

- remaining central interaction-router migrations;
- spatial-overlay interaction arbitration;
- Places interaction ownership;
- typed Inspector Router and URL/history hydration;
- migration of Places and subdivisions away from raw panel snapshots;
- centralized style-generation restoration;
- runtime telemetry for source/layer counts and control-plane health;
- viewport-safe UI padding;
- deterministic place-label collision behavior;
- shared transient-tooltip ownership for remaining consumers;
- behavioral scenario coverage for drag, zoom, projection, wrapped worlds, overlap and inspector transitions.

Each capability is ported only if current `main` does not already contain an equal or stronger implementation.

The old `__potatoAtlasOverlayHandled` compatibility marker is not removed globally until all relevant interaction targets have migrated and the validator contract is updated in the same slice. A validator must never require a marker that the architecture intentionally retired.

### Phase 3 — restore a green canonical World Map validation chain

For each reconstruction slice:

- add or adapt the regression first;
- confirm the pre-fix state fails for the intended reason when practical;
- implement the smallest production change;
- run the focused validator;
- run `scripts/validate_world_map_source.py` or its current canonical replacement;
- inspect GitHub Actions on the exact branch head before claiming integration readiness.

A failure in the canonical World Map runtime gate blocks merge even if unrelated repository checks are green.

### Phase 4 — port the architecture auditor

PR #188 is also treated as a source branch rather than merged wholesale.

Port the useful auditor components onto the post-Safety-Wave-2 baseline:

- `scripts/audit_world_map.py`;
- `scripts/test_world_map_auditor.py`;
- `data/world-map-audit-contract.json`;
- CI generation/upload of a World Map audit artifact;
- a blocking gate only for errors whose ownership model remains valid against the reconstructed map.

The audit contract must be regenerated or reviewed against the current architecture rather than preserving stale suppressions or stale ownership expectations.

The auditor is evidence-producing infrastructure. It must report collisions, lifecycle duplication and ownership drift without creating a second runtime control plane.

### Phase 5 — branch archaeology and targeted salvage

Audit the remaining map-related branches in families:

- Places/search/data pipeline;
- subdivisions and geography fixes;
- physical-world layers;
- render stack and UI coordination;
- investigation/Trace/Path/functional-chain tooling;
- geographic enrichment and population layers;
- old unification/consolidation branches;
- special overlays and one-off repairs.

For each branch, write a short disposition record containing:

- branch name;
- merge base / divergence from current `main`;
- unique files or behaviors not represented on `main`;
- classification: represented / superseded / salvage / historical;
- action taken or reason for no action.

Older Places PR #136 and its relatives are archaeological sources. Current `main` already owns the newer `data/world-places` partitioned runtime, unified search, bounded cache/runtime rules and GeoNames builder. Only unique missing behavior may be ported; obsolete runtime owners and older interaction patterns must not return.

### Phase 6 — repair remaining active map gaps

After consolidation, continue directly against the live roadmap rather than branch archaeology. Priority order:

1. finish active interaction migrations and retire compatibility markers when proven safe;
2. audit remaining raw zoom thresholds and assign them to canonical scale bands where appropriate;
3. define physical versus schematic route-geometry semantics;
4. finish projection/dateline regressions;
5. add the visual-channel compatibility matrix and audit competing country fill/pattern/outline/height writers;
6. retire stale UI/runtime owners only after unique behavior is represented by a tested canonical owner;
7. improve keyboard, focus, reduced-motion, color-independent semantics and mobile occlusion;
8. expose concise active-view summaries;
9. publish useful World Map audit artifacts through the existing CI structure.

## Conflict policy

When an old branch and current `main` disagree:

1. prefer the newer canonical owner on `main`;
2. preserve verified user-visible behavior from the old branch when it is genuinely missing;
3. preserve newer bounded-runtime, stale-async, interaction-priority and lifecycle safeguards;
4. do not restore duplicate event listeners, duplicate popup/tooltip owners, duplicate capital renderers, duplicate styledata owners or duplicate country-style writers;
5. update tests to express the intended architecture instead of forcing production code to satisfy obsolete implementation markers.

## Data and performance constraints

Consolidation must preserve:

- one primary MapLibre map application;
- same-origin browser data runtime;
- bounded Places and subdivision loading/caching;
- no polling for runtime coordination;
- no second DOM `MutationObserver` introduced for map coordination;
- lazy specialist loading where already established;
- missing data remains missing;
- real geographic entities use real coordinates;
- symbolic/project geography remains explicitly typed;
- camera zoom remains presentation scale, not ontology.

## Water and physical-world constraint

The merged Physical Water zoom-handoff repair is part of the baseline and must not be reverted. Detail/overview scale transitions must have one effective owner so a native layer threshold cannot race a separate `zoomend` visibility handoff.

The same single-owner principle should be checked in land cover, hydrology, deserts/xeric and later physical layers.

## Validation strategy

Minimum evidence before a consolidation slice is merged:

- JavaScript syntax for modified runtime files;
- focused unit/static regression for the behavior being changed;
- the applicable subsystem validator;
- canonical `scripts/validate_world_map_source.py` pass, unless a newer explicitly canonical map validation entry point replaces it;
- repository quality workflow result inspected on the exact branch head;
- diff review confirming no unrelated Great Book, Bible, Story or other project content was pulled in accidentally.

Where browser-only visual behavior cannot be reproduced in the connector environment, the PR must state that limitation explicitly and use the strongest static/behavioral regression available rather than claiming visual proof.

## Commit and PR strategy

Use small reviewable commits grouped by architectural ownership, not by historical source branch.

Preferred sequence:

1. tests/contracts;
2. minimal runtime migration or repair;
3. validator integration;
4. roadmap/disposition documentation when the slice closes a known gap.

Avoid giant cherry-pick stacks and avoid merging historical PRs merely to inherit their commit graph.

Each integration PR should target `main`, contain only World Map work plus directly required validation/docs, and be merged only after exact-head verification.

## Branch retention

Do not delete old map branches during consolidation. They remain archaeological evidence until the salvage pass is complete. Branch deletion is a separate cleanup decision.

Open obsolete PRs may be closed as superseded only after their unique behavior has been classified and any necessary salvage is safely on `main`.

## Completion criteria

The consolidation is complete when:

- current `main` contains all unique, still-desired World Map behavior discovered in the audited branches;
- Safety Wave 2 capabilities are either integrated, superseded by stronger current implementations, or explicitly rejected with a recorded reason;
- the World Map architecture auditor is running against the modern architecture;
- canonical World Map validation is green on the integration head;
- no known duplicate interaction/tooltip/style/panel/render owner remains without an explicit compatibility reason;
- the live roadmap reflects actual merged state rather than branch-local progress;
- old map PRs have a documented disposition;
- future World Map work can proceed from `main` without depending on an unmerged historical branch.
