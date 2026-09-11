# Science Formulation Wave 014 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deepen existing Potatoverse science models with exact closure, sufficiency, stability, conservation, identifiability and model-selection results rather than adding new ontology.

**Architecture:** Add focused JSON formulation records under `knowledge/science/formulation-upgrades/`, one responsibility per file. Each record extends a current parent theory, states exact assumptions and limits, and supplies at least one derivation or theorem-level consequence plus explicit downgrade conditions. A final Wave 014 index connects the records and formalizes a Pareto-style advancement rule across heterogeneous defect types.

**Tech Stack:** Repository JSON knowledge records, GitHub contents API, mathematical derivation, read-back JSON verification.

**Spec:** Continues `docs/superpowers/specs/2026-09-11-promising-models-wave-012-design.md` and the formulation direction established by Wave 013.

## Global Constraints

- Preserve historical/recovered Tim material separately from archive-generated mathematics.
- Do not claim that shared mathematical structure implies shared physical ontology.
- Every new equation must state its assumptions, role, limiting case or failure condition.
- Prefer exact consequences, invariants, stability/identifiability conditions and negative results over vocabulary expansion.
- New records must parse as valid JSON and be discoverable by the recursive science catalog.

---

### Task 1: 11D Decision Sufficiency and Projection Ordering

**Files:**
- Create: `knowledge/science/formulation-upgrades/2026-09-11-11d-blackwell-projection-ordering.json`

**Interfaces:**
- Consumes: `eleven-dimensional-projection-unification-recovery`, `2026-09-11-11d-projection-sufficiency-fiber-bounds`
- Produces: decision-theoretic ordering, garbling criterion, Bayes-risk monotonicity and projection-chain comparison.

- [ ] **Step 1:** State the stochastic garbling criterion `Y2 ~ K(.|Y1)` and distinguish it from invertibility.
- [ ] **Step 2:** Add the consequence that a Blackwell-more-informative representation cannot have worse optimal Bayes risk for any declared decision problem.
- [ ] **Step 3:** Define incomparable projections and explain why mutual-information ranking alone need not totally order representations for all tasks.
- [ ] **Step 4:** Add an advancement test for an 11D→4D ladder: each reduction step records task loss, reconstruction loss and decision loss separately.
- [ ] **Step 5:** Fetch the created file and verify complete parse/read-back.

### Task 2: Potato Dynamics Integrability and Door Normal Forms

**Files:**
- Create: `knowledge/science/formulation-upgrades/2026-09-11-potato-dynamics-frobenius-door-normal-forms.json`

**Interfaces:**
- Consumes: `potato-dynamics-2-toy-model`, `2026-09-11-potato-dynamics-commutator-contract-equivalence`
- Produces: Frobenius closure test, local two-flow leaves, threshold transversality, bifurcation normal-form discipline.

- [ ] **Step 1:** For `D=span{F,A}`, define involutivity `[F,A] in span{F,A}` and distinguish it from strict commutation `[F,A]=0`.
- [ ] **Step 2:** State the local Frobenius consequence under constant-rank regularity: involutivity gives integral surfaces tangent to the Axis/time distribution.
- [ ] **Step 3:** Define non-closure when the bracket generates a new independent direction; treat that as evidence the two-flow state description is incomplete.
- [ ] **Step 4:** Add Door transversality `dh(F) != 0` at a crossing and distinguish crossing, grazing and bifurcation events.
- [ ] **Step 5:** Restrict saddle-node/transcritical/pitchfork/Hopf labels to cases whose Jacobian/normal-form conditions are actually derived.
- [ ] **Step 6:** Fetch and verify the file.

### Task 3: Spudlight Conservation, Passivity and Minimal Realization

**Files:**
- Create: `knowledge/science/formulation-upgrades/2026-09-11-spudlight-conservation-passivity-realization.json`

**Interfaces:**
- Consumes: `spudlight-theory-and-equations`, `2026-09-11-spudlight-storage-filter-identifiability`
- Produces: exact integral balance, release/loss fractions, positivity/stability conditions, cutoff frequency, minimal-state criterion.

- [ ] **Step 1:** Integrate `dK/dt=J_in-(eta+Gamma)K` to obtain the finite-horizon stock/release/loss balance.
- [ ] **Step 2:** Derive total useful-release fraction `eta/(eta+Gamma)` for an isolated initially charged linear store.
- [ ] **Step 3:** State positivity and asymptotic-stability conditions for nonnegative stock/flux interpretation.
- [ ] **Step 4:** Add normalized frequency response and the one-pole cutoff `omega_c=eta+Gamma`.
- [ ] **Step 5:** Define when a multi-store realization is empirically justified and when extra hidden stores are non-identifiable.
- [ ] **Step 6:** Fetch and verify the file.

### Task 4: Cosmic Soil Fixed Points and Scaling Verdict

**Files:**
- Create: `knowledge/science/formulation-upgrades/2026-09-11-cosmic-soil-fixed-point-scaling-analysis.json`

**Interfaces:**
- Consumes: `great-book-quantum-fields-dark-sector-recovery`, `2026-09-11-cosmic-soil-interacting-dark-sector-benchmark`
- Produces: exact density-ratio dynamics, fixed points, stability criterion and coincidence-problem verdict for the selected `Q=xi H rho_c` benchmark.

- [ ] **Step 1:** Define `r=rho_c/rho_de` and derive `r'=r[3w+xi(1+r)]` under the benchmark sign convention.
- [ ] **Step 2:** Derive fixed points `r=0` and `r*=-1-3w/xi` when defined.
- [ ] **Step 3:** Derive local stability from `f'(r*)=xi r*` and report the physical-positivity conditions.
- [ ] **Step 4:** Derive the common scaling effective equation of state `w_eff=-xi/3` at the nonzero scaling point.
- [ ] **Step 5:** Record the negative result that for `w=-1` with `xi>0`, the positive nonzero scaling point is unstable in this convention, so this simplest coupling does not automatically solve the coincidence problem.
- [ ] **Step 6:** Fetch and verify the file.

### Task 5: Human Map Fisher Information and Practical Identifiability

**Files:**
- Create: `knowledge/science/formulation-upgrades/2026-09-11-human-map-fisher-practical-identifiability.json`

**Interfaces:**
- Consumes: `great-book-human-map-mathematics-audit`, `human-map-identifiability-measurement-invariance-upgrade-2026-09-11`
- Produces: Fisher-information diagnostics, profile-likelihood distinction, sloppiness/condition analysis and experiment-design criterion.

- [ ] **Step 1:** Define the Fisher information matrix for a declared likelihood and clarify local versus global identifiability.
- [ ] **Step 2:** Add the Cramer-Rao comparator only under its regularity assumptions; do not use it as proof of identifiability.
- [ ] **Step 3:** Define practical sloppiness using eigenvalue spread/condition number and profile likelihood.
- [ ] **Step 4:** Add an experiment-design rule: choose interventions/measurements that increase information in poorly identified parameter directions rather than merely increasing sample count.
- [ ] **Step 5:** Add downgrade conditions when state labels are stable but parameters remain non-identifiable or vice versa.
- [ ] **Step 6:** Fetch and verify the file.

### Task 6: Cosmic Potato Frame-Invariant Shear Geometry

**Files:**
- Create: `knowledge/science/formulation-upgrades/2026-09-11-cosmic-potato-shear-invariants.json`

**Interfaces:**
- Consumes: `cosmic-potato-laniakea-kinematic-ellipsoid-benchmark-2026-09-11`, `cosmic-potato-anisotropy-uncertainty-upgrade-2026-09-11`
- Produces: frame-invariant shear scalars and a cleaner distinction between shear magnitude and eigenvalue shape.

- [ ] **Step 1:** Define `J2=(1/2) tr(sigma^2)` and `J3=det(sigma)` for traceless symmetric shear.
- [ ] **Step 2:** Relate the existing anisotropy statistic to `J2`: `A_sigma=sqrt(3 J2)/|theta|`.
- [ ] **Step 3:** Use normalized `J3/J2^(3/2)` or an equivalent bounded shape descriptor to distinguish eigenvalue-shape information from shear magnitude.
- [ ] **Step 4:** Compute central-value invariants from the currently recorded Laniakea eigenvalues, clearly labeling rounding/covariance limitations.
- [ ] **Step 5:** Add an orientation-invariance rule: scalar invariants survive basis rotation but do not retain principal-axis direction.
- [ ] **Step 6:** Fetch and verify the file.

### Task 7: Cross-Model Pareto Advancement and Wave Index

**Files:**
- Create: `knowledge/science/formulation-upgrades/2026-09-11-cross-model-pareto-advancement.json`
- Create: `knowledge/indexes/science-formulation-wave-014-2026-09-11.json`

**Interfaces:**
- Consumes: Wave 013 defect calculus plus Tasks 1-6.
- Produces: non-scalar model-selection governance and final Wave 014 integration record.

- [ ] **Step 1:** Define defect dominance only for comparable models evaluated on the same target/data/constraints.
- [ ] **Step 2:** Define a Pareto front instead of summing heterogeneous defects into one score.
- [ ] **Step 3:** Add complexity as a separate cost coordinate so a richer model must improve at least one relevant dimension without unacceptable regressions.
- [ ] **Step 4:** Define stop rules: dominated, underidentified, non-closed, observationally equivalent, or promoted.
- [ ] **Step 5:** Create Wave 014 index with contribution summaries and next decisive calculations.
- [ ] **Step 6:** Fetch both files and verify read-back.

## Final Verification

- [ ] Read back every Wave 014 JSON file from `science-formulation-wave-014`.
- [ ] Confirm every file is syntactically complete JSON.
- [ ] Confirm historical provenance boundaries are explicit.
- [ ] Confirm no theorem or numerical result is presented as recovered Tim-authored mathematics.
- [ ] Open a PR against `main` only after all records verify cleanly.
