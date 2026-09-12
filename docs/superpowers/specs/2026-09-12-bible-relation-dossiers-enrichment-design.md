# Bible Relation Dossiers — Contextual Enrichment Design

**Date:** 2026-09-12  
**Status:** Approved for implementation  
**Repository:** `ThePotatoOfLife/TimDooley`  
**Branch:** `religion/bible-relation-dossiers-20260912`

## 1. Purpose

Deepen the Tim Dooley / Son / Thomas ↔ Bible comparison system so relations read like historically situated arguments rather than isolated motif matches.

The public comparator already focuses on one relation at a time. The next problem is content density. Many canonical rows are compact routing records even when specialist owners contain richer chronology, testimony, textual context, counter-texts, narrative sequence and discovery history.

A serious relation should answer: what was happening; what Tim/the Son actually said or did; what Tim was doing, discussing, reacting to or trying to explain when the relation surfaced where recoverable; what happened before and after; whether scripture was explicit at the time or discovered later; what the biblical passage does in its own context; why the relation is meaningful beyond a shared noun; where it breaks; what the maximum defensible claim is; and what the comparison changed in the developing Potatoverse.

The governing architecture remains:

> **Research discovers; canonical owners decide; projections expose.**

## 2. Scene context is evidence-bearing narrative context

The comparator should be able to reconstruct the conditions under which an idea became thinkable, not merely the final claim.

A scene can be narrow or wide:

- immediate: what Tim was doing in the minute/hour when the idea appeared;
- conversational: what question, person, AI exchange, joke, story, dog interaction, image, stream or argument triggered it;
- daily: whether the idea appeared after waking, during a long work session, while coding, on the couch, in the bath, walking, doing chores, streaming, making art or writing;
- lead-up: what themes, conflicts or metaphors had occupied the preceding days or weeks;
- aftermath: what changed in the next conversation, post, theological model or project file.

These details are not decoration. They explain how one idea emerged from another.

### 2.1 Scene provenance rule

Never invent an activity because it would make an anecdote persuasive. Store one of:

- `exact` — directly present in a dated/timestamped source;
- `recovered` — user/autobiographical memory, not independently corroborated;
- `adjacent-context` — surrounding dated material supports the setting/topic but not every detail;
- `date-only` — date known, immediate scene unknown;
- `unknown` — no defensible reconstruction.

A vivid `unknown` scene is forbidden.

## 3. Canonical Relation Dossier contract

`knowledge/traditions/biblical-syncretism-field.json` remains the canonical relation owner. Existing compact fields stay for filtering. High-value relations gain richer dossier fields.

### 3.1 Scene and project context

Support:

```json
"scene_context": {
  "summary": "...",
  "setting": "...",
  "activity": "...",
  "conversation_trigger": "...",
  "participants": ["..."],
  "surrounding_topics": ["..."],
  "lead_up": "...",
  "before": "...",
  "after": "...",
  "source_status": "exact | recovered | adjacent-context | date-only | unknown",
  "source_ids": ["..."]
}
```

Also support `what_happened`, `exact_wording`, `wording_status`, `speaker`, `audience`, `platform_or_setting`, `understood_then`, `later_reinterpretation`, `what_changed_after`, and `project_source_ids`.

### 3.2 Scripture context

Support `scripture_actor`, `scripture_speaker`, `scripture_audience`, `literary_context`, `genre`, `canonical_context`, `historical_context`, `intertext_chain`, `reception_history`, and `translation_or_textual_caveats`.

A verse fragment is not self-interpreting.

### 3.3 Relation argument

Use an argument rather than a noun match:

```json
"relation_argument": {
  "project_sequence": ["..."],
  "biblical_sequence": ["..."],
  "correspondences": ["..."],
  "why_dense": "...",
  "why_it_matters": "...",
  "maximum_claim": "..."
}
```

Prefer sequence form: `A → transition → B → consequence`.

Examples include Thomas/Twin → co-dying → Way/question → wounds → recognition; beloved Son → tenant farmers → killing/outside → rejected stone → cornerstone; rejection → prison → grain infrastructure → preservation; House → Key → opening/shutting → secure peg → seat → vessels; death → burial → seed → growth.

### 3.4 Discovery history and negative evidence

Support `discovery_history`, `mismatch`, `counter_texts`, `role_counterdistribution`, `alternative_explanations`, and `unresolved_questions`.

A mismatch defines the maximum defensible claim; it is not boilerplate embarrassment.

## 4. Density levels

### Level A — Full dossier

For most strength-4/5 identity-sensitive or major chronology relations. Requires context status, evidence/wording status, project sequence, Bible context, relation argument, mismatch/limit, discovery direction and provenance.

### Level B — Contextual relation

For narrower strength-3/4 material. Requires short context, Bible context, one clear argument and one limit.

### Level C — Lexical/provenance relation

For minor phrases/puns/occurrence tracking. May stay compact but must not be presented as equivalent to a dense narrative sequence.

## 5. First enrichment families

### Son / Jesus / Passion chronology

Promote or deepen early Christian background; 2011 Tree ordeal; 2016 accusation/custody/trial/prison; prison among offenders; claimed external Jesus/Lamb recognition; Lamb/transgressors; enemy-love vs reciprocity; 2017/2018 Jesus/crucifixion declaration with date uncertainty preserved; rejection/ridicule; 2018 persona-death; 2019/20 meme-death/burial/disappearance; Thomas/Twin; grain; rejected stone; Door; return.

### Thomas / Twin

Go beyond etymology: Didymus/Twin; John 11:16 co-dying; John 14:5 Way/question; John 20 wounds/recognition; canonical boundary; later Syriac/Thomasine twin traditions; project chronology; Door as differentiated relation rather than duplicate identity.

### Father / House / Gardener / Davidic architecture

Deepen John 15; 2 Samuel 7 / 1 Chronicles 17; Isaiah 22 / Revelation 3; Hebrews 3; 1 Corinthians 3; Psalm 127; Acts 17.

### Door / Gate / Ladder / Way / Veil

Deepen Jacob/John 1:51; Eden guarded Way; paired guardians/narrow gate; Exodus veil → Hebrews living Way; John 10 Door+Shepherd; John 14 Way/House; road-building; Micah breaker; Psalm 107 release.

### Death / Seed / Stone / Joseph / Return

Deepen John 12 Son-of-Man glory + grain; 1 Corinthians 15; tenant farmers → Son → outside → cornerstone; positive vs pathological return; burial/absence without forced three-day equivalence; Joseph descent/prison/grain/preservation.

### Dog / Mud / boundary semantics

Separate Dog→vomit/mire recurrence; Psalm 22 hostile perimeter; Revelation 22 outside-city boundary; Matthew 15/Mark 7 contested household-Dog/bread threshold; Ezekiel 34 muddy-water leadership accountability. Keep ancient polemical language behavioral/symbolic, never fixed human essence.

### Footstool

Separate cosmic footstool, sacred/cultic footstool, enemy-subjection footstool and New Testament role constraints.

### Revelation / Zion / New Jerusalem / North

Deepen Lion/Root/Lamb; throne/rainbow/circumference; 144,000 role differentiation; New Jerusalem city/bride/dwelling; positive cubic sacred geometry countertext; Zion/North comparison with North-Pole geography boundary; Isaiah 14 self-exaltation warning; new creation/repair.

### Spirit / flow / garden / repair

Deepen breath; Ezekiel 37; Eden river/stewardship; Ezekiel 47/Revelation 22 river-tree-healing; olive-oil-lamp flow; explicit boundary against literal CSF=Spirit claims.

### Ethical countertexts

Promote enemy-love vs reciprocity; king-under-law; service/non-grasping before exaltation; shepherd accountability; reflexive judgment; verticality reversal; positive/negative return; positive cord/anchor; sacred cube; Son/Christ integration counterroles.

## 6. Candidate promotion process

Every candidate is classified as `promote-new`, `merge-into-existing`, `enrich-existing`, `keep-specialist`, `countertext-only`, `reject-duplicate`, `reject-low-density`, or `unresolved-provenance`.

Prioritize earlier chronology, exact/recovered wording, scene/circumstance, multi-step narrative correspondence, role distribution/counterdistribution, distinct semantic function, strong countertext, intertextual chain, and specialist relations absent from the public field.

Do not prioritize another generic Tree/Father/Door/Lion/God match when the function is already represented.

## 7. Finding more material

Search project-first. Start from dated Tim/Son material and identify unusual actions, sequences and transitions before looking for biblical neighbors. Search the Bible by function, not keyword alone: guarded access, rejected heir, opening/shutting authority, suffering outside gate, return to former state, seed death/multiplication, source→flow→fruit→healing, role reversal, house/inhabitation, judge measured by own measure, shepherd stewardship, obstacle removal, sacred center, breach/release, hiddenness/recognition/wounds/witness.

Search reception history only where it materially changes the comparison, and keep reception distinct from canonical text.

Search prior conversations specifically for exact timestamps, activities, setting, question/AI exchange that triggered a realization, metaphors already in motion, who introduced the biblical reference, and what changed afterward.

## 8. Narrative style contract

Preferred public order:

1. scene/circumstance;
2. project anchor/wording;
3. biblical scene in context;
4. argument;
5. density/multi-feature sequence;
6. limit/mismatch;
7. what the relation changed in the project.

Avoid database prose such as “Thomas means Twin; John calls Thomas Didymus; strong parallel.” Prefer historically situated reasoning: Thomas is already Twin when he volunteers to die with Jesus, later asks about the Way, and finally confronts the wounds of the returned Jesus; the project’s Thomas relation develops after a Son-story already organized around death, disappearance, return, witness and Door. The comparison is therefore a sequence—Twin → co-dying → Way → wounds → recognition—not merely an etymology.

Never claim Tim knew or fulfilled a passage at the time unless the source supports that.

## 9. Question quality

Keep a few orientation questions but favor archive-specific questions such as: Why does the Son become a Door after rejection? What did Tim say before anyone found the verse? Why does Thomas matter beyond “Twin”? Why can Lion and Lamb belong to one figure? Is return resurrection, repentance, homecoming or recurrence? Why can footstool be sacred in one passage and conquered enemies in another? What happens when the Bible gives the Son a function the Potatoverse usually gives the Father? Which parallels survive their strongest countertext? What existed in 2011–2019 before mature Potatoverse theology?

## 10. Scripture fragments

Expand `biblical-passage-fragments.json` for promoted dossiers, especially John 11:16; John 14:5-6; John 20:24-29; Mark 12/Matthew 21; Hebrews 13; Isaiah 22; Hebrews 3; 1 Corinthians 3; Acts 17; Proverbs 26/2 Peter 2; Psalm 22; Revelation 22:15; Matthew 15/Mark 7; Psalm 110; Isaiah 66; Philippians 2; Ezekiel 34; Isaiah 35/40/57/62; Micah 2; Psalm 107; 1 Corinthians 8; Colossians 1; Ezekiel 37; Ezekiel 47/Revelation 22.

## 11. Validation

Upgrade `scripts/check_biblical_syncretism_field.py` so designated Level-A dossiers require context status, evidence/wording status, mechanisms, relation argument, a meaningful mismatch/limit for identity-sensitive strength-4/5 comparisons, discovery/source direction and owners.

If scene status is `date-only` or `unknown`, reject unsupported rich activity/participants/setting. Strength-5 cannot be justified by one shared word plus one verse.

## 12. Public comparator projection

Preserve the focused single-relation browser and stable viewport. The front face should show scene summary, anchor/wording, scripture, substantial argument, and visible mismatch/maximum-claim note. Progressive disclosures should expose Circumstances & sequence, Bible in context, Discovery history, Intertext/reception, Counter-texts & alternatives, Sources & provenance, and Related comparisons.

## 13. Success criteria

A reader should understand a major relation without opening three specialist files; relations should feel anchored in dates/scenes/development; evidence classes remain visible; early Son chronology is restored; overloaded symbols are split by function; countertexts constrain claims; public questions arise from actual archive tensions; and the prose gains personality from real circumstances without inventing documentary scenes.

The desired experience is not “here are many Bible verses that resemble Tim Dooley.” It is: **here is what happened, what was being lived/discussed, what was understood then, what the biblical text does in its own world, when the relation was noticed, why it is dense, where it breaks, what it changed, and the strongest claim the evidence can carry.**
