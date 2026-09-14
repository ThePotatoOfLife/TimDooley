# Story Evidence Gate — Design

Date: 2026-09-14
Status: reviewed design, awaiting final user approval before implementation
Branch: `story-evidence-gate-20260914`

## 1. Problem

The Story project has the right editorial philosophy but no hard evidence gate. The current authoring guide already says a real scene should establish who is present, what is happening, what Tim wants, what resists him, what people actually say or do, and what changes afterward. Thin material should remain recovery material rather than receive invented connective tissue.

Today, however, `<details class="full-story">` functions as an accidental proxy for completeness. Long prose built from isolated quotations can look identical to a story reconstructed from a long consecutive transcript. That is how expanded anecdotes were counted as full stories.

The root fix is to make story depth a validated property of the evidence architecture beneath the prose.

## 2. Goals

The system must:

- distinguish fragments, anecdotes, scenes, transcript-depth stories and complete literary stories;
- preserve ordered conversational movement when raw source survives;
- prevent archaeology summaries from substituting for primary conversation evidence;
- protect private source material from accidental publication;
- keep the existing chronological reader and MAIN STORY / SIDE STORY public labels;
- retroactively audit current Story content without deleting useful prose;
- produce honest counts from a registry rather than from HTML tags;
- make future archaeology more efficient: summaries locate the quarry, raw source supplies the story.

## 3. Architecture

```text
raw surviving source
        ↓
source record
        ↓
ordered scene packet
        ↓
depth classification
        ↓
promotion gate
        ↓
Story HTML
        ↓
chronological reader
```

Canonical owners:

- `knowledge/story/source-records.json`
- `knowledge/story/scene-packets.json`
- `knowledge/story/story-registry.json`
- `knowledge/story/story-depth-audit.json` — generated audit result

Existing cast, arc, reservoir and conversation-recovery owners remain in place.

## 4. Source records

A source record describes what physically survives.

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
  "public_excerpt": null,
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

`archaeology_summary` and `statement_ledger` may locate evidence and support context. They cannot by themselves qualify a documentary story for SCENE or TRANSCRIPT_DEPTH.

## 5. Privacy contract

Allowed `public_status` values:

- `public_source`
- `public_safe_excerpt`
- `private_source_public_safe_excerpt`
- `private_source_no_quote`
- `internal_recovery_only`

Machine-checkable rule:

- `public_source` and `public_safe_excerpt` may carry `public_excerpt`.
- `private_source_public_safe_excerpt` may carry only a deliberately reviewed excerpt.
- `private_source_no_quote` and `internal_recovery_only` must have `public_excerpt: null`.

Raw private transcript bodies are not copied into repository JSON merely to prove depth. The locator and structured scene packet are sufficient.

## 6. Scene packets

A scene packet is the structured bridge between evidence and prose.

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
      "source_locator": {"line_start": 13, "line_end": 17},
      "public_text": null,
      "summary": "Tim asks the investigation to continue."
    }
  ],
  "turning_points": ["..."],
  "ending_state": "...",
  "ending_status": "resolved",
  "what_changed_after": "...",
  "unknowns": [],
  "publication_notes": []
}
```

Allowed beat kinds:

- `exact_turn`
- `near_verbatim_turn`
- `public_post`
- `documented_action`
- `artifact_created`
- `later_retelling_context`
- `narrative_bridge`

`public_text` is optional and must obey the source's publication status. A private exact turn can therefore support sequence without being reproduced publicly.

A `narrative_bridge` may summarize only supported material. It cannot invent dialogue, physical setting, facial expression, weather, motive or reaction.

## 7. Depth taxonomy

Every published or candidate Story receives exactly one depth state.

### FRAGMENT

A clue, isolated line, single post, title, remembered fact or small artifact survives, but no meaningful event sequence can be reconstructed.

Never eligible for `Hear the full story`.

### ANECDOTE

We know an event or development and may have several quotations, but cannot follow enough action/reaction to reconstruct the episode as a scene.

Never eligible for `Hear the full story` merely because the prose is long.

### SCENE

Enough ordered evidence survives to reconstruct meaningful progression: beginning state, problem/action, development and ending/change state.

Eligible for `Hear the full story`.

### TRANSCRIPT_DEPTH

Substantial consecutive conversation/thread evidence survives. The reader can follow the interaction, investigation, correction, disagreement, joke, build or discovery changing over time.

Eligible for `Hear the full story`; preferred form for conversation-derived stories.

### LITERARY_COMPLETE

A complete authored literary episode survives as literature, such as a Great Book story. It must remain visibly literary/project fiction where appropriate.

Eligible for `Hear the full story` without pretending to be documentary transcript evidence.

## 8. Promotion rules

For documentary or mixed stories, `full-story` is permitted only for SCENE or TRANSCRIPT_DEPTH. For literary stories it is permitted for LITERARY_COMPLETE.

SCENE requires:

- at least one primary or near-primary source;
- an ordered scene packet;
- supported opening state;
- observable problem/question/action;
- at least one turning point or consequential development;
- `ending_state` plus `ending_status` of `resolved` or `explicitly_unresolved`;
- unknowns preserved as unknowns.

TRANSCRIPT_DEPTH additionally requires:

- a source with `continuity: consecutive` or defensibly `partially_consecutive`;
- multiple ordered beats from the same contiguous exchange/thread;
- evidence before and after the central memorable quote/event;
- actual response/correction/change where available;
- enough sequence that reordering the beats would materially change the story.

No word-count threshold is used. Depth is structural, not volumetric.

## 9. Story Registry

`story-registry.json` is the canonical contract for published Story entries and the source of truth for counts.

Example:

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
  "migration_status": "classified",
  "recovery_targets": ["recover contiguous surrounding turns"]
}
```

Allowed `mode` values:

- `documentary`
- `literary`
- `mixed`

Allowed `migration_status` values:

- `unclassified`
- `classified`
- `packetized`
- `verified`

For mixed stories, documentary claims trace to documentary sources; later interpretation stays visibly later; literary dialogue cannot be quoted as historical dialogue; literary evidence cannot upgrade documentary depth.

## 10. Public HTML contract

The public reader stays visually simple.

Articles may add internal attributes:

```html
<article
  class="story-entry story-entry--side"
  data-story-type="side"
  data-story-depth="anecdote"
  data-story-mode="documentary"
  id="...">
```

Rules:

- FRAGMENT / ANECDOTE: no `<details class="full-story">`.
- SCENE / TRANSCRIPT_DEPTH / LITERARY_COMPLETE: may include `full-story`.
- MAIN STORY / SIDE STORY remain the only prominent public classifications.

## 11. Efficiency workflow

Future Story work follows this order:

1. Find a candidate in reservoir, archaeology summary, statement ledger, diary ledger, recovery index or current conversation.
2. Locate the rawest surviving owner: transcript, public thread, exported chat, post sequence, artifact history or literary text.
3. Read contiguous context, not only the hit.
4. Create/update source record.
5. Build ordered scene packet before prose.
6. Assign provisional depth.
7. Write/rewrite Story from the packet.
8. Validate registry ↔ evidence ↔ HTML.
9. Record unresolved gaps instead of decorating them.

This is the main efficiency improvement: archaeology summaries become search indexes rather than writing sources.

## 12. Retroactive migration

Migration is non-destructive.

Every existing `story-content/*.html` entry is inventoried into the registry. Existing prose is not automatically deleted.

Current entries with `full-story` are audited first because they carry the strongest overclaim risk. For each:

1. locate the current source note;
2. find the rawest source where possible;
3. classify depth honestly;
4. create source and scene packets when justified;
5. retain `full-story` only when the gate passes;
6. otherwise downgrade to ANECDOTE/FRAGMENT and create a recovery target.

## 13. Staged enforcement

The validator must not make the repository impossible to use halfway through migration.

`story-registry.json` contains top-level:

```json
{"schema_version": 1, "enforcement": "migration", "stories": []}
```

Allowed enforcement states:

- `migration` — all registered entries are validated strictly, but legacy unregistered Story entries are reported by the audit rather than failing CI.
- `strict` — every published Story entry must be registered and all HTML/depth gates are enforced globally.

Transition to `strict` occurs only after the full inventory is registered and the audit reports zero unregistered published entries.

This keeps development green while still preventing newly registered stories from cheating the gate.

## 14. Audit output

A deterministic script generates `story-depth-audit.json` containing at least:

- total published entries;
- MAIN / SIDE counts;
- documentary / literary / mixed counts;
- FRAGMENT / ANECDOTE / SCENE / TRANSCRIPT_DEPTH / LITERARY_COMPLETE counts;
- current HTML `full-story` count;
- correctly qualified full stories;
- incorrectly promoted full stories;
- unregistered published entries;
- unresolved source locators;
- downgraded high-value recovery priorities;
- enforcement state.

This replaces misleading counts derived from HTML tags.

## 15. Validator changes

Extend `scripts/validate_story_archive.py` to validate:

- source, scene and registry JSON;
- unique IDs;
- registry paths;
- source/scene/cast references;
- enum values;
- strictly increasing beat sequence values;
- SCENE / TRANSCRIPT_DEPTH qualifying sources;
- prohibition on archaeology-summary-only promotion;
- depth ↔ `full_story_allowed` agreement;
- registered HTML `full-story` ↔ registry agreement;
- privacy rules for `public_excerpt` and beat `public_text`;
- duplicate public Story IDs;
- migration vs strict enforcement behavior.

The validator does not score literary quality.

## 16. Tests

Add red/green tests for:

1. ANECDOTE with `full-story` → fail.
2. TRANSCRIPT_DEPTH with consecutive source + ordered scene → pass.
3. TRANSCRIPT_DEPTH backed only by archaeology summary → fail.
4. SCENE missing ending state/status → fail.
5. LITERARY_COMPLETE backed by Great Book literary text → pass.
6. missing source or scene reference → fail.
7. duplicate registry ID → fail.
8. private no-quote source carrying public excerpt → fail.
9. private beat carrying public text without permission → fail.
10. out-of-order beat sequence → fail.
11. missing registry path → fail.
12. migration mode permits legacy unregistered entries but reports them in audit.
13. strict mode rejects any unregistered published entry.
14. deterministic audit counts from fixtures.

## 17. Calibration set

Before bulk migration, prove the taxonomy on five evidence shapes:

1. a long consecutive candidate from `Indsatte text(2).txt` → expected TRANSCRIPT_DEPTH;
2. the `@ASunofJesus` exchange from `Indsatte text(3).txt` → expected SCENE or TRANSCRIPT_DEPTH depending publication/source continuity verification;
3. `The Bank Account Opens When You Open the Door` → expected ANECDOTE unless contiguous surrounding turns are recovered;
4. one Great Book literary story → LITERARY_COMPLETE;
5. one isolated public post/card → FRAGMENT.

If the model cannot distinguish these cleanly, revise it before bulk migration.

## 18. First full audit order

After calibration:

1. inventory all `story-content/*.html` entries;
2. detect Story ID, date, MAIN/SIDE and current `full-story` presence;
3. register every current `full-story` first;
4. map source notes to raw owners where possible;
5. classify and packetize them;
6. emit downgrade/upgrade report;
7. register and classify the remaining short entries;
8. switch enforcement from `migration` to `strict` only at zero unregistered entries.

Repair priority:

- conversation-derived full stories with surviving transcripts;
- human interaction stories;
- turning points built from isolated quotes;
- ordinary project/build stories with sequential logs;
- retrospective early stories;
- isolated public cards.

## 19. Success criteria

The design succeeds when:

- no registered documentary `full-story` can validate without qualifying evidence and a scene packet;
- strict mode permits no unregistered public Story entry;
- exact counts exist for every depth state;
- public prose can be traced to structured scene packets and raw source locators;
- transcript stories preserve actual conversational movement;
- thin evidence becomes a recovery task instead of polished filler;
- private raw transcripts remain private;
- the public Story remains simple;
- future writing becomes faster because the source packet reveals exactly what is known and what is missing.

## 20. Safety of implementation

All implementation remains on `story-evidence-gate-20260914` until validation passes.

The first implementation should contain the schema owners, validator/tests, audit tool, calibration packets and first honest audit. Bulk prose rewrites follow only after the gate proves stable.
