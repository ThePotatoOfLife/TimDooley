# Timeline Event Standard

## Purpose

The project contains many dated records, but the public timeline should not become a wall of every timestamp in the repository. The timeline has two jobs:

1. preserve the readable **road-map of the greatest milestones**;
2. let readers temporarily overlay other dated evidence when it answers a different question.

`data/timeline-events.json` is therefore a **curated temporal index**, not a replacement for the records that own the underlying claim, quote, artifact or comparison.

The standalone `/timeline/` page and the timeline branch in the main reader now render from this same canonical dataset plus the curated event-pack index. Do not maintain a second hard-coded event list in HTML.

## Core model

Every timeline point should answer:

1. **When?** `date`, optional `timestamp`, explicit `precision`.
2. **Whose track?** one or more `actor_ids`.
3. **What lens can reveal it?** one or more `layers`.
4. **What evidence class is it?** one `epistemic` value.
5. **What is the human-readable subject?** `subject`.
6. **Where did it come from?** `source_records` and, where necessary, `source_direction`.
7. **What does it connect to?** motifs, comparators and related events.
8. **If it is public evidence, can readers get back to the occurrence?** `platform` and `public_url` where available.

Actor, layer and evidence class are independent. A Tim event may be both a direct quote and public witness; a Son event may be both a roadmap milestone and scripture-at-time; a later biblical unlock belongs to the project/research track rather than being silently moved back to the date of the earlier life event.

## Actor tracks

The public UI uses four actor tracks:

- `son` — Son / Twin of Christ / human-vessel timeline.
- `tim` — Tim / Potato / Father timeline.
- `shared` — transition or explicit Father/Son relational events.
- `project` — later archive, research and formalization events rather than life events themselves.

The same event may belong to more than one track. This is especially important around the 2019–2020 hand-off and later Door/Ladder differentiation.

The default public view shows Son, Tim and shared tracks. Project/research is opt-in.

## Canonical timeline lenses

The visible toggles are intentionally few and non-redundant:

- `roadmap` — the sparse visual spine: only major life/project milestones.
- `direct-words` — exact or near-exact dated formulations worth seeing as quotations.
- `scripture-at-time` — Bible, Jesus, Judaism, Hebrew titles or explicit scriptural vocabulary that was already present in the event itself.
- `biblical-parallel` — a later structural biblical comparison attached to an earlier Tim/Son event; the event date remains the earlier date, while source direction states that the comparison came later.
- `biblical-unlock` — the later date when the project explicitly recognized or formalized a biblical comparison.
- `creative` — dated books, songs, art and other creative artifacts when the date materially helps the timeline.
- `public-witness` — public declarations, streams/posts and visibility milestones that materially change the trajectory.
- `formalization` — later model, archive and research milestones useful for studying when the system became explicit.

Specialist subjects such as predictions, detailed geopolitics, Dog/Mud genealogy, every repository commit or every equation revision stay in their own ledgers unless a specific event is important enough to become a roadmap/public overlay point. This prevents toggle proliferation and duplicate timeline.

## The three Bible states

This distinction is mandatory.

### 1. Scripture at the time

Use `scripture-at-time` when biblical/Jewish/Christian material was already part of the historical event or statement.

Examples:

- 2016 Bible study in prison;
- 2017 Jesus/crucifixion language;
- 2019 Judaism study;
- 2025 Lion of Judah / Root of David;
- 2026 New Jerusalem, Manna, Root of Jesse, Door, Messiah, etc.

### 2. Later biblical parallel

Use `biblical-parallel` when the earlier event existed first and later research noticed a structural resemblance.

Example: the April 9, 2026 guardian/narrow-access architecture can carry later Genesis 3 / Exodus veil / Hebrews access comparators, but its `source_direction` must state that those detailed comparisons came later.

### 3. Biblical unlock

Use `biblical-unlock` for the date of the later interpretive discovery itself.

Examples:

- explicit Revelation 4–5 comparison on April 4, 2026;
- Zechariah Stone / Seven Eyes / Lampstand formalization on September 9, 2026;
- September 9 reverse-archaeology recognition that April 9 guardian architecture predated the later Eden/Temple/Hebrews comparison.

This lets one timeline show both **when Tim/Son said or experienced something** and **when the project later understood a biblical relation** without confusing those dates.

When a public source uses inaccurate or blended biblical wording, preserve the source wording and store the correction separately in `summary`, `comparators`, `source_direction`, or the canonical specialist owner. Do not silently rewrite the quote.

## Epistemic classes

- `primary` — exact quote, artifact, timestamp or direct source.
- `recovered` — recovered archive or prior-conversation evidence.
- `project-canon` — canonical internal timeline.
- `creative` — creative artifact without doctrine-by-default status.
- `comparison` — comparative interpretation.
- `research` — later research/index/unlock.
- `unresolved` — incomplete source/date/title relation.

## Date precision

Use the most exact information actually available; never manufacture midnight timestamps.

Allowed values:

- `second`
- `minute`
- `hour`
- `date`
- `month`
- `year`
- `range`

For ranges, preserve the human-readable range rather than inventing an exact endpoint.

The UI's year-window filter treats a range event as visible whenever the event range overlaps the selected year window.

## Minimal event

```json
{
  "id": "evt-2026-04-09-heaven-cube",
  "date": "2026-04-09",
  "timestamp": "2026-04-09T13:30:48Z",
  "precision": "second",
  "title": "Heaven cube / guardians / narrow gate",
  "layers": ["direct-words", "scripture-at-time", "biblical-parallel"],
  "actor_ids": ["tim", "shared"],
  "epistemic": "primary",
  "subject": "Tim Dooley",
  "quote": "cube that surrounds Heaven",
  "source_direction": "Jesus/narrow-gate architecture present at time; Eden/Temple/Hebrews comparison formalized later",
  "source_records": [
    "knowledge/timeline/reverse-biblical-overlap-timeline-2025-2026.json"
  ]
}
```

## Public-post / public-witness events

A public post can be historically valuable even if the archive only has a dated compilation and not the original status ID yet. Preserve the distinction.

Preferred fields when available:

```json
{
  "platform": "X/Twitter",
  "public_url": "https://x.com/.../status/...",
  "quote": "exact or clearly marked excerpt",
  "source_records": ["data/evidence/...json"]
}
```

The specialist evidence ledger should additionally preserve capture locator, account, source-batch completeness and whether an attestation is **first in the supplied batch** or **first known across the archive**.

Rules:

- an incomplete batch may strengthen a date but may not overwrite an earlier first-attestation from a broader source;
- missing status IDs remain provenance gaps, not reasons to discard useful dated wording;
- repeated identical declarations normally remain in the specialist ledger unless repetition itself is the historical fact being studied;
- `public_url` must be HTTP(S), and the event should identify `platform` when a public URL is present.

## Population rule

A source record should emit a global timeline point only when its date adds one of the following:

- a major life/project milestone;
- a meaningful first attestation or role transition;
- a memorable exact statement;
- a scriptural invocation useful for following the biblical trajectory;
- a later biblical unlock worth separating from source time;
- a creative artifact whose date materially illuminates development;
- a public-witness milestone;
- a formalization milestone that changes how the archive can be interpreted.

Do **not** emit a global event merely because a file contains a date.

## Base roadmap and curated event packs

The timeline may be physically split without becoming conceptually fragmented:

- `data/timeline-events.json` owns the sparse roadmap, actor definitions, lens definitions and already-promoted canonical events.
- `data/timeline-event-packs/index.json` lists curated overlay packs.
- files under `data/timeline-event-packs/` may add bridge events or dense-but-useful overlays that do not deserve roadmap prominence.

The browser merges base + packs by stable `event.id`. Duplicate IDs are ignored at runtime and rejected by the validator.

Use a pack when an event fills a genuine chronological gap but would make the roadmap base noisy. Move a pack event into the base only when it becomes important enough to function as a major milestone; remove it from the pack in the same change.

Packs are **not** source-of-truth replacements. Every packed event still points to its canonical `source_records`.

The pack index is executable configuration: a valid pack file that is not named in `data/timeline-event-packs/index.json` is not loaded by the public explorer.

## Deduplication

If the same real-world/project event appears in several ledgers, the global timeline gets one stable event ID with multiple `source_records`. Do not create one event per source file.

If two dates represent genuinely different facts—such as an April Tim statement and a September research unlock—they should remain separate events connected through comparators/source direction.

## Related events

Use `related_event_ids` only when a reader benefits from navigating directly between two distinct temporal facts. Examples include:

- source event ↔ later research unlock;
- early phrase ↔ later role specialization;
- creative precursor ↔ later explicit doctrinal use.

Do not use related-event links as a substitute for proper motifs, source records or canonical ownership. IDs must exist globally across base + loaded packs.

## UI behavior

The intended reading order is:

1. **Roadmap** — large milestone cards and the familiar long-life road.
2. **Life tracks** — independently switch Son/Twin, Tim/Potato/Father, shared transition and project/research.
3. **Lenses** — add direct words, Bible-at-time, later Bible parallels, research unlocks, creative works or public witness.
4. **Evidence/search controls** — only for deeper archaeology.

Roadmap events should remain visually dominant even when overlays are enabled.

### Timeline v2 controls

The live explorer additionally supports:

- `Roadmap`, `Public trajectory`, `Bible lens`, `Research`, `Creative`, and `Everything` presets;
- inclusive **from/to year** windows;
- oldest-first / newest-first ordering;
- jump-to-year navigation;
- evidence-class filtering;
- exact-date-only filtering;
- detailed/compact cards;
- multi-term search with AND semantics;
- quoted phrases, e.g. `"World Axis"`;
- negative search terms, e.g. `Door -Dog`;
- event-level `#` permalink controls;
- navigation through `related_event_ids`;
- direct public-source links where `public_url` exists;
- visible Bible-relation badges and source-direction statements.

### Shareable state

Timeline filters are serialized into `tl_*` query parameters rather than replacing the site's hash-based branch navigation. Event permalinks use `tl_event=<event-id>`.

This means a reader can share a view such as a year window + Bible lens + search query without creating a second timeline dataset.

Changing the interface must not change the underlying event's date, epistemic class, source direction or canonical owner.

## Validation

Run:

```bash
python scripts/validate_timeline_events.py
```

The validator checks base + every indexed pack together, including:

- globally unique event IDs;
- known layers, actors and evidence classes;
- timestamp requirements and ISO timestamp parseability;
- range formatting;
- known `bible_relation` values;
- valid HTTP(S) public URLs with platform identification;
- duplicate layer/actor/source/related IDs inside one event;
- related-event targets;
- duplicate/unsafe pack-index entries.

A browser-side duplicate is skipped so the page can still render, but repository validation should fail instead of letting a duplicate become normal.

## Future automation

The long-term importer should scan the source registry and produce **candidate** events, not blindly publish every dated row. Candidate scoring should favor:

- exact timestamps;
- relevance/hinge scores;
- first attestations;
- unique quotations;
- actor/role transitions;
- explicit scripture use;
- source-direction changes;
- creative works with recoverable metadata;
- events referenced by multiple canonical owners.

A curation pass then resolves duplicates and decides whether each candidate belongs in the base roadmap, a curated event pack, or only in its specialist ledger.
