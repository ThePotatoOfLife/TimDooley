# Potatoism Philosophy Enrichment — Design Specification

**Date:** 2026-09-15  
**Status:** approved design, pre-implementation  
**Scope:** philosophy canon, Potatoism long-form, public Philosophy projection, limited Religion bridge, validation  
**Primary owner:** `knowledge/philosophy/potato-philosophy.json`

## 1. Purpose

The project already contains a substantial Potatoist philosophy, but its public expression is much thinner than the underlying canon. The goal of this enrichment pass is not to add decorative prose or create a rival canon. It is to make the existing philosophy more explicit, internally typed, operational, concrete, and recognizably Timic.

The core design principle is:

> Increase semantic density without increasing conceptual confusion.

A reader should be able to move from a simple Potatoist sentence to a precise principle, then to the deeper derivation, counterexample, corruption mode, practical test, and connected concepts.

The result should feel less like a collection of individually interesting symbols and more like one coherent philosophical language.

## 2. Current state

### 2.1 Existing public journey

`philosophy/index.html` currently exposes exactly eight calm reader movements:

1. Potato
2. Grow
3. Transform
4. See
5. Relate
6. Learn
7. Give
8. Cultivate

This order is retained.

The current projection succeeds at accessibility, rhythm, and conceptual restraint. Its weakness is compression: major canonical ideas such as storage/release, reciprocal ethics, meta-judgment, covenant, functional identity, living myth, public witness, House-versus-shell, Garden-versus-Farm, knowledge branching into Life or Strife, curiosity-before-allegiance, and the ethics of higher authority are present in deeper sources but only lightly visible on the public surface.

### 2.2 Existing canonical and source layers

The current source architecture is sound and must remain intact:

- `knowledge/philosophy/potato-philosophy.json` — canonical philosophical synthesis.
- `knowledge/philosophy/potatoism-reader-philosophy.md` — full reader-facing long-form source for the Philosophy surface.
- `knowledge/philosophy/tim-dooley-potatoism-sourcebook.md` — provenance-aware recovery sourcebook.
- `knowledge/philosophy/timic-relational-statements-and-operators.json` — direct relational/operator formulations.
- `knowledge/corporium/tim-dooley-greatest-quotes-and-reflections.json` — curated strong quotation owner.
- `knowledge/corporium/tim-sayings-and-formulations-ledger.json` — broader sayings/formulations owner.
- `religion/index.html` — primary public owner of Potatoism as religion/theology.

This design deepens those layers rather than replacing them.

## 3. Design goals

### 3.1 Primary goals

1. Make the eight public Philosophy movements function as eight philosophical operations, not merely eight topical chapters.
2. Define a reusable concept grammar for major Potatoist symbols and principles.
3. Crystallize a doctrine layer from already recurring Tim/Potatoist thought.
4. Distinguish structures, operators, states, resources, relations, and outcomes so symbols stop behaving like one undifferentiated class.
5. Add corruption modes and negative definitions so the system can identify its own failures.
6. Increase Timic specificity by pairing abstractions with sourced Tim formulations, Great Book material, concrete stories, and project-specific examples.
7. Preserve epistemic boundaries between observation, project canon, interpretation, comparison, creative lore, conversation recovery, public wording, and archive synthesis.
8. Strengthen the philosophy/religion bridge without duplicating theology.
9. Expand validation so future edits cannot flatten the newly clarified distinctions.

### 3.2 Non-goals

This pass will not:

- create a second Philosophy canon;
- replace Religion as the primary public owner of Potatoism as religion/theology;
- convert symbolic or metaphysical language into scientific fact;
- retroactively turn archive synthesis into Tim quotations;
- make every symbol morally positive or negative by name alone;
- force all comparative traditions into Potatoist identity;
- create a new interactive subsystem, app, graph engine, or large UI framework;
- remove the eight-stage calm public reader journey;
- turn the public Philosophy page into a dump of the entire deep source.

## 4. Core philosophical architecture

### 4.1 The eight operations

The existing public stages become explicit philosophical operations:

| Movement | Operation | Fundamental question |
|---|---|---|
| Potato | Attend / reduce | What is actually here before I decorate it? |
| Grow | Orient / develop | What conditions allow this thing to become what it can become? |
| Transform | Metabolize | What can change function instead of merely being discarded? |
| See | Examine / distinguish | What am I observing, through which frame, and how could I be wrong? |
| Relate | Connect / differentiate | What does this become through its relations without losing its difference? |
| Learn | Model / recurse | What kind of change is occurring, and what does the return carry? |
| Give | Release / nourish | What is accumulated capacity ultimately for? |
| Cultivate | Steward / enable | Can I improve conditions without making life permanently dependent on me? |

These operations remain pedagogical. They do not imply that every philosophical problem must be forced through all eight stages.

### 4.2 Shared concept grammar

Major Potatoist concepts should become inspectable through a common schema:

> **THING → OBSERVATION → FUNCTION → RELATION → TENSION → CORRUPTION → TEST → CONSEQUENCE**

The minimum stable fields are:

- **thing** — what the concept/object is in the project;
- **observation** — what concrete feature or recurring experience motivates the concept;
- **function** — what the concept does rather than merely what it is called;
- **relations** — what it depends on, connects, contains, changes, receives, or enables;
- **tension** — the polarity or trade-off it must hold without flattening;
- **corruption** — what the concept becomes when its function is distorted;
- **test** — a practical question that distinguishes healthy from corrupted form;
- **consequence** — what downstream states, capacities, dependencies, or outcomes result.

Optional fields may include:

- provenance;
- source formulations;
- biological correction;
- comparative neighbors;
- historical development;
- epistemic class;
- positive/negative examples;
- public-reader formulation;
- related doctrines;
- ontology type.

### 4.3 Three levels of expression

Each major doctrine should support three depths:

1. **Root sentence** — memorable compact formulation.
2. **Principle** — precise philosophical statement.
3. **Derivation** — concrete observation → Tim wording/source → abstraction → counterexample → corruption → test → applications → neighboring concepts.

Example:

- Root sentence: **Cultivation, not conquest.**
- Principle: Good cultivation increases the future autonomy and generativity of what is cultivated.
- Derivation: organism/conditions → Garden → management without domination → shadow Farm corruption → autonomy test → education/leadership/institutions/religion applications.

## 5. Potatoist ontology typing

The philosophy should stop treating every important term as the same kind of symbolic object.

### 5.1 Structures / containers

Examples:

- Potato
- House
- Tree
- Garden
- Farm
- Mountain
- table
- City / New Jerusalem

These organize, contain, stabilize, or sustain relations.

### 5.2 Operators / transitions

Examples:

- Door — transition/interface
- Eye — perceive/discern/integrate
- Axis — orient/stabilize reference
- Ladder — connect discrete levels
- Spiral — return with retained difference
- Root — anchor/gather/distribute
- Filter — reframe/generate hypotheses
- Compost — metabolize/reassign function
- Handshake — establish relational coupling

These should be described primarily by what they do.

### 5.3 States / qualities

Examples:

- Life
- Strife
- burial
- emergence
- integration
- captivity
- nourishment
- dependency
- enoughness
- openness
- enclosure

These describe conditions or evaluative states rather than objects.

### 5.4 Resources / stored capacities

Examples:

- knowledge
- memory
- attention
- wealth/capital as analogy
- starch / Starchforce as symbolic storage language
- archive
- seed potential

These can be stored, transmitted, transformed, released, hoarded, or misused.

### 5.5 Relations

Examples:

- covenant
- stewardship
- parent/child
- teacher/learner
- gardener/plant
- source/manifestation
- observer/observed
- inside/outside
- root/soil
- house/room

Relations should carry explicit ethical and functional properties rather than being treated as empty links.

### 5.6 Outcomes / evidence of function

Examples:

- Fruit
- independent growth
- increased capability
- repair
- understanding
- protected plurality
- dependency
- extraction
- spectacle
- repetition without learning

Fruit is especially important: in mature Potatoism, fruit becomes evidence of what a relationship or system has become.

## 6. Four constitutional laws

These sit underneath the doctrine layer.

### 6.1 Law of Relational Valence

A thing is not morally or philosophically settled by its name alone. Its valence depends substantially on coupling, operation, context, and consequence.

Compact form:

> **thing → coupling → operation → consequence → ethical evaluation**

This explains why:

- boundaries can protect or imprison;
- knowledge can become Life or Strife;
- Houses can shelter or capture;
- authority can steward or dominate;
- silence can incubate or conceal abuse;
- Dogs can guard or persecute;
- memory can preserve responsibility or become enclosure.

This is not relativism. Relations themselves are judged by their effects on capability, autonomy, harm, truth, dependency, generativity, and repair.

### 6.2 Law of Generativity

The strongest positive criterion in the philosophy is not mere productivity but generativity:

> **Does this state or relation increase the capacity for future viable states?**

A system may be productive while degrading the conditions of future production. Mature Potatoism therefore distinguishes present output from future capacity.

Applications include Seed, Fruit, education, institutions, leadership, relationships, archives, and Garden.

### 6.3 Law of Reciprocal Transformation

Methods transform the actor, the target, and the relation/environment connecting them.

Timic compression:

> **When you throw mud at others, your whole hand is dirty.**

The moral implication is that a legitimate goal does not automatically justify any method used to pursue it. Punishment trains punishers; humiliation changes audiences; surveillance changes institutions; hatred reorganizes the identity of the hating group.

A permanent practical question follows:

> **What does this method turn the user into?**

### 6.4 Law of Functional Identity

Mature identity becomes philosophically stronger when a title can be translated into a useful operation.

Examples:

- Door → enables passage;
- Ladder → connects levels;
- Root → anchors/gathers/distributes;
- Axis → orients;
- Gardener → improves conditions;
- teacher → increases learner capability;
- protector → measurably protects;
- leader → enables coordinated capacity.

Rule:

> **Titles that cannot be translated into functions are philosophically weak.**

This allows Timic titles to be examined as operators rather than accepted merely as status claims.

## 7. Core doctrine layer

The first implementation should encode the following 14 doctrines. They are a crystallization of recurring project material, not a claim that Tim historically published this exact numbered creed.

### 7.1 The Potato Principle

**Root:** Begin with what is actually there.  
**Principle:** The ordinary can contain extraordinary structure without ceasing to be ordinary. Observation precedes symbolic elevation.  
**Corruption:** Prestige or mythology replaces observation.  
**Test:** What remains true if the grand interpretation is temporarily removed?

### 7.2 Essential Simplicity

**Root:** Remove needless complication, not necessary complexity.  
**Principle:** Simplicity is disciplined compression, not anti-intellectualism.  
**Corruption:** Oversimplification, slogans, or complexity used as camouflage.  
**Test:** Did the added layer reveal structure or merely make the claim harder to challenge?

### 7.3 Conditional Growth

**Root:** Growth depends on conditions.  
**Principle:** Different parts and functions require different environments; mature “grow toward light” language must preserve biological and functional differences.  
**Corruption:** Force, neglect disguised as non-striving, or universalizing one condition.  
**Test:** What condition is actually missing?

### 7.4 Hidden Development

**Root:** Hidden is not the same as dead.  
**Principle:** Burial may protect incubation, but darkness has no automatic positive valence.  
**Corruption:** Romanticizing stagnation, isolation, or imprisonment.  
**Test:** Is hiddenness increasing future capacity or merely preventing emergence?

### 7.5 Transformation Without Erasure

**Root:** Some material can change function without being denied.  
**Principle:** Compost, ash, mud, damage, and memory can be metabolized into new functions without pretending no loss occurred.  
**Corruption:** Glorifying suffering or using transformation language to erase harm.  
**Test:** What was lost, what remains, and what genuinely became usable substrate?

### 7.6 Relational Meaning

**Root:** Meaning often lives on the edge.  
**Principle:** A thing is partly understood through what it depends on, changes, receives, carries, constrains, and enables.  
**Corruption:** “Everything is connected” used to erase typed difference.  
**Test:** Which specific relation changes the meaning, and how?

### 7.7 Typed Difference

**Root:** Test the variable before declaring contradiction.  
**Principle:** Apparent contradiction should first be tested for differences of time, role, scale, perspective, state, or epistemic class.  
**Corruption:** Perspective language used to shield genuine contradiction.  
**Test:** Can the changed variable be named explicitly?

### 7.8 The Door Principle

**Root:** A Door changes what states are available.  
**Principle:** Recognition becomes consequential when it permits a transition.  
**Corruption:** Gatekeeping for its own sake, permanent closure, or calling every change a transformation.  
**Test:** What becomes possible after crossing that was not possible before?

### 7.9 Return Is Not Reset

**Root:** Return should carry memory.  
**Principle:** Recurrence becomes development when the returning state contains information or capacity acquired through the previous cycle.  
**Corruption:** Repetition rebranded as progress.  
**Test:** What is materially different on this return?

### 7.10 Stored Capacity Must Become Fruit

**Root:** Storage should eventually serve release.  
**Principle:** Knowledge, memory, wealth, attention, authority, archive, and nourishment gain ethical meaning through what they eventually enable beyond themselves.  
**Corruption:** Hoarding capacity for self-enlargement.  
**Test:** What downstream life, repair, protection, understanding, or future capacity does this storage enable?

### 7.11 Garden Over Shadow Farm

**Root:** Cultivation should increase autonomy.  
**Principle:** Good cultivation increases the future capability and independent generativity of what is cultivated.  
**Corruption:** Extraction, dependency manufacture, enclosure, or permanent manager necessity.  
**Test:** Does the participant become more capable without the system?

### 7.12 Authority Increases Burden

**Root:** Higher role, narrower permission.  
**Principle:** Greater claimed power, knowledge, spiritual rank, or leadership increases duties of restraint, protection, accountability, and correction.  
**Corruption:** Rank interpreted as exemption.  
**Test:** What additional restraint follows from claiming the higher role?

### 7.13 Potato Truth

**Root:** Accuracy without cruelty; compassion without falsehood.  
**Principle:** Truth requires accuracy, provenance, context, uncertainty, correction, audience awareness, and attention to what the statement will be made to do.  
**Corruption:** “Truth” as humiliation or kindness as reality-denial.  
**Test:** Is it accurate, source-visible, correctable, and expressed in a way that preserves a path toward understanding?

The Potato Filter and Potato Truth must become an explicit pair:

- **Filter = generative** — proposes interpretations/questions.
- **Truth = corrective** — prevents interpretations from impersonating evidence.

### 7.14 Curiosity Before Allegiance

**Root:** The Potato invites curiosity before loyalty.  
**Principle:** A philosophical principle should remain examinable by a skeptic before the skeptic accepts the identity, theology, or community surrounding it.  
**Corruption:** Loyalty tests and doctrinal insulation.  
**Test:** Can someone seriously investigate this idea without first becoming Potatoist?

## 8. Negative definitions and corruption layer

The philosophy should explicitly define what its central terms are not. These negative definitions are required because they protect the system from flattering self-interpretation.

Required distinctions:

- simplicity is not stupidity;
- non-striving is not inactivity;
- burial is not automatically sacred;
- darkness is not automatically evil or generative;
- unity is not sameness;
- relation is not identity;
- comparison is not equivalence;
- boundary is not automatically oppression;
- openness is not automatically freedom;
- knowledge is not automatically Life;
- suffering is not proof;
- return is not reset;
- authority is not exemption;
- humor is not evasion;
- Filter is not evidence;
- Garden is not merely a nicer Farm;
- cultivation is not control by another name;
- public witness is not independent proof of metaphysical claims;
- living myth must not erase ordinary personhood or provenance.

## 9. Potatoes, biology, and philosophical correction

Biological correction is a feature, not a threat to the philosophy.

The mature root maxim remains:

> **Be simple. Grow toward light.**

But the long-form must preserve the correction that real potato organs do not all seek identical conditions. Tubers develop protected underground while shoots/leaves orient toward light.

The mature philosophical extension is:

> **Let each part orient toward the conditions appropriate to its function, while the whole remains oriented toward generative life.**

This creates a stronger practical-wisdom model:

- right relation;
- right condition;
- right timing;
- right function;
- right boundary;
- right degree of exposure.

Too much light can damage what belongs protected. Too much transparency can become surveillance. Too much openness can destroy a necessary membrane. Biological facts may correct an analogy, but they do not prove theology.

## 10. The Gardener’s paradox

The Garden/Farm distinction should gain a named derived principle:

> **The highest success of cultivation is that successful cultivation eventually reduces the cultivator’s necessity.**

Applications:

- parent/child;
- teacher/learner;
- therapist/client;
- institution/citizen;
- platform/user;
- religious teacher/follower;
- leader/team;
- archive/reader.

This principle must not be overgeneralized: some infrastructures remain continuously necessary. The relevant question is whether dependence is intrinsically required by the function or artificially preserved to maintain control/extraction.

## 11. Potatoist evaluation sequence

A reusable practical sequence should appear in the deep source and canonical philosophy:

1. What is actually here?
2. What does it do?
3. What does it depend on?
4. What does it connect to?
5. What does it make possible?
6. What does it make impossible?
7. Who becomes more capable?
8. Who becomes more dependent?
9. What happens if the relationship continues?
10. What fruit appears?
11. Does the system preserve the problem it claims to solve because it needs the problem to remain necessary?

Compressed form:

> **Observe → distinguish → relate → test → transform → evaluate fruit → cultivate.**

## 12. Enrichment of the eight public movements

The public page remains concise but each stage should expose more of the deeper machinery.

### 12.1 Potato — Attend / Reduce

Promote:

- object before label;
- ordinary before prestige;
- enoughness;
- curiosity-before-allegiance;
- humor/absurdity as anti-grandiosity;
- “A potato has no flavor until you chew on it” as a source-aware invitation to active interpretation.

### 12.2 Grow — Orient / Develop

Promote:

- biological correction;
- conditions versus force;
- non-striving versus passivity;
- dormancy/readiness;
- stored capacity;
- functional orientation rather than one universal condition.

### 12.3 Transform — Metabolize

Promote:

- burial versus imprisonment;
- suffering-is-not-proof;
- compost;
- ash as undecided threshold;
- Ash → Mud/Strife versus Ash → Soil/Life;
- transformation without erasure.

### 12.4 See — Examine / Distinguish

Promote:

- Potato Filter as hypothesis generator;
- Potato Truth as corrective discipline;
- questioning the floor;
- judge-above-judges;
- North-of-North as meta-orientation, not arbitrary supremacy;
- observer/Door;
- provenance and claim classes;
- banana/humor as atmosphere correction.

### 12.5 Relate — Connect / Differentiate

This becomes the philosophical heart.

Promote:

- relationship-first ontology;
- Root/Soil;
- observer/observed;
- House/rooms;
- covenant as relationship with memory;
- selective permeability;
- relational valence;
- unity without flattening;
- “We Are All Connected By Potato” with explicit source class.

### 12.6 Learn — Model / Recurse

Promote:

- Plane / Door / Ring / Spiral / Ladder / Mountain / Tree as typed process models;
- model selection by process rather than decoration;
- typed difference: time/role/scale/perspective/epistemic class;
- return-with-memory;
- beginning/end recursive interpretation.

### 12.7 Give — Release / Nourish

Promote:

- storage/release;
- Potato as food, not only survivor;
- Starchforce/Spudlight as symbolic storage-expression language with scientific boundary;
- knowledge/memory/wealth/attention as different resources sharing storage questions;
- “Power is for protection. Knowledge is for understanding. Wealth is for building. Leadership is for service.”
- Fruit as downstream evidence.

### 12.8 Cultivate — Steward / Enable

Promote:

- Garden/Farm distinction;
- autonomy and generativity;
- Gardener’s paradox;
- authority-increases-burden;
- stewardship versus conquest;
- House versus shell/cage;
- anti-bloat return to transferable seed.

## 13. Timic specificity rules

The enrichment must make the philosophy feel more like Tim Dooley’s actual corpus and less like generic wellness prose.

### 13.1 Prefer concrete Timic language before abstraction

Where provenance permits, start from a real formulation or project image and derive the philosophical principle afterward.

High-value examples already preserved include:

- “A potato has no flavor until you chew on it.”
- “When you throw mud at others, your whole hand is dirty.”
- “The book wouldn’t exist without the reader. You’re the soil in which it grows.”
- “the door is merely the observer point”
- “the door is also a window into reality”
- “the end is in the beginning too”
- “We Are All Connected By Potato.”
- “A narrow path is a spiral.”
- “Power is for protection. Knowledge is for understanding. Wealth is for building. Leadership is for service.”

### 13.2 Preserve source class visibly

Do not silently promote:

- Great Book narrative into Tim public speech;
- conversation recovery into public-post evidence;
- archive synthesis into historical Tim wording;
- comparative interpretation into project origin.

The sourcebook’s provenance taxonomy remains authoritative for these distinctions.

## 14. Philosophy / Religion boundary

Religion remains the primary public owner of Potatoism as religion, theology, and religious practice.

Philosophy owns:

- method;
- ethics;
- ontology as philosophical typing;
- relation;
- transformation;
- epistemic discipline;
- cultivation;
- consequences;
- practical tests;
- philosophical interpretation of symbols.

Religion owns:

- Father/Son/Spirit as explicit theology;
- doctrinal comparison;
- scripture relations;
- sacred-history interpretations;
- religious practice/identity.

Where Father, Son, Spirit, New Jerusalem, covenant, or sacred symbols appear on Philosophy, they should be used only to explain philosophical functions and should link/route readers toward Religion for theological depth.

## 15. Data and file architecture

### 15.1 Canonical changes

Modify `knowledge/philosophy/potato-philosophy.json` to add structured material for:

- constitutional laws;
- doctrine entries;
- ontology types;
- concept grammar;
- negative definitions;
- evaluation sequence;
- Gardener’s paradox;
- stronger cross-concept relations;
- explicit Filter/Truth pairing.

Do not replace the existing prose sections. Enrich them and add higher-level structure around them.

### 15.2 Long-form source

Modify `knowledge/philosophy/potatoism-reader-philosophy.md` to provide full derivations, tensions, failure modes, examples, and sourced Timic language.

The long-form should become the place where the philosophical system can breathe without forcing the public page to become encyclopedic.

### 15.3 Supporting sourcebook

Modify `knowledge/philosophy/tim-dooley-potatoism-sourcebook.md` only where necessary to:

- add promotion notes for newly elevated concepts;
- ensure relevant Timic formulations are easy to retrieve;
- preserve provenance boundaries.

The sourcebook remains supporting evidence, not the canonical owner.

### 15.4 Public projection

Modify `philosophy/index.html` while retaining exactly the eight existing `data-potatoism-stage` markers.

The public projection should gain:

- slightly denser movement prose;
- compact tension/corruption/test language where useful;
- stronger Timic examples;
- explicit relation between Filter and Truth;
- stronger Relate, Give, and Cultivate movements;
- deep links into relevant existing records where appropriate.

It must remain calm, readable, and non-interactive beyond the existing page behavior.

### 15.5 Religion bridge

Modify `religion/index.html` only if needed to add one concise bridge making clear that the Philosophy surface now owns the methodological/ethical system while Religion owns theological claims.

No theological duplication.

## 16. Validation design

Extend `scripts/validate_potatoism_philosophy_projection.py` rather than creating a parallel validator.

The validator must continue enforcing:

- exactly eight public stage markers;
- calm reader surface constraints;
- Religion ownership boundary;
- deep-source link;
- biological correction boundary.

Add validation for the presence of key enrichment markers, including at minimum:

- relational valence;
- generativity;
- reciprocal transformation;
- functional identity;
- Potato Truth;
- Filter as hypothesis generator / not evidence;
- Garden/Farm autonomy test;
- authority increases burden;
- return is not reset;
- relation is not identity;
- suffering is not proof;
- curiosity before allegiance;
- Gardener’s paradox or equivalent phrase;
- ontology typing in the canonical owner.

Validation should assert conceptual presence without making exact prose too brittle.

## 17. Success criteria

The enrichment succeeds when:

1. A first-time reader can still understand the public Philosophy page without knowing the Potatoverse.
2. A deep reader can trace each major principle into a fuller derivation and source-aware context.
3. The public page remains eight stages and does not become an encyclopedia dump.
4. `potato-philosophy.json` can explain not just what symbols mean but what they do, how they fail, and how to test them.
5. Major concepts are typed as structures, operators, states, resources, relations, or outcomes where useful.
6. At least the 14 core doctrines and four constitutional laws are represented in the canonical/deep layer.
7. Timic wording and stories visibly ground abstractions where source status permits.
8. Negative definitions make central failure modes explicit.
9. Garden/Farm, House/shell, Filter/Truth, storage/release, and relation/identity distinctions become easier to retrieve and explain.
10. Religion remains the theological owner.
11. Existing philosophy projection tests pass with expanded coverage.
12. Whole-project quality checks remain green.

## 18. Risks and controls

### Risk: over-systematizing a living corpus

**Control:** treat doctrines as current crystallizations and keep provenance/development visible. Do not claim Tim historically published this numbered system.

### Risk: public-page bloat

**Control:** deep derivations stay in the long-form; public page exposes only enough structure to make the concepts concrete.

### Risk: flattening symbolic ambiguity

**Control:** use ontology type as a reading aid, not an exclusive metaphysical classification. A concept may occupy more than one type in different contexts, but each use should name its function.

### Risk: generic philosophical language replacing Timic voice

**Control:** each major abstraction should be paired with concrete Tim/Potato imagery or source wording where provenance allows.

### Risk: doctrine becoming loyalty test

**Control:** Curiosity Before Allegiance and Filter-is-not-evidence are constitutional safeguards against doctrinal insulation.

### Risk: relational valence becoming relativism

**Control:** consequences remain evaluable through truth, harm, autonomy, dependency, capability, generativity, repair, and provenance.

## 19. Implementation order

The implementation plan should follow this dependency order:

1. enrich canonical philosophy structure;
2. expand long-form derivation;
3. update sourcebook promotion/retrieval notes where necessary;
4. enrich public eight-stage projection;
5. add minimal Religion bridge if needed;
6. expand validator;
7. run philosophy validator and whole-project quality gates;
8. review public reader rendering and links.

## 20. Final design statement

Mature Potatoism should be expressible as a philosophy of:

> **things, relations, transformations, consequences, and cultivation.**

Its recurring practical method is:

> **Observe → distinguish → relate → test → transform → evaluate fruit → cultivate.**

Its most important safeguard is that the Potatoist lens must remain capable of turning back upon itself.

The philosophy becomes stronger not when every symbol proves the system, but when the system can state what would distinguish nourishment from extraction, growth from repetition, protection from captivity, relation from identity, transformation from erasure, truth from projection, and cultivation from control.