# Public Rooms Navigation Design

**Date:** 2026-09-16  
**Status:** approved direction; implementation pending  
**Scope:** public information architecture and route projection only

## Problem

The repository already contains substantial Culture/Subculture, Politics/Geopolitics, World Systems, legal, economic and chronological material, but the public entry architecture promotes only five primary Doors: Tim Dooley, Religion, Philosophy, Science and World. This keeps the homepage simple, but it makes mature specialist subjects feel absent unless a reader already knows their route.

The gap is not primarily missing data. It is a missing **middle floor** between the five Doors and the deep Explore/archive layer.

## Design principle

Preserve the existing five primary Doors exactly as they are. Add a visible **Rooms** layer beneath them.

The Rooms layer is a navigation/projection system, not a new knowledge owner. Existing canonical datasets and research files remain authoritative in their current locations. New human-facing pages only explain scope and route readers into those owners.

The public architecture becomes:

1. **Five Doors** — Tim Dooley, Religion, Philosophy, Science, World.
2. **Rooms** — cross-cutting human-readable subjects such as Culture, History, Politics, Law, Economy and World Systems.
3. **Deep archive** — Explore, records, contexts, sources and research owners.

## Public routes

### Existing routes retained

- Culture & Subculture → `/context/culture/`
- Politics & Geopolitics → `/politics/`
- World Systems → `/world-systems/`
- World Map → `/world-map/`
- North → `/north/`
- Sources & Evidence → `/context/source-authority/`
- Timeline → `/timeline/`
- Explore → `/explore/`

### New routes

- Rooms directory → `/rooms/`
- History & Time → `/history/`
- Law & Justice → `/law/`
- Economy & Finance → `/economy/`

These new pages are guides/indexes only. They do not become canonical owners.

## Homepage

The homepage continues to expose exactly five links in the primary `.sections` navigation. That contract must not change.

Immediately below the five Doors, add a visually separate **Explore the Rooms** corridor with at least:

- Culture & Society → `/context/culture/`
- History & Time → `/history/`
- Politics & Geopolitics → `/politics/`
- Law & Justice → `/law/`
- Economy & Finance → `/economy/`
- World Systems → `/world-systems/`
- Sources & Evidence → `/context/source-authority/`
- All Rooms → `/rooms/`

The existing Story, Timeline, Collection and Works “Ways in” corridor remains available and distinct from Rooms.

## Rooms directory

`/rooms/` is the human-readable middle-floor map of the project. It explains that Rooms cross-cut the five Doors and groups mature surfaces without exposing internal file layout.

It should include the principal public subject surfaces already present in the House, including Culture, History, Politics/Geopolitics, Law, Economy, World Systems, World Map, North, Sources/Evidence, Timeline, Works, Bible/Traditions, Science/formal models and other mature readers where appropriate.

It must link back to Home and to Explore for deeper browsing.

## History & Time

`/history/` broadens discoverability beyond the Tim-specific Timeline without pretending the repository already contains a complete universal history.

The page should route readers to:

- `/timeline/` for project chronology and dated material;
- existing chronology/history records and Explore paths;
- Politics/Geopolitics for political-historical material;
- Culture for cultural development and memory;
- Religion/Bible for textual and tradition history;
- Sources & Evidence for attestation and provenance.

The page must clearly distinguish historical occurrence, later interpretation and project mythology.

## Law & Justice

`/law/` is a public guide over the existing legal backend, law/regulation blueprint material and related governance/justice surfaces.

It should expose themes such as:

- constitutions and legislation;
- rights, duties and prohibitions;
- ministries, regulators, courts, prosecutors and ombudsmen;
- enforcement and jurisprudence;
- constitutional review, treaties and cross-border law;
- evidence, procedure, due process and accountability;
- Interpretive Justice as a related philosophical surface, not a substitute for positive law.

The page must not convert project claims, case reconstructions or political assertions into established legal findings. It routes to source/evidence layers and preserves provenance boundaries.

## Economy & Finance

`/economy/` is a focused human-facing index over the existing World Systems and economic-network material.

It should route readers through:

- public finance and debt;
- banking and capital markets;
- ownership and production;
- trade and supply/value chains;
- infrastructure and energy;
- labour and skills;
- strategic dependencies and resilience;
- North/European economic-system material;
- World Map when geography is the useful representation.

It does not introduce synthetic scores or fill missing values.

## World gateway

`/world/` remains the fifth primary Door. It should visibly expose the expanded subject corridors instead of only Map, Politics, North and Systems.

At minimum it should link to:

- World Map;
- Politics & Geopolitics;
- Law & Justice;
- Economy & Finance;
- World Systems;
- Culture & Society;
- History & Time;
- North;
- Sources & Evidence.

These are sibling lenses over shared canonical owners; World does not duplicate their data.

## House registry and projection contracts

Update `data/house/public-surfaces.json` and `knowledge/research/potato-house-master/public-route-topology.json` so `rooms`, `history`, `law` and `economy` are registered active public surfaces.

Suggested classifications:

- `rooms`: guide, parent `home`, cross-room directory, secondary visibility.
- `history`: guide, parent `home`, rooms `time-history`, `archive-sources`, `culture-information`, `world-systems`.
- `law`: guide, parent `world`, rooms `world-systems`, `archive-sources`, `culture-information`, `research-lab`.
- `economy`: guide, parent `world`, rooms `world-systems`, `archive-sources`, `research-lab`.

Keep `primary_gateway_ids` exactly `tim`, `religion`, `philosophy`, `science`, `world`.

Update `data/frontend-atlas-bridge.json` with an explicit rooms/subject projection map or equivalent secondary-surface entries while preserving the five-door contract. Canonical owners remain unchanged.

## Navigation contract

Add a dedicated validator for the Rooms layer rather than weakening the existing five-door validators.

The regression contract must assert:

1. Homepage primary `.sections` still contains exactly the five existing Door routes in order.
2. Homepage contains a separate Rooms corridor linking Culture, History, Politics, Law, Economy, World Systems and All Rooms.
3. `/rooms/`, `/history/`, `/law/` and `/economy/` exist and identify themselves correctly.
4. `/world/` links History, Culture, Politics, Law, Economy, World Systems, Map, North and Sources.
5. House registry and route topology contain the new surfaces and remain convergent.
6. New pages link to evidence/deep archive rather than embedding new canonical data copies.
7. Build output contains the new routes and public-navigation validation passes.

## Testing strategy

Use TDD:

1. Add a focused failing `scripts/validate_public_rooms.py` regression on the feature branch.
2. Run it before production changes and confirm it fails because the Rooms corridor/routes do not exist.
3. Implement the smallest navigation/pages/registry changes that satisfy the contract.
4. Run the focused validator plus House/public-projection validators.
5. Open a PR and require the full repository quality workflow to pass on the exact head before merge.

## Non-goals

This wave does **not**:

- change or expand the five primary Doors;
- rewrite Culture, Politics or World Systems content;
- create new canonical legal/economic/history datasets;
- merge stale feature branches;
- redesign Explore;
- claim completeness for law, economics or world history;
- collapse political interpretation, project mythology or legal allegations into observed fact.

## Success criterion

A visitor starting at `/` can discover Culture, History, Politics/Geopolitics, Law, Economy and World Systems without knowing hidden URLs, while the repository still has exactly five primary Doors and one authoritative backend for each fact.