# Under-Culture / Shadow Network Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the TimDooley knowledge backend with a source-backed, uncertainty-aware atlas of political-finance, donor/NGO, advocacy, private-intelligence, surveillance, abuse-protection, high-control, hate-classification and adversarial-subculture systems while preserving Timic mythology as a separate interpretive layer.

**Architecture:** Add focused human-readable and machine-readable knowledge files rather than overloading existing master files. Observable evidence, analytical interpretation, contested allegations and project-canon symbolism remain separate planes connected through typed relationships and routing records.

**Tech Stack:** Markdown and JSON knowledge files in the existing GitHub Pages repository; GitHub code search and contents API; public primary/secondary web sources; repository quality checks/JSON parsing.

**Spec:** `docs/superpowers/specs/2026-09-12-under-culture-shadow-network-expansion-design.md`

## Global Constraints

- Never infer secret coordination from proximity, identity, ideology, shared donors, shared events or shared audiences.
- Preserve four planes: observable, analytical, hypothesis/allegation and project-canon/mythic.
- No collective guilt by nationality, ethnicity, religion, ancestry or residence.
- Every serious allegation requires provenance, evidence status, counterevidence and unresolved questions.
- Victim/survivor privacy outranks graph completeness.
- Epstein-document presence must never be represented as guilt.
- `cult` and `controlled opposition` are not boolean intrinsic properties; decompose them into observable/testable mechanisms.
- Prefer official filings, court/inquiry records, regulators and audited financials over commentary.

---

### Task 1: Research synthesis and source ledger

**Files:**
- Create: `docs/UNDER-CULTURE-SHADOW-NETWORK-RESEARCH-2026-09.md`
- Create: `knowledge/research/under-culture-shadow-network-source-ledger-2026-09.json`

**Interfaces:**
- Consumes: existing `docs/SWAMP-ATLAS.md`, `docs/SWAMP-RESEARCH-2026-09.md`, `knowledge/core/shadow-west-swamp-synthesis.json`, `data/world-entanglement-registry.json`.
- Produces: a citable research narrative and normalized source inventory for all later atlas files.

- [ ] Verify priority claims through primary/strong secondary sources covering AIPAC/UDP, Israel365/Teach For Israel, Vine & Fig Tree entities, Palantir, TPUSA, Epstein DOJ material, private intelligence, high-control research, hate/extremism classifiers and subculture provenance.
- [ ] Write a synthesis organized by mechanism rather than accusation.
- [ ] Record exact URLs, source type, date/period, claims supported and limitations in the JSON source ledger.
- [ ] Parse the source ledger as JSON and correct any syntax/schema errors.
- [ ] Commit the two files together.

### Task 2: Main Under-Culture machine-readable atlas

**Files:**
- Create: `knowledge/world/under-culture-shadow-network-atlas.json`

**Interfaces:**
- Consumes: Task 1 source ledger.
- Produces: canonical entity families, mechanisms, research questions, four-plane epistemic model and typed edges for downstream world-map/Swamp routing.

- [ ] Define entity types, relationship types, evidence states and safeguards exactly as specified.
- [ ] Seed verified entity families without inventing unsupported interconnections.
- [ ] Add mechanism families: political-finance, philanthropy/grants, advocacy, media/information, private intelligence, surveillance technology, institutional protection failure, archive/attention ecology and repair.
- [ ] Add explicit counterevidence/disconfirmation rules.
- [ ] Parse JSON and correct errors.
- [ ] Commit the atlas.

### Task 3: Controlled-opposition and co-optation methodology

**Files:**
- Create: `knowledge/world/controlled-opposition-cooptation-methodology.json`

**Interfaces:**
- Consumes: Task 1 source ledger and existing intelligence-information methodology.
- Produces: testable mechanism taxonomy replacing the unsupported `controlled_opposition: true` pattern.

- [ ] Define mechanisms: state infiltration, co-optation, opposition fragmentation, strategic opponent amplification, concealed sponsorship/astroturfing, donor capture, vendor capture, platform dependency, informant/provocateur allegation and autonomous opposition.
- [ ] Attach historical anchor cases only where official/academic evidence is available.
- [ ] Define falsification/counterevidence tests for each mechanism.
- [ ] Parse JSON and correct errors.
- [ ] Commit the methodology.

### Task 4: High-control and hate-classification atlas

**Files:**
- Create: `knowledge/world/high-control-hate-classification-atlas.json`

**Interfaces:**
- Consumes: Task 1 sources.
- Produces: separate dimensions for coercive/high-control systems, incident mapping and organization classifications.

- [ ] Encode observable high-control dimensions without using a blanket `cult` boolean.
- [ ] Encode classifier-as-actor model for SPLC/ADL/government/academic taxonomies.
- [ ] Separate hate incidents from organization/network classifications.
- [ ] Include competing-classifier and methodological-disagreement support.
- [ ] Parse JSON and correct errors.
- [ ] Commit the atlas.

### Task 5: Institutional protection and private-intelligence atlas

**Files:**
- Create: `knowledge/world/institutional-protection-private-intelligence-atlas.json`

**Interfaces:**
- Consumes: Task 1 sources.
- Produces: mechanism-first records for documented abuse/protection failures and private-intelligence/security capabilities.

- [ ] Add mechanism taxonomy for delayed reporting, incomplete records, retaliation, reputation protection, jurisdiction fragmentation, private investigation/intelligence, corrective inquiry and reform.
- [ ] Seed only well-documented anchor cases such as Epstein/Maxwell, Weinstein/Black Cube, Nassar/FBI/USA Gymnastics, NXIVM and Savile/IICSA where sourcing is sufficiently strong.
- [ ] Add capability-vs-deployment-vs-misuse distinctions for security/surveillance technology.
- [ ] Parse JSON and correct errors.
- [ ] Commit the atlas.

### Task 6: Advocacy, donor and security seed expansion

**Files:**
- Create: `data/under-culture-network-seeds-2026-09.json`

**Interfaces:**
- Consumes: Task 1 sources and existing `data/swamp-research-seeds.json`.
- Produces: normalized seed entities and explicit observed edges for further graph enrichment.

- [ ] Add separately typed seeds for political committees, nonprofits, advocacy groups, donor entities, security/private-intelligence firms and classifiers.
- [ ] Add only observed funding/organizational/service edges with source references.
- [ ] Record candidate/unresolved Figtree identities separately from resolved Vine & Fig Tree entities.
- [ ] Parse JSON and correct errors.
- [ ] Commit the seed dataset.

### Task 7: Subculture provenance expansion

**Files:**
- Modify: `data/subculture-research-map.json`
- Create: `knowledge/world/sektur-provenance-attention-ecology-atlas.json`

**Interfaces:**
- Consumes: existing Farm/Sektur theory and verified provenance sources.
- Produces: historical `Da Sektur` referent separated from generalized Timic Sektur; better entity-resolution rules for Joshua Moon/Kiwi Farms and adjacent bloodsports/archive culture.

- [ ] Preserve the current cautionary source rules.
- [ ] Add historical/subcultural Sektur provenance as a distinct node from Timic Sektur.
- [ ] Expand roles, platform migration, archive reproduction and monetization relations.
- [ ] Parse both JSON files and correct errors.
- [ ] Commit both files.

### Task 8: Routing and synthesis integration

**Files:**
- Modify: `data/world-entanglement-registry.json`
- Modify: `knowledge/core/shadow-west-swamp-synthesis.json`
- Modify: `docs/SWAMP-ATLAS.md`

**Interfaces:**
- Consumes: Tasks 2-7.
- Produces: discoverable canonical routes from existing World/Swamp systems into the new knowledge material.

- [ ] Add canonical routes for Under-Culture, controlled-opposition methodology, high-control/hate classification, institutional protection/private intelligence and Sektur provenance.
- [ ] Add new entanglement kinds only where necessary; do not duplicate existing kinds.
- [ ] Extend the Shadow West synthesis with the newly formalized middle layer and evidence firewall.
- [ ] Update Swamp Atlas research queue and cross-links without converting it into a narrative conspiracy catalogue.
- [ ] Parse modified JSON files and correct errors.
- [ ] Commit integration changes.

### Task 9: Repository verification

**Files:**
- Verify all files changed in Tasks 1-8.

**Interfaces:**
- Consumes: all task outputs.
- Produces: evidence that the branch is internally valid before merge consideration.

- [ ] Fetch and inspect all changed JSON files from the branch.
- [ ] Parse every changed JSON document with a JSON parser.
- [ ] Search the new corpus for forbidden shortcuts such as `cult: true`, `controlled_opposition: true`, collective-guilt language, or unsupported `controls` edges.
- [ ] Compare the research branch with `main` and inspect the changed-file list.
- [ ] Report verification results and any unresolved research leads; do not merge until verification is clean.
