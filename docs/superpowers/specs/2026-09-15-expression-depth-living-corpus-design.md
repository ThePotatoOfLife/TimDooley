# Expression Depth / Living Corpus — Architectural Design

**Date:** 2026-09-15  
**Status:** design direction approved in chat; written spec awaiting review  
**Repository:** `ThePotatoOfLife/TimDooley`  
**Base:** current `main` at `bdf987dce9132113c9fcdbd3a7f55060c9209220`

## 1. Purpose

The repository already contains much more Tim Dooley material than the public reader surfaces can currently express: public statements, Great Book wording, conversation recovery, thought archives, sayings, aphorisms, expression patterns, stories, timeline attestations, theology, philosophy, creative work, public witness and later ethical formulations.

The problem is therefore not primarily lack of content. It is **promotion, routing and expression depth**.

The goal of this design is to make the public project feel more inhabited by Tim Dooley without turning it into a quote dump, a larger navigation system, an argument/counterargument machine, or another duplicate content database.

The governing distinction is:

- **information depth** asks what the archive knows;
- **expression depth** asks whether the reader can encounter the source language, actions, objects, motives, changes, humor, tensions, ordinary life and developmental texture that made the archive know it.

The governing editorial question is adapted from the Story authoring guide:

> Does this help the reader spend time with Tim Dooley, or does it merely help the archive explain Tim Dooley?

This principle is strongest on Tim, Philosophy, Religion and Story. It is intentionally weaker on Science, Evidence and empirical World surfaces, where distance and auditability are part of the design.

---

## 2. Architectural fit

This design extends existing architecture rather than replacing it.

### Existing owners remain authoritative

- `data/frontend-atlas-bridge.json` remains the canonical backend-to-frontend routing contract.
- `data/backend-coverage-map.json` remains the backend ownership / public projection map.
- canonical philosophy, theology, timeline, evidence and world records remain the owners of their claims.
- `knowledge/indexes/tim-statement-corpus-index.json` remains the top-level statement ingestion/navigation owner.
- `knowledge/corporium/tim-voice-anthology.json`, `tim-sayings-and-formulations-ledger.json`, `tim-dooley-greatest-quotes-and-reflections.json` and `tim-dooley-expression-grammar.json` remain the principal voice/formulation owners.
- `knowledge/story/AUTHORING-GUIDE.md` plus the Story evidence-gate registry/source packets remain the authority for whether evidence is rich enough to become narrative scene prose.

### New layer: editorial projection intelligence

Expression Depth adds one new **index/control layer**, not a new truth owner:

`knowledge/indexes/expression-depth-routing.json`

Its job is to map public surfaces to:

- their expected Tim-presence intensity;
- the canonical source families that can feed them;
- the forms appropriate to that surface;
- the forms to avoid;
- provenance requirements;
- known enrichment gaps;
- intentionally cool / low-persona surfaces.

It never becomes the owner of quotations, theology, philosophy, chronology or story facts.

`data/frontend-atlas-bridge.json` will point to this contract through one `expression_contract` field. It must not absorb the editorial details itself.

---

## 3. Core rules

### 3.1 Recover before synthesizing

Before adding new explanatory prose to a Tim-facing page, search the existing source owners for material that already carries the idea in a more distinctive form.

Preferred sequence:

`source expression -> provenance -> context -> canonical owner -> public placement -> concise interpretation`

Do not reverse the sequence into:

`generic interpretation -> invented Tim-like wording`

### 3.2 Source language is not decoration

A quotation or recovered formulation should appear publicly only when its wording contributes something paraphrase would lose, such as:

- compression;
- humor;
- rhythm;
- emotional force;
- strangeness;
- historical significance;
- conceptual adjacency;
- title stacking;
- identity-to-function movement;
- ordinary material detail;
- a visible change in Tim's language over time.

### 3.3 Negative space is allowed

Do not surround every strong Tim line with a point, counterpoint, caveat, interpretation, FAQ and bibliography paragraph.

Use a quiet provenance label and enough context to prevent misattribution. Put larger epistemic boundaries at the page/section level when possible. Let high-compression material stand when further explanation would weaken it.

### 3.4 Expression does not erase epistemics

The repository's source classes remain mandatory. At minimum, public placements distinguish:

- documented/public Tim wording;
- recovered/conversation wording;
- Great Book or project-attributed wording;
- creative/literary material;
- archive interpretation.

A later synthesis never becomes retroactive Tim speech.

### 3.5 Emotion is recovered through evidence, not invented psychology

The archive may express emotional reality through documented/recoverable evidence such as:

- what Tim said he wanted;
- what he repeatedly refused;
- what he returned to;
- observable changes in tone/register;
- actions after an event;
- jokes and profanity;
- public grief or celebration when directly expressed;
- shifts from warning/conflict toward building/service;
- changes in relationships and creative output.

Do not invent private mental states merely to make prose richer.

### 3.6 Concrete nouns and verbs beat archive fog

Where the source permits it, prefer the actual objects and actions that recur in Tim's language and work: potato, couch, camera, stream, road, Door, garden, mud, book, map, screen, tree, line, room, root; build, plant, fix, stream, write, map, argue, return, grow, protect.

Abstract archive terms remain useful, but they should not replace the lived material they summarize.

### 3.7 One natural home, contextual secondary appearances

A source expression can inform multiple owners without being copied everywhere.

One surface receives the strongest public treatment. Secondary appearances are shorter and justified only when they help that page explain its own subject.

### 3.8 No style quota for the whole site

Expression Depth must preserve deliberate tonal asymmetry. A source-heavy Tim page and a cool Evidence page are both correct.

No global rule requires every page to contain Tim quotations, emotion, stories or humor.

---

## 4. Surface placement contract

### Home — low Tim presence

**Job:** threshold and routing.

Allow only high-compression orientation or questions that help a visitor choose a door. Do not turn Home into a quotation wall or miniature biography.

### Tim Dooley — very high Tim presence

**Job:** let the reader meet Tim as developing public subject, builder, witness, riddle, source-persona and later Gardener.

Appropriate forms:

- source-labelled direct/recovered wording;
- work and action;
- developmental transitions;
- public witness;
- cosmic/mundane register switching;
- identity becoming function;
- purpose and service;
- selected ordinary detail.

The current Tim page already contains the placement-first riddle/work/Gardener wave. Future work should deepen selectively rather than continually expand the page.

### Religion — medium-high Tim presence

**Job:** define Potatoism/theology before comparison and show how the religious system was actually spoken and developed.

Appropriate forms:

- a small number of source anchors for Father / Son / Spirit;
- House / Root / Axis / Door / Ladder / Garden language;
- one compact developmental strand showing vocabulary migration;
- later service/cultivation language;
- quiet links to Bible comparison and source owners.

Avoid turning Religion into a quotation anthology. The Bible laboratory remains the home for detailed comparison.

### Philosophy — very high Tim presence

**Job:** be the strongest public place for encountering how Tim thinks.

Appropriate forms:

- sayings;
- questions;
- small stories and parables;
- absurdity;
- contradictions;
- observations;
- practical tests;
- frame changes;
- relationship-first thinking;
- authorship/reader questions;
- power -> responsibility;
- sparse delayed interpretation (`Chew on it`).

The current page has begun this transition. Future work should mine the much larger philosophy inquiry/sourcebook before writing additional generic explanation.

### Science — conditional / low persona

**Job:** formalize, test, compare or reject.

Tim voice appears only when the originating question or exact formulation materially explains why a model exists. Scientific status, assumptions and failure conditions remain primary.

### World — method-first, not persona-first

**Job:** public gateway to geography, systems, politics, North and map investigation.

Tim is expressed mainly through method: relationships before isolated entities, capability/dependency questions, trajectory and repair discipline.

Do not add personality merely because Tim is the project owner.

### North — medium Tim presence at the symbolic edge

**Job:** bridge symbolic/sacred North to empirical North Programme work.

Early sections may use carefully sourced North/Axis/Seat wording to explain the symbolic genealogy. Empirical geography and policy sections then become cooler and evidence-led.

### Timeline — attestation/development presence

**Job:** show first appearances, change, recognition dates and later reinterpretation.

Source expression is important here as historical evidence. The Timeline should preserve event-time versus interpretation-time rather than use quotations simply for atmosphere.

### Story — very high lived texture, evidence-gated

**Job:** scene, sequence, people, action/reaction and ordinary life.

Expression Depth supplies recovery candidates; it does not bypass Story's evidence gate. A strong isolated quote remains a fragment/anecdote until ordered evidence supports scene depth.

### Evidence / Source Authority — intentionally cool

**Job:** provenance and audit.

No pressure to make these pages feel more personal. Their restraint is part of the information architecture.

### Explore / machine surfaces — complete access, not editorial theatre

**Job:** retrieval and source navigation.

Do not impose reader-style expression requirements on raw archive discovery.

---

## 5. Source families

The first routing contract should recognize, at minimum:

### Primary / public evidence

- `data/evidence/rational-potato-x-occurrence-ledger-2024-2026.json`
- `data/evidence/rational-potato-twitter-compilation-2025-2026-summary.json`
- `data/tim-dooley-public-theology-timeline-2025-2026.json`
- `data/timeline-event-packs/x-public-attestations-2024-2026.json`

### Thought / statement / voice

- `data/tim-dooley-thought-archive.json`
- `knowledge/indexes/tim-statement-corpus-index.json`
- `knowledge/corporium/tim-voice-anthology.json`
- `knowledge/corporium/tim-sayings-and-formulations-ledger.json`
- `knowledge/corporium/tim-dooley-greatest-quotes-and-reflections.json`
- `knowledge/corporium/tim-dooley-expression-grammar.json`
- conversation and memory recovery waves referenced by the statement corpus index.

### Philosophy / Potatoism

- `knowledge/philosophy/potato-philosophy.json`
- `knowledge/philosophy/tim-dooley-philosophical-inquiry.json`
- `knowledge/philosophy/tim-dooley-potatoism-sourcebook.md`
- `knowledge/philosophy/timic-relational-statements-and-operators.json`
- `knowledge/philosophy/potatoism-reader-philosophy.md`

### Story / chronology

- `knowledge/story/AUTHORING-GUIDE.md`
- Story evidence-gate registries/source packets/scene packets already owned by the Story system.
- `knowledge/timeline/dated-master-timeline-2026.json`
- `knowledge/timeline/developmental-genealogy.json`
- expression-development timeline packs.

### Creative / ordinary life

Creative archives, music records, Great Book chapters and public-diary/story fragments may supply texture when their provenance and publication status permit it.

---

## 6. Expression Depth routing contract

Create `knowledge/indexes/expression-depth-routing.json` as a human-authored editorial control file.

Each public surface record should contain:

- `surface_id`
- `route`
- `presence_intensity`
- `primary_job`
- `canonical_source_families`
- `allowed_forms`
- `avoid_forms`
- `provenance_requirements`
- `current_strengths`
- `known_gaps`
- `candidate_topics`
- `story_handoff_policy` when relevant

Allowed `presence_intensity` values are exactly:

- `very-high`
- `medium-high`
- `medium`
- `low`
- `method-only`
- `cool`

`provenance_requirements` is an array of policy keys chosen from:

- `label-public-wording`
- `label-recovered-wording`
- `label-book-project-wording`
- `label-creative-literary`
- `label-archive-interpretation`
- `attribute-serious-allegations`
- `story-evidence-gate-required`

The contract validator checks only these defined values.

This file does **not** contain copied quotations. It points to owners and describes placement policy.

The contract should also classify surfaces that are intentionally low-persona so the audit cannot mistake restraint for incompleteness.

---

## 7. Repository-wide audit

Create `scripts/audit_expression_depth.py`.

The audit is advisory. It should produce `expression-depth-report.json` during CI and local runs.

### What the audit may measure safely

- public surfaces defined in the routing contract exist;
- canonical source paths defined for those surfaces exist;
- existing public source/provenance labels;
- number and classes of source anchors already used on each surface;
- direct links from public surfaces to appropriate deeper routes;
- candidate source records available to each surface;
- candidate expressions not visibly surfaced yet;
- unresolved provenance candidates that should **not** be promoted yet;
- source families with rich material but no meaningful public projection;
- expressions appearing on too many public surfaces;
- public pages that appear to duplicate canonical owner text excessively.

### What the audit must not pretend to measure automatically

- whether prose is emotionally powerful;
- whether a page is beautiful;
- whether Tim sounds authentic based on generic language statistics;
- whether a quote is philosophically important solely because it is repeated;
- private emotional state;
- whether a Story fragment has scene depth without the Story evidence gate.

The report can propose candidates. Editorial review decides promotion.

### Candidate extraction

The audit may recursively inspect structured corpus records for common expression fields such as:

- `quote`
- `wording`
- `wording_or_paraphrase`
- `text`
- `text_or_formulation`
- `remembered_wording`

and common metadata such as:

- `source_class`
- `provenance_class`
- `themes`
- `domains`
- `routing`
- `date`
- `status`
- `confidence`

Schema differences must not be normalized into false equivalence. The report preserves original source path and source class.

---

## 8. Validation and CI

Create `scripts/validate_expression_depth_contract.py` as a hard structural validator.

It should fail only on objective contract errors such as:

- missing referenced public surface;
- missing source owner path;
- duplicate `surface_id`;
- invalid `presence_intensity`;
- unknown provenance policy key;
- a routing entry claiming canonical ownership of source content;
- Story placement that omits `story-evidence-gate-required`;
- a `cool` surface that also declares mandatory source-expression forms.

The advisory audit itself should not fail CI because a page has unused candidates.

Update `.github/workflows/quality-checks.yml` to:

1. run the expression contract validator as a normal quality check;
2. run the expression audit;
3. upload `expression-depth-report.json` as a short-retention artifact even when no enrichment change is required.

This parallels the existing content-depth philosophy: structure can fail; editorial opportunity remains advisory.

---

## 9. First implementation wave

The first implementation wave should be deliberately bounded enough to prove the system.

### 9.1 Foundation

- add `knowledge/indexes/expression-depth-routing.json`;
- add the structural validator;
- add the advisory audit;
- wire both into quality checks;
- add `expression_contract: "knowledge/indexes/expression-depth-routing.json"` to `data/frontend-atlas-bridge.json`;
- add `expression-depth-routing` to the `connections` array of `knowledge/indexes/tim-statement-corpus-index.json`; do not duplicate corpus records there.

### 9.2 Calibrate on Religion

Religion is the best first calibration page because its current structure is accurate but more explanatory than source-inhabited.

Enrich `religion/index.html` with a **small** number of source anchors selected from existing canonical owners. The intended result is not more volume; it is more specificity.

Targets:

- one source-facing Father / Root / House / Axis formulation;
- one Son / Door relation where source status supports it;
- one later religious-life / service formulation;
- optionally one tiny vocabulary-development bridge if it makes the theology easier to feel historically.

Keep the Bible Lab, comparative boundaries and existing theological-center structure intact.

### 9.3 Audit Tim + Philosophy, do not bulk-expand them

The existing placement-first wave already improved these pages substantially. The first Expression Depth implementation should use them as calibration controls:

- verify the audit recognizes their existing strengths;
- report unused high-value candidates;
- make only small corrections if a clearly superior source expression is currently buried;
- do not turn either page into an anthology.

### 9.4 Story handoff only

Do not bulk-edit Story prose in this wave.

The audit may emit Story recovery candidates and source paths. Actual Story promotion must go through the existing evidence-gate workflow and active Story restoration work.

This avoids conflict with current Story branches/PRs and preserves scene discipline.

---

## 10. Later enrichment waves

After the audit is stable, enrichment proceeds surface-by-surface.

Recommended order:

1. Religion — theological source anchors.
2. Philosophy — mine underused Great Book / conversation philosophy only where it improves rhythm or missing concepts.
3. North — strengthen symbolic genealogy before empirical programme handoff.
4. Tim — ordinary-life and work texture if the audit finds a real gap.
5. Timeline — first-attestation / expression-mode views.
6. Science — originating questions only where provenance is strong and scientifically useful.
7. World — method language only; avoid personality creep.
8. Story — recovered scenes through the Story evidence gate.

Each wave should deepen existing owners/surfaces rather than create new master pages.

---

## 11. Relationship to content-depth, SEO and hygiene

Expression Depth complements existing project maintenance rather than replacing it.

### Content depth

`audit_content_depth.py` asks whether canonical records are structurally substantive. Expression Depth asks whether important source material is appropriately projected into reader experience.

A record can be deep while its public page is expression-thin. A public page can be vivid while its canonical owner is structurally weak. Both audits are needed.

### SEO

Expression enrichment should naturally improve semantic specificity, internal-link relevance and long-tail answer quality, but SEO remains its own pipeline.

Do not distort Tim's voice to satisfy keyword density. Search titles/descriptions can be optimized independently from visible source wording.

### Hygiene

Expression work must follow repository hygiene rules:

- one canonical owner;
- no duplicate master files;
- no stale public route;
- no raw private material published merely for texture;
- no unsupported allegations converted into narrator fact;
- no new UI system when existing pages can carry the content directly.

---

## 12. Privacy, allegations and sensitive material

Expression richness is not permission to publish everything recoverable.

Do not promote:

- private family identities;
- unnecessary medical detail;
- addresses or credentials;
- private participant details without a public-project basis;
- unsupported serious allegations as facts;
- raw private transcripts merely because they make a scene vivid.

For allegations involving crimes, intelligence services, trafficking, cults or comparable serious conduct, public narration remains clearly attributed to Tim/project sources unless independently established.

---

## 13. Success criteria

The architecture is successful when:

1. every major public reader surface has an explicit expression-placement policy without changing its canonical owner;
2. the routing contract uses only the defined presence-intensity and provenance-policy enums;
3. CI validates the contract structurally and emits an advisory expression-depth report;
4. the report can identify rich source material that has not yet reached its natural public home;
5. unresolved/recovered material remains visibly distinct from documented public wording;
6. Religion becomes more source-inhabited without becoming a quote anthology or losing comparative discipline;
7. Tim and Philosophy remain rich but do not become quote dumps;
8. Story candidates are routed into the Story evidence gate rather than narrated prematurely;
9. Science, Evidence and empirical World surfaces retain appropriate distance;
10. no new generic site-wide widget, navigation layer or duplicate canonical database is introduced;
11. full repository quality checks remain green;
12. the reader gets more Tim through specificity, voice, action, objects, development and source texture—not through generic praise or inflated explanation.

---

## 14. Governing principle

The project should become denser by becoming **more particular**, not merely longer.

When a source expression already exists, prefer recovering and placing it over writing a generic explanation of it. When the source is too weak, keep the gap visible and recover more. When the page already carries enough Tim, stop.

The intended end state is not maximum quotation density. It is a public archive in which the reader can feel the difference between:

- what Tim said;
- what Tim later said it meant;
- what the archive infers;
- what older traditions say;
- what science can test;
- what a story can actually reconstruct;
- and what remains unresolved.

That distinction is what allows more of Tim Dooley to become visible without making the project less reliable.