# Temporal Atlas Enrichment Design

**Date:** 2026-09-12  
**Status:** Design specification  
**Branch:** `chronology/2011-kolding-reconstruction`

## Purpose

Extend the project timeline from a mostly biographical/public-development chronology into a **Temporal Atlas**: one evidence-aware temporal index spanning biography, world/geopolitical development, scientific/formal work, public presence, creative artifacts, legal/institutional transitions, neurotheology/body development, and archive/research corrections.

The default roadmap remains sparse. Richness comes from domain filters, event packs, state changes, first-attestation chains, and links into the World Atlas rather than by putting every dated fact into one flat list.

## Core principle

The project is relationship-first, so time should track not only **events** but also **changes in relationships and states**.

Examples:

- the Son moves from Haderslev to Copenhagen;
- the project changes England from included to pending;
- an equation moves from symbolic seed to explicit formula to archive formalization;
- a concept moves from first seed to first exact attestation to mature definition;
- an institution announces a change on one date and makes it effective on another;
- a creative image turns an earlier symbol into a historically traceable artifact;
- an archive correction changes what the project believes about an older event without changing the date of the older event.

Timeline ordering must never be treated as proof of causality.

---

# 1. Temporal Atlas model

## 1.1 One temporal corpus, multiple lanes

Use one canonical timeline/event system with optional domain/event-type metadata. Do not create independent competing timelines for science, North, art, legal history, body symbolism, etc.

The timeline may be projected through these top-level domains:

- `life`
- `potatoism`
- `religion`
- `bible`
- `philosophy`
- `science`
- `creative`
- `public`
- `legal-institutional`
- `body-neurotheology`
- `north-world`
- `project-research`

An event may belong to more than one domain.

## 1.2 Controlled event types

Use a deliberately small event-type vocabulary:

- `life-event`
- `move-or-place-transition`
- `public-statement`
- `public-presence-milestone`
- `concept-first-attestation`
- `concept-definition`
- `religious-development`
- `theory-development`
- `scientific-formalization`
- `creative-work`
- `legal-event`
- `administrative-state-change`
- `world-context`
- `world-program-milestone`
- `network-membership-change`
- `measurement-or-estimate`
- `research-discovery`
- `correction`
- `reinterpretation`
- `project-milestone`

Fine-grained meaning belongs in topics/tags rather than expanding this list indefinitely.

## 1.3 Optional event metadata

Extend timeline events conservatively with optional fields:

- `domains`: controlled broad domains;
- `event_types`: controlled event types;
- `topics`: existing or free project tags;
- `places`: existing structured place metadata;
- `country_codes`: canonical sovereign-state references where appropriate;
- `atlas_refs`: references to country, network, relationship or world-atlas records;
- `related_event_ids`: direct event-to-event links;
- `temporal_relations`: typed relations such as `before`, `after`, `develops-into`, `reinterpreted-by`, `supersedes`, `same-period-as`, `state-changed-by`;
- `attestation_stage`: optional `seed`, `first-known`, `first-exact`, `first-public`, `first-definition`, `mature-synthesis`, `canonical-promotion`;
- `state_change`: optional before/after representation for project/world/institutional state changes;
- `measurement`: optional metric/value/unit/method/status object for duration or quantitative milestones;
- `world_context`: optional explicit external-context object when a public world event is shown next to project history;
- `context_firewall`: explicit note when timing overlap is interpretive rather than causal;
- `confidence`: retained and used consistently;
- `source_records`: canonical owners, never merely downstream projections.

These fields are additive. Existing events remain valid without them.

---

# 2. Lane A — North / World development

## Purpose

Expose the development of the North project and relevant world context without equating project membership with legal/geopolitical reality.

## Internal North events to promote

Candidate milestones already present in the repository:

- `2025–2026` — sacred North increasingly connects to Denmark, Greenland, Arctic and Europe;
- `2026-02` — North Axis crystallizes as an explicit organized field;
- `2026-02 to 2026-09` — design graph gives way to observation graph: ownership, money, debt, procurement, infrastructure, trade, energy, technology, labour, research and security become observable relationship layers;
- `mid-2026` — North membership formulation expands and differentiates anchor/core/under-axis/extension/external statuses;
- `2026-07-19` — explicit `Canada → Turkey minus England` formulation; England pending, Russia excluded, Estonia under-axis, Australia shared, Mesopotamia possible later;
- `2026-09` — world-repair architecture explicitly couples North of North, tikkun, World Atlas, Economic Graph, Obligation Graph and North Programme.

Canonical owners:

- `knowledge/timeline/north-programme-development-genealogy.json`
- `data/north-axis-membership-history.json`
- `knowledge/core/north-axis-tikkun-world-repair-synthesis.json`
- `knowledge/indexes/north-axis-routing-index.json`

## External world-context markers

Promote only high-value public events that materially explain why a project milestone was historically salient. Initial source family:

- `knowledge/timeline/contextual-synchronisms.json`

Examples include Greenland sovereignty/Arctic developments around the 2026 North crystallization.

Every external event must use:

- `event_types:["world-context"]`;
- external source provenance;
- `context_firewall` stating that temporal or symbolic overlap does not prove prophecy, causation, sovereignty or authorization.

## World-map integration

Where an event references countries or networks, include `country_codes` and/or `atlas_refs` so a future map control can open the World Atlas in the corresponding state.

Do not rewrite historical borders in this phase.

---

# 3. Lane B — Science / equation genealogy

## Purpose

Make mathematical and scientific development chronological so later formalizations are not silently backdated into earlier symbolic material.

Canonical owner:

- `knowledge/science/equation-lineage-and-theory-graph.json`

Initial milestones:

- `2024` — Great Book boundary/mediator model;
- `2024` — Great Book logarithmic/golden spiral equation;
- `2024` — Great Book New Trinity functional model;
- `2024` — microtubule/body-mind-spirit model and standard-equation comparators;
- `2025-04-18` — recovered Unified Potato Theory proposal;
- `2025-04-21` — primary recovered Potato Axis spiral formula;
- `2025-07-23` — Hashem/Father theological attestation where relevant to later operator formalization;
- `2026` — Potato Dynamics tuple `P=(S,g,A,D,O,I)`;
- `2026-09-07` — repository spatial Axis model;
- `2026-09-09` — Trinity operator formalization;
- `2026-09-09` — Higgs/Potato-sector repair;
- `2026-09-09` — microtubule open-system comparator.

## Attestation chain

Science events should support:

`symbolic seed → explicit mathematical form → public/primary attestation → archive formalization → repaired/testable formulation`

An archive-derived mathematical repair must be labelled `project-research` / `scientific-formalization`, not presented as historical Tim-authored mathematics.

## Maturity

Where available, preserve theory maturity (`T0`–`T5` or current project scale) as metadata/topic/context rather than implying all equations have equal scientific standing.

---

# 4. Lane C — Public presence / cumulative duration

## Purpose

Represent public presence as a **cumulative temporal quantity**, not merely a one-off 100,000-hour event.

Canonical owner:

- `knowledge/timeline/livestream-duration-and-100000-hour-threshold.json`

Initial milestones:

- `2011-04-19` — candidate Minecraft Beta 1.5 anchor for beginning of the public-stream continuum; external game date is exact, personal stream start remains a project claim pending archive evidence;
- historical ~109,000-hour estimate;
- historical 112,542-hour estimate;
- 100,000-hour threshold crossing in project chronology;
- current ~107,000-hour working estimate and its measurement-method caveats.

Use `measurement` objects for estimates:

- metric;
- value;
- unit;
- measurement window;
- derivation/method;
- deduplication status;
- confidence/status.

Do not present internal cumulative estimates as externally certified world records.

---

# 5. Lane D — Creative / artifact history

## Purpose

Show when symbols become books, songs, images, performances, games or simulations.

Canonical owners:

- `knowledge/creative/artifact-history-registry.json`
- `knowledge/creative/tim-dooley-suno-music-archive.json`
- `knowledge/culture/creative-systems-archive.json`
- `knowledge/creative/visual-art-symbolic-composition-archive.json`

Initial milestones:

- `2024` — *The Great Book of Potato*;
- `2026-05-26 onward` — Mashy Arc;
- `2026-07-20` — Heavenly Gardener / Green Ring composition;
- `2026-07-21` — Wall Practice / Carving Sequence;
- exact-dated Suno works where creation time is directly recovered;
- selected games/simulations only when historically important to development.

## Promotion rule

The timeline should not ingest every song or generated image. Promote artifacts when at least one is true:

- first use of a major symbol or title;
- transition in Tim/Potato identity;
- historically important public/creative milestone;
- artifact later becomes a recurring doctrinal or cultural reference;
- exact date resolves chronology otherwise left vague.

---

# 6. Lane E — Legal / institutional state change

## Purpose

Expose exact legal and administrative transitions that already exist in specialist owners, while keeping legal facts separate from later theological interpretation.

Canonical owners:

- `knowledge/timeline/mai-mercado-2016-to-2025-long-tail-impact-timeline.json`
- `knowledge/legal/mai-mercado-2016-full-understanding-and-timeline.md`
- `knowledge/legal/mai-mercado-2016-long-term-aftermath-and-retirement-impact.md`
- `data/timeline-event-packs/retirement-kingship-2025.json`

Initial milestones:

- `2016-06-17` — initiating public Facebook post;
- `2016-06-17 to 2016-06-21` — escalation corridor;
- `2016-06-21` — remand;
- `2016-08-12` — conviction on three of four counts / five-month unconditional sentence;
- `2016 release` — project-biographical release event, exact date pending;
- `2017` — Great Book-described Facebook deletion / institutional withdrawal / streaming turn;
- `2025 after April Turning, exact date unresolved` — autobiographical retirement/release event;
- exact public kingship/Godhood attestations remain separate events rather than being merged into the administrative retirement event.

## Boundary

Legal/civil facts use official/contemporaneous evidence where available. Theological kingship, throne, release/rest and biblical parallels remain separate later interpretations.

---

# 7. Lane F — Body / neurotheology attestation

## Purpose

Show that the mature body map developed in layers rather than existing fully formed from the beginning.

Canonical owner:

- `knowledge/timeline/neurotheology-attestation-ledger.json`

Initial milestones:

- `2024` — Great Book thalamus / inner-potato / Potato Room stratum;
- `2026-07-08` — 33-step / 33-vertebrae Ladder development;
- `2026-08-21T21:32:08Z` — explicit user-originated Pineal=Son/Door and Thalamus=Father's House mapping;
- `2026-09-08T22:38:50Z` — exact mature House/Seed/Eye/Pineal/Ladder/Garden cluster;
- `2026-09-09` — cleanup into Thalamus=House metaphor, Pineal=Son/Eye/Door metaphor, Spine=Ladder, C1 Atlas/C2 Axis literal anatomy, CSF/Breath as Spirit-flow analogues, plus empirical neuroscience context.

Use `attestation_stage` so an early seed is not confused with a mature synthesis.

---

# 8. Lane G — Archive / research history

## Purpose

Make the repository's own changing understanding historically inspectable.

Important distinction:

`event date ≠ recovery date ≠ correction date ≠ canonical promotion date`

Examples:

- an event occurred in 2009;
- a contradictory Chapter 24.1 date was noticed in 2026;
- direct recollection resolved the order on 2026-09-12;
- the corrected chronology was promoted later that day.

Archive events use `subject:"project"` or `actor_ids:["project"]` and `event_types:["research-discovery"]`, `["correction"]`, or `["project-milestone"]`.

Candidate owners:

- chronology reconciliation/audit files;
- conversation-archaeology ledgers;
- inference ledger;
- source/provenance indexes;
- repository architecture milestones where historically meaningful.

Do not emit routine commits as timeline events.

---

# 9. State-change objects

## Why state changes matter

Some of the project's most important temporal information is not a single event but a changed state.

Examples:

- England: included/field → pending;
- Russia: possible/external → excluded → future-reconnection possibility;
- Estonia: ordinary Baltic relation → explicitly `under_axis`;
- theory maturity: T1 → T2;
- concept: seed → first exact attestation → mature synthesis;
- public-hour estimate: 109k → 112,542 → 107k working estimate;
- biography: nursing-home date variant 2007 → preferred 2009 working placement after evidence reconciliation.

Optional `state_change` object:

```json
{
  "entity_ref": "...",
  "dimension": "membership-status",
  "before": "included",
  "after": "pending",
  "effective_or_attested_on": "2026-07-19",
  "state_kind": "project-formulation"
}
```

State change must say whether it describes empirical reality, project canon, interpretation, measurement revision or archive correction.

---

# 10. Atlas time integration

The existing `data/atlas-time-contract.json` is the governing model for world-state chronology.

Temporal Atlas events should be compatible with:

- `valid_from`
- `valid_to`
- `announced_on`
- `effective_on`
- `observed_at`
- `source_published_on`
- `first_attested`
- `last_verified`

The timeline event contract does not need to copy all fields onto every event. Instead, events may reference stateful Atlas records via `atlas_refs`.

Future integration target:

- click timeline world event → open corresponding map state;
- select map `As of…` date → surface relevant timeline events;
- compare two dates → show both geographic/network changes and project North formulation changes.

This design phase does not implement historical borders.

---

# 11. First implementation wave

Implement in this order:

1. extend timeline schema/validator with `domains`, `event_types`, `country_codes`, `atlas_refs`, `related_event_ids`, `temporal_relations`, `attestation_stage`, `state_change`, `measurement`, `world_context`, `context_firewall`;
2. create `data/timeline-event-packs/north-world-development-2019-2026.json`;
3. create `data/timeline-event-packs/science-formalization-2024-2026.json`;
4. create `data/timeline-event-packs/public-presence-2011-2026.json`;
5. create `data/timeline-event-packs/creative-artifact-history-2024-2026.json`;
6. create `data/timeline-event-packs/legal-institutional-2016-2025.json`;
7. create `data/timeline-event-packs/body-neurotheology-2024-2026.json`;
8. add a small `project-research` pack containing only high-value corrections/research milestones;
9. register all packs in the timeline pack index and source registry;
10. update `docs/TIMELINE.md` with Temporal Atlas lanes and cross-domain rules;
11. update the timeline UI/filter model only after the data contracts and packs are stable.

---

# 12. Promotion thresholds

A dated record should enter the Temporal Atlas only if it materially answers at least one of these:

- What changed?
- When did a major idea first become explicit?
- When did a relationship/state change?
- When did the project enter a new developmental stage?
- When did a creative artifact materially carry or transform an idea?
- When did an externally datable world event become necessary context for understanding the project's development?
- When did later research correct or significantly reinterpret an older record?

A mere date is not enough.

---

# 13. Epistemic firewalls

1. **World context is not fulfillment.** External geopolitical events may contextualize project development but do not prove prophecy or divine authorization.
2. **Project membership is not legal membership.** North Axis formulations never imply state consent or treaty status.
3. **Archive formalization is not historical authorship.** A September 2026 equation repair must not be dated back to a 2024 symbolic seed.
4. **Measurement revision is not historical change.** A revised public-hour estimate changes the archive's estimate, not past elapsed time.
5. **Creative recurrence is not independent evidence.** A song or image repeating a concept is historical cultural evidence, not factual corroboration of the concept.
6. **Legal records outrank retrospective biography for legal precision.** Biographical meaning remains separately preservable.
7. **Body symbolism remains metaphor unless independently supported scientifically.** Anatomy dates track project mappings, not discovery of new anatomy.
8. **Recovery date is separate from event date.** Corrections and research unlocks receive their own project/research events.

---

# 14. Success criteria

The Temporal Atlas enrichment succeeds when:

1. one timeline can answer life, science, public, world, creative, legal, body and archive questions through filters rather than separate competing timelines;
2. North membership changes become versioned state changes instead of one timeless list;
3. world events are visible as external context without causal/prophetic inflation;
4. equations and concepts show development/attestation stages;
5. public presence can show cumulative measurements and revisions;
6. creative artifacts become historically traceable carriers of ideas;
7. legal/administrative dates remain distinct from theological interpretation;
8. the body/neurotheology model shows its actual development history;
9. archive corrections are temporally explicit rather than silently rewriting earlier records;
10. future World Atlas time controls can consume the same temporal references.

## Non-goals

- complete global historical borders;
- automatic ingestion of every dated repository record;
- treating every song/post/commit as a timeline milestone;
- causal inference from temporal sequence;
- prophecy scoring based only on coincidence;
- replacing specialist canonical owners with timeline cards.
