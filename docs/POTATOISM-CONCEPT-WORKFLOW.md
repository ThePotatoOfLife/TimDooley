# Potatoism concept workflow

## Why the old view was wrong

The Potatoism corpus contains several legitimate *occurrences* of the same concept. A lexicon entry, a cosmology row, a corpus record, a timeline event and a relationship edge may all mention Father. They are not five Fathers.

The old repository projection treated those occurrences as independent visible records. That produced repetition without increasing understanding: the same one-line definition appeared again and again while the reader had no single place to study the concept deeply.

The same problem applies to Heaven, Door, Axis, Ladder, Tree of Life and other recurring concepts.

## Permanent model

Use four different things and do not confuse them:

1. **Canonical concept identity** — `data/potatoism-concept-registry.json`. One `canonical_id` per recurring project concept, with aliases and the stable conceptual definition.
2. **Substantive content** — canonical corpus/dossier material. This is where long explanations, evidence boundaries, timeline and interpretation live.
3. **Occurrences / projections** — lexicons, cosmology tables, maps, timelines and comparative layers. They may mention or characterize a concept but do not create another identity.
4. **Relationships** — graph edges such as Father → Son. An edge is a relationship, not a duplicate node.

The repository index must therefore display one canonical concept where several Potatoism files describe the same identity, while retaining provenance links to the underlying occurrences.

## Identity rules

- `Father`, `Father in Heaven`, `Father Above` and `Tim Dooley / Father` resolve to `tim-dooley-father` when used as the same Potatoism concept.
- `Father's House` remains a distinct concept because it is a place/metaphor, not the Father itself.
- `Father → Son` remains an edge/relationship and must not become a second Father record.
- `Heaven` is one concept. `Heavenward` may be an alias or a directional relation, not an excuse for another Heaven node.
- Historical or comparative figures such as Jesus, Thomas or Yggdrasil must retain their external identity and epistemic status. A project alias does not erase a historical source.
- Similar words do not automatically mean identical concepts. Consolidation requires an explicit registry mapping.

## Build workflow

1. Add or improve the substantive canonical concept once.
2. Register its `canonical_id` and aliases in the concept registry.
3. Keep source occurrences for provenance and context.
4. Build `repository-index.json` from source records plus the concept registry.
5. When an occurrence resolves to a registered concept, expose the canonical concept once and attach occurrence metadata rather than rendering another copy.
6. Keep graph edges, research records and comparative sources as their own record types.
7. Run the source-of-truth audit and repository build before deployment.

## What not to do

- Do not copy the same definition into five files merely to make navigation work.
- Do not delete source occurrences just because they are projections; provenance is valuable.
- Do not make the graph the content.
- Do not make the lexicon the entire dossier.
- Do not infer identity from loose keyword matching.
- Do not create a new concept because a page needs a navigation target.
- Do not pad a canonical entry with repeated prose. Depth must come from distinct explanation, mechanism, relationships, timeline, comparison, evidence boundaries and research questions.

## Definition of done

A recurring concept is healthy when a reader can:

- open one canonical concept;
- read a substantial explanation there;
- see what the concept means inside the project;
- see what it is related to;
- distinguish project symbolism from historical/scientific evidence;
- inspect where the concept occurs elsewhere;
- return to one identity instead of being presented with repeated definitions.

This is the permanent consolidation rule for Potatoism navigation.