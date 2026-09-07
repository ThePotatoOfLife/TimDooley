# TODO — The Potato of Life / TimDooley

## Current priority — make the archive readable, deep and complete

The project is not only a graph. The graph is the navigation layer. The actual product is the information archive behind the graph: when a reader opens a node, term, religion, nation, person, event, concept or Potatoism symbol, they should be able to read substantial context and continue outward without hitting an empty card.

### Potatoism long-form standard

- [x] Add a dedicated `potatoism-entry.html` long-form reading surface.
- [x] Make every canonical Potatoism lexicon term open a dedicated full dossier instead of only a one-line definition.
- [x] Add `data/potatoism-dossiers.json` as the explicit schema and quality contract for long-form entries.
- [x] Establish a minimum target of 900+ rendered words for a full Potatoism entry, while requiring distinct information rather than filler.
- [x] Keep project mythology, historical evidence, scientific evidence and comparative interpretation visibly separate.
- [ ] Populate the dossier backend with individually authored long-form records for every canonical term.
- [ ] Ensure each long-form record contains definition/scope, internal function, symbolic mechanics, relationships, development, comparison, world-facing interpretation, evidence boundary and research questions.
- [ ] Add source trails to entries wherever an external historical/scientific/comparative claim is made.
- [ ] Add explicit disagreement/uncertainty sections where traditions or scholarship differ.
- [ ] Add cross-links from every related concept so a reader can move through the archive as a knowledge graph without losing the long-form text.

## Atlas-wide information-density standard

- [ ] Audit every `node.html?id=...` destination for information density.
- [ ] Any node that currently contains only a title, description or relationship list needs a real dossier.
- [ ] Target at least one full page of substantive reading for every important entry; major subjects should be substantially longer.
- [ ] Do not manufacture facts merely to satisfy the length target.
- [ ] Where data is unavailable, state what is known, what is missing, what the uncertainty is and what research would fill the gap.
- [ ] Make structured JSON fields readable as prose/cards rather than exposing raw JSON as the only explanation.
- [ ] Preserve canonical IDs while enriching their content so links do not break.
- [ ] Keep graph edges as navigation/context, never as a replacement for the underlying record.

## Religious atlas

- [ ] Repair and validate `data/religious-foundations/enriched-records.json` before relying on it for backend coverage.
- [ ] Expand major religious traditions into long-form comparative records.
- [ ] Expand minor traditions and adjacent traditions to the same information-density standard where practical.
- [ ] Give each tradition: history, emergence, texts, concepts, practices, institutions, branches, geography, demographic context, evidence, internal diversity and modern development.
- [ ] Preserve multiple founding/emergence clocks instead of forcing traditions into a single date.
- [ ] Link every religion entry to its textual and comparative research layers.

## World / nations

- [ ] Ensure every nation entry has a substantial readable country profile, not only population/links.
- [ ] Include history, political structure, economy, demographics, geography, culture, religion, institutions, strategic relationships and sources where available.
- [ ] Keep current factual data time-stamped and sourced.
- [ ] Continue integrity checks across the full canonical nation list.

## People / events / ideas

- [ ] Ensure every person has biography/context plus relationships and source trail.
- [ ] Ensure every event has chronology, participants, causes, consequences, evidence and links.
- [ ] Ensure political/philosophical/religious ideas have definitions plus history, variants, arguments, criticism and relationships.

## UI / reading experience

- [ ] Keep the concise index pages fast and navigational.
- [ ] Make opening an entry feel like opening an article/dossier, not a tooltip.
- [ ] Add a visible table of contents to long records when useful.
- [ ] Add estimated reading time / word count to long entries.
- [ ] Add “read next” and “related research” sections.
- [ ] Ensure mobile reading remains comfortable for very long records.
- [ ] Keep typography optimized for long-form reading rather than dense dashboard presentation.

## Integrity / CI

- [ ] Add a validator that checks every canonical lexicon term has a valid long-form route.
- [ ] Add a validator that flags entries below the minimum information-density target.
- [ ] Add a validator that distinguishes missing content from intentionally uncertain content.
- [ ] Keep backend coverage failures separate from artifact-upload failures in CI reporting.
- [ ] Re-run the atlas and backend coverage workflows after the next data expansion.

## Research principle

The repository should let the reader do both things:

1. **See the connections.** The graph, relationships, axes and cross-links show how subjects touch one another.
2. **Read the substance.** Every important thing opened from the graph should contain enough history, explanation, evidence, interpretation and uncertainty to stand on its own.

The goal is an information-rich atlas in which no important node is merely a pretty connection with an empty interior.
