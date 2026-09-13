# Potato House — Eightfold Placement Grammar

**Status:** research architecture; intended for promotion into the permanent House specification after corpus tests.

## Principle

Every thing should be able to answer a common set of placement questions without forcing every thing into one ontology or one folder tree.

The Eightfold Placement Grammar is therefore **relational**, not categorical. A person, country, law, neuron, source document, equation, Room, script, event, claim or artwork can all be located from these eight angles.

## The eight directions

| Direction | Potato term | Question | Structural meaning |
|---|---|---|---|
| **WITHIN** | **Room / Box / House** | Where does this belong? | bounded context, ownership, containment, interface boundary |
| **HERE** | **Plane** | At what operative frame is this being seen? | present context, scale, representation, jurisdiction, time-slice, active view |
| **UP** | **North / Mountain / Heaven** | What broader integration or orientation does this point toward? | abstraction, integration, composition, selected orientation, summit/goal |
| **DOWN** | **Roots / Soil / Archive** | What supports, precedes, causes, evidences or feeds this? | provenance, dependency, ancestry, causal/incentive support, historical depth |
| **OUT** | **Tree / Branch / Fruit / Seed** | What unfolds, differentiates, grows or results from this? | decomposition into branches, generativity, consequences, outputs, descendants |
| **ACROSS** | **Road / Relation / Stolon** | What is this connected to laterally? | peers, flows, comparisons, membership, influence, ownership, dependency, exchange |
| **THROUGH** | **Door / Ladder / Threshold** | How does this move or change? | transitions, guarded state change, context switch, promotion, migration, traversal |
| **STATE** | **Garden / Forge / Swamp / Dormancy / Wound / Repair** | What regime is this currently in? | health, viability, pressure, entanglement, maturity, maintenance, publication/research state |

These are not mutually exclusive physical directions. They are eight relational questions.

## Why this works

A single hierarchy cannot describe all of the following honestly:

- a Bible passage is inside a text, sourced from an edition, interpreted in many traditions, linked to themes, and may generate later interpretations;
- a country is part of regions/institutions, depends on infrastructure and trade, relates laterally to other states, and changes legal/political state through events;
- a scientific equation is inside a model/context, rests on assumptions and evidence, connects to other formalisms, and generates predictions;
- a source file is inside an Archive/Room, rests on acquisition provenance, connects to extracted Assertions, and may cross a Door into canonical use;
- a Room itself is inside the House, sits on the current Plane, has Roots in prior architecture, connects to neighboring Rooms, contains branches, and evolves through schema Doors.

The Eightfold Grammar gives each object a place without making all objects identical.

## Nested boxes

A Box is a bounded context. A Room is a meaningful Box with local semantics and interfaces.

Boxes may nest:

```text
House
└── Room
    └── Subcontext
        └── Dossier / Subject / Collection
            └── Internal section or component
```

Nesting never implies truth rank. It describes containment/context only.

Every Box should declare:

- what may be inside;
- what must remain outside;
- what it owns;
- what it merely references;
- which Doors cross its boundary;
- which Roads connect it to peers;
- what its North orientation is, if any;
- what health states apply.

## Plane

The Plane is the **currently operative frame**.

A thing can occupy multiple potential contexts while one Plane is active for a particular View or task.

Plane examples:

- empirical science;
- project canon;
- historical reconstruction;
- legal jurisdiction;
- a particular date or release;
- a country map view;
- a public-reader view versus an internal research view.

Plane therefore prevents the House from collapsing unlike interpretations into one flat page.

## Up: North, Mountain, Heaven

`UP` is integration/orientation, not moral or epistemic superiority.

Distinguish:

- **Mountain** — many → fewer; compression/integration;
- **North** — selected orientation or broader integrative direction;
- **Heaven** — maximal local coherence/integration reachable within the active context; a summit state, not automatic factual truth.

A Context may choose one primary North step for navigational clarity while still retaining other broader-context relations.

## Down: Roots, Soil, Archive

`DOWN` is depth/support, not inferiority.

Distinguish:

- **Root** — dependency, provenance, cause, antecedent, evidence or supporting relation;
- **Soil** — surrounding enabling conditions/environment;
- **Archive** — preserved historical/source depth;
- **Roots of Strife** — recurrent conditions feeding destructive regimes;
- **Roots of Ash** — residue from rupture that may become Archive, Mud, Soil or Forge input.

Downward traversal should explain why the current thing exists or why a claim is believed.

## Out: Tree, Branch, Fruit, Seed

`OUT` is differentiation/generation.

Distinguish:

- **Tree** — one/few → many; structured unfolding;
- **Branch** — a differentiated pathway/component/case;
- **Fruit** — useful consequence/output;
- **Seed** — compressed transferable pattern capable of regrowth;
- **Tree of Life** — viable/generative regime;
- **Tree of Strife** — recurrent branching into conflict/low-exit states;
- **World Tree** — connective/topological comparator joining differentiated regions.

A child/component relation and a downstream consequence are both outward relations but must retain distinct relation types.

## Across: Roads, Relations, Stolons

`ACROSS` captures lateral coupling.

Examples:

- comparison;
- ownership/control;
- alliance;
- influence;
- trade;
- information transfer;
- citation;
- similarity;
- contradiction;
- biological transport;
- membership;
- dependency;
- kinship.

Roads may carry typed flows. A Road is never an excuse to flatten all relations to an untyped graph edge.

## Through: Doors and Ladders

`THROUGH` captures transition.

A weak Door is navigation/context crossing.

A strong Door is a durable Transition with:

- source state/context;
- guard/preconditions;
- trigger;
- crossing Activity;
- destination state/context;
- preserved invariants;
- provenance;
- reversibility/rollback.

A Ladder is an ordered sequence of Doors.

Examples:

- raw source → archived source → extracted claim → reviewed claim → canonical knowledge;
- research → review → publication;
- historical record v1 → migrated schema v2;
- Room A → cross-Room View → Room B;
- component → system → broader system.

## State: Garden, Forge, Swamp and related regimes

`STATE` describes condition rather than location.

- **Garden** — viable environment where growth can proceed with autonomy and usable feedback;
- **Forge** — bounded pressure intentionally transformed into capability;
- **Swamp** — entanglement, unresolved ownership, feedback loops, opacity, blocked exit or accumulated unprocessed material;
- **Dormancy** — organized viable potential held inactive;
- **Wound** — damage requiring repair;
- **Repair** — active restoration;
- **Mature** — stable developed capability;
- **Ash** — residue after breakdown;
- **Mud** — mixed/unresolved material that may still be processed.

Swamp is not a folder and Archive is not Swamp by default.

## Universal address

Any durable object may expose a partial or full address:

```yaml
placement:
  within:
    room_ids: []
    context_ids: []
  here:
    plane_id: null
  up:
    north_ref: null
    broader_refs: []
  down:
    root_refs: []
    soil_refs: []
    archive_refs: []
  out:
    branch_refs: []
    fruit_refs: []
    seed_refs: []
  across:
    relation_refs: []
  through:
    door_refs: []
    ladder_refs: []
  state:
    regime: null
    maintenance: null
    viability: null
```

This address is a View over richer typed relations, not necessarily a duplicated authoritative block stored in every file.

## Website rendering contract

Every important public Subject/Room page should make the eightfold grammar usable without exposing all backend jargon at once.

Default page translation:

1. **Identity / You are here** — HERE
2. **Belongs to / Context** — WITHIN
3. **Broader context** — UP
4. **Inside / Branches / Consequences** — OUT
5. **Connections** — ACROSS
6. **History / Sources / Evidence** — DOWN
7. **Next steps / State changes / Related pathways** — THROUGH
8. **Status / Health / Research condition** — STATE when relevant

The public labels can be ordinary language while the backend retains the Potato grammar.

## Refinement principle

The same eight questions recurse at every scale.

A House has Rooms. A Room can itself be treated as a Box. A Subject can contain components. A Programme can contain phases. A source can contain passages. A page can contain sections. Each level can be located relative to broader and narrower contexts without changing the universal grammar.

Thus “everything has a place” means:

> every meaningful object can be located **within, here, up, down, out, across, through, and in-state**, even when some directions are intentionally empty.
