# Bible Continuous Listen + Duplicate Cleanup + Targeted Mining

Date: 2026-09-17
Status: proposed design for review
Repository: `ThePotatoOfLife/TimDooley`

## Goal

Improve the existing Bible comparator without redesigning it: let a reader press Listen once and hear the current result sequence from beginning to end, clean true duplicates and near-duplicates without collapsing the large example corpus, and add only genuinely distinct Bible parallels discovered by a targeted mining pass.

## Scope guardrails

1. This is **not** a full comparator overhaul.
2. Keep the existing atlas, focus/order controls, filters, Previous/Next, Results list, evidence-first reading surface, TTS drawer, scripture reader and scene reader.
3. Preserve a large example corpus. Deduplication is cleanup, not compression.
4. A relation stays separate when it has a materially different project event/date, Bible passage/scene, operator/function, role assignment, source direction, evidence class, or countertext.
5. Merge only when two records are substantially the same claim with substantially the same evidence and function.
6. Use `Ego Death` as the reader-facing label for the 2011 event where that is the intended concept. Preserve exact historical/source wording in provenance fields when needed.
7. Continue adding genuinely new examples after duplicate cleanup so the public comparator remains broad.
8. Do not present a structural Bible parallel as proof of literal identity, prophecy, or historical dependence.

## A. Continuous Listen mode

### Existing foundation

`app/bible-tts-adapter.js` already:
- mounts the one canonical Bible TTS drawer;
- builds Project / Scripture / Why / Both scopes;
- receives `complete`, `stop`, and `error` events from the shared TTS drawer;
- watches the active relation and refreshes its payload when the comparator moves.

The comparator already exposes Previous/Next relation behavior through `app/bible-study.js`.

### Required behavior

Add a Bible-specific **Continue through results** toggle to the existing TTS drawer integration.

When enabled:
1. User presses Listen/Play once.
2. TTS reads the selected scope for the active relation.
3. On natural `complete`, the Bible adapter asks the comparator to select the next visible relation.
4. The comparator renders the next relation.
5. The adapter waits until the active relation ID changes and the new payload is available.
6. It starts the same TTS scope again automatically.
7. This repeats until the final visible result.
8. At the final result, playback stops cleanly and announces/end-labels the sequence as complete.

### Stop conditions

Auto-advance must turn off when:
- user presses Stop;
- TTS raises an error;
- user disables Continue;
- user manually changes route/focus/filter/search/order while the system is between relations;
- the next relation does not materialize within a bounded DOM/update cycle;
- there is no next visible relation.

Pause does **not** turn Continue off. Resuming continues the same relation, then advances after completion.

Manual Previous/Next while Continue is enabled is allowed; playback follows the newly selected relation rather than fighting the user.

### Interface contract

Expose one minimal comparator navigation hook from `app/bible-study.js`:

```js
window.BibleStudyReader = {
  activeId: () => string,
  hasNext: () => boolean,
  selectNext: () => boolean,
  onSequenceChange: (listener) => unsubscribe
};
```

The TTS adapter consumes this hook. The shared `tts-reader.js` and generic `tts-drawer.js` do not gain Bible-specific navigation logic.

### Persistence

Persist Continue mode in the existing `potato-tts-settings` object as:

```json
{"bibleContinue": true}
```

Default is `false` for existing users.

## B. Duplicate and near-duplicate cleanup

### Why this belongs in tooling

The current quality report evaluates evidence/context completeness but does not actually compute duplicate or near-duplicate candidates. Add deterministic duplicate analysis before any manual merge decisions.

### Duplicate classes

#### 1. Exact duplicate

Two active relations are exact-duplicate candidates when normalized values strongly match across:
- project anchor / exact wording;
- Bible refs or primary scene;
- project event/date;
- operator/function;
- central comparison claim.

Action: merge metadata/evidence into the stronger canonical owner, then redirect the weaker relation ID.

#### 2. Near duplicate — merge candidate

Very similar central claim and same underlying project/Bible situation, but one record contains richer wording, better countertext, stronger scene linkage or provenance.

Action: manual review. Merge only when the weaker record does not add a distinct example/function.

#### 3. Same motif, distinct example

Examples:
- two different Tim dates using Door imagery;
- John 10 Door versus John 14 Way/House;
- multiple resurrection-recognition scenes with different mechanics;
- same Bible passage paired to different project events.

Action: **retain both**. Add `related_relation_ids` or family/scene links if useful.

### Similarity features

Add duplicate scoring based on normalized sets, not opaque semantic AI:
- same project date/event ID;
- same primary biblical scene;
- Jaccard overlap of Bible refs;
- Jaccard overlap of motifs/operators/roles;
- normalized title/project-anchor token overlap;
- same source direction/discovery mode;
- same central sequence/mechanism.

The report emits:

```json
{
  "duplicate_candidates": [
    {
      "left_id": "...",
      "right_id": "...",
      "score": 0.93,
      "class": "exact|near|same-motif-distinct",
      "reasons": ["same project event", "same primary scene", "same operator"]
    }
  ]
}
```

No relation is deleted automatically by the scorer.

### Redirect contract

Create a small canonical redirect owner:

`knowledge/traditions/bible-relation-redirects.json`

Shape:

```json
{
  "redirects": {
    "old-relation-id": "canonical-relation-id"
  }
}
```

Runtime URL handling resolves legacy `?id=` values through this map so old links remain useful.

### Corpus preservation rule

The merge pass must not reduce distinct examples merely to make the corpus smaller. A successful pass may remove exact repetition while simultaneously adding new distinct relations. Public breadth is a feature.

## C. Targeted Bible-parallel mining

Before adding another broad wave, test a small set of missing high-value scenes that current repository search did not surface.

### Candidate 1 — Emmaus: returned but unrecognized until bread is broken

Bible target: Luke 24:13-35.

Distinct function:
- return already happened;
- companions interact with the returned figure before recognition;
- recognition occurs in connection with breaking bread;
- recognition and presence are temporally separated.

Project comparison target:
- staged return / recognition rather than one timestamp;
- bread/food symbolism where supported by project evidence.

Boundary:
Do not convert delayed recognition into proof of project identity.

### Candidate 2 — Mary mistakes the risen Jesus for the gardener

Bible target: John 20:11-18, especially the garden/gardener misrecognition.

Distinct function:
- resurrection setting;
- misrecognition precedes naming/recognition;
- explicit gardener image appears in a return scene.

Project comparison target:
- Gardener motif + return/recognition architecture.

Boundary:
Mary is mistaken; John does not identify Jesus literally as the gardener. The comparison is garden/gardener imagery plus delayed recognition, not a textual claim that Jesus holds the gardener title there.

### Candidate 3 — Forty-day post-resurrection interval

Bible target: Acts 1:1-11, especially Acts 1:3.

Distinct function:
- resurrection is not the final temporal stage;
- appearances/teaching continue before ascension;
- supports a staged model: death → resurrection → recognition/teaching → ascent/mission.

Project comparison target:
- distinguish death date, becoming, public identity, recognition and later return/ascent markers without forcing a three-day numerical equivalence.

### Candidate 4 — Shore recognition and feeding

Bible target: John 21:1-14.

Distinct function:
- returned Jesus initially unrecognized;
- recognition develops in action;
- meal/bread/fish and feeding context follows return.

Retain separately from Emmaus only if the project-side comparison adds a distinct feeding/shepherd function rather than repeating delayed recognition.

### Candidate 5 — Paul’s three-day blindness/transformation

Bible target: Acts 9:1-19.

Distinct function:
- three-day liminal interval;
- blindness/fasting;
- restored sight;
- identity/mission transition.

Promote only if a concrete project-side three-day darkness/waiting transformation has strong provenance. Otherwise keep as research-only.

### Candidate 6 — Hosea third-day revival

Bible target: Hosea 6:1-3.

Distinct function:
- two-day/third-day revival language predating the Gospel resurrection narrative.

Promote only if it adds historical/intertextual context to an existing three-day dossier. It should probably enrich an existing relation rather than create a standalone duplicate.

## D. Return-sequence reconciliation

Do **not** create a giant replacement relation. Instead enrich existing death/return/Thomas records with an ordered comparison note:

Bible side:

`death → burial → resurrection → appearances → delayed recognition → continued teaching → ascension/mission`

Project side, only using already documented project chronology:

`earlier Ego Death/prefiguration → later death threshold → becoming/germination → Potato of Life identity → interpretation/development → later return/recognition/ascent markers`

The purpose is to explain why multiple existing relations are related without merging distinct events into one card.

## E. Reader-facing terminology cleanup

Replace reader-facing uses of `Tree Ordeal` with `Ego Death` when the label refers to the 2011 transformation event.

Do not rewrite:
- exact quotations;
- cited source titles;
- provenance fields that preserve historical wording;
- comparisons where the literal tree is the actual subject rather than merely the event label.

## F. Tests and validation

Add/extend validation for:
- Continue toggle exists only on the Bible TTS surface;
- natural TTS completion advances exactly one result when enabled;
- final result does not wrap unexpectedly;
- Stop/error disables continuation;
- Pause preserves continuation intent;
- manual navigation while continuing is respected;
- same scope is retained across relation changes;
- legacy relation redirects resolve;
- duplicate report is deterministic;
- exact duplicate fixture is flagged;
- same-motif/distinct-event fixture is retained;
- current manifest-defined relations remain loadable after redirects;
- no-loss rule: every removed active relation ID resolves to a retained canonical ID;
- new candidate relations require source direction, Bible refs/scene, project evidence, mismatch/boundary and maximum supported claim.

## G. Files expected to change

Likely implementation files:
- `app/bible-tts-adapter.js`
- `app/bible-study.js`
- `app/tts-drawer.css` only if the Continue control needs a tiny shared visual rule; prefer Bible-specific CSS first
- `app/bible-study.css`
- `scripts/test_bible_tts_adapter.mjs`
- `scripts/validate_bible_reader.py`
- `scripts/build_bible_comparator_quality.py`
- a focused duplicate-analysis helper/test under `scripts/`
- `knowledge/traditions/bible-relation-redirects.json`
- one focused additive relation/enrichment file for accepted new parallels
- `knowledge/traditions/bible-layer-manifest.json`
- scene/fragments files only for accepted new passages

## H. Success criteria

1. A user can press Listen once and hear the current comparator result sequence continuously to the end.
2. Continuous reading uses the existing result order/filter context.
3. Existing manual reading still works exactly as before.
4. True duplicate relations can be safely consolidated without breaking old links.
5. Near-duplicate cleanup preserves distinct examples rather than flattening them.
6. The public comparator remains large and varied.
7. At least the highest-confidence genuinely missing Bible scenes are evaluated, with only distinct, evidence-backed relations promoted.
8. Reader-facing terminology uses `Ego Death` for the 2011 event label where appropriate.
