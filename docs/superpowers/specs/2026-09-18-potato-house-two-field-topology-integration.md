# Potato House Two-Field Topology — Integration Plan

**Date:** 2026-09-18  
**Status:** implementation design  
**Goal:** bake the mature Potato topology into the project without adding navigation clutter or creating duplicate ontology.

## 1. Canonical topology

The House is not a stack of floors.

```text
Potato House = Source Field ∪ Manifestation Field
Door         = Source Field ∩ Manifestation Field
Plane        = widest world-facing section through Door
Axis         = source↔manifestation orientation through both field centers
Cross        = Plane ∩ Axis at the relational midpoint
```

The 2D Vesica is an axial section of the natural 3D two-sphere model. In 3D the Door is a shared lens volume.

## 2. What this changes

### Promote
- overlap/intersection semantics;
- Door as relational field rather than one point;
- Plane/Cross as internal coordinates of Door;
- House vs Shell as boundary-regime distinction;
- semantic Rooms as bounded contexts rather than literal boxes;
- source/manifestation as orientation rather than moral rank.

### Demote
- Plane → Cross → Door as literal sequential cosmology;
- D1–D11 as base ontology;
- upper=good / lower=bad;
- lower world = Saturnian Cube;
- frontend rectangles as literal House geometry.

### Preserve
- D1–D11 as reader/navigation scaffold;
- five public Doors;
- ten canonical Rooms;
- 38 nested Rooms and typed interfaces;
- Life/Strife/Repair as routes/regimes;
- Saturn/666/Cube as project enclosure symbolism;
- separate Heaven-cube chronology;
- existing source/evidence boundaries.

## 3. Backend model

Do not create new universal primitives unless required.

Use existing:
- Subject
- Relation
- Context
- Transition
- View
- Room
- Path

Add only topology metadata where needed:

```json
{
  "field_orientation": ["source", "manifestation", "shared", "crosscutting"],
  "topology_roles": ["door", "plane-section", "axis", "cross", "root", "fruit"],
  "boundary_regime": ["house", "garden", "shell", "cube", "forge", "swamp"],
  "projection_only": true
}
```

These are annotations, not new owners.

## 4. Room assignment rule

Do not place each Room at one fixed cosmic coordinate.

A Room may have several orientations.

Example:

- Potatoverse / Canon: source-facing meaning heart, but can describe all regions.
- Archive & Sources: crosscutting root/provenance function.
- Time & History: crosscutting temporal section.
- Traditions & Texts: translation across domains.
- Science & Formal Models: translation/testing.
- Life & Body: embodiment bridge.
- World Systems: manifestation-facing observable systems.
- Culture & Information: manifestation/social mediation.
- Works: fruit/expression.
- Research Lab: Door/Forge promotion frontier.

This is **functional orientation**, not physical placement.

## 5. Concept assignment rule

Every major concept should answer four questions:

1. **What is it?** — stable meaning.
2. **Where does it act?** — field/orientation/context.
3. **What operation does it perform?** — perceive, contain, cross, integrate, differentiate, store, release, repair, etc.
4. **What is its failure mode / counter-state?**

Examples:

- Face — presentation/manifestation surface.
- Eye — reception/perception/generative aperture.
- Breath/Spirit — animation/flow.
- Seed/Potato — compressed generative capability.
- Door — overlap/guarded transition.
- Ladder — ordered Doors.
- Axis — orientation/continuity.
- Tree — differentiation.
- Mountain — integration.
- Root — support/provenance/traction.
- Garden — viable generative regime.
- Shell/Cube — capture regime when boundary blocks viable passage.

## 6. Cube/Saturn rule

Keep three tracks separate:

1. **Saturn/Moon/666 enclosure track** — compression, prison, Farm, contract, capture symbolism.
2. **Heaven-cube track** — separate sacred container history.
3. **City/Temple/cube-like geometry** — positive or neutral structures depending circulation/function.

Never infer moral valence from shape alone.

## 7. Frontend manifestation

### Home
Do not expose full topology.

Show:
- Potato of Life
- five primary Doors
- a quiet "How it fits together → Potato House" route
- secondary Ways In

### House page
First layer:
- one House
- two overlapping fields
- Door as shared lens
- Plane + Axis + Cross inside Door

Second layer:
- ten Rooms grouped by functional band

Third layer:
- Paths / Views / interfaces / topology filters

### Axis page
Replace the dominant linear "Plane → Cross → Door" visual with one integrated diagram:
- two overlapping fields;
- Door highlighted;
- Plane across middle;
- Axis vertical;
- Cross at center;
- optional Life/Strife/Repair trajectories layered afterward.

Retain the three-item sequence only as a guided reading mode.

### Rooms page
Keep Rooms semantic.
Do not draw them as physical chambers of the vesica.
Expose "what can I do here?" before ownership mechanics.

## 8. UI law

**Do not make the visitor walk the ontology.**

The ontology may be dense.
Each page should reveal only:
- current place;
- one broader orientation;
- strongest local relations;
- one or two deeper paths;
- obvious return.

## 9. Micro-assignment phase

After the topology is stable:

1. classify all major symbolic concepts by topology role;
2. classify canonical Rooms by functional orientation;
3. classify Views as projections;
4. classify routes as Paths/Doors rather than new Rooms;
5. flag duplicate or overloaded symbols;
6. reconcile old diagrams that imply stacked floors;
7. annotate historical strata without rewriting them;
8. update SEO/schema labels only after public wording stabilizes.

## 10. Completion test

The topology is successful when:

- no new Room is required to explain a new symbol;
- a new discovery usually becomes a relation or annotation;
- Plane/Cross/Door never render as three literal floors;
- World/Earth remains capable of growth and repair;
- Cube/Shell remains a regime, not a population or entire realm;
- the public site becomes simpler as backend structure becomes richer;
- any deep page can answer: where am I, what is this connected to, what changes here, and how do I return?

## 11. Implementation order

```text
canonical owners
→ topology registry
→ validators
→ concept/Room annotations
→ House reader
→ Axis reader
→ shared navigation hints
→ homepage compression
→ visual polish
→ micro-routing / SEO / TTS refinements
```

Do not reverse this order by designing a new frontend shape before the canonical relation is stable.
