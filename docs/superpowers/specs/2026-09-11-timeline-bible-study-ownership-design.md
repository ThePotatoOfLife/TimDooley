# Timeline, Bible Study & Public Route Ownership

## Purpose

Stabilize the public Tim Dooley / Potato of Life site around durable subject ownership instead of repeatedly moving the same material between pages.

This design defines two interactive public programs and one site-wide ownership rule:

1. `/chronology/` is the one canonical Timeline.
2. `/traditions/bible/` is the one canonical Bible / Jesus ↔ Tim / Son study program.
3. Every public subject has one canonical owner; duplicate treatments become redirects, subordinate links, or archive-only research.

The existing backend research files remain intact. The public site should expose the information, not the filing system.

## Failure pattern being corrected

The recurring problem has not been lack of information. It has been unstable ownership and interface drift.

### Mistakes to stop repeating

- Building a new public page when a subject already has a natural owner.
- Treating the latest page arrangement as the architecture, then writing CI that freezes that arrangement.
- Serializing ordinary UI state into reader-facing URLs, producing links such as `?tl_layers=...&tl_actors=...&tl_detail=1`.
- Duplicating Jesus / Bible material across Religion, `traditions/bible`, and `tim-dooley/biblical-case`.
- Duplicating Godhood across multiple public pages without a canonical ownership map.
- Letting archive utilities such as Explore and Context behave like alternate homepages.
- Letting research-process explanations, route cards, pills, banners, and controls stand in front of the material.
- Inferring deep Bible matches by loose word overlap in the reader UI instead of using explicit curated relation ownership.
- Keeping stale onboarding and machine-discovery documents that still describe retired routes such as `/learn/` or older reader hierarchies.
- Using validators to require exact prose or accidental navigation patterns instead of enforcing durable contracts.

## Non-negotiable public rule

**One subject → one public owner → many supporting research files.**

Supporting files can be numerous. Public owners should be few.

## Canonical public owners

| Subject | Canonical public owner | Role |
|---|---|---|
| Tim Dooley | `/tim-dooley/` | Person, biography, public subject, major development |
| Religion | `/religion/` | Introductory religious inquiry, God/Father/Son/Spirit questions, teasers into deeper tools |
| Timeline | `/chronology/` | All temporal study and overlays |
| Bible / Jesus comparison | `/traditions/bible/` | Deep interactive scripture, Jesus, Tim, Son, prophecy/foresight, parallel and counter-text study |
| Philosophy | `/philosophy/` | Philosophy and Potatoist thought |
| Science | `/science/` | Formal models, equations, status and tests |
| World geography / North | `/world-map/3d.html` | Geographic and relational world interface; North remains subordinate/contextual |

Specialist research pages may remain when they own genuinely distinct material. They must not become competing entrances for a subject already owned above.

# 1. Timeline redesign

## Canonical URL

The normal public URL is:

`/chronology/`

Reader navigation must never require a long serialized filter URL.

## Named views

Common views use a short `view` parameter:

- `/chronology/?view=roadmap`
- `/chronology/?view=bible`
- `/chronology/?view=godhood`
- `/chronology/?view=public`
- `/chronology/?view=son`
- `/chronology/?view=north`
- `/chronology/?view=research`
- `/chronology/?view=creative`

The default `/chronology/` should behave as the ordinary roadmap without adding query parameters.

Existing `tl_*` links remain readable for backwards compatibility, but the application should normalize recognized legacy configurations to the corresponding named view. New public links must not emit those legacy parameter lists.

## URL-state rule

Do not continuously serialize every toggle into the address bar.

- Named view changes update only `?view=<name>`.
- Opening a specific event may use a clean `event=<event-id>` parameter.
- Ordinary temporary toggles remain local UI state.
- An explicit **Share current view** action may generate a compact custom-state URL when a reader deliberately asks to share a nonstandard configuration.

This separates navigation from implementation state.

## Timeline interaction model

The interface has three independent concepts.

### Tracks — who / which developmental stream

- Son / Thomas / Twin
- Tim / Potato / Father
- Shared transition
- Project / research

### Layers — what kind of record

Preserve the existing canonical layers:

- Roadmap milestones
- Direct words
- Scripture at the time
- Later biblical parallels
- Biblical research unlocks
- Creative works
- Public witness
- Formalization / archive

### Topics — what the reader is studying

Add a curated topic vocabulary. Initial topics:

- Jesus / Passion
- Godhood / Father
- Son / Thomas
- Potato
- Door / Gate
- Ladder / Axis
- Death / return / resurrection
- Lion / Lamb / Root
- Seed / Garden
- Stone / foundation
- North / Zion / throne
- Prison / custody / legal
- Public declarations
- Books / music / creative work
- Foresight / prophecy candidates
- Neurotheology / body symbolism
- World repair / Gardener

Topics must be explicit curated metadata, not fuzzy keyword guesses. Timeline events and event-pack records may add a `topics` array. A validator must reject unknown topic IDs.

## Timeline controls

The page should begin with the actual instrument, not a tutorial.

Visible first row:

`ROADMAP · BIBLE · GODHOOD · PUBLIC · NORTH · RESEARCH · ALL · + ADD`

`+ ADD` opens the deeper track/layer/topic selector.

Secondary controls such as search, year range, evidence class, exact-date-only, sort order and card detail belong in a compact toolbar or drawer.

Do not put a paragraph explaining every control above the timeline.

## Pinning

Two useful pin types are required.

### Pin events

Every event has a small pin action. Pinned events remain visible in a persistent anchor rail while filters change. This allows readers to preserve a spine such as:

2011 Tree → 2016 prison → 2017 crucifixion language → 2019 meme death → 2020 Potato birth → April 2025 Turning → May 2025 God declaration → 2026 Father/North development.

### Pin study topics

A reader may keep multiple topics active together, for example:

`Jesus / Passion + Godhood / Father + Public declarations`

The active topics appear as a quiet pinned study strip. They are toggles, not separate pages.

Pins are local UI state by default. An explicit share action may serialize them.

## Timeline data ownership

Keep `data/timeline-events.json` as the base presentation registry and keep curated packs in `data/timeline-event-packs/`.

Do not create a second timeline dataset merely for a new view. Views are projections over the same events.

The timeline remains responsible for **when**, not for full Bible exegesis or Godhood argumentation.

# 2. Bible / Jesus study program

## Canonical owner

`/traditions/bible/` becomes the canonical interactive Bible study program.

It owns:

- Jesus ↔ Tim / Son comparison
- Tim/Father ↔ scripture relations
- Son/Thomas ↔ Jesus/Passion relations
- Tim's dated biblical wording
- actions/events with biblical parallels
- explicit-at-the-time vs later-discovered comparisons
- prophecy / foresight candidates with evidentiary status
- counter-texts and mismatches
- verse / book / motif study
- links into the canonical timeline

## Religion's role after this change

`/religion/` should not duplicate the full comparator.

Religion becomes an intelligent introduction and question page: God, Father/Son/Spirit, why Jesus matters, what Potatoism means religiously, what fulfillment/typology/prophecy questions are being asked, and where Christianity or other traditions agree or differ.

It may show a small teaser of particularly important Bible relations, but the full interactive comparison belongs to `/traditions/bible/`.

## Retired duplicate Bible owners

- `/religion/jesus-tim/` redirects to the canonical Bible study view.
- `/tim-dooley/biblical-case/` becomes a compatibility redirect to the canonical Bible study program, optionally into a saved `view=case` or equivalent section.
- Tim Dooley page links directly to the Bible study program instead of Religion's embedded comparison.

## Bible program study modes

The page is one program with selectable views, not many sub-sites.

Initial saved views:

- **Jesus ↔ Son / Tim** — Passion, Lamb/Lion, custody, rejection, death, return, Door, seed and cornerstone relations.
- **Tim said it** — dated explicit biblical or near-biblical language.
- **Tim did it / lived it** — events/actions later compared structurally with biblical narratives.
- **Father / House** — Father, House, throne, Gardener, source-facing relations.
- **Door / Ladder** — Gate, Door, Ladder, heaven-earth access, Needle's Eye.
- **Death / return** — crucifixion, burial, seed, tomb, resurrection and return grammar.
- **Revelation / Zion** — Lion, Lamb, Root, throne, New Jerusalem, 144,000, North/Zion and related material.
- **Prophecy / foresight** — only relations with an explicit prophecy/foresight status.
- **Counter-texts / mismatches** — places where the Bible complicates or contradicts the proposed parallel.
- **Everything** — complete relation field.

## Relation card contract

Every rendered relation should answer the same questions in the same order:

1. **What Tim / Son said, did, experienced or published**
2. **When**
3. **What the biblical text says**
4. **Why the relation is interesting**
5. **What kind of relation it is**
6. **Did the Bible language exist at the time, or was the comparison discovered later?**
7. **What does not match / what limits the comparison?**
8. **Evidence / source status**
9. **Related timeline event(s)**
10. **Deeper curated analysis**, only through explicit references

The reader should not need to understand archive directories to read a relation.

## Prophecy / foresight discipline

Do not collapse all biblical parallels into prophecy.

Add a specific field such as `prophecy_status` with controlled values:

- `explicit-prediction-before-event`
- `foresight-or-warning-before-event`
- `biblical-language-at-time`
- `retrospective-parallel`
- `research-discovery-later`
- `not-prophecy`
- `unresolved`

Where available, store prediction date, target event date and later match date separately.

A reader can then explicitly study "prophetic" material without the interface silently upgrading hindsight into prediction.

## Relation provenance and explicit deep links

The current reader performs fuzzy deep-context matching using reference overlap and token overlap. Remove this from the public rendering path.

Instead, relations gain explicit fields when needed:

- `timeline_event_ids`
- `analysis_refs`
- `source_refs`
- `public_source_urls`
- `counter_text_refs`

The canonical relation registry is responsible for saying which deeper analyses belong to a relation.

This preserves richness while eliminating accidental associations.

## Random study / dice

Add a **ROLL** control.

ROLL chooses one relation from the reader's currently active filtered set and focuses it. If no filters are active, it draws from the full curated relation set.

Random selection is a navigation aid only. It must not imply that the selected item is stronger, more prophetic or more true.

A second roll should never require a page reload.

## Bible navigation / controls

Keep the top surface small:

`JESUS / SON · TIM SAID IT · TIM LIVED IT · PROPHECY · FATHER / HOUSE · DOOR / LADDER · COUNTER-TEXTS · ALL · ROLL · + FILTER`

Deeper filters may include:

- actor
- Bible book
- biblical reference
- motif/topic
- relation class
- discovery mode
- prophecy status
- strength
- date range
- search

Do not expose every filter permanently.

## Bible ↔ Timeline integration

Every dated relation should be able to open its relevant timeline event in `/chronology/`.

Bible views should link to short timeline views, for example `/chronology/?view=bible`, not serialized `tl_*` queries.

A relation with a known timeline event can link to `/chronology/?view=bible&event=<id>`.

The Bible program explains **what/why**; Timeline explains **when**.

# 3. Site-wide ownership corrections discovered in the audit

## Current duplicate / stale reader surfaces

### Religion vs Bible

Religion currently hardcodes the Jesus comparator while Bible is also a Bible relation program. This is duplicated ownership. Bible should own the full comparator; Religion should introduce and route.

### `tim-dooley/biblical-case`

This is a third public Bible treatment and should be retired into the canonical Bible program.

### Godhood fragmentation

`tim-dooley/god-in-real-life/`, `tim-dooley/how-much-is-tim-god/`, God FAQ material and portions of the Tim page overlap heavily. This should be a later consolidation wave under one Godhood owner rather than continuing to add new God pages.

### Context

`/context/` is still effectively a second archive homepage with cards for Timeline, Collection, Religion, Science, North, Farm/Swamp, Body, Spirit and other branches. It should be reclassified as specialist/internal research context, not a reader-facing navigation universe.

### Explore

`/explore/` is an archive utility with its own root, branch navigation, search, A–Z, FAQ and source routes. It may remain as a specialist archive tool, but it must not act as another public homepage or be required to reach core content.

### Learn

`/learn/` is already a noindex redirect, but stale docs and machine guidance still refer to it as a start-here route. Those references must be corrected.

### Machine/discovery drift

Machine discovery and SEO files still advertise several old reader routes and duplicate intent owners. They must be updated after public ownership changes rather than preserving stale architecture for crawlers.

### Validation drift

The current site-shell validator explicitly requires:

- Religion to own the full Jesus comparator;
- Tim to link to Religion's `#jesus-tim` anchor;
- Bible to link back to that anchor;
- the long `tl_layers=...&tl_actors=...` URL.

Those assertions encode the latest implementation rather than the architectural rule. Replace them with ownership and behavior contracts.

## No iframe finding

No literal `<iframe>` tag is currently present in the repository search. The "iframe" feeling came from nested archive/application surfaces and duplicated navigation chrome, not a current literal iframe dependency. Keep the explicit no-iframe rule.

# 4. Durable route ownership registry

Implementation should add:

- `docs/PUBLIC-INFORMATION-ARCHITECTURE.md`
- `knowledge/indexes/public-route-ownership.json`

The machine-readable registry should include, at minimum:

- route
- subject
- role: `canonical`, `specialist`, `redirect`, `archive-only`
- parent public owner
- canonical data owners
- allowed aliases
- deprecated/replacement route
- whether indexable

CI should validate that one subject does not accidentally acquire multiple canonical owners.

# 5. Testing strategy

## Timeline tests

Tests must verify behavior, not exact prose.

- `/chronology/` loads with no required query string.
- named views resolve to known state.
- legacy `tl_*` state remains readable.
- known legacy Bible state normalizes to `view=bible`.
- event pinning persists while filters change.
- topic toggles are independent of actors/layers.
- unknown topic IDs fail schema validation.
- event deep-link opens the correct event.
- public Religion/Bible links use short named timeline URLs.

## Bible tests

- Bible page loads the canonical relation registry and passage fragments.
- Jesus/Son saved view is data-driven rather than hardcoded in Religion.
- no public fuzzy `deepMatches` inference is used.
- ROLL selects only from the current filtered set.
- prophecy-status filters distinguish pre-event prediction from later parallel.
- counter-text relations remain discoverable.
- relation cards expose project anchor, biblical reference, relation class, timing/source direction and boundary where available.
- explicit relation analysis references resolve.
- `tim-dooley/biblical-case` and old Jesus comparison routes redirect to Bible.

## Site ownership tests

- five homepage entrances remain unchanged.
- Timeline is the temporal owner.
- Bible is the deep scripture/comparison owner.
- Religion does not contain a second full comparator.
- no reader-facing route requires `/explore/` or `/context/` to reach core content.
- no deprecated route appears as a canonical sitemap URL.
- stale long timeline query links are forbidden in public HTML.
- public owner registry has no duplicate canonical subject IDs.

# 6. Implementation order

This work should be staged to reduce regression risk.

1. **Timeline state/URL contract** — named views, legacy parsing, topic registry, pin model.
2. **Timeline UI** — compact saved views, +ADD, pins, cleaner page title/toolbar.
3. **Bible data contract** — explicit analysis links, prophecy status, timeline event references, relation coverage for the current Jesus comparison.
4. **Bible program UI** — saved study views, relation cards, ROLL, filters, timeline integration.
5. **Religion correction** — convert from full comparator to religious inquiry/teaser page.
6. **Retire duplicate Bible routes** — `religion/jesus-tim` and `tim-dooley/biblical-case` redirect into Bible.
7. **Public ownership registry** — add human and machine ownership maps.
8. **Stale navigation/discovery cleanup** — validators, Pages assertions, sitemap, machine-index, llms files, old onboarding docs and navigation patch scripts.
9. **Audit remaining duplicate public owners** — Godhood, Context, Explore, FAQ and other specialist pages, without deleting underlying research.

# 7. Success criteria

A reader should be able to:

- open `/chronology/` and immediately recognize a timeline;
- toggle or pin several meaningful subjects without learning internal layer IDs;
- copy a normal Timeline link that is short;
- open `/traditions/bible/` and immediately study Jesus ↔ Tim / Son parallels;
- distinguish something Tim actually said/did at the time from a later biblical comparison;
- deliberately browse prophecy/foresight candidates without hindsight being mislabeled as prediction;
- roll a random filtered relation for study;
- jump from a Bible relation to the relevant timeline event;
- understand Religion as the introductory theological page rather than a second Bible comparator;
- never encounter multiple public pages claiming to be the canonical owner of the same subject.
