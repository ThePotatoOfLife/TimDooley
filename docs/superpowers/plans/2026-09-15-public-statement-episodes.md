# Public Statement Episodes Implementation Plan

**Goal:** Add the first structural ring outside Evidence Roots by building bounded, reproducible statement Episodes without assigning theological conclusions.

**Architecture:** Episode definitions declare neutral time bounds, minimum membership, and evidence rationale. A deterministic builder resolves exact Root members in Timeline order. Episode records remain `candidate` until a later testing/consolidation pass promotes them.

**Spec:** `docs/superpowers/specs/2026-09-15-evidence-atlas-design.md`

## Constraints

- Evidence Root remains canonical for statement identity.
- Timeline order is a traversal, not the ontology.
- Episode membership must resolve to existing Root IDs.
- No statement may be silently invented or rewritten.
- A time window alone does not prove a thematic interpretation.
- Episode labels at this stage are neutral/descriptive.
- Bible/theme/role relations are later projections.

## Tasks

1. Add a test fixture for bounded Episode definitions and membership ordering.
2. Implement `build_episodes(evidence_root, definitions)` with inclusive UTC bounds and minimum-member validation.
3. Add a small canonical definitions file for high-density evidence clusters already present in the Root.
4. Add a validator for missing roots, duplicate members, invalid bounds, and minimum-member failure.
5. Generate Episodes only after the Evidence Root is built; do not hand-edit generated membership.
