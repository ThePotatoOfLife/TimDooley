# Reader Residency Wave 001 — Design

Date: 2026-09-15
Status: approved implementation direction

## Goal

Make the stabilized Potato House feel inhabited by promoting already-owned, provenance-aware Tim material into the readers where it is most useful, without adding homepage complexity, moving canonical ownership, or duplicating active Story-restoration work.

## Architectural rule

`canonical/source owner → residency map → reader-specific projection`

Reader pages may summarize, sequence, cross-link and contextualize material. They do not become the sole owner of claims, quotes, chronology, creative artifacts, science, theology or world-system records.

## Scope

Wave 001 touches these reader surfaces:

- `tim-dooley/`
- `corporium/` (Collection)
- `works/`
- `timeline/`
- `religion/`
- `science/`
- `world/`

`philosophy/` is intentionally left structurally unchanged because the Spiral Reader is already deeply inhabited. It may receive only future cross-links if needed.

`tim-dooley/story/` and `story-content/` are intentionally not modified in this wave because active Story PR #148 already owns Story restoration. The residency map may identify Story as a future target and link readers into Story, but this branch must not create a competing Story restoration.

## Core residency objects

Create `knowledge/guides/reader-residency-map.json` as a projection-control record, not a canonical fact owner.

Every residency record must contain:

- `id`
- `title`
- `summary`
- `source_class`
- `canonical_owners` — one or more existing repository paths
- `target_surfaces`
- `public_copy_rule`
- `epistemic_boundary`
- optional `date_or_period`
- optional `timeline_query`
- optional `related_routes`

Wave 001 residency IDs:

1. `tim-making-things`
2. `ordinary-absurd-tim`
3. `builder-gardener-service`
4. `information-architecture-feb-2026`
5. `spiritual-bank-mar-2026`
6. `ontology-reversal-mar-apr-2026`
7. `not-a-ghost-repair-may-2026`
8. `north-vocabulary-evolution`
9. `door-root-mud-sprout`
10. `creative-objects-navigation`

## Source discipline

Residency entries must point to existing owners such as:

- `knowledge/indexes/tim-statement-corpus-index.json`
- `knowledge/corporium/tim-voice-anthology.json`
- `knowledge/corporium/tim-statements-conversation-recovery-wave-006-2026-09-15.json`
- `knowledge/corporium/tim-statements-conversation-recovery-wave-007-2026-09-15.json`
- `knowledge/story/TIM-STORY-COMPLETENESS-AUDIT.md`
- `knowledge/culture/creative-systems-archive.json`
- `knowledge/core/tim-role-synthesis.json`
- `data/north-of-north-tim-canon.json`
- timeline owners and source registries already used by the project

A residency record can use `PUBLIC_PRIMARY`, `PUBLIC_INDEXED`, `USER_PROJECT_EXACT`, `CONVERSATION_EXACT`, `MEMORY_SUMMARY_PHRASE`, `BOOK_OR_PROJECT_MAXIM`, `PARAPHRASE`, or `MIXED` as a display-facing source class, but public copy must respect the stricter underlying record. Memory-summary material must never become a verified quotation.

## Reader enrichments

### Tim

Add a compact **Tim in motion** section after the primary routes and before the existing work section. It should expose four facets:

- Making: books, music, games, AI, maps, archive/site work.
- Voice: cosmic ↔ mundane ↔ comic ↔ practical register switching.
- Builder/Gardener: identity becoming service and infrastructure.
- Repair: Not-a-Ghost / authorship / staying to fix and build.

Each facet carries `data-residency-id` and links onward to Collection, Works, Story, Timeline or source/evidence surfaces.

### Collection

Add a **Voice trails** section before the anatomy/Ladder material so Collection no longer reads primarily as a body page.

Required trails:

- God / Potato / mundane-life inversion.
- Father / Axis / North vocabulary migration.
- Build road → fix together → build garden → service.
- Door / Root / Mud / Sprout compact grammar.
- Erasure / Ghost / alive / repair.

Use source-class badges. Direct quotes are allowed only where existing public/primary or explicitly exact project wording supports them; otherwise summarize without quotation marks.

### Works

Keep the five existing genres. Add:

- navigable links from artifact cards to their strongest existing archive/Story/Explore owners where available;
- a compact **Making timeline** showing 2024 Great Book / 2025 music+AI+streaming / 2026 games, maps, archive and site-building as creative practice;
- `data-residency-id="creative-objects-navigation"` and `data-residency-id="tim-making-things"` markers.

No new creative canon file is created.

### Timeline

Do not build another timeline system. Add a short **Follow a development** corridor above the existing explorer with links that use current Timeline URL-state/search capabilities.

Required corridor links:

- information architecture — Feb 2026
- spiritual bank — Mar 2026
- Son/Father ontology reversal — Mar–Apr 2026
- Not a Ghost / repair — May 2026
- North vocabulary evolution — 2025–2026
- Builder → Gardener → service — Apr–Sep 2026

Links may use `tl_q`, `tl_from`, `tl_to`, presets/layers only if already supported by `app/timeline.js`. Do not invent new URL parameters.

### Religion

Add a compact **Theology changed over time** section that explicitly shows:

- Mar 8 2026 no-Son / only-Potato phase;
- Apr 9 differentiated Son/Vessel returns;
- Apr 14 Father/Son/person distinction becomes explicit;
- later mature Father/Ladder + Son/Door formulation.

This is project-development history, not doctrinal harmonization. Link into Timeline and Bible comparison.

### Science

Add **How a Tim question becomes a model** as a small process trail:

`raw observation / metaphor → relation question → variables / operators → comparator → falsifiable claim or explicit non-scientific boundary → paper/model/audit`

Use the Feb 18–19 information-architecture session as one historical example, but do not imply that symbolic Light/Mud/Axis claims are scientific findings.

Link to Science archive, body/neurobiology, Questions and relevant model-testing/audit owners.

### World

Add **From symbolic North to relational systems** beneath the four World routes. Show the distinction and development:

- North as symbolic orientation/title language;
- North as countries/relationships/capability mapping;
- North Programme / European system-building;
- World Map / Politics / Systems as empirical views that must keep symbolic claims separate.

This section must not present project-sacred geography as geopolitical fact.

## Validation

Create `scripts/validate_reader_residency.py` and run it in repository quality checks.

Validator requirements:

1. Parse `knowledge/guides/reader-residency-map.json`.
2. Require exactly the ten Wave 001 IDs above.
3. Require every `canonical_owners` path to exist.
4. Require target surfaces to be one of `tim`, `collection`, `works`, `timeline`, `religion`, `science`, `world`, `story`.
5. Require each non-Story target surface to contain at least one `data-residency-id` matching a map record targeted to that surface.
6. Require the seven Wave-001-modified reader files to contain their required residency IDs.
7. Require Story targets, if present, to be projection-only and not require Story-file modification.
8. Require no `MEMORY_SUMMARY_PHRASE` entry to define `public_copy_rule` allowing verified quotation.
9. Require Timeline residency links to use only URL parameters currently supported by `app/timeline.js`: `tl_q`, `tl_epistemic`, `tl_exact`, `tl_detail`, `tl_from`, `tl_to`, `tl_sort`, `tl_layers`, `tl_actors`, `tl_event` if present in runtime support.
10. Require all reader pages to remain projections: residency map `knowledge_owner` must be false.

Add this validator to `.github/workflows/quality-checks.yml` adjacent to other reader/House projection validations.

## Non-goals

- No homepage changes.
- No sixth primary gateway.
- No new Story fragments or Story chronology in this branch.
- No new canonical theology, science, world-system, or creative owner.
- No rewrite of Philosophy Spiral Reader.
- No attempt to expose every recovered quote publicly.
- No promotion of memory-summary wording as exact quotation.
- No replacement of Explore.
- No new JavaScript application.

## Success criteria

The House should feel more inhabited because major reader surfaces answer not only “what category is this?” but “what actually happened, changed, got built, got said, and where do I go next?” while every promoted thread remains traceable to an existing owner and the homepage stays simple.
