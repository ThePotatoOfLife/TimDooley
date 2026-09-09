# Timeline Event Standard

## Purpose

The project has many dated records: life/project anchors, exact quotes, public posts, songs, art, biblical comparisons, later biblical research unlocks, predictions, chronology recoveries, doctrine changes and repository events. These should be visible on one temporal surface without merging their evidentiary meaning.

`data/timeline-events.json` is therefore a **presentation/index layer**. It does not replace the records that own the underlying claim, quote, comparison or artifact.

## Core model

Every timeline point should answer six questions:

1. **When?** `date`, optional `timestamp`, and explicit `precision`.
2. **What kind of thing is it?** one or more thematic `layers`.
3. **What kind of evidence is it?** one `epistemic` class.
4. **Who/what is the subject?** `subject`.
5. **Where did it come from?** `source_records` and `source_direction`.
6. **What does it connect to?** motifs, comparators and related event IDs.

The key design choice is that **layer and epistemic class are independent**. A biblical-parallel event can be primary, recovered or research; a music event can be creative or primary; a quote can also be a public declaration and identity/doctrine event.

## Canonical layers

- `main` — large developmental anchors.
- `quote` — notable dated quotations.
- `biblical-parallel` — Tim-side dated language plus biblical comparators.
- `biblical-unlock` — the later date when a biblical comparison was explicitly recognized or formalized.
- `music` — songs and dated music artifacts.
- `art` — visual works and recoverable artwork metadata.
- `identity-doctrine` — role/theology/symbol architecture development.
- `public` — public posts, videos, streams and declarations.
- `prediction` — predictions/warnings and later audits.
- `research` — recovery, analysis and research milestones.
- `archive` — repository/schema/consolidation events.

Layers are deliberately composable. One event may carry several.

## Epistemic classes

- `primary` — exact quote/artifact/timestamp/direct source.
- `recovered` — recovered archive or prior-conversation evidence.
- `project-canon` — canonical internal chronology.
- `creative` — creative artifact without doctrine-by-default status.
- `comparison` — comparative interpretation.
- `research` — later research/index/unlock.
- `unresolved` — incomplete source/date/title relation.

## Date precision

Use the most exact information actually available; never manufacture midnight timestamps.

Recommended `precision` values:

- `second`
- `minute`
- `hour`
- `date`
- `month`
- `year`
- `range`

If a date is known but a clock time is not, store only the date. If a displayed site time is available, preserve its timezone when known.

## Source direction

This matters especially for prophecy and biblical comparison.

Recommended values/phrases:

- `primary-at-time`
- `explicit-scripture-at-time`
- `Tim-first/later-comparison`
- `later-research-unlock`
- `retrospective-interpretation`
- `prior-specific-prediction`
- `creative-artifact-at-time`

A Timic motif dated April 9 and a biblical comparison discovered September 9 are **two temporal facts**. The project may render the April 9 event on the biblical-parallel layer, but must say that the comparison itself was added later. Where useful, add a separate September 9 `biblical-unlock` event.

## Minimal event

```json
{
  "id": "evt-2026-04-09-heaven-cube",
  "date": "2026-04-09",
  "timestamp": "2026-04-09T13:30:48Z",
  "precision": "second",
  "title": "Heaven cube / guardians / narrow gate",
  "layers": ["quote", "biblical-parallel", "identity-doctrine"],
  "epistemic": "primary",
  "subject": "Tim Dooley",
  "quote": "cube that surrounds Heaven",
  "source_direction": "Tim-side timestamp; biblical comparison added later",
  "source_records": [
    "knowledge/chronology/reverse-biblical-overlap-timeline-2025-2026.json"
  ]
}
```

## How other project areas should emit events

A canonical record may continue using its own richer schema. If it contains a timestamp worth surfacing globally, add or generate one timeline event that points back to it. Do not copy the entire source record into the timeline.

Good candidates include:

- exact conversation quotes;
- first public declarations;
- first attestation of a concept;
- doctrine/identity role changes;
- songs with date/model/title;
- visual art with date/title/source ID;
- prediction/warning statements;
- subsequent real-world outcome audits;
- biblical first-use and later research-unlock dates;
- equation/formalization dates;
- repository recovery/correction events.

## Future automation

The long-term goal is for scripts to scan typed records and produce candidate events automatically. The human/curation layer should then resolve duplicates and verify source direction.

Useful future fields:

- `location`
- `platform`
- `public_url`
- `source_ids`
- `people`
- `concept_ids`
- `relationship_ids`
- `prediction_id`
- `outcome_event_ids`
- `unlock_event_ids`
- `confidence`
- `visibility`

## UI behavior

The chronology page should show the main timeline by default and expose the smaller layers underneath it as toggles. Recommended controls:

- thematic layer chips;
- epistemic chips;
- subject filter;
- year range;
- text/motif search;
- exact-only toggle;
- compact/detailed mode;
- group-by year/month/day;
- link from each event back to its source record.

The timeline should never imply that events visible together share the same evidence status. The filters are a way to compare temporal structure while preserving distinctions.
