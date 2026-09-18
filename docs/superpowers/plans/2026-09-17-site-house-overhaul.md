# Site House Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the public site into one coherent House by centralizing route/shell authority, preventing archive/legacy leakage, projecting one shared navigation system across public page families, promoting the Great Book, and consolidating shared visual ownership without flattening specialist applications.

**Architecture:** `data/house/public-surfaces.json` remains the public route identity authority and is expanded with shell/navigation metadata. Shared Python helpers derive primary Doors, parent chains, shell types, and relative links; hand-authored and generated surfaces consume the same authority. Shared CSS owns site identity and navigation, while specialist page-family CSS keeps content/application geometry.

**Tech Stack:** Static HTML/CSS/JavaScript, Python build/generator scripts, JSON House registries, existing repository validators, GitHub Pages build pipeline.

**Spec:** `docs/superpowers/specs/2026-09-17-site-house-navigation-overhaul-design.md`

## Global Constraints

- The five primary Doors remain exactly: Tim Dooley, Religion, Philosophy, Science, World.
- Great Book becomes globally discoverable but does not become a sixth Door.
- Keep the site static, crawlable, and framework-free.
- Preserve specialist interfaces; do not force World Map, Bible, Timeline, Explore, or TTS into article-width geometry.
- Preserve existing canonical content and semantic validation markers.
- Historical `archive/` files remain in git but do not deploy as current public presentation unless explicitly whitelisted.
- Redirect and diagnostic surfaces remain minimal and `noindex`.
- Shared shell navigation should work without JavaScript; JavaScript may enhance but not create basic navigation.
- New shell rules augment existing semantic, reader, TTS, Bible, Timeline, World Map, House, and SEO validators rather than replacing them.

---

## Error inventory: macro → micro

### Macro architecture errors

1. Public navigation truth is duplicated across House registries, build scripts, SEO logic, generated page templates, and hand-authored HTML.
2. The static build can copy legacy/archive HTML into `_site`, contradicting the audit's stated deployed-web scope.
3. Public page families represent several historical design generations, so the site reads like multiple websites rather than one system.
4. Generated discovery/record pages carry a second embedded site shell instead of consuming the public House identity.
5. There is no universal enforceable contract saying every indexable public surface must expose Home/context navigation and a declared shell family.

### Information architecture errors

6. The five-Door model is canonical in `public-surfaces.json`, but stale code still treats World Map as the fifth primary Door.
7. Great Book is a major public work but is absent from the durable public surface registry and therefore can disappear from shared navigation.
8. Rooms, specialist surfaces, Paths, and discovery surfaces are not consistently distinguished in presentation.
9. Parent/up navigation differs page by page, producing arbitrary local navigation behavior.
10. Some branches expose siblings well while deep pages become navigational dead ends or mini-sites.

### Build/generator errors

11. `scripts/build_site.py` has its own primary-door labels and embedded page-shell CSS/navigation.
12. `scripts/build_discovery.py` emits its own embedded site theme/navigation rather than a shared shell primitive.
13. `scripts/optimize_seo.py` carries stale primary-door assumptions rather than deriving them from House authority.
14. Generated Topic/Context/Record/Question/A–Z pages cannot inherit a future visual/navigation change automatically from one source.
15. Sitemap/index generation can only be trustworthy if deployable routes and legacy exclusions are aligned first.

### Page-shell errors

16. Newer `site-system.css` pages, old reader pages, long-form readers, and one-off dossiers disagree on typography, spacing, navigation, cards, and responsive rules.
17. Several pages redefine global `:root`, `body`, heading, link, card, and navigation rules inline.
18. Deep science and archive-style readers depend on `app/style.css` / `app/reader.css` as a site-level skin even when the content should be part of the new House.
19. Tim deep dossiers and FAQ-family pages reproduce page shell CSS locally.
20. Specialist apps often lack a consistently placed House/Home escape because their chrome was designed in isolation.

### Route/deployment errors

21. `great-book.html` is a publishing stub rather than a compatibility redirect to the real `/great-book/` reader.
22. Legacy Religion/Bible/World Map pages can remain reachable if archive copying is not blocked.
23. Compatibility redirects need one consistent `noindex`/minimal pattern.
24. Diagnostic pages need an explicit technical/noindex classification rather than accidentally participating in public navigation.

### Visual/usability errors

25. Border/card/pill treatments are repeated too broadly and can obscure hierarchy.
26. Navigation, metadata, body content, evidence notes, and interactive controls are not sufficiently differentiated across generations.
27. Mobile navigation is inconsistent because every page family solves it separately.
28. Long-form reader chrome and global navigation can compete for vertical space.
29. Full-screen tools cannot safely inherit ordinary article widths or oversized editorial headers.
30. Focus/current-state/accessibility behavior varies by page family.

### Validation errors

31. Existing validators catch important semantic and navigation failures but do not yet require a recognized shell classification for every deployed public HTML page.
32. There is no explicit build assertion that `archive/**/*.html` is absent from `_site`.
33. There is no single validation asserting generated primary Doors exactly match House authority.
34. There is no explicit validation that Great Book is a registered, globally discoverable major work.
35. CSS ownership drift is not guarded: a newly added page can recreate unscoped global theme rules without failing CI.

---

## File responsibility map

### Public authority
- `data/house/public-surfaces.json` — durable public routes, parents, shell types, global-navigation visibility, aliases.
- `data/house/rooms.json` — Room semantics only; not duplicated into route authority.
- `scripts/house_public_surfaces.py` — typed/validated resolver and navigation derivation helpers.

### Shell/build system
- `scripts/house_shell.py` — **new** focused renderer for House bar, breadcrumbs, local family navigation, related routes, and relative URL resolution.
- `scripts/build_site.py` — copies deployable source, excludes legacy archive, generates Topic/Context/Record pages using shared shell helpers.
- `scripts/build_discovery.py` — generates Questions/families/A–Z using shared shell helpers.
- `scripts/optimize_seo.py` — derives public gateway assumptions from House authority; does not own route taxonomy.

### Shared presentation
- `app/site-system.css` — tokens, base public typography, shell/navigation primitives, standard editorial components.
- `app/longform-reader.css` — long-form reading geometry only; stops acting as an alternate global theme.
- specialist stylesheets — retain application-specific geometry and consume shared tokens where safe.

### High-impact hand-authored surfaces
- `index.html` — orientation-first homepage.
- `great-book.html` — compatibility redirect.
- `great-book/index.html` — compact long-form House identity.
- `rooms/index.html` — Room-centered hub rather than miscellaneous page grid.
- five primary gateway HTML files — canonical House shell examples.

### Validation
- `scripts/validate_public_navigation.py` — shell/parent/Home/archive/gateway consistency.
- `scripts/validate_reader_surfaces.py` — preserve existing semantic contracts and add Great Book/surface assertions where appropriate.
- `scripts/audit_web.py` — deployed-source scope remains aligned with build exclusions.
- existing build/test entry points — unchanged unless required to invoke the new focused validator assertions.

---

### Task 1: Make House public-surface authority complete and testable

**Files:**
- Modify: `data/house/public-surfaces.json`
- Modify: `scripts/house_public_surfaces.py`
- Modify: `scripts/validate_public_navigation.py`

**Interfaces:**
- Consumes: existing `load_public_surfaces(root: Path) -> dict`, `primary_gateway_rows(root: Path) -> list[dict]`.
- Produces: `surface_rows(root: Path) -> list[dict]`, `surface_by_id(root: Path, surface_id: str) -> dict`, `surface_by_route(root: Path, route: str) -> dict | None`, `parent_chain(root: Path, surface_id: str) -> list[dict]`, `secondary_global_rows(root: Path) -> list[dict]`.
- Registry rows gain explicit `shell_type` and `navigation_group`; Great Book is registered as an active long-form global work/path.

- [ ] **Step 1: Write failing resolver/registry assertions**

Add validation cases that fail when:

```python
required_shell_types = {"editorial", "longform", "specialist", "utility", "redirect", "diagnostic", "home"}
assert tuple(row["id"] for row in primary_gateway_rows(ROOT)) == (
    "tim", "religion", "philosophy", "science", "world"
)
assert surface_by_route(ROOT, "/great-book/")["id"] == "great-book"
assert surface_by_route(ROOT, "/great-book/")["shell_type"] == "longform"
```

Also assert every active registered row has `shell_type`, valid parentage, canonical route, and recognized navigation group.

- [ ] **Step 2: Run the targeted navigation validator and confirm failure**

Run:

```bash
python scripts/validate_public_navigation.py
```

Expected: failure because the new helper functions/Great Book/shell metadata are not present yet.

- [ ] **Step 3: Extend `public-surfaces.json` without changing the five primary IDs**

Add `shell_type` and `navigation_group` to durable public rows. Register:

```json
{
  "id": "great-book",
  "route": "/great-book/",
  "canonical_route": "/great-book/",
  "surface_type": "work",
  "shell_type": "longform",
  "title": "Great Book",
  "primary_parent": "works",
  "primary_room_ids": ["works", "potatoverse-canon", "archive-sources", "time-history"],
  "status": "active",
  "visibility": "global-work",
  "navigation_group": "read",
  "primary_navigation": false,
  "is_view": true,
  "knowledge_owner": false,
  "legacy_routes": ["/great-book.html"]
}
```

Use `home` shell for Home, `editorial` for normal readers/gateways, `specialist` for app-like explorers, and keep exceptions explicit.

- [ ] **Step 4: Add validated resolver helpers**

Implement helpers in `scripts/house_public_surfaces.py` that normalize routes, validate unique IDs/routes, verify parent IDs exist, and expose navigation groups without duplicating labels elsewhere.

- [ ] **Step 5: Run navigation validation**

Run:

```bash
python scripts/validate_public_navigation.py
```

Expected: PASS for authority checks.

- [ ] **Step 6: Commit**

```bash
git add data/house/public-surfaces.json scripts/house_public_surfaces.py scripts/validate_public_navigation.py
git commit -m "feat: centralize public surface shell authority"
```

---

### Task 2: Stop deploying historical archive HTML

**Files:**
- Modify: `scripts/build_site.py`
- Modify: `scripts/audit_web.py` only if comments/contracts need alignment
- Modify: `scripts/validate_public_navigation.py`

**Interfaces:**
- Consumes: existing build `EXCLUDE` set and `copy_tree()`.
- Produces: `_site` never contains source `archive/` files unless a future explicit whitelist is introduced.

- [ ] **Step 1: Add a failing post-build assertion**

Add validation equivalent to:

```python
archive_html = list((ROOT / "_site" / "archive").rglob("*.html")) if (ROOT / "_site" / "archive").exists() else []
if archive_html:
    fail("historical archive HTML leaked into _site: " + ", ".join(map(str, archive_html[:10])))
```

- [ ] **Step 2: Build and confirm the assertion fails on current behavior**

Run:

```bash
python scripts/build_site.py
python scripts/validate_public_navigation.py
```

Expected before implementation: archive leakage assertion fails if current source archive is copied.

- [ ] **Step 3: Exclude `archive` at the build-copy boundary**

Update the `EXCLUDE` set used by `copy_tree()` so `archive` is treated consistently with the web-audit scope.

Do not delete archive files from the repository.

- [ ] **Step 4: Rebuild and verify**

Run:

```bash
python scripts/build_site.py
python scripts/validate_public_navigation.py
```

Expected: no `_site/archive/**/*.html`; validation passes.

- [ ] **Step 5: Commit**

```bash
git add scripts/build_site.py scripts/audit_web.py scripts/validate_public_navigation.py
git commit -m "fix: keep legacy archive out of public build"
```

---

### Task 3: Create the shared House shell renderer

**Files:**
- Create: `scripts/house_shell.py`
- Modify: `scripts/house_public_surfaces.py`
- Modify: `scripts/validate_public_navigation.py`

**Interfaces:**
- Consumes: surface resolver helpers from Task 1.
- Produces:
  - `relative_href(from_route: str, to_route: str) -> str`
  - `render_house_bar(root: Path, surface_id: str, *, compact: bool = False) -> str`
  - `render_breadcrumbs(root: Path, surface_id: str) -> str`
  - `render_local_nav(root: Path, surface_id: str) -> str`
  - `render_related_routes(root: Path, surface_id: str) -> str`
  - `render_house_footer(root: Path, surface_id: str) -> str`

- [ ] **Step 1: Add failing focused shell tests/validator assertions**

Assertions must prove:

```python
html = render_house_bar(ROOT, "public-witness")
assert "Potato of Life" in html
for label in ("Tim Dooley", "Religion", "Philosophy", "Science", "World"):
    assert label in html
assert 'aria-current="page"' in render_house_bar(ROOT, "world")
assert "../" in relative_href("/tim-dooley/story/", "/tim-dooley/")
```

Also verify no sixth primary Door is emitted.

- [ ] **Step 2: Run and confirm failure**

Run:

```bash
python scripts/validate_public_navigation.py
```

Expected: import/function failures for the new shell renderer.

- [ ] **Step 3: Implement relative route resolution**

Use POSIX paths and route normalization so generated/static pages work from GitHub Pages subpaths without root-relative assumptions.

- [ ] **Step 4: Implement semantic shell fragments**

House bar markup must use semantic `<nav>` and current-state attributes. Breadcrumbs should follow registry parent chains. Local navigation should derive siblings sharing a primary parent/navigation group rather than embed manual lists.

- [ ] **Step 5: Run validation**

Run:

```bash
python scripts/validate_public_navigation.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/house_shell.py scripts/house_public_surfaces.py scripts/validate_public_navigation.py
git commit -m "feat: add shared House navigation renderer"
```

---

### Task 4: Remove stale primary-door logic from builders and SEO

**Files:**
- Modify: `scripts/build_site.py`
- Modify: `scripts/build_discovery.py`
- Modify: `scripts/optimize_seo.py`
- Modify: `scripts/validate_public_navigation.py`

**Interfaces:**
- Consumes: `primary_gateway_rows()` and House shell renderer.
- Produces: all generated public page families derive the same five Doors and shared shell HTML.

- [ ] **Step 1: Add failing assertions for generated output**

After a build, inspect representative pages:

```python
representatives = [
    ROOT / "_site" / "topics" / "tim" / "index.html",
    ROOT / "_site" / "questions" / "index.html",
    ROOT / "_site" / "index-a-z" / "index.html",
]
for page in representatives:
    html = page.read_text(encoding="utf-8")
    assert "site-housebar" in html
    assert ">World<" in html
    assert "World Map" not in extract_primary_nav(html)
```

- [ ] **Step 2: Run build + validator and confirm failure**

```bash
python scripts/build_site.py
python scripts/build_discovery.py
python scripts/validate_public_navigation.py
```

- [ ] **Step 3: Replace `build_site.py` hard-coded Door rendering**

Remove/retire `DOOR_LABELS` as a public taxonomy owner. `page_shell()` should consume shared House shell fragments and shared stylesheet assets.

- [ ] **Step 4: Replace `build_discovery.py` embedded theme/navigation**

Keep discovery-specific content generation, but use shared shell fragments and `app/site-system.css` rather than a second inline global theme.

- [ ] **Step 5: Make SEO derive gateways from House authority**

Replace stale `PRIMARY_DOORS` ownership in `scripts/optimize_seo.py` with calls to the shared resolver or data derived from it.

- [ ] **Step 6: Rebuild and validate representative generated pages**

Run:

```bash
python scripts/build_site.py
python scripts/build_discovery.py
python scripts/optimize_seo.py
python scripts/validate_public_navigation.py
```

Expected: shared five-Door output and no stale World Map gateway.

- [ ] **Step 7: Commit**

```bash
git add scripts/build_site.py scripts/build_discovery.py scripts/optimize_seo.py scripts/validate_public_navigation.py
git commit -m "refactor: make generators consume House navigation authority"
```

---

### Task 5: Build Visual System v2 shell primitives

**Files:**
- Modify: `app/site-system.css`
- Modify: `app/longform-reader.css`
- Modify: `scripts/validate_public_navigation.py`

**Interfaces:**
- Consumes: semantic classes emitted by `scripts/house_shell.py`.
- Produces: responsive House bar, breadcrumb, local nav, footer, cards/notes, standard widths, focus states, compact specialist modifier.

- [ ] **Step 1: Add source/output CSS assertions**

Validate that `app/site-system.css` contains stable primitives such as:

```text
.site-housebar
.site-primary-nav
.site-breadcrumbs
.site-local-nav
.site-related
.site-footer
.page--reading
.page--wide
```

and that migrated/generated output loads `app/site-system.css`.

- [ ] **Step 2: Implement central tokens**

Consolidate shared background/surface/text/line/accent/spacing/radius/type/focus/motion tokens in `:root`. Preserve temporary aliases required by existing migrated pages to avoid a flag-day rewrite.

- [ ] **Step 3: Implement shell layout and accessibility states**

Add desktop/mobile House bar behavior, visible `:focus-visible`, active state, accessible native disclosure styling, breadcrumb overflow, and reduced-motion handling.

- [ ] **Step 4: Narrow long-form CSS responsibility**

Keep chapter/reading geometry in `app/longform-reader.css`, but remove or override global theme ownership now provided by `site-system.css`.

- [ ] **Step 5: Run validation**

```bash
python scripts/build_site.py
python scripts/validate_public_navigation.py
python scripts/validate_reader_surfaces.py
```

- [ ] **Step 6: Commit**

```bash
git add app/site-system.css app/longform-reader.css scripts/validate_public_navigation.py
git commit -m "feat: introduce House visual system v2"
```

---

### Task 6: Fix Great Book route and give it permanent House visibility

**Files:**
- Modify: `great-book.html`
- Modify: `great-book/index.html`
- Modify: `index.html`
- Modify: `works/index.html`
- Modify: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: Great Book registry entry and long-form shell.
- Produces: `/great-book.html` redirects to `/great-book/`; Book is visible in global secondary navigation and homepage Library/Read section.

- [ ] **Step 1: Add failing Great Book assertions**

Assert:

```python
assert surface_by_route(ROOT, "/great-book/")["id"] == "great-book"
assert_redirect(ROOT / "great-book.html", "/great-book/")
assert_home_feature(ROOT / "index.html", "/great-book/", "Great Book")
```

- [ ] **Step 2: Convert `great-book.html` to the standard compatibility redirect pattern**

Include canonical target and `robots=noindex`.

- [ ] **Step 3: Mount compact House chrome on Great Book reader**

Preserve chapter IDs, TOC, search, progress, TTS controls, and existing reader JavaScript hooks.

- [ ] **Step 4: Promote Great Book on Home and Works**

The homepage should expose a clear Library/Read section with Great Book as the strongest work card beneath the five Doors. Works should identify it as a primary work/path.

- [ ] **Step 5: Run reader and navigation validations**

```bash
python scripts/build_site.py
python scripts/validate_reader_surfaces.py
python scripts/validate_public_navigation.py
```

- [ ] **Step 6: Commit**

```bash
git add great-book.html great-book/index.html index.html works/index.html scripts/validate_reader_surfaces.py
git commit -m "feat: promote Great Book across the House"
```

---

### Task 7: Migrate Home + five primary Doors as canonical editorial examples

**Files:**
- Modify: `index.html`
- Modify: `tim-dooley/index.html`
- Modify: `religion/index.html`
- Modify: `philosophy/index.html`
- Modify: `science/index.html`
- Modify: `world/index.html`
- Modify: `scripts/validate_public_navigation.py`

**Interfaces:**
- Consumes: House shell markup/classes and shared site system.
- Produces: canonical public editorial pattern copied by later family migrations.

- [ ] **Step 1: Add shell-coverage assertions for the six canonical pages**

Every page must expose brand/Home, the exact five Doors, correct `aria-current` state, and no duplicate old global nav block.

- [ ] **Step 2: Rebuild the homepage hierarchy**

Keep exactly five primary Door sections/cards, then Library/Paths, Rooms, Find/Verify layers. Do not turn every secondary surface into an equal card.

- [ ] **Step 3: Migrate the five gateway pages**

Replace hand-specific global navigation with the shared House pattern while preserving page-specific content and semantic IDs required by existing validators.

- [ ] **Step 4: Run validators**

```bash
python scripts/build_site.py
python scripts/validate_reader_surfaces.py
python scripts/validate_public_navigation.py
```

- [ ] **Step 5: Commit**

```bash
git add index.html tim-dooley/index.html religion/index.html philosophy/index.html science/index.html world/index.html scripts/validate_public_navigation.py
git commit -m "feat: migrate primary gateways to House shell"
```

---

### Task 8: Rebuild Rooms as the middle navigation layer

**Files:**
- Modify: `rooms/index.html`
- Modify: `scripts/validate_reader_surfaces.py`
- Modify: `scripts/validate_public_navigation.py`

**Interfaces:**
- Consumes: `data/house/rooms.json`, public surface registry relationships.
- Produces: Rooms hub that explains Rooms as bounded subject neighborhoods and points to their strongest public surfaces.

- [ ] **Step 1: Add assertions that Rooms exposes all canonical room IDs/titles**

Read `rooms.json` and require the page to represent each active canonical room exactly once in its main directory.

- [ ] **Step 2: Replace miscellaneous public-surface cards with canonical Room cards**

Each Room card should expose purpose, one recommended starting surface, and bounded adjacent public routes where available.

- [ ] **Step 3: Keep specialist views separate**

World Map, Bible, Politics, Law, Economy, etc. may be linked from Room cards but are not redefined as Rooms merely because they are visitor-facing pages.

- [ ] **Step 4: Run validators and commit**

```bash
python scripts/build_site.py
python scripts/validate_reader_surfaces.py
python scripts/validate_public_navigation.py
git add rooms/index.html scripts/validate_reader_surfaces.py scripts/validate_public_navigation.py
git commit -m "feat: make Rooms the canonical middle navigation layer"
```

---

### Task 9: Migrate deep editorial page families and remove local global themes

**Files:**
- Modify: Tim deep dossier HTML/CSS blocks under `tim-dooley/`
- Modify: deep Science pages under `science/`
- Modify: FAQ pages under `faq/`
- Modify: Context/standalone reader pages that currently own unscoped global theme rules
- Modify: `scripts/validate_public_navigation.py`

**Interfaces:**
- Consumes: canonical editorial shell from Tasks 5 and 7.
- Produces: deep readers that share House orientation while retaining page-specific content components.

- [ ] **Step 1: Add a migration allowlist/coverage assertion**

For public editorial surfaces, fail when unscoped inline blocks redefine global `:root`, `body`, or site navigation unless the page is explicitly classified specialist/utility/diagnostic.

- [ ] **Step 2: Migrate Tim dossier family**

Prioritize `100000-hours`, `public-witness`, `evidence`, ontology/biblical-case/god-in-real-life/how-much-is-tim-god` pages as one family.

- [ ] **Step 3: Migrate deep Science readers**

Detach archive site skin from content components. Keep scientific diagrams/equations/component rules local.

- [ ] **Step 4: Migrate FAQ and standalone editorial readers**

Replace duplicated global theme/navigation CSS with shared classes while preserving content and anchors.

- [ ] **Step 5: Run full reader/navigation validation**

```bash
python scripts/build_site.py
python scripts/validate_reader_surfaces.py
python scripts/validate_public_navigation.py
```

- [ ] **Step 6: Commit by family**

Create separate reviewable commits for Tim, Science, FAQ, and remaining standalone reader migrations rather than one enormous CSS commit.

---

### Task 10: Add compact House identity to specialist applications

**Files:**
- Modify: `world-map/index.html` and its specialist stylesheet as needed
- Modify: `traditions/bible/index.html` and Bible stylesheet as needed
- Modify: `explore/index.html` and archive explorer stylesheet as needed
- Modify: `timeline/index.html` and Timeline stylesheet as needed
- Modify: `tools/tts/index.html` and tool stylesheet as needed
- Modify: `scripts/validate_public_navigation.py`

**Interfaces:**
- Consumes: compact shell classes/tokens.
- Produces: stable Home/House escape and context label without imposing article layout.

- [ ] **Step 1: Add specialist shell assertions**

Each specialist surface must expose a compact Home/House control and domain context while preserving its existing application root/container IDs.

- [ ] **Step 2: Migrate World Map and Bible first**

These are the strongest examples of full-screen/specialist geometry. Add compact House chrome without changing core application layout or interaction contracts.

- [ ] **Step 3: Migrate Explore, Timeline, and TTS**

Use the same compact identity pattern, customized only for collision with existing toolbars.

- [ ] **Step 4: Run specialist suites**

Run the repository's existing World Map, Bible, Timeline, TTS, public navigation, and general reader validators/build checks.

- [ ] **Step 5: Commit by specialist family**

Use separate commits where the application regression surface is meaningfully different.

---

### Task 11: Enforce the House contract on every deployed HTML surface

**Files:**
- Modify: `scripts/validate_public_navigation.py`
- Modify: `scripts/audit_web.py`
- Modify: build/test workflow entry point only if needed to ensure validator execution

**Interfaces:**
- Consumes: registry shell types and final `_site` output.
- Produces: CI failure for orphaned public pages, undeclared shell behavior, archive leakage, stale primary gateways, broken parentage, or missing Home escape.

- [ ] **Step 1: Classify every deployed HTML output**

Validation rules:

```text
indexable editorial/longform/generated => shared House identity required
specialist/utility => compact House escape required
redirect/diagnostic => noindex required, full shell not required
archive source => must not deploy
```

- [ ] **Step 2: Add route-to-registry/generator-family coverage**

Every deployed HTML file must resolve either to a registered durable surface, a known generated-family contract, an explicit redirect, or an explicit diagnostic.

- [ ] **Step 3: Add global primary-nav comparison**

Extract primary nav from representative deployed shells and compare IDs/order with `primary_gateway_rows()` rather than hard-coded labels in the validator.

- [ ] **Step 4: Add Great Book and archive assertions**

Make the high-impact regressions impossible to reintroduce silently.

- [ ] **Step 5: Run complete repository build/validation suite**

At minimum:

```bash
python scripts/build_site.py
python scripts/build_discovery.py
python scripts/optimize_seo.py
python scripts/audit_web.py
python scripts/validate_public_navigation.py
python scripts/validate_reader_surfaces.py
```

Run any additional documented specialist validation commands discovered in repository scripts/workflows.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_public_navigation.py scripts/audit_web.py .github/workflows || true
git commit -m "test: enforce the public House contract"
```

---

### Task 12: Final consolidation and dead-style cleanup

**Files:**
- Modify: shared/public CSS and migrated HTML only where proven redundant
- Modify: documentation if build/public-route ownership docs need alignment

**Interfaces:**
- Consumes: fully migrated/validated site.
- Produces: no obsolete duplicate global navigation definitions or clearly dead public-theme rules remain in active public surfaces.

- [ ] **Step 1: Search for stale navigation authorities**

Search for old primary-Door arrays, `World Map` used as fifth primary gateway, duplicate top-level Door markup, and old global nav labels.

- [ ] **Step 2: Search for obsolete global CSS ownership**

Identify unscoped root/body/nav rules in active editorial pages that are now redundant. Remove only when validators/build prove the shared system covers them.

- [ ] **Step 3: Rebuild and run every validator**

The final build must pass the complete suite with no archive leakage and no orphan indexable surfaces.

- [ ] **Step 4: Review built output, not only source**

Inspect representative `_site` outputs from every shell family: Home, Door, deep editorial, long-form, generated, specialist, utility, redirect, diagnostic.

- [ ] **Step 5: Commit final cleanup**

```bash
git add -A
git commit -m "refactor: finish House shell consolidation"
```

---

## Execution order and impact rationale

The implementation starts with Tasks 1–4 because they eliminate the largest classes of repeat error before visual migration begins:

1. **Authority** prevents future disagreement.
2. **Archive exclusion** removes incorrect public pages immediately.
3. **Shared renderer** makes navigation reusable.
4. **Generator/SEO centralization** stops machine-generated pages from reintroducing old architecture.

Tasks 5–8 then establish the visible design system and canonical high-traffic surfaces. Tasks 9–10 migrate the breadth of the site by family rather than random page order. Tasks 11–12 make the improvement durable through validation and cleanup.

## Self-review

- Spec coverage: all design-spec sections map to at least one task.
- Scope: large but coherent because every task advances the same public House contract; specialist internals are explicitly out of scope.
- Placeholders: none; every task names files, interfaces, tests, expected behavior, and commit boundary.
- Type consistency: all shell consumers depend on the Task 1 resolver and Task 3 renderer names defined above.
- Safety boundary: content semantics are preserved; the work changes navigation/presentation/build ownership rather than substantive page claims.
