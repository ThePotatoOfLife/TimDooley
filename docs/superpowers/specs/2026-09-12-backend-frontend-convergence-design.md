# Backend → Frontend Convergence Design

Status: approved architectural direction

## Goal

Remove drift between the repository backend/catalogue and the public site so the project has one authoritative navigation/projection model: five simple public doors on top, rich canonical/backend material underneath, and explicit routes connecting the two.

## Problem

The project currently has several partially-overlapping navigation contracts:

- `manifest.json` is the current relationship-first public archive manifest.
- `data/atlas-manifest.json` describes current internal architecture but still carries some old route assumptions.
- `data/frontend-atlas-bridge.json` still describes the retired single-`index.html` public Door and `index.html#node=...` routing.
- `data/backend-coverage-map.json` still names `index.html` / `root.js` as generic frontend consumers even though `root.js` is retired as public architecture.
- the five real public doors are `/tim-dooley/`, `/religion/`, `/philosophy/`, `/science/`, `/world-map/`.
- `/explore/` is the deep human archive explorer.
- build/discovery scripts create additional topic, record, context, question and A–Z pages.
- the repository index contains many more backend records than the human explorer can currently open from its explicit manifest/context allowlist.

The result is three different notions of coverage:

1. a record exists in the backend;
2. a record has a generated/crawlable page;
3. a human can naturally reach it through current navigation.

Those states must become explicit rather than accidentally diverging.

## Architectural rule

`data/frontend-atlas-bridge.json` becomes the single backend→frontend projection contract. It does not own content. It owns routing intent.

The hierarchy is:

`canonical/source records → manifest/core/context indexes → frontend projection contract → five public doors + deep/global routes → generated discovery/static pages`

The five primary doors remain exactly:

1. Tim Dooley
2. Religion
3. Philosophy
4. Science
5. World Map

No new top-level public door is introduced by this work.

## Projection model

Every major manifest branch must have one of:

- `primary_door`: one of the five public doors;
- `global_route`: a secondary system-wide route such as Timeline, Sources or Explore;
- `backend_only`: an explicit reason why direct public routing is inappropriate.

A branch may also declare `related_doors` for legitimate cross-domain access. Related doors never duplicate canonical ownership.

Recommended primary mapping:

- `tim` → Tim Dooley
- `son` → Religion
- `spirit` → Religion
- `transformation` → Philosophy
- `cosmology` → Religion
- `science` → Science
- `body` → Science
- `corporium` → Philosophy
- `traditions` → Religion
- `north` → World Map
- `world` → World Map
- `timeline` → global Timeline route
- `works` → Tim Dooley, with Explore as deep route
- `sources` → global Sources route

The homepage remains five-door and does not become a catalogue.

## Human navigation

Each of the five door pages gets one compact deeper-navigation surface fed by the projection contract. It should expose only high-value branch threads and deep routes relevant to that door. It must not become another giant directory.

The existing `/explore/` interface remains the full human archive explorer. It must accept valid canonical records from the canonical record registry, not only paths manually repeated in `manifest.json` or context clusters.

## Static/generated navigation

Generated topic and record pages must route back to the correct public parent rather than always defaulting to Tim-oriented links.

Branch→door mapping is shared with the projection contract. Generated context pages can route to `/explore/` when they span several branches.

## Discovery schema preservation

When Tim question records are imported into the discovery layer:

- `deep_sources` must be preserved as canonical/deep owner paths when `canonical_owners` is absent;
- `class` must be preserved as the archive/epistemic classification when `epistemic_class` is absent;
- scalar classification strings must be normalized to a list rather than iterated character-by-character.

Question pages should therefore retain the backend provenance needed to continue deeper into the archive.

## Retired architecture cleanup

Current code and documentation must not treat `root.js`, `index.html#node=...`, or the old single-index/public-Door model as current architecture.

Historical/retired references may remain only where explicitly labeled as retired provenance. If `root.js` has no live consumer after convergence, remove it.

`learn/` and reader-guide behavior must not point users into a dead or obsolete Start Here route. Any surviving guide action must route to a current public surface.

## Validators

Add a convergence validator that fails when:

- the five primary doors differ from the approved set;
- a major manifest branch has no projection status;
- current bridge/coverage metadata names `root.js` as a live consumer;
- current routing still uses `index.html#node=` as the public record route;
- `atlas-manifest` interactive routes disagree with `/explore/`;
- Tim question discovery drops `deep_sources` or `class`;
- generated records cannot determine an appropriate parent route;
- the five door pages lack a projection mount/section;
- `/explore/` cannot resolve a registry-backed canonical record that is not manually listed in one branch.

The validator should be part of the main quality workflow before the public build.

## Cleanup policy

This work removes presentation/routing drift, not substantive research. Do not delete canonical, evidentiary, dated or specialist records merely because they are not directly linked from a primary door.

A file may be removed when it is a retired presentation implementation with no current consumer and its architectural purpose is already represented by current code/contracts.

## Success criteria

A newcomer should be able to:

1. start at the homepage and see exactly five major doors;
2. enter any major domain and see a compact set of deeper relevant threads;
3. reach the full archive without learning internal file paths;
4. open canonical backend records through `/explore/` even when they are not manually duplicated into one branch;
5. follow generated topic/record/question pages back to the correct human parent;
6. encounter no current metadata or validators that describe the retired single-index/root.js architecture as live.

CI must prove those contracts on the exact branch head before the convergence pass is considered complete.
