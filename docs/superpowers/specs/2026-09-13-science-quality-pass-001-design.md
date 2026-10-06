# Science Quality Pass 001 — Design

**Date:** 2026-09-13
**Status:** approved direction

## Goal

Raise genuinely underdeveloped science branches to the standard already reached by the repository's strongest models. Do this by increasing calculability, observability, baseline comparison and falsifiability — not by adding decorative equations or scientific vocabulary.

The homepage and Potato House visual architecture are out of scope.

## First principle: audit the current records, not stale summaries

Direct inspection shows that two items previously routed as weak models are already substantially developed:

- `knowledge/science/merkaba-counterrotation-oscillator-model.json` contains coupled phase equations, mean/relative coordinates, phase locking, symmetry breaking, order parameters, noise, measurement protocol and a falsifier.
- `knowledge/science/integration-fragmentation-red-blue-dynamics-recovery.json` contains typed subsystem states, coupled dynamics, stability, alternative integration metrics, an empirical programme and explicit failure conditions.

Pass 001 therefore begins by refreshing the current rigor/completion map. It must not spend effort rebuilding models that already meet the T2 standard.

## Canonical quality contract

A serious model should expose: research question; provenance; domain/state space; variables; units; parameters; equations/model class; initial/boundary conditions where relevant; assumptions; validity regime; stability/well-posedness; established baselines; what is project-specific; observables; calibration/identifiability; discriminating prediction or model-selection criterion; falsifier; limiting cases; known gaps; sources; maturity.

Use the existing maturity ladder unchanged:

- T0 metaphor/motif
- T1 defined conceptual model
- T2 internally calculable mathematical toy model
- T3 calibrated or parameter-constrained model
- T4 predeclared quantitative discriminating prediction
- T5 independently replicated theory

No maturity increase is earned by prose alone.

## Deliverable 1 — refresh the rigor matrix

Update `knowledge/science/science-theory-rigor-completion-matrix-2026-09-11.json` rather than creating a competing registry.

For every major model family, inspect its current canonical owner and record:

- `Q=(P,T,D,E,C,O,F,B,N)` component assessment using the existing 0–4 diagnostic rubric;
- strongest current asset;
- largest scientific gap;
- smallest next calculation/data/test that could materially strengthen or reject it;
- work that would be decorative or premature;
- truthful current maturity.

Do not collapse Q into a truth score.

Routing classes remain:

- `A_high_value` — concrete calculation/data/test can strengthen or reject the model;
- `B_structural_value` — useful formalism without claiming a new physical law;
- `C_archaeology_value` — source recovery should precede more physics;
- `D_do_not_inflate` — preserve as symbolic/comparative because more equations would currently confuse categories.

The refreshed audit must recognize Merkaba and Red/Blue as already-developed T2 branches, not first-pass repair targets.

## Deliverable 2 — Starchforce / Spudlight flagship model

The existing branch already has the stock-flow form

`dK/dt = J_in - J_SL - Gamma K`

with a linear release option

`J_SL = eta K`

plus relaxation time, steady state, runway and nonlinear-release candidates. Its real gap is not mathematics but lack of one calibrated flagship domain.

Pass 001 chooses **potato plant carbon/starch storage and mobilization** as the primary empirical interpretation because it gives the Potato/Starch vocabulary a measurable biological domain without inventing a new force.

Minimal model:

`dK/dt = J_in(t) - eta K - Gamma K`

where `K` is a measurable starch/carbohydrate pool or declared proxy, `J_in` is storage input, `eta` is mobilization/release rate and `Gamma` is other loss/turnover. Units must be explicit.

Only if data justify it, compare the saturating release form

`J_SL(K) = J_max K/(K + K_half)`

against the linear model.

Required additions: measurement model; units; initial-condition convention; parameter identifiability; calibration method; uncertainty; held-out comparison where possible; baseline models; model-selection criterion; null-result interpretation; external plant-physiology provenance.

Baselines should include a naive/persistence baseline, a simple ordinary stock-flow baseline, the linear storage-release model, and the nonlinear model only if it earns its extra complexity.

A successful fit validates only the biological model. It does not validate a universal Starchforce. T3 is permitted only if real data are fitted and parameter uncertainty is recorded. Otherwise this branch remains T2.

## Deliverable 3 — Field of Life scientific descendant

The historical Great Book material compares Potato to an excitation in a `Field of Life`. Keep that historical statement separate from any later scientific model.

Pass 001 will **not** invent a fundamental life field. It will create a dedicated scientific descendant using conventional reaction–diffusion/ecological field mathematics.

Minimal family:

`partial_t phi = D nabla^2 phi + f(phi; theta) + S(x,t)`

where `phi(x,t)` is a measurable density/concentration/occupancy/proxy, `D` is a transport coefficient, `f` is a declared local reaction/growth/decay law and `S` is an external source/sink. Initial and boundary conditions must be explicit.

A logistic comparator is allowed:

`f(phi) = r phi (1 - phi/K)`

but must be labeled established external mathematics rather than a Potato law.

The first scientific question is: can one specified spatial life-pattern dataset be described or predicted by a field model with explicit variables, dynamics and observables, and does the project-specific mapping add anything beyond ordinary reaction–diffusion/ecological models?

Required boundaries:

- historical Field of Life metaphor remains T0 unless a separate empirical model is specified;
- reaction–diffusion equations are external established mathematics;
- a project-specific descendant begins only when measurable `phi`, dataset, mechanism and prediction are declared;
- fitting a reaction–diffusion model is not evidence for a metaphysical universal field;
- QFT language is not used unless a real QFT action, field content, symmetry, quantization and observable are defined.

Compare against local-only dynamics, diffusion-only dynamics, a standard reaction–diffusion model and a network-spread model when the domain is graph-like. If spatial coupling adds no predictive value over local dynamics, the field interpretation is unnecessary for that application.

Historical metaphor: T0. Defined calculable descendant: at most T2. Fitted descendant: potentially T3.

## Provenance rule

Maintain strict distinctions among:

- Tim-authored/recovered equations;
- project-attested equations with unresolved first source;
- later archive-generated mathematics;
- established external equations;
- new Pass-001 modelling decisions.

No new equation from this pass may be silently attributed to Tim.

## Repository integration

Canonical science content remains under `knowledge/science/`; `/science/` remains generated through the existing build/catalog pipeline.

Likely changes:

- modify `knowledge/science/science-theory-rigor-completion-matrix-2026-09-11.json`;
- modify `knowledge/science/spudlight-theory-and-equations.json` and/or add one narrowly scoped linked empirical/formulation record;
- create one dedicated `knowledge/science/field-of-life-*.json` descendant/owner record;
- update `knowledge/science/science-model-registry.json`, `science-master-index.json` and relevant crosswalks only where discoverability requires it;
- add focused analysis code only if real data/calculation warrants it.

Do not modify homepage layout or Potato House wave-design files.

## Validation

Pass 001 is complete only when:

1. changed JSON parses;
2. the existing site/science build succeeds;
3. the existing science portal validator succeeds;
4. the rigor matrix no longer routes Merkaba or Red/Blue as unbuilt priority models;
5. Starchforce/Spudlight has one explicit flagship empirical route with units, baselines, calibration/failure rules and truthful maturity;
6. Field of Life cleanly separates historical metaphor from calculable scientific descendant;
7. no record claims empirical validation without actual data/results;
8. archive-generated equations are labeled as such;
9. generated public science pages preserve epistemic status.

## Deferred to later passes

Human Map/consciousness calibration; full UPT EFT repair; GUT/SUSY route selection; Infinite Soil dark-sector fitting; a new fundamental Starchforce; literal universal Field of Life physics; extra Merkaba or Red/Blue mathematics without an empirical need.

The rule is simple: deepen only where the next step creates scientific constraint.
