# Concrete Culture Field Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an evidence-backed concrete Culture field that projects named formations, human trajectories, events, flows and pathways into `/context/culture/` without collapsing unlike social forms or weakening source/legal/privacy boundaries.

**Architecture:** Keep canonical knowledge in `knowledge/culture/concrete-culture-field-atlas.json` plus a source ledger. Validate those files independently, then render a static HTML projection into the built Culture page through `scripts/project_public_culture_field.py`, invoked from the existing post-build ontology pipeline. Public validation checks the rendered contract and TTS remains inherited from `.culture-page`.

**Tech Stack:** Python 3 standard library, JSON, static HTML, existing GitHub Pages build and quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-17-concrete-culture-field-design.md`

## Global Constraints

- Culture, subculture, cult/high-control formation, gang, movement, NGO, criminal network, fandom, anti-fandom, platform, institution and mainstream culture are not synonyms.
- Shared audience or adjacency is not proof of common command or coordination.
- Every externally testable atlas claim must resolve to source-ledger IDs.
- Criminal/legal claims must expose their legal/evidence status; aggregate police statistics must not be attributed to named groups unless the source does so.
- Named human cases require a strong public basis and privacy notes; no private addresses/contact data or incidental family data.
- `lolcow` may appear only as an attributed audience/internet-cultural label, never as an intrinsic person type.
- Public HTML is a projection, not a second canonical database.
- The projector is fail-closed if the Culture page or insertion anchor is missing.

---

### Task 1: Regression contract first

**Files:**
- Create: `scripts/test_concrete_culture_field.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: the approved spec.
- Produces: a source-data/public-projection contract that must fail before implementation exists.

- [ ] **Step 1: Write the failing test**

Create a Python test/contract script that requires:

```python
ATLAS = ROOT / "knowledge/culture/concrete-culture-field-atlas.json"
LEDGER = ROOT / "knowledge/culture/concrete-culture-source-ledger.json"
PROJECTOR = ROOT / "scripts/project_public_culture_field.py"

REQUIRED_TOP_LEVEL = (
    "formations", "human_cases", "events", "flows",
    "relationships", "pathways", "case_groups", "public_projection",
)
REQUIRED_CASE_IDS = {
    "loyal-to-familia", "otf-grimm-violence-as-a-service", "nxivm",
    "kiwi-farms", "online-snark-communities", "hip-hop",
    "medecins-sans-frontieres", "icrc",
}
REQUIRED_HUMAN_CASE_IDS = {"ghyslain-raza-star-wars-kid"}
```

It must fail if canonical files/projector are absent, source refs dangle, human cases lack `public_basis`/`privacy_notes`, money flows omit currency/period, or a record stores `lolcow` as a formation/person type.

- [ ] **Step 2: Wire the test into CI**

Add a quality step before `Build public site`:

```yaml
      - name: Validate concrete Culture field
        run: python scripts/test_concrete_culture_field.py
```

- [ ] **Step 3: Verify RED**

Open/update the feature PR and confirm the quality workflow fails specifically because the atlas/ledger/projector are missing.

- [ ] **Step 4: Commit**

Commit message: `test: require concrete culture field atlas`

---

### Task 2: Canonical source ledger and first corpus

**Files:**
- Create: `knowledge/culture/concrete-culture-source-ledger.json`
- Create: `knowledge/culture/concrete-culture-field-atlas.json`

**Interfaces:**
- Produces source IDs consumed by every externally testable atlas record.
- Atlas is consumed by `scripts/project_public_culture_field.py`.

- [ ] **Step 1: Build the source ledger**

Seed official/scholarly sources for Danish Police 2025 rocker/gang reporting; Danish Supreme Court LTF judgment; Europol OTF GRIMM and VaaS role-chain reporting; DOJ NXIVM conviction/sentencing; Cloudflare 2022 Kiwi Farms block; 2026 New Media & Society snark study; NFB Ghyslain Raza documentary; Smithsonian hip-hop history/canon material; MSF 2025 finances; ICRC 2025 finances.

Each source record must include:

```json
{
  "id": "source-id",
  "title": "...",
  "publisher": "...",
  "url": "https://...",
  "publication_date": "YYYY-MM-DD or YYYY",
  "accessed": "2026-09-17",
  "source_class": "official_record|court_record|scholarly|first_party_financial|institutional_history",
  "claim_scope": "...",
  "limitations": "..."
}
```

- [ ] **Step 2: Seed formations**

Include at minimum LTF, the Danish police conflict field, OTF GRIMM/VaaS, NXIVM, Kiwi Farms, online snark communities, hip-hop, MSF and ICRC. Other Danish conflict counterpart names may be lightweight formation records where needed for relationship integrity.

- [ ] **Step 3: Seed human trajectory**

Add `ghyslain-raza-star-wars-kid` with the public/private distinction and the pathway:

```text
private recording -> publication by other students -> viral label/remix culture ->
persistent digital identity -> later documentary participation/reclamation
```

Do not reproduce humiliating media or private details.

- [ ] **Step 4: Seed events, flows and relationships**

Include:

```text
Danish 2025 environment statistics (aggregate only)
LTF court dissolution/legal status
VaaS instigator -> recruiter -> enabler -> perpetrator
Cloudflare -> blocks -> Kiwi Farms (2022)
Bronx hip-hop scene -> mass/global culture -> Smithsonian preservation/canon
MSF private-source funding -> MSF operations
ICRC donor mix -> ICRC operations
```

- [ ] **Step 5: Run contract until GREEN for canonical data**

`python scripts/test_concrete_culture_field.py` should now fail only on the missing projector/public projection portion.

- [ ] **Step 6: Commit**

Commit message: `feat: add concrete culture evidence atlas`

---

### Task 3: Static Culture projector

**Files:**
- Create: `scripts/project_public_culture_field.py`
- Modify: `scripts/patch_public_ontology.py`

**Interfaces:**
- Consumes: `load_atlas() -> dict`, `load_sources() -> dict[str, dict]` from local JSON files.
- Produces: `render_concrete_culture_field(atlas, sources) -> str` and `project_culture_field() -> None`.

- [ ] **Step 1: Extend the contract for projector behavior**

The test must create a temporary/minimal Culture HTML fixture containing `<h2>Culture is multidimensional</h2>`, run the projector helper, and assert exactly one `data-culture-field` section with these headings:

```text
Who is actually here?
Where violence actually appears
Follow the flows
People behind the labels
How a formation changes type
Concrete Tree of Strife
```

It must also assert idempotence.

- [ ] **Step 2: Verify RED**

Run `python scripts/test_concrete_culture_field.py` and confirm the projector assertions fail because functions do not yet exist.

- [ ] **Step 3: Implement minimal projector**

Use only standard-library `html`, `json`, and `pathlib`. Escape all data. Render source links from the ledger. Insert before `<h2>Culture is multidimensional</h2>`. Abort with `SystemExit` if the target page, anchor, atlas or ledger is missing. If `data-culture-field` already exists, do nothing.

- [ ] **Step 4: Hook into post-build pipeline**

In `scripts/patch_public_ontology.py` import and call `project_culture_field()` before `patch_public_navigation()`.

- [ ] **Step 5: Verify GREEN**

Run the contract script; canonical and projector tests pass.

- [ ] **Step 6: Commit**

Commit message: `feat: project concrete culture field into public reader`

---

### Task 4: Public contract and reader integration

**Files:**
- Modify: `scripts/validate_public_navigation.py`
- Optionally modify: `context/culture/index.html` only if a stable source-level explanatory bridge is needed; do not duplicate the generated case database.

**Interfaces:**
- Consumes built `_site/context/culture/index.html` after `patch_public_ontology.py`.
- Produces regression errors when concrete Culture projection disappears or loses required source/TTS structure.

- [ ] **Step 1: Add built-page assertions**

Require:

```text
data-culture-field
Who is actually here?
Where violence actually appears
Follow the flows
People behind the labels
How a formation changes type
Concrete Tree of Strife
```

Also require the existing `culture-tts` host and source links inside the concrete section.

- [ ] **Step 2: Preserve semantic distinctions in public copy**

The projection must explicitly state that a named conflict edge does not assign aggregate police statistics to every group, and that the examples are contrastive rather than morally equivalent.

- [ ] **Step 3: Commit**

Commit message: `test: guard concrete culture public projection`

---

### Task 5: End-to-end verification and landing

**Files:**
- No new production files unless verification reveals a defect.

**Interfaces:**
- Consumes all prior tasks.
- Produces a merge-ready feature branch.

- [ ] **Step 1: Open/update pull request**

Create a PR from `feat/concrete-culture-field` to `main` with a description that distinguishes sourced external facts from project-analysis language.

- [ ] **Step 2: Run full repository quality workflow**

Expected: the complete Repository quality checks workflow passes, including the new concrete Culture test, build, ontology/projector pass, TTS/public navigation validation and site-shell validation.

- [ ] **Step 3: Inspect the built contract through CI results**

If quality fails, fetch the failing job/step logs, fix root cause, and re-run before landing.

- [ ] **Step 4: Verify branch diff**

Confirm changes are limited to the approved Culture feature, its tests, source corpus, projection integration and docs.

- [ ] **Step 5: Merge/fast-forward only after green verification**

Do not claim completion before the successful workflow is observed on the final commit.
