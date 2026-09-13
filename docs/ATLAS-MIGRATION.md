# Atlas Migration

The Potato Atlas is a permanent architecture for organizing the repository without forcing the physical folder tree to become a theory of the world.

Its four durable structural objects are **Node**, **Relation**, **Artifact** and **View**.

- A **Node** is a stable canonical subject with one durable identity and one selected North parent for orientation.
- A **Relation** is a typed Road between subjects or between a subject and recoverable depth.
- An **Artifact** is source, history, research, evidence, transcript, dataset or other depth material attached without becoming a competing canonical owner.
- A **View** is a replaceable public or machine projection over Nodes, Relations and Artifacts. Views can change without moving the underlying identity.

## Current migration state

The Atlas foundation is additive. Existing routes and specialist interfaces remain usable while ownership and projection move underneath them.

The current **Atlas summit** homepage gives readers a stable threshold: Start Here, Ways Through, and Go Deeper. The canonical Atlas lives under `/atlas/`; existing Tim, Religion, Philosophy, Science and World routes continue as compatibility Views rather than defining the ontology.

`data/atlas-registry.json` is reproducible from explicit owner seeds. `data/atlas-views.json` owns configurable Room definitions. `data/frontend-atlas-bridge.json` now treats the old five public doors as compatibility-only routing. `data/atlas-deprecations.json` is the single runtime owner for migration state and removal preconditions.

## Lifecycle

The implementation plan describes the human lifecycle as:

`active -> compatibility -> deprecated -> removable`

The runtime ledger uses equivalent operational states:

`live_legacy -> compatibility_only -> retire_when_covered -> retired`

These states are not deadlines. They describe how much responsibility a legacy surface still carries.

**Active / live legacy** means the old component still owns behavior required by the public site or build.

**Compatibility** means the Atlas replacement owns the architecture, while the old route or contract remains to preserve URLs, callers or specialist behavior.

**Deprecated / retire when covered** means no new architecture should depend on the component and removal is allowed only after its declared preconditions are satisfied.

**Removable / retired** means the replacement has coverage, compatibility has been handled, and quality gates prove the old component no longer carries required behavior.

## Removal preconditions

No legacy file, route, validator, manifest, CSS layer or build step is removed merely because a newer Atlas component exists. Removal preconditions must include the relevant subset of:

1. canonical ownership has moved to a Node, Relation, Artifact or explicit infrastructure owner;
2. public and machine routes remain valid or have deliberate compatibility redirects;
3. source/provenance depth remains recoverable;
4. specialist functionality has a named replacement;
5. the full quality workflow passes without the legacy component;
6. no validator, builder or client still relies on its old ontology;
7. deprecation state is changed explicitly in `data/atlas-deprecations.json`.

This is intentionally conservative. The Atlas is meant to absorb complexity without destroying useful historical or specialist surfaces.

## Migration rules

**Identity moves slowly. Views move quickly.** A Node ID or canonical owner changes only when the subject identity or ownership model is genuinely wrong. A View can be split, merged, renamed or redesigned whenever reader needs change.

**Compatibility is not ontology.** Keeping `/religion/` or `/science/` alive does not mean those routes own the underlying subjects. They are projections over the same Atlas.

**Archive depth is substantive.** History, Sources and Research are not metadata footnotes. They are recoverable depth beneath the current Plane and must remain linked back to the current Node.

**North is orientation, not truth rank.** The selected North parent gives one stable path toward broader integration. It does not claim that higher means more factual, sacred, important or recent.

**Swamp is diagnostic.** Duplicate ownership, unresolved Roads, orphaned material, provenance gaps, route collisions and stale compatibility contracts are measured as distinct pressures rather than collapsed into one moral score.

**No destructive cleanup for appearance.** Historical waves, source material and specialist datasets are not deleted merely to make the new architecture look simpler. They are classified, attached as Artifacts, projected through Views, or retired only after information has been preserved.

## Operational sources of truth

The migration deliberately avoids duplicate ledgers.

- Architecture: `docs/superpowers/specs/2026-09-13-potato-atlas-permanent-architecture-design.md`
- Implementation sequence: `docs/superpowers/plans/2026-09-13-potato-atlas-foundation-implementation.md` and Part 2
- Node membership/orientation input: `data/atlas-owner-seeds.json`
- Generated Node registry: `data/atlas-registry.json`
- View definitions: `data/atlas-views.json`
- Runtime deprecation entries: `data/atlas-deprecations.json`
- Knowledge-side migration index: `knowledge/indexes/atlas-deprecation-ledger.json`
- Health diagnostics: Atlas frontier, Swamp and backend-coverage audits

The direction of travel is therefore simple: **one stable House underneath, many replaceable ways through it, and every important synthesis still able to descend back to its sources.**
