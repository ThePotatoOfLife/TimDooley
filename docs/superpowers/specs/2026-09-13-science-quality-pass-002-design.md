# Science Quality Pass 002 — Design

Date: 2026-09-13
Status: approved design
Branch: `science-quality-pass-002`

## Goal

Create three concrete scientific descendants for branches that still stop at programme-level discussion. Each descendant must add a real calculation, comparison, or rejection criterion rather than more vocabulary.

The three targets are:

1. Gauge unification -> minimal non-supersymmetric SU(5) coupling-running benchmark.
2. Infinite Soil / dark sector -> one explicit interacting-dark-sector dynamical model.
3. Microtubules -> classical-versus-open-quantum necessity benchmark.

Existing strong descendants under `knowledge/science/promising-models/` are not duplicated.

## Global scientific rules

All new records must distinguish recovered Tim material, archive-generated descendants, and established external mathematics/physics. No new equation may be silently attributed to Tim.

Use the repository maturity ladder. T2 means a calculable model. T3 requires actual parameter constraints or calibration against data. Failure of a model is a valid scientific result and must be preserved.

Every new model should state variables, dimensions/units where applicable, equations, assumptions, validity regime, baselines, observables, calibration path, failure conditions, provenance, and authorship boundary.

## 1. Minimal SU(5) coupling-running benchmark

### Reason for selection

`gauge-unification-supersymmetry-archaeology.json` already contains a strong representation and renormalization-group contract but still does not choose one route and calculate it through. Pass 002 will choose minimal non-supersymmetric SU(5) as a benchmark, not as a preferred final theory.

### Model

Use the measured Standard Model gauge couplings at a declared reference scale and conventional SU(5) hypercharge normalization:

`g1 = sqrt(5/3) gY`

At one loop:

`d alpha_i^(-1) / d ln(mu) = -b_i/(2 pi)`

or equivalently

`alpha_i^(-1)(mu) = alpha_i^(-1)(mu0) - b_i/(2 pi) ln(mu/mu0)`.

The record must state the Standard Model one-loop coefficients under its convention and source them from authoritative literature.

### Required results

The benchmark must calculate or specify how to calculate pairwise crossing scales, the three-coupling mismatch near the best apparent meeting point, sensitivity to input uncertainties, and the effect of threshold corrections as an explicit missing extension.

It must connect the inferred heavy scale qualitatively or quantitatively to proton-decay expectations without pretending the one-loop crossing alone is a full proton-decay calculation.

### Success / failure

Success does not mean "SU(5) is true." The benchmark succeeds if it gives a reproducible numerical answer for how well minimal SU(5) unifies under stated assumptions.

If the three couplings fail to meet within reasonable uncertainties and no declared threshold structure repairs the mismatch, that negative result must be stated directly.

### Maturity

A calculation using current measured couplings can be parameter-constrained, but the larger Timic/Potato interpretation remains unvalidated. The benchmark's maturity applies only to the selected SU(5) calculation.

## 2. Infinite Soil interacting-dark-sector descendant

### Reason for selection

`great-book-quantum-fields-dark-sector-recovery.json` already separates several possible dark-sector forks but stops before choosing one. Pass 002 will choose one deliberately simple phenomenological interacting-dark-sector model so the Soil idea has a calculable descendant without claiming one physical Soil has been discovered.

### Model

Use a flat FLRW background with pressureless cold dark matter and dark energy. Choose one explicit interaction convention, for example:

`rho_c_dot + 3 H rho_c = +Q`

`rho_de_dot + 3 H (1+w) rho_de = -Q`

with

`Q = beta H rho_c`.

The sign convention must be stated clearly because literature conventions differ.

### Required derivations

Define dimensionless density variables such as `Omega_c` and `Omega_de`, rewrite the system using `N = ln a`, derive the autonomous evolution equations, identify fixed points in the chosen simplified case, state positivity/physical-domain constraints, and recover the uncoupled limit as `beta -> 0`.

The record must identify observables affected by the interaction: expansion history, matter growth, CMB/BAO/SN distances, redshift-space growth, weak lensing, and related probes where appropriate.

### Baseline and falsifier

Lambda-CDM or the uncoupled constant-w model is the baseline. The interacting model must justify its extra parameter by model comparison and must not be called superior from background expansion alone.

The branch fails scientifically if the coupling is non-identifiable, produces unstable/unphysical evolution in the claimed region, or adds no predictive value relative to the baseline.

### Maturity

The autonomous dynamical system is T2. T3 requires actual cosmological parameter constraints from a stated dataset/likelihood or authoritative published constraints imported with provenance.

## 3. Microtubule classical-versus-quantum necessity benchmark

### Reason for selection

`microtubule-tubulin-consciousness-recovery.json` has a good multiscale programme but still lacks a concrete nested-model test that decides whether quantum machinery is needed for a declared microtubule observable.

### Model M0 — classical baseline

Use a damped, driven stochastic mode:

`M q_ddot + Gamma q_dot + K q = F(t) + xi(t)`

with clearly defined displacement/generalized coordinate, effective mass, damping, stiffness, forcing, noise model, resonance frequency and quality factor where applicable.

### Model M1 — open quantum extension

Use a quantum harmonic-mode comparator only after the physical mode is defined:

`H = hbar omega (a^dagger a + 1/2) + H_drive + H_int`

`rho_dot = -(i/hbar)[H,rho] + L_decoh[rho]`.

The exact Lindblad/decoherence terms must correspond to the chosen observable rather than being decorative.

### Quantum necessity gate

The quantum model is scientifically necessary only if all of the following are satisfied:

- a quantum-sensitive observable is declared;
- M0 cannot account for it within uncertainty;
- M1 predicts it quantitatively;
- coherence/interaction/readout timescales are compatible with the proposed mechanism;
- the quantum model improves predictive/model-selection performance after complexity penalties;
- the microscopic effect can be connected to a downstream cellular or neural variable if consciousness relevance is claimed.

Ordinary synchrony, resonance, correlation, or oscillation is not a quantum-specific observable.

### Maturity

The benchmark design is T2. T3 requires real measurements that constrain mode and decoherence parameters. No consciousness claim is promoted merely because a quantum model fits a molecular observable.

## Repository integration

Expected new records:

- `knowledge/science/promising-models/minimal-su5-coupling-running-benchmark-2026-09-13.json`
- `knowledge/science/promising-models/infinite-soil-interacting-dark-sector-benchmark-2026-09-13.json`
- `knowledge/science/promising-models/microtubule-classical-quantum-necessity-benchmark-2026-09-13.json`

Update their canonical owners only with links and concise completion-status notes where needed. Do not rewrite already-strong archaeology records wholesale.

If calculations are reproducible with a small script, add focused Python under `scripts/` or the repository's existing analysis convention rather than embedding unexplained numerical results in prose.

The generated `/science/` catalogue remains the public surface. Do not create a second science database or touch homepage layout.

## Validation

Implementation is complete only when:

- all new JSON parses;
- each benchmark includes provenance, variables, equations, baselines, observables and falsifiers;
- SU(5) states the hypercharge convention and numerical mismatch honestly;
- the dark-sector model recovers the uncoupled limit;
- the microtubule benchmark has an explicit classical null and quantum-necessity gate;
- no benchmark claims validation beyond its actual calculation/data;
- existing science build and portal validation remain green when executable;
- the branch diff contains only science-pass changes and documentation.

## Deferred

Pass 002 does not add further Human Map, Cosmic Potato, Dimensional Door, Door Handshake, Golden Spiral, or Higgs-singlet formalism because dedicated benchmark descendants already exist for those branches.
