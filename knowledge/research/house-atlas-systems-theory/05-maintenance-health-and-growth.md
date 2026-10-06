# Maintenance, Health and Growth of the House

**Status:** exploratory research; non-canonical.

## The House as a learning system

A useful high-level loop is:

```text
observe
→ preserve
→ normalize
→ infer
→ canonicalize
→ project
→ receive contradiction/question
→ research
→ revise
→ observe again
```

The system learns only if feedback can change its current state.

An archive that stores contradictions but has no path to review them is accumulating, not learning.

## Formal maintenance operators

Repository maintenance can be described as a small set of recurring operators.

### Promote
Move unique durable knowledge from research/source material into a canonical owner while preserving provenance.

### Merge
Consolidate duplicate owners after migrating unique information, routes and dependencies.

### Split
Fission an overloaded owner into clearer responsibilities while retaining parent synthesis and compatibility paths.

### Archive
Remove current ownership/presentation role while preserving historical/provenance value.

### Deprecate
Mark a current contract or projection as superseded and point to its replacement.

### Project
Generate a human or machine View from canonical material with explicit selection/aggregation/loss.

### Reparent
Change the canonical North parent under strong review and cycle/route checks.

### Validate
Test invariants without mutating the thing being validated.

### Prune
Remove only after unique information and live dependencies are known to be safe.

Expression:

> **Cleanup is safer when treated as typed transformations with preconditions, not arbitrary file editing.**

## Door as maintenance gate

A Door can be a guarded transition:

```text
D: G ⊆ S -> S'
```

where `G` is the condition under which the transition is allowed.

Examples:

- research candidate → canonical owner after review;
- legacy route → replacement after redirect validation;
- private/internal artifact → public projection after publication rules;
- observed state → scenario state only after explicitly entering scenario mode.

A Door should declare:

- precondition;
- what changes;
- what identity/provenance remains invariant;
- whether/how to return.

## Room pressure

Signals that one Room/owner may be under structural pressure:

- too many unrelated reasons to change;
- multiple independent reader tasks;
- several specialist representations competing for priority;
- large internal navigation with little cohesion;
- different update/source cadences;
- many inbound links targeting independent subsections;
- repeated exceptions to its current grammar.

Possible responses, from least to most structural:

1. better internal navigation;
2. specialist View;
3. relation/event promotion;
4. child Room;
5. new canonical identity;
6. owner split.

Do not split merely because a file is long.

## Relation pressure

A generic `related-to` edge should be refined when:

- direction matters;
- mechanism matters;
- users repeatedly ask what the relationship actually is;
- the relation needs dates, values or sources;
- different mechanisms are being conflated.

Candidate diagnostic:

```text
generic_relation_ratio = count(related-to) / count(all semantic relations)
```

The goal is not zero. Generic relation remains useful when semantics are genuinely weak or unknown.

## Projection pressure

A View may deserve a specialist public surface when:

- it answers a repeated user task;
- the generic Room cannot represent it well;
- it has substantial internal interaction/state;
- it composes many canonical owners instead of owning duplicate truth;
- it can maintain stable routing/accessibility.

This gives a disciplined path for future maps, graphs, readers, simulations and comparison tools.

## Health vector

Avoid one universal health score.

Useful health dimensions include:

### Structural
- unique canonical IDs;
- North cycles;
- orphan rate;
- unresolved endpoint rate;
- route alias validity;
- generic relation pressure.

### Provenance
- provenance coverage;
- broken source paths;
- derived outputs without lineage;
- source freshness by domain.

### Epistemic
- unclassified contradictions;
- later interpretation rendered as first attestation;
- scientific claims missing source/test boundary;
- interpretation not labeled as interpretation.

### Presentation
- unclear page purpose;
- competing navigation;
- excessive first-level choices;
- core reading requiring JavaScript;
- accessibility/layout instability.

### Maintainability
- bespoke page systems proliferating;
- files with unrelated consumers/responsibilities;
- generated artifacts behaving as masters;
- old research waves never promoted or retired.

### Growth
- valuable information added per permanent artifact;
- rate of successful promotion/retirement;
- increase in navigation complexity relative to knowledge gain.

Master question:

> **Does added information increase system capability faster than it increases confusion and maintenance burden?**

## Dependency graph

A future dependency graph can connect:

```text
source
→ canonical owner
→ derived index/aggregate
→ reader page/tool
→ sitemap/search/machine output
```

This graph can serve three purposes at once:

- provenance;
- impact analysis;
- incremental rebuild/review invalidation.

Expression:

> **Dependency knowledge should power both provenance and incremental builds.**

## Event-sourcing / materialized-view analogy

The project already partly behaves like:

```text
source strata / history
→ current canonical state
→ disposable generated projections
```

This is similar to event-sourced systems with materialized views.

Useful principle:

> **Preserve the history; rebuild the view.**

Generated indexes/pages should be convenient outputs, not second truth stores.

## Exploration versus exploitation

Growth has two modes:

- exploration: new sources, domains, models, relations;
- exploitation: deepen, consolidate, validate and publish what is already known.

Too much exploration creates proliferation/Swamp.
Too much exploitation creates polished islands while important unknowns remain untouched.

The existing expansion → calibration → pruning → expansion rhythm is healthy.

## Growth law

A compact long-term principle:

> **Expansion without gardening becomes Swamp; gardening without expansion becomes a museum.**

Healthy growth alternates:

```text
add
→ connect
→ observe pressure
→ merge duplicates
→ split overloaded owners
→ repair provenance
→ improve traversal
→ prune obsolete projections
→ expand again
```

## Final maintenance stance

The architecture should favor:

- stable identity;
- cheap reversible projections;
- explicit dependency/provenance;
- typed transitions;
- observable health;
- conservative canonical mutation;
- iterative calibration.

The goal is not maximum architecture. It is maximum future usefulness per unit of permanent complexity.
