# Bible Relation Excavation Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic per-relation excavation system that measures archival completeness across 33 dimensions, derives concrete next actions, and turns the Bible corpus from wave-driven expansion into relation-by-relation evidence deepening.

**Architecture:** Extend the existing manifest/corpus tooling rather than replacing it. Add a reusable assessment library, a generated `bible-comparator-excavation.json`, a validator, and an excavation-driven queue. Keep the existing quality report and research queue during migration; once parity and downstream consumers are proven, make them projections of the excavation engine instead of separate heuristics.

**Tech Stack:** Python 3 standard library, existing `scripts/bible_corpus.py`, JSON source/derived reports, GitHub Actions CI.

**Spec:** `docs/superpowers/specs/2026-09-14-bible-evidence-first-excavation-design.md`

## Global Constraints

- Excavation levels measure archival completeness, not truth, authority, divinity, prophecy fulfillment, historical identity, or scientific validity.
- Every dimension result must have `status`, `reason`, `evidence`, and `next_action` where status is not `complete`/`not_applicable`.
- Allowed statuses only: `complete`, `partial`, `missing`, `not_applicable`, `blocked_external`.
- No LLM/network calls in build or CI.
- Assessment must be deterministic from repository state.
- Do not create new relation records merely to improve an excavation score.
- Enrich existing canonical relations unless a genuinely distinct relation exists under the spec's relation-creation policy.
- Evidence quality/strength and excavation completeness remain separate axes.
- Existing `strength`, `dossier_level`, source classes, and relation classes must not be overwritten by excavation levels.
- Preserve all existing specific recovery tasks from `build_bible_research_queue.py` until they are represented in the new engine.

---

## File Structure Locked by This Plan

### New core tooling

- `scripts/bible_excavation.py` — dimension definitions, assessment helpers, level derivation, next-action generation.
- `scripts/build_bible_excavation.py` — assemble current corpus/context and write derived report.
- `scripts/validate_bible_excavation.py` — schema/integrity/freshness checks.
- `scripts/test_bible_excavation.py` — deterministic unit tests.
- `knowledge/indexes/bible-comparator-excavation.json` — generated derived report.

### Existing tooling migrated to consume excavation results

- `scripts/build_bible_comparator_quality.py`
- `scripts/build_bible_research_queue.py`
- `scripts/audit_bible_witness_coverage.py`
- `.github/workflows/quality-checks.yml`

### Optional future enrichment layers, not created by this plan unless first queue batch is executed

- existing manifest relation-enrichment JSON files
- existing scene-link/enrichment JSON files

---

### Task 1: Define the Excavation Dimension Contract

**Files:**
- Create: `scripts/bible_excavation.py`
- Create: `scripts/test_bible_excavation.py`

**Interfaces:**
- Produces constants:
  - `STATUSES`
  - `DIMENSIONS`
  - `DIMENSION_GROUPS`
- Produces helper result constructor:

```python
def result(status: str, reason: str, evidence: list[str], next_action: str | None = None) -> dict: ...
```

- [ ] **Step 1: Write failing dimension-contract tests**

Assert exactly these 33 dimensions in stable order:

```python
EXPECTED = [
 'project_exact_wording','project_primary_source','project_earliest_attestation',
 'project_scene_context','project_before_after','project_recurrence','project_wording_status',
 'bible_exact_passage','bible_primary_scene','bible_literary_context','bible_historical_context',
 'bible_parallel_passages','bible_counter_texts','relation_type','relation_sequence_project',
 'relation_sequence_bible','relation_argument','relation_mismatch','maximum_defensible_claim',
 'source_direction','event_date','first_attestation_date','first_comparison_date',
 'formal_archive_date','owner_paths','public_occurrence_links','timeline_links',
 'provenance_summary','related_relations','shared_scene_links','shared_motif_links',
 'shared_operator_links','research_frontier'
]
assert list(DIMENSIONS) == EXPECTED
```

Assert `STATUSES` equals the five allowed values and `result()` rejects unknown statuses.

- [ ] **Step 2: Run and verify failure**

```bash
python scripts/test_bible_excavation.py
```

- [ ] **Step 3: Implement constants and result validation**

Each dimension definition must include:

```python
{
  'group': 'project' | 'bible' | 'relation' | 'chronology' | 'network',
  'label': str,
  'description': str
}
```

Do not put scoring weights in dimension definitions.

- [ ] **Step 4: Run contract tests**

Expected: pass.

- [ ] **Step 5: Commit Task 1**

```bash
git add scripts/bible_excavation.py scripts/test_bible_excavation.py
git commit -m "feat: define Bible excavation dimension contract"
```

---

### Task 2: Assess Project-Side Evidence Dimensions

**Files:**
- Modify: `scripts/bible_excavation.py`
- Modify: `scripts/test_bible_excavation.py`

**Interfaces:**
- Produces:

```python
def assess_project(row: dict, context: dict) -> dict[str, dict]: ...
```

`context` exposes occurrence/timeline/attestation indexes by ID/date.

- [ ] **Step 1: Add exact-wording tests**

Cases:

- exact/public/recovered wording exists → `complete`;
- only `project_anchor` summary → `missing`, next action explicitly asks to recover exact wording;
- primary artifact known but inaccessible/offline → `blocked_external` only when row/context explicitly records an external blocked source; never infer blockage.

- [ ] **Step 2: Add primary-source tests**

Complete when at least one strong source route exists via explicit source/occurrence/timeline/owner metadata. Owner path alone is not automatically a primary source; classify as `partial` if it only points to a later synthesis.

- [ ] **Step 3: Add earliest-attestation tests**

Complete only if a dedicated earliest/first attestation is explicitly identified via row fields or attestation/timeline linkage. A row `date` alone is not proof of earliest occurrence; mark `partial` with reason `event date exists but earliest attestation is not established`.

- [ ] **Step 4: Add scene/before-after/recurrence tests**

`project_scene_context` complete when scene has summary plus at least one meaningful contextual field (`setting`, `activity`, `trigger`, `participants`, `surrounding_topics`).

`project_before_after` complete when both lead-up/before and after/consequence exist; partial if only one side.

`project_recurrence` complete only with explicit recurrence/repetition links or multiple source occurrences; do not infer recurrence from shared motifs elsewhere.

- [ ] **Step 5: Add wording-status test**

Complete when explicit `wording_status` exists or can be deterministically classified from actual stored fields. Never label a summary exact.

- [ ] **Step 6: Implement `assess_project` and run tests**

```bash
python scripts/test_bible_excavation.py
```

- [ ] **Step 7: Commit Task 2**

```bash
git add scripts/bible_excavation.py scripts/test_bible_excavation.py
git commit -m "feat: assess Bible project-side excavation"
```

---

### Task 3: Assess Bible-Side Evidence Dimensions

**Files:**
- Modify: `scripts/bible_excavation.py`
- Modify: `scripts/test_bible_excavation.py`

**Interfaces:**
- Produces:

```python
def assess_bible(row: dict, context: dict) -> dict[str, dict]: ...
```

`context` contains scene map and a local-WEB reference validator supplied by later builder wiring.

- [ ] **Step 1: Test exact-passage assessment**

Complete only when at least one exact relation/scene reference parses and resolves against local WEB verse coordinates. Generic strings such as `Gospel crucifixion tradition`, `messianic tradition`, or `Revelation 21-22` without verse resolution are `partial`, not complete.

- [ ] **Step 2: Test primary-scene assessment**

Complete when `primary_biblical_scene_id` resolves. Partial when only secondary scene links exist. Missing when a narrative/scene-bearing relation has none. `not_applicable` is allowed only for genuinely lexical/non-narrative references and must have a reason.

- [ ] **Step 3: Test literary/historical context**

Use `scripture_context` and linked primary scene fields. Literary context complete when local passage function is explicit. Historical context may be `not_applicable` only when historical detail would not materially alter the comparison; do not auto-penalize every verse without a history paragraph.

- [ ] **Step 4: Test parallel passages and counter-texts**

Parallel passages complete with explicit secondary biblical refs/scenes that are semantically classified as parallels, not merely multiple citations.

Counter-texts complete with explicit `counter_text`, scripture-side counterreadings/limits, or dedicated counter relation. If no counter-reading is expected for a direct explicit quotation relation, allow `not_applicable` with reason.

- [ ] **Step 5: Implement and run tests**

- [ ] **Step 6: Commit Task 3**

```bash
git add scripts/bible_excavation.py scripts/test_bible_excavation.py
git commit -m "feat: assess Bible-side excavation depth"
```

---

### Task 4: Assess Relation Quality, Chronology, Provenance and Network

**Files:**
- Modify: `scripts/bible_excavation.py`
- Modify: `scripts/test_bible_excavation.py`

**Interfaces:**
- Produces:

```python
def assess_relation(row: dict, context: dict) -> dict[str, dict]: ...
def assess_chronology(row: dict, context: dict) -> dict[str, dict]: ...
def assess_network(row: dict, context: dict) -> dict[str, dict]: ...
```

- [ ] **Step 1: Test relation-type/source-direction distinctions**

`relation_type` requires explicit relation/discovery classification. `source_direction` requires explicit direction/history classification; `discovery_mode` alone can make this `partial` but not necessarily complete.

- [ ] **Step 2: Test sequence and argument dimensions**

Project and Bible sequences are assessed independently. Generic prose does not count as a sequence. `relation_argument` complete when `why_dense`/`why_it_matters` or equivalent explicit retained-comparison argument exists.

- [ ] **Step 3: Test mismatch and maximum-claim dimensions**

`relation_mismatch` complete only with explicit mismatch/counterpressure. `maximum_defensible_claim` complete only with an explicit bounded conclusion. Do not derive maximum claims automatically from strength.

- [ ] **Step 4: Test chronology dimensions independently**

Do not collapse dates. Rules:

- `event_date`: row/project anchor date present.
- `first_attestation_date`: explicit first-attestation field/linked ledger.
- `first_comparison_date`: `discovery_history.first_comparison_date` or equivalent.
- `formal_archive_date`: explicit formal archive date.

A relation may therefore be complete on event date and missing first-attestation date.

- [ ] **Step 5: Test provenance dimensions**

`owner_paths`: at least one existing repository owner path.
`public_occurrence_links`: complete when relevant public occurrence IDs exist; `not_applicable` for non-public-source relations.
`timeline_links`: complete when event/timeline IDs exist where chronological relation applies.
`provenance_summary`: explicit provenance/source summary, not inferred solely from owners.

- [ ] **Step 6: Test network dimensions with deterministic relation index**

Build shared indexes across rows for scene IDs, motifs, operators, timeline event IDs. Dimensions are complete when the relation has at least one meaningful linked neighbor in that category; `not_applicable` is allowed when the relation genuinely has no such structural category.

`related_relations` complete when at least one related relation is derived through structural indexes.

- [ ] **Step 7: Test research-frontier dimension**

Complete when a relation has explicit recovery target/open question/research action OR appears in the research queue with a specific evidence need. Generic `more research needed` is only partial.

- [ ] **Step 8: Implement and run tests**

- [ ] **Step 9: Commit Task 4**

```bash
git add scripts/bible_excavation.py scripts/test_bible_excavation.py
git commit -m "feat: assess Bible relation chronology and network"
```

---

### Task 5: Derive Excavation Levels Without Creating a Truth Score

**Files:**
- Modify: `scripts/bible_excavation.py`
- Modify: `scripts/test_bible_excavation.py`

**Interfaces:**
- Produces:

```python
def derive_level(dimensions: dict[str, dict]) -> dict: ...
```

Returns `{level: int, label: str, reason: str}`.

- [ ] **Step 1: Encode level gates explicitly**

Do not average dimensions. Use prerequisite gates:

```text
Level 0 Stub:
  default when Level 1 gates fail.

Level 1 Attested requires:
  project_primary_source != missing
  bible_exact_passage != missing OR bible_primary_scene != missing
  relation_type complete/partial

Level 2 Contextualized additionally requires:
  project_scene_context complete/partial
  bible_literary_context complete/partial
  source_direction complete/partial

Level 3 Dossier-complete additionally requires:
  project_exact_wording complete/partial
  bible_exact_passage complete
  relation_argument complete
  relation_mismatch complete/not_applicable
  maximum_defensible_claim complete
  event_date complete
  provenance_summary complete/partial

Level 4 Excavated additionally requires:
  project_earliest_attestation complete/partial
  project_recurrence complete/not_applicable
  bible_primary_scene complete/not_applicable
  bible_parallel_passages complete/not_applicable
  bible_counter_texts complete/not_applicable
  relation_sequence_project complete/not_applicable
  relation_sequence_bible complete/not_applicable
  owner_paths complete
  related_relations complete/not_applicable

Level 5 Research-frontier explicit additionally requires:
  research_frontier complete
```

- [ ] **Step 2: Test that high `strength` cannot raise a level**

Two otherwise identical fixtures with strength 1 and strength 5 must get the same excavation level.

- [ ] **Step 3: Test that more prose without evidence cannot raise Level 1/2 gates**

- [ ] **Step 4: Implement and run tests**

- [ ] **Step 5: Commit Task 5**

```bash
git add scripts/bible_excavation.py scripts/test_bible_excavation.py
git commit -m "feat: derive non-truth Bible excavation levels"
```

---

### Task 6: Generate the Machine-Readable Excavation Report and Queues

**Files:**
- Create: `scripts/build_bible_excavation.py`
- Create/generated: `knowledge/indexes/bible-comparator-excavation.json`
- Modify: `scripts/test_bible_excavation.py`

**Interfaces:**
- Consumes: manifest relations/scenes plus timeline/attestation/public occurrence/research queue files.
- Produces report with top-level:

```json
{
  "id":"bible-comparator-excavation",
  "version":"1.0.0",
  "status":"derived-maintenance-audit",
  "manifest_version":"...",
  "active_relation_count":0,
  "dimensions":{},
  "level_counts":{},
  "status_counts":{},
  "relations":[],
  "queues":{}
}
```

- [ ] **Step 1: Implement context loaders**

Load optional context defensively from known canonical paths. Missing optional context should reduce completeness, not crash. Missing manifest/scenes/relation data remains a hard error.

- [ ] **Step 2: Implement one `assess_all(rows, scenes, context)` path**

For each relation, combine all 33 dimension assessments and `derive_level`.

Each relation record contains:

```json
{
  "id":"...",
  "date":"...",
  "strength":5,
  "dossier_level":"A",
  "excavation_level":3,
  "excavation_label":"Dossier-complete",
  "dimensions":{...},
  "next_actions":[...]
}
```

- [ ] **Step 3: Generate global queues by dimension**

At minimum keys:

- `missing_exact_project_wording`
- `missing_earliest_attestation`
- `missing_primary_biblical_scene`
- `imprecise_or_missing_scripture`
- `missing_relation_sequence`
- `missing_counterpressure`
- `missing_maximum_claim`
- `missing_source_direction`
- `missing_provenance`
- `missing_research_frontier`

Queue entries contain `relation_id`, date, strength, excavation level, dimension, status, reason, next_action.

Sort by:

1. lower excavation level;
2. stronger existing relation strength (to deepen high-value surviving relations first);
3. earlier date for chronology queues / stable relation ID final tie-break.

- [ ] **Step 4: Generate current report**

```bash
python scripts/build_bible_excavation.py
```

- [ ] **Step 5: Add assertions to tests for deterministic ordering and all active relation coverage**

- [ ] **Step 6: Commit Task 6**

```bash
git add scripts/build_bible_excavation.py scripts/test_bible_excavation.py knowledge/indexes/bible-comparator-excavation.json
git commit -m "feat: generate Bible excavation report"
```

---

### Task 7: Add Excavation Report Validation and Freshness Checks

**Files:**
- Create: `scripts/validate_bible_excavation.py`
- Modify: `scripts/test_bible_excavation.py`

**Interfaces:**
- Consumes generated report and live corpus.
- Produces nonzero exit for invalid/stale structure only, not low completeness.

- [ ] **Step 1: Implement validation rules**

Hard errors:

- unknown/missing dimension;
- unknown status;
- relation count mismatch with live manifest corpus;
- report relation ID unknown/missing;
- missing reason/evidence on every result;
- non-complete status missing `next_action` unless `not_applicable`;
- referenced repository evidence path does not exist when evidence is a path;
- excavation level outside 0..5;
- queue references unknown relation/dimension;
- report differs from deterministic rebuild.

- [ ] **Step 2: Explicitly prohibit truth-score vocabulary in level metadata**

Validator should reject level label/description containing phrases such as `truth score`, `true relation`, `prophecy fulfilled`, `divine certainty`, `historically identical`.

- [ ] **Step 3: Add stale-report test**

Generate in memory, mutate one dimension, ensure validator catches mismatch.

- [ ] **Step 4: Run tests/validator**

```bash
python scripts/test_bible_excavation.py
python scripts/build_bible_excavation.py
python scripts/validate_bible_excavation.py
```

- [ ] **Step 5: Commit Task 7**

```bash
git add scripts/validate_bible_excavation.py scripts/test_bible_excavation.py
git commit -m "test: validate Bible excavation integrity"
```

---

### Task 8: Migrate Existing Quality and Research Queues onto Excavation Results

**Files:**
- Modify: `scripts/build_bible_comparator_quality.py`
- Modify: `scripts/build_bible_research_queue.py`
- Modify: `scripts/audit_bible_witness_coverage.py`
- Modify: `scripts/test_bible_corpus.py`

**Interfaces:**
- Consumes: functions/report structures from `bible_excavation.py`.
- Produces backward-compatible existing report/queue files during migration.

- [ ] **Step 1: Refactor quality report to project from excavation**

Keep current public keys (`active_relation_count`, `active_scene_count`, `relations_with_reusable_scene`, `action_counts`, etc.) where downstream tests depend on them, but derive missing/enrich/research state from excavation dimensions rather than a second independent checklist.

Recommended mapping:

- `retain`: Level >= 3 and no critical project/bible provenance gaps.
- `enrich`: Level 1-2 or Level >=3 with noncritical partial/missing dimensions.
- `research`: project primary source/earliest attestation is missing on low-strength/provisional relations, or explicit recovery task exists.

Do not turn Level 0 into automatic deletion/quarantine.

- [ ] **Step 2: Preserve all six current specific recovery tasks**

Move `SPECIFIC` recovery definitions into `bible_excavation.py` or a dedicated data constant/module only after tests prove identical task text/status/priority. `build_bible_research_queue.py` then selects from excavation `research_frontier`/project evidence gaps.

- [ ] **Step 3: Simplify witness coverage audit**

Make it summarize excavation groups/levels instead of maintaining another bespoke completeness definition. Keep the unsupported-rich-scene check because it is a distinct integrity check.

- [ ] **Step 4: Update corpus tests**

Replace direct tests of old `research_reasons` heuristics with excavation mapping tests while preserving output compatibility assertions.

- [ ] **Step 5: Run migration tests**

```bash
python scripts/test_bible_excavation.py
python scripts/test_bible_corpus.py
python scripts/build_bible_comparator_quality.py
python scripts/build_bible_research_queue.py
python scripts/audit_bible_witness_coverage.py
```

- [ ] **Step 6: Commit Task 8**

```bash
git add scripts/build_bible_comparator_quality.py scripts/build_bible_research_queue.py scripts/audit_bible_witness_coverage.py scripts/test_bible_corpus.py scripts/bible_excavation.py
git commit -m "refactor: drive Bible quality queues from excavation"
```

---

### Task 9: Wire Excavation into CI and Produce the First Mining Batch

**Files:**
- Modify: `.github/workflows/quality-checks.yml`
- Create: `docs/superpowers/plans/2026-09-14-bible-excavation-batch-001.md` only after current report exists.

**Interfaces:**
- Consumes: generated excavation report.
- Produces: CI freshness protection and a concrete first enrichment batch chosen from actual gaps.

- [ ] **Step 1: Add CI build/validate commands**

Under Bible validation:

```bash
python scripts/test_bible_excavation.py
python scripts/build_bible_excavation.py
python scripts/validate_bible_excavation.py
```

Report build must occur before validation.

- [ ] **Step 2: Run current report and inspect queues**

```bash
python scripts/build_bible_excavation.py
python scripts/validate_bible_excavation.py
```

Record actual level counts and top missing dimensions. Do not guess them in advance.

- [ ] **Step 3: Select first batch using deterministic rule**

Choose 5-10 relations meeting all:

1. active manifest relation;
2. highest-value missing dimension among exact wording / earliest attestation / primary scene / relation sequence / maximum claim / source direction;
3. relation has existing strength >=4 OR is historically foundational to the Tim/Son chronology;
4. no need to create a new relation to improve it.

- [ ] **Step 4: Write the concrete batch plan**

The batch plan must name exact relation IDs and exact missing dimensions from the generated report. Each relation task must state source files to inspect and the expected enrichment owner/layer.

Do not write a generic “mine more” batch.

- [ ] **Step 5: Commit Task 9**

```bash
git add .github/workflows/quality-checks.yml knowledge/indexes/bible-comparator-excavation.json docs/superpowers/plans/2026-09-14-bible-excavation-batch-001.md
git commit -m "chore: wire Bible excavation into quality workflow"
```

---

## Completion Gate

Run:

```bash
python scripts/test_bible_excavation.py
python scripts/build_bible_excavation.py
python scripts/validate_bible_excavation.py
python scripts/test_bible_corpus.py
python scripts/build_bible_comparator_quality.py
python scripts/build_bible_research_queue.py
python scripts/audit_bible_witness_coverage.py
python scripts/validate_bible_reader.py
```

Then require `Repository quality checks` to pass in the implementation PR.

The engine is complete only when every active manifest relation appears once in `bible-comparator-excavation.json` with all 33 dimensions, an excavation level, and concrete next actions for incomplete dimensions.
