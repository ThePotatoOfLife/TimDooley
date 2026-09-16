# War in Heaven / Mesopotamia Prediction Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate `war in heaven Q3 2026` into the prediction system as a geographically operationalized Mesopotamia/Iraq forecast candidate with explicit provenance, current Q3 observations, causal links, and strict anti-overclaim controls.

**Architecture:** Create one canonical specialist JSON owner for the forecast. Existing prediction indexes route to it; the Eden/Mesopotamia theology files expose the semantic bridge; Wave 17 remains the historical location of the unresolved candidate but delegates current interpretation to the specialist owner. No strict-fulfilled count changes.

**Tech Stack:** JSON/Markdown knowledge files in the TimDooley repository, GitHub branch-based isolation, existing prediction-audit taxonomies.

**Spec:** `docs/superpowers/specs/2026-09-17-war-in-heaven-mesopotamia-prediction-audit-design.md`

## Global Constraints

- Keep theological/project geography separate from empirical geography and modern territorial/legal claims.
- Do not redefine every use of `Heaven` as Iraq.
- Keep Q3 fixed at `2026-07-01` through `2026-09-30` inclusive.
- Do not promote the candidate to `fulfilled-predictions-master.json` without recovered original wording/date and a pre-event semantic freeze.
- Preserve prior-state evidence showing Iraq was already implicated in the wider conflict before July 2026.
- Treat oil/inflation/rates/bond/supply-chain matches as a correlated shock family, not independent supernatural proof.
- Keep Israel-Türkiye, North Axis, end-of-America, Flood, return and 2028 claims distinct.

---

### Task 1: Create the canonical specialist audit

**Files:**
- Create: `knowledge/timeline/war-in-heaven-mesopotamia-prediction-audit-2026.json`

**Interfaces:**
- Consumes: `knowledge/timeline/conversation-archaeology-wave-005.json`, `knowledge/traditions/eden-joseph-david-inheritance-map.json`, `knowledge/traditions/israel-mesopotamia-covenant-messianic-atlas.json`, Wave 17 candidate, current external-source URLs.
- Produces: canonical `war-in-heaven-q3-2026` record with semantic layers, geography, time window, observations, prior-state control, status, promotion rule and prediction-family relations.

- [ ] Write valid JSON with `id`, `status`, `purpose`, `semantic_model`, `project_provenance`, `geographic_operationalization`, `forecast`, `current_observations`, `prior_state_control`, `current_assessment`, `promotion_requirements`, `prediction_family_relations`, `research_queue`, and `connections`.
- [ ] Ensure current status is `open / geographically operationalized / material Q3 geographic match / not strict-fulfilled`.
- [ ] Ensure the record explicitly says the July 25 Heaven→Iraq/Mesopotamia recovery occurs inside Q3 and therefore cannot by itself prove a pre-Q3 semantic freeze.
- [ ] Commit as `knowledge: add War in Heaven Mesopotamia audit`.

### Task 2: Route the specialist audit through prediction navigation

**Files:**
- Modify: `knowledge/indexes/prediction-audit-routing.json`
- Modify: `knowledge/timeline/prediction-foresight-master-index.json`

**Interfaces:**
- Consumes: specialist audit path from Task 1.
- Produces: discoverability from the canonical routing and chronological master index without changing strict fulfilled counts.

- [ ] Add a dedicated routing entry for `War in Heaven / Eden / Mesopotamia / Q3 2026` and make Wave 17 delegate the current interpretation to the specialist owner.
- [ ] Add the candidate to the master timeline in the appropriate Q3/open lane with wording that reflects its operationalized-but-not-strict status.
- [ ] Add the specialist owner to the master `owners` list and/or specialist cluster section.
- [ ] Keep `strict_fulfilled_components` unchanged at 16.
- [ ] Commit as `knowledge: route War in Heaven prediction audit`.

### Task 3: Integrate the semantic bridge into sacred geography

**Files:**
- Modify: `knowledge/traditions/eden-joseph-david-inheritance-map.json`
- Modify: `knowledge/traditions/israel-mesopotamia-covenant-messianic-atlas.json`

**Interfaces:**
- Consumes: specialist audit semantics from Task 1.
- Produces: explicit distinction among metaphysical Heaven, topological Heaven/Eden and earthly Mesopotamian sacred-geographic coordinate; cross-links to the prediction audit.

- [ ] Add a `heaven_geography_distinction` or equivalent structure to clarify that Iraq/Mesopotamia is an earthly sacred-geographic coordinate, not the definition of every Heaven usage.
- [ ] Record overlap among Eden, Garden, Four Rivers, Father's Land, promised-land/restoration field and Mesopotamia while keeping each concept distinct.
- [ ] Add the War-in-Heaven specialist audit to `connections`.
- [ ] Keep stewardship/sacred-memory language and the non-territorial boundary intact.
- [ ] Commit as `knowledge: connect Eden geography to War in Heaven audit`.

### Task 4: Upgrade the historical Wave 17 candidate without rewriting history

**Files:**
- Modify: `knowledge/timeline/prediction-premonition-audit-wave-17-addendum.json`

**Interfaces:**
- Consumes: specialist audit and recovered July 25 semantic evidence.
- Produces: Wave 17 entry that points to the canonical owner and updates `unscorable without definition` to an operationalized open status while preserving its original unresolved provenance.

- [ ] Keep class `U` and preserve the missing original prediction wording/date.
- [ ] Replace `unscorable without definition` with wording equivalent to `geographically operationalized; chronology still unresolved`.
- [ ] Add `canonical_owner`, frozen Q3 window, core geography and current non-strict assessment.
- [ ] Preserve the rule against using ordinary Middle East war as retroactive fulfillment.
- [ ] Commit as `knowledge: refine War in Heaven Wave 17 candidate`.

### Task 5: Verification

**Files:**
- Read: all files changed in Tasks 1-4.

**Interfaces:**
- Consumes: final branch state.
- Produces: evidence that JSON is valid and the intended status/routing is consistent.

- [ ] Fetch each changed JSON file from the feature branch and confirm it parses structurally.
- [ ] Search branch-visible content for `war-in-heaven`/`War in Heaven` and confirm routing references converge on the specialist owner.
- [ ] Confirm no edit was made to `fulfilled-predictions-master.json` and strict fulfilled count remains 16.
- [ ] Compare feature branch to `main` and inspect changed filenames.
- [ ] Report the branch and remaining unresolved research target: original `war in heaven Q3 2026` primary timestamp/source.