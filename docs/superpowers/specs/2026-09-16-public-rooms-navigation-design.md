# Public Rooms Navigation Design

**Date:** 2026-09-16  
**Status:** implemented on PR #209; exact-head verification required before merge  
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

- Culture, Cult & Society → `/context/culture/`
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

It includes the principal public subject surfaces already present in the House, including Culture/Cult/high-control analysis, History, Politics/Geopolitics, Law, Economy, World Systems, World Map, North, Sources/Evidence, Timeline, Works, Bible/Traditions, Science/formal models and the deep archive.

It links back to Home and to Explore for deeper browsing.

## History & Time

`/history/` broadens discoverability beyond the Tim-specific Timeline without pretending the repository already contains a complete universal history.

The page routes readers to:

- `/timeline/` for project chronology and dated material;
- existing chronology/history records and Explore paths;
- Politics/Geopolitics for political-historical material;
- Culture for cultural development and memory;
- Religion/Bible for textual and tradition history;
- Sources & Evidence for attestation and provenance.

The page clearly distinguishes historical occurrence, later interpretation and project mythology.

## Law & Justice

`/law/` is a public guide over the existing legal backend, law/regulation blueprint material and related governance/justice surfaces.

It exposes themes such as:

- constitutions and legislation;
- rights, duties and prohibitions;
- ministries, regulators, courts, prosecutors and ombudsmen;
- enforcement and jurisprudence;
- constitutional review, treaties and cross-border law;
- evidence, procedure, due process and accountability;
- Interpretive Justice as a related philosophical surface, not a substitute for positive law.

The page does not convert project claims, case reconstructions or political assertions into established legal findings. It routes to source/evidence layers and preserves provenance boundaries.

The implementation also exposes the existing generic law/regulation blueprint and specialist legal research index directly from the Law guide while `data/frontend-atlas-bridge.json` projects `knowledge/legal/` to `/law/` without moving or duplicating canonical ownership.

## Economy & Finance

`/economy/` is a focused human-facing index over the existing World Systems and economic-network material.

It routes readers through:

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

The implementation directly exposes existing specialist economic sources, including the inflation/rates/bond ledger and North obligation graph, while `data/frontend-atlas-bridge.json` projects `knowledge/economics/` to `/economy/` without creating a second source of truth.

## World gateway

`/world/` remains the fifth primary Door. It visibly exposes the expanded subject corridors instead of only Map, Politics, North and Systems.

At minimum it links to:

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

`data/house/public-surfaces.json` and `knowledge/research/potato-house-master/public-route-topology.json` register `rooms`, `history`, `law` and `economy` as active public surfaces.

Classifications:

- `rooms`: guide, parent `home`, cross-room directory, secondary visibility.
- `history`: guide, parent `home`, rooms `time-history`, `archive-sources`, `culture-information`, `world-systems`.
- `law`: guide, parent `world`, rooms `world-systems`, `archive-sources`, `culture-information`, `research-lab`.
- `economy`: guide, parent `world`, rooms `world-systems`, `archive-sources`, `research-lab`.

`primary_gateway_ids` remains exactly `tim`, `religion`, `philosophy`, `science`, `world`.

`data/frontend-atlas-bridge.json` contains the explicit `public_rooms` projection and backend-family routes for legal and economic material. Canonical owners remain unchanged.

## Navigation contract

A dedicated `scripts/validate_public_rooms.py` validator protects the Rooms layer without weakening the existing five-door validators.

The regression contract asserts:

1. Homepage primary `.sections` still contains exactly the five existing Door routes in order.
2. Homepage contains a separate Rooms corridor linking Culture/Cult, History, Politics, Law, Economy, World Systems and All Rooms.
3. `/rooms/`, `/history/`, `/law/` and `/economy/` exist and identify themselves correctly.
4. `/world/` links History, Culture, Politics, Law, Economy, World Systems, Map, North and Sources.
5. House registry and route topology contain the new surfaces and remain convergent.
6. Law and Economy expose existing specialist sources while remaining non-owning guide surfaces.
7. The frontend bridge maps legal/economic backend families into their public Rooms without moving canonical ownership.
8. Build output contains the new routes and public-navigation validation passes.

## Testing strategy

The implementation used TDD:

1. A focused `scripts/validate_public_rooms.py` regression was introduced before production navigation changes and observed failing on the missing Rooms/routes.
2. The initial implementation made that contract green.
3. Code review identified semantic-access gaps for specialist Law/Economy material and missing Cult wording.
4. The validator was strengthened first and observed failing specifically on those gaps.
5. The public pages and projection contract were then tightened until the strengthened contract passed.
6. Full repository quality checks are required on the exact final branch head before merge.

## Non-goals

This wave does **not**:

- change or expand the five primary Doors;
- rewrite Culture, Politics or World Systems content;
- create new canonical legal/economic/history datasets;
- merge stale feature branches;
- redesign Explore;
- claim completeness for law, economics or world history;
- collapse political interpretation, project mythology or legal allegations into observed fact.

## Implementation status

Implemented on PR #209:

- separate Home Rooms corridor while preserving the five primary Doors;
- `/rooms/`, `/history/`, `/law/` and `/economy/` public guide routes;
- expanded World and World Systems routing;
- House registry and route-topology entries;
- explicit frontend `public_rooms`, legal and economics projections;
- direct specialist legal/economic source access;
- explicit Culture/Cult/high-control discoverability;
- focused Rooms regression validation wired into the repository quality workflow.

The feature remains a presentation/routing layer. Canonical facts continue to live with their existing owners.

## Success criterion

A visitor starting at `/` can discover Culture/Cult, History, Politics/Geopolitics, Law, Economy and World Systems without knowing hidden URLs, while the repository still has exactly five primary Doors and one authoritative backend for each fact.
