# World Map Auditor — Design Specification

Date: 2026-09-15
Status: design-approved in chat; implementation not started
Scope: canonical `world-map/` runtime and its CI contracts

## 1. Purpose

The World Map already has many strong specialized validators: ownership, source/runtime contracts, UI shell/layout, render stack, physical layers, subdivisions, Places budgets, search races, browse/hover regressions, spatial overlays, Palestine geometry, Path, investigation surfaces, and entity-aware Trace. These validators protect local invariants well, but they do not provide one whole-system answer to the recurring question:

> Who owns every mutable map resource, what lifecycle does it follow, where can two modules collide, and which collisions are most likely to produce visual or interaction artifacts?

The World Map Auditor adds that missing systems view. It is a static architecture auditor first. It inventories active map modules, normalizes the mutable resources they touch, compares actual usage against an explicit ownership contract, scores risks, emits a machine-readable report, and fails CI only on high-confidence architectural violations.

It does not replace existing validators. Existing validators remain authoritative for their specialist domain. The auditor links those domains into one ownership and lifecycle graph.

## 2. Goals

The auditor must:

1. Inventory active World Map runtime modules under `world-map/3d-*.js` while excluding archived copies and compatibility-only routes.
2. Detect and record ownership of:
   - MapLibre sources;
   - MapLibre layers;
   - render-stack registrations;
   - feature-state keys;
   - paint-property writes;
   - layout-property writes;
   - source `setData` writes;
   - map event listeners;
   - window/document event listeners;
   - MapLibre popup creation and transient hover markup;
   - style restoration hooks;
   - URL query-state keys;
   - top-level public `window.__potatoAtlas*` APIs;
   - DOM IDs created by JavaScript.
3. Distinguish intentional shared ownership from accidental multiple writers through a checked-in contract.
4. Detect likely artifact-producing conditions before they become visible regressions.
5. Produce deterministic JSON output suitable for CI artifacts and later runtime/browser augmentation.
6. Keep the first version static, fast, dependency-light, and runnable with repository Python only.
7. Provide enough evidence in every finding to make the next hardening wave actionable without rediscovering the architecture manually.

## 3. Non-goals

Version 1 will not:

- perform screenshot comparison;
- launch a browser;
- monkey-patch MapLibre at runtime;
- replace end-to-end interaction tests;
- infer dynamic IDs that cannot be resolved statically with confidence;
- fail CI merely because a module is complex or has multiple legitimate responsibilities;
- force all mutable behavior through one giant coordinator.

Runtime instrumentation and visual scenario testing are future layers that will consume the same report/contract vocabulary.

## 4. Architecture

### 4.1 Components

The subsystem has three durable artifacts.

#### `scripts/audit_world_map.py`

The scanner and rule engine. It walks canonical World Map JavaScript, extracts known mutation and ownership patterns, normalizes them into records, applies the ownership contract, computes findings and risk summaries, writes a JSON report, prints a concise console summary, and returns a non-zero exit code only when blocking errors exist.

#### `data/world-map-audit-contract.json`

The declarative source of intentional architecture exceptions and explicit owners. The contract prevents the Python scanner from becoming a pile of one-off hard-coded exemptions.

It records:

- canonical resource owners;
- explicitly shared feature-state keys or mutable resources;
- modules allowed to participate in style restoration;
- known compatibility aliases;
- transient-popup conventions;
- ignored generated/dynamic patterns with rationale;
- severity overrides only where justified.

Every exception must include a human-readable rationale. The contract is architecture documentation, not a suppression dump.

#### `world-map-audit-report.json`

Generated at repository root during validation. It is not required to be committed. CI uploads it as an artifact.

Top-level shape:

```json
{
  "schema_version": "1.0",
  "generated_at": "ISO-8601",
  "scope": "world-map",
  "summary": {
    "modules": 0,
    "resources": 0,
    "errors": 0,
    "warnings": 0,
    "notes": 0,
    "risk_score": 0
  },
  "inventory": {},
  "ownership": {},
  "findings": [],
  "risk_domains": {},
  "next_actions": []
}
```

The JSON key order and list ordering must be deterministic except for `generated_at`.

### 4.2 Data flow

1. Discover canonical `world-map/3d-*.js` modules.
2. Read each file once.
3. Run a bounded set of extractors over each source string.
4. Normalize matches into typed inventory records.
5. Group records by resource identity.
6. Apply contract owners/exceptions.
7. Run collision and lifecycle rules.
8. Score findings and domains.
9. Emit JSON report.
10. Print a compact summary and actionable top findings.
11. Exit `1` only when severity `error` findings exist; otherwise exit `0`.

## 5. Canonical inventory model

Every extracted record should use a common envelope:

```json
{
  "kind": "feature_state_write",
  "resource": "countries:selected",
  "module": "world-map/3d-country-selection.js",
  "operation": "setFeatureState",
  "line": 123,
  "confidence": "high",
  "details": {}
}
```

`confidence` is one of `high`, `medium`, `low`.

Only high-confidence records may independently create a blocking error in v1. Medium-confidence records may contribute to warnings. Low-confidence records are inventory-only unless corroborated by another signal.

### 5.1 Resource identities

Use stable normalized identities:

- source: `source:<source-id>`
- layer: `layer:<layer-id>`
- render-stack registration: `render-stack:<layer-id>`
- feature state: `feature-state:<source-id>:<key>`
- paint writer: `paint:<layer-id>:<property>`
- layout writer: `layout:<layer-id>:<property>`
- source data writer: `set-data:<source-id>`
- map listener: `map-event:<event>:<layer-id-or-global>`
- DOM/window listener: `dom-event:<target>:<event>`
- popup: `popup:<module>:<ordinal>`
- URL state: `url:<query-key>`
- public API: `api:<window-property>`
- DOM surface: `dom:<element-id>`
- style restoration participant: `style-restore:<module>`

## 6. Extraction strategy

Version 1 deliberately uses conservative static scanning rather than a JavaScript parser dependency. The repository already uses recognizable literal patterns. Extractors should target only patterns whose resource identity can be resolved reliably.

High-confidence examples:

- `map.addSource('literal-id', ...)`
- `map.addLayer({ id:'literal-id', ... })`
- `map.removeSource('literal-id')`
- `map.removeLayer('literal-id')`
- `map.setFeatureState({ source:'literal-id', ... }, { literalKey: ... })`
- `map.setPaintProperty('literal-layer', 'literal-property', ...)`
- `map.setLayoutProperty('literal-layer', 'literal-property', ...)`
- `map.getSource('literal-id')?.setData(...)`
- `map.on('literal-event', 'literal-layer', ...)`
- `map.on('styledata', ...)`
- `renderStack.register('literal-layer', { ... })`
- `new maplibregl.Popup(...)`
- `searchParams.set('literal-key', ...)`
- `searchParams.delete('literal-key')`
- `window.__potatoAtlasName = ...`
- `element.id = 'literal-id'`

Dynamic expressions are recorded only when a stable prefix or constant can be resolved without executing code.

The scanner must retain file and line evidence for every match.

## 7. Ownership contract

`data/world-map-audit-contract.json` uses this conceptual structure:

```json
{
  "schema_version": "1.0",
  "owners": {
    "feature-state:countries:selected": ["world-map/3d-country-selection.js"]
  },
  "shared": {
    "resource-id": {
      "modules": ["..."],
      "rationale": "Why this is intentionally shared"
    }
  },
  "style_restoration": {
    "allowed_modules": {
      "world-map/3d-render-stack.js": "canonical z-order reconciliation"
    }
  },
  "conventions": {
    "transient_popup_class": "atlas-hover"
  },
  "ignore": {
    "patterns": []
  }
}
```

The implementation may refine field names, but the semantics above are fixed.

Contract rules:

1. A resource named under `owners` must not gain another high-confidence writer unless also declared under `shared`.
2. Shared resources require at least two named modules and a non-empty rationale.
3. Ignore rules require a non-empty rationale and should be as narrow as possible.
4. Contract entries referring to modules or literal resources that no longer exist produce warnings so stale suppressions cannot silently accumulate.

## 8. Rule set

### 8.1 Blocking errors

Version 1 should fail CI on these high-confidence conditions:

1. **Duplicate source creation** — the same literal source ID is created by more than one active module without an explicit shared declaration.
2. **Duplicate layer creation** — the same literal layer ID is created by more than one active module without an explicit shared declaration.
3. **Feature-state ownership collision** — the same literal source/key pair has multiple writers and the contract does not explicitly allow it.
4. **Conflicting canonical paint ownership** — the same literal layer/property has multiple modules writing it when the contract declares a single owner.
5. **Conflicting canonical layout ownership** — same principle for layout properties.
6. **Transient popup convention violation** — a popup used from hover-style map events renders transient markup without the canonical `.atlas-hover` class, because the Wave 4 drag guard cannot suppress it reliably.
7. **Unknown render-stack slot registration** — if a literal registration can be resolved and uses a slot outside the coordinator contract.
8. **Broken contract reference** where an explicitly declared canonical owner module is absent.

### 8.2 Warnings

Warnings identify likely wonkiness without blocking until the architecture is understood or migrated:

1. multiple `styledata` restoration participants;
2. style-restoring modules with no visible reentrancy/scheduling guard marker;
3. layer created but not registered with the render stack when its layer family is expected to participate;
4. source/layer remove operations owned by a different module than creation;
5. multiple `setData` writers for one source;
6. global map listeners installed by more than one module for the same event/layer combination;
7. popup creation outside known interaction modules;
8. URL query key written by multiple modules;
9. DOM ID created by multiple modules;
10. public `window.__potatoAtlas*` API assigned by multiple modules;
11. contract exception that no longer matches inventory;
12. mutable map resource whose owner cannot be confidently resolved.

Warnings must include remediation language rather than only counts.

### 8.3 Notes

Notes provide useful architecture inventory without implying defects, including:

- total sources/layers/listeners/popups;
- modules with the largest mutation surface;
- all style restoration participants;
- all feature-state keys grouped by source;
- all render-stack slots and registrants;
- all URL state keys;
- all transient popup owners.

## 9. Risk scoring

The report includes both finding severity and an advisory risk score. CI pass/fail is based on errors, never on score alone.

Per finding weights:

- error: 10
- warning: 3
- note: 0

Domain score is the sum of weights for findings in that domain. Overall risk score is the sum capped at 100.

Risk domains:

- `render_ownership`
- `feature_state`
- `style_lifecycle`
- `event_lifecycle`
- `popup_interaction`
- `data_mutation`
- `url_state`
- `dom_ownership`

`next_actions` are derived deterministically from the highest domain scores and highest-severity findings. They are recommendations, not automatic code changes.

## 10. CI integration

Add a dedicated quality step immediately after `Validate canonical World Map runtime` and before UI/layout/spatial checks:

```yaml
- name: Audit World Map runtime architecture
  id: world_map_audit
  continue-on-error: true
  run: python scripts/audit_world_map.py

- name: Upload World Map audit report
  if: ${{ always() && hashFiles('world-map-audit-report.json') != '' }}
  uses: actions/upload-artifact@v4
  with:
    name: world-map-audit-report
    path: world-map-audit-report.json
    if-no-files-found: error
    retention-days: 7

- name: Enforce World Map audit gate
  if: steps.world_map_audit.outcome == 'failure'
  run: exit 1
```

Using `continue-on-error` for the audit step ensures the report is uploaded before CI enforces failure.

The auditor itself must complete quickly enough that it does not materially change the existing quality workflow runtime.

## 11. Compatibility with existing validators

The auditor must not duplicate specialist logic unnecessarily.

Existing validators remain responsible for:

- exact render-stack ordering behavior;
- subdivision and Places memory budgets;
- hover async race behavior;
- drag suppression behavior;
- map-state reset semantics;
- hydrology request deduplication;
- UI placement ownership;
- investigation-surface arbitration;
- path/trace correctness;
- geometry-specific contracts.

The auditor inventories ownership and cross-module lifecycle relationships around those systems. Where possible, report entries should name the specialist validator relevant to the finding.

## 12. Testing strategy

Implementation follows TDD.

### 12.1 Scanner fixture tests

Create small fixture JavaScript files under a test fixture directory or generate them in the test process. Tests must prove extraction for:

- sources;
- layers;
- feature-state keys;
- paint/layout writers;
- `setData` writers;
- listeners;
- popups;
- styledata hooks;
- URL keys;
- public APIs;
- DOM IDs.

### 12.2 Rule tests

Tests must prove:

- duplicate source/layer owners fail;
- duplicate feature-state writers fail unless declared shared;
- stale contract entries warn;
- transient hover popup without `.atlas-hover` fails;
- style restoration multiplicity warns rather than fails initially;
- deterministic ordering of findings and inventory.

### 12.3 Repository integration test

Run the auditor against the live `world-map/` tree. Initial implementation is allowed to surface warnings, but before merge there must be zero uncontracted blocking errors.

The first live report becomes the input to the next hardening wave.

## 13. First expected hardening target

The first follow-on work after the auditor lands is feature-state and style-lifecycle convergence.

Why:

- multiple modules currently write distinct state keys into the shared `countries` source;
- country selection also owns direct line paint changes;
- Chain, Impact, Lenses and scalar/compositor systems contribute other feature-state values;
- multiple physical modules independently listen to `styledata` and restore resources;
- the render-stack coordinator independently reacts to `styledata` to restore ordering.

These patterns can be valid, but the auditor should make the ownership explicit and expose collisions or restoration races. The next wave should be chosen from the highest-confidence findings in the generated report, not from guesswork.

## 14. Future extension points

The report schema intentionally supports two later layers without redesigning v1:

### Runtime instrumentation

A development-only browser harness can instrument MapLibre calls and emit runtime records using the same resource identities. Static and runtime inventories can then be diffed.

### Scenario/visual audit

A browser test can execute canonical scenarios such as drag, zoom, select, pin, enable/disable layers, style reload, reset, and historical mode. It can record resource counts and screenshots while attaching failures to the same risk domains.

Neither extension is required for v1.

## 15. Success criteria

The first implementation is complete when:

1. `python scripts/audit_world_map.py` produces a valid deterministic report from the live repository.
2. Every high-confidence literal source/layer/feature-state writer is represented in inventory.
3. Intentional shared ownership is explicit in `data/world-map-audit-contract.json`.
4. The live map has zero uncontracted blocking audit errors.
5. CI always uploads the report and fails only after upload when blocking errors exist.
6. Existing World Map validators remain green.
7. The report identifies and ranks at least the feature-state and style-lifecycle domains so the next hardening wave can be selected from evidence.

## 16. Design decision summary

Choose a static whole-map architecture auditor first, backed by a declarative ownership contract and deterministic JSON report. Keep existing specialist validators. Use the auditor as the cross-system radar that reveals ownership collisions, stale lifecycle hooks, and likely artifact risks. Add runtime and visual auditing later against the same vocabulary rather than introducing a second architecture.