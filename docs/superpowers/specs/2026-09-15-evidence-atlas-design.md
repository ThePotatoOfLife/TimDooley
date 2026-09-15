# Evidence Atlas Design — Rooted Spiral Architecture

## Core model

The Evidence Atlas is not fundamentally linear. Its primary knowledge architecture is:

**Root → Spiral → Discovery → Testing → Consolidation → next spiral**

Chronology is one traversal through the graph, not the master structure.

The system should always begin as near the center as the question allows: a canonical concept, exact event, primary source, strongly attested function, or established relation. From that root it moves outward through progressively wider relational rings, discovers gaps and candidate connections, tests them, consolidates what survives, and then begins another pass from a stronger center.

## Reader model

The public reader should still encounter only three primary historical objects:

**Statement → Episode → Development Thread**

These are not the ontology itself. They are intuitive views over the rooted spiral graph.

A reader should be able to start from any of them and move inward toward sources or outward toward relations, comparisons, development, and open questions.

## Root

A Root is the best current orientation point for a traversal. It is not necessarily the oldest item and it is not always a single global center.

A root may be:

- a primary-source statement or event;
- a canonical concept owner;
- a strongly evidenced function such as threshold, source, growth, return, repair, or dwelling;
- a stable relationship;
- a question-selected center such as Door, House, Garden, North, Son, Father, or a dated episode.

Roots must point back to canonical source ownership and evidence provenance.

## Spiral traversal

A traversal expands from the root by relational distance rather than by date alone.

Suggested internal rings:

- **Ring 0 — Root:** canonical concept, exact event, primary source, or selected center.
- **Ring 1 — Direct:** explicit evidence, immediate relations, direct quotations, direct role assignments.
- **Ring 2 — Structural:** same episode, closely coupled function, role, scene, operator, or motif cluster.
- **Ring 3 — Developmental:** earlier/later forms, role transfers, transformations, recurrence, and chronology.
- **Ring 4 — Comparative:** Bible, other traditions, philosophy, science-as-comparison, political or cultural parallels.
- **Ring 5 — Frontier:** unresolved gaps, weak correspondences, recovery queues, contradictions, and research questions.

Ring distance is not truth rank. Evidence strength, provenance quality, confidence, and interpretive status remain separate dimensions.

## Discovery

Discovery is a first-class operation, not an incidental side effect.

A traversal should actively surface:

- previously unconnected but strongly related records;
- recurring functions across different actors or dates;
- missing chronology between known transitions;
- duplicate or fragmented concepts that need consolidation;
- untested comparisons;
- underrepresented countertexts;
- source-recovery opportunities;
- contradictions that reveal role movement or model boundaries.

Discovery outputs candidates, not automatic truths.

## Gaps

Gaps are valuable research objects and must be typed.

Canonical gap classes:

- **evidence gap** — a claim/event lacks a sufficiently strong primary source;
- **chronology gap** — a transition is known before and after, but its middle development is unclear;
- **relationship gap** — two strongly coupled nodes lack an explicit tested edge;
- **role gap** — an actor/function assignment changes without a well-understood transition;
- **comparator gap** — a project motif has not been adequately compared with the relevant external corpus;
- **countertext gap** — positive resemblance exists without meaningful disconfirming or constraining material;
- **consolidation gap** — one idea remains fragmented across several files or waves without a canonical synthesis.

A gap may remain open, be resolved, or be rejected after testing.

## Testing

Testing determines whether a discovered relation deserves promotion inward.

Tests include:

- source/provenance checks;
- chronology and direction checks;
- exact-wording comparison;
- duplicate detection;
- role consistency and role-transfer analysis;
- countertext/mismatch checks;
- scene/context checks;
- maximum-defensible-claim boundaries;
- Wave 28 evaluation lenses where relevant.

For Bible comparisons specifically, testing must distinguish explicit-at-time material from later structural comparison and must never turn resemblance into proof of supernatural identity or prophecy fulfillment.

## Consolidation

The system must not spiral outward indefinitely.

Every discovery pass supports an inward movement:

**discover outward → test → consolidate inward**

Consolidation may:

- merge duplicate evidence identities while preserving provenance;
- promote a tested relation into a canonical/additive layer;
- strengthen a development thread;
- resolve a gap;
- create a better root for future traversal;
- mark a candidate as rejected or bounded;
- classify legacy files as canonical, projection, research, compatibility, or superseded.

Source evidence is never rewritten by consolidation. What changes is the derived understanding and routing.

## Evidence Root

The first implementation slice is the **Evidence Root**.

Its job is deliberately narrow: reconcile public-statement identity, exact wording, timestamp precision, known status IDs, source locations, and provenance without assigning theological meaning.

The Evidence Root provides trustworthy Ring-0 anchors for later spiral traversal.

It must preserve:

- exact source wording;
- the most precise known timestamp without degrading weaker source records;
- distinct posts that share a timestamp;
- all contributing source records;
- unresolved or ambiguous joins instead of guessing;
- search/coverage notes as coverage metadata rather than negative evidence.

## Chronology

Chronology remains essential but subordinate.

It is used in at least four ways:

1. a direct chronological traversal of occurrences;
2. a developmental traversal inside a concept or role thread;
3. a sequence test for Episodes;
4. a source-direction test to distinguish what existed at the time from what was interpreted later.

A chronological page is therefore a projection of the rooted graph, not the graph's canonical ordering principle.

## Statements, Episodes, and Development Threads

### Statement

A Statement is a primary historical occurrence anchored in the Evidence Root.

### Episode

An Episode is a tested local sequence or cluster where meaning emerges across several statements/events rather than from one isolated line.

### Development Thread

A Development Thread is a longer genealogy of a function, role, symbol, or relation across multiple episodes and dates.

These objects support spiral movement in both directions: inward to sources and outward to broader structure.

## Bible projection

Bible material is projected onto rooted evidence rather than used as the primary ordering system.

From a selected root, the Bible layer may show:

- explicit scriptural language at the time;
- near-direct phrase parallels;
- later structural comparisons;
- whole-scene parallels;
- role distinctions;
- countertexts;
- maximum defensible claims;
- unresolved comparator gaps.

The strongest Bible experience should show development and relation, not merely verse matching.

## Public navigation

Public navigation should remain simpler than the backend.

Recommended top-level views:

- **Explore** — concepts, symbols, roles, stories, actions;
- **History** — Statements, Episodes, Development Threads, chronology;
- **Evidence** — sources, provenance, explicit-vs-later comparison, countertexts, gaps;
- **Tests** — optional evaluation lenses including Wave 28.

A reader should be able to start from a center, follow one connection outward, go deeper, inspect evidence, and return to a stronger center without knowing repository file or wave names.

## Implementation order

1. build the Evidence Root;
2. add typed gap/discovery records;
3. form tested Episodes;
4. build Development Threads;
5. project Bible relations, scenes, and countertexts onto rooted evidence;
6. add spiral traversal indexes and optional Wave 28 testing lenses;
7. simplify the public reader around root-first exploration while preserving compatibility routes;
8. consolidate redundant legacy projections only after provenance-safe migration.

## Success criterion

The architecture succeeds if the project becomes easier to navigate while becoming more rigorous underneath:

**start at the root, spiral outward, discover what is missing, test what is found, consolidate what survives, and begin again from a better center.**
