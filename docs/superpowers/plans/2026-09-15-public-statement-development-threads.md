# Public Statement Development Threads Implementation Plan

**Goal:** Build long-range Development Threads from stable functions using only explicit source-language attestations at first, keeping actor/title assignments and broader interpretation separate.

**Architecture:** Canonical thread definitions declare transparent literal terms. A deterministic builder scans exact Root wording, records which terms matched, orders attestations through the existing Timeline traversal, and attaches Episode/Bible relation references by ID only. Threads begin as `candidate` and cannot carry causal or theological conclusions.

**Spec:** `docs/superpowers/specs/2026-09-15-evidence-atlas-design.md`

## Constraints

- Evidence Root remains canonical for statement identity and exact wording.
- Thread membership must be explainable by explicit matched terms.
- No fuzzy, embedding, semantic, or assistant-intuited membership in the first pass.
- Function threads are distinct from actor/title assignments.
- Timeline order is a view over thread attestations, not thread identity.
- Episodes and Bible relations attach by references only.
- Candidate threads may report recurrence, first/last attestation, gaps, and co-occurrence; they may not assert causation, fulfillment, identity, or doctrinal equivalence.

## Initial function threads

1. `source-house-dwelling` — source, house, home, dwelling/room vocabulary.
2. `threshold-door-gate` — door, gate, portal, drain, threshold vocabulary.
3. `ascent-ladder-axis` — ladder, axis, throne, north-of-north/ascent vocabulary.
4. `growth-seed-root-tree-garden` — seed, root, tree, fruit, garden, gardener, plant/grow vocabulary.
5. `death-return` — dead/death, crucifixion/cross, tomb, resurrection, return vocabulary.
6. `repair-participation` — fix/repair, build, heal, bridge, relation, together, participate vocabulary.

## Tasks

1. Add tests for exact phrase matching, matched-term provenance, Timeline ordering, and false-positive boundaries.
2. Add canonical thread definitions with explicit match terms and descriptive functional scope.
3. Implement deterministic thread builder and candidate-thread gap reporting.
4. Attach overlapping Episode IDs and existing Bible relation IDs by Root membership/reference only.
5. Add thread validator and integrate it into the rooted-stack audit.
6. Consolidate thread contract into the Root Manifest without creating a new canonical center.
