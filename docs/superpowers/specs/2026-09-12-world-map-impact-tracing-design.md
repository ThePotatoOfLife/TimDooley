# World Map Dependency Impact Tracing Design

## Status
Approved direction from the 2026-09-12 World Map roadmap: build “What breaks?” / dependency-impact tracing before the broader maritime systems layer. This spec refines that approved direction against the current repository architecture.

## Goal
Turn the World Map from a representation of relationships into a tool that can answer a bounded counterfactual question:

> If this represented country, territory, gateway, dependency or functional chain becomes unavailable or constrained, what explicitly represented systems are directly affected, what is connected one step beyond them, and what alternatives are already documented?

The feature must expose **represented dependency structure**, not predict real-world collapse.

No synthetic risk score, fragility score, resilience score, probability estimate or casualty/economic-loss forecast is introduced.

---

## 1. Architectural finding

The repository already contains most of the ingredients, but they are projected separately:

- canonical country records contain explicit dependency material;
- some country records contain structured `strategic_dependencies` objects with `dependency`, `mechanism` and `importance`;
- `build_world_map_runtime.py` currently preserves only string-like dependency values, so structured dependency objects are silently omitted from the browser runtime;
- `world-map-gateways.json` contains empirical chokepoints, associated countries, systems, observations and some documented alternative-route language;
- `world-system-chains.json` contains functional systems and members;
- `world-relational-map.json` contains general relationship topology;
- `3d-pathfinder.js` computes undirected shortest paths through the general curated relationship graph.

The impact feature must **not** reuse the pathfinder graph as if every relationship were a causal dependency.

`connected_to(A,B)` does not imply `A depends_on B`.

The solution is a separate directed impact projection generated from explicit dependency evidence.

---

## 2. Three possible approaches

### Approach A — generated evidence-first impact graph — selected

Generate a compact `impact` plane inside `world-map-data-runtime.json` from canonical owners. Preserve structured dependency records, resolve targets where possible, and keep unresolved dependency concepts as named non-geographic nodes. Add gateway/chain relationships only with explicit edge semantics such as `uses-gateway`, `alternative-route`, `member-of-chain` or `contextual-system`.

Advantages:
- one generated browser source;
- strong epistemic separation;
- reusable by future maritime/infrastructure layers;
- supports directed tracing;
- can improve as country records become richer;
- missing data stays missing.

Trade-off: early coverage will be uneven because the repository’s dependency evidence is uneven.

### Approach B — infer impact in the browser from strings and existing relationships

Scan `systems.dependencies`, gateway countries and general relational edges in JavaScript and guess a graph dynamically.

Advantage: faster initial implementation.

Rejected because it creates hidden inference rules, duplicates ownership and risks presenting ordinary relationships as causal dependencies.

### Approach C — full resilience / disruption simulation engine

Model capacities, substitutions, propagation weights, loss functions and scenario outputs.

Rejected for this wave. The current repository does not contain enough comparable capacity/substitution data to make such outputs defensible.

---

## 3. Canonical impact model

The impact graph is generated, not hand-maintained as a second database.

Runtime shape:

```json
{
  "impact": {
    "version": "1.0.0",
    "policy": {
      "max_browser_depth": 2,
      "score_policy": "no aggregate impact score inferred",
      "missing_policy": "not represented is not no dependency"
    },
    "nodes": {
      "country:AND": {
        "id": "country:AND",
        "kind": "country",
        "code": "AND",
        "label": "Andorra"
      },
      "dependency:and:france-spain-road-access": {
        "id": "dependency:and:france-spain-road-access",
        "kind": "dependency-concept",
        "label": "France and Spain road access"
      },
      "gateway:danish-straits": {
        "id": "gateway:danish-straits",
        "kind": "gateway",
        "label": "Danish Straits"
      }
    },
    "edges": [
      {
        "source": "country:AND",
        "target": "dependency:and:france-spain-road-access",
        "relationship": "depends-on",
        "mechanism": "physical trade, tourism and labour mobility",
        "importance": "critical",
        "causal_status": "explicit-dependency",
        "evidence_class": "canonical-country-record"
      }
    ]
  }
}
```

### Node kinds

Initial supported kinds:

- `country`
- `territory`
- `gateway`
- `functional-chain`
- `dependency-concept`

Future-compatible but out of scope for this wave:

- port
- cable
- pipeline
- grid/interconnector
- company/facility
- maritime-area

The node scheme should already allow those additions without changing the browser trace contract.

---

## 4. Dependency extraction

### Structured dependencies

Country records may contain arrays such as:

```json
{
  "dependency": "France and Spain road access",
  "mechanism": "physical trade, tourism and labour mobility",
  "importance": "critical"
}
```

The runtime builder must preserve these as structured impact facts.

Recognized fields:

- `dependency`
- `target`
- `mechanism`
- `importance`
- `source`
- `source_url`
- `year` / `period` / `reference_period`
- `confidence`

Unknown fields may be preserved in source metadata but do not gain semantics automatically.

### String dependencies

Existing string lists remain usable. They generate dependency-concept nodes with no invented mechanism or importance.

### Typed relationships

Only relationship records whose type is explicitly dependency-like can generate impact edges:

- `depends-on`
- `dependency`
- `strategic-dependency`
- `import-dependence`
- `depends_on`

Ordinary trade, alliance, cultural, border, institutional or project relations do not become impact edges unless their canonical record explicitly encodes dependency semantics.

### Target resolution

A dependency target is resolved only when deterministic enough.

Resolution order:

1. explicit ISO3/code field;
2. exact canonical entity name;
3. exact gateway id/label;
4. exact functional-chain id/label;
5. otherwise a scoped `dependency-concept` node owned by the source entity.

Do not fuzzy-resolve strings such as “European market access” into the EU or a specific country without explicit canonical evidence.

---

## 5. Direction and impact semantics

Dependency edges point from the dependent object toward what it depends on:

`dependent -> dependency`

For the “What breaks if X is constrained?” query, traversal therefore follows **incoming** dependency edges:

`X <- direct dependents <- second-order dependents`

This distinction must be explicit in code and documentation.

Example:

```text
Danish Straits
    <- represented Baltic access dependency
        <- represented country/system dependency
```

The browser should describe this as:

- **Directly exposed** — an explicit dependency edge terminates at the selected node.
- **Second-order** — an explicit dependency path of two edges reaches the selected node.
- **Context** — a chain/system shares the affected nodes but is not itself encoded as causal dependency.
- **Alternative** — the repository explicitly documents a route/substitute; not inferred from geography.

---

## 6. Gateway semantics

Gateways already have empirical system tags and associated countries. Association alone is not dependency.

The impact projection may create these edge types:

- `located-at` / `associated-with` — contextual only;
- `serves-system` — contextual only;
- `uses-gateway` — causal only when explicitly owned by a source record;
- `alternative-route` — only when an owner explicitly documents the alternative relationship.

Initial explicit alternative relationships that can be represented from existing gateway descriptions include:

- Suez / Bab el-Mandeb disruption ↔ Cape of Good Hope route as documented rerouting context;
- Hormuz alternative capacity remains partial and must not be represented as full substitution.

If a gateway description merely says it is “important,” the runtime must not manufacture affected countries from that adjective.

---

## 7. Functional-chain semantics

Functional chains are useful explanatory context but membership does not imply dependency.

The runtime may expose:

```text
impact node -> contextual chain membership
```

but the browser must keep contextual chains visually/textually separate from direct/second-order impact.

When an affected country belongs to the Baltic chain, the result may say:

> Context: Baltic functional chain

It must not say:

> The Baltic chain breaks

unless there is an explicit causal edge supporting that statement.

---

## 8. Browser interaction

### Entry points

Do not add a permanent top-level map button.

Add contextual `Impact` actions in places where a user already has an object selected:

- country/territory card;
- gateway popup;
- active functional-chain context strip.

The action label may be `Impact` with title/aria text equivalent to “Trace represented dependency impact”.

### Result surface

Use one compact contextual panel, analogous to the current Path/Chain surfaces.

It shows:

1. selected object;
2. `Directly exposed` rows;
3. `Second-order` rows;
4. `Known alternatives` when explicitly represented;
5. `Context` functional chains;
6. evidence boundary:
   `This traces represented dependencies, not a forecast of real-world failure.`

The result is bounded:

- max depth: 2;
- max direct rows: 12;
- max second-order rows: 12;
- deterministic ordering by evidence quality / explicit importance, then label;
- overflow summarized as `+N more represented dependencies`.

### Map visualization

Use a dedicated feature-state outline channel:

- selected impact source: strong outline;
- direct exposed countries/territories: primary impact outline;
- second-order countries/territories: lighter outline.

Do not change the base scalar fill.

Gateway nodes already have their own point layer and can be highlighted contextually.

No red/green “danger” heat map and no alarm-style UI.

### URL state

Persist only the selected impact node:

`?impact=<node-id>`

Depth stays fixed at 2 in this wave; no extra URL options are necessary.

Invalid/stale ids clear cleanly rather than falling back to a different node.

---

## 9. Runtime API

Extend the shared runtime API with:

```js
impactNode(id)
impactFor(id)
impactNodeForEntity(code)
impactNodeForGateway(id)
impactNodeForChain(id)
```

`impactFor(id)` returns a fully bounded result object:

```js
{
  root,
  direct: [],
  secondOrder: [],
  alternatives: [],
  contextChains: [],
  boundary: 'represented-dependencies-not-forecast'
}
```

Traversal logic should live in one focused browser module or generated runtime helper contract, not be copied into card/gateway/chain modules.

Recommended browser owner:

`world-map/3d-impact-trace.js`

---

## 10. Fix the existing dependency projection while building this

The current `explicit_dependencies(record)` helper returns strings and ignores structured dependency objects.

Replace it with two distinct projections:

- `dependency_labels(record) -> list[str]` for the current compact `System role / Depends` card;
- `structured_dependency_facts(record, code) -> list[dict]` for the impact graph.

This avoids overloading one helper and prevents loss of mechanism/importance data.

The existing country-card system role remains compact; it does not need to display every structured field.

---

## 11. Epistemic and causal guardrails

The feature must distinguish:

- explicit dependency;
- explicit alternative;
- contextual association;
- functional-chain membership;
- unresolved concept.

It must never infer:

- probability of disruption;
- severity of disruption;
- economic loss;
- military outcome;
- political collapse;
- population harm;
- resilience score;
- complete substitutability;
- causal dependence from ordinary graph adjacency;
- causal dependence from shared institutional membership.

Missing impact edges mean **not represented in the current dataset**, never **no real-world impact**.

---

## 12. TDD / validation contract

Create a dedicated validator before production implementation.

It must assert:

### Runtime

- `impact` exists in generated runtime;
- impact policy says no aggregate score inferred;
- every impact edge has `source`, `target`, `relationship`, `causal_status`;
- every edge endpoint exists in `impact.nodes`;
- explicit country structured dependency objects survive projection;
- unresolved dependency strings become dependency-concept nodes rather than being discarded;
- country count remains 195;
- territory nodes such as Greenland can participate without becoming countries.

### Causal guardrails

- ordinary `curated_edges` are not bulk-imported as `depends-on` edges;
- chain membership alone cannot generate `depends-on`;
- gateway country association alone cannot generate `depends-on`;
- no `impact_score`, `risk_score`, `resilience_score`, `collapse_score` fields.

### Browser

- `3d-impact-trace.js` exists;
- bootstrap loads it contextually after runtime/card/gateway/chain modules;
- shared runtime exposes the five impact APIs;
- result panel contains direct, second-order, alternatives and context sections;
- depth is bounded at 2;
- URL state uses `impact`;
- direct/second-order map visualization uses a dedicated outline/feature-state channel;
- no permanent top-level Impact button is added to World Bar.

### Regression fixture

Use a small generated fixture:

```text
A depends on B
C depends on A
D is merely connected to B
```

Impact on `B` must return:

- direct: `A`
- second-order: `C`
- not affected: `D`

This fixture is essential because it proves the feature is tracing **directional dependency** rather than generic graph proximity.

---

## 13. Implementation order

1. Add failing impact validator and canonical CI gate.
2. Refactor dependency extraction to preserve structured facts without changing existing compact card behavior.
3. Generate impact nodes/edges into the World Map runtime.
4. Add deterministic two-hop impact query helper/API.
5. Add `3d-impact-trace.js` contextual panel and dedicated outline state.
6. Add contextual Impact actions to country/territory card, gateway popup and chain strip.
7. Add a small set of explicit gateway-alternative edges only where the current repository already owns the statement.
8. Run full repository quality suite on exact PR head.
9. Merge only after full green.

---

## 14. Relationship to the next maritime wave

This feature deliberately establishes node/edge semantics that the maritime layer can reuse.

Future maritime nodes can enter as:

```text
maritime-area: north-sea
port: rotterdam
cable-system: ...
pipeline: ...
offshore-hub: ...
```

and explicit infrastructure dependencies can connect them to the same impact engine without redesigning the UI or causal rules.

The next maritime wave should therefore focus on **adding better real-world nodes and edges**, not building a second tracing system.

---

## 15. Out of scope

- probabilistic scenario simulation;
- economic loss modelling;
- live shipping telemetry;
- full maritime-area rendering;
- complete global supply-chain ingestion;
- automatic LLM inference of dependencies;
- synthetic risk/resilience scores;
- arbitrary depth graph exploration;
- replacing the existing shortest relationship Path tool.

Path answers “how are these represented objects connected?”
Impact answers “who explicitly depends on this represented object?”

Both belong in the map because they answer different questions.
