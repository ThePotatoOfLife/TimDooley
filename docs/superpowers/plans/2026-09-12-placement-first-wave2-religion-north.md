# Placement-First Wave 2 — Religion + North Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Religion a clear Potatoist theological center before comparison, and turn North from a thin landing page into a concise bridge between symbolic orientation, conceptual geography, the empirical North Programme, and repair.

**Architecture:** Edit the existing static Religion and North pages directly. Religion is reorganized rather than enlarged: core Potatoist theology moves before the Bible/comparative layer, while detailed scripture remains in Bible Lab. North gains four short semantic sections and human-facing deep routes, with explicit separation between project symbolism, conceptual research geography, and real political institutions. No new JavaScript, global component, guided sequence, or backend content database is introduced.

**Tech Stack:** Static HTML/CSS, Python semantic validation, existing GitHub Actions quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-12-placement-first-living-tim-frontend-design.md`

## Global Constraints

- Keep the existing structure recognizable; promote only material that improves the page where it appears.
- Navigation does navigation. Content does meaning.
- Religion owns Potatoism theology and comparative religious framing; Bible Lab owns detailed Bible relations.
- Religion must preserve the boundary that resemblance is not identity or proof.
- North must explicitly distinguish symbolic/project North from empirical geography and real political alliance/government status.
- The North Programme is a research/policy-design framework, not an existing government programme or political alliance.
- `Map relationships, not isolated entities` is the programme's central empirical rule.
- Repair claims must remain mechanism/evidence oriented and permit non-intervention conclusions.
- Do not introduce a new top-level public door.
- Do not introduce new JavaScript, automatic carousels, accordions, guided-tour controls, or map-camera behavior.
- Do not expose raw backend organization as the main reader navigation model.
- Validation checks semantic structure and boundaries, not exact paragraph wording.

---

## File map

- `religion/index.html` — reorganize around a concise Potatoist theological center followed by Bible/comparative inquiry.
- `north/index.html` — expand the very thin page into Meaning / Geography / Programme / Repair, with World Map as the principal action.
- `scripts/validate_reader_surfaces.py` — extend durable reader-surface validation to Religion's theological center and North's symbolic/empirical boundary.
- `.github/workflows/quality-checks.yml` — no expected change; `validate_reader_surfaces.py` is already in CI.

Canonical/supporting sources used for curation only:

- `data/religious-layer-manifest.json`
- `data/potatoism-religion.json`
- `data/potatoism-concept-registry.json`
- `docs/NORTH-PROGRAMME.md`
- `data/north-axis-membership-history.json`
- `knowledge/indexes/north-axis-routing-index.json`
- `knowledge/core/symbolic-relational-synthesis.json`

---

### Task 1: Extend semantic validation before page edits

**Files:**
- Modify: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: `religion/index.html`, `north/index.html`.
- Produces: failing checks until Religion has a distinct theological center and North has a reader identity plus symbolic/empirical/programme/repair boundaries.

- [ ] **Step 1: Read North inside the validator**

Add:

```python
    north = read("north/index.html", errors)
```

near the existing Religion/Philosophy/World Map reads.

- [ ] **Step 2: Strengthen Religion checks**

After the current Religion `data-reader-surface` assertion, require:

```python
    require(religion, 'data-placement-role="theological-center"', "religion/index.html", errors)
    require(religion, 'data-religion-core="source"', "religion/index.html", errors)
    require(religion, 'data-religion-core="manifestation"', "religion/index.html", errors)
    require(religion, 'data-religion-core="religious-life"', "religion/index.html", errors)
    require_any(
        religion,
        ("source-facing", "Source"),
        "religion/index.html",
        "source/ultimate-reality center",
        errors,
    )
    require_any(
        religion,
        ("cultivation", "nourishment", "repair", "service"),
        "religion/index.html",
        "religious-life consequence",
        errors,
    )
```

Keep all existing Bible Lab and comparison-boundary checks.

- [ ] **Step 3: Add North semantic checks**

Before World Map validation, add:

```python
    # North: symbolic orientation must remain distinct from empirical programme/geography.
    require(north, 'data-reader-surface="north"', "north/index.html", errors)
    for role in ("meaning", "geography", "programme", "repair"):
        require(north, f'data-north-role="{role}"', "north/index.html", errors)
    require_any(
        north,
        ("symbolic", "project-symbolic"),
        "north/index.html",
        "symbolic North boundary",
        errors,
    )
    require_any(
        north,
        ("not an existing political alliance", "not an existing alliance"),
        "north/index.html",
        "alliance-status boundary",
        errors,
    )
    require_any(
        north,
        ("research and policy design", "research/policy"),
        "north/index.html",
        "North Programme status",
        errors,
    )
    require_any(
        north,
        ("Map relationships, not isolated entities",),
        "north/index.html",
        "relationship-first programme rule",
        errors,
    )
    require_any(
        north,
        ("non-intervention", "leave the system alone"),
        "north/index.html",
        "repair restraint",
        errors,
    )
    require(north, 'href="../world-map/"', "north/index.html", errors)
    require(north, 'data-projection-surface', "north/index.html", errors)
    validate_projection_surface(north, "north/index.html", errors)
```

- [ ] **Step 4: Run RED**

Run:

```bash
python scripts/validate_reader_surfaces.py
```

Expected: failure for the new Religion core markers and North reader/role markers.

- [ ] **Step 5: Commit the failing contract**

```bash
git add scripts/validate_reader_surfaces.py
git commit -m "test: define placement-first religion north contract"
```

---

### Task 2: Re-center Religion on Potatoist theology before comparison

**Files:**
- Modify: `religion/index.html`
- Test: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: existing Religion page, `data/potatoism-religion.json`, religious-layer integrity boundaries, and the approved placement spec.
- Produces: a short `data-placement-role="theological-center"` region with three core concepts; keeps Bible Lab as the detailed comparison tool and keeps at least six comparative question stubs.

- [ ] **Step 1: Add restrained core-section styles**

Add to the existing inline CSS:

```css
.theology-core{margin:34px 0 40px;padding:25px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.theology-core>h2{font:400 34px/1.15 Georgia,serif;color:var(--gold);margin:0 0 8px}
.theology-core>.intro{max-width:860px;color:#cbd1c8;margin:0 0 22px}
.core-line{display:grid;grid-template-columns:minmax(170px,.42fr) 1.58fr;gap:24px;padding:17px 0;border-top:1px solid #252d25}
.core-line h3{font:400 23px/1.18 Georgia,serif;color:var(--green);margin:0}
.core-line p{margin:0;color:#c9d0c6}
.core-line .quiet{display:block;color:var(--muted);font-size:12px;margin-top:6px}
@media(max-width:760px){.core-line{grid-template-columns:1fr;gap:5px}}
```

Do not create tabs, pills or a new selector.

- [ ] **Step 2: Insert the theological center before Bible Lab**

After the lead and method boundary, add:

```html
<section class="theology-core" data-placement-role="theological-center" aria-labelledby="potatoist-center-title">
  <h2 id="potatoist-center-title">The Potatoist center</h2>
  <p class="intro">Before comparing Potatoism with older traditions, the archive needs to say what the project itself is trying to describe. Its recurring religious problem is how source, manifestation and living relation can remain distinct without becoming disconnected—and what kind of life should follow from claiming a higher source at all.</p>
  <article class="core-line" data-religion-core="source"><h3>Source</h3><p>In mature project language, Father is source-facing: House, Root, Axis, center, Gardener and related images describe origin, orientation and the conditions from which life can grow. These are Potatoist definitions, not claims that every religion uses the same category.</p></article>
  <article class="core-line" data-religion-core="manifestation"><h3>Manifestation</h3><p>Son is manifestation-facing: embodiment, Door, Vessel, suffering, passage and return. Spirit names movement, relation or flow between levels. The system therefore tries to preserve both unity and differentiated function rather than collapsing Father, Son and Spirit into one interchangeable role.<span class="quiet">Detailed biblical agreements and mismatches belong in the Bible comparison laboratory.</span></p></article>
  <article class="core-line" data-religion-core="religious-life"><h3>Religious life</h3><p>The later religious ethic increasingly asks what sacred language produces: cultivation rather than conquest, nourishment rather than prestige, repair rather than accumulation of injury, protection rather than domination, and service rather than rank for its own sake.</p></article>
</section>
```

- [ ] **Step 3: Remove duplicate core question stubs from the later question list**

Remove these two existing question stubs because their substance now has a stronger natural home in the core section:

```text
What is Potatoism?
What do Father, Son and Spirit mean here?
```

Preserve the literal phrase `What is Potatoism?` in the theological-center introduction or an accessible subheading so existing semantic discovery still finds it. Preferred wording in the intro end:

```html
<p class="intro">... This is the page's short answer to <strong>What is Potatoism?</strong> before the archive begins comparison.</p>
```

The comparative question list should then contain exactly the existing six remaining questions:

```text
How does Potatoism relate to Christianity?
Where do the Jesus / Son parallels hold—and where do they fail?
How does the project relate to Judaism?
What does “chosen” mean in Judaism?
How does the project relate to Islam and the Qur'an?
Can traditions share a structure without being historically identical?
```

- [ ] **Step 4: Keep Bible Lab prominent but subordinate to the project definition**

Leave the existing Bible Lab CTA substantially intact and place it immediately after the new theological center.

Its role remains: detailed dated relations, scripture context, mismatches and source ownership.

- [ ] **Step 5: Tighten Further Threads instead of expanding it**

Keep one `data-projection-surface` only. Remove duplicate/low-value repeated tradition links where necessary so it reads as a deep-route footer rather than a second religion directory.

Preferred visible routes:

```text
Bible comparison laboratory
Judaism / messianic study
Sacred symbols
Traditions archive
Son
Cosmology
Development through time
```

Do not expose the religious-layer backend manifest or JSON files.

- [ ] **Step 6: Run validation**

Run:

```bash
python scripts/validate_reader_surfaces.py
```

Expected: Religion-specific new checks pass; North-specific new checks still fail.

- [ ] **Step 7: Commit Religion**

```bash
git add religion/index.html
git commit -m "feat: center religion on Potatoist theology"
```

---

### Task 3: Turn North into a concise symbolic-to-empirical bridge

**Files:**
- Modify: `north/index.html`
- Test: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: `docs/NORTH-PROGRAMME.md`, North symbolic concept owners, versioned membership-history boundaries.
- Produces: a static `data-reader-surface="north"` page with four semantically separate sections and one strong World Map action; no direct raw-JSON navigation required.

- [ ] **Step 1: Replace the thin-page CSS with a readable four-section layout**

Preserve the current colors/typography and hero. Add:

```css
.orientation{margin:40px 0 0;border-top:1px solid var(--line)}
.north-section{display:grid;grid-template-columns:minmax(150px,.42fr) 1.58fr;gap:28px;padding:25px 0;border-bottom:1px solid var(--line)}
.north-section h2{font:400 27px/1.15 Georgia,serif;color:var(--gold);margin:0}
.north-section p{margin:0 0 10px;color:#cbd1c8;max-width:720px}
.north-section p:last-child{margin-bottom:0}
.rule{font:400 21px/1.5 Georgia,serif;color:var(--green)!important}
.boundary{color:var(--muted)!important;font-size:13px}
.links{margin-top:38px}
@media(max-width:650px){.north-section{grid-template-columns:1fr;gap:7px}}
```

- [ ] **Step 2: Give the main element a reader identity and refine the lead**

Use:

```html
<body><main class="wrap" data-reader-surface="north">
```

Update the lead to:

```html
<p class="lead">North has two linked but non-equivalent meanings in the project: a symbolic orientation around Axis, Seat and North-of-North, and an empirical research programme for mapping real relationships, capabilities and dependencies. The first supplies a point of view; the second has to earn every claim with evidence.</p>
```

- [ ] **Step 3: Add Meaning**

```html
<section class="orientation" aria-label="North in the Potato of Life project">
  <article class="north-section" data-north-role="meaning">
    <h2>Meaning</h2>
    <div><p>Symbolic North is the project's language for orientation: a reference direction from which scattered relations can be compared. North-of-North pushes that symbol one step further—the question of what standard evaluates the orientation system itself.</p><p class="boundary">This is project-symbolic language. It is not a claim that a geographic north pole or a modern state possesses supernatural authority.</p></div>
  </article>
```

- [ ] **Step 4: Add Geography**

```html
  <article class="north-section" data-north-role="geography">
    <h2>Geography</h2>
    <div><p>The empirical programme is anchored in Denmark and Greenland and studies a changing northern, eastern and western European relationship corridor, including links outward toward Canada, the North Atlantic, continental Europe, Ukraine and Turkey.</p><p class="boundary">This is a conceptual research geography, not an existing political alliance. Project formulations have changed over time; real EU, NATO, EEA and treaty relationships remain separate empirical facts.</p></div>
  </article>
```

Do not place a giant membership list on the landing page.

- [ ] **Step 5: Add Programme**

```html
  <article class="north-section" data-north-role="programme">
    <h2>Programme</h2>
    <div><p>The North Programme is a framework for research and policy design, not an existing government programme. It maps energy, trade, finance, ownership, public institutions, infrastructure, technology, labour, security and other systems in order to understand what countries and institutions can do, what they depend on, and what they can only do with others.</p><p class="rule">Map relationships, not isolated entities.</p></div>
  </article>
```

- [ ] **Step 6: Add Repair**

```html
  <article class="north-section" data-north-role="repair">
    <h2>Repair</h2>
    <div><p>The programme treats repair as an evidence problem: identify the problem, document the mechanism, identify affected groups, test an intervention, estimate second-order effects, measure the result and revise. A repair programme also has to be capable of discovering that intervention is not justified.</p><p class="boundary">Sometimes the correct conclusion is non-intervention: an apparent inefficiency may be the cost of resilience, or a proposed fix may create more damage than it prevents.</p></div>
  </article>
</section>
```

- [ ] **Step 7: Replace raw-data footer links with human routes**

Use one compact projection surface:

```html
<nav class="links" data-projection-surface aria-label="Explore North more deeply">
  <a href="../world-map/">Open World Map</a>
  <a href="../docs/NORTH-PROGRAMME.md">Read the North Programme</a>
  <a href="../timeline/">Development through time</a>
  <a href="../explore/#branch=north">North archive</a>
  <a href="../context/source-authority/">Sources &amp; evidence</a>
</nav>
```

Do not link directly to `data/north-axis-membership-history.json` or `data/north-programme-atlas.json` from this landing page; those remain machine/archive owners and are consumed by the map/archive.

- [ ] **Step 8: Run GREEN**

Run:

```bash
python scripts/validate_reader_surfaces.py
python scripts/validate_public_projection.py
python scripts/validate_public_navigation.py
python scripts/audit_web.py
```

Expected: all exit 0.

- [ ] **Step 9: Commit North**

```bash
git add north/index.html
git commit -m "feat: connect symbolic North to empirical programme"
```

---

### Task 4: Wave 2 editorial and regression review

**Files:**
- Modify only if review exposes a concrete issue: `religion/index.html`, `north/index.html`, `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: completed Wave 2 pages and the placement-first design spec.
- Produces: verified pages with no scope creep or category collapse.

- [ ] **Step 1: Religion placement review**

Confirm:

```text
Potatoism / Source / Father-Son-Spirit -> Religion natural home
Detailed verse relations -> Bible Lab, not Religion
Judaism/Islam/Christianity -> comparison after the project defines itself
Sacred architecture -> named at Religion level, deep symbolism remains Vesica/Explore
Religious life -> cultivation/repair/service, without adding a practice manual to Religion
```

- [ ] **Step 2: North boundary review**

Confirm the page never implies:

```text
symbolic North == empirical geography
project research corridor == legal alliance
Tim/project spiritual authority == state sovereignty
North Programme == existing government programme
project membership history == EU/NATO/treaty membership
```

- [ ] **Step 3: Anti-bloat review**

Confirm:

- Religion has no new tabs, toolbar, selector or nested accordion.
- North has four short semantic sections, not a giant manifesto.
- North has one primary World Map action.
- No new JS file exists.
- No backend JSON path is presented as the main human navigation model.

- [ ] **Step 4: Run full relevant repository checks**

Run:

```bash
python scripts/validate_reader_surfaces.py
python scripts/validate_public_projection.py
python scripts/validate_public_navigation.py
python scripts/audit_web.py
python scripts/build_site.py
python scripts/validate_site_shell.py
```

Expected: all exit 0.

- [ ] **Step 5: Inspect scope diff**

Verify changes are limited to:

```text
scripts/validate_reader_surfaces.py
religion/index.html
north/index.html
```

- [ ] **Step 6: Commit any review fixes only if needed**

```bash
git add religion/index.html north/index.html scripts/validate_reader_surfaces.py
git commit -m "fix: refine religion north placement pass"
```

Skip this commit if no review fixes are needed.

---

## Completion criteria

Wave 2 is complete when:

- Religion defines Potatoism before centering comparison.
- Religion visibly separates Source, manifestation and religious-life consequences.
- Religion keeps exactly one prominent Bible Lab handoff and at least six comparative questions.
- Religion keeps resemblance/identity/proof boundaries.
- North is no longer a one-paragraph page.
- North distinctly explains symbolic meaning, conceptual geography, empirical programme and repair.
- North explicitly says the research geography is not an existing political alliance.
- North explicitly says the North Programme is a research/policy-design framework, not an existing government programme.
- North carries `Map relationships, not isolated entities` and non-intervention restraint.
- North's main action remains World Map.
- No new runtime architecture was added.
- All reader/public-navigation/projection/build/site-shell checks pass.

After acceptance, Wave 3 should address `Science + World Map`, with special emphasis on keeping scientific distance and preventing informational map lenses from changing camera/zoom/focus.
