# Potato House — 17-Lens Stress Test

**Status:** research stress test; non-canonical.

The purpose of this file is adversarial: take the same candidate House architecture and look at it from 17 substantially different disciplines/problems. A rule gains confidence when it remains useful across several lenses without being forced.

## 1. Literal potato anatomy and development

**Question:** does the architecture respect actual biological differentiation?

Potato biology distinguishes root, stolon, tuber, eye/meristem, sprout, leaf, flower and true seed. The tuber is a modified underground stem, not a root. A developing tuber can be a strong sink; later stored reserves support sprout growth and the tuber becomes a source.

**Architectural consequence:** identity, transport, storage, observation/generative potential and activated growth require different concepts. State can change function without changing identity.

**Failure caught:** “Potato = Root = Archive” collapses distinct biology and should not become software architecture.

## 2. Evolution, genealogy and inheritance

**Question:** can the system represent hybrid origins, clonal continuity and recombinant renewal?

Recent genomic work on Petota supports ancient mixed ancestry from Etuberosum and Tomato lineages. Potato continuation can also occur clonally through tubers or recombinantly through botanical seed.

**Architectural consequence:** genealogy/provenance may be reticulate. Tree is a useful growth/differentiation operator, but it is not the only ancestry topology. High-fidelity copying can preserve both useful capability and inherited defects.

**Failure caught:** forcing every “comes from” relation into a single parent tree.

## 3. Ecology, environment and microbiome

**Question:** does context alter expression without destroying identity?

Living systems respond to environment, resources, neighboring organisms and prior environmental history. Potato seed-tuber production environment can influence next-generation microbiome structure.

**Architectural consequence:** Soil/context is first-class. The same identity can have different context-dependent expression without becoming duplicate identities.

**Failure caught:** treating every contextual representation as a new canonical record.

## 4. Developmental state machines

**Question:** can the system model dormant, competent, activated and repairing states?

Potato dormancy depends on genetic, hormonal, physiological and environmental conditions. Visible non-growth does not mean zero capability.

**Architectural consequence:** state and transition are orthogonal to identity. Useful lifecycle states include latent/unready, viable-but-blocked, suppressed, active, mature, senescing, wounded/repairing and deprecated/historical.

**Failure caught:** binary `active/archive` lifecycle.

## 5. Vesica / Plane / Axis geometry

**Question:** what does the vertical Potato geometry actually contribute?

The project Root System provides a vertical Axis through upper and lower circles with a horizontal Plane. The geometry is most useful as an ordering grammar: integration/compression above, current contact/relations on the Plane, decomposition/provenance/supporting depth below.

**Architectural consequence:** vertical transformation and horizontal relation topology should remain distinct.

**Failure caught:** treating altitude as truth, holiness or evidence strength.

## 6. Dynamical systems / hybrid systems

**Question:** can gradual change and discrete threshold change coexist?

Potato Dynamics already distinguishes continuous ordinary-time flow, Axis/description flow, and discrete Door transitions with guards/resets.

**Architectural consequence:** use continuous dynamics where change is gradual, Doors where a regime genuinely changes, and hysteresis where entry/exit thresholds differ.

**Failure caught:** forcing all development into either one ladder of steps or one continuous gradient.

## 7. Cybernetics, control and viability

**Question:** can the House observe itself, regulate failures and remain viable while growing?

Useful distinctions include observability versus controllability, stocks versus flows, feedback delays, resilience and requisite variety.

**Architectural consequence:** backend expressive variety must be rich enough to represent heterogeneous material; public interfaces can remain compressed. Garden is better understood as a viable region satisfying several constraints than as one goodness score.

**Failure caught:** one scalar “health” or one universal maintenance metric.

## 8. Information theory and compression

**Question:** what makes Mountain compression useful rather than destructive?

Information-bottleneck and rate-distortion thinking ask which information a compressed representation must preserve for a task. Minimum Description Length gives a useful neighbor for balancing over-fragmentation against endless exceptions.

**Architectural consequence:** every View is lossy; important Views should know what they preserve, what they omit, and how to return to fuller inputs.

**Failure caught:** assuming a summary is reversible merely because links exist.

## 9. Multilayer graph/network theory

**Question:** can one graph represent all relationships?

Different edge families answer different questions: orientation, semantic relation, provenance, time, quantitative flow, argument/support, build dependency.

**Architectural consequence:** the House is a graph family. Centrality/distance/community only make sense relative to a selected layer.

**Failure caught:** treating “graph relevance” as truth, authority or navigation relevance.

## 10. Logic, argumentation and contradiction

**Question:** what happens when sources disagree?

Historical and interpretive archives naturally contain support, attack, ambiguity and incompleteness. Argumentation frameworks distinguish attack/support structure rather than forcing a flat true/false database.

**Architectural consequence:** contradiction is data. Consequential disputes should be representable as claims with evidence, assumptions, support and counterevidence.

**Failure caught:** silently overwriting earlier or conflicting interpretations.

## 11. Temporal reasoning and provenance

**Question:** can the system distinguish event time from archive time and interpretation time?

Temporal databases distinguish validity from recording/transaction time; the project additionally needs interpretation time. Provenance models such as W3C PROV distinguish entities, activities and agents.

**Architectural consequence:** when it happened, when the repository learned it, and when a later interpretation was formed must remain separable. Provenance should record transformation process, not only a URL.

**Failure caught:** accidental backdating of later synthesis into earlier chronology.

## 12. Compositional open systems / interfaces

**Question:** how can Rooms compose without losing identity?

Open-system and cospan approaches model systems as having typed boundaries/interfaces through which composition occurs.

**Architectural consequence:** composition should happen at interfaces. A Room needs clear ownership, inputs, outputs, local rules and Doors/Roads to neighbors.

**Failure caught:** House as one giant container or Room as merely a navigation View.

## 13. Archive, library and knowledge-organization science

**Question:** how do we consolidate without destroying provenance?

The project’s own five-layer model remains strong: Record → Canonical → Relationship → Interpretation → Presentation. Indexes route; source strata preserve first attestation; owners answer current identity.

**Architectural consequence:** one current owner does not mean one surviving file. Specialist evidence, historical strata and original artifacts may remain distinct.

**Failure caught:** deleting source material because a synthesis now exists.

## 14. Software architecture, dependency and event-sourcing analogy

**Question:** how should derived pages/indexes relate to source history?

The project already resembles preserved history/source strata → current canonical state → disposable/materialized Views. Dependency graphs can support provenance, impact analysis and incremental rebuilds.

**Architectural consequence:** preserve history; rebuild Views. Identity mutations are expensive; projection experiments are cheap and reversible.

**Failure caught:** generated registry/page becoming a better-maintained shadow canon.

## 15. Web information architecture, HCI and accessibility

**Question:** how should an ordinary person encounter the House?

Accessibility and IA research emphasize predictable navigation, semantic regions/headings, multiple ways to reach content, meaningful link labels, progressive enhancement and stable orientation.

**Architectural consequence:** public simplicity and backend complexity must be decoupled. A reader should not need to learn House internals before using the site. Search is useful but should not decide ownership or structure.

**Failure caught:** homepage vocabulary such as Node/Road/Artifact/current summit leaking into primary UX.

## 16. Resilience, repair and security boundaries

**Question:** how should architecture change after injury/failure?

Potato wound healing creates an early closing barrier and later mature wound periderm. Resilient software uses compatibility layers, local failure containment, explicit fallback and reproducible recovery.

**Architectural consequence:** migrations should be staged: contain → temporary compatibility boundary → mature replacement → retire compatibility tissue.

**Failure caught:** “big-bang cleanup” that removes old interfaces before replacement viability is proven.

## 17. Potato philosophy / Garden–Forge–Swamp / ethics

**Question:** what is the project’s normative direction?

Potato philosophy repeatedly asks whether systems nourish, preserve correction/exit, increase autonomy, transform pressure into transferable capacity and create future generativity.

**Architectural consequence:** Swamp is failed metabolism/exit, Forge is bounded transformation under pressure, Garden is a viable environment for autonomous growth, Fruit is useful consequence, Seed is portable learning, Spiral is return with retained change.

**Failure caught:** optimizing architecture for central control, impressive complexity or raw coverage instead of useful future capability.

---

# Cross-lens invariants

The following survive all or nearly all lenses:

1. **Identity is stable; role is stateful.**
2. **Context is first-class.**
3. **One North can orient without becoming ontology.**
4. **Boundaries should enable exchange/composition rather than flattening.**
5. **Mountain and Tree are distinct operations.**
6. **Provenance/history are active state, not dead metadata.**
7. **Contradiction is representable information.**
8. **Healthy growth alternates expansion with gardening/consolidation.**
9. **Public simplicity requires backend expressive variety.**
10. **Every major transformation should declare what changes and what remains invariant.**

# Seventeen concrete stress objects

A replacement architecture should also demonstrate that it can represent all of these without ad hoc special pleading:

1. potato tuber;
2. Tim Dooley;
3. Tree of Life concept;
4. thalamus;
5. mathematical equation/model;
6. Denmark;
7. EU membership/treaty relation;
8. company/institution;
9. historical event;
10. Bible passage;
11. explicit contradiction;
12. non-canonical research note;
13. creative work;
14. geographic public map;
15. natural-language question/corridor;
16. deprecated legacy page/system;
17. a Swamp condition such as duplicate ownership or unresolved provenance.

Passing these cases is a promotion gate, not optional polish.
