# Site House Presentation Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the site-wide House overhaul by converging legacy reader presentation, adding a safe utility shell, deriving continuation paths from House authority, enforcing CSS ownership, and completing responsive/accessibility/deployment hardening.

**Architecture:** Keep `data/house/public-surfaces.json` as the route/shell authority and keep specialist applications in control of their geometry. Editorial and long-form readers receive shared House identity plus a House-scoped compatibility layer; utilities receive a namespaced compact escape; related/continuation links are generated from registry parentage/Rooms rather than hand-written mini-navs. Validation moves from page allowlists toward policy derived from shell type and source/runtime behavior.

**Tech Stack:** Static HTML/CSS/JavaScript, Python build/validation scripts, JSON House registry, GitHub Pages/Actions.

**Spec:** `docs/superpowers/specs/2026-09-17-site-house-navigation-overhaul-design.md`

## Global Constraints

- The five primary Doors remain exactly: Tim Dooley, Religion, Philosophy, Science, World.
- Great Book remains a global work/path, never a sixth Door.
- The House owns orientation; page families own presentation; canonical records own truth.
- Do not impose editorial widths or global CSS resets on World Map, Bible, Timeline, Explore, or TTS.
- Keep compatibility/diagnostic routes minimal and `noindex`.
- Preserve canonical content, semantic IDs, application roots and existing specialist interaction contracts.
- Prefer policy-derived coverage over page-ID allowlists.
- Every behavior change follows RED → GREEN → full-suite verification.

---

## File responsibility map

### Shared visual layers
- `app/site-system.css` — global House tokens, editorial shell, focus/mobile behavior.
- `app/reader.css` — existing legacy reader integration point.
- `app/reader-v2.css` — House-scoped compatibility styling for older editorial/long-form readers only.
- `app/specialist-house.css` — namespaced specialist House escape; no global resets.
- `app/utility-house.css` — new namespaced utility House escape for TTS and future self-contained tools.

### House derivation/build
- `scripts/house_shell.py` — shell fragments, specialist/utility escape fragments, continuation links.
- `scripts/build_site.py` — registry-driven shell projection; no presentation allowlists.
- `scripts/house_public_surfaces.py` — route/parent/Room resolution.

### Validation
- `scripts/check_css_namespace_collisions.py` — shared/global CSS ownership gate.
- `scripts/validate_generated_navigation.py` — shell-type navigation contract.
- `scripts/validate_house_coverage.py` — authored/deployed ownership coverage.
- `scripts/validate_public_navigation.py` — built public navigation correctness.
- `scripts/validate_seo_pipeline.py` — canonical/indexability/sitemap authority.

---

### Task 13: Activate the House-scoped reader convergence layer

**Files:**
- Modify: `app/reader.css`
- Existing: `app/reader-v2.css`
- Existing test: `scripts/check_css_namespace_collisions.py`

**Interfaces:**
- Consumes: `.site-housebar ~ main` emitted by build projection.
- Produces: all legacy readers already loading `app/reader.css` inherit `reader-v2.css` without per-page edits.

- [x] **Step 1: Verify RED gate**

Run/observe:

```bash
python scripts/check_css_namespace_collisions.py
```

Expected before fix: `app/reader.css must import the House-scoped reader-v2.css convergence layer`.

- [x] **Step 2: Add the minimal import**

At the start of `app/reader.css`:

```css
@import url("layout-guard.css");
@import url("reader-v2.css");
```

- [ ] **Step 3: Verify GREEN and the full workflow**

Expected: CSS namespace check passes and all downstream build/reader/navigation checks run.

- [x] **Step 4: Commit**

Commit: `fix: activate House reader convergence layer`.

---

### Task 14: Make reader-v2 adoption measurable by family

**Files:**
- Modify: `scripts/check_css_namespace_collisions.py`
- Modify: `scripts/validate_generated_navigation.py` only if built-output assertions are clearer there.
- Inspect: registered editorial/long-form surfaces under `science/`, `tim-dooley/`, `faq/`, `context/`, `traditions/`, standalone long-form routes.

**Interfaces:**
- Consumes: active surface rows and built House projection.
- Produces: policy-derived assertions proving older reader families are actually beneath the House shell and protected by reader-v2 where they rely on legacy reader CSS.

- [ ] **Step 1: Write failing policy assertion**

Derive all active source-backed `editorial`/`longform` surfaces. For pages whose authored source loads `app/reader.css`, require the shared reader integration chain to include `reader-v2.css`; do not maintain a list of page IDs.

- [ ] **Step 2: Run the focused validator and confirm any uncovered family**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/validate_generated_navigation.py
```

- [ ] **Step 3: Fix only uncovered integration points**

Use one shared import/projection path rather than adding one stylesheet link to every page.

- [ ] **Step 4: Build and inspect representative outputs**

Inspect at least:

```text
/science/quantum/
/science/spudlight/
/tim-dooley/evidence/
/faq/
/traditions/vesica/
/context/culture/
```

Require House bar, breadcrumbs, unchanged reader root/content hooks, and no specialist styling leakage.

- [ ] **Step 5: Commit**

```bash
git commit -m "test: enforce reader convergence by shell policy"
```

---

### Task 15: Converge Tim dossiers and FAQ without flattening content layouts

**Files:**
- Modify: `app/reader-v2.css`
- Modify: Tim dossier HTML only where local global-shell styles cannot be safely overridden.
- Modify: `faq/index.html`, `faq/all/index.html`, `faq/all/god/index.html` only where duplicated shell ownership remains.
- Modify: `scripts/check_css_namespace_collisions.py`

**Interfaces:**
- Consumes: shared House shell + reader-v2.
- Produces: one typography/surface rhythm while preserving dossier-specific and FAQ-specific components.

- [ ] **Step 1: Add RED checks for prohibited shell ownership**

For active editorial/long-form source files, detect unscoped inline/global declarations that recreate site-level `:root`, `body`, `.site-*`, or generic global navigation ownership. Allow component-local selectors and documented legacy exceptions only while they are actively being migrated.

- [ ] **Step 2: Migrate Tim dossier family first**

Remove/neutralize only global theme/nav duplication. Keep dossier grids, evidence cards, charts, semantic IDs and page-specific modules intact.

- [ ] **Step 3: Migrate FAQ family**

Move shared background/type/nav concerns to House/reader-v2; keep question lists, filters and FAQ content rules local.

- [ ] **Step 4: Verify representative pages and full suite**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/build_site.py
python scripts/validate_reader_surfaces.py
python scripts/validate_generated_navigation.py
```

- [ ] **Step 5: Commit by family**

Use separate Tim and FAQ commits if both require source edits.

---

### Task 16: Give TTS a geometry-safe utility House escape

**Files:**
- Create: `app/utility-house.css`
- Modify: `scripts/house_shell.py`
- Modify: `scripts/build_site.py`
- Modify: `scripts/validate_generated_navigation.py`
- Preserve: `tools/tts/index.html` application geometry/hooks.

**Interfaces:**
- Produces:
  - `render_utility_house_escape(root: Path, surface_id: str, *, from_route: str) -> str`
  - registry-driven projection for active `shell_type == "utility"` surfaces.

- [ ] **Step 1: Add failing utility shell assertion**

For `/tools/tts/`, built output must contain:

```text
data-house-surface="tts"
class="site-utility-house"
Home/House link
```

and must retain the TTS application root/control markers.

- [ ] **Step 2: Add namespaced CSS only**

`app/utility-house.css` may style only `.site-utility-house...`; it must not define `:root`, `html`, `body`, generic `a`, `.nav`, `.card`, or app geometry.

- [ ] **Step 3: Add renderer and registry-driven projection**

Mount the fragment into the utility page without adding `site-system.css` or changing body sizing.

- [ ] **Step 4: Run TTS + public navigation/build checks**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add compact House escape to utility surfaces"
```

---

### Task 17: Add a shared continuation layer: Up / Beside / Across / Deeper

**Files:**
- Modify: `scripts/house_shell.py`
- Modify: `scripts/house_public_surfaces.py` only if a small derivation helper belongs there.
- Modify: `scripts/build_site.py`
- Modify: `scripts/validate_generated_navigation.py`
- Modify: `app/site-system.css`

**Interfaces:**
- Produces: `render_continuation_routes(root: Path, surface_id: str) -> str`.

**Derivation rules:**
- **Up** = `primary_parent`.
- **Beside** = nearest active siblings sharing `primary_parent` and compatible navigation group.
- **Across** = strongest active route sharing a canonical Room but living under another primary parent/branch.
- **Deeper** = active child route, preferring same Room/navigation group.
- Omit empty directions; never fabricate links.

- [ ] **Step 1: Write failing deterministic helper tests**

Prove a known surface gets an Up route and that no generated direction points back to itself or to inactive/redirect/diagnostic routes.

- [ ] **Step 2: Implement derivation without hard-coded page IDs**

Tie-breaking must be deterministic using registry order/canonical route.

- [ ] **Step 3: Render after content on editorial/long-form pages**

Do not inject into specialists/utilities/redirects/diagnostics.

- [ ] **Step 4: Add compact responsive CSS**

Use the existing `.site-related` family or a named continuation component; do not create another global nav system.

- [ ] **Step 5: Validate graph correctness and build output**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat: derive contextual continuation paths from House authority"
```

---

### Task 18: Turn CSS ownership warnings into enforceable policy

**Files:**
- Modify: `scripts/check_css_namespace_collisions.py`
- Modify active CSS/source files only when the new gate identifies real ownership conflicts.

**Interfaces:**
- Consumes: shell type from House registry.
- Produces: CI failure when active editorial/long-form pages recreate global site-level themes/navigation outside approved shared files.

- [x] **Step 1: Define approved global owners**

At minimum:

```text
app/site-system.css
app/style.css (legacy archive/application ownership only)
app/reader.css (integration, not global shell)
app/reader-v2.css (House-scoped selectors only)
app/specialist-house.css (namespaced only)
app/utility-house.css (namespaced only)
```

- [x] **Step 2: Add RED scan of active registered source pages**

Detect newly introduced inline `:root`/`body`/generic site-nav ownership in editorial/long-form surfaces. Exempt documented component-local scopes, specialists, utilities and diagnostics.

- [x] **Step 3: Remove or scope violations until GREEN**

Prefer deleting redundant global blocks now owned by `site-system.css` over copying them into another stylesheet.

- [x] **Step 4: Commit**

```bash
git commit -m "test: enforce shared CSS ownership across public readers"
```

---

### Task 19: Responsive and accessibility hardening across shell families

**Files:**
- Modify: `app/site-system.css`
- Modify: `app/specialist-house.css`
- Modify: `app/utility-house.css`
- Modify: `scripts/validate_public_navigation.py` and/or focused accessibility validator.

**Interfaces:**
- Produces a consistent baseline for keyboard, focus, touch and narrow-screen navigation without rewriting specialist apps.

- [x] **Step 1: Add source/built assertions**

Require visible `:focus-visible`, mobile House navigation, 44px-class touch targets where practical, reduced-motion handling, horizontal overflow safety for breadcrumbs/continuation rows, and `aria-current` on active routes.

- [x] **Step 2: Harden shared editorial shell**

Check 320–390px width behavior for House bar, breadcrumbs, long titles and continuation links.

- [x] **Step 3: Harden namespaced specialist/utility escapes**

No fixed overlay may cover app primary controls; controls must remain keyboard reachable.

- [x] **Step 4: Run all specialist and reader suites**

- [x] **Step 5: Commit**

```bash
git commit -m "feat: harden House navigation accessibility and responsive behavior"
```

---

### Task 20: Final deployment, SEO and branch verification

**Files:**
- Modify only files proven necessary by failing audits.
- Update PR control surface after verification.

**Interfaces:**
- Produces one merge-ready draft candidate with no known House architecture/presentation regressions.

- [x] **Step 1: Run the complete repository workflow**

Require all current quality/build stages to pass.

- [x] **Step 2: Inspect representative built shell families**

```text
Home
primary Door
legacy deep editorial reader
Tim dossier
FAQ
Great Book long-form
specialist: Timeline / Explore / Bible / World Map
utility: TTS
redirect
World Map diagnostic
one generated topic
one generated record
one generated question
```

- [x] **Step 3: Verify deployment/SEO invariants**

Check canonical routes, robots rules, sitemap membership, archive absence, legacy redirect behavior, exact five-Door primary order, and Great Book secondary visibility.

- [x] **Step 4: Update PR body with exact head SHA and workflow run**

Do not claim green until the workflow conclusion is `success`.

Verified on head `c11efde463a2ab84ada07cba7bedc80e10c30b5f` by Repository quality checks run `35296191199` (`success`).

- [ ] **Step 5: Request final code review before merge decision**

---

## Execution order

1. Restore green after activating `reader-v2`.
2. Make reader convergence measurable.
3. Converge Tim/FAQ visual ownership.
4. Add TTS utility escape.
5. Add derived continuation paths.
6. Enforce CSS ownership.
7. Harden responsive/accessibility behavior.
8. Run deployment/SEO/final review.

This order keeps every wave independently reviewable and prevents presentation work from reopening route/shell authority that is already stable.
