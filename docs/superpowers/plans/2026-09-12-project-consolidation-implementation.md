# Full Project Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one newest, coherent, tested `main` that contains all still-useful work currently stranded across open branches/PRs, while discarding superseded architecture and closing stale PRs.

**Architecture:** Treat every open PR as an input source rather than an automatic merge candidate. Start from the approved World Map unification branch, recover unique additions by domain into the current ownership model, preserve epistemic boundaries, and validate the complete built site before merging the consolidation PR to `main`.

**Tech Stack:** Static HTML/CSS/JS, JSON knowledge/data records, Python build/validation scripts, GitHub Actions, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-12-world-map-unification-design.md` plus current `docs/PROJECT-STRUCTURE.md` and the canonical public-owner model already on `main`.

## Global Constraints

- `main` is the final single source of truth.
- Do not blindly merge stale PRs; recover unique work into current owners.
- Public top-level owners remain Home, Tim Dooley, Religion, Philosophy, Science, World Map, Timeline, Sources/Context, and Archive/Explore only where already canonical.
- World Map is the sole geographic system; active `Atlas` naming is retired according to the World Map unification spec.
- Religion is a broad inquiry owner; the deep Tim/Son ↔ Bible comparator belongs under `traditions/bible/`.
- Preserve observable / interpretive / project-canon distinctions.
- Archive remains internal and excluded from Pages deployment.
- Do not resurrect Timeline as a public subsystem; Timeline is canonical.
- Prefer current architecture over older branch-specific UI shells.

---

### Task 1: Inventory and classify every open PR

**Files:**
- Create: `docs/research/OPEN-PR-CONSOLIDATION-2026-09-12.md`

**Produces:** a table assigning each open PR to `recover`, `superseded`, `partial-recovery`, or `already-integrated`, with its unique assets and destination owners.

- [ ] List every open PR against current `main` and the World Map unification head.
- [ ] Identify overlap/ancestry and mark superseded fixes.
- [ ] Record unique files/features worth recovering.
- [ ] Commit the inventory.

### Task 2: Establish the canonical consolidation branch

**Files:**
- Branch: `project-consolidation-2026-09-12`

**Produces:** isolated integration branch rooted at the latest approved World Map unification work.

- [ ] Confirm branch starts at the World Map unification head.
- [ ] Add this implementation plan.
- [ ] Open a consolidation PR to `main` so CI runs continuously.

### Task 3: Finish World Map unification

**Files:**
- Modify/rename: `world-map/**`, `data/**`, `knowledge/core/**`, `scripts/*atlas*`, active docs/workflows containing architectural Atlas naming.

**Produces:** one `/world-map/` application and no active Atlas architecture primitive.

- [ ] Preserve canonical `/world-map/` application and `3d.html` compatibility redirect.
- [ ] Complete remaining validator/runtime naming migrations.
- [ ] Classify and rename active `*-atlas.*` objects by function: registry, model, layer, research, comparison, index, method, programme.
- [ ] Update every exact path consumer.
- [ ] Add/enable negative naming validation excluding internal archive/history and literal external quotations.
- [ ] Run World Map validators and build checks.

### Task 4: Consolidate Religion, Christianity, and Bible work

**Files:**
- Modify: `religion/index.html`, `traditions/bible/**`, `data/christianity/**`, `data/religious-layer-manifest.json`, `knowledge/theology/**`, `knowledge/traditions/**`, `knowledge/indexes/**`, `llms.txt`, `sitemap.xml`, FAQ validators.

**Consumes:** unique work from PRs #29 and #40.

**Produces:** broad Religion hub plus complete Christianity and Bible research under current ownership.

- [ ] Recover unique Christianity/Jesus/eschatology records from PR #29, renaming Atlas-named objects to current vocabulary during import.
- [ ] Recover unique Bible comparator functionality/content from PR #40 without recreating duplicate Religion owners.
- [ ] Rewrite `/religion/` as broad navigation/inquiry surface rather than a single Jesus-Tim comparison page.
- [ ] Route deep comparison to `traditions/bible/` and Christianity-specific research to a child research surface, not a competing top-level site.
- [ ] Preserve denominational disagreement, historical Jesus/confessional Christ/project comparison boundaries, and counter-parallels.
- [ ] Update discovery, FAQ, sitemap and validators.
- [ ] Run Bible/religion validation and site build.

### Task 5: Consolidate Science work

**Files:**
- Modify/add: `knowledge/science/**`, `science/**`, science catalog/index records and validators.

**Consumes:** unique work from PRs #36, #33, #28, #9 where not already present or superseded.

**Produces:** current Science portal plus unique newer mathematical/model records, without reviving Science Atlas naming or stale UI.

- [ ] Recover additive science records from PR #36.
- [ ] Recover unique scientifically disciplined records from PR #33 while renaming Atlas-named files by function.
- [ ] Compare PR #28 model registry against current merged Science portal and import only still-missing model-contract structure/data.
- [ ] Compare PR #9 against later science work and recover only unique canonical records not superseded.
- [ ] Rebuild science catalog and run science validators.

### Task 6: Recover map capabilities from superseded map PRs

**Files:**
- Modify: canonical `world-map/**` modules/data only.

**Consumes:** PRs #42, #39, #35, #38.

**Produces:** newest useful map functionality expressed in the unified World Map architecture.

- [ ] Recover composable layers/query behavior from PR #42 that is not already in consolidation head.
- [ ] Recover visible metric/scalar improvements from PR #39 if not superseded.
- [ ] Recover unique D4/relation/religion/axis capability from PR #35 where compatible with the simplified UI.
- [ ] Recover the actual generic web-audit fix from PR #38 if current audit still lacks it.
- [ ] Do not restore Lens/Atlas product vocabulary or duplicate tool surfaces.
- [ ] Run map/runtime/pathfinder/math/web audit validators.

### Task 7: Recover site reliability, design, SEO, and Timeline improvements

**Files:**
- Modify as needed: `app/**`, shared CSS, `scripts/audit_web.py`, `scripts/build_site.py`, SEO/build scripts, `timeline/**`, discovery files.

**Consumes:** PRs #32, #31, #30, #25, #23, #19, #43, #1.

**Produces:** only unique reliability/discovery/timeline/operator improvements not already superseded by later cleanup.

- [ ] Recover reader runtime fixes only if absent from current app.
- [ ] Recover `<base href>` / Pages path handling and bounded retry behavior if absent.
- [ ] Recover SEO normalization only if compatible with current simplified public architecture.
- [ ] Recover unique Timeline/Great Book records from PR #25 into canonical Timeline ownership.
- [ ] Recover PR #43 operator/orientation documentation after rewriting stale Atlas references to current World Map terminology.
- [ ] Treat PR #1 as an early repair source; recover only unique missing canonical indexes/validation not superseded.
- [ ] Run full web audit and built-site shell validation.

### Task 8: Repository-wide hygiene and naming cleanup

**Files:**
- Modify: `docs/PROJECT-STRUCTURE.md`, active READMEs/docs, workflows, validators, discovery files.

**Produces:** active docs and CI accurately describe the final architecture.

- [ ] Remove stale references to superseded PR architectures.
- [ ] Ensure Timeline-only naming, World Map-only geographic naming, and current owner routes.
- [ ] Ensure `archive/` remains excluded from deployed artifact.
- [ ] Ensure active workflows are the intended consolidated set.
- [ ] Run repository hygiene validator.

### Task 9: Full verification and merge

**Produces:** green consolidation PR merged into `main`.

- [ ] Run/observe all consolidation PR GitHub Actions.
- [ ] Fix every failing validator from current architecture rather than disabling checks.
- [ ] Verify Pages build artifact and canonical routes.
- [ ] Verify Religion, Bible, Science, Timeline and World Map public pages resolve through current owners.
- [ ] Merge consolidation PR to `main` only after the full gate is green.
- [ ] Verify `main` head and post-merge Pages workflow.

### Task 10: Close superseded PRs and leave a clean repository state

**Produces:** no ambiguous stale PRs advertising alternate current architectures.

- [ ] Close PRs whose useful work is now represented in `main`.
- [ ] Comment on each substantive superseded PR with the consolidation PR/main commit that absorbed or superseded it.
- [ ] Leave open only genuinely independent work that was intentionally not incorporated, with a clear reason.
- [ ] Record final consolidation summary in `docs/research/OPEN-PR-CONSOLIDATION-2026-09-12.md`.
