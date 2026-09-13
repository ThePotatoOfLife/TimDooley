# Potato House — Formal House Model

**Status:** research candidate; non-canonical.

A stronger compact object than a single Atlas tree is:

`House = (I, S, C, G, D, B, P, Q)`

where:

- `I` = stable identities;
- `S` = state/lifecycle variables;
- `C` = contexts/environments;
- `G` = family of typed graphs;
- `D` = Door/transition operators and guards;
- `B` = boundaries/interfaces/Rooms;
- `P` = projections/Views;
- `Q` = quality/viability/epistemic constraints.

A useful graph family is:

`G = {T_N, E_B, E_R, E_P, E_T, E_A, E_D, E_F, E_build}`

- `T_N` selected North orientation;
- `E_B` other broader contexts;
- `E_R` semantic Roads;
- `E_P` provenance/derivation;
- `E_T` time/version;
- `E_A` argument/support/attack;
- `E_D` state-transition graph;
- `E_F` quantitative flows where valid;
- `E_build` dependency/rebuild graph.

The distinction is semantic; these need not be separate physical databases.

## North

One North remains useful as a selected orientation arborescence inside richer context. It can stabilize breadcrumbs and public orientation without becoming ontology. Re-parenting should be conservative. Other broader contexts remain explicit relations or Room membership.

## Door

Door is a guarded transition:

`D: (state, context) --[guard]--> new_state`

A serious Door should record source state, precondition, transition activity, destination state, preserved invariants, generated provenance and reversibility/rollback where relevant.

Examples include research→canonical, internal→public, legacy route→replacement, raw source→normalized observation and unresolved claim→reviewed claim state.

## Room

A Room earns architectural status when it has several of:

- independent reader tasks;
- distinct evidence/source rules;
- separate update cadence;
- specialist representation or tooling;
- internal cohesion;
- clear external interfaces;
- local failure containment;
- enough material for local navigation.

A Room should state what it owns, what it never owns, accepted inputs, outputs, stable IDs consumed/produced, freshness rules, epistemic boundary, validators and Doors/Roads to neighbors.

A Room may expose many Views.

## View

A View is a task-specific lossy projection, not an owner. Important Views should know input scope, filters, aggregation, omitted relation/time detail, preserved uncertainty/invariants and the route back to fuller material.

## Context

Context is first-class. Useful dimensions include Room/domain, audience, time, geography/jurisdiction, evidence threshold, public/internal state, scenario/current reality and language/translation.

Context may change expression without changing identity.

## Provenance and time

Root/provenance should eventually distinguish source entity, transformation activity, agent/tool, derived observation/claim, canonical synthesis and public projection.

Keep distinct where material:

- valid time;
- recorded/retrieved time;
- interpretation time;
- source publication time;
- review time.

## Contradiction and arguments

Unknown and contradicted are different states. Consequential disputed claims should be representable with evidence, assumptions, support and counterevidence rather than silently collapsed into one confidence number.

## Public website

The public interface should not require this formal vocabulary. A normal subject surface should answer:

1. What is this?
2. What context am I in?
3. What matters here now?
4. What is connected, and why?
5. How did it change?
6. What supports this account?
7. Where can I go deeper?

Use the representation suited to the task: map for geography, timeline for change, graph for typed relations, diagram for anatomy/geometry, dossier for evidence, table/chart for quantitative comparison, reader for prose and state machine for regime transitions.

Search is a temporary corridor through permanent Rooms, not the architecture.
