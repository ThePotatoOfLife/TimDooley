# Potatoism Philosophy Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich the Potatoism philosophy canon, long-form reader source, public Philosophy journey, and validation so the project expresses a coherent operational philosophy without creating a rival canon or bloating the public page.

**Architecture:** Keep `knowledge/philosophy/potato-philosophy.json` as canonical owner, use `knowledge/philosophy/potatoism-reader-philosophy.md` for full derivation, retain `tim-dooley-potatoism-sourcebook.md` as provenance-aware support, and project a selective eight-stage journey through `philosophy/index.html`. Extend the existing `scripts/validate_potatoism_philosophy_projection.py` contract rather than introducing a parallel validator.

**Tech Stack:** JSON knowledge records, Markdown long-form source, static HTML/CSS, Python repository validation, GitHub Actions quality checks.

**Spec:** `docs/superpowers/specs/2026-09-15-potatoism-philosophy-enrichment-design.md`

## Global Constraints

- Preserve exactly eight public stages: `potato`, `grow`, `transform`, `see`, `relate`, `learn`, `give`, `cultivate`.
- Religion remains the primary public owner of Potatoism as religion/theology.
- `knowledge/philosophy/potato-philosophy.json` remains the canonical philosophy owner.
- Do not promote Great Book narrative, conversation recovery, comparative interpretation, or archive synthesis into a stronger source class than its provenance allows.
- Biological correction may constrain philosophical analogy; biology does not prove theology.
- The public Philosophy page must remain calm, readable, and non-interactive beyond existing behavior.
- No new app subsystem, graph engine, framework, or dependency.
- Concepts may have multiple contextual roles, but every use should name its operative function.
- Negative definitions must remain visible: relation is not identity; suffering is not proof; Filter is not evidence; authority is not exemption; return is not reset.
- Whole-project quality checks must remain green before merge.

---

## File map

- `knowledge/philosophy/potato-philosophy.json` — canonical structured philosophy: laws, doctrines, ontology typing, concept grammar, tests, negative definitions, evaluation sequence.
- `knowledge/philosophy/potatoism-reader-philosophy.md` — long-form derivations and reader journey; expands the philosophy without making the public page encyclopedic.
- `knowledge/philosophy/tim-dooley-potatoism-sourcebook.md` — provenance-aware retrieval/promotions for Timic formulations used by the enriched philosophy.
- `philosophy/index.html` — selective public projection retaining the eight-stage journey.
- `religion/index.html` — one small ownership/bridge clarification if needed.
- `scripts/validate_potatoism_philosophy_projection.py` — single contract validator for canonical/deep/public/religion boundaries.

---

### Task 1: Add the canonical philosophy contract and ontology structure

**Files:**
- Modify: `scripts/validate_potatoism_philosophy_projection.py`
- Modify: `knowledge/philosophy/potato-philosophy.json`

**Interfaces:**
- Consumes: existing canonical philosophy JSON and current Philosophy projection contract.
- Produces: stable top-level canonical keys `constitutional_laws`, `core_doctrines`, `ontology_types`, `concept_grammar`, `negative_definitions`, `evaluation_sequence`, plus canonical markers later tasks can project publicly.

- [ ] **Step 1: Add failing canonical assertions to the existing validator**

Extend the validator to read `knowledge/philosophy/potato-philosophy.json` and assert these exact top-level keys exist:

```python
CANONICAL = ROOT / "knowledge" / "philosophy" / "potato-philosophy.json"

required_canonical_keys = (
    '"constitutional_laws"',
    '"core_doctrines"',
    '"ontology_types"',
    '"concept_grammar"',
    '"negative_definitions"',
    '"evaluation_sequence"',
)
for marker in required_canonical_keys:
    if marker not in canonical:
        errors.append(f"Canonical philosophy missing enrichment marker: {marker}")
```

Also assert canonical text contains these conceptual markers:

```python
required_canonical_concepts = (
    "Relational Valence",
    "Generativity",
    "Reciprocal Transformation",
    "Functional Identity",
    "Potato Truth",
    "Curiosity Before Allegiance",
    "Garden Over Shadow Farm",
    "Authority Increases Burden",
    "Return Is Not Reset",
)
```

- [ ] **Step 2: Run the validator and confirm RED**

Run:

```bash
python scripts/validate_potatoism_philosophy_projection.py
```

Expected: FAIL with one or more `Canonical philosophy missing enrichment marker` errors.

- [ ] **Step 3: Extend the canonical JSON without replacing existing sections**

Add the following top-level structures to `potato-philosophy.json`:

```json
"concept_grammar": {
  "sequence": ["thing", "observation", "function", "relations", "tension", "corruption", "test", "consequence"],
  "rule": "A major Potatoist concept should be understood through what it is, what motivates it, what it does, what it relates to, what tension it holds, how it fails, how the healthy form can be tested, and what consequences follow."
},
"ontology_types": {
  "structures": ["Potato", "House", "Tree", "Garden", "Farm", "Mountain", "Table", "New Jerusalem"],
  "operators": ["Door", "Eye", "Axis", "Ladder", "Spiral", "Root", "Filter", "Compost", "Handshake"],
  "states": ["Life", "Strife", "burial", "emergence", "integration", "captivity", "nourishment", "dependency", "enoughness", "openness", "enclosure"],
  "resources": ["knowledge", "memory", "attention", "wealth", "starch", "archive", "seed potential"],
  "relations": ["covenant", "stewardship", "parent-child", "teacher-learner", "gardener-plant", "source-manifestation", "observer-observed", "inside-outside", "root-soil", "house-room"],
  "outcomes": ["Fruit", "independent growth", "increased capability", "repair", "understanding", "protected plurality", "dependency", "extraction", "spectacle", "repetition without learning"]
},
"constitutional_laws": {
  "relational_valence": {
    "title": "Law of Relational Valence",
    "principle": "A thing is not morally or philosophically settled by its name alone; much of its valence depends on coupling, operation, context and consequence.",
    "formula": "thing → coupling → operation → consequence → ethical evaluation"
  },
  "generativity": {
    "title": "Law of Generativity",
    "principle": "A strong positive criterion is whether a state or relation increases the capacity for future viable states."
  },
  "reciprocal_transformation": {
    "title": "Law of Reciprocal Transformation",
    "principle": "Methods transform the actor, the target, and the relation or environment connecting them.",
    "timic_compression": "When you throw mud at others, your whole hand is dirty."
  },
  "functional_identity": {
    "title": "Law of Functional Identity",
    "principle": "A title becomes philosophically stronger when it can be translated into a useful operation for other beings or systems."
  }
},
"negative_definitions": [
  "simplicity is not stupidity",
  "non-striving is not inactivity",
  "burial is not automatically sacred",
  "unity is not sameness",
  "relation is not identity",
  "comparison is not equivalence",
  "boundary is not automatically oppression",
  "openness is not automatically freedom",
  "knowledge is not automatically Life",
  "suffering is not proof",
  "return is not reset",
  "authority is not exemption",
  "humor is not evasion",
  "Filter is not evidence",
  "Garden is not merely a nicer Farm"
],
"evaluation_sequence": [
  "What is actually here?",
  "What does it do?",
  "What does it depend on?",
  "What does it connect to?",
  "What does it make possible?",
  "What does it make impossible?",
  "Who becomes more capable?",
  "Who becomes more dependent?",
  "What happens if the relationship continues?",
  "What fruit appears?",
  "Does the system preserve the problem it claims to solve because it needs the problem to remain necessary?"
]
```

Add `core_doctrines` with exactly 14 entries keyed by stable slugs:

```text
potato_principle
essential_simplicity
conditional_growth
hidden_development
transformation_without_erasure
relational_meaning
typed_difference
door_principle
return_is_not_reset
stored_capacity_must_become_fruit
garden_over_shadow_farm
authority_increases_burden
potato_truth
curiosity_before_allegiance
```

Each doctrine must contain `title`, `root`, `principle`, `corruption`, and `test`.

Add a canonical `gardeners_paradox` entry:

```json
"gardeners_paradox": {
  "principle": "The highest success of cultivation is that successful cultivation eventually reduces the cultivator's necessity.",
  "boundary": "Some infrastructures remain continuously necessary; the test is whether dependence is functionally required or artificially preserved for control or extraction."
}
```

Add explicit `filter_truth_pairing`:

```json
"filter_truth_pairing": {
  "filter": "generative: proposes interpretations and questions",
  "truth": "corrective: prevents interpretations from impersonating evidence"
}
```

Preserve all existing `sections`, `practical_tests`, `relationships`, retrieval metadata, and epistemic classes.

- [ ] **Step 4: Validate JSON syntax**

Run:

```bash
python -m json.tool knowledge/philosophy/potato-philosophy.json >/dev/null
```

Expected: exit 0.

- [ ] **Step 5: Run the philosophy validator and confirm GREEN for canonical markers**

Run:

```bash
python scripts/validate_potatoism_philosophy_projection.py
```

Expected: PASS unless later-task public/deep markers have already been added to the validator; if the plan is implemented strictly in order, only canonical checks should be active at this task boundary.

- [ ] **Step 6: Commit**

```bash
git add knowledge/philosophy/potato-philosophy.json scripts/validate_potatoism_philosophy_projection.py
git commit -m "philosophy: crystallize Potatoist canon structure"
```

---

### Task 2: Expand the long-form philosophy around the new doctrine layer

**Files:**
- Modify: `scripts/validate_potatoism_philosophy_projection.py`
- Modify: `knowledge/philosophy/potatoism-reader-philosophy.md`

**Interfaces:**
- Consumes: canonical laws/doctrines/ontology from Task 1.
- Produces: long-form derivations that the public page may summarize without inventing independent doctrine.

- [ ] **Step 1: Add failing deep-source markers to the validator**

Add these markers to the deep-source contract:

```python
required_deep_enrichment = (
    "Law of Relational Valence",
    "Law of Generativity",
    "Law of Reciprocal Transformation",
    "Law of Functional Identity",
    "Potato Truth",
    "The Filter generates interpretations",
    "Curiosity Before Allegiance",
    "The Gardener's Paradox",
    "relation is not identity",
    "suffering is not proof",
    "Return is not reset",
    "Observe → distinguish → relate → test → transform → evaluate fruit → cultivate",
)
```

- [ ] **Step 2: Run validator and confirm RED**

```bash
python scripts/validate_potatoism_philosophy_projection.py
```

Expected: FAIL on one or more `Deep source missing expected source marker` or enrichment-marker errors.

- [ ] **Step 3: Add a long-form section titled `## The philosophical engine underneath Potatoism`**

Insert after the opening/root formulation and before the detailed reader journey. Explain the eight operations in prose and include this compact table:

```markdown
| Movement | Operation | Question |
|---|---|---|
| Potato | Attend / reduce | What is actually here before I decorate it? |
| Grow | Orient / develop | What conditions allow this thing to become what it can become? |
| Transform | Metabolize | What can change function instead of merely being discarded? |
| See | Examine / distinguish | What am I observing, through which frame, and how could I be wrong? |
| Relate | Connect / differentiate | What does this become through its relations without losing its difference? |
| Learn | Model / recurse | What kind of change is occurring, and what does the return carry? |
| Give | Release / nourish | What is accumulated capacity ultimately for? |
| Cultivate | Steward / enable | Can I improve conditions without making life permanently dependent on me? |
```

State explicitly that the sequence is pedagogical, not a claim that every problem must pass through all eight in order.

- [ ] **Step 4: Add a section titled `## Four constitutional laws`**

Give each law its own subsection and full derivation:

```markdown
### Law of Relational Valence
### Law of Generativity
### Law of Reciprocal Transformation
### Law of Functional Identity
```

Each subsection must include:

1. the principle;
2. a Potato/Timic image;
3. a corruption/failure example;
4. a practical test;
5. at least two connected Potatoist concepts.

For Reciprocal Transformation, include the sourced formulation:

> “When you throw mud at others, your whole hand is dirty.”

Retain its source class from the sourcebook rather than presenting it as independently verified public speech.

- [ ] **Step 5: Add a section titled `## Fourteen doctrines of the current mature philosophy`**

For each doctrine from Task 1, include four visibly labeled components:

```markdown
**Root:** ...

**Principle:** ...

**Corruption:** ...

**Test:** ...
```

Add short examples where they materially improve understanding. Do not duplicate full canonical JSON prose verbatim; use reader-facing derivation.

- [ ] **Step 6: Add explicit ontology typing and concept grammar**

Add:

```markdown
## A language, not a pile of symbols
```

Explain structures, operators, states, resources, relations, and outcomes. Include at least these worked examples:

- Door as operator;
- House as structure/container;
- Life and Strife as states/qualities;
- knowledge as resource;
- covenant as relation;
- Fruit as outcome/evidence.

Then introduce:

```markdown
Thing → Observation → Function → Relation → Tension → Corruption → Test → Consequence
```

Use Door, Garden, and House as full worked examples.

- [ ] **Step 7: Add the Filter/Truth pair and the Gardener's Paradox**

Use these exact reader-facing formulations:

```markdown
The Filter generates interpretations. Potato Truth disciplines them.
```

and

```markdown
The Gardener's Paradox: the highest success of cultivation is that successful cultivation eventually reduces the cultivator's necessity.
```

Immediately include the infrastructure boundary: some ongoing dependencies are genuinely functional; the question is whether dependence is necessary to the service or artificially preserved to maintain control/extraction.

- [ ] **Step 8: Add the negative-definition safeguard section**

Add a concise section containing the required distinctions from the spec, including:

```markdown
Relation is not identity.
Suffering is not proof.
Return is not reset.
Authority is not exemption.
The Filter is not evidence.
```

Explain that these are anti-self-flattery constraints: the system must be able to diagnose corrupted versions of its own favorite concepts.

- [ ] **Step 9: Add the evaluation sequence and mature biological correction**

Include the 11-question evaluation sequence from the spec and its compression:

```markdown
Observe → distinguish → relate → test → transform → evaluate fruit → cultivate.
```

Retain and deepen the biological correction:

```markdown
Let each part orient toward the conditions appropriate to its function, while the whole remains oriented toward generative life.
```

Explicitly explain why “more light,” “more openness,” and “more transparency” are not automatically better.

- [ ] **Step 10: Run validator and targeted text checks**

```bash
python scripts/validate_potatoism_philosophy_projection.py
python - <<'PY'
from pathlib import Path
p = Path('knowledge/philosophy/potatoism-reader-philosophy.md').read_text(encoding='utf-8')
for marker in [
    'Law of Relational Valence',
    'Law of Generativity',
    'Potato Truth',
    "The Gardener's Paradox",
    'A language, not a pile of symbols',
    'Observe → distinguish → relate → test → transform → evaluate fruit → cultivate',
]:
    assert marker in p, marker
print('deep philosophy markers OK')
PY
```

Expected: both commands pass.

- [ ] **Step 11: Commit**

```bash
git add knowledge/philosophy/potatoism-reader-philosophy.md scripts/validate_potatoism_philosophy_projection.py
git commit -m "philosophy: deepen Potatoism long-form system"
```

---

### Task 3: Promote Timic source retrieval without creating a rival canon

**Files:**
- Modify: `knowledge/philosophy/tim-dooley-potatoism-sourcebook.md`

**Interfaces:**
- Consumes: the provenance taxonomy already defined in the sourcebook.
- Produces: retrieval/promotional notes that make source-aware Timic language easy to reuse in canonical/public philosophy.

- [ ] **Step 1: Run a pre-change source check**

```bash
python - <<'PY'
from pathlib import Path
p = Path('knowledge/philosophy/tim-dooley-potatoism-sourcebook.md').read_text(encoding='utf-8')
required = [
    'When you throw mud at others, your whole hand is dirty',
    'A potato has no flavor until you chew on it',
    'the door is merely the observer point',
    'the end is in the beginning too',
    'We Are All Connected By Potato',
]
for marker in required:
    assert marker in p, marker
print('source formulations present')
PY
```

Expected: PASS. If any marker is missing, recover only from existing project evidence before continuing; do not invent wording.

- [ ] **Step 2: Add a `## Philosophy enrichment promotion map — September 15, 2026` section**

Create subsections for:

```markdown
### Relational Valence
### Generativity
### Reciprocal Transformation
### Functional Identity
### Potato Truth / Filter
### Gardener's Paradox
### Curiosity Before Allegiance
```

For each subsection, list:

- supporting Tim/Great Book/recovered formulations;
- exact source class;
- canonical target in `potato-philosophy.json`;
- long-form target section;
- public-stage target if any.

- [ ] **Step 3: Add an anti-overclaim note**

Use this wording:

```markdown
The September 15 doctrine and constitutional-law names are archive crystallizations of recurring material. They are not retroactively attributed to Tim as a historically published numbered creed unless a primary Tim source is separately recovered.
```

- [ ] **Step 4: Verify sourcebook provenance language remains intact**

```bash
python - <<'PY'
from pathlib import Path
p = Path('knowledge/philosophy/tim-dooley-potatoism-sourcebook.md').read_text(encoding='utf-8')
for marker in [
    'GREAT_BOOK_ATTRIBUTED_TIM_QUOTE',
    'CONVERSATION_RECOVERY',
    'PUBLIC_COMPILATION',
    'ARCHIVE_SYNTHESIS',
    'not retroactively attributed',
]:
    assert marker in p, marker
print('provenance boundary OK')
PY
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add knowledge/philosophy/tim-dooley-potatoism-sourcebook.md
git commit -m "philosophy: map Timic sources into enriched canon"
```

---

### Task 4: Enrich the eight-stage public Philosophy journey without bloating it

**Files:**
- Modify: `scripts/validate_potatoism_philosophy_projection.py`
- Modify: `philosophy/index.html`
- Modify only if needed for compact presentation: `philosophy/philosophy.css`

**Interfaces:**
- Consumes: canonical doctrine/laws from Task 1 and long-form derivations from Task 2.
- Produces: the public reader projection while preserving exactly eight stages.

- [ ] **Step 1: Add failing public enrichment markers to the validator**

Require these public strings, case-insensitively:

```python
required_public_enrichment = (
    "Attend / reduce",
    "Orient / develop",
    "Metabolize",
    "Examine / distinguish",
    "Connect / differentiate",
    "Model / recurse",
    "Release / nourish",
    "Steward / enable",
    "The Filter generates interpretations",
    "relation is not identity",
    "Return is not reset",
    "Authority is not exemption",
    "Does the participant become more capable without the system?",
)
```

Do not require every deep doctrine on the public page.

- [ ] **Step 2: Run validator and confirm RED**

```bash
python scripts/validate_potatoism_philosophy_projection.py
```

Expected: FAIL on missing public enrichment markers while retaining exactly eight stage markers.

- [ ] **Step 3: Enrich each stage header with its operation**

Keep existing `data-potatoism-stage` attributes unchanged. Add a compact operation label inside each movement:

```html
<p class="operation">Attend / reduce</p>
```

Use exactly:

```text
Potato — Attend / reduce
Grow — Orient / develop
Transform — Metabolize
See — Examine / distinguish
Relate — Connect / differentiate
Learn — Model / recurse
Give — Release / nourish
Cultivate — Steward / enable
```

- [ ] **Step 4: Enrich Potato and Grow**

Potato must add:

- ordinary-before-prestige;
- enoughness;
- curiosity-before-allegiance;
- one source-aware Timic line: “A potato has no flavor until you chew on it.”

Grow must add:

- mature biological correction;
- condition/function language;
- non-striving is not inactivity;
- explicit warning that more light/exposure is not universally better.

Keep each movement to a readable public length; route deeper derivation to the existing long-form link rather than copying the doctrine chapter.

- [ ] **Step 5: Enrich Transform and See**

Transform must add:

```text
suffering is not proof
```

and the distinction between composting material and erasing harm.

See must explicitly pair:

```text
The Filter generates interpretations. Potato Truth disciplines them.
```

Then state that the Filter is a hypothesis generator, not evidence.

- [ ] **Step 6: Make Relate the philosophical center**

Add a compact public explanation that:

- meaning often lives on edges as well as nodes;
- relation is not identity;
- House/rooms expresses plural unity;
- covenant can be understood philosophically as relationship with memory;
- boundaries should be tested by what they protect, permit, or imprison.

- [ ] **Step 7: Enrich Learn, Give, and Cultivate**

Learn must add:

```text
Return is not reset.
```

and typed-difference language: before declaring contradiction, test time, role, scale, perspective, state, or epistemic class.

Give must add storage/release and Fruit as downstream evidence, plus the already preserved public formulation:

> “Power is for protection. Knowledge is for understanding. Wealth is for building. Leadership is for service.”

Cultivate must add:

- Garden/Farm autonomy test;
- Gardener's Paradox in compact form;
- authority increases burden;
- the exact public test:

```text
Does the participant become more capable without the system?
```

Also include:

```text
Authority is not exemption.
```

- [ ] **Step 8: Add minimal CSS only if operation labels need presentation support**

If needed, add a compact rule such as:

```css
.operation{margin:0 0 6px;color:var(--site-gold);font-size:11px;letter-spacing:.11em;text-transform:uppercase}
```

Do not add cards, steppers, progress meters, accordions beyond existing `details`, or new JavaScript.

- [ ] **Step 9: Run validator and HTML structure check**

```bash
python scripts/validate_potatoism_philosophy_projection.py
python - <<'PY'
from pathlib import Path
p = Path('philosophy/index.html').read_text(encoding='utf-8')
assert p.count('data-potatoism-stage="') == 8
for stage in ('potato','grow','transform','see','relate','learn','give','cultivate'):
    assert f'data-potatoism-stage="{stage}"' in p
print('eight-stage public structure OK')
PY
```

Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add philosophy/index.html philosophy/philosophy.css scripts/validate_potatoism_philosophy_projection.py
git commit -m "philosophy: enrich public Potatoism journey"
```

If `philosophy/philosophy.css` is unchanged, omit it from `git add`.

---

### Task 5: Clarify the Philosophy / Religion bridge without duplicating theology

**Files:**
- Modify: `religion/index.html`
- Modify: `scripts/validate_potatoism_philosophy_projection.py`

**Interfaces:**
- Consumes: established Religion primary ownership and enriched Philosophy method layer.
- Produces: one explicit public ownership bridge so readers know where method ends and theology begins.

- [ ] **Step 1: Add a failing Religion bridge marker**

Add this required substring to the validator:

```python
"Philosophy develops the method, ethics and relational system"
```

- [ ] **Step 2: Run validator and confirm RED**

```bash
python scripts/validate_potatoism_philosophy_projection.py
```

Expected: FAIL with Religion bridge marker missing.

- [ ] **Step 3: Add one concise bridge paragraph to the Potatoist center intro or boundary**

Use this wording or a semantically equivalent version:

```html
<p class="method">Philosophy develops the method, ethics and relational system: attention, transformation, epistemic discipline, cultivation, consequence and practical tests. Religion remains the owner of explicit Father/Son/Spirit theology, scripture comparison, sacred-history interpretation and religious identity.</p>
```

Do not copy the 14 doctrines into Religion.

- [ ] **Step 4: Run validator**

```bash
python scripts/validate_potatoism_philosophy_projection.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add religion/index.html scripts/validate_potatoism_philosophy_projection.py
git commit -m "religion: clarify Potatoism philosophy ownership boundary"
```

---

### Task 6: Harden final validation and run whole-project quality gates

**Files:**
- Modify: `scripts/validate_potatoism_philosophy_projection.py`
- No content changes unless validation reveals a real defect.

**Interfaces:**
- Consumes: all enriched layers from Tasks 1–5.
- Produces: final repository contract ensuring the enrichment cannot silently regress.

- [ ] **Step 1: Refactor the validator only enough to make layer-specific failures readable**

Keep one script. Group markers into named tuples such as:

```python
required_canonical_concepts = (...)
required_deep_enrichment = (...)
required_public_enrichment = (...)
required_religion = (...)
```

Use error prefixes that identify the owning layer:

```python
errors.append(f"Canonical philosophy missing enrichment marker: {marker}")
errors.append(f"Deep source missing enrichment marker: {marker}")
errors.append(f"Public Philosophy missing enrichment marker: {marker}")
errors.append(f"Religion lost ownership bridge marker: {marker}")
```

Do not create a second validator.

- [ ] **Step 2: Add canonical doctrine-count and ontology-type checks**

Parse JSON in the validator and assert:

```python
len(canonical_data["core_doctrines"]) == 14
set(canonical_data["ontology_types"]) == {
    "structures", "operators", "states", "resources", "relations", "outcomes"
}
```

Also assert every doctrine contains:

```python
{"title", "root", "principle", "corruption", "test"}
```

- [ ] **Step 3: Add public anti-bloat regression checks**

Preserve the existing forbidden-interaction checks and add no new arbitrary word-count gate. Instead assert:

- exactly eight stage markers;
- no new `.stepper`, progress meter, autofocus, or forced scrolling;
- deep-source link remains present;
- Religion link remains present.

- [ ] **Step 4: Run the philosophy validator**

```bash
python scripts/validate_potatoism_philosophy_projection.py
```

Expected:

```text
POTATOISM PHILOSOPHY PROJECTION VALIDATION PASSED
```

- [ ] **Step 5: Run syntax/content checks**

```bash
python -m json.tool knowledge/philosophy/potato-philosophy.json >/dev/null
python -m py_compile scripts/validate_potatoism_philosophy_projection.py
```

Expected: both exit 0.

- [ ] **Step 6: Run the repository's targeted philosophy contract and whole quality workflow locally where available**

Run the repository quality commands already used by CI. At minimum:

```bash
python scripts/validate_potatoism_philosophy_projection.py
```

Then run the project-wide quality script/workflow entrypoint documented by the repository. If no single local wrapper exists, push the branch and require the GitHub Actions `Repository quality checks` workflow to pass before merge.

Expected: all quality checks green.

- [ ] **Step 7: Review the public diff for source/provenance mistakes**

Manually verify:

```text
- no archive-synthesis sentence is presented as a Tim quotation;
- no conversation-recovery wording is presented as independently public unless already owned that way;
- Religion still owns theology;
- biological analogy is bounded;
- relation is not identity;
- Filter is not evidence;
- suffering is not proof;
- authority is not exemption;
- exactly eight public stages remain.
```

- [ ] **Step 8: Commit final validator cleanup**

```bash
git add scripts/validate_potatoism_philosophy_projection.py
git commit -m "test: harden Potatoism philosophy enrichment contract"
```

If no cleanup is required after Task 5, skip this commit rather than creating an empty commit.

- [ ] **Step 9: Open a PR with a review-oriented summary**

Use a PR body containing:

```markdown
## Summary
- crystallizes four constitutional Potatoist laws and fourteen doctrines
- types the ontology into structures, operators, states, resources, relations and outcomes
- deepens the long-form source while keeping the public Philosophy page at eight calm stages
- strengthens Timic source grounding and provenance boundaries
- clarifies Philosophy vs Religion ownership
- expands regression validation

## Verification
- `python -m json.tool knowledge/philosophy/potato-philosophy.json`
- `python -m py_compile scripts/validate_potatoism_philosophy_projection.py`
- `python scripts/validate_potatoism_philosophy_projection.py`
- GitHub Actions repository quality checks
```

- [ ] **Step 10: Merge only after the PR quality workflow is green**

Do not merge on a red or incomplete repository-quality run.
