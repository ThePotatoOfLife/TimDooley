# Potato House Wave 1 Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the first machine-readable Potato House governance layer: ten Domain Rooms, stable public-surface identities, a route-topology bridge, consistent World-as-fifth-Hub routing, and exact-artifact validation without redesigning the homepage.

**Architecture:** Add two small governance registries under `data/house/`, validate them with one focused Python standard-library validator, and connect the current bridge/coverage/manifest files to those contracts without deleting their existing responsibilities. Remove only the known World→World Map route drift so source, build, and deployed artifact agree on the same five-Hub architecture.

**Tech Stack:** Python 3 standard library, JSON, JSON Schema Draft 2020-12 documents, static HTML, GitHub Actions YAML. No new runtime framework and no new Python dependency.

**Spec:** `docs/superpowers/specs/2026-09-13-potato-house-public-crystallization-design.md`

**Companion roadmap:** `docs/superpowers/specs/2026-09-13-potato-house-six-wave-roadmap.md`

**Downstream dependency:** Waves 2–6 all depend on the stable Room/public-surface contracts created here. Do not start Wave 2 implementation until this plan is complete on the actual execution branch and the exact built artifact is green.

## Global Constraints

- Whole-project architecture authority remains `docs/POTATO-HOUSE-CONSTITUTION.md`.
- Public Home remains reader-first and keeps exactly five primary gateways: Tim Dooley, Religion, Philosophy, Science, World.
- World is the fifth Hub; World Map, Politics & Geopolitics, North, and World Systems are specialist World-family surfaces.
- `data/canonical-source-map.json` remains current canonical fact-family ownership authority.
- `data/canonical-record-registry.json` remains generated inventory/discovery, not ownership authority.
- `data/repository-spine.json` remains an independent internal classification coordinate; Domain Rooms do not replace it.
- `manifest.json` remains the relationship-first branch/pathway archive map during Wave 1.
- `data/frontend-atlas-bridge.json` remains the branch/backend-family projection compatibility contract during Wave 1.
- `/explore/` remains the deep reader; do not introduce a competing root reader.
- Project canon, autobiography, interpretation, comparative research, history, science, and external evidence remain distinguishable.
- No truth score, maturity score, altitude score, or graph-centrality score is introduced in Wave 1.
- Essential public navigation remains semantic HTML; JavaScript remains enhancement.
- Migration is additive-first and reversible until consumers have moved.
- Validators must validate; they must not repair/mutate artifacts into compliance.
- Do not mass-move knowledge files, redesign Home, or auto-generate relation blocks in Wave 1.
- At execution time, create an isolated worktree with `superpowers:using-git-worktrees` and record `git rev-parse HEAD` before mutation.

---

## File Structure Locked by This Plan

### New files

- `data/house/rooms.json` — canonical Domain Room governance records only.
- `data/house/public-surfaces.json` — canonical public route/surface identities only.
- `schemas/house-room-registry.schema.json` — contract for Rooms.
- `schemas/house-public-surface-registry.schema.json` — contract for public surfaces.
- `knowledge/research/potato-house-master/public-route-topology.json` — migration/topology ledger, not substantive knowledge owner.
- `scripts/validate_house_governance.py` — focused governance/route validator.

### Existing files to modify

- `data/frontend-atlas-bridge.json`
- `data/backend-coverage-map.json`
- `data/atlas-manifest.json`
- `tim-dooley/index.html`
- `religion/index.html`
- `philosophy/index.html`
- `science/index.html`
- `scripts/patch_home_discovery.py`
- `scripts/validate_site_shell.py`
- `.github/workflows/pages.yml`
- `.github/workflows/quality-checks.yml`
- `docs/ROOT-NAVIGATION-ARCHITECTURE.md`
- `docs/PROJECT-STRUCTURE.md`
- `docs/superpowers/specs/2026-09-13-potato-house-public-crystallization-design.md`
- `docs/superpowers/specs/2026-09-13-potato-house-six-wave-roadmap.md`

---

### Task 1: Domain Room Registry and Validator Kernel

**Files:**
- Create: `scripts/validate_house_governance.py`
- Create: `schemas/house-room-registry.schema.json`
- Create: `data/house/rooms.json`

**Interfaces:**
- Consumes: `docs/POTATO-HOUSE-CONSTITUTION.md` and approved ten-Room names.
- Produces: `load_json(path: Path, errors: list[str]) -> dict`, `validate_schema_subset(value, schema, owner, errors) -> None`, `validate_rooms(errors) -> dict`.
- Produces stable Room IDs: `potatoverse-canon`, `archive-sources`, `time-history`, `traditions-texts`, `science-formal-models`, `life-body`, `world-systems`, `culture-information`, `works`, `research-lab`.

- [ ] **Step 1: Write the failing validator kernel**

Create `scripts/validate_house_governance.py` with this initial implementation:

```python
#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOMS_PATH = ROOT / "data" / "house" / "rooms.json"
ROOMS_SCHEMA_PATH = ROOT / "schemas" / "house-room-registry.schema.json"
EXPECTED_ROOM_IDS = (
    "potatoverse-canon", "archive-sources", "time-history",
    "traditions-texts", "science-formal-models", "life-body",
    "world-systems", "culture-information", "works", "research-lab",
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
        errors.append(f"{owner} must be {expected_type}"); return
    if isinstance(expected_type, list) and not any(matches_type(value, item) for item in expected_type):
        errors.append(f"{owner} must match one of {expected_type}"); return
    if "const" in schema and value != schema["const"]:
        errors.append(f"{owner} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{owner} must be one of {schema['enum']!r}")
    if isinstance(value, str) and schema.get("pattern") and not re.search(schema["pattern"], value):
        errors.append(f"{owner} does not match pattern {schema['pattern']!r}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value: errors.append(f"{owner} missing required field: {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties: errors.append(f"{owner} contains unexpected field: {key}")
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, dict):
                validate_schema_subset(value[key], child_schema, f"{owner}.{key}", errors)
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{owner} requires at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{owner} allows at most {schema['maxItems']} items")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            errors.append(f"{owner} items must be unique")
        if isinstance(schema.get("items"), dict):
            for index, item in enumerate(value):
                validate_schema_subset(item, schema["items"], f"{owner}[{index}]", errors)

def validate_rooms(errors: list[str]) -> dict:
    schema = load_json(ROOMS_SCHEMA_PATH, errors)
    rooms = load_json(ROOMS_PATH, errors)
    if schema and rooms: validate_schema_subset(rooms, schema, "rooms", errors)
    entries = rooms.get("rooms", []) if isinstance(rooms, dict) else []
    ids = [row.get("id") for row in entries if isinstance(row, dict)]
    if tuple(ids) != EXPECTED_ROOM_IDS:
        errors.append(f"canonical Room IDs/order must equal {EXPECTED_ROOM_IDS!r}; got {tuple(ids)!r}")
    known = set(ids)
    for row in entries:
        if isinstance(row, dict):
            for target in row.get("interfaces", []):
                if target not in known:
                    errors.append(f"Room {row.get('id')} references unknown interface Room {target}")
    return rooms

def main() -> int:
    errors: list[str] = []
    validate_rooms(errors)
    if errors:
        print("POTATO HOUSE GOVERNANCE VALIDATION FAILED")
        for error in errors: print(f"- {error}")
        return 1
    print("POTATO HOUSE GOVERNANCE VALIDATION PASSED: 10 canonical Domain Rooms")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Verify RED**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: FAIL for missing Room schema and registry.

- [ ] **Step 3: Create the Room schema**

Create `schemas/house-room-registry.schema.json` with root fields `version`, `updated`, `authority`, `rooms`; `authority` must be `bounded-context-governance`; exactly ten Room records; each Room record requires:

```text
id, title, purpose, includes, excludes, owned_fact_families, never_owns,
supported_primitives, schema_extensions, epistemic_policy, time_policy,
provenance_policy, freshness_policy, interfaces, allowed_surface_types,
validators, status
```

Use primitive enum exactly:

```text
subject, assertion, artifact, occurrence, relation, activity, transition, context
```

Use surface-type enum exactly:

```text
home, hub, subject, guide, explorer, evidence
```

Use status enum exactly:

```text
active, planned, retiring
```

- [ ] **Step 4: Create the ten Room records**

Create `data/house/rooms.json` with `version: "1.0.0"`, `updated: "2026-09-13"`, `authority: "bounded-context-governance"`, and Room IDs/titles in this exact order:

```text
potatoverse-canon      Potatoverse / Canon
archive-sources        Archive & Sources
time-history           Time & History
traditions-texts       Traditions & Texts
science-formal-models  Science & Formal Models
life-body              Life & Body
world-systems          World Systems
culture-information    Culture & Information
works                  Works
research-lab           Research Lab
```

Each record must explicitly state what it owns and never owns. Use the design meanings: project-canon synthesis without empirical inflation; provenance without later-synthesis ownership; chronology without backdating; comparative traditions without identity collapse; science/formal models without metaphor→evidence promotion; anatomy without symbolic overwrite; world facts without map-render ownership; culture/information without stealing person/institution identity; works without doctrine/biography promotion; research questions without canonical/public promotion.

Use `status: "active"` and include `scripts/validate_house_governance.py` in `validators` for all ten.

- [ ] **Step 5: Verify GREEN**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: PASS with ten canonical Rooms.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_house_governance.py schemas/house-room-registry.schema.json data/house/rooms.json
git commit -m "architecture: add Potato House room registry"
```

---

### Task 2: Public Surface Registry and Stable Route Identity

**Files:**
- Modify: `scripts/validate_house_governance.py`
- Create: `schemas/house-public-surface-registry.schema.json`
- Create: `data/house/public-surfaces.json`

**Interfaces:**
- Consumes: Room IDs from Task 1.
- Produces: `validate_public_surfaces(errors, rooms) -> dict` and stable IDs `home`, `tim`, `religion`, `philosophy`, `science`, `world`, `timeline`, `explore`, `sources`, `world-map`, `politics`, `north`, `world-systems`, `bible`.

- [ ] **Step 1: Add failing public-surface assertions**

Add to the validator:

```python
SURFACES_PATH = ROOT / "data" / "house" / "public-surfaces.json"
SURFACES_SCHEMA_PATH = ROOT / "schemas" / "house-public-surface-registry.schema.json"
EXPECTED_PRIMARY_GATEWAYS = ("tim", "religion", "philosophy", "science", "world")
EXPECTED_PRIMARY_ROUTES = ("/tim-dooley/", "/religion/", "/philosophy/", "/science/", "/world/")
```

Implement `validate_public_surfaces(errors, rooms)` so it checks schema, exact gateway IDs/order, exact primary routes, unique canonical routes, valid Room references, valid parent references, no `is_view=true` surface with `knowledge_owner=true`, and no compatibility/legacy-route collision.

Call it from `main()` after `validate_rooms()`.

- [ ] **Step 2: Verify RED**

```bash
python scripts/validate_house_governance.py
```

Expected: FAIL for missing public-surface schema/registry.

- [ ] **Step 3: Create public-surface schema**

Create `schemas/house-public-surface-registry.schema.json` requiring root fields:

```text
version, updated, authority, room_registry, primary_gateway_ids,
secondary_global_ids, surfaces
```

Use `authority: "public-route-identity"`, `room_registry: "data/house/rooms.json"`, surface type enum `home|hub|subject|guide|explorer|evidence`, status enum `active|compatibility|retired`, visibility enum `primary|secondary|specialist|compatibility`, `knowledge_owner: false`, and unique `legacy_routes`.

- [ ] **Step 4: Create exact initial surface registry**

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

Populate exactly these fourteen surfaces:

```text
home          /                         home      parent=null
tim           /tim-dooley/              hub       parent=home
religion      /religion/                hub       parent=home
philosophy    /philosophy/              hub       parent=home
science       /science/                 hub       parent=home
world         /world/                   hub       parent=home
timeline      /timeline/                explorer  parent=home      legacy=/chronology/
explore       /explore/                 explorer  parent=home
sources       /context/source-authority/ evidence parent=home
world-map     /world-map/               explorer  parent=world     legacy=/world-map/3d.html
politics      /politics/                guide     parent=world
north         /north/                   guide     parent=world
world-systems /world-systems/           guide     parent=world
bible         /traditions/bible/        explorer  parent=religion  legacy=/religion/jesus-tim/
```

Use the approved Room memberships from the Wave 1 design/roadmap; `explore` may reference all ten Rooms. Set every row `status: "active"`, `knowledge_owner: false`, and `route == canonical_route` in Wave 1.

- [ ] **Step 5: Verify GREEN**

```bash
python scripts/validate_house_governance.py
```

Expected: PASS for Room and public-surface contracts.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_house_governance.py schemas/house-public-surface-registry.schema.json data/house/public-surfaces.json
git commit -m "architecture: add public surface registry"
```

---

### Task 3: Route Topology Ledger and Compatibility Pointers

**Files:**
- Modify: `scripts/validate_house_governance.py`
- Create: `knowledge/research/potato-house-master/public-route-topology.json`
- Modify: `data/frontend-atlas-bridge.json`
- Modify: `data/backend-coverage-map.json`
- Modify: `data/atlas-manifest.json`

**Interfaces:**
- Consumes: Room/surface IDs from Tasks 1–2.
- Produces: topology classification for the fourteen major public surfaces plus explicit pointers from existing compatibility contracts to House authority.

- [ ] **Step 1: Add failing topology/migration checks**

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

Implement `validate_topology(errors, rooms, surfaces)` and `validate_migration_pointers(errors)` to check exact surface order, matching route/surface type/Room set, valid hub IDs, and these exact pointers:

```text
frontend-atlas-bridge.json:
  authority_status = branch-and-backend-family-projection-compatibility
  room_registry = data/house/rooms.json
  public_surface_registry = data/house/public-surfaces.json

backend-coverage-map.json:
  room_contract = data/house/rooms.json
  public_surface_contract = data/house/public-surfaces.json

atlas-manifest.json:
  house_rooms = data/house/rooms.json
  public_surfaces = data/house/public-surfaces.json
```

- [ ] **Step 2: Verify RED**

```bash
python scripts/validate_house_governance.py
```

Expected: FAIL for missing topology and migration pointers.

- [ ] **Step 3: Create topology ledger**

Create `knowledge/research/potato-house-master/public-route-topology.json` with one record per `EXPECTED_MAJOR_SURFACES`, in exact order. Each record has:

```text
surface_id
surface_type
canonical_route
primary_hub_id
room_ids
specialist_view
migration_status = current
compatibility_routes
```

Hub rules:

```text
home -> null
five primary hubs -> self
timeline/explore/sources -> null
world-map/politics/north/world-systems -> world
bible -> religion
```

Set `specialist_view=true` initially for Timeline, Explore, Sources, World Map, Bible; Guides remain false.

- [ ] **Step 4: Add migration pointers without deleting current data**

Add the fields above to `data/frontend-atlas-bridge.json`, `data/backend-coverage-map.json`, and `data/atlas-manifest.json`. Preserve existing `public_doors`, branch projection, backend-family projection, route map, resolution/fallback rules, coverage data, and manifest descriptions.

- [ ] **Step 5: Verify House + current ownership/projection contracts**

```bash
python scripts/validate_house_governance.py
python scripts/validate_public_projection.py
python scripts/audit_source_of_truth.py
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_house_governance.py knowledge/research/potato-house-master/public-route-topology.json data/frontend-atlas-bridge.json data/backend-coverage-map.json data/atlas-manifest.json
git commit -m "architecture: map House route topology"
```

---

### Task 4: Normalize World as the Fifth Public Hub Everywhere

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
- Consumes: primary-gateway contract from Task 2.
- Produces: one stable rule from source through deployment: fifth primary destination is `/world/`; `/world-map/` remains only where the map is intentionally the specialist destination.

- [ ] **Step 1: Add failing route-drift checks**

Extend `scripts/validate_house_governance.py` with:

```python
PRIMARY_PEER_NAV_FILES = (
    "tim-dooley/index.html", "religion/index.html",
    "philosophy/index.html", "science/index.html",
)

def first_nav(text: str) -> str:
    match = re.search(r"<nav\\b[^>]*>(.*?)</nav>", text, flags=re.I | re.S)
    return match.group(1) if match else ""

def validate_primary_world_routing(errors: list[str]) -> None:
    for rel in PRIMARY_PEER_NAV_FILES:
        nav = first_nav((ROOT / rel).read_text(encoding="utf-8"))
        if 'href="../world/"' not in nav:
            errors.append(f"{rel} primary peer nav must link to ../world/")
        if 'href="../world-map/"' in nav:
            errors.append(f"{rel} primary peer nav must not use World Map as fifth peer")
    patch = (ROOT / "scripts" / "patch_home_discovery.py").read_text(encoding="utf-8")
    if "GITHUB_WORKFLOW" in patch and "world-map/" in patch and 'href="world/"' in patch:
        errors.append("patch_home_discovery.py must not rewrite canonical World for deploy compatibility")
    shell = (ROOT / "scripts" / "validate_site_shell.py").read_text(encoding="utf-8")
    if "restore_canonical_world_route" in shell:
        errors.append("validate_site_shell.py must validate rather than mutate built World routing")
```

Call it from `main()`.

- [ ] **Step 2: Verify RED on known drift**

```bash
python scripts/validate_house_governance.py
```

Expected: FAIL on the four peer-nav files and any deploy-time repair/rewrite still present.

- [ ] **Step 3: Fix only the four primary peer-nav links**

In the first nav of each file, use:

```html
<a href="../world/">World</a>
```

Do not remove contextual links to World Map elsewhere.

- [ ] **Step 4: Remove deploy-only World→World Map mutation**

In `scripts/patch_home_discovery.py`, delete only the workflow-specific block that changes homepage `world/` to `world-map/`. Remove `import os` only if unused afterward. Preserve all unrelated discovery, North, Map, sitemap, and machine-index patching.

- [ ] **Step 5: Make site-shell validation non-mutating**

In `scripts/validate_site_shell.py`, delete `restore_canonical_world_route()` and its invocation. Keep the canonical Home-link assertion ending in `world/`.

- [ ] **Step 6: Fix Pages deployment smoke expectations**

In `.github/workflows/pages.yml`:

```bash
test -f _site/world/index.html
grep -q 'href="world/"' _site/index.html
```

and use:

```python
expected = ['tim-dooley/','religion/','philosophy/','science/','world/']
```

Preserve separate checks proving World Map still exists and works.

- [ ] **Step 7: Verify source + built artifact**

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

Expected: all PASS and `_site/index.html` still contains `href="world/"` after patching.

- [ ] **Step 8: Commit**

```bash
git add scripts/validate_house_governance.py tim-dooley/index.html religion/index.html philosophy/index.html science/index.html scripts/patch_home_discovery.py scripts/validate_site_shell.py .github/workflows/pages.yml
git commit -m "fix: make World the stable fifth public hub"
```

---

### Task 5: CI Authority, Documentation, and Exact-Artifact Gate

**Files:**
- Modify: `.github/workflows/quality-checks.yml`
- Modify: `.github/workflows/pages.yml`
- Modify: `docs/ROOT-NAVIGATION-ARCHITECTURE.md`
- Modify: `docs/PROJECT-STRUCTURE.md`
- Modify: `docs/superpowers/specs/2026-09-13-potato-house-public-crystallization-design.md`
- Modify: `docs/superpowers/specs/2026-09-13-potato-house-six-wave-roadmap.md`

**Interfaces:**
- Consumes: governance validator and contracts from Tasks 1–4.
- Produces: quality/deploy gates and docs that agree on one authority hierarchy.

- [ ] **Step 1: Wire governance validation into both workflows**

Add to `.github/workflows/quality-checks.yml` after the source-of-truth/route audit:

```yaml
      - name: Validate Potato House governance
        run: python scripts/validate_house_governance.py
```

Add the same step to `.github/workflows/pages.yml` before build/discovery work.

- [ ] **Step 2: Mark old Root Navigation as historical / Explore UX donor**

At the top of `docs/ROOT-NAVIGATION-ARCHITECTURE.md`, set status to:

```text
historical architecture / Explore UX donor; superseded as whole-site and homepage authority
```

State current authority as `docs/POTATO-HOUSE-CONSTITUTION.md` + `data/house/public-surfaces.json`, and preserve the remainder as architectural history.

- [ ] **Step 3: Update Project Structure authority language**

In `docs/PROJECT-STRUCTURE.md`, state:

```text
Stable public route identity is owned by data/house/public-surfaces.json.
Bounded semantic governance is owned by data/house/rooms.json.
manifest.json remains relationship-first branch/pathway mapping.
data/frontend-atlas-bridge.json remains Wave 1 branch/backend projection compatibility.
```

Add canonical-ownership rows for Public route identity and Domain Room governance.

- [ ] **Step 4: Record implementation authorization state**

Update umbrella design status to:

```text
Status: approved architecture; Wave 1 implementation authorized
```

Update roadmap status to:

```text
Status: approved companion roadmap; execute sequentially, one planned wave at a time
```

Do not mark Waves 2–6 implementation-complete or implementation-authorized by this text alone.

- [ ] **Step 5: Run focused architecture checks**

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

- [ ] **Step 6: Run the deploy-tail sequence**

Run the repository-equivalent tail in this order:

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

Then assert the exact final artifact:

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

Do not add an artifact repair if this fails; fix the source/build consumer that created drift.

- [ ] **Step 7: Run the repository quality workflow locally where practical**

Run every Python validator/build command currently listed in `.github/workflows/quality-checks.yml` that does not require external network downloads, then:

```bash
git diff --check
git status --short
```

Expected: no whitespace errors and only intended Wave 1 changes.

- [ ] **Step 8: Commit**

```bash
git add .github/workflows/quality-checks.yml .github/workflows/pages.yml docs/ROOT-NAVIGATION-ARCHITECTURE.md docs/PROJECT-STRUCTURE.md docs/superpowers/specs/2026-09-13-potato-house-public-crystallization-design.md docs/superpowers/specs/2026-09-13-potato-house-six-wave-roadmap.md
git commit -m "docs: finalize Potato House Wave 1 authority"
```

---

## Wave 1 Completion Gate

Before claiming Wave 1 complete, verify all of the following at the exact execution-branch head:

- `data/house/rooms.json` has exactly ten canonical Rooms in approved order.
- `data/house/public-surfaces.json` has exactly the fourteen initial major surfaces.
- Five primary gateway IDs are exactly Tim, Religion, Philosophy, Science, World.
- World Map is a specialist Explorer under World.
- Politics, North, World Systems are specialist World-family surfaces.
- Timeline, Explore, Sources are secondary/global surfaces rather than Home peers.
- All Room references and parent references resolve.
- Topology records agree with public-surface authority.
- Existing bridge/coverage/atlas contracts point to the new registries without losing their compatibility roles.
- Tim, Religion, Philosophy, Science peer nav use World, not World Map.
- Contextual World Map links remain where intentionally map-specific.
- `patch_home_discovery.py` no longer rewrites World to World Map.
- `validate_site_shell.py` no longer mutates the built Home into compliance.
- Pages smoke tests expect `world/` as the fifth entrance.
- House governance validation runs in both quality and deploy workflows.
- Root Navigation is clearly historical/Explore-specific.
- Project Structure names House route/Room authority correctly.
- `index.html` is not visually redesigned.
- No new runtime dependency was added.
- No knowledge owner was moved merely to satisfy navigation.
- Existing projection, Explore, discovery, source-of-truth, and site-shell checks remain green.
- Exact `_site/index.html` retains `/world/` after all post-build scripts.

## Explicitly Deferred to Later Waves

Do not pull these into Wave 1:

- generated Related/History/Sources/Broader/Explore-further blocks;
- subject-level topology for thalamus, Denmark, companies, passages, equations or creative works;
- crystallization/readiness/Gardener queues;
- lifecycle promotion;
- automatic public page generation;
- Explore redesign or Tree/Yggdrasil/Root visualization;
- deeper Timeline/World Map/Bible canonical-ID migration;
- homepage Start-here redesign;
- mass migration/deletion of manifest or frontend-bridge consumers;
- deletion of legacy architecture/provenance files.

Wave 1 ends when governance and routing authority are explicit, validated, deploy-consistent, and boring enough that Wave 2 can build on them safely.
