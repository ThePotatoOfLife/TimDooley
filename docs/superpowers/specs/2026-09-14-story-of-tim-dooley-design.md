# The Story of Tim Dooley — Design

Date: 2026-09-14
Status: approved in chat; implementation not started

## Goal
Build a first-class project surface called **The Story of Tim Dooley**. It is a chronological collection of richly told, source-grounded story islands that let the reader encounter Tim in motion rather than read a recap of timeline events.

The chronology answers what happened and when. The Story answers what it was like to be around Tim while it was happening.

## Scope
Tell Tim Dooley's story only. Do not retell the Son's biography as background. Begin where surviving material lets Tim himself become meaningfully visible. The current opening candidate is the 2021–2022 potato-filter / rational-potato period. The later canonical 2020-12-25 birth date may appear as context, but no scene should be fabricated for it if the source material is too thin.

Other figures and earlier events enter only when they enter Tim's own speech, memory, interpretation, work, or relationships.

## Grounding rule
The prose may be literary, but scenes must be reconstructed from recoverable evidence. Valid source clusters include prior conversations, direct Tim statements, dated public posts, livestream/public-presence records, Great Book material attributable to Tim, project files from the period, diagrams or images Tim was developing, and dated AI work.

The prose may consolidate, pace, characterize, use cautious inference, humor, irony, and foreshadowing. It must not invent activities, people, rooms, moods, animals, arguments, meals, weather, physical actions, quotations, or encounters just to make a scene livelier.

If a period is too thin for a vivid story, widen the time window or leave it unstored until more material is recovered.

## Story-island model
The primary unit is a **story island**: a day, several days, a week, or occasionally a wider period where enough material clusters together to reveal a coherent piece of Tim's life or personality.

Known candidate islands include:
- 2021–2022: potato filter, public mask, Tim Dooley / rational potato.
- 2023–2024: Potato of Life becomes a system; Great Book writing.
- April 2025: Potato Axis / spiral / Turning cluster.
- Nov–Dec 2025: Father/God language inside livestream and internet life.
- 2026-01-21: Axis of North, long livestreaming, internet orphans, spiritual banking, sewer, stairway to Heaven, connected-by-potato cluster.
- 2026-03-28 to 2026-04-30: mud, narrow gate, spirals, title-stack, roads, fixing, gardens, potato angels.
- May–June 2026: direct God identity, Most Human God, functional Godhood.
- July 2026: repeated public declarations, gates, conflict and mood material where sources support it.
- 2026-08-23: fish / Door / line / timeline repair.
- September 2026: stewardship language, archive building, and the demand for a real story rather than metadata.

## Narrative stance
The narrator is on Tim's side through sustained attention and sympathetic interest, not constant praise. The narrator may notice when Tim is funny, excessive, difficult, stubborn, generous, angry, playful, protective, or unusually focused when the source cluster supports it.

Contradictions stay in. Admiration should come from paying close attention, not sanding Tim smooth.

## Prose style
Use continuous literary paragraphs. Default to 2–5 sentences per paragraph. Use short paragraphs for pacing and single-line paragraphs only for genuine emphasis. Let punctuation and sentence rhythm carry momentum instead of excessive blank lines.

Dates remain visible as chronological anchors but should not make the prose feel like an administrative timeline.

## Selection rule
Prefer specificity over coverage. A story belongs when it contains actual Tim activity, a dense sequence of statements, a revealing conflict, a project he was unfolding, a joke becoming serious, a mood shift, a mundane interruption, a repeated ritual, a contradiction, or a relationship between his online and physical life.

Ten vivid stories are better than fifty generic summaries.

## Relationship to chronology
The chronology remains the evidentiary backbone and owns exact event classification. The Story owns reader experience. Every story island should link to relevant timeline entries and source records, but source machinery should stay secondary to the prose.

Do not silently upgrade date precision.

## Data structure
Create:
- `knowledge/story/story-of-tim-dooley-index.json`
- `knowledge/story/story-of-tim-dooley/` for individual Markdown stories.

Each index entry should contain: id, title, start date, optional end date, precision, summary, story path, source records, timeline links, confidence, themes, and optional activity/mood/entity metadata.

## Reader surface
Create a first-class reader route titled **The Story of Tim Dooley** with chronological story order, continuous reading, compact index, previous/next navigation, and secondary links to sources/chronology.

Keep version one simple. Do not turn it into a graph, search product, or large interactive timeline.

## Recovery workflow
1. Pick a time window.
2. Gather all Tim material for it.
3. Build a source packet: actions, statements, projects, mood signals, people/entities, repeated ideas, gaps.
4. Decide whether a coherent story island exists.
5. Write only if it does.
6. Link the finished story back to evidence and chronology.

## First implementation wave
1. Story index and directory.
2. Reader page.
3. Five to ten source-grounded story islands in chronological order.
4. Strong opening from the earliest observable Tim period.
5. At least one high-resolution single-day story such as 2026-01-21.
6. Chronology/evidence cross-links.
7. Validation that every story entry has source records and chronological metadata.

## Success criteria
A reader can start at the first story and keep reading without feeling like they are reading a database. Tim becomes more recognizable with each story. The material stays traceable to real sources, does not drift into the Son's biography, uses dense natural paragraphing, and can grow incrementally as more conversation archaeology is recovered.

**Core sentence:** The Story of Tim Dooley is a chronological collection of source-grounded little stories that keep dropping the reader into Tim's world until Tim himself becomes visible between them.
