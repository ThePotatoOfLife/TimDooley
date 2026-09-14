# Project Calibration Spine Design

**Status:** proposed architecture

**Date:** 2026-09-14

## 1. Purpose

Build one durable calibration mechanism that tells maintainers where the repository is structurally mature, thin, duplicated, stale, or hard to reach without creating another public dashboard or another competing source of truth.

The calibration spine exists to support the repository's established loop:

`inspect → consolidate → deepen → connect → expose → verify → prune → repeat`

It measures structural maturity and discoverability. It does **not** measure whether a theological, historical, scientific, political, or autobiographical claim is true.

## 2. Current problem

The repository is healthy at the build/deployment layer, but several maintenance signals have drifted:

- `docs/PROJECT-OPERATING-MAP.md` still describes a consolidation branch as the active implementation workspace even though `main` is the current integration/deployment baseline.
- stale work can remain visibly active after its substantive content has already been absorbed elsewhere, as happened with PR #121.
- the core index, public manifest, source index, question index, context graph, and domain-specific completion matrices contain enough metadata to judge structural maturity, but there is no repository-wide maturity view.
- cleanup and enrichment decisions are therefore still partly manual and can favor the loudest recent file rather than the weakest important canonical owner.

The solution is not another hand-maintained status document. The solution is a deterministic audit derived from current canonical routing and existing records.

## 3. Design decision

Create a **canonical-owner maturity audit** driven by the current `knowledge/indexes/core-index.json` record list and cross-checked against `manifest.json` and existing routing/evidence indexes.

The audit will produce a machine-readable report that answers:

1. Is this record clearly defined?
2. Can its development through time be traced where relevant?
3. Are meaningful relationships exposed?
4. Is provenance available?
5. Are uncertainty, contradiction, mismatch, or counterevidence represented where relevant?
6. Can a reader get a direct answer or clear public explanation?
7. Can the record be found through aliases/terms?
8. Is it reachable through the current public/navigation architecture?
9. Does it expose unresolved questions or a research frontier?

The report is a maintenance instrument, not a public truth ranking.

## 4. Scope

### In scope

- reconcile stale operator guidance with current `main` workflow;
- create one repository-wide maturity audit over canonical owners;
- make audit results traceable to concrete files/fields/links;
- produce a ranked maintenance queue from structural gaps;
- validate the report in CI;
- use existing canonical indexes and readers as inputs rather than inventing parallel ownership metadata.

### Out of scope

- scoring the truth of project claims;
- changing theological or autobiographical doctrine;
- deleting historical branches;
- automatically deleting files judged redundant;
- creating a new public dashboard;
- replacing domain-specific completion matrices;
- turning every specialist research file into a canonical owner;
- forcing all domains to use identical evidence standards.

## 5. Canonical inputs

The first implementation should use these existing owners as inputs:

- `knowledge/indexes/core-index.json` — canonical owner inventory and canonical grouping;
- `manifest.json` — public branches, pathways, relations, and reader reachability;
- `knowledge/indexes/source-index.json` — provenance routing/evidence classes;
- `knowledge/indexes/context-graph.json` — curated cross-owner relationships;
- `knowledge/reader/tim-dooley-question-index.json` — direct reader-answer reachability;
- `knowledge/guides/project-growth-compass.json` — editorial maturity dimensions and research priorities;
- each canonical record referenced by `core-index.json`.

Domain-specific completion matrices may be consumed as supporting evidence when they already exist, but they remain domain owners and are not replaced.

## 6. Output architecture

### Generator

Create:

`./scripts/build_canonical_owner_maturity.py`

Responsibilities:

- load the canonical owner inventory from `core-index.json`;
- inspect each referenced canonical record;
- inspect cross-index routing and public reachability;
- apply deterministic feature detectors;
- write one generated report;
- fail clearly when a canonical owner path is missing or malformed.

### Generated report

Create:

`knowledge/indexes/canonical-owner-maturity.json`

This report is a **derived maintenance projection**, not a canonical knowledge owner.

Top-level fields:

- `version`
- `updated`
- `status: "derived-maintenance-audit"`
- `purpose`
- `method_boundary`
- `inputs`
- `dimensions`
- `owners`
- `summary`
- `maintenance_queue`

Each owner entry should contain:

- `id`
- `path`
- `branch`
- `kind`
- `dimensions`
- `structural_coverage`
- `evidence`
- `gaps`
- `recommended_next_action`

### Validator

Create:

`./scripts/validate_canonical_owner_maturity.py`

Responsibilities:

- regenerate the report in memory;
- compare it with the checked-in generated report;
- fail on stale output;
- verify every core-index owner exists;
- verify every dimension has an explicit evidence reason;
- reject unknown dimension/status values;
- verify the maintenance queue references real owners and real gaps.

The validator should be added to the existing repository quality workflow.

## 7. Maturity dimensions

The audit uses nine dimensions from the project growth compass.

Each dimension has one of four statuses:

- `strong`
- `partial`
- `missing`
- `not_applicable`

Do not infer semantic quality from file length. Do not award maturity merely because many keys exist.

### 7.1 Definition

Question: does the owner explain what it is and what it owns?

Positive structural evidence may include explicit `definition`, `purpose`, `summary`, `description`, `thesis`, `scope`, or equivalent top-level explanatory fields.

### 7.2 Timeline

Question: can meaningful development through time be traced when chronology matters?

Evidence may come from owner-local dated material or explicit links to canonical timeline owners/ledgers.

A timeless geometry or static reference may legitimately be `not_applicable` rather than penalized.

### 7.3 Relations

Question: does the owner expose meaningful connections rather than exist as an isolated dossier?

Evidence may come from owner-local `connections` / `relations`, `context-graph`, or manifest relations involving the owner/branch.

### 7.4 Provenance

Question: can important claims be traced back toward sources or evidence classes?

Evidence includes explicit source fields, source ledgers, registry links, provenance metadata, or source-index routing.

### 7.5 Counterevidence / uncertainty

Question: does the record expose boundaries, mismatches, contradictions, uncertainty, alternatives, or unresolved claims where relevant?

Positive evidence can include `boundary`, `counter*`, `uncertainty`, `limitations`, `mismatch`, `disputed`, `conflicts`, `unresolved`, or linked contradiction records.

This dimension must not require manufactured disagreement. A purely descriptive source registry may be `not_applicable`.

### 7.6 Reader answer

Question: can the archive produce a direct human-readable answer or explanation from this material without inventing new facts?

Evidence may come from the question index, a branch reader, or explicit reader routes.

### 7.7 Aliases / retrieval terms

Question: can a reader or machine find the owner under the names people actually use?

Evidence includes core-index `terms`, owner aliases, names, labels, keywords, or question-index terms.

### 7.8 Public reachability

Question: is the owner reachable from the current architecture rather than merely existing on disk?

Evidence requires a traceable route such as:

`manifest branch/pathway → branch record → canonical owner`

or another explicit public/index route.

The audit should preserve the distinction between **publicly reachable** and **intentionally specialist-only**.

### 7.9 Research frontier

Question: does the owner expose what remains unresolved or what should be investigated next?

Evidence may include `research_frontier`, `next_actions`, `open_questions`, `recovery_targets`, `remaining_work`, `research_queue`, or similar fields.

## 8. Structural coverage score

For sorting only, calculate a transparent structural-coverage percentage:

- `strong = 1.0`
- `partial = 0.5`
- `missing = 0.0`
- `not_applicable` excluded from the denominator

The percentage is explicitly labeled **structural coverage**, never confidence, truth, authority, scientific validity, or importance.

No owner is declared "bad" solely because its score is low. A low score means the audit found missing structural support that may deserve review.

## 9. Evidence trace requirement

Every dimension result must include an evidence object such as:

```json
{
  "status": "partial",
  "reason": "Owner has direct sources but no source-ledger connection",
  "evidence": [
    "knowledge/core/example.json#sources",
    "knowledge/indexes/source-index.json"
  ]
}
```

A maturity status without a reason/evidence trace is invalid.

This makes the audit reviewable and prevents hidden heuristic judgments.

## 10. Maintenance queue

The generated report should derive a queue ordered by:

1. canonical importance / first-class core-index membership;
2. missing public reachability;
3. missing provenance;
4. missing definition;
5. missing reader answer;
6. missing relations;
7. missing uncertainty/counterevidence where relevant;
8. missing timeline where relevant;
9. missing aliases;
10. missing research frontier.

The queue should contain concrete actions, for example:

- `connect owner to source ledger`
- `add direct reader answer`
- `expose owner from manifest branch`
- `add contradiction boundary`
- `consolidate duplicate definition into this owner`

It must not automatically edit owners.

## 11. Current-state documentation calibration

Update `docs/PROJECT-OPERATING-MAP.md` so it reflects the actual workflow:

- `main` is the integration and deployment baseline;
- substantial changes begin on fresh branches rooted in current `main`;
- CI validates replacement/integration branches before merge;
- stale or superseded branches are provenance/history, not active architecture;
- no historical branch should be merged merely because it exists.

Update `TODO.md` after the audit exists:

- mark the repository-wide maturity test as implemented;
- add the generated maintenance queue as the preferred source for choosing structural calibration work;
- retain the existing editorial priority for source recovery, role transitions, contradiction surfaces, sequence comparison, and reader journeys.

Do not create a second current-state document.

## 12. PR #121 and stale-work handling

PR #121 is a concrete example of why the calibration spine is needed:

- its substantive attestation records were later absorbed into `main`;
- one derived file on `main` is already newer than the PR copy;
- the remaining unabsorbed file is an obsolete implementation plan rather than missing canonical knowledge.

Therefore:

- do not merge PR #121;
- do not resurrect its stale implementation-plan file merely to match an old diff;
- close/supersede the PR when GitHub mutation is available;
- do not encode PR #121 as a permanent special case in the maturity engine.

## 13. CI behavior

The first release should be strict about **integrity** but advisory about **maturity**.

CI must fail if:

- a core-index owner path does not exist;
- the maturity report is stale;
- report schema/status values are invalid;
- an evidence trace points to a nonexistent repository path;
- the maintenance queue references an unknown owner or unknown gap.

CI must **not** fail merely because an owner has low structural coverage.

Low maturity creates work; it does not break the build.

## 14. Determinism and stability

The generator must be deterministic:

- stable owner ordering follows `core-index.json`;
- stable dimension ordering follows this specification;
- stable maintenance ordering uses explicit priority rules plus owner ID as a final tie-breaker;
- no timestamps more precise than repository date are necessary;
- no network calls;
- no AI/LLM judgment at build time.

This ensures that a generated diff reflects repository changes rather than nondeterministic scoring.

## 15. Testing strategy

Implementation should use TDD.

Minimum test cases:

1. owner with strong local definition/provenance/relations;
2. owner whose timeline support is supplied by a linked canonical ledger;
3. owner intentionally specialist-only for public reachability;
4. timeless/static owner where timeline is not applicable;
5. owner with uncertainty/boundary fields;
6. owner with missing path — hard failure;
7. stale generated report — validator failure;
8. unknown maturity status — validator failure;
9. maintenance queue ordering remains deterministic;
10. current repository audit generates successfully from `main` inputs.

## 16. Success criteria

The calibration spine is successful when:

- current operator docs describe the real `main`-first workflow;
- every core-index canonical owner receives a transparent nine-dimension maturity assessment;
- every assessment is traceable to repository evidence;
- maintainers get a ranked, concrete queue instead of guessing what to fix next;
- no new public dashboard or duplicate canonical truth source is introduced;
- low maturity is advisory while structural corruption remains CI-blocking;
- future enrichment work can point to a specific gap and show that the gap improved after the change.

## 17. Follow-on use

After this calibration spine lands, the next work wave should select the highest-value queue item and choose one of two modes:

- **reachability calibration** — make valuable existing knowledge easier to reach through current Doors/readers;
- **knowledge-depth calibration** — deepen the canonical owner in the exact missing dimension, such as provenance, contradiction handling, timeline precision, or reader answer.

The maturity report becomes the measurement instrument; existing canonical owners remain the knowledge system.
