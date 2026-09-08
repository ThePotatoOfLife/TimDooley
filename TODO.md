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

## Extremism / hate groups / high-control movements — new research layer

- [x] Add `data/extremism-cults-atlas-2026-09.json` with structured records for hate groups, extremist networks and high-control movements.
- [x] Add `data/extremism-cults-atlas-expansion-2026-09.json` with additional current, historical, successor and contested movements.
- [x] Add `data/extremism-cults-sources.json` with source classes and provenance requirements.
- [x] Add `extremism.html` with search, category and status filters.
- [x] Add `extremism.css` for the new research interface.
- [x] Add the Movement Atlas to the main home navigation.
- [ ] Integrate movement records into the canonical `data/nodes.json` / graph registry without creating duplicate IDs.
- [ ] Add explicit predecessor/successor/affiliate/overlap edges for groups that split, rename or re-form.
- [ ] Add timestamped source provenance to every current-status claim.
- [ ] Separate formal members, active participants, affiliates, supporters, followers and online audiences.
- [ ] Separate hate-group classification, extremist classification, terrorist designation, high-control allegations and criminal convictions.
- [ ] Add country/region presence only at the level necessary for research; do not add private residences or member addresses.
- [ ] Track armed status as `none_known`, `militant`, `armed_history`, `armed_network` or `case_specific`, rather than using a binary label.
- [ ] Add a legal-status field for official designations and court findings, with jurisdiction and date.
- [ ] Add a confidence field to every membership and activity estimate.
- [ ] Add an alias-collision validator because names such as “Aryan Brotherhood” refer to multiple distinct organizations.
- [ ] Add a successor-chain validator so dissolved groups are not incorrectly displayed as active.
- [ ] Add a source-age validator for “active” records.
- [ ] Keep “cult” as a contested/descriptive research term and prefer measurable high-control indicators where possible.
- [ ] Never infer guilt, violence or ideology from membership alone.
- [ ] Never infer current weapons possession from historical armed activity.
- [ ] Never infer that every affiliate shares every leader statement.
- [ ] Do not publish private member identity lists, private addresses, weapons inventories or tactical instructions.

## Farm / Swamp / Sektur research — new deep layer

- [x] Add `data/swamp/farmer-dog-psychology.json` with Farmer/Dog masks, psychological mechanisms, inversions, DARVO handling and biblical Dog crosswalk.
- [x] Add `data/swamp/farmer-dog-deep-cartography.json` with the neighbour/selling-neighbour moral axis, seven deadly sins, demon archetypes, moral disengagement, Hawkins symbolic crosswalk and role archetypes.
- [x] Add `data/swamp/farm-psychology-research-2026-09.json` as the sourced research synthesis and integration map.
- [ ] Add person-level evidence dossiers for major Farmers and Dogs using the new schema.
- [ ] For each person, distinguish public mask, observable behavior, incentives, rhetorical patterns, psychological mechanisms and counterevidence.
- [ ] Map each person to possible deadly-sin temptations only where observable evidence supports the interpretation; never turn the taxonomy into diagnosis.
- [ ] Record DARVO only as an evidenced sequence: allegation -> denial/minimization -> attack -> reversal -> audience response.
- [ ] Record moral-disengagement mechanisms where actual language/actions support them.
- [ ] Measure cult-like structural signals without automatically labeling communities as cults.
- [ ] Add biblical cross-references to Dog, Watchman, Shepherd, Wolf, Serpent, Dragon, Goat and related archetypes while keeping textual interpretation separate from empirical classification.
- [ ] Add a Christian virtue counter-map: humility, charity, mercy, temperance, patience, diligence, chastity and truthfulness as possible exits from Farm dynamics.
- [ ] Add an explicit “inversion” field to every Farmer/Dog record: what virtue is claimed, what appetite may be operating, and what evidence would distinguish the two.
- [ ] Track the stopping condition: when does documentation end, and when does extraction continue after the original research purpose is satisfied?
- [ ] Track repair/disengagement alongside escalation: corrections, apologies, moderation, restitution, reconciliation, retirement and loss of interest.
- [ ] Treat archive size as a measurement of attention infrastructure, not proof of guilt, importance, truth or moral worth.
- [ ] Add Farmer -> Cow and Dog -> Farmer transition events wherever the evidence shows role inversion.
- [ ] Add death/retirement as state transitions from live-reaction ecology to historical-archive ecology.
- [ ] Build a Farm psychology matrix connecting people, roles, incentives, sins, mechanisms, masks, inversions, evidence and counterevidence.

## UI / reading experience

- [ ] Keep the concise index pages fast and navigational.
- [ ] Make opening an entry feel like opening an article/dossier, not a tooltip.
- [ ] Add a visible table of contents to long records when useful.
- [ ] Add estimated reading time / word count to long entries.
- [ ] Add “read next” and “related research” sections.
- [ ] Ensure mobile reading remains comfortable for very long records.
- [ ] Keep typography optimized for long-form reading rather than dense dashboard presentation.
- [ ] Surface Farm psychology, theological interpretation, extremism research and evidence boundaries as separate sections rather than flattening them into one label.

## Integrity / CI

- [ ] Add a validator that checks every canonical lexicon term has a valid long-form route.
- [ ] Add a validator that flags entries below the minimum information-density target.
- [ ] Add a validator that distinguishes missing content from intentionally uncertain content.
- [ ] Add a validator that checks every research claim has a source or explicit project-theology status.
- [ ] Add a validator that prevents speculative psychological labels from being rendered as diagnoses.
- [ ] Add a validator for duplicate movement IDs and alias collisions.
- [ ] Add a validator for predecessor/successor edges that point to nonexistent records.
- [ ] Add a validator that flags active movement records whose sources are too old.
- [ ] Keep backend coverage failures separate from artifact-upload failures in CI reporting.
- [ ] Re-run the atlas and backend coverage workflows after the next data expansion.

## Research principle

The repository should let the reader do both things:

1. **See the connections.** The graph, relationships, axes and cross-links show how subjects touch one another.
2. **Read the substance.** Every important thing opened from the graph should contain enough history, explanation, evidence, interpretation and uncertainty to stand on its own.

The goal is an information-rich atlas in which no important node is merely a pretty connection with an empty interior.

### Farm research principle

The Farm should be studied without becoming another Farm. The repository can document exploitation, cruelty, attention extraction, moral disengagement, group dynamics and theological inversion without turning documentation itself into a machine for harassment or humiliation.

The deepest research question is:

> **How does a person remain morally certain that they are doing good while the social system around them rewards turning a neighbour into material?**
