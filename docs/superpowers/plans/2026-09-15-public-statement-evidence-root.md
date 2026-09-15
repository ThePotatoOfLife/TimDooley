# Public Statement Evidence Root Implementation Plan

> **STATUS — IMPLEMENTED / HISTORICAL EXECUTION PLAN.** The authoritative current contract is `data/evidence/public-statement-root-manifest.json`, enforced by the rooted-stack builders and validators. Unchecked boxes below are retained as execution history and must not be interpreted as the current backlog.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox syntax for tracking.

**Goal:** Build a lossless Evidence Root that supplies trustworthy Ring-0 statement anchors for the Root → Spiral → Discovery → Testing → Consolidation architecture.

**Architecture:** Source ledgers remain immutable evidence owners. Reconciliation produces stable statement identities with exact wording, best-known timestamp precision, status IDs, and full provenance. Chronological ordering is emitted only as one traversal index; it does not define canonical identity or graph centrality.

**Tech Stack:** Python 3 stdlib, JSON, pytest.

**Spec:** `docs/superpowers/specs/2026-09-15-evidence-atlas-design.md`

## Global constraints

- Start from canonical/primary evidence and move outward.
- Preserve exact wording.
- Preserve the most precise known time without erasing weaker source records.
- Never merge solely because timestamps match.
- Status ID is the strongest available public-post identity key.
- Exact `(date, quote)` is the fallback merge key.
- Ambiguous joins remain unresolved.
- Coverage/search gaps are metadata, not negative evidence.
- Evidence strength and spiral distance are separate dimensions.
- This slice assigns no biblical or theological interpretation.

---

### Task 1 — Reconciliation kernel

**Files:**
- `tests/fixtures/public-statement-evidence-sources.json`
- `tests/test_public_statement_evidence_root.py`
- `scripts/public_statement_evidence_root.py`

- [x] RED: tests require precision upgrades, same-second separation, status-ID priority, verbatim wording, and full provenance.
- [x] GREEN: implement `timestamp_precision(record)` and `reconcile_records(records)`.
- [x] Verify locally: 5 tests pass.

### Task 2 — Timestamp capture importer

**Files:**
- `tests/test_public_statement_timestamp_import.py`
- `scripts/import_public_statement_timestamp_capture.py`
- `data/evidence/rational-potato-x-timestamped-ledger-2025-2026.json`

- [x] RED: parser module absent.
- [x] GREEN: parse second-level GMT records, preserve capture line and verbatim quote, suffix true same-second collisions, and emit search-gap metadata.
- [x] Verify against supplied capture locally: 104 occurrences, range `2025-09-15T14:39:46Z` → `2026-09-15T08:20:48Z`, one two-record same-second collision, one Jan–Feb search-gap note.
- [ ] Persist the generated 104-record timestamp ledger in the repository.

### Task 3 — Root builder

**Files:**
- `tests/test_public_statement_evidence_root_builder.py`
- `scripts/build_public_statement_evidence_root.py`
- `data/evidence/public-statement-evidence-root.json`

**Contract:**

```json
{
  "id": "public-statement-evidence-root",
  "version": "1.0.0",
  "model": "rooted-spiral",
  "source_owners": [],
  "roots": [],
  "coverage_notes": [],
  "traversals": {"chronological": []},
  "reconciliation": {"merged_groups": 0, "unresolved": []}
}
```

- [ ] RED: builder tests require source reconciliation without identity-by-sort-order.
- [ ] GREEN: adapt existing date ledger and timestamp ledger into neutral records and call `reconcile_records`.
- [ ] Emit `roots` as canonical statement anchors.
- [ ] Emit chronology only under `traversals.chronological` as root IDs.
- [ ] Preserve unresolved joins explicitly.

### Task 4 — Status-ID enrichment

**Files:**
- `scripts/build_public_statement_evidence_root.py`
- `tests/test_public_statement_evidence_root_builder.py`

- [ ] Join known September status IDs only on unambiguous evidence.
- [ ] Use exact status ID when already present.
- [ ] Permit unique date+minute candidate attachment only when exactly one candidate exists.
- [ ] Leave ambiguous minute matches unresolved.

### Task 5 — Gap/discovery seed

**Files:**
- `knowledge/indexes/public-statement-discovery-gaps.json`
- `scripts/build_public_statement_evidence_root.py`

- [ ] Emit typed evidence/chronology/consolidation gaps discovered during reconciliation.
- [ ] Do not auto-promote them into relations.
- [ ] Each gap records source roots, reason, status (`open`, `resolved`, `rejected`) and next test.

### Task 6 — Validation and ownership

**Files:**
- `scripts/validate_public_statement_evidence_root.py`
- `data/canonical-source-map.json`
- `.github/workflows/quality-checks.yml`

- [ ] RED validator tests: duplicate status IDs, precision regression, source loss, quote mutation, accidental same-second collapse, unresolved references, identity/order coupling.
- [ ] GREEN validator.
- [ ] Declare `public_statements` canonical family: Evidence Root owns reconciled statement identity; source ledgers remain evidence owners; chronology remains a derived traversal.
- [ ] Wire builder + validator + pytest into quality checks.

## Completion boundary

This plan ends when the Evidence Root is trustworthy. Episodes, Development Threads, Bible projection, countertexts, Wave 28 lenses, and public spiral navigation are later outward passes built from this root.

## Supersession

This plan supersedes `2026-09-15-public-statement-evidence-spine.md`. The older plan is retained as design history but its linear “spine” terminology is no longer canonical.
