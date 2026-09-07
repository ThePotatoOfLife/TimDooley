# Research Integrity Audit

This audit is a repository-level control document. Expansion files must be additive, inspectable, source-aware and explicit about epistemic status.

## Canonical invariants

- `data/tree.json` is canonical and must not be reordered.
- `data/frame.json` defines the evidence classes and the rule that metaphor is not evidence.
- `data/tree-child-records.json` supplies real records for canonical children that are not promoted into the main node registry.
- `site.js` fails loudly when a canonical child has no backend record; it does not invent placeholder records.

## Verified recent expansion layers

- `data/expansions/religious-foundations-wave-011.json`
- `docs/QLIPHOTH-TREE-OF-STRIFE.md`
- `data/expansions/trajectory-topology-standard-model-spin-wave-013.json`
- `data/expansions/angel-demon-topology-wave-014.json`
- `docs/TRAJECTORY-TOPOLOGY-STANDARD-MODEL-SPIN-DEEP-DIVE.md`
- `data/expansions/sector-depth-round-010.json`

## Physics integrity

1. Never identify angels, demons or spiritual entities with particles, fields or quantum states.
2. Keep trajectory, configuration space, phase space, Hilbert space and spacetime distinct.
3. Keep gauge redundancy distinct from ordinary physical symmetry.
4. Keep spin distinct from classical rotation.
5. Keep helicity distinct from chirality, especially for massive particles.
6. Keep Standard Model structure distinct from speculative extensions.
7. Treat instantons, monopoles, vortices and domain walls as theory-dependent configurations.
8. Treat anomaly cancellation as a consistency condition of chiral gauge theory, not metaphysical evidence.
9. Mark religious/physics bridges as comparative, systems-analogy or project-interpretation.

## Religious integrity

1. `malakh` is a historical Hebrew messenger term; do not impose a modern generic angel ontology on every occurrence.
2. Biblical, Second Temple, rabbinic, Hekhalot, Zoharic and Lurianic layers remain distinguishable.
3. Jewish demonology is not equivalent to Christian demonology, Islamic jinn traditions or modern occult catalogues.
4. Samael, Lilith, Asmodeus, Azazel and the Watchers have different textual histories.
5. The later tenfold Western Qliphoth with named shells and demon correspondences is a reception layer, not a single ancient Jewish canonical diagram.
6. Structural similarity does not establish historical borrowing or ontological identity.

## Graph integrity

An expansion can remain outside `data/nodes.json` while it is a research layer. Promotion into the canonical graph is a separate operation requiring a clear definition, evidence class, source status and graph role. Expansion relationships must distinguish historical, observed, mathematical, comparative and project-interpretive edges.

## Verified Git history

The latest main branch before this audit was `02c35b2e8b34fdb91a8b1f5bb7780b1abcf8a714`, whose parent was the verified angel/demon expansion commit `6a0a93edffb16ab9251c2a99936cf0e9f671ef03`. The earlier trajectory/topology commit `4c5c8321783d13cf05131ec14201c35ddf0707a9` is an ancestor in that history. This confirms the recent work is committed history, not merely proposed patches.

## Next validation targets

- duplicate IDs;
- orphaned expansion relationships;
- source coverage;
- epistemic-status coverage;
- canonical-child coverage;
- exact Standard Model representation checks;
- historical source strata for angel/demon figures.
