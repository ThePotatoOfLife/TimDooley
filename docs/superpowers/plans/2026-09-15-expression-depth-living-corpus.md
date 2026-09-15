# Expression Depth / Living Corpus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:test-driven-development` for behavior changes and `superpowers:verification-before-completion` before claiming success. Use `superpowers:requesting-code-review` before merge.

**Goal:** Add a durable editorial-routing and audit layer that finds rich Tim Dooley source material that has not reached its natural public home, then prove the system with one restrained Religion-page enrichment.

**Architecture:** Canonical owners remain unchanged. Add `knowledge/indexes/expression-depth-routing.json` as editorial projection control, a hard structural validator, and an advisory audit. Connect the contract to the frontend bridge and Tim statement-corpus index. Calibrate on `religion/index.html`; treat Tim and Philosophy as already-inhabited controls; send Story candidates to the existing Story evidence gate instead of publishing them directly.

**Spec:** `docs/superpowers/specs/2026-09-15-expression-depth-living-corpus-design.md`

## Global constraints

- Implement on a fresh feature branch from current `main`, not on this design branch.
- Tests precede production behavior changes.
- The routing contract never owns quotations, doctrine, philosophy, chronology, or Story facts.
- Public, recovered-conversation, Great Book/project, creative/literary, and archive-interpretation classes remain distinct.
- The audit suggests placement only. It must never score authenticity, emotional power, truth, beauty, or Story scene-readiness.
- Editorial opportunity never fails CI; malformed routing/ownership/provenance structure may fail CI.
- Religion receives exactly three deliberate first-wave source anchors. Tim and Philosophy are not bulk-expanded.
- Story files are read-only in this wave. Story candidates always hand off to the existing evidence gate.
- Evidence / Source Authority and Explore remain intentionally cool; World remains method-first.
- Private or sensitive material is not promoted for texture.
- **Diagnostic output is internal-only.** Write the report to `archive/reports/expression-depth-report.json`; `build_site.py` already excludes the top-level `archive/` tree, preventing accidental publication in GitHub Pages.

---

## Task 1 — Routing contract and structural validator (TDD)

**Create:**
- `scripts/test_expression_depth_contract.py`
- `scripts/validate_expression_depth_contract.py`
- `knowledge/indexes/expression-depth-routing.json`

### 1.1 RED tests

Follow the temporary-directory `unittest` style used by `scripts/test_story_archive_validator.py`.

Expose:

```python
from validate_expression_depth_contract import validate_expression_depth_contract
```

Build a minimal fixture containing `tim-dooley/index.html`, `tim-dooley/story/index.html`, source files, and `knowledge/indexes/expression-depth-routing.json`.

Add separate tests for:

1. valid minimal contract passes;
2. duplicate `surface_id` fails;
3. invalid `presence_intensity` fails;
4. unknown provenance policy fails;
5. missing public route fails;
6. missing source-family path fails;
7. undeclared source-family reference fails;
8. recursive ownership keys (`canonical_owner`, `content_owner`, `owns_content`) fail;
9. Story without `story-evidence-gate-required` fails;
10. Story handoff other than `existing-story-evidence-gate` fails;
11. a `cool` surface declaring `direct-quote`, `recovered-quote`, `story-scene`, or `parable` fails.

Run:

```bash
python scripts/test_expression_depth_contract.py
```

Expected RED: import/module failure because the validator does not exist.

### 1.2 GREEN validator

Implement:

```python
def validate_expression_depth_contract(root: Path) -> list[str]:
    ...
```

Enums:

```python
ALLOWED_PRESENCE = {
    "very-high", "medium-high", "medium", "low", "method-only", "cool",
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
FORBIDDEN_OWNERSHIP_KEYS = {"canonical_owner", "content_owner", "owns_content"}
EXPRESSIVE_FORMS = {"direct-quote", "recovered-quote", "story-scene", "parable"}
```

Rules:

- contract path is `knowledge/indexes/expression-depth-routing.json`;
- root `id == "expression-depth-routing"`;
- `source_families` is an object of nonempty repository-path arrays;
- every path exists, regardless of extension;
- each surface contains the spec fields and unique `surface_id`;
- `foo/` routes resolve to `foo/index.html`; literal HTML paths remain literal;
- source-family names must resolve;
- provenance/intensity values must use enums;
- recursively reject ownership keys;
- Story requires the evidence-gate provenance key and exact handoff policy;
- cool surfaces cannot require expressive forms.

CLI exits 1 only for structural errors.

### 1.3 Production routing contract

Create source families:

- `public_primary`: X occurrence ledger, Twitter compilation, public theology timeline, X public-attestations pack.
- `voice`: thought archive, voice anthology, sayings ledger, greatest-quotes, expression grammar.
- `philosophy`: canonical Potato philosophy, philosophical inquiry, philosophy sourcebook, relational statements/operators, reader philosophy.
- `theology_identity`: Tim Godhood, Tim-God question, Godhood modalities, Tim role synthesis, North-of-North canon.
- `story_timeline`: Story authoring guide, Story registry/source records/scene packets, dated master timeline, developmental genealogy, expression-development pack.
- `method_provenance`: source index, archive epistemics, inference ledger.

Create surface entries:

| surface | route | intensity |
|---|---|---|
| home | `index.html` | low |
| tim | `tim-dooley/` | very-high |
| religion | `religion/` | medium-high |
| philosophy | `philosophy/` | very-high |
| science | `science/` | low |
| world | `world/` | method-only |
| north | `north/` | medium |
| timeline | `timeline/` | medium |
| story | `tim-dooley/story/` | very-high |
| evidence | `context/source-authority/` | cool |
| explore | `explore/` | cool |

Use the approved spec for `allowed_forms`, `avoid_forms`, provenance requirements, strengths, gaps, and candidate topics. **Do not copy quotations into this file.**

Verify:

```bash
python scripts/test_expression_depth_contract.py
python scripts/validate_expression_depth_contract.py
```

Commit:

```bash
git add scripts/test_expression_depth_contract.py scripts/validate_expression_depth_contract.py knowledge/indexes/expression-depth-routing.json
git commit -m "feat: add expression depth routing contract"
```

---

## Task 2 — Advisory expression audit (TDD)

**Create:**
- `scripts/test_expression_depth_audit.py`
- `scripts/audit_expression_depth.py`

**Generated, never committed:**
- `archive/reports/expression-depth-report.json`

### 2.1 RED tests

Expose:

```python
from audit_expression_depth import build_expression_depth_report
```

Fixture tests must prove:

1. recursive extraction of `quote`, `wording`, `wording_or_paraphrase`, `text`, `text_or_formulation`, `remembered_wording`;
2. preservation of source path, JSON location, original field, raw source/provenance class;
3. public / recovered / book-project / creative-literary / archive-interpretation remain distinct;
4. `THOUGHT_ARCHIVE`, `THIRD_PARTY_MIRROR`, memory-only, paraphrase, or missing provenance become `review-required`;
5. visible-page detection works after conservative normalization;
6. high-presence unseen candidates are reported;
7. cool/method-only surfaces do not receive an “underfilled” penalty;
8. Story candidates carry `handoff: existing-story-evidence-gate` and `direct_promotion_allowed: false`;
9. cross-surface reuse is reported only at 3+ surfaces;
10. malformed **JSON** source is recorded under `source_errors` without raising;
11. `.md`/other non-JSON source owners are recorded as non-structured sources and **not** treated as parse errors;
12. repeated runs return identical dictionaries.

Run:

```bash
python scripts/test_expression_depth_audit.py
```

Expected RED: import/module failure.

### 2.2 Candidate extraction

Constants:

```python
EXPRESSION_FIELDS = {
    "quote", "wording", "wording_or_paraphrase", "text",
    "text_or_formulation", "remembered_wording",
}
META_FIELDS = {
    "source_class", "provenance_class", "themes", "domains", "routing",
    "routes", "promote_to", "date", "status", "confidence",
}
```

For `.json` source-family paths, recursively emit candidates preserving:

- `source_path`
- JSON `location`
- original expression field
- exact text
- raw source/provenance class
- nearby themes/domains/routing/routes/date/status/confidence.

For `.md`, `.html`, or other non-JSON canonical owners in source families:

- validate existence via Task 1;
- add them to a top-level `non_structured_sources` list;
- **skip automatic candidate extraction in wave 1**;
- do not put them in `source_errors`.

This keeps the audit honest instead of pretending Markdown prose has the same schema as structured corpus records.

### 2.3 Provenance buckets

Use conservative ordered matching:

1. `THOUGHT_ARCHIVE`, `THIRD_PARTY`, `MEMORY`, `PARAPHRASE`, unknown/missing → `review-required`;
2. `PUBLIC`, `P0`, `P1-ARCHIVE` → `public`;
3. `CONVERSATION`, `RECOVERY`, `USER_PROJECT` → `recovered`;
4. `GREAT_BOOK`, `BOOK`, `PROJECT_MAXIM` → `book-project`;
5. `CREATIVE`, `LITERARY`, `PARABLE`, `NARRATIVE` → `creative-literary`;
6. `INTERPRET`, `SYNTHESIS` → `archive-interpretation`.

The order prevents `THOUGHT_ARCHIVE` from becoming archive interpretation merely because it contains the word `ARCHIVE`.

### 2.4 Visible-text parsing and matching

Use `html.parser.HTMLParser`; ignore script/style text.

```python
def normalize_text(value: str) -> str:
    value = html.unescape(value).lower()
    value = re.sub(r"\s+", " ", value)
    return re.sub(r"[^\w\s]", "", value).strip()
```

- normal candidate: normalized candidate substring in normalized page text → visible;
- very short candidate (<12 normalized characters) → `ambiguous-short`, not a confident seen/unseen classification.

### 2.5 Placement ordering, not importance scoring

Use `placement_score` only:

- +4 if explicit routing/routes mention the surface ID/route;
- +2 public provenance;
- +1 recovered or book-project provenance;
- +1 candidate theme/domain overlaps surface `candidate_topics`;
- +1 if text length is roughly 20–280 characters.

Sort by score desc, then source path, JSON location, normalized text. Never call this truth, quality, authenticity, or importance.

### 2.6 Report shape

Keep anchor measures separate:

```json
"anchors": {
  "data_expression_source": 0,
  "source_note_class": 0,
  "provenance_label_hits": 0
}
```

Top-level:

```json
{
  "schema_version": 1,
  "generated_by": "scripts/audit_expression_depth.py",
  "source_errors": [],
  "non_structured_sources": [],
  "surfaces": [],
  "cross_surface_reuse": [],
  "story_handoff": []
}
```

Story items always include:

```json
{
  "handoff": "existing-story-evidence-gate",
  "direct_promotion_allowed": false
}
```

### 2.7 CLI / internal-only output

Support:

```bash
python scripts/audit_expression_depth.py --output archive/reports/expression-depth-report.json
```

The script creates parent directories as needed and writes deterministic UTF-8 JSON with a final newline. JSON parse problems are advisory `source_errors`; command remains exit 0. Structural contract errors belong to the validator.

Verify:

```bash
python scripts/test_expression_depth_audit.py
python scripts/audit_expression_depth.py --output archive/reports/expression-depth-report.json
```

Inspect that Religion is relatively source-thin while Tim/Philosophy already expose source-note signals; Evidence/Explore are not penalized; Story direct promotion is disabled.

Commit only scripts:

```bash
git add scripts/test_expression_depth_audit.py scripts/audit_expression_depth.py
git commit -m "feat: add expression depth audit"
```

---

## Task 3 — Connect to existing routing and corpus architecture

**Modify:**
- `scripts/validate_public_projection.py`
- `data/frontend-atlas-bridge.json`
- `knowledge/indexes/tim-statement-corpus-index.json`

### 3.1 RED projection contract

Add:

```python
EXPECTED_EXPRESSION_CONTRACT = "knowledge/indexes/expression-depth-routing.json"
```

Require `bridge.get("expression_contract")` to equal that path.

Run:

```bash
python scripts/validate_public_projection.py
```

Expected RED: bridge pointer missing.

### 3.2 GREEN architecture links

Add to `data/frontend-atlas-bridge.json`:

```json
"expression_contract": "knowledge/indexes/expression-depth-routing.json"
```

Do not place surface policy or quotes in the bridge.

In `knowledge/indexes/tim-statement-corpus-index.json`:

- minimally bump version;
- update date to `2026-09-15`;
- append `expression-depth-routing` to `connections` only.

Verify:

```bash
python scripts/validate_expression_depth_contract.py
python scripts/validate_public_projection.py
python scripts/validate_content_integrity.py
```

Commit:

```bash
git add scripts/validate_public_projection.py data/frontend-atlas-bridge.json knowledge/indexes/tim-statement-corpus-index.json
git commit -m "feat: connect expression depth to project routing"
```

---

## Task 4 — Religion source calibration

**Modify:**
- `scripts/validate_reader_surfaces.py`
- `religion/index.html`

### 4.1 RED semantic contract

Add a helper that extracts an `<article>` by data attribute without freezing prose:

```python
def data_article(text: str, attribute: str, value: str) -> str:
    match = re.search(
        rf'<article\b[^>]*{re.escape(attribute)}=["\']{re.escape(value)}["\'][^>]*>(.*?)</article>',
        text,
        flags=re.I | re.S,
    )
    return match.group(1) if match else ""
```

In Religion validation:

```python
if class_count(religion, "source-anchor") < 3:
    errors.append("Religion theological center needs at least three provenance-labelled source anchors")

for role in ("source", "manifestation", "religious-life"):
    section = data_article(religion, "data-religion-core", role)
    if not section:
        errors.append(f"Religion missing core section {role}")
    elif "data-expression-source=" not in section:
        errors.append(f"Religion core section {role} needs a source anchor")
```

Run:

```bash
python scripts/validate_reader_surfaces.py
```

Expected RED: Religion source-anchor failures only.

### 4.2 Add restrained styling

Add low-chrome `.source-anchor` and nested `.source-note` styling to `religion/index.html`; no JS, carousel, component framework, or navigation change.

### 4.3 Add exactly three source anchors

Under `data-religion-core="source"`:

> Public compilation · April 30, 2026  
> “I am the father in heaven. I am the root. The potato of life. I am the seat of north, the north of north. The ladder.”

Under `data-religion-core="manifestation"`:

> Public compilation · May 19, 2026  
> “i am God in heaven ... I am the ladder to heaven. My son is a door.”

Under `data-religion-core="religious-life"`:

> Public compilation · September 7, 2026  
> “Power is for protection. Knowledge is for understanding. Wealth is for building. Leadership is for service.”

Each wrapper uses:

```html
<span class="source-anchor" data-expression-source="public-compilation">
  <span class="source-note">...</span>
  ...
</span>
```

These are repository-preserved public-compilation formulations; do not imply original status URLs have been recovered.

Do not add a fourth quote in this wave.

### 4.4 GREEN / calibration

Run:

```bash
python scripts/validate_reader_surfaces.py
python scripts/audit_expression_depth.py --output archive/reports/expression-depth-report.json
python scripts/audit_web.py
```

Then:

```bash
python - <<'PY'
import json
p = "archive/reports/expression-depth-report.json"
r = json.load(open(p, encoding="utf-8"))
s = {x["surface_id"]: x for x in r["surfaces"]}
assert s["religion"]["anchors"]["data_expression_source"] >= 3
print("Religion expression calibration visible to audit")
PY
```

Commit:

```bash
git add scripts/validate_reader_surfaces.py religion/index.html
git commit -m "feat: make religion more source inhabited"
```

---

## Task 5 — CI integration without public leakage

**Modify:** `.github/workflows/quality-checks.yml`

Near reader/public projection checks add:

```yaml
      - name: Validate expression depth contract
        run: |
          python scripts/test_expression_depth_contract.py
          python scripts/validate_expression_depth_contract.py
          python scripts/test_expression_depth_audit.py

      - name: Audit expression depth
        run: python scripts/audit_expression_depth.py --output archive/reports/expression-depth-report.json

      - name: Upload expression-depth diagnostics
        if: ${{ always() && hashFiles('archive/reports/expression-depth-report.json') != '' }}
        uses: actions/upload-artifact@v4
        with:
          name: quality-expression-depth-report
          path: archive/reports/expression-depth-report.json
          if-no-files-found: warn
          retention-days: 7
```

There is **no** “enforce expression opportunities” step.

Because the report lives under `archive/`, `scripts/build_site.py` excludes it from `_site`. Add a focused verification after site build in Task 6 rather than relying on assumption.

Run locally:

```bash
python scripts/test_expression_depth_contract.py
python scripts/validate_expression_depth_contract.py
python scripts/test_expression_depth_audit.py
python scripts/audit_expression_depth.py --output archive/reports/expression-depth-report.json
```

Commit:

```bash
git add .github/workflows/quality-checks.yml
git commit -m "ci: publish expression depth diagnostics"
```

---

## Task 6 — Final verification, report calibration, draft PR

No planned production edits. Fix only real bugs exposed by verification; do not broaden scope.

### 6.1 Focused checks

```bash
python scripts/test_expression_depth_contract.py
python scripts/test_expression_depth_audit.py
python scripts/validate_expression_depth_contract.py
python scripts/audit_expression_depth.py --output archive/reports/expression-depth-report.json
python scripts/validate_reader_surfaces.py
python scripts/validate_public_projection.py
```

All must exit 0.

### 6.2 Story non-bypass proof

```bash
python scripts/validate_story_archive.py
python scripts/test_story_archive_validator.py
python scripts/test_story_depth_audit.py
```

Then:

```bash
python - <<'PY'
import json
r = json.load(open("archive/reports/expression-depth-report.json", encoding="utf-8"))
for item in r.get("story_handoff", []):
    assert item["handoff"] == "existing-story-evidence-gate"
    assert item["direct_promotion_allowed"] is False
print("Story handoff policy preserved")
PY
```

### 6.3 Calibration controls

```bash
python - <<'PY'
import json
r = json.load(open("archive/reports/expression-depth-report.json", encoding="utf-8"))
s = {x["surface_id"]: x for x in r["surfaces"]}
assert not r["source_errors"], r["source_errors"]
assert s["religion"]["anchors"]["data_expression_source"] >= 3
assert s["evidence"]["presence_intensity"] == "cool"
assert s["world"]["presence_intensity"] == "method-only"
# Tim/Philosophy are controls: require evidence of existing source/provenance
# signals, but do not hard-code decorative counts that could force markup bloat.
assert (
    s["tim"]["anchors"]["source_note_class"] > 0
    or s["tim"]["anchors"]["provenance_label_hits"] > 0
)
assert (
    s["philosophy"]["anchors"]["source_note_class"] > 0
    or s["philosophy"]["anchors"]["provenance_label_hits"] > 0
)
print("Expression-depth calibration checks passed")
PY
```

### 6.4 Broader repo checks and leak test

```bash
python scripts/validate_content_integrity.py
python scripts/audit_web.py
python scripts/build_site.py
python scripts/validate_public_navigation.py
test ! -e _site/archive/reports/expression-depth-report.json
test ! -e _site/expression-depth-report.json
```

All must exit 0. The last two commands explicitly prove the internal diagnostic did not enter the public artifact.

### 6.5 Editorial report review

Review `archive/reports/expression-depth-report.json` and record in the PR description:

- Religion’s post-calibration anchor state;
- high-value unused Religion candidates remaining after the three-anchor cap;
- whether Tim/Philosophy are correctly recognized as already inhabited;
- whether cool/method-only surfaces avoid false pressure;
- later-wave candidate backlogs;
- review-required material that should remain buried until provenance improves;
- non-structured canonical sources skipped by the first structured extractor.

Do not implement those later-wave candidates in this PR.

### 6.6 Expected changed-file scope

Production files should be limited to:

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

Plus approved design/plan docs on the implementation branch as appropriate.

Unexpected Story, Science, North, World, Tim, or Philosophy edits require explicit justification or should be reverted.

### 6.7 Draft PR

Suggested title:

`Expression depth foundation and Religion source calibration`

PR body must state:

- canonical ownership is unchanged;
- audit is advisory;
- Religion is the only deliberately enriched reader surface in wave 1;
- Tim/Philosophy are controls;
- Story direct promotion is disabled and existing Story evidence gate remains authoritative;
- report artifact is internal-only and excluded from Pages;
- report drives later surface-specific waves.

Use the PR-triggered `Repository quality checks` as definitive integration verification and inspect the `quality-expression-depth-report` artifact.

### 6.8 Completion gate

Before merge/claiming success:

1. invoke `superpowers:verification-before-completion`;
2. rerun focused + broad checks on final head;
3. invoke `superpowers:requesting-code-review` and review actual diff;
4. verify Repository quality checks green on final SHA;
5. verify expression-depth artifact exists with no structural/source-path errors;
6. verify no diagnostic report is present in `_site`;
7. verify no unrelated Story/map work was absorbed.

Only then merge through normal PR flow.

---

## Explicit non-goals for wave 1

Do not:

- bulk-expand Tim or Philosophy;
- rewrite Story entries;
- turn Religion into a quote anthology;
- alter Bible comparator data model;
- add persona material to Science, World, or World Map;
- solve the separate SEO long-title backlog;
- close/reconcile stale PRs;
- turn content-depth or expression-depth opportunity into a hard editorial gate;
- publish private transcript bodies;
- add a site-wide quote widget or new navigation layer.

## Completion criteria

Wave 1 is complete when:

1. expression-routing contract exists and validates;
2. advisory audit deterministically reads structured canonical owners while explicitly skipping non-structured owners from automatic extraction;
3. provenance classes remain distinct;
4. frontend bridge points to the contract without absorbing content;
5. Tim statement corpus links to the routing index without duplicating records;
6. Religion has the intended three source anchors and preserves comparative/evidence boundaries;
7. Tim/Philosophy remain stable controls;
8. Story can only receive handoff candidates, never direct audit promotion;
9. cool/method-only surfaces are not penalized for restraint;
10. CI validates structure, runs the advisory audit, and uploads the internal artifact;
11. the report is provably absent from the public Pages artifact;
12. focused and broad checks are green on the final PR head;
13. the report gives a defensible ranked backlog for later enrichment waves without forcing them into this PR.
