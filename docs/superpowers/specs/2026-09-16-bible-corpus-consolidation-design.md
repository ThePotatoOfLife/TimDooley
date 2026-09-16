# Bible Corpus Consolidation Design

**Date:** 2026-09-16  
**Status:** Proposed design — awaiting implementation review  
**Scope:** Existing Bible comparator backend only

## Goal

Make the existing Bible corpus materially easier to retrieve, reason over, de-duplicate, and present without adding a new symbolic ontology or deleting source relations.

The system should preserve the full active relation corpus while generating a deterministic consolidation projection that answers three questions for every pair/group of related records:

1. Are these effectively the same finding?
2. Are they distinct parts of one larger finding?
3. Do they only look similar while actually differing or reversing function?

The consolidation layer must improve retrieval and maintenance without silently changing theology, source direction, provenance, or maximum defensible claims.

## Non-goals

- No new Bible "mode" or alternative reader ontology.
- No LLM-generated canonical relation merges.
- No destructive deletion of existing relation records.
- No automatic prophecy, identity, causation, role-transfer, or supernatural inference.
- No reduction of a symbol to one meaning. Stone, Door, Mountain, Valley, Yoke, Dog, Cube, Gate, etc. remain context-dependent.
- No replacement of `bible_corpus.py`, `bible_excavation.py`, or the canonical manifest.
- No generated family-level theological prose that is stronger than, or independent from, the existing relation records.

## Existing foundations to reuse

### Canonical corpus assembler

`scripts/bible_corpus.py` remains the only active relation assembler. It owns deterministic manifest ordering and exact relation-ID collision rejection.

### Excavation/quality assessment

`scripts/bible_excavation.py` already evaluates relation completeness across source quality, exact wording, whole scenes, biblical references, sequence, mismatch/counterpressure, source direction, provenance, related relations, and maximum defensible claim.

The consolidation system must consume these outputs rather than inventing a competing quality score.

## Proposed architecture

### 1. Normalized relation fingerprint

Generate a non-destructive fingerprint for every active relation. The fingerprint is an index artifact, not a new canonical relation.

It contains normalized forms of fields that already exist:

- relation ID
- project anchor tokens
- precise biblical references
- project sequence
- biblical sequence
- source direction
- source-owner paths
- motifs/operators when present
- primary/reusable scene IDs when present
- mismatch/boundary text presence
- maximum-claim presence
- excavation completeness level

Normalization may lower case, normalize whitespace/punctuation and canonicalize scripture-reference formatting, but must not rewrite source wording.

### 2. Pair classification

Every candidate pair can be classified into one of four states:

- `duplicate_candidate` — substantially the same finding under different IDs.
- `overlap_candidate` — distinct findings that materially contribute to one larger point.
- `contrast_candidate` — shared vocabulary/context but materially different or reversed function.
- `unrelated` — insufficient structural relationship.

Pair classification is deterministic and explainable. Each classification must expose the features that caused it.

No automatic merge occurs from a pair classification alone.

### 3. Canonical relation families

The system generates families from high-confidence overlap/contrast structure.

A family is a retrieval projection over existing relations. It must contain:

- stable generated family ID
- human-readable label derived from existing relation vocabulary
- member relation IDs
- representative relation ID
- supporting member IDs
- contrasting/counterpressure member IDs
- shared biblical references
- shared project anchors/functions
- distinct functions preserved per member
- provenance summary by source owner
- unresolved duplicate candidates
- unresolved research gaps

Families do not own theology. The original relation records remain authoritative for their exact claims.

Examples of useful families include Door, Mountain, Stone, Root/Branch, Debt/Release, Garden/Farm, Yoke/Cord, House/Temple/City, but family creation should be data-driven rather than hard-coded to those names.

**Family-ID stability rule:** family IDs must be derived deterministically from normalized family identity/features, not from input ordering. Reordering relations must not change IDs. Adding a new member that clearly joins an existing family should not unnecessarily rename that family.

### 4. Representative selection

When a family needs one entry point, select the best representative using the existing excavation dimensions rather than recency or naming style.

Prefer relations with stronger existing support in this order:

1. precise project/source provenance
2. precise biblical span / reusable biblical scene
3. explicit ordered project and biblical sequences
4. explicit mismatch/counterpressure
5. explicit maximum defensible claim
6. explicit source direction
7. broader supporting provenance/occurrence links

Selection must use a deterministic lexicographic decision over these existing dimensions rather than inventing a separate opaque weighted score.

The representative is only the best retrieval entry point. It does not replace other members.

### 5. Duplicate reconciliation queue

Probable duplicates are emitted into a review queue instead of being silently collapsed.

For each duplicate candidate, output:

- candidate IDs
- recommended canonical representative
- overlap reasons
- evidence unique to each record
- fields that would be lost by a naive merge
- suggested action: `alias`, `enrich_existing`, `keep_distinct`, or `manual_review`

An `alias` is only a recommendation in Phase 1. Phase 1 does not rewrite IDs, relation files, or references. Any later alias decision must remain resolvable and provenance-preserving.

### 6. Retrieval bundles

Generate a compact bundle for each family so readers/tools do not need to scan dozens of files.

Each bundle contains:

- central retrieval representative
- strongest supporting relations
- strongest counterpressure/contrast relations
- exact Bible references
- project-side source owners
- the existing maximum-defensible-claim texts from relevant member relations
- unresolved gaps
- member IDs for drill-down

The bundle is derived only. It does **not** synthesize a new theological maximum claim. It surfaces the existing member-level claim ceilings and must never imply a stronger combined conclusion than those source records permit.

### 7. New-ingestion duplicate pressure

When a future Bible wave is added, CI should compare its new relations against the active corpus and report:

- likely duplicates
- likely family membership
- likely contrast relations
- genuinely novel relations

A warning is advisory unless an exact relation ID collision occurs. The purpose is to prevent duplicate inflation without blocking legitimate new evidence or a distinct functional reversal.

## Deterministic matching strategy

Use staged evidence rather than one opaque score.

### Stage A — exact structural matches

High-confidence duplicate signals:

- same normalized precise biblical reference set
- same or strongly overlapping project anchor
- same ordered biblical sequence
- same source direction
- same central maximum claim/function

### Stage B — partial structural overlap

Potential family membership:

- shared precise passage or reusable scene
- shared project function/anchor vocabulary
- shared operators/motifs
- compatible ordered sequence

### Stage C — contrast detection

Force `contrast_candidate` instead of duplicate when records share a symbol but preserve opposing functions, such as:

- Door as invitation vs Door as confinement
- Mountain as revelation vs Mountain as temptation-to-possession
- Yoke as learning/rest vs Yoke as slavery
- Stone as foundation vs Stone as obstacle/judgment

Existing mismatch/boundary/countertext fields are first-class evidence for this classification.

### Stage D — no relation

Shared words alone are not enough. If structural evidence is thin, leave relations unrelated.

## Data products

Generated artifacts should live under `knowledge/indexes/` and remain rebuildable:

- `bible-relation-fingerprints.json`
- `bible-relation-families.json`
- `bible-duplicate-review-queue.json`

Generated artifacts must not be manually edited.

## Code boundaries

Recommended implementation units:

- `scripts/bible_consolidation.py` — pure normalization/classification/family logic.
- `scripts/build_bible_consolidation.py` — loads manifest corpus + excavation data and writes generated indexes.
- `scripts/validate_bible_consolidation.py` — validates references, determinism, membership, representative selection and claim boundaries.

Existing `bible_corpus.py` remains unchanged unless a narrowly necessary reusable helper is extracted.

Existing `bible_excavation.py` remains the quality/completeness owner.

## Required invariants

1. Every family member ID resolves to exactly one active relation.
2. No relation is deleted or rewritten by consolidation.
3. Exact active relation-ID collisions remain hard failures in `bible_corpus.py`.
4. A relation may belong to more than one retrieval family only when the memberships represent distinct existing functions and are explicitly explainable.
5. A contrast cannot be auto-promoted to a duplicate.
6. Representative selection and family IDs are deterministic and input-order independent.
7. Retrieval bundles may expose member-level maximum claims but may not generate a stronger family-level theological claim.
8. Alias recommendations cannot erase unique evidence; unique fields must be surfaced before any later manual alias decision.
9. Shared vocabulary alone cannot create a duplicate or family.
10. Generated indexes are rebuild-only and must match the active manifest version they were generated from.
11. Phase 1 cannot mutate canonical relation IDs, relation ownership, manifest relation contents, or public rendering.

## TDD cases from the real corpus

The first test set should use real relation patterns already present in the corpus.

### Duplicate candidate

Two relations with the same Romans 11 root/branches passage, same anti-boasting function and materially equivalent project sequence should be flagged as a duplicate candidate rather than emitted as independent top-level results.

### Overlap family

Sinai, Zion, Nebo and Matthew 4 Mountain relations belong to a Mountain family but remain separate functions.

### Contrast

Matthew 11 teaching yoke and Galatians 5 slavery yoke must never be classified as duplicates even though both use `yoke`.

### Door reversal

Invitation/open-gate relations and barrier/confinement relations should share a Door family while preserving opposing function labels.

### Stone reversal

Cornerstone/foundation and road-obstacle/downward-judgment stone relations should be grouped as related but not merged.

### Representative stability

Reordering input relations must not change the selected representative or family IDs.

### Family-ID stability

Adding a clearly related member to an existing family must preserve the family ID when the normalized family identity is unchanged.

### Unique evidence preservation

If two duplicate candidates differ because one has a stronger countertext or exact source occurrence, the duplicate queue must identify that unique evidence rather than recommending blind replacement.

### Weak lexical coincidence

Two relations sharing only a word such as `light`, `house` or `root` without passage/function/sequence support must remain unrelated.

### No synthesized theology

A family containing several member-level maximum claims must return those existing claims by source relation ID and must not emit a newly invented stronger claim string.

## Integration

The existing quality workflow should add, in order:

1. build Bible consolidation indexes
2. validate Bible consolidation indexes
3. continue existing Bible reader / comparator / parity checks

The public reader does not need to change in the first implementation. Backend consolidation must prove useful and stable first.

A later reader pass may consume family bundles to reduce repeated cards and improve retrieval, but that is explicitly outside this first implementation.

## Success criteria

The change is successful only if it produces tangible improvement on the current corpus:

- identifies real duplicate candidates that are currently separate records
- gathers multi-record functional families without flattening counterexamples
- reduces repeated top-level retrieval results for the same underlying point
- surfaces the strongest evidence and strongest counterpressure together
- makes future wave additions visibly checkable for duplicate pressure
- preserves all existing canonical relation records and provenance
- remains deterministic and fully testable

If the generated families merely restate relation tags or create additional clutter, the implementation has failed its purpose and should not be promoted into the reader.

## Rollout boundary

Phase 1 is backend-only consolidation and validation.

Do not alter public Bible rendering, relation ownership, canonical relation records, relation IDs, or aliases until the generated indexes demonstrate useful consolidation on the real corpus and pass full repository verification.
