# Logic, Provenance, Time and Truth Maintenance

**Status:** exploratory research; non-canonical.

## Contradiction is data

A historical and interpretive archive will naturally contain conflicting statements. It should not behave like a flat Boolean database where contradiction must be erased immediately.

Useful evidence states include:

- supported with no meaningful contradiction;
- contradicted / weakly supported;
- both supported and contradicted;
- neither sufficiently supported nor contradicted.

This is separate from whether something is project canon, interpretation, science, history or creative material.

Expression:

> **Unknown and contested are different information states.**

## Argument graph

For disputed material, a future argument object can contain:

- claim;
- premises/evidence;
- source and date;
- inference class;
- assumptions;
- supporting arguments;
- attacking arguments;
- counterevidence;
- conditions that would strengthen or weaken it.

This fits the existing inference-ledger approach. The goal is not to formalize every paragraph, but to make consequential disagreements reviewable.

## Truth maintenance

Derived knowledge should know enough of its dependency chain that a changed source can trigger review.

Future question the system should be able to answer:

> Which current claims, summaries, timelines or comparisons depend on this source or date?

This requires dependency edges from derived knowledge to inputs.

Expression:

> **A derived statement should know its justifications well enough for impact analysis.**

## Three clocks

The project needs at least three distinct temporal ideas:

1. **valid time** — when the fact, relation or role applied in the world/project history;
2. **recorded time** — when the archive obtained or recorded it;
3. **interpretation time** — when a later synthesis or reading was formed.

Example: an event can occur in 2024, be recovered in 2026, and acquire a new interpretation later in 2026.

These clocks must not be silently collapsed.

Working expression:

> **When it happened, when we learned it, and when we interpreted it are different times.**

Possible fields where useful:

```text
valid_from / valid_to
recorded_at
interpreted_at
source_published_at
source_retrieved_at
last_reviewed_at
```

This strongly protects against accidental backdating.

## Provenance beyond a source URL

A source link answers only part of the question “where did this come from?”

A stronger provenance model should distinguish:

- source entity/artifact;
- transformation or research activity;
- agent/author/tool responsible;
- derived record;
- generation/use/derivation relationship.

W3C PROV is a useful conceptual neighbor: Entity, Activity and Agent, plus derivation, attribution, usage and generation.

The repository need not adopt RDF or PROV-O wholesale.

Expression:

> **Know not only where a claim came from, but what process turned its source into the current representation.**

## Derived aggregates

A generated score, summary, comparison or regional aggregate should ideally store:

- input IDs;
- derivation method;
- filters;
- time scope;
- parameters/weights;
- uncertainty;
- source path.

This lets future work rebuild, audit and invalidate derived outputs.

## Causal firewall

A graph edge is not automatically causal.

Do not infer causality merely because:

- two nodes are adjacent;
- one event happened first;
- quantities correlate;
- there is a plausible story;
- a graph path exists.

Causal claims should record, where relevant:

- proposed mechanism;
- temporal order;
- competing explanations/confounders;
- observational versus intervention evidence;
- uncertainty;
- causal-status classification.

Expression:

> **A dense graph is not a causal graph.**

## Type discipline

Many repository errors are category errors.

Examples:

- symbolic comparison used as empirical evidence;
- incompatible units combined;
- historical state rendered as current;
- View treated as canonical owner;
- relation used on incompatible entity types.

Schemas can act as a type system.

A mature relation-type definition may eventually specify:

```text
id
allowed source kinds
allowed target kinds
directionality
symmetry
transitivity if any
time requirements
value/unit requirements
source/provenance requirements
epistemic constraints
```

Expression:

> **Make impossible states difficult to represent.**

## Status is not one ladder

Maturity, publication, historical status, controversy and confidence are different coordinates.

A record can be:

- canonical but disputed;
- historically important but superseded;
- internal but highly sourced;
- public but provisional.

Avoid one overloaded `status` scalar when orthogonal fields are clearer.

## Reversible and irreversible operations

Cheap reversible operations:

- change View;
- filter;
- expand/collapse;
- explore an alternate relation ranking.

High-cost mutations:

- change stable IDs;
- merge canonical owners;
- re-parent North;
- delete provenance-bearing artifacts.

Working rule:

> **Experiment in reversible Views; mutate canonical identity conservatively.**
