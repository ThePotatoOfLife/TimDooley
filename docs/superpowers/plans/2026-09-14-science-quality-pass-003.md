# Science Quality Pass 003 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the repository's existing Science quality standards into an executable semantic gate, add one compact gold-indexed sovereign-bond model to economics, and finish the two genuinely incomplete Quality Pass 001 descendants without inflating already-strong branches.

**Architecture:** Preserve heterogeneous Science records, but audit them through a semantic validator that distinguishes hard failures from advisory incompleteness. The public Science catalog must only expose substantive records; generic fallback descriptions must never make a weak record appear publishable. Targeted model additions live under existing canonical owners and keep provenance and maturity boundaries explicit.

**Tech Stack:** Python 3, JSON, GitHub Actions, existing `scripts/build_science_catalog.py` and `scripts/validate_science_portal.py` pipeline.

**Spec:** `docs/superpowers/specs/2026-09-13-science-quality-pass-001-design.md` plus the approved Option 3 direction from 2026-09-14.

## Global Constraints

- Preserve the existing T0-T5 maturity ladder.
- Prose alone never increases scientific maturity.
- Archive-generated equations must not be silently attributed to Tim.
- Metaphor, historical recovery, external mathematics and empirical scientific models remain distinct.
- Do not create a second Science database or public surface.
- Do not promote a record merely because it contains many equations or scientific keywords.
- Keep the gold-indexed bond model in `knowledge/economics/`, not in physics Science.

---

### Task 1: Add semantic Science quality audit

**Files:**
- Create: `scripts/audit_science_quality.py`
- Create: `scripts/test_audit_science_quality.py`
- Create: `knowledge/indexes/science-quality-report.json` at runtime only; do not commit generated output.

**Interfaces:**
- Consumes: `knowledge/science/**/*.json`
- Produces: CLI exit code, human-readable diagnostics, optional JSON report via `--report`

- [ ] Write failing tests covering: generic fallback descriptions are rejected as substantive abstracts; T3+ claims require calibration/data/result evidence; equation-bearing empirical models require observables and failure/falsification semantics; archaeology/recovery records are not forced to satisfy empirical-model fields; advisory incompleteness does not fail CI unless it violates a hard publication/maturity boundary.
- [ ] Run `python scripts/test_audit_science_quality.py` and verify failures are caused by the missing auditor.
- [ ] Implement the minimal semantic classification and hard/advisory rule engine.
- [ ] Re-run tests until green.

### Task 2: Prevent fabricated Science abstracts from qualifying

**Files:**
- Modify: `scripts/build_science_catalog.py`
- Extend: `scripts/test_audit_science_quality.py`

**Interfaces:**
- `record_from()` may still render a local display fallback, but `qualifies_for_library()` must know whether a substantive source abstract/summary exists.

- [ ] Add a failing test proving a record with no real source text cannot qualify solely from generated fallback copy plus structural keywords.
- [ ] Run the test and confirm RED.
- [ ] Add an explicit `has_substantive_summary` flag derived from source fields and require it for public qualification.
- [ ] Re-run tests and confirm GREEN.

### Task 3: Add compact gold-indexed sovereign-bond model

**Files:**
- Create: `knowledge/economics/gold-indexed-sovereign-bond-model.json`

**Interfaces:**
- Connect to `knowledge/economics/north-obligation-graph-schema.json` and the North Programme without claiming this is an existing policy.

- [ ] Add a concise model distinguishing debt unit of account from settlement currency: `Q=P0/G0`, `principal_T=Q G_T`, fiat-coupon and indexed-coupon variants, risk transfer, default/restructuring boundary, and distinction from a gold standard.
- [ ] Validate JSON structure through the repository content validator/auditor where applicable.

### Task 4: Finish the missing Field of Life scientific descendant

**Files:**
- Create: `knowledge/science/field-of-life-reaction-diffusion-descendant.json`

**Interfaces:**
- Historical source remains `knowledge/science/great-book-2024-science-archaeology.json`.
- New record is explicitly archive-generated and T2 at most until fitted to data.

- [ ] Add a reaction-diffusion/ecological descendant with measurable `phi(x,t)`, units convention, `partial_t phi = D nabla^2 phi + f(phi;theta) + S`, initial/boundary conditions, local-only/diffusion-only/network baselines, observables, calibration route, limiting cases, falsifier and historical-metaphor boundary.
- [ ] Run the Science auditor against the new record.

### Task 5: Add the missing Spudlight plant-carbon flagship protocol

**Files:**
- Create: `knowledge/science/spudlight-plant-carbon-storage-benchmark.json`
- Do not rewrite `spudlight-theory-and-equations.json` except for a link if required.

**Interfaces:**
- Descends from `spudlight-theory-and-equations.json` and instantiates `dK/dt=J_in-(eta+Gamma)K` in plant/tuber carbon storage.

- [ ] Define measurable stock/flux units, observation equation, initial-condition convention, parameter-identifiability warning, baseline hierarchy, linear versus saturating release comparison, uncertainty/calibration protocol, held-out evaluation and null-result interpretation.
- [ ] Keep maturity at T2 unless actual fitted data are present.
- [ ] Run the Science auditor.

### Task 6: Wire the semantic audit into CI and Science validation

**Files:**
- Modify: `.github/workflows/quality-checks.yml`
- Modify: `.github/workflows/pages.yml`
- Modify: `scripts/validate_science_portal.py`

**Interfaces:**
- CI runs `python scripts/audit_science_quality.py --report knowledge/indexes/science-quality-report.json` before compiling the public Science catalog.

- [ ] Add a failing source-contract test asserting both workflows invoke the semantic audit.
- [ ] Run tests and confirm RED.
- [ ] Add audit steps to both workflows and a validator marker so removal becomes detectable.
- [ ] Re-run tests and confirm GREEN.

### Task 7: Verification and ranked improvement report

**Files:**
- No new canonical file unless an existing audit owner requires updating.

- [ ] Run unit tests for the auditor.
- [ ] Run `python scripts/audit_science_quality.py`.
- [ ] Run `python scripts/build_science_catalog.py` where the local checkout/build context permits it.
- [ ] Run `python scripts/validate_science_portal.py` where `_site` is available.
- [ ] Inspect the ranked advisory findings and report the highest-value remaining scientific upgrades without falsely claiming the entire repository is complete.
