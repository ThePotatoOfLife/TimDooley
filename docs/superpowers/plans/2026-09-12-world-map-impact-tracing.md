# World Map Dependency Impact Tracing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bounded evidence-first “What breaks?” trace that follows explicit directed dependencies for two hops, preserves structured dependency facts, exposes documented alternatives/context, and never converts generic connectivity into causality.

**Architecture:** Add one focused Python impact module that owns dependency extraction, target resolution, impact-graph generation and a pure directional trace helper. `build_world_map_runtime.py` projects that graph into the existing generated runtime without changing the 195-country model. A focused `3d-impact-trace.js` module extends the shared browser runtime with impact APIs, renders one contextual panel, and uses a dedicated feature-state outline channel. Existing card/gateway/chain modules only provide entry points; they do not duplicate traversal logic.

**Tech Stack:** Python runtime generation/validation, JSON canonical data owners, MapLibre GL JS feature-state layers, existing World Map runtime API, GitHub Actions canonical quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-12-world-map-impact-tracing-design.md`

## Global Constraints

- Dependency edges point `dependent -> dependency`; impact queries traverse incoming causal edges.
- Browser traversal depth is exactly 2 for this wave.
- Country count stays exactly 195; territories remain separate entities.
- Generic curated relationships, chain membership and gateway-country association never become causal dependency edges by themselves.
- Missing dependency evidence means “not represented”, not “no real-world dependency”.
- No `impact_score`, `risk_score`, `resilience_score`, `collapse_score`, probability or economic-loss forecast.
- No permanent top-level Impact button or new toolbox.
- Existing shortest-path behavior remains separate and unchanged.

---

### Task 1: Define the failing impact contract

**Files:**
- Create: `scripts/validate_world_map_impact_trace.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Validator imports `scripts/world_map_impact.py` when present.
- CI gate: `Validate World Map dependency impact trace`.

- [ ] **Step 1: Write the directional regression fixture first**

The validator must require a pure helper:

```python
trace_incoming_impact(nodes, edges, root_id, max_depth=2)
```

and run this fixture:

```python
nodes = {
    "country:A": {"id":"country:A","kind":"country","label":"A"},
    "country:B": {"id":"country:B","kind":"country","label":"B"},
    "country:C": {"id":"country:C","kind":"country","label":"C"},
    "country:D": {"id":"country:D","kind":"country","label":"D"},
}
edges = [
    {"source":"country:A","target":"country:B","relationship":"depends-on","causal_status":"explicit-dependency"},
    {"source":"country:C","target":"country:A","relationship":"depends-on","causal_status":"explicit-dependency"},
    {"source":"country:D","target":"country:B","relationship":"connected-to","causal_status":"contextual-association"},
]
result = trace_incoming_impact(nodes, edges, "country:B", max_depth=2)
assert [row["node"]["id"] for row in result["direct"]] == ["country:A"]
assert [row["node"]["id"] for row in result["second_order"]] == ["country:C"]
assert "country:D" not in {row["node"]["id"] for row in result["direct"] + result["second_order"]}
```

- [ ] **Step 2: Add runtime contract assertions**

Require:

```python
runtime["country_count"] == 195
runtime["impact"]["policy"]["max_browser_depth"] == 2
runtime["impact"]["policy"]["score_policy"] == "no aggregate impact score inferred"
"country:AND" in runtime["impact"]["nodes"]
"territory:GRL" in runtime["impact"]["nodes"]
```

Every edge must have `source`, `target`, `relationship`, `causal_status`, and both endpoints must exist.

Require at least one Andorra edge preserving:

```text
France and Spain road access
physical trade, tourism and labour mobility
critical
```

Require at least one unresolved dependency-concept node, proving string/structured dependencies are not discarded merely because they cannot be mapped geographically.

- [ ] **Step 3: Add causal guardrails**

Reject runtime/source patterns that bulk-promote:

```text
world-relational-map curated_edges -> depends-on
chain members -> depends-on
gateway countries -> depends-on
```

Reject forbidden score fields anywhere in the impact plane.

- [ ] **Step 4: Add browser contract assertions**

Require:

```text
world-map/3d-impact-trace.js
impactNode(id)
impactFor(id)
impactNodeForEntity(code)
impactNodeForGateway(id)
impactNodeForChain(id)
atlas-impact-outline
atlasImpactRoot
atlasImpactDirect
atlasImpactSecond
Directly exposed
Second-order
Known alternatives
Context
searchParams.get('impact')
searchParams.set('impact'
represented dependencies, not a forecast
```

Require bootstrap loads `./3d-impact-trace.js` after functional chains. Require World Bar does not contain a top-level Impact control.

- [ ] **Step 5: Wire the gate into the canonical workflow**

Add `node --check world-map/3d-impact-trace.js` to the existing JavaScript syntax step and add:

```yaml
      - name: Validate World Map dependency impact trace
        run: python scripts/validate_world_map_impact_trace.py
```

immediately after the functional-chain/entity-system validators.

- [ ] **Step 6: Open the PR and verify RED**

Open a PR from `world-map-impact-tracing-2026-09-12` to `main`. Expected failure is the new impact gate because the helper/runtime/browser feature does not exist yet; all earlier gates should reach/preserve their prior behavior.

- [ ] **Step 7: Commit**

```text
test(world-map): define dependency impact contract
```

---

### Task 2: Build the evidence-first impact graph

**Files:**
- Create: `scripts/world_map_impact.py`
- Modify: `scripts/build_world_map_runtime.py`

**Interfaces:**

```python
dependency_labels(record: dict) -> list[str]
structured_dependency_facts(record: dict, source_code: str) -> list[dict]
build_impact_plane(country_rows, country_records, entities, gateways, chains) -> dict
trace_incoming_impact(nodes: dict, edges: list[dict], root_id: str, max_depth: int = 2) -> dict
```

- [ ] **Step 1: Implement normalization helpers**

Create stable helpers for:

```python
slug(value)
importance_rank(value)
entity_node_id(code, canonical_country)
```

Node ids:

```text
country:AND
territory:GRL
gateway:danish-straits
chain:baltic
dependency:and:france-spain-road-access
```

- [ ] **Step 2: Preserve structured dependency objects**

`dependency_labels(record)` must include labels from both strings and objects:

```python
{"dependency":"imported energy","mechanism":"domestic electricity and fuel supply","importance":"high"}
```

becomes compact label `imported energy` for the current System Role card.

`structured_dependency_facts()` preserves `dependency`, `target`, `mechanism`, `importance`, `source`, `source_url`, `period`, `confidence` when present.

- [ ] **Step 3: Implement exact-only target resolution**

Build exact lookup maps for:

```text
ISO3/entity code
canonical country/entity name
gateway id/label
chain id/label
```

If no exact deterministic resolution exists, create a source-scoped dependency-concept node. Do not fuzzy match.

- [ ] **Step 4: Build graph nodes**

Generate nodes for all 195 countries, registered territories/entities, gateways and chains before dependency edges are resolved.

Territory node example:

```json
{"id":"territory:GRL","kind":"territory","code":"GRL","label":"Greenland"}
```

- [ ] **Step 5: Build causal edges only from explicit dependency evidence**

For each country record dependency fact:

```json
{
  "source":"country:AND",
  "target":"dependency:and:france-spain-road-access",
  "relationship":"depends-on",
  "causal_status":"explicit-dependency",
  "evidence_class":"canonical-country-record",
  "mechanism":"physical trade, tourism and labour mobility",
  "importance":"critical"
}
```

Typed country `relationships` only become causal when their type is in the explicit dependency allowlist.

- [ ] **Step 6: Add contextual chain index without causal edges**

Produce:

```json
"context_chains": {
  "country:DNK": ["chain:baltic", "chain:northern-energy", ...]
}
```

Chain membership must not create `depends-on` edges.

- [ ] **Step 7: Implement the pure incoming traversal helper**

`trace_incoming_impact()` follows only edges with causal status `explicit-dependency` (future-compatible allowlist may include explicit gateway dependency), returns deduplicated direct and second-order rows, excludes root/direct duplicates, and honors `max_depth <= 2` for this wave.

Each result row contains:

```python
{"node": nodes[source_id], "edge": edge, "via": optional_node_id}
```

- [ ] **Step 8: Integrate into runtime builder**

Replace use of `explicit_dependencies(record)` with `dependency_labels(record)` for existing `systems.dependencies`, accumulate country records for impact generation, then add:

```python
runtime["impact"] = build_impact_plane(...)
```

The generated runtime remains the single browser projection; do not commit `world-map-data-runtime.json` by hand.

- [ ] **Step 9: Run the impact validator**

Expected: directional fixture and runtime structure pass; browser checks remain red until Task 4.

- [ ] **Step 10: Commit**

```text
feat(world-map): generate explicit dependency impact graph
```

---

### Task 3: Add explicit documented gateway alternatives

**Files:**
- Modify: `data/world-map-gateways.json`
- Modify: `scripts/world_map_impact.py`

**Interfaces:**
- Gateway owner may expose `alternatives: []` records.
- Alternative edges are non-causal traversal edges and appear only in `impactFor(...).alternatives`.

- [ ] **Step 1: Add only repository-supported alternatives**

For `suez-sumed` and `bab-el-mandeb`, add explicit alternative-route records pointing to `cape-good-hope-route`, using the existing EIA source and wording that the Cape is a rerouting option rather than an equivalent substitute.

Example:

```json
"alternatives":[{
  "target":"cape-good-hope-route",
  "relationship":"alternative-route",
  "status":"rerouting-option",
  "note":"Traffic can reroute around southern Africa when Red Sea/Suez access is disrupted; this does not imply equal distance, cost or capacity.",
  "source":"U.S. Energy Information Administration",
  "source_url":"https://www.eia.gov/outlooks/steo/report/energysecurity/article.php"
}]
```

- [ ] **Step 2: Project alternatives separately**

Generate edges with:

```json
"causal_status":"explicit-alternative"
```

They must never be traversed as direct/second-order affected nodes.

- [ ] **Step 3: Represent Hormuz conservatively**

Do not fabricate a full substitute node. Keep the existing description that alternatives cover only part of normal flows; no `alternative-route` edge is required until a canonical target is explicitly represented.

- [ ] **Step 4: Extend validator**

Require Suez/Bab -> Cape alternatives exist and are not counted by incoming dependency traversal.

- [ ] **Step 5: Commit**

```text
data(world-map): encode documented gateway alternatives
```

---

### Task 4: Add shared browser impact APIs and bounded trace UI

**Files:**
- Create: `world-map/3d-impact-trace.js`
- Modify: `world-map/3d-bootstrap.js`

**Interfaces:**

```js
runtime.impactNode(id)
runtime.impactFor(id)
runtime.impactNodeForEntity(code)
runtime.impactNodeForGateway(id)
runtime.impactNodeForChain(id)
window.__potatoAtlasImpactTrace = { show, showEntity, showGateway, showChain, clear, current }
```

- [ ] **Step 1: Load the module after functional chains**

Bootstrap sequence:

```js
await loadAfterPaint('Functional Chains', './3d-chain-explorer.js');
await loadAfterPaint('Impact Trace', './3d-impact-trace.js');
```

This loads capability without adding a permanent control.

- [ ] **Step 2: Extend the shared runtime API**

Each resolver returns exact ids only:

```js
impactNodeForEntity('DNK') -> 'country:DNK'
impactNodeForEntity('GRL') -> 'territory:GRL'
impactNodeForGateway('danish-straits') -> 'gateway:danish-straits'
impactNodeForChain('baltic') -> 'chain:baltic'
```

`impactFor(id)` builds incoming adjacency only from explicit causal edges, returns max 12 direct and 12 second-order rows plus overflow counts, explicit alternatives and context chains.

- [ ] **Step 3: Implement deterministic ordering**

Order by explicit importance:

```text
critical > high > medium > low > unspecified
```

then node label/id. No computed severity score.

- [ ] **Step 4: Add dedicated map outline layer**

Create `atlas-impact-outline` over the `countries` source using feature-state keys:

```text
atlasImpactRoot
atlasImpactDirect
atlasImpactSecond
```

Root, direct and second-order use distinct non-alarm outline emphasis. Base fills remain untouched.

- [ ] **Step 5: Render one compact result panel**

Panel id: `atlasImpactContext`.

Required headings/text:

```text
Dependency impact
Directly exposed
Second-order
Known alternatives
Context
This traces represented dependencies, not a forecast of real-world failure.
```

Rows expose mechanism/importance only when present. Dependency-concept nodes remain visible even when they have no map geometry.

- [ ] **Step 6: Persist only root state**

Use:

```js
?impact=<node-id>
```

Invalid ids remove the parameter and clear feature-state safely.

- [ ] **Step 7: Restore on boot**

If a valid `impact` query parameter exists, render it after runtime/map initialization without changing selected country state.

- [ ] **Step 8: Commit**

```text
feat(world-map): add bounded dependency impact trace
```

---

### Task 5: Add contextual entry points without UI sprawl

**Files:**
- Modify: `world-map/3d-country-card.js`
- Modify: `world-map/3d-entity-runtime.js`
- Modify: `world-map/3d-gateways.js`
- Modify: `world-map/3d-chain-explorer.js`

**Interfaces:**
- Delegated attributes consumed by `3d-impact-trace.js`:
  - `data-impact-entity="DNK"`
  - `data-impact-gateway="danish-straits"`
  - `data-impact-chain="baltic"`

- [ ] **Step 1: Add country-card Impact action**

Add one button inside the existing `.atlas-country-actions`:

```html
<button type="button" data-impact-entity="DNK" title="Trace represented dependency impact">Impact</button>
```

Do not add another action row or menu.

- [ ] **Step 2: Ensure territories have the same action**

If the normal compact card does not render an action for a non-country entity, `3d-entity-runtime.js` adds a single Impact action inside its existing entity context block. Avoid duplicates when the main card already provides it.

- [ ] **Step 3: Add gateway-popup Impact action**

Gateway popup HTML includes:

```html
<button type="button" data-impact-gateway="...">Impact</button>
```

The central impact module owns the click behavior.

- [ ] **Step 4: Add chain-strip Impact action**

Active chain context includes:

```html
<button type="button" data-impact-chain="...">Impact</button>
```

This queries impact for explicit dependencies on the chain node; ordinary membership remains Context only.

- [ ] **Step 5: Validate no top-level UI drift**

`3d-world-bar.js` remains unchanged by this task. Validator explicitly rejects a persistent Impact control there.

- [ ] **Step 6: Run JavaScript syntax + impact validator**

Expected: browser contract becomes green.

- [ ] **Step 7: Commit**

```text
feat(world-map): expose contextual impact actions
```

---

### Task 6: Integration verification and merge

**Files:**
- No new production files unless verification exposes a concrete defect.

**Interfaces:**
- PR exact-head `Repository quality checks` must complete successfully.

- [ ] **Step 1: Run/check all World Map gates**

Required green checks include:

```text
Validate JavaScript syntax
Validate World Map data runtime
Validate World Map Axis and systems
Validate World Map system intelligence
Validate World Map functional chain explorer
Validate World Map entity and Africa repair
Validate World Map dependency impact trace
Validate canonical World Map runtime
Validate World Map UI shell
Validate canonical World Map relationship path finder
Validate entity-aware Trace
Build public site
```

- [ ] **Step 2: Inspect generated runtime behavior**

Confirm:

```text
country_count = 195
country:AND preserves structured dependency mechanism/importance
territory:GRL exists as impact node
Suez/Bab alternatives point to Cape and do not become affected nodes
no forbidden score field exists
```

- [ ] **Step 3: Check PR head has not moved after the green run**

Use exact commit SHA from the PR and the workflow run associated with that SHA.

- [ ] **Step 4: Merge with expected head SHA only after full green**

Merge method: normal merge commit, preserving the branch history and red→green evidence.

- [ ] **Step 5: Confirm main points at the merge commit**

Do not claim completion until the merge commit is visible on `main`.

---

## Self-review

- No TBD/TODO placeholders.
- Causal direction is consistent: dependent -> dependency; impact traverses incoming causal edges.
- Path finder remains separate and undirected; impact does not consume generic curated edges.
- Graph generation, traversal and UI rendering have isolated owners.
- The plan fixes the real structured-dependency data-loss issue before adding UI.
- Gateway alternatives remain explicit non-causal alternatives.
- The node contract is ready for the next maritime-area/port/cable/pipeline wave without redesigning impact tracing.
