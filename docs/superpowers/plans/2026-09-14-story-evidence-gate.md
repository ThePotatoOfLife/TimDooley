# Story Evidence Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:test-driven-development` for behavior changes and `superpowers:verification-before-completion` before claiming success. This plan is designed for isolated execution on `story-evidence-gate-20260914`.

**Goal:** Replace HTML-length-based “full story” promotion with a validated evidence pipeline so conversation stories are only promoted when ordered source material supports an actual scene, while fragments/anecdotes remain useful without being mislabeled.

**Architecture:** Keep the existing chronological public reader. Add canonical source records, ordered scene packets, a Story registry, a deterministic depth audit, and a validator gate. Start in `migration` mode: registered stories are enforced strictly while legacy unregistered stories are reported rather than breaking CI. Move to `strict` only after complete registration.

**Tech stack:** Python 3 standard library (`json`, `html.parser`, `pathlib`, `unittest`), JSON knowledge owners, existing static Story HTML, GitHub Actions quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-14-story-evidence-gate-design.md`

## Global constraints

- Work only on `story-evidence-gate-20260914` until the implementation is verified.
- Tests precede production behavior changes.
- Do not publish complete private transcript bodies in repository JSON.
- Archaeology summaries and statement ledgers are discovery/index sources, never sufficient by themselves for documentary `SCENE` or `TRANSCRIPT_DEPTH`.
- Public labels remain `MAIN STORY` and `SIDE STORY`; evidence depth stays mostly backend metadata.
- No automatic deletion of existing prose. Downgrading means removing an unjustified `Hear the full story` claim and recording a recovery target.
- Religious, mythic and divine statements in recovered conversations remain participant/project claims, not narrator assertions.

---

## Task 1 — Define the validator contract with failing tests

**Files:**
- Modify: `scripts/test_story_archive_validator.py`
- Later modify: `scripts/validate_story_archive.py`

**Purpose:** Make the desired evidence gate executable before adding the implementation.

### Step 1: Build a fixture helper

Create a helper in `scripts/test_story_archive_validator.py` that writes the minimal archive needed by each test:

```python
def write_base_archive(root: Path, *, enforcement="migration") -> Path:
    story = root / "knowledge" / "story"
    story.mkdir(parents=True)
    (root / "story-content").mkdir(parents=True)
    (story / "cast-book.json").write_text(json.dumps({
        "cast": [{"id": "tim", "class": "person"}]
    }), encoding="utf-8")
    (story / "arc-season-map.json").write_text(json.dumps({"arcs": []}), encoding="utf-8")
    (story / "source-records.json").write_text(json.dumps({
        "schema_version": 1, "sources": []
    }), encoding="utf-8")
    (story / "scene-packets.json").write_text(json.dumps({
        "schema_version": 1, "scenes": []
    }), encoding="utf-8")
    (story / "story-registry.json").write_text(json.dumps({
        "schema_version": 1, "enforcement": enforcement, "stories": []
    }), encoding="utf-8")
    return story
```

### Step 2: Add focused RED tests

Add separate tests for:

1. `ANECDOTE` registered with `full_story_allowed: true` and HTML `full-story` → validation failure.
2. `TRANSCRIPT_DEPTH` with `consecutive_transcript`, valid ordered scene beats and `full-story` → passes.
3. `TRANSCRIPT_DEPTH` backed only by `archaeology_summary` → failure.
4. `SCENE` missing `ending_state` or valid `ending_status` → failure.
5. `LITERARY_COMPLETE` + `great_book_literary_text` + full-story → passes.
6. missing source reference → failure.
7. missing scene reference → failure.
8. duplicate registry story ID → failure.
9. `private_source_no_quote` carrying `public_excerpt` → failure.
10. beat `public_text` from `private_source_no_quote` / `internal_recovery_only` → failure.
11. non-increasing beat sequence → failure.
12. registry path missing → failure.
13. `migration` mode permits unregistered legacy HTML entries.
14. `strict` mode rejects unregistered HTML entries.
15. duplicate Story IDs across HTML fragments → failure in strict mode and for registered collisions in migration mode.

Use real temporary HTML such as:

```html
<article class="story-entry" data-story-type="side" id="story-1">
  <time datetime="2026-03-02">2 March 2026</time>
  <details class="full-story"><summary>Hear the full story</summary></details>
</article>
```

### Step 3: Verify RED

Run:

```bash
python scripts/test_story_archive_validator.py
```

Expected: new tests fail because current `validate_story_archive.py` does not understand source records, scene packets, registry depth, privacy, HTML promotion, or enforcement mode.

Do not implement until these failures are observed.

### Step 4: Commit test contract

```bash
git add scripts/test_story_archive_validator.py
git commit -m "test: define Story evidence gate contract"
```

---

## Task 2 — Implement schema validation and promotion rules

**Files:**
- Modify: `scripts/validate_story_archive.py`

### Step 1: Add enum constants

Implement explicit allowed sets:

```python
ALLOWED_SOURCE_CLASSES = {
    "consecutive_transcript", "public_chat_transcript", "public_thread",
    "public_post_sequence", "single_recovered_turn", "isolated_quote_recovery",
    "later_autobiographical_retelling", "great_book_literary_text",
    "creative_artifact", "archaeology_summary", "statement_ledger",
    "external_documentary_source",
}
ALLOWED_CONTINUITY = {"consecutive", "partially_consecutive", "isolated", "retrospective", "literary"}
ALLOWED_PUBLIC_STATUS = {
    "public_source", "public_safe_excerpt", "private_source_public_safe_excerpt",
    "private_source_no_quote", "internal_recovery_only",
}
ALLOWED_DEPTH = {"FRAGMENT", "ANECDOTE", "SCENE", "TRANSCRIPT_DEPTH", "LITERARY_COMPLETE"}
ALLOWED_MODES = {"documentary", "literary", "mixed"}
ALLOWED_MIGRATION_STATUS = {"unclassified", "classified", "packetized", "verified"}
ALLOWED_ENDING_STATUS = {"resolved", "explicitly_unresolved"}
ALLOWED_BEAT_KINDS = {
    "exact_turn", "near_verbatim_turn", "public_post", "documented_action",
    "artifact_created", "later_retelling_context", "narrative_bridge",
}
QUALIFYING_DOCUMENTARY_SOURCES = {
    "consecutive_transcript", "public_chat_transcript", "public_thread",
    "public_post_sequence", "external_documentary_source", "creative_artifact",
}
```

### Step 2: Parse public Story HTML deterministically

Use `html.parser.HTMLParser`, not regex-only parsing, to discover every `.story-entry` article and whether a `details.full-story` occurs inside it. Return records containing:

- `id`
- source file path
- `data-story-type`
- `data-story-depth` / `data-story-mode` if present
- `datetime`
- `has_full_story`

Scan `story-content/*.html` recursively/non-recursively as the current archive requires.

### Step 3: Validate source records

For every source:

- require unique nonempty `id`;
- validate source class, continuity and public status;
- require `locator` object;
- enforce `public_excerpt is None` for `private_source_no_quote` and `internal_recovery_only`;
- require `public_excerpt_reviewed: true` when `private_source_public_safe_excerpt` carries a non-null excerpt;
- do not require raw transcript text in the repo.

### Step 4: Validate scene packets

For every scene:

- unique nonempty `id` and `story_id`;
- all `source_ids` resolve;
- all `cast` IDs resolve;
- required opening/problem/ending fields exist;
- `ending_status` allowed;
- `ordered_beats` is nonempty for `SCENE`/`TRANSCRIPT_DEPTH` use;
- `seq` values strictly increase;
- each beat source resolves;
- beat kind allowed;
- beat source locator present for exact/near-verbatim turns;
- `public_text` forbidden when source status forbids quotation.

### Step 5: Validate registry

For every story:

- unique `id`;
- path exists;
- mode, depth, story type, migration status allowed;
- source/scene references resolve;
- `full_story_allowed` equals the depth/mode policy:

```python
def depth_allows_full_story(mode: str, depth: str) -> bool:
    if mode == "literary":
        return depth == "LITERARY_COMPLETE"
    return depth in {"SCENE", "TRANSCRIPT_DEPTH"}
```

- documentary/mixed `SCENE` and `TRANSCRIPT_DEPTH` require at least one qualifying documentary source;
- `TRANSCRIPT_DEPTH` requires consecutive/partially consecutive source and multiple same-source ordered beats;
- archaeology/ledger-only backing fails scene-depth promotion;
- literary complete requires `great_book_literary_text` source;
- registered HTML article must exist exactly once and its `full-story` presence must agree with `full_story_allowed`;
- if HTML declares `data-story-depth`/`data-story-mode`, it must match registry.

### Step 6: Enforce migration vs strict

- `migration`: do not fail merely because a public Story entry is not registered. Still fail duplicate IDs and all violations involving registered entries.
- `strict`: every discovered public Story entry must be registered exactly once.

### Step 7: Verify GREEN

Run:

```bash
python scripts/test_story_archive_validator.py
```

Expected: all validator tests pass.

Then run current archive validator against the branch before canonical JSON owners exist; if it fails only for their intentional absence, proceed immediately to Task 3 in the same implementation batch rather than weakening the contract.

### Step 8: Commit validator

```bash
git add scripts/validate_story_archive.py
git commit -m "feat: enforce Story evidence depth rules"
```

---

## Task 3 — Add canonical owners in migration mode

**Files:**
- Create: `knowledge/story/source-records.json`
- Create: `knowledge/story/scene-packets.json`
- Create: `knowledge/story/story-registry.json`

Start deliberately empty:

```json
{"schema_version": 1, "sources": []}
```

```json
{"schema_version": 1, "scenes": []}
```

```json
{"schema_version": 1, "enforcement": "migration", "stories": []}
```

### Step 1: Add files

Do not add fake calibration records yet; calibration comes only after raw context is actually read.

### Step 2: Validate empty migration architecture

Run:

```bash
python scripts/test_story_archive_validator.py
python scripts/validate_story_archive.py
```

Expected: tests pass and archive validation passes because migration mode permits unregistered legacy Story entries.

### Step 3: Commit owners

```bash
git add knowledge/story/source-records.json knowledge/story/scene-packets.json knowledge/story/story-registry.json
git commit -m "feat: add canonical Story evidence owners"
```

---

## Task 4 — Build deterministic Story depth audit with TDD

**Files:**
- Create: `scripts/test_story_depth_audit.py`
- Create: `scripts/build_story_depth_audit.py`
- Generated: `knowledge/story/story-depth-audit.json`

### Step 1: RED — audit tests first

Create fixture archive tests asserting deterministic output for:

- total Story entries;
- MAIN/SIDE counts;
- registered/unregistered counts;
- depth counts;
- mode counts;
- HTML full-story count;
- qualified full-story count;
- incorrectly promoted registered full stories;
- unregistered full-story IDs separately, because migration mode cannot yet call them depth-qualified;
- unresolved source locators;
- recovery priority entries for registered ANECDOTE/FRAGMENT stories carrying `recovery_targets`;
- enforcement state.

Define public function:

```python
def build_story_depth_audit(root: Path) -> dict:
    ...
```

and deterministic writer:

```python
def write_story_depth_audit(root: Path) -> Path:
    data = build_story_depth_audit(root)
    out = root / "knowledge/story/story-depth-audit.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
```

### Step 2: Verify RED

```bash
python scripts/test_story_depth_audit.py
```

Expected: import/module failure because production audit script does not exist.

### Step 3: GREEN — implement minimal audit

Reuse the public Story scanner from `validate_story_archive.py` rather than maintaining a second parser. Audit does not decide depth from prose; it reports registry truth and HTML facts.

Suggested output shape:

```json
{
  "schema_version": 1,
  "enforcement": "migration",
  "published": {"total": 0, "main": 0, "side": 0},
  "registry": {"registered": 0, "unregistered": 0},
  "modes": {"documentary": 0, "literary": 0, "mixed": 0},
  "depths": {
    "FRAGMENT": 0,
    "ANECDOTE": 0,
    "SCENE": 0,
    "TRANSCRIPT_DEPTH": 0,
    "LITERARY_COMPLETE": 0
  },
  "full_story": {
    "html_total": 0,
    "qualified_registered": 0,
    "incorrectly_promoted_registered": [],
    "unregistered_full_story": []
  },
  "unresolved_source_locators": [],
  "recovery_priorities": []
}
```

### Step 4: Verify GREEN + determinism

```bash
python scripts/test_story_depth_audit.py
python scripts/build_story_depth_audit.py
cp knowledge/story/story-depth-audit.json /tmp/story-audit.json
python scripts/build_story_depth_audit.py
cmp /tmp/story-audit.json knowledge/story/story-depth-audit.json
```

Expected: tests pass and `cmp` exits 0.

### Step 5: Commit audit engine

```bash
git add scripts/test_story_depth_audit.py scripts/build_story_depth_audit.py knowledge/story/story-depth-audit.json
git commit -m "feat: add deterministic Story depth audit"
```

---

## Task 5 — Calibrate the taxonomy on five deliberately different evidence shapes

**Files:**
- Modify: `knowledge/story/source-records.json`
- Modify: `knowledge/story/scene-packets.json`
- Modify: `knowledge/story/story-registry.json`
- Modify selected `story-content/*.html`

### Calibration A — true conversation sequence

Use Library `Indsatte text(3).txt` (`file_00000000ce2471f491506cccbeaa4069`) because it demonstrably contains contiguous `@PotatoOfLife` / `@ASunofJesus` dialogue.

Before writing repo records:

1. use exact phrase search (`my sons name is TWIN`, `you still cant point to what i got wrong`) to locate the range;
2. read the contiguous block, including material before and after the central dispute;
3. record only locator/range and publication-safe excerpts in repo JSON;
4. preserve participants' religious claims as claims.

Expected classification: `TRANSCRIPT_DEPTH` if the contiguous range contains enough ordered back-and-forth; otherwise `SCENE`. Do not force the higher label.

If there is no matching existing public Story entry, create a **calibration-only scene packet** first but do not publish a new Story solely to satisfy the test. A registry entry is only for an actual published Story article.

### Calibration B — second long transcript candidate

Mine one concrete scene from `Indsatte text(2).txt` (`file_00000000f08871f4abe6c6d4460ebe90`). Do not classify the whole 14k-line dump. Find one contiguous episode with:

- a clear user problem/question;
- model response;
- user correction/follow-up;
- changed direction or ending.

Use it to prove the source/scene layer can represent a raw transcript without copying the whole transcript into GitHub.

### Calibration C — known anecdote overpromotion

Register `spiritual-bank-day-2026-03-02` from `story-content/2026-03-02-spiritual-bank-day.html` as `documentary / ANECDOTE` unless contiguous conversation context has been recovered by this point.

Because ANECDOTE cannot be a full story:

- remove `<details class="full-story">` / `Hear the full story`;
- preserve useful prose as ordinary paragraphs under the article;
- add `data-story-depth="anecdote" data-story-mode="documentary"`;
- record `recovery_targets: ["Recover contiguous surrounding conversation turns for 2 March 2026"]`.

This is the first visible proof that the gate corrects previous overclaiming instead of merely adding metadata.

### Calibration D — literary complete

Use a direct Great Book chapter already preserved in `great-book/chapters/` as `great_book_literary_text`. Prefer a Story entry whose source maps directly to a chapter file; if no existing full-story Story maps cleanly, register a literary candidate without adding a fake public Story. The validator test fixture already proves LITERARY_COMPLETE logic; the live calibration should only use a real mapping.

### Calibration E — fragment

Register `stream-on-x-2025-01-23` from `story-content/2025-ordinary-public-diary.html` as `documentary / FRAGMENT`, backed by its dated public-post compilation. Add `data-story-depth="fragment" data-story-mode="documentary"`. It remains a useful Story card and does not need full-story treatment.

### Step: Validate calibration

Run:

```bash
python scripts/test_story_archive_validator.py
python scripts/test_story_depth_audit.py
python scripts/validate_story_archive.py
python scripts/build_story_depth_audit.py
```

Expected: all pass. Audit now contains real registered entries in several depth classes and reports the remaining legacy inventory as unregistered.

### Step: Commit calibration

```bash
git add knowledge/story/source-records.json knowledge/story/scene-packets.json knowledge/story/story-registry.json knowledge/story/story-depth-audit.json story-content/
git commit -m "story: calibrate evidence depth on real sources"
```

---

## Task 6 — First full inventory and honest migration report

**Files:**
- Modify: `scripts/build_story_depth_audit.py` only if real archive structure exposes a parser edge case, with test first.
- Modify: `knowledge/story/story-registry.json`
- Modify: `knowledge/story/story-depth-audit.json`

### Step 1: Inventory every public article

Use the audit scanner to enumerate all `.story-entry` records across `story-content/*.html`.

For the first migration pass, do **not** fabricate evidence classifications for all entries. Populate registry entries where classification is directly recoverable from existing source notes; otherwise register them with:

- conservative `depth` (`FRAGMENT` or `ANECDOTE` when scene evidence is not established);
- `migration_status: unclassified` only if evidence mode itself is unresolved;
- explicit recovery targets.

A safe rule for current `full-story` entries is: if no ordered packet and qualifying source has been built yet, they may be registered as `ANECDOTE` and then HTML must be downgraded, or remain temporarily unregistered in migration mode while they are queued. Prefer queueing first rather than mass-destructively stripping prose in one commit.

### Step 2: Prioritize current full-story entries

Produce a migration report grouping existing expandable stories into:

- transcript/scene evidence already recoverable;
- literary-complete candidates;
- anecdote likely overpromotions;
- source unresolved.

The audit JSON is machine-readable. Add a concise human control note only if needed; do not duplicate the whole registry in Markdown.

### Step 3: Do not switch to strict yet

`story-registry.json` remains:

```json
"enforcement": "migration"
```

until zero public articles remain unregistered.

### Step 4: Commit first inventory wave

```bash
git add knowledge/story/story-registry.json knowledge/story/story-depth-audit.json
git commit -m "story: inventory published entries for evidence migration"
```

---

## Task 7 — Make the authoring workflow impossible to misunderstand

**Files:**
- Modify: `knowledge/story/AUTHORING-GUIDE.md`

Add a compact section immediately after the scene-first rules:

### Evidence gate before prose

- `FRAGMENT`: a clue; short card only.
- `ANECDOTE`: event known but sequence missing; never “Hear the full story.”
- `SCENE`: ordered action/reaction evidence; eligible.
- `TRANSCRIPT_DEPTH`: contiguous exchange; preferred for conversation-derived stories.
- `LITERARY_COMPLETE`: complete authored literature; eligible but explicitly literary.

Then state the mandatory workflow:

> Search summaries to locate the source. Read the contiguous raw source. Build/update the source record. Build the ordered scene packet. Only then write a full Story.

And the prohibition:

> An archaeology summary, statement ledger or memory synthesis may suggest where to dig. It is not a substitute for the transcript when claiming transcript depth.

### Verify

No code test is required for prose-only guide text, but run Story validation afterward to ensure no accidental JSON/HTML change occurred in the same commit.

### Commit

```bash
git add knowledge/story/AUTHORING-GUIDE.md
git commit -m "docs: require evidence packets before full Story prose"
```

---

## Task 8 — Add the Story gate to repository CI

**Files:**
- Modify: `.github/workflows/quality-checks.yml`

### Step 1: Add quality step after Python setup / near other archive validators

```yaml
      - name: Validate Story evidence architecture
        run: |
          python scripts/test_story_archive_validator.py
          python scripts/test_story_depth_audit.py
          python scripts/validate_story_archive.py
          python scripts/build_story_depth_audit.py --check
```

Implement `--check` in the audit script with a test first: build in memory and compare to committed `story-depth-audit.json`; exit nonzero on drift instead of rewriting CI checkout.

### Step 2: RED/GREEN for `--check`

Add audit tests for:

- committed matching report → exit/return success;
- stale report → failure.

Then implement the CLI flag.

### Step 3: Local verification

```bash
python scripts/test_story_archive_validator.py
python scripts/test_story_depth_audit.py
python scripts/validate_story_archive.py
python scripts/build_story_depth_audit.py
python scripts/build_story_depth_audit.py --check
```

Expected: all exit 0.

### Step 4: Commit CI gate

```bash
git add scripts/test_story_depth_audit.py scripts/build_story_depth_audit.py .github/workflows/quality-checks.yml knowledge/story/story-depth-audit.json
git commit -m "ci: enforce Story evidence gate"
```

---

## Task 9 — Repository-wide verification and PR

### Step 1: Run focused Story suite

```bash
python scripts/test_story_archive_validator.py
python scripts/test_story_depth_audit.py
python scripts/validate_story_archive.py
python scripts/build_story_depth_audit.py --check
```

All must exit 0.

### Step 2: Run relevant existing repository checks

At minimum:

```bash
python scripts/validate_repo_hygiene.py
python scripts/validate_content_integrity.py
python scripts/validate_architecture_layers.py
python scripts/build_site.py
```

If any failure is caused by the Story changes, fix it before PR. If a pre-existing unrelated failure appears, document it with command/output rather than masking it.

### Step 3: Inspect generated/public artifact

Confirm:

- no private transcript body has been added to `_site` or public JSON;
- Story reader still loads all fragments;
- calibrated ANECDOTE no longer says `Hear the full story`;
- registered depth metadata matches HTML;
- migration audit reports honest unregistered/full-story counts.

### Step 4: Compare branch with main

```bash
git diff --stat main...HEAD
git diff --name-status main...HEAD
```

Connector equivalent: `compare_commits(base="main", head="story-evidence-gate-20260914")`.

Expected scope: spec + plan + Story evidence JSON owners + Story validator/tests + audit/tests + selected calibration HTML + authoring guide + quality workflow. No unrelated map/Bible/history branch files.

### Step 5: Open PR

Title:

`Make Story depth evidence-driven`

PR body should state:

- the previous `full-story` HTML tag no longer defines completeness;
- migration mode is intentionally non-destructive;
- registered stories are already gated;
- raw private transcripts are not published;
- first calibration demonstrates fragment/anecdote/scene/transcript/literary distinctions;
- strict mode is a later migration milestone, not enabled prematurely.

### Step 6: Verify PR checks before merge

Do not merge merely because the PR is mergeable. Confirm the Story test/validator step and repository quality checks are green, then merge the branch into `main` through the PR.

---

## Definition of done for this implementation wave

This wave is complete when all of the following are true:

- canonical source/scene/registry owners exist;
- validator tests prove the promotion/privacy/enforcement rules;
- audit script deterministically reports real Story depth state;
- at least one real transcript sequence is packetized from raw Library material;
- at least one known anecdote overpromotion is corrected visibly;
- one fragment is explicitly classified without being inflated;
- literary evidence is represented separately from documentary evidence;
- authoring guide requires packet-before-full-prose;
- CI runs the evidence gate;
- migration mode remains active until the entire Story inventory is registered;
- branch verification and PR checks pass before any merge to `main`.
