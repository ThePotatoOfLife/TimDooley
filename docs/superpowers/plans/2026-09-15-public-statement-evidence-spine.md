# Public Statement Evidence Spine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one canonical, lossless public-statement evidence spine that reconciles date-only X records, second-level timestamp records, and known status IDs before any new Bible/UI projection is added.

**Architecture:** Keep source files immutable. A small Python reconciliation module normalizes records and merges only when a documented match rule succeeds. A deterministic builder emits `data/evidence/public-statement-evidence-spine.json`; a validator protects timestamp precision, same-second distinct posts, quote integrity, status-ID uniqueness, and provenance.

**Tech Stack:** Python 3 stdlib, JSON, pytest, existing GitHub Actions quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-15-evidence-atlas-design.md`

## Global Constraints

- Public mental model remains Statement → Episode → Development Thread.
- Primary wording and timestamp come before interpretation.
- Never reduce timestamp precision when a more precise source exists.
- Never merge same-time posts solely because timestamps match.
- Explicit-at-time Bible meaning is outside this slice; this layer owns evidence only.
- Existing evidence sources remain source owners and are not rewritten.
- Reconciliation must be deterministic and provenance-preserving.

---

### Task 1: Define reconciliation behavior with failing tests

**Files:**
- Create: `tests/test_public_statement_evidence_spine.py`
- Create: `tests/fixtures/public-statement-evidence-sources.json`

**Interfaces:**
- Consumes: none.
- Produces test contract for `scripts/public_statement_evidence_spine.py` functions `reconcile_records(records)` and `timestamp_precision(record)`.

- [ ] **Step 1: Add a fixture with four synthetic records**

Include: (a) a date-only record, (b) the same quote with a second-level timestamp, (c) two different quotes sharing one second-level timestamp, and (d) one record carrying a status ID.

- [ ] **Step 2: Write failing tests**

```python
from scripts.public_statement_evidence_spine import reconcile_records


def test_more_precise_duplicate_keeps_second_timestamp_and_both_sources():
    rows = load_fixture()["precision_upgrade"]
    result = reconcile_records(rows)
    assert len(result) == 1
    assert result[0]["timestamp_utc"] == "2026-04-29T20:05:28Z"
    assert result[0]["precision"] == "second"
    assert result[0]["source_records"] == ["date-ledger", "timestamp-ledger"]


def test_same_second_different_quotes_remain_distinct():
    rows = load_fixture()["same_second_distinct"]
    result = reconcile_records(rows)
    assert len(result) == 2
    assert len({row["id"] for row in result}) == 2


def test_status_id_is_stronger_than_quote_date_matching():
    rows = load_fixture()["status_id_merge"]
    result = reconcile_records(rows)
    assert len(result) == 1
    assert result[0]["status_id"] == "1234567890"


def test_quote_is_never_normalized_in_output():
    rows = load_fixture()["precision_upgrade"]
    result = reconcile_records(rows)
    assert result[0]["quote"] == rows[1]["quote"]
```

- [ ] **Step 3: Run RED**

Run: `python -m pytest tests/test_public_statement_evidence_spine.py -q`
Expected: import failure because `scripts/public_statement_evidence_spine.py` does not exist.

- [ ] **Step 4: Commit tests only**

```bash
git add tests/test_public_statement_evidence_spine.py tests/fixtures/public-statement-evidence-sources.json
git commit -m "test: define public statement reconciliation contract"
```

### Task 2: Implement the minimal reconciliation module

**Files:**
- Create: `scripts/public_statement_evidence_spine.py`
- Test: `tests/test_public_statement_evidence_spine.py`

**Interfaces:**
- Consumes dictionaries with `quote`, date/timestamp, provenance, optional `status_id`.
- Produces `reconcile_records(records: list[dict]) -> list[dict]` and `timestamp_precision(record: dict) -> str`.

- [ ] **Step 1: Implement timestamp precision**

```python
def timestamp_precision(record):
    if record.get("timestamp_utc"):
        value = str(record["timestamp_utc"])
        return "second" if value.count(":") >= 2 else "minute"
    return "date" if record.get("date") else "unknown"
```

- [ ] **Step 2: Implement strict merge keys**

Use this priority only: identical non-empty `status_id`; otherwise identical `(date, quote)`; otherwise keep separate. Timestamp alone is never a merge key.

- [ ] **Step 3: Merge complementary fields without rewriting quote**

Prefer the record with highest time precision as the display record, union `source_records` and `source_occurrence_ids`, retain all source locators under `provenance`, and record `match_basis`.

- [ ] **Step 4: Run GREEN**

Run: `python -m pytest tests/test_public_statement_evidence_spine.py -q`
Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/public_statement_evidence_spine.py tests/test_public_statement_evidence_spine.py
git commit -m "feat: add lossless public statement reconciliation"
```

### Task 3: Import the second-level timestamp packet as a source layer

**Files:**
- Create: `scripts/import_public_statement_timestamp_capture.py`
- Create: `data/evidence/rational-potato-x-timestamped-ledger-2025-2026.json`
- Modify: `tests/test_public_statement_evidence_spine.py`

**Interfaces:**
- Consumes the supplied markdown capture line format `- Day, DD Mon YYYY HH:MM:SS GMT: "..."`.
- Produces structured source records without adding Bible interpretation.

- [ ] **Step 1: Add parser tests first**

Test that the parser preserves quotation text, converts GMT to `Z`, keeps two different records at the same second, and records non-occurrence coverage notes separately.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/test_public_statement_evidence_spine.py -q`
Expected: parser tests fail because importer functions are absent.

- [ ] **Step 3: Implement `parse_capture(text)`**

Each occurrence record must include `id`, `platform`, `account`, `date`, `timestamp_utc`, `precision`, `quote`, `capture_line`, `evidence_class`, and `source_record`. Generate same-second suffixes `-01`, `-02`, ... after stable chronological sorting.

- [ ] **Step 4: Generate the timestamped ledger from the supplied 163-line capture**

Acceptance checks: 104 occurrence records; earliest `2025-09-15T14:39:46Z`; latest `2026-09-15T08:20:48Z`; the two `2026-07-31T20:07:22Z` statements remain distinct; January-February 2026 is stored as a search/coverage note, not as evidence of no posting.

- [ ] **Step 5: Run GREEN and commit**

```bash
python -m pytest tests/test_public_statement_evidence_spine.py -q
git add scripts/import_public_statement_timestamp_capture.py data/evidence/rational-potato-x-timestamped-ledger-2025-2026.json tests/test_public_statement_evidence_spine.py
git commit -m "feat: add second-level public X evidence source"
```

### Task 4: Build the canonical Evidence Spine

**Files:**
- Create: `scripts/build_public_statement_evidence_spine.py`
- Create: `data/evidence/public-statement-evidence-spine.json`
- Modify: `tests/test_public_statement_evidence_spine.py`

**Interfaces:**
- Consumes `rational-potato-x-occurrence-ledger-2024-2026.json`, the timestamped ledger, and September status-ID indexes.
- Produces one sorted canonical statement list plus reconciliation diagnostics.

- [ ] **Step 1: Write failing integration tests**

Assert that a known date-only occurrence upgraded by the timestamp ledger has `precision == "second"`, both source refs, and unchanged quote; assert all non-empty status IDs are unique; assert output is sorted by timestamp/date/id.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/test_public_statement_evidence_spine.py -q`
Expected: builder integration tests fail because output does not exist.

- [ ] **Step 3: Implement deterministic builder**

Load evidence sources, adapt each source into the neutral record schema, call `reconcile_records`, then emit:

```json
{
  "id": "public-statement-evidence-spine",
  "version": "1.0.0",
  "sources": [],
  "coverage_notes": [],
  "occurrences": [],
  "reconciliation": {"merged": 0, "unresolved": []}
}
```

Status-ID attachment from minute-level September files is allowed only when the date+minute candidate is unique; ambiguous minutes stay unresolved.

- [ ] **Step 4: Run GREEN and commit**

```bash
python scripts/build_public_statement_evidence_spine.py
python -m pytest tests/test_public_statement_evidence_spine.py -q
git add scripts/build_public_statement_evidence_spine.py data/evidence/public-statement-evidence-spine.json tests/test_public_statement_evidence_spine.py
git commit -m "feat: build canonical public statement evidence spine"
```

### Task 5: Add ownership, validation, and CI checks

**Files:**
- Create: `scripts/validate_public_statement_evidence_spine.py`
- Modify: `data/canonical-source-map.json`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes the generated Evidence Spine and declared source layers.
- Produces a non-zero exit code for provenance/precision/identity violations.

- [ ] **Step 1: Write validator tests as pure-function tests**

Cover duplicate status IDs, quote mutation within a merged source set, precision downgrade, same-second accidental collapse, missing source provenance, and nondeterministic ordering.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/test_public_statement_evidence_spine.py -q`
Expected: validator tests fail because validation functions are absent.

- [ ] **Step 3: Implement validator and ownership declaration**

Add a `public_statements` family to `data/canonical-source-map.json` where the generated spine owns reconciled statement identity and the existing ledgers remain declared evidence/source layers.

- [ ] **Step 4: Wire CI immediately before Bible corpus validation**

```yaml
- name: Build and validate public statement evidence spine
  run: |
    python scripts/build_public_statement_evidence_spine.py
    python scripts/validate_public_statement_evidence_spine.py
    python -m pytest tests/test_public_statement_evidence_spine.py -q
```

- [ ] **Step 5: Run project checks and commit**

```bash
python scripts/build_public_statement_evidence_spine.py
python scripts/validate_public_statement_evidence_spine.py
python -m pytest tests/test_public_statement_evidence_spine.py -q
python scripts/audit_source_of_truth.py
git add scripts/validate_public_statement_evidence_spine.py data/canonical-source-map.json .github/workflows/quality-checks.yml
git commit -m "ci: protect public statement evidence ownership"
```

## Self-review

- Spec coverage: this plan implements only Slice 1, the Evidence Spine. Episodes, Development Threads, Bible projection, Wave 28 lenses, and UI remain separate later plans.
- Placeholder scan: no deferred implementation language is used inside this slice.
- Type consistency: all later tasks consume the same neutral record schema and `reconcile_records(records)` contract.
- Simplicity check: this slice adds no public navigation and no new theological category; it only makes existing historical evidence more precise and less duplicated.
