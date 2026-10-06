# World Map Auditor — Design Specification

Date: 2026-09-15
Status: approved for implementation
Scope: canonical `world-map/` runtime and CI contracts

## Purpose

Add a static whole-map architecture auditor above the existing specialist validators. The auditor must answer who owns every mutable map resource, where ownership is intentionally shared, where modules collide, and which lifecycle patterns are most likely to produce visual or interaction artifacts. Existing validators remain authoritative for their specialist behavior.

## Durable artifacts

- `scripts/audit_world_map.py` — static scanner/rule engine.
- `data/world-map-audit-contract.json` — explicit owners, intentional sharing, conventions and narrow exceptions with rationale.
- `world-map-audit-report.json` — generated deterministic machine-readable report; not committed; uploaded by CI.

## Inventory

Scan canonical `world-map/3d-*.js` modules and inventory high-confidence literal usage of:

- MapLibre sources and layers;
- render-stack registrations;
- feature-state keys;
- paint/layout mutations;
- source `setData` writes;
- map and DOM/window listeners;
- MapLibre popups and transient hover markup;
- `styledata` restoration participants;
- URL query-state keys;
- top-level `window.__potatoAtlas*` APIs;
- JavaScript-created DOM ids.

Every record carries `kind`, normalized `resource`, `module`, `operation`, `line`, `confidence`, and `details`.

Stable resource identities include:

- `source:<id>`
- `layer:<id>`
- `render-stack:<layer-id>`
- `feature-state:<source-id>:<key>`
- `paint:<layer-id>:<property>`
- `layout:<layer-id>:<property>`
- `set-data:<source-id>`
- `map-event:<event>:<layer-or-global>`
- `dom-event:<target>:<event>`
- `popup:<module>:<ordinal>`
- `url:<key>`
- `api:<window-property>`
- `dom:<element-id>`
- `style-restore:<module>`

## Extraction strategy

Use conservative static scanning with Python only. High-confidence matches must resolve literal resource identities such as `addSource('id')`, `addLayer({id:'id'})`, `setFeatureState({source:'id'}, {key:...})`, `setPaintProperty('layer','prop')`, `setLayoutProperty('layer','prop')`, `getSource('id').setData`, `map.on('event','layer')`, `map.on('styledata')`, render-stack registrations, `new maplibregl.Popup`, literal search-param keys, `window.__potatoAtlas*` assignments, and literal DOM ids. Dynamic expressions are inventory-only unless safely resolvable.

## Contract semantics

`data/world-map-audit-contract.json` declares:

- canonical owners;
- intentionally shared resources with named modules and rationale;
- allowed style-restoration participants with rationale;
- transient popup class convention (`atlas-hover`);
- narrowly scoped ignores with rationale.

Stale contract entries must warn so suppressions cannot accumulate silently.

## Blocking errors

Only high-confidence findings may independently fail CI in v1:

1. duplicate literal source creation without explicit sharing;
2. duplicate literal layer creation without explicit sharing;
3. duplicate feature-state source/key writers without explicit sharing;
4. paint or layout writers contradicting a declared canonical owner;
5. transient hover popup lacking `.atlas-hover` and therefore escaping the drag suppression contract;
6. literal render-stack slot outside the known coordinator slots;
7. declared canonical owner module absent from the repository.

## Warnings

Warnings do not fail CI in v1. They include:

- multiple `styledata` restoration participants;
- restoration participants with no visible guard/scheduling marker;
- layers expected to participate in render order but lacking registration;
- source/layer removal owned separately from creation;
- multiple `setData` writers;
- repeated listener ownership;
- popup creation outside known interaction modules;
- multiple URL-key writers;
- multiple DOM-id creators;
- duplicate public API assignment;
- stale contract exceptions;
- unresolved mutable-resource ownership.

Every warning must include evidence and remediation language.

## Risk report

Top-level report keys:

```json
{
  "schema_version":"1.0",
  "generated_at":"ISO-8601",
  "scope":"world-map",
  "summary":{"modules":0,"resources":0,"errors":0,"warnings":0,"notes":0,"risk_score":0},
  "inventory":{},
  "ownership":{},
  "findings":[],
  "risk_domains":{},
  "next_actions":[]
}
```

All ordering must be deterministic except `generated_at`.

Weights are advisory only: error=10, warning=3, note=0; total risk capped at 100. Domains: `render_ownership`, `feature_state`, `style_lifecycle`, `event_lifecycle`, `popup_interaction`, `data_mutation`, `url_state`, `dom_ownership`. Pass/fail depends on blocking errors, never score.

## CI integration

Add an audit step immediately after `Validate canonical World Map runtime`, run it with `continue-on-error`, upload `world-map-audit-report.json` with `actions/upload-artifact@v4` under `always()`, then enforce failure if the audit step failed. This guarantees a report is retained even on blocking findings.

## TDD requirements

Scanner tests must prove extraction of sources, layers, feature state, paint/layout, `setData`, listeners, popups, style hooks, URL keys, public APIs and DOM ids. Rule tests must prove duplicate source/layer and feature-state collisions fail, sharing can allow intentional collisions, stale contract entries warn, transient hover popup convention is enforced, style restoration multiplicity warns, and output ordering is deterministic.

The first live report may contain warnings, but before merge it must contain zero uncontracted blocking errors.

## First follow-on target

After the auditor lands, choose the next hardening work from the report. The expected highest-value domains are feature-state ownership and style lifecycle because multiple systems mutate the shared country surface and several physical modules independently restore after style changes. Do not patch these based on expectation alone; use the audit evidence.

## Non-goals for v1

No browser launch, screenshot diffing, MapLibre monkey-patching, runtime instrumentation, or replacement of existing specialist validators. Runtime and visual scenario auditors are later extensions using the same resource vocabulary.