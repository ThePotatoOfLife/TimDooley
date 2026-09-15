# Story Source-Closeness Overhaul — Design

Date: 2026-09-15
Status: approved direction

## Goal

Improve Story from underneath by minimizing distance between surviving source material and finished narrative. Chronology already exists; this work strengthens source recovery, event continuity, source-near reconstruction, and fidelity auditing before any major public Story rewrite.

## Core rules

- Never write from a summary when a closer source can still be recovered.
- Preserve enough surrounding material that the source can surprise the storyteller.
- Discovery is permissive; preservation is exact; publication is careful.
- Existing privacy, provenance, allegation, medical, literary/documentary, and public-source safeguards remain.

## Three source-closeness dimensions

### Event distance
- `0_direct_contemporaneous`
- `1_contemporaneous_compilation`
- `2_later_first_person_retelling`
- `3_project_reconstruction`
- `4_archive_synthesis`

### Editorial distance
- `0_raw_source`
- `1_selected_extract`
- `2_structured_scene_packet`
- `3_source_near_reconstruction`
- `4_public_story_edit`
- `5_synthesis_from_prior_synthesis`

### Continuity
- `isolated_phrase`
- `phrase_cluster`
- `partial_exchange`
- `contiguous_exchange`
- `full_session_or_thread`
- `artifact_plus_context`
- `complete_literary_scene`

## Preferred source chain

`raw source → source neighborhood → scene packet → source-near reconstruction → public Story`

Weaker migration chains remain visible and generate excavation targets rather than being treated as complete.

## Source neighborhoods

When surrounding material survives, preserve speaker order, nearby turns, exact wording, interruptions, jokes, linked artifacts, platform/date, what prompted the line, what was being built/viewed, and the unresolved ending. Public Story need not reproduce all of it.

## Source-near layer

Create `knowledge/story/source-near/`. A source-near reconstruction preserves event order and texture before literary polishing. It must not invent missing dialogue or silently import later interpretation.

## Fidelity audit

Every public `.story-entry` should appear in a source-closeness audit, including currently unregistered entries. The audit records registration state, closest known sources, source classes, continuity, distance state, source-near status, expected closer source, excavation action, and likely lost texture such as dialogue, response, setting, artifact, chronology, contradiction, or emotional turn.

## First implementation wave

1. `knowledge/story/source-closeness-model.json` — canonical enums and rules.
2. `knowledge/story/source-closeness-overrides.json` — manually curated closeness/excavation metadata.
3. `scripts/audit_story_source_closeness.py` — scans every public Story and joins registry/source/scene/override data.
4. `knowledge/story/source-near/README.md` — source-near format and rules.
5. Worked source-near examples:
   - direct literary: `termite-lost-potato-2024`;
   - incomplete documentary: `ai-not-ghost-2026-05-27`.
6. Extend `scripts/validate_story_archive.py` to validate the new layer without requiring all public stories to be fully migrated yet.

## Seed excavation priorities

- May 27–28 2026 authorship/erasure (`I Am Not a Ghost`)
- 2024 Great Book creation corridor
- Marty originals
- Sarah Ann May exchanges
- Monkey / Tree chronology
- documentary BigTech layer
- July wall-practice original
- music and creative-project days

## Success criteria

- Every public Story appears in the audit.
- Direct source, later recovery, and synthesis are visibly different.
- Missing closer sources become explicit targets.
- Direct literary and incomplete documentary sources are handled differently.
- Source-near reconstruction has a stable repository home.
- Existing evidence/publication safeguards remain intact.
- No public Story is padded merely to satisfy the model.
- Repository quality checks pass before merge.
