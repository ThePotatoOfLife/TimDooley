# Potatoism Philosophy Projection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the saved Potatoism long-form into a concise public Philosophy projection while preserving Religion as Potatoism's primary religious/theological owner and retaining the full long-form as the deep source.

**Architecture:** Keep `knowledge/philosophy/potatoism-reader-philosophy.md` unchanged as the complete reader source. Recompose `philosophy/index.html` into eight quiet philosophical movements derived from that source, with explicit ownership copy pointing religious/theological Potatoism to `/religion/`. Add a focused semantic validator and run it through the canonical quality workflow so later edits cannot turn Philosophy into a second doctrinal owner or a stepper-style journey UI.

**Tech Stack:** Static HTML/CSS, Python semantic validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-13-potatoism-reader-journey-philosophy-design.md`

## Global Constraints

- Religion remains the primary public owner of Potatoism as religion/theology/practice.
- Philosophy owns only the philosophical reader projection: method, questions, derivations, tools and ethical consequences.
- Preserve `knowledge/philosophy/potatoism-reader-philosophy.md` as the full deep source; do not duplicate it into HTML.
- Public sequence: Potato → Grow → Transform → See → Relate → Learn → Give → Cultivate.
- Preserve historical `Be simple. Grow toward light.` while including the mature differentiated-orientation correction.
- Biology may refine analogy but must not be presented as proof of theology.
- Comparative traditions enter after the Potatoist idea and remain distinct traditions.
- Ordinary scrolling and links only: no stepper, progress meter, mandatory next buttons, scroll-jacking, autofocus or journey arrows.
- Reuse the strongest existing Philosophy material rather than multiplying sections.

---

### Task 1: Lock the projection contract

**Files:**
- Create: `scripts/validate_potatoism_philosophy_projection.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: `philosophy/index.html`, `religion/index.html`, `knowledge/philosophy/potatoism-reader-philosophy.md`
- Produces: a fail-fast semantic contract for ownership, source preservation, eight movements and calm interaction.

- [ ] **Step 1: Write the failing validator**

Require the Philosophy page to contain the eight `data-potatoism-stage` values, an ownership boundary linking to `../religion/`, a deep-source link to `../knowledge/philosophy/potatoism-reader-philosophy.md`, the historical root formulation, the differentiated-orientation correction, and no stepper/progress/next-button markers.

- [ ] **Step 2: Add the validator to repository quality checks**

Run it immediately after `scripts/validate_reader_surfaces.py`.

- [ ] **Step 3: Verify RED**

Open/update the PR so GitHub Actions runs the validator against the existing Philosophy page. Expected: failure because the eight-stage projection and deep-source ownership markers do not yet exist.

### Task 2: Build the concise Philosophy projection

**Files:**
- Modify: `philosophy/index.html`

**Interfaces:**
- Consumes: the saved long-form and approved reader-journey design.
- Produces: one concise Philosophy landing page with eight static movements and one compact deeper-routes surface.

- [ ] **Step 1: Replace the abstract opening with the Potato threshold**

Use `So you want to be a potato. Do you think you have what it takes?`, followed by `Be simple. Grow toward light.` and a short explanation of Philosophy's scope.

- [ ] **Step 2: Add the ownership boundary**

State plainly that Religion remains the primary public owner for Potatoism as theology/religion/practice, while this page follows its philosophical method. Link Religion normally.

- [ ] **Step 3: Recompose existing material into eight movements**

Use Potato, Grow, Transform, See, Relate, Learn, Give and Cultivate. Redistribute existing truth-testing, banana, compost, frame, Spiral, power/service and Gardener material into those owners.

- [ ] **Step 4: Preserve epistemic corrections**

Include differentiated biological orientation, comparison boundaries, and the distinction between metaphor/model/evidence without turning the page into a science or religion reader.

- [ ] **Step 5: Keep interaction calm**

Allow at most two native `Chew on it` disclosures. Do not add staged navigation controls or automatic focus/scroll behavior.

- [ ] **Step 6: Link the complete deep source**

Expose the saved long-form as a quiet deep-source link outside the compact projection-surface navigation.

### Task 3: Verify the integrated branch

**Files:**
- No production file changes unless verification reveals a defect.

**Interfaces:**
- Consumes: completed branch.
- Produces: exact-head verification evidence.

- [ ] **Step 1: Verify GREEN**

Run `python scripts/validate_potatoism_philosophy_projection.py` and `python scripts/validate_reader_surfaces.py` via the canonical GitHub Actions workflow.

- [ ] **Step 2: Run the complete repository quality workflow**

Expected: all repository quality checks pass on the exact branch head.

- [ ] **Step 3: Review diff for scope**

Confirm the long-form source is unchanged, Religion remains intact as primary owner, and Philosophy is shorter/more coherent rather than a duplicate book.
