# Bible Corpus Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic backend consolidation layer that finds duplicate candidates, meaningful overlap families, functional contrasts, and better retrieval representatives across the existing active Bible corpus without deleting, rewriting, or strengthening canonical relations.

**Architecture:** Reuse `scripts/bible_corpus.py` as the sole active-corpus assembler and `scripts/bible_excavation.py` as the quality/completeness owner. Add one pure consolidation module, one builder, one validator, generated index artifacts under `knowledge/indexes/`, and CI checks. The public reader stays unchanged in this phase.

**Tech Stack:** Python 3, stdlib only (`re`, `hashlib`, `json`, `collections`, `pathlib`), pytest, existing GitHub Actions quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-16-bible-corpus-consolidation-design.md`

## Global Constraints

- Preserve every active canonical/additive relation record exactly as assembled by `scripts/bible_corpus.py`.
- Do not delete, rewrite, rename, or auto-merge canonical relation records.
- Do not synthesize new theological claims, prophecy claims, supernatural identities, causal claims, or role transfers.
- Shared vocabulary alone is insufficient for duplicate or family membership.
- Contrasting functions must remain distinct even when they share a symbol or passage family.
- Representative selection must be deterministic and independent of input order.
- Generated family IDs must be deterministic and independent of input order.
- The consolidation output may surface existing maximum claims but may not create a stronger family-level theological conclusion.
- Existing exact relation-ID collision behavior in `scripts/bible_corpus.py` remains unchanged.
- Public Bible rendering is outside this implementation.

---

### Task 1: Normalize relation fingerprints and classify pairs

**Files:**
- Create: `scripts/bible_consolidation.py`
- Create: `tests/test_bible_consolidation.py`

**Interfaces:**
- Consumes: active relation dictionaries from `bible_corpus.assemble_relations()` and optional excavation assessments keyed by relation ID.
- Produces:
  - `fingerprint_relation(row: dict, assessment: dict | None = None) -> dict`
  - `classify_pair(left: dict, right: dict) -> dict`
  - `normalize_ref(value: str) -> str`
  - classification values: `duplicate_candidate`, `overlap_candidate`, `contrast_candidate`, `unrelated`

- [ ] **Step 1: Write failing fingerprint tests**

Add tests proving normalization is deterministic and non-destructive:

```python
from scripts.bible_consolidation import fingerprint_relation


def test_fingerprint_is_input_order_independent_and_preserves_source_row():
    row = {
        "id": "sample",
        "project_anchor": " Door / Gate  access ",
        "biblical_refs": ["John 10:9", "Revelation 3:20"],
        "source_owners": ["b.json", "a.json"],
        "relation_argument": {
            "project_sequence": ["door", "entry"],
            "biblical_sequence": ["knock", "open", "meal"],
            "maximum_claim": "A bounded claim.",
        },
    }
    before = repr(row)
    fp = fingerprint_relation(row)
    assert repr(row) == before
    assert fp["relation_id"] == "sample"
    assert fp["biblical_refs"] == ["john 10:9", "revelation 3:20"]
    assert fp["source_owners"] == ["a.json", "b.json"]
```

- [ ] **Step 2: Write failing pair-classification tests**

Use synthetic records derived from real corpus patterns:

```python
def test_same_passage_same_function_is_duplicate_candidate():
    left = make_relation(
        "root-a", ["Romans 11:17-18"],
        anchor="root supports branches; do not boast",
        bible_sequence=["root supports branches", "branches warned not to boast"],
        maximum_claim="Root support and anti-boasting belong together.",
    )
    right = make_relation(
        "root-b", ["Romans 11:17-18"],
        anchor="branches depend on root; anti-boasting control",
        bible_sequence=["root supports branches", "branches warned not to boast"],
        maximum_claim="Root support and anti-boasting belong together.",
    )
    result = classify_pair(fingerprint_relation(left), fingerprint_relation(right))
    assert result["classification"] == "duplicate_candidate"
    assert "same_scripture" in result["reasons"]


def test_yoke_reversal_is_contrast_not_duplicate():
    learning = make_relation(
        "teaching-yoke", ["Matthew 11:28-30"],
        anchor="yoke can teach and give rest",
        bible_sequence=["take yoke", "learn", "find rest"],
        boundary="not slavery",
    )
    slavery = make_relation(
        "slavery-yoke", ["Galatians 5:1"],
        anchor="yoke can suppress freedom",
        bible_sequence=["freedom", "yoke of slavery"],
        boundary="not every obligation is slavery",
    )
    result = classify_pair(fingerprint_relation(learning), fingerprint_relation(slavery))
    assert result["classification"] == "contrast_candidate"
```

Also add a weak lexical coincidence test where only a token such as `house` overlaps; expected `unrelated`.

- [ ] **Step 3: Run tests to verify RED**

Run:

```bash
python -m pytest -q tests/test_bible_consolidation.py
```

Expected: import failure because `scripts/bible_consolidation.py` does not exist.

- [ ] **Step 4: Implement normalization and staged pair classification**

Implement focused helpers:

```python
TOKEN_RE = re.compile(r"[a-z0-9]+")


def norm_text(value: object) -> str:
    return " ".join(TOKEN_RE.findall(str(value or "").lower()))


def normalize_ref(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower().replace("–", "-").replace("—", "-"))


def token_set(value: object) -> set[str]:
    return set(TOKEN_RE.findall(str(value or "").lower()))
```

`fingerprint_relation()` must sort references/owners/motifs/operators/scenes and expose normalized anchor/sequence/max-claim tokens plus boolean presence of boundary/counterpressure and excavation level.

`classify_pair()` must use staged rules, not one opaque similarity number:

1. exact/same normalized reference set + strong sequence/anchor agreement -> `duplicate_candidate`;
2. shared precise passage/scene + meaningful anchor/function overlap -> `overlap_candidate`;
3. shared symbol/function vocabulary with explicit opposing boundary/sequence indicators -> `contrast_candidate`;
4. otherwise -> `unrelated`.

Every non-unrelated result must contain deterministic `reasons` and `shared` evidence fields.

- [ ] **Step 5: Run tests to verify GREEN**

Run:

```bash
python -m pytest -q tests/test_bible_consolidation.py
```

Expected: all Task 1 tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/bible_consolidation.py tests/test_bible_consolidation.py
git commit -m "feat: add deterministic Bible relation fingerprints"
```

---

### Task 2: Build stable functional families and representatives

**Files:**
- Modify: `scripts/bible_consolidation.py`
- Modify: `tests/test_bible_consolidation.py`

**Interfaces:**
- Consumes: fingerprints + pair classifications from Task 1.
- Produces:
  - `build_families(relations: list[dict], assessments: dict[str, dict] | None = None) -> list[dict]`
  - `select_representative(member_ids: list[str], fingerprints: dict[str, dict]) -> str`
  - `stable_family_id(member_ids: list[str], shared_terms: list[str]) -> str`

- [ ] **Step 1: Add failing family tests using real corpus relation IDs**

Require Mountain relations to group without flattening their functions:

```python
def test_mountain_family_preserves_distinct_functions(real_relations):
    wanted = {
        "sinai-guarded-ascent-return-instruction",
        "zion-circulation-center",
        "nebo-vision-without-possession",
        "mountain-temptation-possession-countertext",
    }
    families = build_families([r for r in real_relations if r["id"] in wanted])
    family = next(f for f in families if wanted <= set(f["member_relation_ids"]))
    assert len(family["member_functions"]) >= 4
    assert "mountain-temptation-possession-countertext" in family["contrast_relation_ids"]
```

Require Door relations to share a family while barrier and invitation/open circulation remain distinct members. Require representative selection to remain unchanged after reversing/shuffling input.

- [ ] **Step 2: Run targeted tests to verify RED**

```bash
python -m pytest -q tests/test_bible_consolidation.py -k "family or representative"
```

Expected: fail because family functions do not yet exist.

- [ ] **Step 3: Implement deterministic connected-component family construction**

Build a graph from `overlap_candidate` and `contrast_candidate` edges only; do not create families from weak lexical overlap.

Each family must emit:

```python
{
    "id": "family-<stable-hash>",
    "label": "...",
    "member_relation_ids": [...],
    "representative_relation_id": "...",
    "supporting_relation_ids": [...],
    "contrast_relation_ids": [...],
    "member_functions": {"relation-id": ["normalized", "function", "tokens"]},
    "shared_biblical_refs": [...],
    "source_owners": [...],
    "member_maximum_claims": {"relation-id": "existing claim text"},
}
```

`stable_family_id()` must hash a sorted stable identity basis, never list order.

Representative ranking must consume existing excavation completeness signals in lexicographic priority order rather than inventing a weighted theology score. Ties fall back to relation ID.

- [ ] **Step 4: Run targeted tests to verify GREEN**

```bash
python -m pytest -q tests/test_bible_consolidation.py -k "family or representative"
```

Expected: pass.

- [ ] **Step 5: Run all consolidation tests**

```bash
python -m pytest -q tests/test_bible_consolidation.py
```

Expected: pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/bible_consolidation.py tests/test_bible_consolidation.py
git commit -m "feat: build stable Bible relation families"
```

---

### Task 3: Create the duplicate reconciliation queue with unique-evidence protection

**Files:**
- Modify: `scripts/bible_consolidation.py`
- Modify: `tests/test_bible_consolidation.py`

**Interfaces:**
- Produces:
  - `build_duplicate_queue(relations: list[dict], fingerprints: dict[str, dict], pair_results: list[dict]) -> list[dict]`
  - `unique_evidence(left: dict, right: dict) -> dict`

- [ ] **Step 1: Add failing tests for evidence preservation**

```python
def test_duplicate_queue_exposes_unique_evidence_before_alias_recommendation():
    left = make_relation(
        "a", ["Romans 11:17-18"],
        source_owners=["primary-a.json"],
        boundary="Do not boast.",
    )
    right = make_relation(
        "b", ["Romans 11:17-18"],
        source_owners=["primary-b.json"],
        counter_text="Branches can be removed.",
    )
    queue = build_duplicate_queue_for([left, right])
    item = queue[0]
    assert item["unique_evidence"]["a"]
    assert item["unique_evidence"]["b"]
    assert item["suggested_action"] != "alias" or item["requires_evidence_migration"] is True
```

- [ ] **Step 2: Run test to verify RED**

```bash
python -m pytest -q tests/test_bible_consolidation.py -k unique_evidence
```

Expected: fail because duplicate queue helpers do not exist.

- [ ] **Step 3: Implement duplicate queue**

For each `duplicate_candidate`, emit:

```python
{
    "relation_ids": ["a", "b"],
    "recommended_representative_id": "a",
    "reasons": [...],
    "unique_evidence": {"a": {...}, "b": {...}},
    "requires_evidence_migration": True,
    "suggested_action": "enrich_existing",
}
```

Allow `alias` only when no unique source owner, precise passage, occurrence/provenance, boundary/countertext, sequence, or maximum-claim evidence would disappear.

- [ ] **Step 4: Run tests to verify GREEN**

```bash
python -m pytest -q tests/test_bible_consolidation.py
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/bible_consolidation.py tests/test_bible_consolidation.py
git commit -m "feat: protect evidence in Bible duplicate review"
```

---

### Task 4: Build generated consolidation indexes from the real active corpus

**Files:**
- Create: `scripts/build_bible_consolidation.py`
- Create: `tests/test_build_bible_consolidation.py`
- Generated at runtime: `knowledge/indexes/bible-relation-fingerprints.json`
- Generated at runtime: `knowledge/indexes/bible-relation-families.json`
- Generated at runtime: `knowledge/indexes/bible-duplicate-review-queue.json`

**Interfaces:**
- Consumes `load_manifest`, `assemble_relations`, `assemble_scenes` from `scripts/bible_corpus.py` and `build_report` / `assess_relation` outputs from `scripts/bible_excavation.py`.
- Produces deterministic JSON documents stamped with active `manifest_version` and `relation_count`.

- [ ] **Step 1: Add failing builder test**

```python
def test_build_outputs_cover_every_active_relation(tmp_path):
    outputs = build_outputs(ROOT)
    active_ids = {row["id"] for row in assemble_relations(ROOT, load_manifest(ROOT))}
    assert {row["relation_id"] for row in outputs["fingerprints"]["relations"]} == active_ids
    assert outputs["fingerprints"]["relation_count"] == len(active_ids)
    assert outputs["families"]["manifest_version"] == load_manifest(ROOT)["version"]
```

Also assert building from reversed relation input yields byte-equivalent sorted JSON payloads.

- [ ] **Step 2: Run builder tests to verify RED**

```bash
python -m pytest -q tests/test_build_bible_consolidation.py
```

Expected: fail because builder does not exist.

- [ ] **Step 3: Implement builder**

Expose:

```python
def build_outputs(root: Path) -> dict[str, dict]:
    ...


def write_outputs(root: Path, outputs: dict[str, dict]) -> None:
    ...
```

Sort all emitted lists deterministically. JSON writes use `indent=2`, `sort_keys=True`, trailing newline.

Do not mutate relation source files or manifest.

- [ ] **Step 4: Run builder tests to verify GREEN**

```bash
python -m pytest -q tests/test_build_bible_consolidation.py
```

Expected: pass.

- [ ] **Step 5: Run the builder on the real corpus and inspect counts**

```bash
python scripts/build_bible_consolidation.py
```

Expected: three generated indexes and a summary including active relation count, family count, duplicate-candidate count, contrast count, and ungrouped relation count.

- [ ] **Step 6: Commit code/tests only unless repository convention requires generated indexes tracked**

```bash
git add scripts/build_bible_consolidation.py tests/test_build_bible_consolidation.py
git commit -m "feat: build Bible consolidation indexes"
```

---

### Task 5: Validate no-loss/no-overclaim invariants on generated indexes

**Files:**
- Create: `scripts/validate_bible_consolidation.py`
- Create: `tests/test_validate_bible_consolidation.py`

**Interfaces:**
- Consumes the three generated indexes plus active corpus/manifest.
- Produces exit 0 on valid generated state; nonzero with actionable error lines otherwise.

- [ ] **Step 1: Add failing validator tests**

Test rejection of:

- missing active relation fingerprint;
- family member pointing to unknown relation;
- duplicate family IDs;
- representative outside its family;
- contrast relation also marked as auto-duplicate for same pair;
- manifest-version mismatch;
- family-synthesized `maximum_claim` field not copied from an existing member claim;
- alias suggestion that hides unique evidence.

Example:

```python
def test_validator_rejects_relation_loss(valid_payloads):
    valid_payloads["fingerprints"]["relations"].pop()
    errors = validate_payloads(ROOT, valid_payloads)
    assert any("fingerprint coverage" in error for error in errors)
```

- [ ] **Step 2: Run validator tests to verify RED**

```bash
python -m pytest -q tests/test_validate_bible_consolidation.py
```

Expected: fail because validator does not exist.

- [ ] **Step 3: Implement validator**

Expose:

```python
def validate_payloads(root: Path, payloads: dict[str, dict]) -> list[str]:
    ...
```

The CLI first regenerates/loads current active IDs and validates coverage and referential integrity. It must never modify source relations.

- [ ] **Step 4: Run validator tests to verify GREEN**

```bash
python -m pytest -q tests/test_validate_bible_consolidation.py
```

Expected: pass.

- [ ] **Step 5: Run real builder + validator**

```bash
python scripts/build_bible_consolidation.py
python scripts/validate_bible_consolidation.py
```

Expected: exit 0 and no loss of active relations.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_bible_consolidation.py tests/test_validate_bible_consolidation.py
git commit -m "test: enforce Bible consolidation invariants"
```

---

### Task 6: Add real-corpus acceptance checks proving tangible improvement

**Files:**
- Create: `tests/test_bible_consolidation_real_corpus.py`

**Interfaces:**
- Uses only public interfaces from Tasks 1–5.

- [ ] **Step 1: Add real-corpus acceptance tests**

The acceptance suite must prove all of the following against the current active manifest corpus:

```python
def test_real_corpus_has_no_relation_loss(): ...
def test_real_corpus_produces_at_least_one_duplicate_candidate(): ...
def test_real_corpus_has_mountain_family_with_distinct_functions(): ...
def test_real_corpus_keeps_yoke_learning_and_slavery_distinct(): ...
def test_real_corpus_groups_door_reversals_without_merging_them(): ...
def test_real_corpus_groups_stone_reversals_without_merging_them(): ...
def test_real_corpus_family_ids_and_representatives_are_order_stable(): ...
def test_real_corpus_duplicate_queue_preserves_unique_evidence(): ...
```

The test should use exact known relation IDs from Waves 32–35 where possible, not fuzzy assumptions.

- [ ] **Step 2: Run acceptance tests**

```bash
python -m pytest -q tests/test_bible_consolidation_real_corpus.py
```

Expected: pass. If no real duplicate candidate is found, do **not** weaken thresholds merely to satisfy the test. Instead inspect the corpus and either identify a genuine duplicate pair or change the success criterion to report zero duplicates honestly while retaining family/contrast improvements; record that design finding in the test name/comment.

- [ ] **Step 3: Run all consolidation tests**

```bash
python -m pytest -q tests/test_bible_consolidation.py tests/test_build_bible_consolidation.py tests/test_validate_bible_consolidation.py tests/test_bible_consolidation_real_corpus.py
```

Expected: pass.

- [ ] **Step 4: Commit**

```bash
git add tests/test_bible_consolidation_real_corpus.py
git commit -m "test: prove Bible consolidation on active corpus"
```

---

### Task 7: Integrate consolidation into the existing quality workflow

**Files:**
- Modify: `.github/workflows/quality-checks.yml`
- Create or Modify: `.gitignore` only if generated indexes follow existing ignored-generated-artifact convention.

**Interfaces:**
- CI step consumes builder/validator scripts.
- Existing Bible corpus/reader/static-dynamic parity steps remain in their current order after consolidation validation.

- [ ] **Step 1: Add workflow-contract test before editing workflow**

Add to `tests/test_bible_consolidation_real_corpus.py`:

```python
def test_quality_workflow_builds_and_validates_consolidation_before_reader():
    text = (ROOT / ".github/workflows/quality-checks.yml").read_text(encoding="utf-8")
    build = text.index("python scripts/build_bible_consolidation.py")
    validate = text.index("python scripts/validate_bible_consolidation.py")
    reader = text.index("python scripts/validate_bible_reader.py")
    assert build < validate < reader
```

- [ ] **Step 2: Run test to verify RED**

```bash
python -m pytest -q tests/test_bible_consolidation_real_corpus.py -k workflow
```

Expected: fail because workflow commands are absent.

- [ ] **Step 3: Add one CI step after Bible atlas corpus validation and before Bible reader validation**

```yaml
      - name: Build and validate Bible consolidation
        run: |
          python scripts/build_bible_consolidation.py
          python scripts/validate_bible_consolidation.py
```

Do not create a new workflow.

- [ ] **Step 4: Run workflow-contract test to verify GREEN**

```bash
python -m pytest -q tests/test_bible_consolidation_real_corpus.py -k workflow
```

Expected: pass.

- [ ] **Step 5: Run full Python test suite**

```bash
python -m pytest -q tests
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/quality-checks.yml tests/test_bible_consolidation_real_corpus.py
git commit -m "ci: validate Bible corpus consolidation"
```

---

### Task 8: Verify the whole repository and inspect the actual consolidation value

**Files:**
- Modify only if verification exposes a real bug; every fix requires its own failing regression test first.
- Update PR #184 description after successful verification.

**Interfaces:**
- Uses GitHub Actions `Repository quality checks` as authoritative whole-repo verification.

- [ ] **Step 1: Run local/branch-level deterministic checks**

```bash
python -m pytest -q tests
python scripts/build_bible_consolidation.py
python scripts/validate_bible_consolidation.py
```

Expected: all pass.

- [ ] **Step 2: Inspect generated intelligence for actual usefulness**

Record:

- active relation count;
- number of families;
- family size distribution;
- duplicate candidates;
- contrast candidates;
- ungrouped relations;
- Mountain family members/functions;
- Door family members/functions;
- Stone family members/functions;
- any alias recommendations and their unique-evidence status.

Reject/tune the implementation if it merely groups on common nouns, creates giant meaningless components, or produces no retrieval improvement.

- [ ] **Step 3: Run full repository quality workflow on exact head**

Authoritative check must include pytest, content integrity, Bible corpus, Bible reader, public site build, comparator compilation, static/dynamic parity, and the new consolidation builder/validator.

Expected: workflow conclusion `success` with zero failed required steps.

- [ ] **Step 4: Confirm no source relation loss by count and ID set**

Compare active relation IDs before and after consolidation integration. The sets must be identical because consolidation is derived-only.

- [ ] **Step 5: Update PR #184**

Document:

- consolidation is backend-only;
- original relations remain authoritative and untouched;
- exact relation count unchanged;
- actual family/duplicate/contrast counts;
- representative-selection rule;
- no auto-merge behavior;
- final successful workflow run number/head SHA.

- [ ] **Step 6: Stop before reader/UI changes**

Do not alter `build_bible_study.py`, `app/bible-study.js`, or public rendering in this plan. Reader integration requires a separate review after backend results demonstrate real value.
