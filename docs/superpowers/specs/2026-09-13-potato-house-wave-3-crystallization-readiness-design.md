# Potato House Wave 3 Crystallization / Gardener Readiness Design

Status: approved architectural direction; written-spec review gate

## Goal

Wave 3 gives the Potato House an internal Gardener workbench that can explain what state important material is in, what is blocking it, what needs review, and what useful action should happen next.

Wave 3 does not redesign the public site. It does not automatically promote research to canon, canon to publication, or publication to homepage prominence.

Its purpose is operational clarity.

## Governing principle

> Readiness is an explanation of state, not a truth score.

The House already has epistemic methods, source hierarchies, contradiction rules, inference promotion rules, research frontiers, route governance, public projections, ownership maps, and backend audits. Wave 3 orchestrates those signals into a deterministic report.

It does not replace their authority.

## Chosen approach

Use a generated readiness/reporting layer over existing systems.

Rejected alternatives:

- one universal maturity score: too reductive and too easy to confuse with truth;
- mandatory lifecycle fields added to every canonical record: too invasive and creates a large migration;
- manual spreadsheet-style tracking: too disconnected from repository state and too prone to drift.

The durable part of Wave 3 is policy. The disposable part is the generated report.

Likely responsibilities:

- `data/house/crystallization-policy.json` — lifecycle, readiness vocabulary, queue definitions, review rules, intended-role rules;
- `schemas/house-crystallization-policy.schema.json` — policy contract;
- `schemas/house-crystallization-report.schema.json` — generated report contract;
- `scripts/build_crystallization_report.py` — deterministic report builder;
- `data/house/crystallization-report.json` — generated/disposable output.

Exact paths may adjust after Waves 1–2 are implemented, but policy and report must remain separate.

## Lifecycle

The canonical lifecycle is ordered:

1. `raw` — unprocessed bulk material;
2. `captured` — preserved with provenance;
3. `normalized` — stable or candidate identity has been established;
4. `reviewed` — ownership, epistemic class, important contradictions, and context have been checked;
5. `canonical` — accepted durable knowledge inside the House;
6. `synthesized` — durable records have been integrated into a useful higher-level account;
7. `publishable` — clear, sourced/typed, and context-safe enough for ordinary public presentation;
8. `featured` — deliberately selected for prominent discovery.

This lifecycle is not a contest and not every object should reach every stage.

## Intended role

Every readiness assessment must consider what the object is for.

Initial intended roles:

- `archive-only`
- `research`
- `canonical-backend`
- `public-supporting`
- `public-primary`
- `editorial-feature`

An Artifact that is complete at `captured` may be healthy. A major public dossier stuck at `captured` is not.

Readiness must therefore be interpreted relative to intended role.

## Readiness dimensions

The report should evaluate independent dimensions rather than collapse everything into one number.

Initial dimensions:

- `identity`
- `ownership`
- `room`
- `provenance`
- `epistemic_classification`
- `contradiction_review`
- `time_context`
- `synthesis`
- `public_route`
- `projection`
- `public_copy`
- `freshness`

Common status vocabulary:

- `ready`
- `partial`
- `blocked`
- `missing`
- `stale`
- `not_applicable`
- `unknown`

The vocabulary should remain small. Domain-specific nuance belongs in reasons and source metadata, not dozens of new status labels.

## Readiness record

Conceptual example:

```json
{
  "object_id": "tim-dooley",
  "kind": "subject",
  "intended_role": "public-primary",
  "verified_stage": "publishable",
  "readiness": {
    "identity": "ready",
    "ownership": "ready",
    "room": "ready",
    "provenance": "ready",
    "epistemic_classification": "ready",
    "contradiction_review": "ready",
    "time_context": "ready",
    "synthesis": "ready",
    "public_route": "ready",
    "projection": "ready",
    "public_copy": "ready",
    "freshness": "stale"
  },
  "blocking_reasons": [],
  "recommended_actions": ["review recent chronology additions"],
  "evidence": []
}
```

A source Artifact may instead be healthy at `captured` with `public_route: not_applicable` and `synthesis: not_applicable`.

## Stage inference

Wave 3 may derive a verified stage only when the evidence supporting that stage is explicit enough.

Examples:

- `captured` requires preserved source/provenance evidence;
- `normalized` requires resolved or stable candidate identity;
- `reviewed` requires ownership/epistemic/context review signals;
- `canonical` requires a recognized canonical owner or accepted durable registry status;
- `synthesized` requires a durable synthesis owner or explicit promoted synthesis;
- `publishable` requires public-readiness conditions appropriate to intended role;
- `featured` requires explicit editorial curation, never inference from graph centrality or activity.

The builder must not silently upgrade an object merely because many readiness checks happen to be green.

If stage cannot be determined safely, use the highest explicitly evidenced stage or `unknown`.

## Inputs and authority

Wave 3 consumes existing systems according to their existing authority.

### Epistemic method

`knowledge/philosophy/archive-epistemics.json` remains authoritative for:

- evidence/status distinctions;
- source hierarchy;
- preservation of strata;
- contradiction handling;
- promotion/publication philosophy;
- distinction between epistemic strength and informational contribution.

Wave 3 must not create a competing evidence taxonomy.

### Inference method

`knowledge/indexes/inference-ledger.json` remains authoritative for inference classes, observation anchors, alternatives, disconfirming evidence, and promotion methodology.

Wave 3 may surface `promotion_status`, missing promotion targets, or stale inference review, but it does not re-score inference truth.

### Research backlog

`data/research-frontier.json` remains the explicit research backlog/frontier.

Wave 3 may map frontier entries into Gardener queues such as `research_seed` or `needs_normalization` when appropriate.

### Governance and projection

Wave 1 contracts provide identity, Room, public-surface, and topology context.

Wave 2 projections provide public-route and contextual-projection readiness.

### Backend health

Existing audits such as backend coverage, duplicate detection, unresolved relation reporting, source-of-truth audits, route audits, and ownership audits remain the diagnostic owners for those concerns.

Wave 3 consumes their outputs instead of rebuilding equivalent scanners.

## Gardener queues

The report should group actionable items into stable queue categories.

Initial queues:

- `needs_capture`
- `needs_normalization`
- `needs_owner`
- `needs_room`
- `needs_provenance`
- `needs_epistemic_review`
- `needs_contradiction_review`
- `needs_time_context`
- `needs_synthesis`
- `ready_for_public_review`
- `publishable_without_route`
- `public_but_stale`
- `duplicate_owner_conflict`
- `unresolved_relation`
- `legacy_contract_retirement_candidate`
- `research_seed`

Queues are recommendations. They do not mutate source data.

## Blocking reasons

Blocking reasons are more important than aggregate scoring.

Examples:

- no stable identity;
- no canonical owner;
- Room unresolved;
- source lineage missing;
- epistemic class missing;
- competing dates not reviewed;
- synthesis owner absent;
- public route absent;
- projection unresolved;
- public copy absent;
- source freshness exceeded Room policy;
- duplicate ownership conflict;
- unresolved relation endpoint;
- research-only material appearing on a public surface without boundary labeling.

Every queue item should preserve one or more machine-readable reason codes plus a short readable explanation.

## Contradictions

Contradiction is not automatically failure.

The report must distinguish:

- `unreviewed contradiction` — blocks later maturity where relevant;
- `reviewed unresolved contradiction` — may be acceptable canonical knowledge;
- `resolved contradiction` — records resolution while preserving earlier strata;
- `not applicable`.

The Gardener must never "solve" contradictions by deleting older evidence or choosing the most dramatic formulation.

## Freshness

Freshness is contextual.

Do not apply a universal age threshold.

Examples:

- current economic or political datasets may have explicit source-period freshness expectations;
- historical texts do not become stale merely because time passes;
- project-canon synthesis may become review-due when new primary material materially changes it;
- a historical Occurrence may become review-due when new source evidence conflicts with its date;
- generated projections become stale when their source contracts change.

Wave 1 Room policies and domain-specific source contracts may contribute review triggers.

The report should preserve both `last_reviewed` or source period where available and the reason an item is considered stale/review-due.

## Promotion and publication

No automatic promotion is allowed.

Wave 3 may report:

- `candidate_for_canonical_review`
- `candidate_for_synthesis_review`
- `candidate_for_public_review`
- `candidate_for_feature_review`

But it must never silently change canonical state, publish a page, rewrite a Hub, or add homepage prominence.

The editorial/review Door remains human-governed.

## No universal truth or readiness number

Wave 3 must not produce a single score that is allowed to stand for:

- truth;
- importance;
- canonical status;
- publishability;
- homepage priority;
- scientific validity;
- theological validity;
- historical certainty.

Internal diagnostic counts or per-dimension metrics are allowed when their meaning is narrow and explicit.

If a composite implementation metric is ever used for queue sorting, it must remain an operational convenience and preserve the underlying reasons. It cannot alter lifecycle state.

## Public-design protection

Wave 3 is internal by default.

It must not add:

- maturity meters to public pages;
- green/yellow/red readiness badges across the site;
- canonical percentage scores;
- leaderboards;
- public "truth" meters;
- layout changes merely to display Gardener state;
- new homepage cards generated from readiness output.

Where a reader-facing status is genuinely useful, use ordinary evidence-boundary language already compatible with the site, such as:

- "Project interpretation"
- "Research model; not empirically validated"
- "Historical source"
- "Comparison, not identity"

Any broader public UI for Gardener state requires a later explicit design decision.

## Representative acceptance set

Wave 3 should stress-test the readiness model against a deliberately diverse set before mass adoption:

1. Tim Dooley — stable public Subject crossing several Rooms;
2. Son / Jesus / Door — identity plus symbolic/theological function;
3. April 2025 Turning — Occurrence/synthesis anchor;
4. Yggdrasil — comparative mythological concept;
5. John 10 — textual/source object;
6. thalamus — anatomical Subject plus symbolic comparison;
7. Denmark — country/system Subject;
8. one real company — organization in World Systems;
9. one scientific equation/model — formal object with test/evidence boundaries;
10. one creative work — Works object;
11. Tree of Strife — project synthesis/model;
12. one raw source Artifact — provenance object that may never need a public surface.

For each object, the model should be able to state or explicitly decline:

- intended role;
- lifecycle stage;
- identity readiness;
- owner readiness;
- Room readiness;
- provenance readiness;
- epistemic readiness;
- contradiction status;
- time context;
- synthesis status;
- public route/projection relevance;
- freshness/review state;
- blockers;
- recommended next actions.

If one object requires a new universal status vocabulary merely to fit, investigate the model before expanding the kernel.

## Determinism and reproducibility

The report must be reproducible from repository state.

Do not use model calls, web search, random ranking, or current conversational memory during report generation.

Deleting and rebuilding the report must not lose canonical knowledge or workflow decisions that belong in durable policy.

## Failure behavior

- missing optional diagnostic input: warn and continue with explicit `unknown` where necessary;
- missing required House governance contract: fail report generation;
- malformed readiness policy: fail;
- conflicting owner authority: queue as `duplicate_owner_conflict`, do not guess;
- unresolved relation: queue as `unresolved_relation`, do not invent target;
- unknown intended role: mark `unknown`, do not assume public intent;
- contradictory lifecycle evidence: report the conflict and use the highest safely evidenced stage;
- stale generated projection: report it; do not repair public HTML automatically.

## Report structure

The generated report should support at least:

- `generated_at` / source revision metadata;
- policy version;
- input contract versions/hashes where practical;
- readiness records;
- queue summaries;
- queue members;
- unresolved/unknown counts;
- warnings;
- diagnostic-source references;
- report totals by Room, intended role, lifecycle stage, and readiness dimension where useful.

Counts are operational observability, not value judgments.

## Integration with CI

Wave 3 should be report-first initially.

The builder can run in CI and emit diagnostics without blocking unrelated work simply because research is incomplete.

Hard CI failures should be limited to structural impossibilities such as:

- invalid policy/schema;
- required House registry missing;
- duplicate readiness record IDs;
- impossible references inside the generated report;
- generated report not reproducible from required inputs;
- report generator mutating canonical owners;
- policy allowing automatic publication/promotion.

Readiness debt, stale synthesis, missing provenance, research seeds, and unresolved relations should generally appear as actionable report findings unless an existing canonical validator already defines them as hard failures.

## Relationship to existing audits

Wave 3 must consume rather than duplicate existing diagnostics.

Examples:

- backend coverage audit owns broad unmapped/duplicate/unresolved-ID discovery;
- source-of-truth audits own canonical ownership contradictions;
- route/public projection validators own route integrity;
- Room/public-surface validators own House governance integrity;
- inference ledger owns inference promotion state;
- research frontier owns explicit research backlog.

The Gardener report cross-links these findings into a single action-oriented view.

## Relationship to Wave 2

Wave 2 answers: "How can this object/surface connect to the reader?"

Wave 3 answers: "Is this object mature enough for the role we expect it to perform, and what blocks the next useful state?"

Wave 3 may consume Wave 2 projection availability as a readiness dimension but cannot change projection semantics.

## Relationship to Wave 4

Wave 4 may use Wave 3 to identify mature, stale, blocked, or intentionally backend-only material when converging the five Hubs.

Wave 4 must not blindly render the Gardener queue publicly.

Wave 3 provides internal confidence about what the Hubs can safely consume; Wave 4 owns the actual public convergence behavior.

## Non-goals

Wave 3 does not:

- redesign the homepage or Hubs;
- render readiness dashboards publicly by default;
- auto-promote research to canon;
- auto-publish pages;
- auto-feature homepage material;
- replace archive epistemics;
- replace the inference ledger;
- replace the research frontier;
- replace backend/source-of-truth audits;
- require every historical/source record to become public;
- force every object through all lifecycle states;
- assign a universal truth score;
- resolve contradictions automatically;
- mass-edit canonical records to add workflow metadata.

## Success criteria

Wave 3 succeeds when:

1. durable crystallization policy exists;
2. a disposable/rebuildable readiness report can be generated;
3. readiness is dimensional, explainable, and role-aware;
4. lifecycle stage is backed by explicit repository evidence;
5. not-applicable and valid terminal states are supported;
6. contradictions can be mature without being erased;
7. freshness is domain/context-aware;
8. Gardener queues point to concrete next actions and blocking reasons;
9. existing epistemic/research/audit systems retain authority;
10. no automatic publication/promotion occurs;
11. public design remains unchanged by default;
12. the twelve-object acceptance set can be described without flattening object kinds;
13. Wave 4 can consume readiness information without redesigning the ontology again.

## Invariants

1. Readiness is not truth.
2. Lifecycle is not a leaderboard.
3. Intended role determines what "complete" means.
4. Not every object should become public.
5. Not every object should become canonical.
6. Contradiction may be valid preserved knowledge.
7. Provenance outranks convenience.
8. Human editorial review remains the publication Door.
9. Existing authority systems are composed, not replaced.
10. Blocking reasons are more useful than aggregate scores.
11. Generated reports are disposable; durable knowledge is not.
12. Staleness is contextual, not one global age threshold.
13. Gardener queues recommend; they do not mutate.
14. Public evidence labels may be useful; internal readiness machinery remains hidden.
15. Increasing backend intelligence must not increase public visual complexity by default.
