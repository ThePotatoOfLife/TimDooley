# Timeline, Bible Study & Public Route Ownership

## Purpose

Stabilize the public Tim Dooley / Potato of Life site around durable subject ownership instead of repeatedly moving the same material between pages.

This design defines two interactive public programs and one site-wide ownership rule:

1. `/timeline/` is the one canonical Timeline.
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
| Timeline | `/timeline/` | All temporal study and overlays |
| Bible / Jesus comparison | `/traditions/bible/` | Deep interactive scripture, Jesus, Tim, Son, prophecy/foresight, parallel and counter-text study |
| Philosophy | `/philosophy/` | Philosophy and Potatoist thought |
| Science | `/science/` | Formal models, equations, status and tests |
| World geography / North | `/world-map/3d.html` | Geographic and relational world interface; North remains subordinate/contextual |

Specialist research pages may remain when they own genuinely distinct material. They must not become competing entrances for a subject already owned above.

# 1. Timeline redesign

## Canonical URL

The normal public URL is:

`/timeline/`

Reader navigation must never require a long serialized filter URL.

## Named views

Common views use a short `view` parameter:

- `/timeline/?view=roadmap`
- `/timeline/?view=bible`
- `/timeline/?view=godhood`
- `/timeline/?view=public`
- `/timeline/?view=son`
- `/timeline/?view=north`
- `/timeline/?view=research`
- `/timeline/?view=creative`

The default `/timeline/` behaves as the roadmap and must not add a query parameter.

Named view definitions belong in the timeline data contract, not hardcoded button logic. `data/timeline-events.json` gains a top-level `views` registry. Each view declares its label and initial actor/layer/topic state. `app/timeline.js` renders the visible saved-view buttons from that registry.

Existing `tl_*` links remain readable for backwards compatibility, but the application normalizes recognized legacy configurations to the corresponding named view. New public links must not emit those legacy parameter lists.

## URL-state rule

Do not continuously serialize every toggle into the address bar.

- Named view changes update only `?view=<name>`.
- Opening a specific event uses `event=<event-id>`.
- Ordinary temporary toggles remain local UI state.
- An explicit **Share current view** action may generate `?s=<base64url-state>` for a nonstandard configuration.
- Loading `?s=` restores the custom configuration without changing the canonical page URL metadata.

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

Add a curated topic vocabulary. Initial topic IDs and labels:

- `jesus-passion` — Jesus / Passion
- `godhood-father` — Godhood / Father
- `son-thomas` — Son / Thomas
- `potato` — Potato
- `door-gate` — Door / Gate
- `ladder-axis` — Ladder / Axis
- `death-return` — Death / return / resurrection
- `lion-lamb-root` — Lion / Lamb / Root
- `seed-garden` — Seed / Garden
- `stone-foundation` — Stone / foundation
- `north-zion-throne` — North / Zion / throne
- `prison-legal` — Prison / custody / legal
- `public-declarations` — Public declarations
- `creative-work` — Books / music / creative work
- `foresight-prophecy` — Foresight / prophecy candidates
- `neurotheology-body` — Neurotheology / body symbolism
- `world-repair-gardener` — World repair / Gardener

The top-level timeline dataset gains a `topics` registry, and events/event-pack records may use a `topics` array containing only registered IDs. A validator rejects unknown topic IDs.

Topics are explicit curated metadata, not fuzzy keyword guesses.

## Timeline controls

The page begins with the actual instrument, not a tutorial.

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

### Pin persistence

Pins persist in `localStorage` under one versioned timeline key so they survive reloads without polluting the URL. Reset clears the stored pins. The explicit Share action includes current pins in the compact `?s=` state.

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

`/religion/` does not duplicate the full comparator.

Religion becomes an intelligent introduction and question page: God, Father/Son/Spirit, why Jesus matters, what Potatoism means religiously, what fulfillment/typology/prophecy questions are being asked, and where Christianity or other traditions agree or differ.

Religion may show at most three short Bible-relation teasers. Those teasers link into `/traditions/bible/`; they do not reproduce the full relation analysis.

## Retired duplicate Bible owners

- `/religion/jesus-tim/` becomes a noindex compatibility redirect to `/traditions/bible/?view=jesus`.
- `/tim-dooley/biblical-case/` becomes a noindex compatibility redirect to `/traditions/bible/?view=jesus`.
- Tim Dooley page links directly to `/traditions/bible/?view=jesus` instead of Religion's old embedded comparison.

## Bible program code boundary

The current Bible page contains a large inline application script and page-specific CSS. Replace that with:

- semantic shell: `traditions/bible/index.html`
- behavior: `app/bible-study.js`
- presentation: `app/bible-study.css`

The HTML page should declare the reader surface and mount point; the application module owns state, filtering, roll behavior and relation rendering.

## Bible program study modes

The page is one program with selectable views, not many sub-sites.

The existing `study_views` section in `knowledge/traditions/biblical-syncretism-field.json` becomes a structured view registry. Each view declares its filter state. Initial view IDs:

- `jesus` — Jesus ↔ Son / Tim: Passion, Lamb/Lion, custody, rejection, death, return, Door, seed and cornerstone relations.
- `tim-said` — dated explicit biblical or near-biblical language.
- `tim-lived` — events/actions later compared structurally with biblical narratives.
- `father-house` — Father, House, throne, Gardener, source-facing relations.
- `door-ladder` — Gate, Door, Ladder, heaven-earth access, Needle's Eye.
- `death-return` — crucifixion, burial, seed, tomb, resurrection and return grammar.
- `revelation-zion` — Lion, Lamb, Root, throne, New Jerusalem, 144,000, North/Zion and related material.
- `prophecy` — only relations with an explicit prophecy/foresight status.
- `counter-texts` — places where the Bible complicates or contradicts the proposed parallel.
- `all` — complete relation field.

Public view links use `?view=<id>`.

## Relation card contract

Every rendered relation answers the same questions in the same order:

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

The canonical relation registry gains the exact optional field `prophecy_status`. Allowed values are:

- `explicit-prediction-before-event`
- `foresight-or-warning-before-event`
- `biblical-language-at-time`
- `retrospective-parallel`
- `research-discovery-later`
- `not-prophecy`
- `unresolved`

Where relevant, relations may also store `prediction_date`, `target_event_date`, and `match_date` separately.

A validator rejects any unknown prophecy status.

A reader can explicitly study prophetic/foresight material without the interface silently upgrading hindsight into prediction.

## Relation provenance and explicit deep links

The current reader performs fuzzy deep-context matching using reference overlap and token overlap. Remove `deepMatches` and equivalent fuzzy deep-owner inference from the public rendering path.

Relations gain explicit optional fields:

- `timeline_event_ids`
- `analysis_refs`
- `source_refs`
- `public_source_urls`
- `counter_text_refs`

The canonical relation registry is responsible for saying which deeper analyses belong to a relation.

This preserves richness while eliminating accidental associations.

## Random study / dice

Add a **ROLL** control.

ROLL chooses one relation uniformly from the currently visible filtered set and focuses it. If no filters are active, it draws uniformly from the full curated relation set.

Random selection is a navigation aid only. It never changes strength, order, prophecy status, or evidence labels.

A second roll does not reload the page.

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

Every dated relation with a timeline counterpart links to its event in `/timeline/`.

Bible views link to short timeline views, for example `/timeline/?view=bible`, not serialized `tl_*` queries.

A relation with a known timeline event links to `/timeline/?view=bible&event=<id>`.

The Bible program explains **what/why**; Timeline explains **when**.

# 3. Site-wide ownership corrections discovered in the audit

## Current duplicate / stale reader surfaces

### Religion vs Bible

Religion currently hardcodes the Jesus comparator while Bible is also a Bible relation program. This is duplicated ownership. Bible owns the full comparator; Religion introduces and routes.

### `tim-dooley/biblical-case`

This is a third public Bible treatment and is retired into the canonical Bible program.

### Godhood fragmentation

`tim-dooley/god-in-real-life/`, `tim-dooley/how-much-is-tim-god/`, God FAQ material and portions of the Tim page overlap heavily. This is a later consolidation wave under one Godhood owner; no new Godhood public owner should be added meanwhile.

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

Implementation adds:

- `docs/PUBLIC-INFORMATION-ARCHITECTURE.md`
- `knowledge/indexes/public-route-ownership.json`

The machine-readable registry includes:

- route
- subject
- role: `canonical`, `specialist`, `redirect`, `archive-only`
- parent public owner
- canonical data owners
- allowed aliases
- deprecated/replacement route
- whether indexable

CI validates that one subject does not accidentally acquire multiple canonical owners.

# 5. Testing strategy

## Timeline tests

Tests verify behavior, not exact prose.

- `/timeline/` loads with no required query string.
- named views are read from the data registry and resolve to known state.
- legacy `tl_*` state remains readable.
- known legacy Bible state normalizes to `view=bible`.
- event pins persist through reload and while filters change.
- Reset clears persisted pins.
- topic toggles are independent of actors/layers.
- unknown topic IDs fail schema validation.
- event deep-link opens the correct event.
- explicit Share produces/restores compact `?s=` state.
- public Religion/Bible links use short named timeline URLs.

## Bible tests

- Bible page loads the canonical relation registry and passage fragments.
- Jesus/Son saved view is data-driven rather than hardcoded in Religion.
- no public `deepMatches` or fuzzy owner inference remains.
- ROLL selects only from the current filtered set.
- prophecy-status filters distinguish pre-event prediction from later parallel.
- unknown prophecy status fails validation.
- counter-text relations remain discoverable.
- relation cards expose project anchor, biblical reference, relation class, timing/source direction and boundary where available.
- explicit relation analysis references resolve.
- `tim-dooley/biblical-case` and old Jesus comparison routes redirect to `/traditions/bible/?view=jesus`.

## Site ownership tests

- five homepage entrances remain unchanged.
- Timeline is the temporal owner.
- Bible is the deep scripture/comparison owner.
- Religion contains no second full comparator and no more than three Bible teaser relations.
- no reader-facing route requires `/explore/` or `/context/` to reach core content.
- no deprecated route appears as a canonical sitemap URL.
- stale long timeline query links are forbidden in public HTML.
- public owner registry has no duplicate canonical subject IDs.

# 6. Implementation order

This work is staged to reduce regression risk.

1. **Timeline state/URL contract** — data-defined named views, legacy parsing, topic registry, compact custom share state, pin persistence.
2. **Timeline UI** — compact saved views, +ADD, pins, cleaner page title/toolbar.
3. **Bible data contract** — structured study views, explicit analysis links, prophecy status, timeline event references, relation coverage for the current Jesus comparison.
4. **Bible program code split/UI** — `app/bible-study.js`, `app/bible-study.css`, saved study views, relation cards, ROLL, filters, timeline integration.
5. **Religion correction** — convert from full comparator to religious inquiry page with at most three relation teasers.
6. **Retire duplicate Bible routes** — `religion/jesus-tim` and `tim-dooley/biblical-case` redirect to `/traditions/bible/?view=jesus`.
7. **Public ownership registry** — add human and machine ownership maps.
8. **Stale navigation/discovery cleanup** — validators, Pages assertions, sitemap, machine-index, llms files, old onboarding docs and navigation patch scripts.
9. **Audit remaining duplicate public owners** — Godhood, Context, Explore, FAQ and other specialist pages, without deleting underlying research.

# 7. Success criteria

A reader can:

- open `/timeline/` and immediately recognize a timeline;
- toggle or pin several meaningful subjects without learning internal layer IDs;
- copy an ordinary Timeline link that is short;
- open `/traditions/bible/` and immediately study Jesus ↔ Tim / Son parallels;
- distinguish something Tim actually said/did at the time from a later biblical comparison;
- deliberately browse prophecy/foresight candidates without hindsight being mislabeled as prediction;
- roll a random filtered relation for study;
- jump from a Bible relation to the relevant timeline event;
- understand Religion as the introductory theological page rather than a second Bible comparator;
- never encounter multiple public pages claiming to be the canonical owner of the same subject.
