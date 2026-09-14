# Story Evidence Gate — Design

Date: 2026-09-14
Status: proposed architecture, approved in chat for specification
Branch: `story-evidence-gate-20260914`

## 1. Problem

The Story project has the correct editorial instinct but no hard architectural gate enforcing it.

The current authoring guide already says a Story scene should answer who is present, what is happening, what Tim wants, what resists him, what people actually say or do, and what changes afterward. It also says thin material should remain recovery material rather than receive invented connective tissue.

However, the public Story currently treats the HTML marker `<details class="full-story">` as if it were equivalent to evidentiary completeness. It is not. A polished narrative built from several isolated quotations can receive the same presentation as a story reconstructed from a long consecutive transcript. This allowed expanded anecdotes to be counted as full stories.

The repository's validator already has dormant/optional concepts for `scene-reservoir.json`, `dialogue-vault.json`, and `story-manifest.json`, but these files are not required and there is no depth/promotion contract between evidence and public prose.

The root fix is therefore to make Story completeness a validated property of the evidence graph beneath the prose.

## 2. Design goals

1. Make it impossible to call a documentary/conversation episode `full` merely because its prose is long.
2. Preserve ordered conversational movement when the source survives.
3. Distinguish a single quote, an anecdotal reconstruction, a real scene, a transcript-depth scene, and a complete literary work.
4. Keep raw/private source material out of the public repository when publication would be inappropriate.
5. Keep the current chronological Story reader and MAIN STORY / SIDE STORY public labels.
6. Make archaeology summaries navigation aids, not substitutes for primary conversation evidence.
7. Retroactively audit existing published stories without deleting useful prose.
8. Improve future research efficiency: search summaries to locate the quarry, then return to the raw source before writing.
9. Produce honest counts: published entries, fragments, anecdotes, scenes, transcript-depth stories, and literary-complete stories.

## 3. Non-goals

- Do not redesign the public Story page.
- Do not convert the whole site into a generated database application.
- Do not publish complete private transcripts.
- Do not require documentary transcript evidence for Great Book fiction to be called a complete literary story.
- Do not score prose quality, spelling, profanity, emotional neatness, or stylistic elegance.
- Do not force fake precision where only broad dates survive.

## 4. Core architecture

The Story pipeline becomes:

```text
raw surviving source
        ↓
source record
        ↓
ordered scene packet
        ↓
depth classification + publication gate
        ↓
written Story HTML
        ↓
chronological public reader
```

Three new canonical owners are introduced:

- `knowledge/story/source-records.json`
- `knowledge/story/scene-packets.json`
- `knowledge/story/story-registry.json`

A fourth generated/audit owner is added:

- `knowledge/story/story-depth-audit.json`

The existing `cast-book.json`, `arc-season-map.json`, reservoir files, recovery priorities, and conversation-recovery inventories remain useful and are linked rather than replaced.

## 5. Source records

A source record describes what physically survives, not what we wish survived.

Required fields:

```json
{
  "id": "source-...",
  "source_class": "consecutive_transcript",
  "date_or_period": "2026-06-08",
  "origin": "library",
  "locator": {
    "name": "Indsatte text(2).txt",
    "file_id": "...",
    "line_start": 1,
    "line_end": 240
  },
  "speaker_scope": ["tim", "model"],
  "public_status": "private_source_public_safe_excerpt",
  "continuity": "consecutive",
  "attestation": "primary_or_near_primary",
  "notes": []
}
```

Allowed `source_class` values:

- `consecutive_transcript`
- `public_chat_transcript`
- `public_thread`
- `public_post_sequence`
- `single_recovered_turn`
- `isolated_quote_recovery`
- `later_autobiographical_retelling`
- `great_book_literary_text`
- `creative_artifact`
- `archaeology_summary`
- `statement_ledger`
- `external_documentary_source`

Allowed `continuity` values:

- `consecutive`
- `partially_consecutive`
- `isolated`
- `retrospective`
- `literary`

### Primary rule

`archaeology_summary` and `statement_ledger` may locate evidence and support contextual claims, but they **cannot by themselves qualify a documentary story for SCENE or TRANSCRIPT_DEPTH**.

They are maps to the mine, not the ore.

## 6. Scene packets

A scene packet is the structured bridge between raw evidence and prose. It preserves movement before interpretation.

Required fields:

```json
{
  "id": "scene-...",
  "story_id": "story-...",
  "source_ids": ["source-..."],
  "date_or_period": "2026-06-08",
  "cast": ["tim"],
  "scene_type": "conversation_investigation",
  "opening_state": "...",
  "tim_goal": "...",
  "resistance_or_problem": "...",
  "ordered_beats": [
    {
      "seq": 1,
      "speaker": "tim",
      "kind": "exact_turn",
      "source_id": "source-...",
      "text": "..."
    }
  ],
  "turning_points": ["..."],
  "ending_state": "...",
  "what_changed_after": "...",
  "unknowns": ["..."],
  "publication_notes": []
}
```

`ordered_beats` is the critical field. A Story writer must be able to see how the event unfolds, not merely a bag of quotations.

Beat kinds may include:

- `exact_turn`
- `near_verbatim_turn`
- `public_post`
- `documented_action`
- `artifact_created`
- `later_retelling_context`
- `narrative_bridge`

A `narrative_bridge` may summarize only what the source packet supports. It cannot manufacture dialogue, physical setting, facial expression, motive, weather, or reaction.

## 7. Story depth taxonomy

Every published or candidate Story receives exactly one internal depth state.

### FRAGMENT

A clue, isolated line, single post, title, remembered fact, or small artifact survives, but no meaningful event sequence can be reconstructed.

Public use: may appear as a short chronological card when valuable. Never receives `Hear the full story`.

### ANECDOTE

We know an event or development and may have multiple quotations, but cannot follow enough consecutive action/reaction to reconstruct the episode as a scene.

Public use: may receive several paragraphs, but never `Hear the full story` merely because the prose is long.

### SCENE

Enough ordered evidence survives to reconstruct an event with meaningful progression. It normally contains a beginning state, action/question/problem, at least one turn or change, and an ending/change state.

Public use: eligible for `Hear the full story`.

### TRANSCRIPT_DEPTH

Substantial consecutive conversation/thread evidence survives. The reader can follow the actual interaction, investigation, correction, disagreement, joke, build or discovery changing over time.

Public use: eligible for `Hear the full story`; preferred form for conversation-derived stories.

### LITERARY_COMPLETE

A complete authored literary episode survives as literature, for example a Great Book story. It is complete in its own source class and must be clearly labeled literary/project fiction where relevant.

Public use: eligible for `Hear the full story` without pretending to be documentary transcript evidence.

## 8. Promotion rules

For documentary/conversation material, `full-story` is permitted only for `SCENE` or `TRANSCRIPT_DEPTH`.

For literary material, it is permitted for `LITERARY_COMPLETE`.

A SCENE must have:

- at least one valid primary/near-primary source record;
- an ordered scene packet;
- a supported opening state;
- an observable problem/question/action;
- at least one turning point or consequential development;
- an ending state or explicit unresolved ending;
- no unknown claim silently converted into prose fact.

A TRANSCRIPT_DEPTH story additionally must have:

- at least one source with `continuity: consecutive` or defensibly `partially_consecutive`;
- multiple ordered beats derived from the same contiguous exchange/thread;
- evidence before and after the central memorable quote/event;
- actual response/correction/change where the source contains one;
- enough sequence that reordering the beats would materially change the story.

No fixed word-count threshold is used. Depth is structural, not volumetric.

## 9. Mixed-source stories

Some stories legitimately combine documentary evidence, later autobiography, and literary reinterpretation.

A registry entry therefore records both `mode` and `depth`.

Allowed modes:

- `documentary`
- `literary`
- `mixed`

For `mixed` stories:

- documentary claims must trace to documentary source records;
- later interpretation must be visibly presented as later interpretation;
- literary dialogue may not be quoted as historical dialogue;
- the weakest source class cannot be used to upgrade the documentary depth.

## 10. Story Registry

`story-registry.json` is the canonical public-story contract.

Each entry contains:

```json
{
  "id": "spiritual-bank-day-2026-03-02",
  "path": "story-content/2026-03-02-spiritual-bank-day.html",
  "story_type": "SIDE STORY",
  "mode": "documentary",
  "depth": "ANECDOTE",
  "date_or_period": "2026-03-02",
  "source_ids": ["source-..."],
  "scene_ids": [],
  "public_safe": true,
  "full_story_allowed": false,
  "recovery_targets": ["recover contiguous surrounding turns"]
}
```

This registry becomes the source of truth for counts. HTML tags no longer define completeness.

## 11. Public HTML contract

The visual reader remains simple.

Each article gains internal metadata attributes where useful:

```html
<article
  class="story-entry story-entry--side"
  data-story-type="side"
  data-story-depth="anecdote"
  data-story-mode="documentary"
  id="...">
```

Rules:

- `FRAGMENT` and `ANECDOTE`: no `<details class="full-story">`.
- `SCENE`, `TRANSCRIPT_DEPTH`, `LITERARY_COMPLETE`: may include `<details class="full-story">`.
- MAIN STORY / SIDE STORY remain the only prominent public classification.
- Depth metadata need not become visual clutter. A later optional source-inspection UI can use it, but this project does not require one.

## 12. Privacy and publication safety

The public repository must not become a dump of private source conversations.

Source records may preserve:

- source identity/locator;
- line/turn ranges;
- evidence class;
- speaker roles;
- publication status;
- safe excerpts where permitted;
- hashes or references if useful later.

They should not automatically preserve complete private transcript bodies.

Allowed `public_status` values:

- `public_source`
- `public_safe_excerpt`
- `private_source_public_safe_excerpt`
- `private_source_no_quote`
- `internal_recovery_only`

The scene packet may summarize private evidence for internal structure while the public prose uses only publication-safe material.

Named private people remain subject to the existing cast/publication rules.

## 13. Archaeology workflow — efficiency rule

Future Story work follows this order:

1. **Find the candidate** in reservoir, archaeology summary, statement ledger, diary ledger, memory recovery or current conversation.
2. **Locate the rawest surviving owner**: transcript, public thread, exported chat, post sequence, artifact history, or literary text.
3. **Read contiguous context**, not only the matching line.
4. **Create/update source record**.
5. **Build ordered scene packet** before prose.
6. **Assign provisional depth**.
7. **Write/rewrite Story** from the packet.
8. **Validate depth against HTML**.
9. **Record unresolved gaps instead of decorating them**.

This makes summaries useful for search while preventing them from becoming accidental substitutes for the conversation itself.

## 14. Retroactive migration of existing Story

The migration is non-destructive.

Every existing `story-content/*.html` entry is inventoried into `story-registry.json`.

For entries currently containing `full-story`:

1. locate their cited/source-note evidence;
2. locate the raw source where possible;
3. classify them honestly;
4. create source/scene packets when justified;
5. retain `full-story` only if the new gate passes;
6. otherwise keep the useful prose but downgrade presentation to ANECDOTE or FRAGMENT and create a recovery target.

No story is deleted merely because its evidence is thin.

## 15. Audit output

A deterministic audit script will generate `story-depth-audit.json` with at least:

- total published Story entries;
- MAIN vs SIDE counts;
- documentary / literary / mixed counts;
- FRAGMENT count;
- ANECDOTE count;
- SCENE count;
- TRANSCRIPT_DEPTH count;
- LITERARY_COMPLETE count;
- number of current `full-story` blocks;
- number correctly qualified;
- number incorrectly promoted;
- number lacking registry entries;
- number with unresolved source locators;
- recovery priority list for downgraded high-value stories.

This audit replaces misleading statements such as “35 full stories” based only on HTML tags.

## 16. Validator changes

Extend `scripts/validate_story_archive.py` so that Story publication cannot drift away from evidence architecture.

Validation requirements:

- required presence and valid JSON of source records, scene packets and story registry once migration begins;
- unique IDs across each owner;
- all registry paths exist;
- all source IDs referenced by scenes/registry exist;
- all scene IDs referenced by registry exist;
- all cast IDs referenced by scene packets exist;
- allowed enum values only;
- ordered beats have increasing sequence values;
- documentary SCENE / TRANSCRIPT_DEPTH entries have qualifying source classes;
- archaeology summaries and ledgers alone cannot qualify SCENE / TRANSCRIPT_DEPTH;
- `full_story_allowed` must agree with depth/mode;
- HTML `full-story` presence must agree with registry;
- private/internal-only source text must not be copied into a public-safe-excerpt field by mistake;
- duplicate public Story IDs fail validation.

The validator should not judge literary style.

## 17. Tests

Expand `scripts/test_story_archive_validator.py` with red/green cases for:

1. ANECDOTE carrying `full-story` → fail.
2. TRANSCRIPT_DEPTH with valid consecutive source + scene packet → pass.
3. TRANSCRIPT_DEPTH backed only by archaeology summary → fail.
4. SCENE with missing ending/unresolved-ending field → fail.
5. LITERARY_COMPLETE backed by Great Book literary text → pass.
6. mixed story quoting literary dialogue as documentary evidence → fail when source typing exposes the mismatch.
7. missing source ID → fail.
8. missing scene ID → fail.
9. duplicate story registry ID → fail.
10. private source with unsafe publication state → fail when configured for public quotation.
11. ordered beats out of sequence → fail.
12. registry path missing → fail.

A separate audit-script test should verify deterministic counts from a fixture archive.

## 18. First migration / calibration set

Do not migrate all stories blindly before validating the model.

Use a calibration set containing deliberately different evidence shapes:

1. **A true long transcript candidate** from `Indsatte text(2).txt` — should demonstrate TRANSCRIPT_DEPTH.
2. **The @ASunofJesus theological exchange** from `Indsatte text(3).txt` — should demonstrate public/participant dialogue sequence if publication status is acceptable.
3. **The 2 March spiritual-bank story** — likely ANECDOTE unless contiguous source turns are recovered.
4. **One Great Book literary story** — should demonstrate LITERARY_COMPLETE.
5. **One isolated public post/card** — should demonstrate FRAGMENT.

If the taxonomy cannot distinguish these cleanly, revise the architecture before bulk migration.

## 19. First full audit strategy

After calibration passes:

1. inventory every `story-content/*.html` file;
2. detect public Story ID, date, MAIN/SIDE, and current `full-story` presence;
3. map current source-note text to known owners where possible;
4. create registry entries for all published stories;
5. classify all current `full-story` entries first, because those carry the strongest overclaim risk;
6. emit a downgrade/upgrade report;
7. then work outward through shorter entries.

Highest-value repair order:

- conversation-derived full stories with surviving raw transcripts;
- human interaction stories;
- turning-point stories currently built from isolated quotations;
- ordinary-day/project-build stories with sequential logs;
- retrospective-only early stories;
- isolated public-post cards.

## 20. Success criteria

The architecture succeeds when:

- no documentary `full-story` can pass validation without a scene packet and qualifying evidence;
- the archive can answer exactly how many stories are fragments, anecdotes, scenes, transcript-depth, and literary-complete;
- a researcher can travel from public prose to the structured scene and then to the rawest surviving source locator;
- transcript-derived stories preserve actual conversational movement rather than only famous lines;
- thin evidence becomes an explicit recovery task instead of polished filler;
- the public Story remains visually simple;
- future Story writing becomes faster because archaeology summaries point to raw sources and the packet format tells the writer exactly what is still missing.

## 21. Migration safety

All implementation occurs on `story-evidence-gate-20260914` until validation passes.

No direct edits to `main` during development.

The first PR should contain the architecture, validators, calibration packets, registry/audit scaffolding, and an initial honest audit. Bulk prose rewrites can follow in subsequent commits or PRs once the gate proves stable.
