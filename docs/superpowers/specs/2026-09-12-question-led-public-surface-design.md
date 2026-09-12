# Question-Led Public Surface Design

Date: 2026-09-12
Status: approved design direction; implementation pending
Branch: `project-consolidation-2026-09-12`

## Goal

Keep the public site as simple and legible as the current five-branch skeleton while making it substantially more meaningful to a first-time reader.

The public surface should answer three things immediately:

1. What is this project?
2. What questions is it trying to answer?
3. Where should I go next if one of those questions interests me?

The site should not expose repository complexity as navigation. Backend depth should be promoted selectively into concise public questions, answers, reflections and routes.

The governing reader grammar is:

`major branch → natural question → compact stub → quieter thread → canonical deep owner`

The deeper the material, the smaller its visual claim on the page.

## Source-of-truth order during this redesign

The public redesign is built from the newest consolidated project, not from whichever older PR has the largest amount of content.

Priority order:

1. `project-consolidation-2026-09-12` / PR #45 is the working architectural truth.
2. `main` is the historical baseline and compatibility reference until #45 is merged.
3. Open PRs are source branches from which unique content, functionality or research may be recovered.
4. Older PR shells, naming systems and public layouts are not authoritative merely because useful content exists inside them.
5. A recovered record must be fitted into the current canonical owner rather than recreating an older public subsystem.

Examples:

- Christianity material from PR #29/#46 can strengthen Religion without making an old theology page the new public owner.
- Map functionality from PR #35/#39/#42 can strengthen World Map without restoring Atlas as a product name.
- Timeline research from PR #25 can strengthen Timeline/Tim without restoring Chronology.
- Science contracts from PR #28/#33 can strengthen Science without restoring Science Atlas as a public product.

## The public hierarchy

### Tier 1 — Major branches

The five primary public doors remain:

- Tim Dooley
- Religion
- Philosophy
- Science
- World Map

They remain the most visible elements after the project introduction, but they must become physically smaller and denser than the current homepage rows.

No backend directory becomes a sixth primary door merely because it contains substantial data.

### Tier 2 — Major questions

Each major branch exposes a small set of strong questions before it exposes taxonomies, records or technical structures.

Questions are the connective tissue of the site. They explain why a branch exists and naturally create cross-links between branches.

A homepage branch preview should normally expose two questions. The branch page itself may expose roughly four to eight primary questions, depending on maturity and density.

### Tier 3 — Minor threads

Smaller subject families are shown with lower visual weight. They can appear as compact textual links, chips, inline thread lists or quiet subheadings rather than full-size cards.

Examples include:

- Culture & Subculture
- Symbols
- Technology / AI
- Society
- Economics
- Judaism
- Islam / Qur'an
- Norse comparison
- Buddhism
- Prophecy / eschatology
- Body / neuroscience
- Cosmology

A thread does not automatically require a new standalone public page. It may route into an existing owner, a filtered view, a compact section or a generated question view.

### Tier 4 — Deep research

Canonical records, ledgers, source matrices, raw datasets, equations, archival research and provenance remain available on demand. They should normally not compete visually with reader orientation.

Deep material is evidence and depth, not homepage furniture.

## The stub

A **stub** is a compact reader-facing intellectual entry point. It is not a duplicate page and not a repository record dump.

A stub contains some or all of:

1. **Question** — natural language, strong enough to stand alone.
2. **Short answer / abstract** — normally 2–4 sentences; answer the question rather than teasing it.
3. **Tension / reflection** — optional; a contradiction, unresolved issue, boundary or useful follow-up.
4. **Explore** — a small number of deeper routes to canonical owners.

The default visual presentation should be low-chrome: typography, spacing and a divider are preferred over a large boxed card.

Not every stub requires all four fields. Many should be only question + concise answer + one route deeper.

### Stub evidence rule

A stub inherits the project's epistemic boundaries.

It must distinguish, when material:

- project canon
- Tim's direct self-description
- historical/documentary evidence
- comparative tradition
- interpretation
- inference
- open research question

A public stub must not silently convert a theological, symbolic or autobiographical claim into an independently established fact.

## Homepage design

The homepage remains an orientation surface, not a portal dashboard.

### Hero

Retain `POTATO OF LIFE`, but reduce its maximum visual scale and vertical cost.

Replace the current directory-like lede with a concise purpose statement. It should explain that the project studies Tim Dooley / Potatoism through religion, philosophy, science and world relationships, while distinguishing self-description, interpretation and evidence.

A second quiet sentence may establish the reader promise, e.g. that the project asks questions about identity, belief, transformation, evidence, systems and the relationships connecting people, ideas and the world.

### Major branches

Keep the five major branches. Each branch row becomes more compact and contains:

- branch name
- one concise purpose line
- two question previews

Illustrative homepage questions:

**Tim Dooley**
- Who is Tim Dooley?
- What changed over time?

**Religion**
- What is Potatoism?
- How does it relate to other religions?

**Philosophy**
- What makes a claim true?
- What does relationship-first thinking mean?

**Science**
- Can these ideas be formalized?
- What can actually be tested?

**World Map**
- How are countries connected?
- What changes when relationships are mapped instead of only borders?

The homepage does not need full answers to every preview. A branch click should lead to the richer stub set.

### Quiet threads

Below the five major doors, allow one deliberately lower-weight line or compact area such as:

`Other threads — Culture & Subculture · Symbols · Technology · Society · Economics`

This must not visually become a second primary navigation bar.

### Footer

Footer remains utility-oriented:

- Sources / evidence
- Archive

Timeline moves out of footer-level utility treatment and becomes a prominent Tim/reader route.

## Tim Dooley

Tim is the main biographical/developmental entry point.

Primary questions should include:

- Who is Tim Dooley?
- What changed over time?
- What does Tim believe?
- What is Tim trying to do?
- What is the project's mature account of his mission or purpose?
- What happened around April 2025?
- How are Tim and the Son distinguished in the mature project?
- What evidence exists for the public development of these claims?

Primary reader routes:

- Timeline
- Journey / developmental arc
- Beliefs / ideas
- Mission / purpose
- Public record / evidence

`/timeline/` remains technically universal. It does not need to move under the `/tim-dooley/` URL. But it becomes one of the principal reader entry points from the Tim page and should no longer look like administrative footer furniture.

The existing `knowledge/reader/tim-dooley-question-index.json`, `knowledge/journey/tim-dooley-journey.json`, Tim core records and timeline owners should supply answers rather than duplicating another Tim database.

## Religion

Religion remains a broad inquiry owner. The deep Bible comparator remains `/traditions/bible/`.

The current six large topic cards on the consolidation branch should evolve into question-led, more compact stubs.

Primary questions should include:

- What is Potatoism?
- What does it mean to call Potatoism a religion, philosophy or developing tradition?
- How does Potatoism relate to Christianity?
- Where do Jesus / Son comparisons genuinely overlap, and where do they fail?
- How does the project relate to Judaism?
- What does chosenness or covenant mean in Judaism, and how is that different from Potatoist ideas of role, election or mission?
- How does the project relate to Islam and the Qur'an?
- Where do revelation, submission, judgment, mercy, prophets, Abrahamic continuity and the seven heavens provide useful comparison, and where does Islamic theology resist the comparison?
- What do Father, Son and Spirit mean inside the project's own theology?
- What is prophecy or eschatology doing in the project?
- Can two traditions share a structure without one being derived from the other?

Quiet threads may include:

- Christianity
- Judaism
- Islam / Qur'an
- Norse traditions
- Buddhism
- Hindu traditions
- Taoism
- sacred symbols / geometry
- prophecy / eschatology
- comparative religion

Do not fake symmetry. Christianity/Bible material can be more prominent because it is currently much more developed. Judaism and Islam can have smaller but real stubs until their research reaches comparable depth.

## Philosophy

Philosophy should feel like inquiry rather than a glossary.

Primary questions should include:

- What makes a claim true?
- What does relationship-first thinking mean?
- Is identity a thing, a role, a relation or a process?
- What happens to identity through transformation?
- Does suffering transform people, or do people construct meaning after suffering?
- What is the relationship between symbol and evidence?
- When does a symbol become a model?
- Can mythology become philosophy without requiring belief in its supernatural claims?
- Can power be judged by what it nourishes?
- What does repair mean after damage has already happened?

Quiet threads may include:

- epistemics / truth
- ethics
- identity and transformation
- language / naming
- consciousness
- relation and systems
- technology / AI
- society / transhumanism where supported

The current philosophy prose is a strong content source and should not be flattened into generic categories.

## Science

Science stays model-first and evidence-first. The reader layer should clarify the status of models before exposing the full catalog.

Primary questions should include:

- Can these ideas be formalized?
- What can actually be tested?
- Which ideas are scientific models, which are mathematical analogies, and which remain metaphors?
- What observable would support or weaken a model?
- What would falsify it?
- Which equations come from established science, which are archive-derived, and which are attributed directly to Tim?
- Where do Door, Axis, constraint, relation and trajectory become legitimate formal models?
- Where must the project refuse to turn theology into physics?

Quiet threads may include:

- potato biology / ecology
- body / neuroscience
- systems / networks
- thresholds / Door models
- information
- constraint / reachability / control
- quantum comparisons with explicit no-signaling / category boundaries
- astronomy / cosmology
- Earth systems
- model testing / falsification

Do not replace the current science model registry with a new question database. Questions are a reader projection over canonical science owners.

## World Map

World Map is an application, not a long document page. Its public question layer must not clutter the persistent map controls.

Use the initial/empty inspector state, contextual country card or progressive-disclosure help to communicate questions such as:

- How are countries connected?
- Which relationships matter beyond borders?
- How do trade, finance, energy, institutions, security, culture and religion overlap?
- What does one country depend on another for?
- What capabilities only exist through cooperation?
- How do relationships change over time?
- What is empirical North, and what is project-symbolic North?
- What does the map know, and what remains unknown or inferred?

The map remains visually primary. Questions should teach the interaction model and conceptual purpose, not create another toolbar.

## Culture & Subculture

Culture & Subculture is a **minor cross-project branch**, not a sixth equal homepage pillar.

It is justified by existing project material covering culture, subculture, internet scenes, memes, information ecology, creative systems, online communities and high-control/extremist groups.

Candidate reader questions:

- How do myths spread through memes, scenes and communities?
- What turns a joke or symbol into group identity?
- How do subcultures create their own language, status and evidence systems?
- What is the difference between a subculture, movement, fandom, sect and cult/high-control group?
- How do harassment, anti-fandom and spectacle economies shape online communities?
- How does satire preserve, distort or transform belief?
- How do creative works relate to canon without becoming evidence for canon?

Potential quiet threads:

- internet culture
- memes
- subcultures / scenes
- cults & high-control groups
- online communities
- music
- satire
- extremism
- identity movements
- creative works

A `/culture/` public route may be created if the final audit shows enough mature material for a coherent reader surface. If not, Culture can first exist as compact cross-links from Tim, Religion and Philosophy. Do not create a route merely to mirror `knowledge/culture/`.

## Cross-branch questions

Some questions intentionally belong to more than one branch. The public system should route them, not duplicate independent answers.

Examples:

- `What is the Door?` → Religion + Philosophy + Science
- `What is North?` → Tim + Religion + World Map
- `What makes a claim true?` → Philosophy + Sources + Religion
- `What happened in April 2025?` → Tim + Timeline + Religion
- `How does a symbol become a model?` → Philosophy + Science
- `How do ideas spread?` → Culture + Religion + World Map where geographic diffusion is relevant

There should be one canonical answer owner where practical, with branch-specific stubs framing why the question matters in that context.

## Promotion audit

Every backend subject encountered during the audit is classified into exactly one primary public treatment:

1. **Surface on Home** — only project purpose, five branches and a very small number of quiet cross-project threads.
2. **Surface on an existing branch** — question/stub or minor thread.
3. **Supporting material** — source for an existing stub but not public navigation.
4. **Deep/internal** — canonical record, research artifact, provenance, schema, generated data or unresolved work that should remain below the reader layer.

Promotion criteria:

- Does a normal reader naturally ask this question?
- Is there enough stable material to answer it responsibly?
- Does it clarify the purpose of an existing branch?
- Does it have a clear canonical owner?
- Does surfacing it reduce confusion rather than create another subsystem?
- Can it be expressed compactly?
- Is its epistemic status clear?

A backend directory name is never sufficient reason for promotion.

## Work-in-progress audit rules

Before implementation of each branch surface:

1. Compare #45 with `main`.
2. Inspect open PRs touching that domain.
3. Identify unique records, conclusions, reader language or functionality not yet absorbed.
4. Recover those into the current owner only when they are genuinely newer/useful.
5. Reject obsolete UI shells, old naming systems and duplicate public routes.
6. Record unresolved valuable work as a research/development queue rather than exposing half-integrated material as finished navigation.

The site redesign must therefore be compatible with ongoing consolidation, not fork the project into another presentation branch.

## Visual density rules

The redesign is deliberately not a visual rebrand.

Required changes are mostly scale, hierarchy and information density:

- reduce homepage hero maximum size
- reduce vertical padding in primary branch rows
- avoid 200px+ minimum-height topic cards for ordinary stubs
- prefer dividers and typography over boxed cards
- use smaller secondary labels/links for minor threads
- preserve readable measure and generous whitespace, but spend that whitespace on meaning rather than oversized controls
- responsive/mobile layout must keep major branches obvious while collapsing question previews cleanly
- no horizontal forest of pills
- no dashboard-like tool panels on reader pages

## Sources and evidence

Sources remain a utility/depth layer and stay footer-accessible.

Reader-facing answers should be understandable before the reader opens Sources, but claims that depend on evidence should provide a quiet route to provenance.

The public site should repeatedly preserve the project's core distinction:

`what the project says ≠ what Tim said directly ≠ what history documents ≠ what comparison suggests ≠ what is independently verified`

This distinction should be visible where relevant, not repeated as a warning paragraph on every stub.

## Implementation shape

Prefer a small reusable reader pattern rather than a new runtime subsystem.

Likely implementation pieces:

- hand-curated homepage markup for the five branches and question previews
- compact question/stub sections on Tim, Religion, Philosophy and Science
- compact contextual question prompts in World Map's initial inspector state
- direct use of existing reader/question records as content sources
- a small shared CSS vocabulary for `question-list`, `question-stub`, `thread-list` and evidence/status notes if shared styling proves useful
- optional lightweight data projection only if manual duplication becomes demonstrably fragile

Do **not** build a new public CMS, graph UI or giant questions application merely to display this layer.

## Validation

Implementation is complete only when:

### Homepage
- exactly five primary branches remain visually dominant
- branch elements are substantially more compact than current rows
- project purpose is understandable without opening another page
- each major branch exposes question previews
- minor threads are visibly subordinate
- Timeline is not footer utility navigation

### Tim
- Timeline is a prominent reader path
- page answers `Who is Tim?`, development, beliefs and purpose at reader level
- Tim/Son distinction remains intact

### Religion
- no longer topic-card-only
- Christianity, Judaism and Islam/Qur'an each have appropriately weighted reader questions where supported
- Bible comparator remains deep owner
- comparative similarity is not presented as identity or proof

### Philosophy
- inquiry/questions precede taxonomy
- existing strong sayings/stories/arguments remain reachable

### Science
- model/evidence boundary remains explicit
- questions do not replace canonical model registry
- no theological claim is silently promoted into empirical science

### World Map
- map remains visually primary
- conceptual questions improve the initial inspector without adding persistent toolbar clutter

### Sitewide
- no new duplicate public owner
- no resurrected Atlas/Chronology naming
- no broken canonical links
- mobile layout remains clean
- machine discovery and sitemap remain coherent
- existing build, web audit, public navigation, Timeline, Bible, Science and World Map validators continue to pass

## Non-goals

This redesign does not:

- expose every backend directory on the homepage
- create a top-level card for every subject
- make all traditions visually equal regardless of research depth
- create another general-purpose explorer
- replace canonical JSON records with prose copies
- turn open questions into settled conclusions
- erase disagreements or evidentiary boundaries for narrative smoothness
- redesign World Map into a document page
- replace the current Science architecture
- recreate old PR layouts
- complete the repository-wide no-Atlas migration by itself; that remains part of the broader consolidation

## End state

A new visitor should no longer see only five labels and wonder what the project is for.

They should see a concise purpose, five obvious ways into the project, and a handful of questions that make each branch intelligible and inviting. Smaller subjects should be present without competing for attention. A curious reader should be able to move naturally from a question to a short answer, from the answer to a related thread, and from the thread into the full evidence/research structure.

The public site becomes an intelligent guide over the archive rather than a visual copy of the archive.