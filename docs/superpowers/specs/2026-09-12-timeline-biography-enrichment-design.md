# Timeline Biography Enrichment Design

## Purpose

Strengthen the project-wide chronology now that the Son's 2005–2014 sequence has been substantially reconciled. The enrichment should add more useful dates, places, transitions and major events without turning the canonical roadmap into a wall of low-value timestamps or duplicating source truth across many files.

## Design goals

1. Make the recovered Son-side chronology visible as actual timeline structure rather than leaving it buried in specialist reconciliation files.
2. Promote places such as Haderslev, Copenhagen, Kolding, Aabenraa, Lunderskov, Egypt, Italy and Amsterdam into first-class searchable timeline metadata where they materially identify a transition.
3. Preserve the distinction between exact dates, preferred working years, ranges and unresolved order.
4. Keep `data/timeline-events.json` sparse enough to remain the public roadmap while using a curated event pack for denser biographical bridge points.
5. Enrich narrative consumers so they explain the newly recovered chain rather than continuing to say only "care and design" or "embodied precursor years."
6. Preserve actor separation: pre-2020 ordinary biography belongs to the Son / human vessel.
7. Preserve source independence: repeated projections of Chapter 24 are not independent corroboration.

## Architecture

### 1. Sparse roadmap + dense biography pack

The existing timeline architecture already separates the main roadmap from curated overlay packs. Use that architecture instead of adding every recovered event to the base timeline.

The base `data/timeline-events.json` should gain only a few major promoted points where the current roadmap has a large chronological blind spot. The detailed 2005–2014 chain belongs in a new pack:

`data/timeline-event-packs/son-biography-2005-2014.json`

This pack should contain roughly 20–30 non-duplicative events covering the major transitions now owned by `knowledge/timeline/son-2005-2014-chronology-reconciliation.json` and the specialist Designia, Produktionsskolen and 2011 owners.

### 2. Place metadata

Add optional `places` metadata to the timeline event schema. A place object should support:

- `name` — human-readable place label, required for each object;
- `kind` — optional classification such as `city`, `institution`, `country`, `residence`, `workplace`, `travel`, `hospital`;
- `relation` — optional relation such as `lived`, `worked`, `studied`, `moved-to`, `travelled`, `admitted`, `relationship-base`;
- `country` — optional country label.

The timeline UI should:

- include place names/kinds/relations in full-text search;
- render a compact `Places` row on detailed cards;
- leave cards unchanged when no `places` field exists.

No coordinates or map UI are required in this pass. The value is chronology/search/provenance, not cartography.

### 3. Event precision and confidence

Use the existing `precision` field honestly:

- exact known dates: `date`;
- known year: `year`;
- preferred year but not primary-record exact: keep the year date and add `confidence` plus source-direction language explaining it is a preferred reconstruction;
- corridors such as late 2009–2010: `range`;
- unresolved internal order should not be invented merely to produce a prettier chain.

Events should point back to canonical owners using `source_records`.

### 4. Promoted roadmap points

Promote only events that materially change the visible life story. Recommended additions/replacements in the sparse base:

- 2007 practical labor: painter/decorator → meatpacking;
- 2008 Copenhagen IT / abrupt move / firing / Haderslev return;
- 2009 nursing care → Designia/Kolding/Louise transition;
- 2010 internship/Aabenraa → Produktionsskolen transition;
- 2011 Tree event should remain the major roadmap point but be updated to point to the detailed 2011 owner and use corrected duration/admission framing;
- 2012 integration/travel/birthday/guitar may be a roadmap bridge if the base otherwise jumps directly from 2011 to 2014.

These roadmap entries remain summaries. The pack carries the individual subevents.

### 5. Biography pack event families

The pack should expose the following event families without overclaiming dates:

#### Crash / reconstruction
- 2005 major motorcycle crash.
- 2005 onward multi-year dental reconstruction / recovery.

#### Practical work / Copenhagen
- 2007 painter/decorator work.
- 2007 meatpacking/freezer/forklift period.
- 2008 Copenhagen interview; hired on the spot to start Monday.
- rapid move to Copenhagen.
- IT consultant period.
- firing and return to Haderslev.

#### Haderslev / Designia / Louise
- 2009 nursing-home employment in Haderslev.
- own Haderslev apartment.
- application to HANSENBERG Designia / mediegrafiker.
- mailed circus-poster collage admission task.
- acceptance and summer move to Kolding/dormitory.
- Louise relationship begins.
- licence constraint: no licence during nursing-home period; exact later issue date unresolved.

#### Egypt / internship / Aabenraa
- Egypt travel while already together with Louise; exact relation to internship remains unresolved.
- living with Louise/her parents in Kolding where supported by current recollection.
- internship/cubicle placement.
- move to Aabenraa to be close to internship while relationship continues.
- school/internship path ends.
- move into own place while relationship continues for some time.

#### Produktionsskolen / 2011
- Produktionsskolen in Lunderskov.
- multimedia class and informal assistant-teacher function while still a student.
- leaves Produktionsskolen before Tree event.
- breakup/search corridor before Tree event.
- 2011 acute Tree ordeal.
- sleep / next-day perceptual rupture.
- voluntary psychiatric presentation/admission.
- hospital dream / later crow scene as separate phases.

#### 2012–2014
- Italy with earthly father / Maria candidate.
- Amsterdam 25th birthday on 2012-07-31 if autobiographical birthday memory is retained.
- guitar from father / first personally owned guitar.
- 2013 `The Alchemist` reading candidate.
- 2014 earthly father's fatal aneurysm.

## Narrative propagation

Update the strongest reader-facing and canonical projections that currently compress this corridor too heavily:

- `son-timeline.json`
- `knowledge/timeline/developmental-genealogy.json`
- `knowledge/journey/tim-dooley-journey.json`
- `knowledge/reader/tim-dooley-dossier.json`
- `knowledge/timeline/son-chronology-projection-corrections-2026-09-12.json`

The enrichment should add information, not merely replace one paragraph with another. Important additions include named institutions, cities, causal transitions and skill/competence details where they materially explain later choices.

Narrative surfaces should not reproduce every pack event. They should use the chain to explain development:

`injury/reconstruction → practical labor → corporate IT → care work → design/media training → internship alienation → production-school teaching/technical competence → collapse/search → Tree/psychiatric sequence → integration/travel → father loss`.

## Timeline source routing

Every new timeline event should point to one or more of these owners:

- `knowledge/timeline/son-2005-2014-chronology-reconciliation.json`
- `knowledge/timeline/son-kolding-designia-school-anchor.json`
- `knowledge/timeline/son-lunderskov-production-school-anchor.json`
- `knowledge/timeline/son-2011-kolding-psychonaut-psychiatric-sequence.json`
- `knowledge/research/son-2005-2014-full-chronology-audit-2026-09-12.md`

Do not cite `son-timeline.json` or the Journey as independent evidence for facts that originate in those owners.

## Validation

Extend `scripts/validate_timeline_events.py` to validate optional `places` metadata across base and indexed packs:

- `places` must be a list if present;
- each place must be an object;
- each place must have a non-empty `name`;
- optional `kind`, `relation`, `country` must be non-empty strings if supplied;
- duplicate place tuples inside one event should fail validation.

Update `schemas/timeline-event.schema.json` accordingly.

Run the existing timeline validator after all changes. Also verify JSON parsing for every modified JSON file and search the branch for stale impossible `age 25` 2011 wording and additive `19 + 6` phrasing in the files touched by this pass.

## Non-goals

- Do not create a geospatial map or add coordinates.
- Do not manufacture exact dates for employment, school, Egypt, licence or Produktionsskolen attendance.
- Do not rewrite the whole Great Book ODT in this pass.
- Do not merge the chronology branch into `main` while the branches are diverged.
- Do not turn later mythic interpretation into contemporaneous biography.

## Success criteria

The enrichment is successful when:

1. the timeline can show/search named places;
2. the 2005–2014 biography is represented by a dense but optional curated pack;
3. the base roadmap contains a clearer 2007–2012 life progression without becoming noisy;
4. major narrative consumers explain the recovered chain with named places/institutions and causal transitions;
5. all timeline validation passes;
6. exact/preferred/range/unresolved chronology remains visibly distinguishable;
7. the branch remains isolated and reviewable rather than overwriting main.
