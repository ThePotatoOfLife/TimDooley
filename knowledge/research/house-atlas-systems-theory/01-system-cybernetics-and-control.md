# House Cybernetics, Control and Viability

**Status:** exploratory research; non-canonical.

## Core idea

The House can be studied as a growing regulated system. New sources, domains, contradictions, readers, tools and data are disturbances. Schemas, validators, canonical ownership, provenance rules, room grammars and maintenance workflows act as regulation.

A useful research state is:

```text
q = (provenance, ownership, relation integrity, contradiction handling,
     accessibility, findability, freshness, build health, orientation, ...)
```

Growth introduces disturbances `d(t)`; maintenance actions such as merge, split, promote, deprecate, validate and prune act as controls `u(t)`.

Conceptually:

```text
dq/dt = F(q,u,d)
```

This is not yet a calibrated dynamical model. Its value is conceptual discipline: the project should know what it is trying to observe, preserve and regulate.

## Requisite variety

Ashby's law of requisite variety is a strong architectural neighbor.

The archive receives many kinds of variation:

- documentary, scientific, historical, theological and creative material;
- static and temporal data;
- geographic and non-geographic relations;
- contradictory and uncertain claims;
- prose, equations, maps, graphs, books, datasets and simulations;
- domains with different update rates and evidentiary expectations.

If the backend has too little expressive variety, material is flattened. If it reacts by adding one-off exceptions, the architecture becomes Swamp.

Working rule:

> **Match complexity in the backend; compress complexity at the interface.**

This supports many internal relation types and epistemic states while preserving a calm public threshold.

## Observability

A repository can contain failures that current checks cannot see.

Examples:

- duplicate concepts under different names;
- stale public projections;
- contradictions hidden in separate branches;
- canonical records whose sources no longer resolve;
- valid data that is unreachable from public navigation.

Control theory suggests a useful distinction:

> **A healthy system needs enough sensors to observe the failures it claims to regulate.**

Validators, source-coverage reports, route audits, contradiction audits and visual regressions are the software Eye.

## Controllability

Observation does not imply repair capability.

A duplicated owner may be easy to detect but difficult to consolidate safely because routes, references, source histories and public projections depend on both.

Maintenance planning can therefore distinguish:

- observable and controllable;
- observable but not safely controllable yet;
- controllable but not automatically observed;
- neither.

This is useful for backlog triage.

## Viability / Garden

Garden is better modeled as a viable operating region than as a single goodness score.

Candidate viability constraints:

- stable canonical identity;
- provenance traceability;
- epistemic separation;
- readable public output;
- accessibility;
- maintainability;
- extensibility;
- resilience to partial failures;
- local module autonomy;
- future generativity.

A viable House keeps its state inside acceptable bounds while continuing to grow.

This is fundamentally multi-objective. A design that improves one dimension while destroying several others is not automatically better.

## Swamp as failure vector

Swamp should be treated diagnostically rather than as a scalar moral label.

A repository Swamp vector might include:

```text
s = (
  duplicate_owner_pressure,
  orphan_rate,
  unresolved_edge_rate,
  missing_provenance,
  unclassified_contradiction,
  generic_relation_ratio,
  stale_projection_pressure,
  dead_research_pressure,
  circular_north_pressure,
  reader_clutter,
  hidden_dependency_pressure
)
```

Different failure dimensions require different repairs. Do not collapse them into one number prematurely.

## Feedback loop taxonomy

The project uses feedback language frequently. Improve precision by distinguishing:

- reinforcing feedback — change amplifies further change;
- balancing feedback — response counteracts deviation;
- delayed feedback — response lag can cause overshoot/oscillation;
- feedforward — anticipatory action before disturbance arrives;
- saturation — response is capacity-limited;
- hysteresis — entry and exit thresholds differ;
- lock-in/path dependence — past states constrain future options.

A serious feedback record should name the variables, direction/sign where meaningful, delay, boundary, evidence and whether the loop is measured or hypothesized.

## Stocks and flows

Systems analysis should distinguish accumulated stocks from rates of flow.

Examples inside the repository:

- canonical knowledge = stock; research/promotion = flows;
- unresolved questions = stock; discovery/resolution = flows;
- technical debt = stock; creation/retirement = flows;
- archive corpus = stock; ingestion/recovery = flows.

The same distinction matters in economics, finance, energy and attention systems.

Working rule:

> **Every quantitative system record should know whether a value is a stock, flow, rate, event or cumulative total.**

## Delay and freshness

Different facts age differently.

A company owner, GDP observation, government minister, constitutional structure, manuscript date and historical birth date have radically different freshness profiles.

Do not use one global freshness decay function.

A useful future field is domain-specific update cadence or freshness class.

## Resilience

One canonical source of truth should not imply one operational point of failure.

Resilient design favors:

- replaceable projections;
- reproducible builds;
- modular readers;
- graceful fallback states;
- explicit missing-data behavior;
- multiple retrieval routes over one identity;
- local failure containment;
- stable IDs independent of file names or page implementations.

Expression:

> **One source of truth does not require one point of operational failure.**

## Anti-fragility

A strong maintenance principle:

> **Every serious recurring failure should purchase a permanent invariant, validator, schema rule or clearer ownership boundary.**

The project should become better able to handle future disturbances because it encountered past ones.
