# Expression Depth / Living Corpus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:test-driven-development` for behavior changes and `superpowers:verification-before-completion` before claiming success. Use `superpowers:requesting-code-review` before merge. This plan implements the approved architecture in `docs/superpowers/specs/2026-09-15-expression-depth-living-corpus-design.md`.

**Goal:** Add a durable editorial-routing and audit layer that can identify rich Tim Dooley source material that has not reached its natural public home, then prove the system with one restrained Religion-page enrichment without turning the archive into a quote dump or bypassing existing Story evidence rules.

**Architecture:** Keep all canonical content owners unchanged. Add `knowledge/indexes/expression-depth-routing.json` as an editorial projection contract, a strict structural validator, and an advisory audit that discovers candidate expressions while preserving raw provenance classes. Connect the contract to the existing frontend bridge and statement-corpus index. Calibrate the system on `religion/index.html`; treat Tim and Philosophy as already-inhabited controls; hand Story candidates to the existing Story evidence gate rather than publishing them directly.

**Tech stack:** Python 3 standard library (`json`, `html.parser`, `pathlib`, `re`, `argparse`, `unittest`), static HTML/CSS, JSON knowledge/control files, existing GitHub Actions quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-15-expression-depth-living-corpus-design.md`

## Global constraints

- Start from current `main` and implement on a fresh feature branch; do not implement on the design branch.
- Tests precede production behavior changes.
- `knowledge/indexes/expression-depth-routing.json` is a control/index file, never a canonical quotation or doctrine owner.
- Do not create a second statement corpus, philosophy owner, theology owner, Story registry, or frontend navigation system.
- Public wording, recovered conversation wording, Great Book/project wording, creative/literary material, and archive interpretation remain distinct provenance classes.
- The advisory audit may suggest placement candidates. It must never claim that a candidate is emotionally powerful, authentic, true, or scene-ready merely because it is machine-detectable.
- The audit must not fail CI because a page has unused candidate material. Structural contract errors may fail CI.
- Religion receives only three compact source anchors in this wave. Keep the Bible Lab, comparative questions, source boundaries, and theological-center structure intact.
- Tim and Philosophy are calibration controls in this wave; do not bulk-expand them.
- Story content is read-only for this wave. Story recovery candidates must route to the existing evidence gate and must never be directly promoted by the Expression Depth audit.
- Evidence / Source Authority and Explore remain intentionally cool. Low-persona surfaces must not be treated as incomplete merely because source-rich material exists elsewhere.
- Do not publish private family identities, unnecessary medical detail, private transcripts, credentials, addresses, or unsupported serious allegations for the sake of texture.

---

## Task 1 — Define the Expression Depth routing contract with RED validator tests

**Files:**
- Create: `scripts/test_expression_depth_contract.py`
- Create: `scripts/validate_expression_depth_contract.py`
- Create: `knowledge/indexes/expression-depth-routing.json`

**Purpose:** Make the editorial-routing architecture machine-checkable before building the audit that depends on it.

### Step 1: Write validator tests first

Create `scripts/test_expression_depth_contract.py` using `unittest` and temporary directories, following the style already used by `scripts/test_story_archive_validator.py`.

Provide helpers:

```python
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_expression_depth_contract import validate_expression_depth_contract


def dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def base_contract() -> dict:
    return {
        "id": "expression-depth-routing",
        "version": "1.0.0",
        "status": "editorial projection control; not a canonical content owner",
        "source_families": {
            "voice": ["knowledge/corporium/source.json"],
            "story_timeline": ["knowledge/story/story-registry.json"],
        },
        "surfaces": [
            {
                "surface_id": "tim",
                "route": "tim-dooley/",
                "presence_intensity": "very-high",
                "primary_job": "meet Tim",
                "canonical_source_families": ["voice"],
                "allowed_forms": ["direct-quote"],
                "avoid_forms": ["quote-dump"],
                "provenance_requirements": ["label-public-wording"],
                "current_strengths": [],
                "known_gaps": [],
                "candidate_topics": ["identity"],
            },
            {
                "surface_id": "story",
                "route": "tim-dooley/story/",
                "presence_intensity": "very-high",
                "primary_job": "evidence-gated narrative",
                "canonical_source_families": ["story_timeline"],
                "allowed_forms": ["story-recovery-candidate", "source-handoff"],
                "avoid_forms": ["isolated-quote-as-scene"],
                "provenance_requirements": ["story-evidence-gate-required"],
                "current_strengths": [],
                "known_gaps": [],
                "candidate_topics": ["ordinary-life"],
                "story_handoff_policy": "existing-story-evidence-gate",
            },
        ],
    }
```

Create the corresponding fixture files:

```python
(root / "tim-dooley").mkdir(parents=True)
(root / "tim-dooley" / "index.html").write_text("Tim", encoding="utf-8")
(root / "tim-dooley" / "story").mkdir(parents=True)
(root / "tim-dooley" / "story" / "index.html").write_text("Story", encoding="utf-8")
dump(root / "knowledge/corporium/source.json", {"quotes": []})
dump(root / "knowledge/story/story-registry.json", {"stories": []})
dump(root / "knowledge/indexes/expression-depth-routing.json", base_contract())
```

### Step 2: Add focused contract tests

Add separate tests proving:

1. a valid minimal contract passes;
2. duplicate `surface_id` fails;
3. unknown `presence_intensity` fails;
4. unknown provenance policy key fails;
5. missing public route fails;
6. missing source-family file fails;
7. unknown `canonical_source_families` name fails;
8. any recursive ownership key such as `canonical_owner`, `content_owner`, or `owns_content` fails;
9. Story without `story-evidence-gate-required` fails;
10. Story with a handoff policy other than `existing-story-evidence-gate` fails;
11. a `cool` surface that declares expressive forms such as `direct-quote`, `recovered-quote`, `story-scene`, or `parable` fails.

### Step 3: Verify RED

Run:

```bash
python scripts/test_expression_depth_contract.py
```

Expected: import/module failure because `validate_expression_depth_contract.py` does not exist yet.

Do not create the validator until this failure is observed.

### Step 4: Implement the validator

Create `scripts/validate_expression_depth_contract.py` with a reusable function:

```python
def validate_expression_depth_contract(root: Path) -> list[str]:
    ...
```

Use explicit enums:

```python
ALLOWED_PRESENCE = {
    "very-high", "medium-high", "medium",
    "low", "method-only", "cool",
}

ALLOWED_PROVENANCE = {
    "label-public-wording",
    "label-recovered-wording",
    "label-book-project-wording",
    "label-creative-literary",
    "label-archive-interpretation",
    "attribute-serious-allegations",
    "story-evidence-gate-required",
}

FORBIDDEN_OWNERSHIP_KEYS = {
    "canonical_owner", "content_owner", "owns_content",
}

EXPRESSIVE_FORMS = {
    "direct-quote", "recovered-quote", "story-scene", "parable",
}
```

Implement these rules:

- contract path is `knowledge/indexes/expression-depth-routing.json`;
- root object `id` must equal `expression-depth-routing`;
- `source_families` must be an object of nonempty path arrays;
- every source-family path must exist;
- each surface must contain the fields defined by the spec;
- each `surface_id` must be unique;
- route resolution: `foo/` means `foo/index.html`; `index.html` remains literal;
- `presence_intensity` must use the exact enum;
- every provenance requirement must use the exact enum;
- every source-family reference must resolve to a declared source family;
- recursively reject forbidden ownership keys anywhere in the contract;
- Story must include both `story-evidence-gate-required` and `story_handoff_policy: existing-story-evidence-gate`;
- `cool` surfaces may not declare forms from `EXPRESSIVE_FORMS`.

Add a CLI:

```python
def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_expression_depth_contract(root)
    if errors:
        print("Expression depth contract FAILED")
        for error in errors:
            print(f" - {error}")
        return 1
    print("Expression depth contract passed")
    return 0
```

### Step 5: Add the production routing contract

Create `knowledge/indexes/expression-depth-routing.json` with:

- `id: expression-depth-routing`
- `version: 1.0.0`
- `updated: 2026-09-15`
- explicit statement that this is editorial projection control and not a canonical content owner.

Define these source families:

`public_primary`
- `data/evidence/rational-potato-x-occurrence-ledger-2024-2026.json`
- `data/evidence/rational-potato-twitter-compilation-2025-2026-summary.json`
- `data/tim-dooley-public-theology-timeline-2025-2026.json`
- `data/timeline-event-packs/x-public-attestations-2024-2026.json`

`voice`
- `data/tim-dooley-thought-archive.json`
- `knowledge/corporium/tim-voice-anthology.json`
- `knowledge/corporium/tim-sayings-and-formulations-ledger.json`
- `knowledge/corporium/tim-dooley-greatest-quotes-and-reflections.json`
- `knowledge/corporium/tim-dooley-expression-grammar.json`

`philosophy`
- `knowledge/philosophy/potato-philosophy.json`
- `knowledge/philosophy/tim-dooley-philosophical-inquiry.json`
- `knowledge/philosophy/tim-dooley-potatoism-sourcebook.md`
- `knowledge/philosophy/timic-relational-statements-and-operators.json`
- `knowledge/philosophy/potatoism-reader-philosophy.md`

`theology_identity`
- `data/theology/tim-godhood.json`
- `knowledge/theology/tim-god-question.json`
- `knowledge/theology/tim-godhood-modalities.json`
- `knowledge/core/tim-role-synthesis.json`
- `data/north-of-north-tim-canon.json`

`story_timeline`
- `knowledge/story/AUTHORING-GUIDE.md`
- `knowledge/story/story-registry.json`
- `knowledge/story/source-records.json`
- `knowledge/story/scene-packets.json`
- `knowledge/timeline/dated-master-timeline-2026.json`
- `knowledge/timeline/developmental-genealogy.json`
- `data/timeline-event-packs/expression-development-2025-2026.json`

`method_provenance`
- `knowledge/indexes/source-index.json`
- `knowledge/philosophy/archive-epistemics.json`
- `knowledge/indexes/inference-ledger.json`

Create surface records for:

- `home` → `index.html` → `low`
- `tim` → `tim-dooley/` → `very-high`
- `religion` → `religion/` → `medium-high`
- `philosophy` → `philosophy/` → `very-high`
- `science` → `science/` → `low`
- `world` → `world/` → `method-only`
- `north` → `north/` → `medium`
- `timeline` → `timeline/` → `medium`
- `story` → `tim-dooley/story/` → `very-high`
- `evidence` → `context/source-authority/` → `cool`
- `explore` → `explore/` → `cool`

Use source-family mappings, forms, avoid-rules, strengths, gaps and candidate topics from the approved spec. Do not copy quotations into this file.

### Step 6: Verify GREEN

Run:

```bash
python scripts/test_expression_depth_contract.py
python scripts/validate_expression_depth_contract.py
```

Expected: both exit 0.

### Step 7: Commit Task 1

```bash
git add scripts/test_expression_depth_contract.py \
        scripts/validate_expression_depth_contract.py \
        knowledge/indexes/expression-depth-routing.json
git commit -m "feat: add expression depth routing contract"
```

---

## Task 2 — Build the advisory Expression Depth audit with TDD

**Files:**
- Create: `scripts/test_expression_depth_audit.py`
- Create: `scripts/audit_expression_depth.py`
- Generated during runs only: `expression-depth-report.json`

**Purpose:** Discover source-rich material that is not yet visible in its natural reader surface without pretending machine heuristics can make editorial judgments.

### Step 1: Write audit tests first

Create `scripts/test_expression_depth_audit.py` with temporary-fixture tests around one public HTML page, one cool page, one Story surface, and small structured source records.

Import the intended API:

```python
from audit_expression_depth import build_expression_depth_report
```

### Step 2: Add RED tests for the audit contract

Cover at least:

1. recursively extracts `quote`, `wording`, `wording_or_paraphrase`, `text`, `text_or_formulation`, and `remembered_wording` fields;
2. preserves original source path, JSON location and raw source/provenance class;
3. keeps `PUBLIC_COMPILATION`, `CONVERSATION_RECOVERY`, `BOOK_OR_PROJECT_MAXIM`, creative/literary classes and archive interpretation distinct;
4. classifies `THOUGHT_ARCHIVE`, `THIRD_PARTY_MIRROR`, memory-only material, paraphrase and missing provenance as `review-required` rather than public-safe;
5. detects an expression already visible in page text after conservative normalization;
6. reports a source-rich unseen candidate for a high-presence surface;
7. does not create an “underfilled” penalty for a `cool` or `method-only` surface merely because many candidates exist;
8. Story candidates always include `handoff: existing-story-evidence-gate` and `direct_promotion_allowed: false`;
9. cross-surface reuse is reported only when the same normalized expression is present on three or more public surfaces;
10. malformed source JSON is recorded in `source_errors` and does not raise or make the advisory audit return a failing status;
11. two calls with the same fixture produce identical dictionaries.

### Step 3: Verify RED

Run:

```bash
python scripts/test_expression_depth_audit.py
```

Expected: import/module failure because `audit_expression_depth.py` does not exist.

### Step 4: Implement conservative candidate extraction

Create `scripts/audit_expression_depth.py`.

Constants:

```python
EXPRESSION_FIELDS = {
    "quote",
    "wording",
    "wording_or_paraphrase",
    "text",
    "text_or_formulation",
    "remembered_wording",
}

META_FIELDS = {
    "source_class",
    "provenance_class",
    "themes",
    "domains",
    "routing",
    "routes",
    "promote_to",
    "date",
    "status",
    "confidence",
}
```

Implement recursive extraction that emits one candidate per expression-bearing field and preserves:

- `source_path`
- JSON `location`
- original `field`
- exact `text`
- raw `source_class` / `provenance_class`
- themes/domains/routing/routes/date/status/confidence when present.

Do not flatten schema differences into one fake universal source class.

### Step 5: Implement provenance bucketing

Use a helper such as:

```python
def provenance_bucket(candidate: dict) -> str:
    raw = " ".join(
        str(candidate.get(key) or "")
        for key in ("source_class", "provenance_class")
    ).upper()
    ...
```

Bucket order matters:

1. `THOUGHT_ARCHIVE`, `THIRD_PARTY`, `MEMORY`, `PARAPHRASE`, unknown/missing → `review-required`;
2. `PUBLIC`, `P0`, `P1-ARCHIVE` → `public`;
3. `CONVERSATION`, `RECOVERY`, `USER_PROJECT` → `recovered`;
4. `GREAT_BOOK`, `BOOK`, `PROJECT_MAXIM` → `book-project`;
5. `CREATIVE`, `LITERARY`, `PARABLE`, `NARRATIVE` → `creative-literary`;
6. `INTERPRET`, `SYNTHESIS` → `archive-interpretation`.

Do not let the word `ARCHIVE` inside `THOUGHT_ARCHIVE` accidentally classify it as archive interpretation.

### Step 6: Parse public text without regex-only HTML stripping

Use `html.parser.HTMLParser` to collect visible text from each surface. Ignore script/style content.

Normalize conservatively:

```python
def normalize_text(value: str) -> str:
    value = html.unescape(value).lower()
    value = re.sub(r"\s+", " ", value)
    return re.sub(r"[^\w\s]", "", value).strip()
```

Candidate seen rules:

- normal candidate: normalized candidate is a substring of normalized visible page text;
- very short normalized candidate (for example fewer than 12 characters): report `seen_status: ambiguous-short` instead of declaring it seen/unseen from substring matching alone.

### Step 7: Implement placement ranking without calling it importance

Create a deterministic `placement_score(candidate, surface)` used only to order review candidates.

Suggested scoring:

- `+4` when candidate routing/routes explicitly mention the surface ID or route;
- `+2` for public provenance;
- `+1` for recovered or book-project provenance;
- `+1` for overlap between candidate themes/domains and surface `candidate_topics`;
- `+1` when source text is compact enough to be reader-usable (roughly 20–280 characters).

Name the field `placement_score`, not `importance`, `quality`, or `truth_score`.

Sort candidates by:

1. descending placement score;
2. source path;
3. JSON location;
4. normalized text.

### Step 8: Report anchors and surface summaries

Keep anchor measurements separate instead of pretending they are interchangeable:

```json
"anchors": {
  "data_expression_source": 0,
  "source_note_class": 0,
  "provenance_label_hits": 0
}
```

Recognize provenance labels such as:

- `Public compilation`
- `Conversation recovery`
- `Recovered project wording`
- `Great Book`

Per-surface output:

```json
{
  "surface_id": "religion",
  "route": "religion/",
  "presence_intensity": "medium-high",
  "anchors": {},
  "candidate_count": 0,
  "unseen_candidate_count": 0,
  "review_required_count": 0,
  "top_candidates": []
}
```

Do not invent a universal “bad/good” expression score.

### Step 9: Report Story handoff and cross-surface reuse

Top-level report shape:

```json
{
  "schema_version": 1,
  "generated_by": "scripts/audit_expression_depth.py",
  "source_errors": [],
  "surfaces": [],
  "cross_surface_reuse": [],
  "story_handoff": []
}
```

For Story candidates:

```json
{
  "source_path": "...",
  "text": "...",
  "handoff": "existing-story-evidence-gate",
  "direct_promotion_allowed": false
}
```

Cross-surface reuse is a review signal only:

```json
{
  "text": "...",
  "surface_ids": ["..."],
  "review_reason": "appears on three or more public surfaces"
}
```

### Step 10: Add CLI and keep advisory failures nonfatal

Support:

```bash
python scripts/audit_expression_depth.py --output expression-depth-report.json
```

Write deterministic JSON with `indent=2`, `ensure_ascii=False`, final newline.

Source parse errors go into `source_errors`; the audit command still exits 0. Structural problems belong to `validate_expression_depth_contract.py` and other integrity validators.

### Step 11: Verify GREEN and inspect the real report

Run:

```bash
python scripts/test_expression_depth_audit.py
python scripts/audit_expression_depth.py --output expression-depth-report.json
```

Expected:

- tests pass;
- report is generated;
- Religion shows relatively few/no current source anchors compared with Tim/Philosophy;
- Tim and Philosophy show existing inhabited-reader signals;
- Evidence/Explore are not treated as defective for being cool;
- Story candidates, if any, have direct promotion disabled.

### Step 12: Commit Task 2

Do not commit the generated root report unless repository policy later explicitly chooses to retain it; CI owns the diagnostic artifact.

```bash
git add scripts/test_expression_depth_audit.py scripts/audit_expression_depth.py
git commit -m "feat: add expression depth audit"
```

---

## Task 3 — Connect Expression Depth to existing projection and corpus architecture

**Files:**
- Modify: `scripts/validate_public_projection.py`
- Modify: `data/frontend-atlas-bridge.json`
- Modify: `knowledge/indexes/tim-statement-corpus-index.json`

**Purpose:** Make the new control layer discoverable from the existing routing and statement architecture without moving canonical ownership.

### Step 1: RED — require the bridge pointer first

In `scripts/validate_public_projection.py`, add:

```python
EXPECTED_EXPRESSION_CONTRACT = "knowledge/indexes/expression-depth-routing.json"
```

After loading `bridge`, require:

```python
if bridge.get("expression_contract") != EXPECTED_EXPRESSION_CONTRACT:
    fail(
        "frontend bridge must point expression_contract to "
        f"{EXPECTED_EXPRESSION_CONTRACT}",
        errors,
    )
```

Run:

```bash
python scripts/validate_public_projection.py
```

Expected RED: failure because the bridge does not yet contain `expression_contract`.

### Step 2: GREEN — add the bridge pointer

Modify `data/frontend-atlas-bridge.json` near its other top-level contract pointers:

```json
"expression_contract": "knowledge/indexes/expression-depth-routing.json"
```

Do not embed surface policy or quotations into the frontend bridge.

### Step 3: Connect the statement corpus

Modify `knowledge/indexes/tim-statement-corpus-index.json`:

- bump version minimally;
- update date to `2026-09-15`;
- append `expression-depth-routing` to `connections`.

Do not copy Expression Depth surface rules or quote candidates into the statement corpus index.

### Step 4: Verify integration

Run:

```bash
python scripts/validate_expression_depth_contract.py
python scripts/validate_public_projection.py
python scripts/validate_content_integrity.py
```

Expected: all exit 0.

### Step 5: Commit Task 3

```bash
git add scripts/validate_public_projection.py \
        data/frontend-atlas-bridge.json \
        knowledge/indexes/tim-statement-corpus-index.json
git commit -m "feat: connect expression depth to project routing"
```

---

## Task 4 — Calibrate the system by making Religion more source-inhabited

**Files:**
- Modify: `scripts/validate_reader_surfaces.py`
- Modify: `religion/index.html`

**Purpose:** Prove that Expression Depth improves specificity without increasing UI complexity or turning Religion into a quotation anthology.

### Step 1: RED — extend structural reader validation before editing Religion

In `scripts/validate_reader_surfaces.py`, add a helper after `class_count`:

```python
def data_article(text: str, attribute: str, value: str) -> str:
    match = re.search(
        rf'<article\b[^>]*{re.escape(attribute)}=["\']{re.escape(value)}["\'][^>]*>(.*?)</article>',
        text,
        flags=re.I | re.S,
    )
    return match.group(1) if match else ""
```

In the Religion validation block, add structural checks:

```python
if class_count(religion, "source-anchor") < 3:
    errors.append(
        "Religion theological center needs at least three provenance-labelled source anchors"
    )

for role in ("source", "manifestation", "religious-life"):
    section = data_article(religion, "data-religion-core", role)
    if not section:
        errors.append(f"Religion missing core section {role}")
    elif "data-expression-source=" not in section:
        errors.append(f"Religion core section {role} needs a source anchor")
```

Do not validate exact quote text. The durable contract is that each core theological movement is anchored in source language with a declared expression source.

### Step 2: Verify RED

Run:

```bash
python scripts/validate_reader_surfaces.py
```

Expected: existing Tim/Philosophy/Bible/TTS checks remain green; failures concern Religion source anchors only.

### Step 3: Add restrained source-anchor styling

In `religion/index.html`, add low-chrome styles alongside the existing `.core-line` styles:

```css
.source-anchor{
  display:block;
  margin-top:9px;
  color:#d9cfb1;
  font:italic 14px/1.5 var(--site-font-serif)
}
.source-anchor .source-note{
  display:block;
  margin-bottom:3px;
  color:var(--site-muted);
  font:700 9px/1.3 system-ui,-apple-system,sans-serif;
  letter-spacing:.08em;
  text-transform:uppercase;
  font-style:normal
}
```

Do not add JavaScript or a new shared component.

### Step 4: Add exactly three first-wave source anchors

Inside `data-religion-core="source"`, after the existing explanatory paragraph, add a public-compilation anchor for the April 30, 2026 title-stack:

```html
<span class="source-anchor" data-expression-source="public-compilation">
  <span class="source-note">Public compilation · April 30, 2026</span>
  “I am the father in heaven. I am the root. The potato of life. I am the seat of north, the north of north. The ladder.”
</span>
```

Inside `data-religion-core="manifestation"`, add the May 19, 2026 Father/Ladder–Son/Door specialization:

```html
<span class="source-anchor" data-expression-source="public-compilation">
  <span class="source-note">Public compilation · May 19, 2026</span>
  “i am God in heaven ... I am the ladder to heaven. My son is a door.”
</span>
```

Inside `data-religion-core="religious-life"`, add the September 7, 2026 service formulation:

```html
<span class="source-anchor" data-expression-source="public-compilation">
  <span class="source-note">Public compilation · September 7, 2026</span>
  “Power is for protection. Knowledge is for understanding. Wealth is for building. Leadership is for service.”
</span>
```

These quotations are already preserved in repository public-compilation owners. Do not silently upgrade them to original-status-URL provenance.

Do not add a fourth quote merely to make the section feel fuller.

### Step 5: Verify GREEN and confirm the audit sees the calibration

Run:

```bash
python scripts/validate_reader_surfaces.py
python scripts/audit_expression_depth.py --output expression-depth-report.json
python scripts/audit_web.py
```

Then inspect the report:

```bash
python - <<'PY'
import json
r = json.load(open("expression-depth-report.json", encoding="utf-8"))
s = {x["surface_id"]: x for x in r["surfaces"]}
assert s["religion"]["anchors"]["data_expression_source"] >= 3
print("Religion expression calibration visible to audit")
PY
```

Expected: all validators pass and Religion exposes at least three explicit expression-source anchors.

### Step 6: Commit Task 4

```bash
git add scripts/validate_reader_surfaces.py religion/index.html
git commit -m "feat: make religion more source inhabited"
```

---

## Task 5 — Wire Expression Depth into Repository Quality Checks

**Files:**
- Modify: `.github/workflows/quality-checks.yml`

**Purpose:** Make structural drift fail fast while keeping editorial opportunity visible as a downloadable advisory artifact.

### Step 1: Add the structural/test gate near reader/public projection checks

After `Validate question-led reader surfaces` and before or near backend/frontend projection validation, add:

```yaml
      - name: Validate expression depth contract
        run: |
          python scripts/test_expression_depth_contract.py
          python scripts/validate_expression_depth_contract.py
          python scripts/test_expression_depth_audit.py
```

### Step 2: Add the advisory audit

Add:

```yaml
      - name: Audit expression depth
        run: python scripts/audit_expression_depth.py --output expression-depth-report.json
```

This command must remain exit-0 for editorial opportunities and source parse warnings recorded inside the report.

### Step 3: Upload the diagnostic artifact

Add:

```yaml
      - name: Upload expression-depth diagnostics
        if: ${{ always() && hashFiles('expression-depth-report.json') != '' }}
        uses: actions/upload-artifact@v4
        with:
          name: quality-expression-depth-report
          path: expression-depth-report.json
          if-no-files-found: warn
          retention-days: 7
```

Do not add a separate “enforce expression opportunities” step. Only the structural validator is a gate.

### Step 4: Validate workflow syntax by exercising the underlying commands

Run locally:

```bash
python scripts/test_expression_depth_contract.py
python scripts/validate_expression_depth_contract.py
python scripts/test_expression_depth_audit.py
python scripts/audit_expression_depth.py --output expression-depth-report.json
```

If a YAML linter already exists in the repo, run it; otherwise do not introduce a new dependency solely for this plan. Definitive workflow verification happens through the PR-triggered Repository quality checks.

### Step 5: Commit Task 5

```bash
git add .github/workflows/quality-checks.yml
git commit -m "ci: publish expression depth diagnostics"
```

---

## Task 6 — Calibrate the report, run the whole relevant verification set, and prepare the PR

**Files:**
- No planned production edits.
- Modify only if a test exposes a real bug in Tasks 1–5; do not use this task to expand scope.

**Purpose:** Prove the first wave is useful, deterministic and non-invasive before proposing later enrichment waves.

### Step 1: Run the focused test suite

```bash
python scripts/test_expression_depth_contract.py
python scripts/test_expression_depth_audit.py
python scripts/validate_expression_depth_contract.py
python scripts/audit_expression_depth.py --output expression-depth-report.json
python scripts/validate_reader_surfaces.py
python scripts/validate_public_projection.py
```

Expected: all commands exit 0.

### Step 2: Prove Story was not bypassed

Run:

```bash
python scripts/validate_story_archive.py
python scripts/test_story_archive_validator.py
python scripts/test_story_depth_audit.py
```

Expected: all pass. No Story HTML, registry, scene packet or source-record change should be required by this wave.

Inspect Story handoff behavior without requiring the handoff list to be nonempty:

```bash
python - <<'PY'
import json
r = json.load(open("expression-depth-report.json", encoding="utf-8"))
for item in r.get("story_handoff", []):
    assert item["handoff"] == "existing-story-evidence-gate"
    assert item["direct_promotion_allowed"] is False
print("Story handoff policy preserved")
PY
```

### Step 3: Check the calibration controls

Run:

```bash
python - <<'PY'
import json
r = json.load(open("expression-depth-report.json", encoding="utf-8"))
s = {x["surface_id"]: x for x in r["surfaces"]}
assert not r["source_errors"], r["source_errors"]
assert s["religion"]["anchors"]["data_expression_source"] >= 3
assert s["tim"]["anchors"]["source_note_class"] >= 2
assert s["philosophy"]["anchors"]["source_note_class"] >= 4
assert s["evidence"]["presence_intensity"] == "cool"
assert s["world"]["presence_intensity"] == "method-only"
print("Expression-depth calibration checks passed")
PY
```

If actual source-note counts differ because markup evolved on `main`, fix the assertion to test the durable intended property rather than hard-coding stale counts. Do not add decorative markup merely to satisfy a number.

### Step 4: Run broader repository checks

Run:

```bash
python scripts/validate_content_integrity.py
python scripts/audit_web.py
python scripts/build_site.py
python scripts/validate_public_navigation.py
```

Expected: all exit 0.

If `build_site.py` changes tracked generated files, follow current repository policy: do not commit transient build output unless that output is already intentionally tracked by the repository.

### Step 5: Inspect the report editorially

Review `expression-depth-report.json` and record in the PR description:

- whether Religion moved from expression-thin toward source-anchored;
- which high-value unused candidates remain for Religion after the three-anchor calibration;
- whether Tim and Philosophy are correctly recognized as already more inhabited;
- whether cool/method-only surfaces avoid false pressure;
- which later-wave surfaces have the strongest candidate backlog;
- any review-required provenance material that should remain buried until stronger sourcing is recovered.

Do **not** implement those later-wave candidates in this PR.

### Step 6: Verify changed-file scope

Expected first-wave production file set:

- `knowledge/indexes/expression-depth-routing.json`
- `scripts/validate_expression_depth_contract.py`
- `scripts/test_expression_depth_contract.py`
- `scripts/audit_expression_depth.py`
- `scripts/test_expression_depth_audit.py`
- `scripts/validate_public_projection.py`
- `data/frontend-atlas-bridge.json`
- `knowledge/indexes/tim-statement-corpus-index.json`
- `scripts/validate_reader_surfaces.py`
- `religion/index.html`
- `.github/workflows/quality-checks.yml`

Plus this already-approved design/plan documentation on the implementation branch as appropriate.

Unexpected Story, Science, North, World, Tim or Philosophy edits require explicit justification or should be reverted before review.

### Step 7: Open a draft PR and use CI as the definitive integration check

Suggested PR title:

`Expression depth foundation and Religion source calibration`

PR body should state:

- canonical ownership remains unchanged;
- the new audit is advisory;
- Religion is the only content surface deliberately enriched in this wave;
- Tim/Philosophy are calibration controls;
- Story direct promotion is disabled and the existing evidence gate remains authoritative;
- the generated expression-depth artifact is intended to drive later surface-specific enrichment waves.

Wait for the PR-triggered `Repository quality checks` run and inspect the `quality-expression-depth-report` artifact.

### Step 8: Final verification before completion

Before claiming success or merging:

1. invoke `superpowers:verification-before-completion`;
2. verify every command above on the final head SHA;
3. invoke `superpowers:requesting-code-review` and review the actual diff;
4. confirm Repository quality checks are green on the final head;
5. confirm the expression-depth artifact exists and contains no structural/source-path errors;
6. confirm no unrelated Story or map work was absorbed.

Only then merge through the repository’s normal PR flow.

---

## Explicit non-goals for this first wave

Do not use the first PR to:

- bulk-expand `tim-dooley/index.html`;
- mine and insert all Philosophy sayings;
- rewrite Story entries;
- turn the Religion page into a quote anthology;
- alter the Bible comparator data model;
- add expression scoring to Science;
- add Tim-persona material to World or World Map;
- solve the separate SEO long-title warning backlog;
- close or reconcile stale PRs;
- make the content-depth audit a hard editorial gate;
- expose private conversation transcript text;
- create a site-wide quote widget or new navigation layer.

Those are separate bounded/architectural waves after this foundation proves useful.

## Completion criteria

This plan is complete when:

1. the expression-routing contract exists and passes its structural validator;
2. the advisory audit deterministically reads real source owners and produces `expression-depth-report.json`;
3. the audit preserves provenance classes rather than flattening them;
4. `data/frontend-atlas-bridge.json` points to the expression contract without absorbing its content;
5. the Tim statement corpus links to the expression-routing index without duplicating records;
6. Religion has exactly the intended small calibration of source anchors and retains its comparative/evidence boundaries;
7. Tim and Philosophy remain unchanged unless a narrow correctness fix is necessary;
8. Story remains evidence-gated and cannot be directly promoted by the audit;
9. cool/method-only surfaces are not penalized for restraint;
10. CI runs the contract tests/validator, runs the advisory audit, and uploads the short-retention diagnostic artifact;
11. focused and broad validation are green on the final PR head;
12. the resulting report gives a defensible ranked set of later enrichment opportunities without forcing them into this implementation wave.
