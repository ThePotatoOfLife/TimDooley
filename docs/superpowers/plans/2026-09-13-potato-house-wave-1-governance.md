# Potato House Wave 1 Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the first machine-readable Potato House governance layer: ten Domain Rooms, stable public-surface identities, a route-topology bridge, consistent World-as-fifth-Hub routing, and exact-artifact validation without redesigning the homepage.

**Architecture:** Add two small governance registries under `data/house/` and validate them with a focused standard-library Python contract validator. Keep `manifest.json`, `data/frontend-atlas-bridge.json`, `data/repository-spine.json`, `data/canonical-source-map.json`, and Explore live during migration; add explicit pointers/status so they stop competing silently. Remove the current deploy-time World→World Map compatibility mutation so source, build checks, and uploaded artifact all agree on the same public route.

**Tech Stack:** Python 3 standard library, JSON, JSON Schema Draft 2020-12 documents, static HTML, GitHub Actions YAML. No new runtime framework and no new Python package dependency.

**Spec:** `docs/superpowers/specs/2026-09-13-potato-house-public-crystallization-design.md`

**Companion roadmap:** `docs/superpowers/specs/2026-09-13-potato-house-six-wave-roadmap.md`

## Global Constraints

- The whole-project architecture authority remains `docs/POTATO-HOUSE-CONSTITUTION.md`.
- The visible homepage remains reader-first and keeps exactly five gateways: Tim Dooley, Religion, Philosophy, Science, World.
- World is the fifth Hub; World Map, Politics & Geopolitics, North, and World Systems are specialist World-family surfaces.
- `data/canonical-source-map.json` remains current canonical fact-family ownership authority for existing data families.
- `data/canonical-record-registry.json` remains a generated discovery/inventory aid, not ownership authority.
- `data/repository-spine.json` remains an independent internal classification coordinate; Domain Rooms do not replace it.
- `manifest.json` remains the relationship-first branch/pathway archive map during Wave 1.
- `data/frontend-atlas-bridge.json` remains a live branch/backend-family projection compatibility contract during Wave 1.
- `/explore/` remains the deep interactive reader; no second competing root reader is introduced.
- Public HTML is a projection, never the sole owner of durable knowledge.
- Project canon, autobiography, interpretation, comparative research, historical evidence, and scientific evidence remain epistemically distinct.
- No universal truth score, altitude score, or graph-centrality score is introduced.
- Semantic HTML owns essential public navigation; JavaScript remains enhancement.
- Migration is additive-first and reversible until consumers have moved.
- Validators must validate the artifact; they must not silently mutate it into compliance.
- Do not mass-move knowledge files or redesign `index.html` in Wave 1.
- Before execution, create an isolated worktree using `superpowers:using-git-worktrees`; record `git rev-parse HEAD` as the mutation baseline.

---

## File Structure Locked by This Plan

### New governance files

- Create `data/house/rooms.json` — canonical Domain Room governance identities and bounded-context contracts only.
- Create `data/house/public-surfaces.json` — canonical public route/surface identities only.
- Create `schemas/house-room-registry.schema.json` — machine contract for `rooms.json`.
- Create `schemas/house-public-surface-registry.schema.json` — machine contract for `public-surfaces.json`.
- Create `knowledge/research/potato-house-master/public-route-topology.json` — current major-route topology/migration ledger; research/bridge role, not content ownership.
- Create `scripts/validate_house_governance.py` — focused Wave 1 validator for registry shape, route identity, Room references, topology references, source/deploy routing consistency, and migration pointers.

### Existing machine contracts to modify

- Modify `data/frontend-atlas-bridge.json` — declare compatibility/projection role and pointers to House registries; retain branch/backend projection data.
- Modify `data/backend-coverage-map.json` — add explicit Room/public-surface contract pointers while retaining current dataset ownership/consumer map.
- Modify `data/atlas-manifest.json` — declare House registries in current public-navigation/migration metadata without deleting internal data-layer descriptions.

### Existing public/deploy files to modify

- Modify `tim-dooley/index.html` — primary peer nav World link only.
- Modify `religion/index.html` — primary peer nav World link only; keep contextual World Map links elsewhere.
- Modify `philosophy/index.html` — primary peer nav World link only.
- Modify `science/index.html` — primary peer nav World link only.
- Modify `scripts/patch_home_discovery.py` — remove workflow-specific World→World Map rewrite; retain discovery metadata and specialist World-family patches.
- Modify `scripts/validate_site_shell.py` — remove artifact-healing `restore_canonical_world_route()` mutation and validate the artifact as built.
- Modify `.github/workflows/pages.yml` — verify `/world/` as door five and run House governance validation before artifact build.
- Modify `.github/workflows/quality-checks.yml` — run House governance validation in the main quality gate.

### Existing architecture docs to modify

- Modify `docs/ROOT-NAVIGATION-ARCHITECTURE.md` — mark as historical / Explore UX donor, no longer whole-site/public-root authority.
- Modify `docs/PROJECT-STRUCTURE.md` — replace `manifest.json` as sole public-navigation authority with House public-surface authority plus manifest/bridge compatibility roles.
- Modify `docs/superpowers/specs/2026-09-13-potato-house-public-crystallization-design.md` — status becomes approved for implementation.
- Modify `docs/superpowers/specs/2026-09-13-potato-house-six-wave-roadmap.md` — status becomes approved roadmap.

---

### Task 1: Domain Room Registry and Schema

**Files:**
- Create: `scripts/validate_house_governance.py`
- Create: `schemas/house-room-registry.schema.json`
- Create: `data/house/rooms.json`

**Interfaces:**
- Consumes: `docs/POTATO-HOUSE-CONSTITUTION.md` and the ten approved Domain Room names from the design spec.
- Produces: `load_json(path: Path, errors: list[str]) -> dict`, `validate_schema_subset(value, schema, owner, errors) -> None`, `validate_rooms(errors) -> dict`; later tasks extend the same validator.
- Produces canonical Room IDs used later: `potatoverse-canon`, `archive-sources`, `time-history`, `traditions-texts`, `science-formal-models`, `life-body`, `world-systems`, `culture-information`, `works`, `research-lab`.

- [ ] **Step 1: Write the failing Room validator**

Create `scripts/validate_house_governance.py` with these constants and schema-subset helpers. The validator must use only the Python standard library.

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOMS_PATH = ROOT / "data" / "house" / "rooms.json"
ROOMS_SCHEMA_PATH = ROOT / "schemas" / "house-room-registry.schema.json"

EXPECTED_ROOM_IDS = (
    "potatoverse-canon",
    "archive-sources",
    "time-history",
    "traditions-texts",
    "science-formal-models",
    "life-body",
    "world-systems",
    "culture-information",
    "works",
    "research-lab",
)


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required House contract: {path.relative_to(ROOT)}")
        return {}
    except Exception as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"House contract must be a JSON object: {path.relative_to(ROOT)}")
        return {}
    return value


def matches_type(value, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "null": value is None,
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
    }.get(expected, True)


def validate_schema_subset(value, schema: dict, owner: str, errors: list[str]) -> None:
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not matches_type(value, expected_type):
        errors.append(f"{owner} must be {expected_type}")
        return
    if isinstance(expected_type, list) and not any(matches_type(value, item) for item in expected_type):
        errors.append(f"{owner} must match one of {expected_type}")
        return
    if "const" in schema and value != schema["const"]:
        errors.append(f"{owner} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{owner} must be one of {schema['enum']!r}")
    if isinstance(value, str) and schema.get("pattern") and not re.search(schema["pattern"], value):
        errors.append(f"{owner} does not match pattern {schema['pattern']!r}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{owner} missing required field: {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{owner} contains unexpected field: {key}")
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, dict):
                validate_schema_subset(value[key], child_schema, f"{owner}.{key}", errors)
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{owner} requires at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{owner} allows at most {schema['maxItems']} items")
        if schema.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value):
            errors.append(f"{owner} items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_schema_subset(item, item_schema, f"{owner}[{index}]", errors)


def validate_rooms(errors: list[str]) -> dict:
    schema = load_json(ROOMS_SCHEMA_PATH, errors)
    rooms = load_json(ROOMS_PATH, errors)
    if schema and rooms:
        validate_schema_subset(rooms, schema, "rooms", errors)
    entries = rooms.get("rooms", []) if isinstance(rooms, dict) else []
    ids = [row.get("id") for row in entries if isinstance(row, dict)]
    if tuple(ids) != EXPECTED_ROOM_IDS:
        errors.append(f"canonical Room IDs/order must equal {EXPECTED_ROOM_IDS!r}; got {tuple(ids)!r}")
    known = set(ids)
    for row in entries:
        if not isinstance(row, dict):
            continue
        for target in row.get("interfaces", []):
            if target not in known:
                errors.append(f"Room {row.get('id')} references unknown interface Room {target}")
    return rooms


def main() -> int:
    errors: list[str] = []
    validate_rooms(errors)
    if errors:
        print("POTATO HOUSE GOVERNANCE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("POTATO HOUSE GOVERNANCE VALIDATION PASSED: 10 canonical Domain Rooms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the validator to prove the contract is missing**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: FAIL with missing `schemas/house-room-registry.schema.json` and `data/house/rooms.json`.

- [ ] **Step 3: Create the Room schema**

Create `schemas/house-room-registry.schema.json` with this contract:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://thepotatooflife.github.io/TimDooley/schemas/house-room-registry.schema.json",
  "title": "Potato House Domain Room Registry",
  "type": "object",
  "additionalProperties": false,
  "required": ["version", "updated", "authority", "rooms"],
  "properties": {
    "version": {"type": "string"},
    "updated": {"type": "string"},
    "authority": {"const": "bounded-context-governance"},
    "rooms": {
      "type": "array",
      "minItems": 10,
      "maxItems": 10,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "title", "purpose", "includes", "excludes", "owned_fact_families", "never_owns", "supported_primitives", "schema_extensions", "epistemic_policy", "time_policy", "provenance_policy", "freshness_policy", "interfaces", "allowed_surface_types", "validators", "status"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"},
          "title": {"type": "string"},
          "purpose": {"type": "string"},
          "includes": {"type": "array", "minItems": 1, "items": {"type": "string"}},
          "excludes": {"type": "array", "minItems": 1, "items": {"type": "string"}},
          "owned_fact_families": {"type": "array", "minItems": 1, "items": {"type": "string"}},
          "never_owns": {"type": "array", "minItems": 1, "items": {"type": "string"}},
          "supported_primitives": {"type": "array", "minItems": 1, "items": {"enum": ["subject", "assertion", "artifact", "occurrence", "relation", "activity", "transition", "context"]}},
          "schema_extensions": {"type": "array", "items": {"type": "string"}},
          "epistemic_policy": {"type": "string"},
          "time_policy": {"type": "string"},
          "provenance_policy": {"type": "string"},
          "freshness_policy": {"type": "string"},
          "interfaces": {"type": "array", "items": {"type": "string"}, "uniqueItems": true},
          "allowed_surface_types": {"type": "array", "minItems": 1, "items": {"enum": ["home", "hub", "subject", "guide", "explorer", "evidence"]}},
          "validators": {"type": "array", "items": {"type": "string"}},
          "status": {"enum": ["active", "planned", "retiring"]}
        }
      }
    }
  }
}
```

- [ ] **Step 4: Create the exact ten-room registry**

Create `data/house/rooms.json` with `version: "1.0.0"`, `updated: "2026-09-13"`, `authority: "bounded-context-governance"`, and these exact IDs/titles in this order:

```json
[
  ["potatoverse-canon", "Potatoverse / Canon"],
  ["archive-sources", "Archive & Sources"],
  ["time-history", "Time & History"],
  ["traditions-texts", "Traditions & Texts"],
  ["science-formal-models", "Science & Formal Models"],
  ["life-body", "Life & Body"],
  ["world-systems", "World Systems"],
  ["culture-information", "Culture & Information"],
  ["works", "Works"],
  ["research-lab", "Research Lab"]
]
```

Use these exact purposes and ownership boundaries:

```text
potatoverse-canon: Own project-canon identities, definitions, roles, symbolic systems and mature Potatoverse synthesis without claiming independent empirical status. Never own external-source provenance, independent scientific validity, or country/institution identity.
archive-sources: Own source identity, captures, provenance lineage, evidence classification and archive/recovery state. Never own later synthesis merely because it stores the source.
time-history: Own Occurrence identity, chronology, attestation timing, interpretation timing and historical sequencing. Never silently backdate later interpretation into earlier events.
traditions-texts: Own descriptive/comparative records about traditions, texts, passages and historical religious context. Never turn project resemblance into historical identity or source transmission without evidence.
science-formal-models: Own scientific/formal definitions, models, assumptions, equations, test protocols and evidence-status boundaries. Never treat symbolism or mathematical analogy as established physical evidence.
life-body: Own biological/anatomical/physiological subjects and body-system observations. Never let symbolic body mapping overwrite established anatomy or empirical uncertainty.
world-systems: Own observable countries, institutions, organizations, infrastructure, economic/political/system relationships and programmes grounded in real-world entities. Never let map rendering or project symbolism become the sole owner of world facts.
culture-information: Own cultural/subcultural/information-ecology contexts, media forms, public discourse and social-information relationships. Never own the canonical identity of a person/institution when another family already does.
works: Own creative works, performances, music, writing, visual art, games and explicitly creative artifacts. Never silently promote creative material into doctrine, biography or empirical evidence.
research-lab: Own open questions, hypotheses, research candidates, experiment/design state and unresolved synthesis work. Never present research candidates as canonical or publishable solely because they are indexed.
```

For all ten entries:

- `status` = `"active"`.
- `validators` includes `"scripts/validate_house_governance.py"`.
- `provenance_policy` = `"Preserve source lineage when the Room stores or derives source-bearing claims; public projection never replaces provenance."`.
- `freshness_policy` = `"Review material when its source changes, its public synthesis becomes stale, or a validator/audit reports ownership or route drift."`.
- `allowed_surface_types` must reflect actual use, not every possible type; use `hub/subject/guide/explorer/evidence` as appropriate and do not add `home` except where a Room explicitly feeds Home editorially later.
- `interfaces` must contain only other IDs from the ten-room list.

Use these minimum interface links:

```text
potatoverse-canon -> archive-sources, time-history, traditions-texts, science-formal-models, life-body, works, research-lab
archive-sources -> all other nine Rooms
time-history -> potatoverse-canon, archive-sources, traditions-texts, world-systems, culture-information, works
traditions-texts -> potatoverse-canon, archive-sources, time-history, research-lab
science-formal-models -> archive-sources, life-body, research-lab, world-systems
life-body -> science-formal-models, archive-sources, potatoverse-canon, research-lab
world-systems -> archive-sources, time-history, culture-information, research-lab
culture-information -> archive-sources, time-history, world-systems, works, potatoverse-canon
works -> potatoverse-canon, archive-sources, time-history, culture-information
research-lab -> all other nine Rooms
```

- [ ] **Step 5: Run the Room validator**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: PASS with `10 canonical Domain Rooms`.

- [ ] **Step 6: Commit the Room contract**

```bash
git add scripts/validate_house_governance.py schemas/house-room-registry.schema.json data/house/rooms.json
git commit -m "architecture: add Potato House room registry"
```

---

### Task 2: Public Surface Registry and Route Identity

**Files:**
- Modify: `scripts/validate_house_governance.py`
- Create: `schemas/house-public-surface-registry.schema.json`
- Create: `data/house/public-surfaces.json`

**Interfaces:**
- Consumes: `EXPECTED_ROOM_IDS` and `validate_schema_subset(...)` from Task 1.
- Produces: `EXPECTED_PRIMARY_GATEWAYS`, `validate_public_surfaces(errors, rooms) -> dict`.
- Produces stable public surface IDs consumed by Task 3: `home`, `tim`, `religion`, `philosophy`, `science`, `world`, `timeline`, `explore`, `sources`, `world-map`, `politics`, `north`, `world-systems`, `bible`.

- [ ] **Step 1: Extend the validator first so it fails without the surface registry**

Add:

```python
SURFACES_PATH = ROOT / "data" / "house" / "public-surfaces.json"
SURFACES_SCHEMA_PATH = ROOT / "schemas" / "house-public-surface-registry.schema.json"
EXPECTED_PRIMARY_GATEWAYS = ("tim", "religion", "philosophy", "science", "world")
EXPECTED_PRIMARY_ROUTES = (
    "/tim-dooley/",
    "/religion/",
    "/philosophy/",
    "/science/",
    "/world/",
)


def validate_public_surfaces(errors: list[str], rooms: dict) -> dict:
    schema = load_json(SURFACES_SCHEMA_PATH, errors)
    surfaces = load_json(SURFACES_PATH, errors)
    if schema and surfaces:
        validate_schema_subset(surfaces, schema, "public_surfaces", errors)
    entries = surfaces.get("surfaces", []) if isinstance(surfaces, dict) else []
    by_id = {row.get("id"): row for row in entries if isinstance(row, dict) and row.get("id")}
    if tuple(surfaces.get("primary_gateway_ids", [])) != EXPECTED_PRIMARY_GATEWAYS:
        errors.append("primary_gateway_ids must be exactly Tim, Religion, Philosophy, Science, World")
    routes = tuple(by_id.get(item, {}).get("canonical_route") for item in EXPECTED_PRIMARY_GATEWAYS)
    if routes != EXPECTED_PRIMARY_ROUTES:
        errors.append(f"primary gateway routes must equal {EXPECTED_PRIMARY_ROUTES!r}; got {routes!r}")
    room_ids = {row.get("id") for row in rooms.get("rooms", []) if isinstance(row, dict)}
    canonical_routes: dict[str, str] = {}
    legacy_routes: dict[str, str] = {}
    for surface_id, row in by_id.items():
        route = row.get("canonical_route")
        if route in canonical_routes:
            errors.append(f"duplicate canonical public route {route}: {canonical_routes[route]} and {surface_id}")
        canonical_routes[route] = surface_id
        for room_id in row.get("primary_room_ids", []):
            if room_id not in room_ids:
                errors.append(f"public surface {surface_id} references unknown Room {room_id}")
        parent = row.get("primary_parent")
        if parent is not None and parent not in by_id:
            errors.append(f"public surface {surface_id} references unknown primary_parent {parent}")
        if row.get("is_view") and row.get("knowledge_owner"):
            errors.append(f"Explorer/View {surface_id} cannot be a canonical knowledge owner")
        for legacy in row.get("legacy_routes", []):
            if legacy in canonical_routes:
                errors.append(f"legacy route {legacy} conflicts with canonical route owned by {canonical_routes[legacy]}")
            if legacy in legacy_routes:
                errors.append(f"legacy route {legacy} is duplicated by {legacy_routes[legacy]} and {surface_id}")
            legacy_routes[legacy] = surface_id
    return surfaces
```

Change `main()` to call `rooms = validate_rooms(errors)` followed by `validate_public_surfaces(errors, rooms)`.

- [ ] **Step 2: Run and verify failure**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: FAIL for missing public-surface schema/registry.

- [ ] **Step 3: Create the public-surface schema**

Create `schemas/house-public-surface-registry.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://thepotatooflife.github.io/TimDooley/schemas/house-public-surface-registry.schema.json",
  "title": "Potato House Public Surface Registry",
  "type": "object",
  "additionalProperties": false,
  "required": ["version", "updated", "authority", "room_registry", "primary_gateway_ids", "secondary_global_ids", "surfaces"],
  "properties": {
    "version": {"type": "string"},
    "updated": {"type": "string"},
    "authority": {"const": "public-route-identity"},
    "room_registry": {"const": "data/house/rooms.json"},
    "primary_gateway_ids": {"type": "array", "minItems": 5, "maxItems": 5, "uniqueItems": true, "items": {"type": "string"}},
    "secondary_global_ids": {"type": "array", "uniqueItems": true, "items": {"type": "string"}},
    "surfaces": {
      "type": "array",
      "minItems": 14,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "route", "canonical_route", "surface_type", "title", "primary_parent", "primary_room_ids", "status", "visibility", "primary_navigation", "is_view", "knowledge_owner", "legacy_routes"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"},
          "route": {"type": "string", "pattern": "^/"},
          "canonical_route": {"type": "string", "pattern": "^/"},
          "surface_type": {"enum": ["home", "hub", "subject", "guide", "explorer", "evidence"]},
          "title": {"type": "string"},
          "primary_parent": {"type": ["string", "null"]},
          "primary_room_ids": {"type": "array", "uniqueItems": true, "items": {"type": "string"}},
          "status": {"enum": ["active", "compatibility", "retired"]},
          "visibility": {"enum": ["primary", "secondary", "specialist", "compatibility"]},
          "primary_navigation": {"type": "boolean"},
          "is_view": {"type": "boolean"},
          "knowledge_owner": {"const": false},
          "legacy_routes": {"type": "array", "uniqueItems": true, "items": {"type": "string", "pattern": "^/"}}
        }
      }
    }
  }
}
```

- [ ] **Step 4: Create the exact initial public-surface registry**

Create `data/house/public-surfaces.json` with:

```json
{
  "version": "1.0.0",
  "updated": "2026-09-13",
  "authority": "public-route-identity",
  "room_registry": "data/house/rooms.json",
  "primary_gateway_ids": ["tim", "religion", "philosophy", "science", "world"],
  "secondary_global_ids": ["timeline", "explore", "sources"]
}
```

and these exact surface records:

```text
home          /                         home      parent=null      rooms=[]                                                            primary   nav=false view=false legacy=/learn/
tim           /tim-dooley/              hub       parent=home      rooms=potatoverse-canon,time-history,archive-sources,works,culture-information primary nav=true  view=false
religion      /religion/                hub       parent=home      rooms=potatoverse-canon,traditions-texts,time-history,archive-sources primary   nav=true  view=false
philosophy    /philosophy/              hub       parent=home      rooms=potatoverse-canon,traditions-texts,research-lab               primary   nav=true  view=false
science       /science/                 hub       parent=home      rooms=science-formal-models,life-body,archive-sources,research-lab  primary   nav=true  view=false
world         /world/                   hub       parent=home      rooms=world-systems,time-history,archive-sources,culture-information,research-lab primary nav=true view=false
timeline      /timeline/                explorer  parent=home      rooms=time-history,archive-sources                                  secondary nav=false view=true  legacy=/chronology/
explore       /explore/                 explorer  parent=home      rooms=all ten Room IDs                                              secondary nav=false view=true
sources       /context/source-authority/ evidence parent=home      rooms=archive-sources                                               secondary nav=false view=true
world-map     /world-map/               explorer  parent=world     rooms=world-systems,time-history,archive-sources                    specialist nav=false view=true  legacy=/world-map/3d.html
politics      /politics/                guide     parent=world     rooms=world-systems,time-history,culture-information,archive-sources specialist nav=false view=false
north         /north/                   guide     parent=world     rooms=world-systems,potatoverse-canon,time-history,archive-sources,research-lab specialist nav=false view=false
world-systems /world-systems/           guide     parent=world     rooms=world-systems,archive-sources,research-lab                     specialist nav=false view=false
bible         /traditions/bible/        explorer  parent=religion  rooms=traditions-texts,archive-sources,time-history,potatoverse-canon specialist nav=false view=true legacy=/religion/jesus-tim/
```

For every row:

- `route` equals `canonical_route` in Wave 1.
- `status` = `"active"`.
- `knowledge_owner` = `false`.
- use the visible labels `Home`, `Tim Dooley`, `Religion`, `Philosophy`, `Science`, `World`, `Timeline`, `Explore`, `Sources`, `World Map`, `Politics & Geopolitics`, `North`, `World Systems`, `Bible Comparison`.

- [ ] **Step 5: Run the validator**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: PASS for Room and public-surface contracts.

- [ ] **Step 6: Commit public route identity**

```bash
git add scripts/validate_house_governance.py schemas/house-public-surface-registry.schema.json data/house/public-surfaces.json
git commit -m "architecture: add public surface registry"
```

---

### Task 3: Major-Route Topology Ledger and Migration Pointers

**Files:**
- Modify: `scripts/validate_house_governance.py`
- Create: `knowledge/research/potato-house-master/public-route-topology.json`
- Modify: `data/frontend-atlas-bridge.json`
- Modify: `data/backend-coverage-map.json`
- Modify: `data/atlas-manifest.json`

**Interfaces:**
- Consumes: public surface IDs and Room IDs from Tasks 1–2.
- Produces: `validate_topology(errors, rooms, surfaces) -> dict` and explicit machine-readable migration pointers from existing manifests to House contracts.
- `public-route-topology.json` remains a research/bridge index and never owns facts rendered by its listed surfaces.

- [ ] **Step 1: Add failing topology/migration assertions first**

Add constants:

```python
TOPOLOGY_PATH = ROOT / "knowledge" / "research" / "potato-house-master" / "public-route-topology.json"
BRIDGE_PATH = ROOT / "data" / "frontend-atlas-bridge.json"
COVERAGE_PATH = ROOT / "data" / "backend-coverage-map.json"
ATLAS_PATH = ROOT / "data" / "atlas-manifest.json"
EXPECTED_MAJOR_SURFACES = (
    "home", "tim", "religion", "philosophy", "science", "world",
    "timeline", "explore", "sources", "world-map", "politics", "north",
    "world-systems", "bible",
)
```

Add:

```python
def validate_topology(errors: list[str], rooms: dict, surfaces: dict) -> dict:
    topology = load_json(TOPOLOGY_PATH, errors)
    room_ids = {row.get("id") for row in rooms.get("rooms", []) if isinstance(row, dict)}
    surface_by_id = {
        row.get("id"): row
        for row in surfaces.get("surfaces", [])
        if isinstance(row, dict) and row.get("id")
    }
    rows = topology.get("records", []) if isinstance(topology, dict) else []
    by_id = {row.get("surface_id"): row for row in rows if isinstance(row, dict) and row.get("surface_id")}
    if tuple(by_id) != EXPECTED_MAJOR_SURFACES:
        errors.append(f"topology must classify current major surfaces in canonical order; got {tuple(by_id)!r}")
    for surface_id, row in by_id.items():
        surface = surface_by_id.get(surface_id)
        if not surface:
            errors.append(f"topology references unknown public surface {surface_id}")
            continue
        if row.get("canonical_route") != surface.get("canonical_route"):
            errors.append(f"topology route disagrees for {surface_id}")
        if row.get("surface_type") != surface.get("surface_type"):
            errors.append(f"topology surface_type disagrees for {surface_id}")
        if set(row.get("room_ids", [])) != set(surface.get("primary_room_ids", [])):
            errors.append(f"topology Room set disagrees for {surface_id}")
        hub = row.get("primary_hub_id")
        if hub is not None and hub not in surface_by_id:
            errors.append(f"topology {surface_id} references unknown primary_hub_id {hub}")
        for room_id in row.get("room_ids", []):
            if room_id not in room_ids:
                errors.append(f"topology {surface_id} references unknown Room {room_id}")
    return topology


def validate_migration_pointers(errors: list[str]) -> None:
    bridge = load_json(BRIDGE_PATH, errors)
    coverage = load_json(COVERAGE_PATH, errors)
    atlas = load_json(ATLAS_PATH, errors)
    expected_rooms = "data/house/rooms.json"
    expected_surfaces = "data/house/public-surfaces.json"
    if bridge.get("room_registry") != expected_rooms:
        errors.append("frontend bridge must point to data/house/rooms.json")
    if bridge.get("public_surface_registry") != expected_surfaces:
        errors.append("frontend bridge must point to data/house/public-surfaces.json")
    if bridge.get("authority_status") != "branch-and-backend-family-projection-compatibility":
        errors.append("frontend bridge must declare compatibility projection authority_status")
    if coverage.get("room_contract") != expected_rooms or coverage.get("public_surface_contract") != expected_surfaces:
        errors.append("backend coverage map must declare House Room/public-surface contracts")
    if atlas.get("house_rooms") != expected_rooms or atlas.get("public_surfaces") != expected_surfaces:
        errors.append("atlas manifest must declare House Room/public-surface contracts")
```

Call both from `main()`.

- [ ] **Step 2: Run and verify failure**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: FAIL for missing topology and migration pointers.

- [ ] **Step 3: Create the topology ledger**

Create `knowledge/research/potato-house-master/public-route-topology.json` with:

```json
{
  "version": "1.0.0",
  "updated": "2026-09-13",
  "purpose": "Wave 1 route-topology bridge for current major public surfaces. This file classifies navigation and migration state; it does not own substantive knowledge.",
  "room_registry": "data/house/rooms.json",
  "public_surface_registry": "data/house/public-surfaces.json",
  "records": []
}
```

Populate one record for each `EXPECTED_MAJOR_SURFACES` item, in that exact order. Every record has:

```json
{
  "surface_id": "world-map",
  "surface_type": "explorer",
  "canonical_route": "/world-map/",
  "primary_hub_id": "world",
  "room_ids": ["world-systems", "time-history", "archive-sources"],
  "specialist_view": true,
  "migration_status": "current",
  "compatibility_routes": ["/world-map/3d.html"]
}
```

Use these hub rules:

```text
home -> primary_hub_id null
five major hubs -> primary_hub_id equal their own surface ID
timeline/explore/sources -> primary_hub_id null
world-map/politics/north/world-systems -> primary_hub_id world
bible -> primary_hub_id religion
```

`specialist_view` is true only for Timeline, Explore, Sources, World Map, and Bible in the initial ledger; Guides remain false even when specialist.

- [ ] **Step 4: Add explicit migration pointers without deleting current contracts**

In `data/frontend-atlas-bridge.json` add top-level fields:

```json
"authority_status": "branch-and-backend-family-projection-compatibility",
"room_registry": "data/house/rooms.json",
"public_surface_registry": "data/house/public-surfaces.json"
```

Keep `public_doors`, `branch_projection`, `backend_family_projection`, `route_map`, resolution rules, and integrity requirements intact.

In `data/backend-coverage-map.json` add:

```json
"room_contract": "data/house/rooms.json",
"public_surface_contract": "data/house/public-surfaces.json"
```

Keep `frontend_contract` pointing to `data/frontend-atlas-bridge.json` because that file still owns branch/backend projection compatibility during Wave 1.

In `data/atlas-manifest.json` add:

```json
"house_rooms": "data/house/rooms.json",
"public_surfaces": "data/house/public-surfaces.json"
```

Update its `public_navigation` prose to state that public route identity comes from `data/house/public-surfaces.json`, while `manifest.json` and `data/frontend-atlas-bridge.json` remain branch/pathway/projection compatibility inputs.

- [ ] **Step 5: Run House and existing projection checks**

Run:

```bash
python scripts/validate_house_governance.py
python scripts/validate_public_projection.py
python scripts/audit_source_of_truth.py
```

Expected: all PASS.

- [ ] **Step 6: Commit topology and migration metadata**

```bash
git add scripts/validate_house_governance.py knowledge/research/potato-house-master/public-route-topology.json data/frontend-atlas-bridge.json data/backend-coverage-map.json data/atlas-manifest.json
git commit -m "architecture: map House route topology"
```

---

### Task 4: Normalize Source and Deployed World Routing

**Files:**
- Modify: `scripts/validate_house_governance.py`
- Modify: `tim-dooley/index.html`
- Modify: `religion/index.html`
- Modify: `philosophy/index.html`
- Modify: `science/index.html`
- Modify: `scripts/patch_home_discovery.py`
- Modify: `scripts/validate_site_shell.py`
- Modify: `.github/workflows/pages.yml`

**Interfaces:**
- Consumes: public-surface primary gateway contract from Task 2.
- Produces one consistent route rule in source, build patches, smoke checks, and final validator: fifth primary destination is `/world/`; `/world-map/` remains available only where Map is the intended specialist destination.

- [ ] **Step 1: Extend the House validator so current drift fails before editing pages**

Add:

```python
PRIMARY_PEER_NAV_FILES = (
    "tim-dooley/index.html",
    "religion/index.html",
    "philosophy/index.html",
    "science/index.html",
)


def first_nav(text: str) -> str:
    match = re.search(r"<nav\\b[^>]*>(.*?)</nav>", text, flags=re.I | re.S)
    return match.group(1) if match else ""


def validate_primary_world_routing(errors: list[str]) -> None:
    for rel in PRIMARY_PEER_NAV_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        nav = first_nav(text)
        if 'href="../world/"' not in nav:
            errors.append(f"{rel} primary peer nav must link to ../world/")
        if 'href="../world-map/"' in nav:
            errors.append(f"{rel} primary peer nav must not use World Map as the fifth peer")

    patch = (ROOT / "scripts" / "patch_home_discovery.py").read_text(encoding="utf-8")
    if "GITHUB_WORKFLOW" in patch and "world-map/" in patch and 'href="world/"' in patch:
        errors.append("patch_home_discovery.py must not rewrite the canonical World homepage door for deploy compatibility")

    shell = (ROOT / "scripts" / "validate_site_shell.py").read_text(encoding="utf-8")
    if "restore_canonical_world_route" in shell:
        errors.append("validate_site_shell.py must validate rather than mutate the built World route")

    pages = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    if "['tim-dooley/','religion/','philosophy/','science/','world-map/']" in pages:
        errors.append("Pages deploy smoke test still expects World Map as door five")
```

Call `validate_primary_world_routing(errors)` from `main()`.

- [ ] **Step 2: Run and verify the known failures**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: FAIL on Tim/Religion/Philosophy/Science primary nav, deploy compatibility rewrite, site-shell artifact mutation, and Pages smoke expectation.

- [ ] **Step 3: Normalize only the primary peer nav on the four Hubs**

In the first `<nav>` of each of these files, replace the World Map peer link with World:

```html
<a href="../world/">World</a>
```

Files:

```text
tim-dooley/index.html
religion/index.html
philosophy/index.html
science/index.html
```

Do not remove contextual links such as `Religion in the World Map`, North Map actions, or World-family specialist navigation.

- [ ] **Step 4: Remove the deploy-only homepage rewrite**

In `scripts/patch_home_discovery.py`:

- remove `import os` if unused afterward;
- delete the `if os.environ.get("GITHUB_WORKFLOW") == "Deploy Potato of Life": ...` block that rewrites `world/` to `world-map/`;
- keep sitemap/discovery alternates, North family patch, World Map toolbar patch, and machine-index World-family routes intact.

After the edit, `_site/index.html` remains `/world/` from build through upload.

- [ ] **Step 5: Remove artifact-healing behavior from the site-shell validator**

In `scripts/validate_site_shell.py`:

- delete `restore_canonical_world_route()`;
- delete its invocation from `main()`;
- keep the existing `CANONICAL_HOME_LINKS` tuple ending in `world/` and let validation fail if the artifact disagrees.

This converts the validator from a repair step back into a true gate.

- [ ] **Step 6: Fix the deploy smoke contract itself**

In `.github/workflows/pages.yml`:

1. under `Verify canonical reader surface`, add:

```bash
test -f _site/world/index.html
```

2. change the homepage grep from:

```bash
grep -q 'href="world-map/"' _site/index.html
```

to:

```bash
grep -q 'href="world/"' _site/index.html
```

3. change the Python expected list to:

```python
expected = ['tim-dooley/','religion/','philosophy/','science/','world/']
```

Do not remove the separate World Map existence/runtime checks later in the workflow.

- [ ] **Step 7: Run source and built-artifact checks**

Run:

```bash
python scripts/validate_house_governance.py
python scripts/validate_reader_surfaces.py
python scripts/validate_public_projection.py
python scripts/build_site.py
python scripts/build_discovery.py
python scripts/patch_home_discovery.py
python scripts/validate_public_navigation.py
python scripts/validate_site_shell.py
```

Expected: all PASS and `_site/index.html` still contains `href="world/"` after `patch_home_discovery.py`.

- [ ] **Step 8: Commit the World-routing convergence**

```bash
git add scripts/validate_house_governance.py tim-dooley/index.html religion/index.html philosophy/index.html science/index.html scripts/patch_home_discovery.py scripts/validate_site_shell.py .github/workflows/pages.yml
git commit -m "fix: make World the stable fifth public hub"
```

---

### Task 5: Authority Documentation, CI Wiring, and Exact-Artifact Verification

**Files:**
- Modify: `.github/workflows/quality-checks.yml`
- Modify: `.github/workflows/pages.yml`
- Modify: `docs/ROOT-NAVIGATION-ARCHITECTURE.md`
- Modify: `docs/PROJECT-STRUCTURE.md`
- Modify: `docs/superpowers/specs/2026-09-13-potato-house-public-crystallization-design.md`
- Modify: `docs/superpowers/specs/2026-09-13-potato-house-six-wave-roadmap.md`

**Interfaces:**
- Consumes: `scripts/validate_house_governance.py` from Tasks 1–4.
- Produces: both quality and deploy workflows fail before build if House governance/route contracts drift; documentation points to the same current authority hierarchy.

- [ ] **Step 1: Wire the focused House validator into both workflows**

In `.github/workflows/quality-checks.yml`, add after `Audit source-of-truth and routes`:

```yaml
      - name: Validate Potato House governance
        run: python scripts/validate_house_governance.py
```

In `.github/workflows/pages.yml`, add after `Validate question-led reader surfaces` and before build/discovery work:

```yaml
      - name: Validate Potato House governance
        run: python scripts/validate_house_governance.py
```

Do not remove existing public-projection, reader-surface, generated-navigation, site-shell, or source-of-truth gates.

- [ ] **Step 2: Mark Root Navigation as historical / Explore-specific**

Replace the opening status block in `docs/ROOT-NAVIGATION-ARCHITECTURE.md` with:

```markdown
# Root Navigation Architecture

Status: historical architecture / Explore UX donor; superseded as whole-site and homepage authority
Date: 2026-09-08
Superseded: 2026-09-13
Current authority: `docs/POTATO-HOUSE-CONSTITUTION.md` + `data/house/public-surfaces.json`
Current role: preserve progressive-disclosure, current-path, expandable-tree, dossier-in-place, and state-persistence ideas for `/explore/` and specialist navigation work.

> The WORLD / AXIS root and in-place homepage model below are preserved as architectural history. They are not the current public root contract.
```

Preserve the remaining historical document; do not rewrite it as though it had always described the House architecture.

- [ ] **Step 3: Update Project Structure authority language**

In `docs/PROJECT-STRUCTURE.md`, replace:

```text
The public doorway is `index.html`. The canonical branch/navigation contract is `manifest.json`. The durable cross-project record map is `knowledge/indexes/core-index.json`.
```

with:

```text
The public doorway is `index.html`. Stable public route identity is owned by `data/house/public-surfaces.json`; bounded semantic governance is owned by `data/house/rooms.json`. `manifest.json` remains the relationship-first branch/pathway map and `data/frontend-atlas-bridge.json` remains the Wave 1 branch/backend projection compatibility contract. The durable cross-project record map remains `knowledge/indexes/core-index.json`.
```

In the canonical ownership table, change the public-navigation row so:

```text
Public route identity | data/house/public-surfaces.json | manifest.json, data/frontend-atlas-bridge.json, generated discovery/navigation projections
Domain Room governance | data/house/rooms.json | POTATO-HOUSE-CONSTITUTION.md, Room research/placement maps
```

- [ ] **Step 4: Record the human approval state in the two approved specs**

Change the design status line to:

```text
Status: approved architecture; Wave 1 implementation authorized
```

Change the six-wave roadmap status line to:

```text
Status: approved companion roadmap; execute sequentially, one planned wave at a time
```

Do not change Waves 2–6 into implementation authorization.

- [ ] **Step 5: Run focused governance and architecture checks**

Run:

```bash
python scripts/validate_house_governance.py
python scripts/validate_public_projection.py
python scripts/validate_generated_navigation.py
python scripts/validate_explore_projection.py
python scripts/validate_repository_spine.py
python scripts/validate_architecture_layers.py
python scripts/audit_source_of_truth.py
```

Expected: all PASS.

- [ ] **Step 6: Run the deploy-tail sequence against the exact built artifact**

Run the repository-equivalent build tail in this order:

```bash
python scripts/build_canonical_record_registry.py
python scripts/build_site.py
python scripts/build_bible_study.py
python scripts/build_science_catalog.py
python scripts/validate_science_portal.py
python scripts/build_discovery.py
python scripts/patch_home_discovery.py
rm -rf _site/archive
test ! -e _site/archive
python scripts/enrich_weak_descriptions.py
python scripts/optimize_seo.py
python scripts/validate_public_navigation.py
python scripts/check_machine_discoverability.py
python scripts/validate_site_shell.py
```

Then assert the actual built homepage and four peer Hubs:

```bash
python - <<'PY'
import re
from pathlib import Path

home = Path('_site/index.html').read_text(encoding='utf-8')
nav = re.search(r'<nav class="sections"[^>]*>(.*?)</nav>', home, flags=re.I | re.S)
assert nav
hrefs = re.findall(r'href="([^"]+)"', nav.group(1))
assert hrefs == ['tim-dooley/','religion/','philosophy/','science/','world/'], hrefs

for rel in ('tim-dooley/index.html','religion/index.html','philosophy/index.html','science/index.html'):
    text = Path('_site', rel).read_text(encoding='utf-8')
    first = re.search(r'<nav\b[^>]*>(.*?)</nav>', text, flags=re.I | re.S)
    assert first, rel
    assert 'href="../world/"' in first.group(1), rel
    assert 'href="../world-map/"' not in first.group(1), rel

print('Verified source-to-built House public routing contract')
PY
```

Expected: PASS. Do not add a repair step if this fails; fix the source/build consumer that introduced drift.

- [ ] **Step 7: Run the whole repository quality workflow locally where practical**

At minimum run every Python validator/build command currently listed in `.github/workflows/quality-checks.yml` that does not depend on external network downloads. If a command fails, fix the actual regression before continuing; do not weaken unrelated validators to make Wave 1 pass.

Also run:

```bash
git diff --check
git status --short
```

Expected: no whitespace errors; only intended Wave 1 files changed.

- [ ] **Step 8: Commit CI/docs approval convergence**

```bash
git add .github/workflows/quality-checks.yml .github/workflows/pages.yml docs/ROOT-NAVIGATION-ARCHITECTURE.md docs/PROJECT-STRUCTURE.md docs/superpowers/specs/2026-09-13-potato-house-public-crystallization-design.md docs/superpowers/specs/2026-09-13-potato-house-six-wave-roadmap.md
git commit -m "docs: finalize Potato House Wave 1 authority"
```

---

## Wave 1 Completion Checklist

Before claiming Wave 1 complete, confirm all of the following from the exact branch head:

- [ ] `data/house/rooms.json` contains exactly ten canonical Domain Rooms.
- [ ] `data/house/public-surfaces.json` contains stable identities for all fourteen initial major surfaces.
- [ ] Five primary gateway IDs are exactly Tim, Religion, Philosophy, Science, World.
- [ ] World Map is a specialist Explorer under World.
- [ ] Politics, North, and World Systems are specialist World-family surfaces under World.
- [ ] Timeline, Explore, and Sources are secondary/global surfaces rather than homepage peers.
- [ ] Public-surface Room references resolve.
- [ ] Topology records resolve to public surfaces and Room IDs.
- [ ] Existing bridge/coverage/atlas contracts point to the new House registries without losing their Wave 1 compatibility roles.
- [ ] Tim, Religion, Philosophy, and Science primary peer nav use World, not World Map.
- [ ] Contextual World Map links remain where the Map itself is intended.
- [ ] `patch_home_discovery.py` no longer rewrites World to World Map for the deploy workflow.
- [ ] `validate_site_shell.py` no longer mutates `_site/index.html` into compliance.
- [ ] Pages smoke tests expect `world/` as the fifth entrance.
- [ ] House governance validation runs in both quality and deploy workflows.
- [ ] Root Navigation is explicitly historical / Explore-specific rather than active whole-site authority.
- [ ] Project Structure names House public-surface and Room authority correctly.
- [ ] `index.html` is not visually redesigned.
- [ ] No new runtime dependency was added.
- [ ] No knowledge owner was moved merely to satisfy navigation.
- [ ] Existing public projection, Explore, discovery, source-of-truth, and site-shell checks remain green.
- [ ] The exact built artifact retains `/world/` after all post-build patch scripts.

## Deliberately Deferred to Later Waves

Do not include these in Wave 1 even if they are tempting while editing nearby files:

- automatic `Related`, `History`, `Sources`, `Broader context`, or `Explore further` generation;
- subject-level topology for thalamus, Denmark, companies, passages, equations, or creative works;
- crystallization/readiness scoring or Gardener queue generation;
- lifecycle promotion of raw/captured/reviewed/canonical material;
- automatic public page generation from Domain Rooms;
- Explore UI redesign or Yggdrasil/Tree/Root visualization;
- Timeline/World Map/Bible canonical-ID migration beyond current route identity;
- homepage Start Here editorial redesign;
- mass migration of `manifest.json` or `frontend-atlas-bridge.json` consumers;
- deletion of legacy architecture/provenance files.

Wave 1 ends when governance and routing authority are explicit, validated, and consistent. Wave 2 must be planned from that actual repository state.
