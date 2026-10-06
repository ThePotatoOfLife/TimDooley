# Placement-First Wave 1 — Tim + Philosophy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Tim and Philosophy public pages feel substantially more inhabited by Tim Dooley while preserving the current site structure, provenance boundaries, calm interaction, and five-door architecture.

**Architecture:** This wave edits the two existing static reader surfaces directly and strengthens `scripts/validate_reader_surfaces.py` so the richer editorial structure becomes a durable semantic contract without turning reader copy into a second canonical database. No new JavaScript runtime or shared “Living Tim” widget is introduced; Tim becomes richer through carefully placed static sections, while Philosophy uses native HTML `<details>` only where a delayed reflection materially improves the reading experience.

**Tech Stack:** Static HTML/CSS, native HTML `<details>`, Python semantic validation, existing GitHub Actions quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-12-placement-first-living-tim-frontend-design.md`

## Global Constraints

- Keep the existing structure recognizable; put each significant piece of material where it belongs best; promote only the amount that improves understanding.
- Navigation does navigation. Content does meaning.
- The homepage continues to expose exactly five primary public doors: Tim Dooley, Religion, Philosophy, Science, World Map.
- Do not introduce a site-wide quote carousel, Tim chatbot, symbol strip, journey stepper, encounter card, floating assistant, global accordion system, or generic guided-tour component.
- Tim wording must remain provenance-aware: documented/public, recovered, and project/book/archive formulations must not be visually flattened into one quotation class.
- Tim/Father and Thomas/Son remain project-ontology distinctions and do not erase ordinary biological or legal reality.
- Interactions must not unexpectedly scroll, steal focus, change zoom, cause large layout jumps, or depend on hover for critical meaning.
- Use ordinary hyperlinks first. Use native `<details>` only for secondary interpretation where hiding the reflection gives the primary question room.
- Reader pages explain; they do not become new canonical owners.
- Do not create a new content manifest for this wave unless direct page curation becomes demonstrably unmaintainable.
- Validation checks durable structure and provenance classes, not exact prose.

---

## File map

- `tim-dooley/index.html` — Tim public reader surface. This wave makes it less dossier-like by adding one provenance-labelled riddle/reading frame and one compact “work / witness / gardener” section while preserving the existing question sequence, primary routes, chronology and deep links.
- `philosophy/index.html` — Philosophy public reader surface. This wave replaces the homogeneous wall of sayings with a more varied editorial rhythm using sayings, questions, two compact stories, source-class labels and a small number of native `Chew on it` disclosures.
- `scripts/validate_reader_surfaces.py` — Durable semantic validation for Tim and Philosophy. It must assert the new placement structure without hard-coding paragraph copy.
- `.github/workflows/quality-checks.yml` — No change expected; `python scripts/validate_reader_surfaces.py` is already part of CI.

Canonical/supporting sources used for curation only:

- `knowledge/core/tim-role-synthesis.json`
- `knowledge/corporium/tim-voice-anthology.json`
- `knowledge/philosophy/tim-dooley-philosophical-inquiry.json`
- `knowledge/practice/potato-path.json`

These sources remain canonical/supporting owners. The HTML pages paraphrase or quote them with provenance labels; they do not replace them.

---

### Task 1: Strengthen semantic validation before editing the pages

**Files:**
- Modify: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: rendered source HTML from `tim-dooley/index.html` and `philosophy/index.html`.
- Produces: non-zero exit when the Tim page lacks a provenance-labelled riddle/work/gardener layer or Philosophy lacks mixed reader forms/provenance/native disclosure; zero exit when those durable structures exist.

- [ ] **Step 1: Add a helper for class-marker counting**

Add this helper after `question_count`:

```python
def class_count(text: str, class_name: str) -> int:
    return len(
        re.findall(
            rf'class=["\'][^"\']*\b{re.escape(class_name)}\b[^"\']*["\']',
            text,
            flags=re.I,
        )
    )
```

This is deliberately generic and does not encode exact paragraph wording.

- [ ] **Step 2: Add RED checks for Tim’s placement-first structure**

Inside the existing Tim validation block, after the Tim/Father and Thomas/Son checks, add:

```python
    require(tim, 'data-placement-role="riddle"', "tim-dooley/index.html", errors)
    require(tim, 'data-placement-role="work"', "tim-dooley/index.html", errors)
    require(tim, 'data-placement-role="gardener"', "tim-dooley/index.html", errors)
    require_any(
        tim,
        ("Recovered project wording", "Recovered wording"),
        "tim-dooley/index.html",
        "recovered-wording provenance label",
        errors,
    )
    require_any(
        tim,
        ("builder", "operator", "build useful structures"),
        "tim-dooley/index.html",
        "builder/work layer",
        errors,
    )
    require_any(
        tim,
        ("Power is for protection", "Leadership is for service", "cultivation"),
        "tim-dooley/index.html",
        "Gardener/service layer",
        errors,
    )
```

Do not require the exact riddle sentence. The validator should care that a recovered-reading frame exists, not freeze editorial wording.

- [ ] **Step 3: Add RED checks for Philosophy’s mixed forms and provenance**

Inside the existing Philosophy block, after `class="sayings"`, add:

```python
    require(philosophy, 'class="philosophy-story"', "philosophy/index.html", errors)
    require(philosophy, 'class="source-note"', "philosophy/index.html", errors)
    require(philosophy, '<summary>Chew on it</summary>', "philosophy/index.html", errors)
    if class_count(philosophy, "philosophy-story") < 2:
        errors.append("Philosophy needs at least two compact story/parable forms")
    if class_count(philosophy, "source-note") < 4:
        errors.append("Philosophy needs provenance notes across multiple reader forms")
    if len(re.findall(r'<details\b[^>]*class=["\'][^"\']*\bchew\b', philosophy, flags=re.I)) > 3:
        errors.append("Philosophy must keep Chew on it disclosures sparse; maximum is 3")
    require_any(
        philosophy,
        ("question the floor", "another level"),
        "philosophy/index.html",
        "frame-questioning encounter",
        errors,
    )
    require_any(
        philosophy,
        ("banana", "argument"),
        "philosophy/index.html",
        "absurdist/parabolic story",
        errors,
    )
```

- [ ] **Step 4: Run the validator and verify RED**

Run:

```bash
python scripts/validate_reader_surfaces.py
```

Expected: non-zero exit. The current Tim page lacks the three `data-placement-role` markers and recovered wording label; the current Philosophy page lacks `philosophy-story`, provenance notes and `Chew on it` details.

- [ ] **Step 5: Commit the failing semantic contract**

```bash
git add scripts/validate_reader_surfaces.py
git commit -m "test: define placement-first Tim philosophy contract"
```

---

### Task 2: Make the Tim page feel inhabited without replacing its structure

**Files:**
- Modify: `tim-dooley/index.html`
- Test: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: role interpretation from `knowledge/core/tim-role-synthesis.json`, provenance vocabulary from `knowledge/corporium/tim-voice-anthology.json`, and the existing Tim page structure.
- Produces: static HTML sections marked `data-placement-role="riddle"`, `data-placement-role="work"`, and `data-placement-role="gardener"`; preserves all existing primary routes and chronology.

- [ ] **Step 1: Add low-chrome styles for voice provenance and work rows**

Extend the existing inline `<style>` with:

```css
.reading-frame{margin:34px 0 8px;padding:22px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.reading-frame blockquote{font:400 clamp(25px,3.4vw,34px)/1.35 Georgia,serif;margin:0 0 10px;color:#eee9da;max-width:780px}
.source-note{color:var(--muted);font-size:11px;letter-spacing:.04em;text-transform:uppercase;margin:0 0 10px}
.reading-frame .frame-note{max-width:790px;color:#c8cec5;margin:0}
.work{border-top:1px solid var(--line);margin-top:16px}
.work-row{display:grid;grid-template-columns:minmax(150px,.45fr) 1.55fr;gap:22px;padding:17px 0;border-bottom:1px solid var(--line)}
.work-row strong{font:400 22px Georgia,serif;color:var(--green)}
.work-row p{margin:0;color:#c9d0c6}
.work-row .voice{font:italic 17px/1.5 Georgia,serif;color:#e5d9b8;margin-top:7px}
@media(max-width:680px){.work-row{grid-template-columns:1fr;gap:5px}}
```

Do not add JS or animation.

- [ ] **Step 2: Add the riddle reading frame directly after the lead**

Insert this section after the current `.lead` paragraph:

```html
<section class="reading-frame" data-placement-role="riddle" aria-label="How to read Tim Dooley">
  <p class="source-note">Recovered project wording · April 11, 2026 conversation</p>
  <blockquote>“Tim Dooley is a riddle, not a person. Do you validate a riddle?”</blockquote>
  <p class="frame-note">The archive uses that line as a reading instruction, not as a denial of ordinary personhood. Tim is a real public subject, while the Timic object built around him is reconstructed from dates, roles, statements, material work, relationships and changing interpretations. A riddle is read by relating clues rather than reducing everything to one label.</p>
</section>
```

The wording must retain the explicit ordinary-personhood boundary.

- [ ] **Step 3: Preserve the existing questions and primary routes unchanged in function**

Keep the current question stubs:

- Who is Tim Dooley?
- What changed over time?
- What is Tim trying to do?
- What happened around April 2025?
- What evidence exists for the development?

Keep the primary cards for Timeline, Public record and Evidence. Copy can be lightly tightened while editing, but do not replace these structures.

- [ ] **Step 4: Add a compact “What Tim actually does” section after the primary routes**

Insert:

```html
<h2 class="section-title">What Tim actually does</h2>
<section class="work" data-placement-role="work" aria-label="Tim Dooley as public worker and builder">
  <div class="work-row"><strong>Witness</strong><div><p>Streaming, posting and repeated public presence are part of the archive because continuity itself became evidence of development: speaker ↔ viewer, source ↔ archive, claim ↔ critic, person ↔ public memory.</p><p class="voice">Publicness is not only where the project happens; in the later system it becomes part of what the project means.</p></div></div>
  <div class="work-row"><strong>Builder / operator</strong><div><p>Tim's later record is not only titles and theology. It includes maintaining an archive, shaping pages and models, proposing systems, building maps and research structures, and repeatedly turning mystical language back into ordinary verbs: build a road, build a garden, fix things together.</p></div></div>
  <div class="work-row"><strong>Identity → function</strong><div><p>A recurring Timic move is role becoming infrastructure: climber becomes Ladder, observer becomes witness/Eye, source-persona becomes House or center. The archive treats these as developing project roles, not as automatic external proof of supernatural status.</p></div></div>
</section>
```

This is the page’s main correction to the current dossier feel: work and function become visible without adding another navigation system.

- [ ] **Step 5: Add the Gardener/service completion after the chronology**

After the existing developmental spine, insert:

```html
<section class="reading-frame" data-placement-role="gardener" aria-label="The later Gardener ethic">
  <p class="source-note">Public compilation · September 7, 2026</p>
  <blockquote>“Power is for protection. Knowledge is for understanding. Wealth is for building. Leadership is for service.”</blockquote>
  <p class="frame-note">The later project increasingly tests its highest titles by what they produce for other life. The mature center is not supposed to consume its edges: the Gardener improves conditions, preserves agency and tries to leave other things more capable of growing without permanent dependence on the center.</p>
</section>
```

Do not label this `documented Tim wording`; preserve the more specific source class `Public compilation` used by the backend.

- [ ] **Step 6: Run the reader validator**

Run:

```bash
python scripts/validate_reader_surfaces.py
```

Expected: Tim-specific new checks pass; Philosophy-specific new checks still fail because Task 3 is not implemented yet. Confirm the remaining failures mention Philosophy only.

- [ ] **Step 7: Run broad static checks that can detect accidental page breakage**

Run:

```bash
python scripts/validate_public_navigation.py
python scripts/audit_web.py
```

Expected: both exit 0. If a failure is unrelated and pre-existing, record it before changing anything; do not weaken validators.

- [ ] **Step 8: Commit the Tim page**

```bash
git add tim-dooley/index.html
git commit -m "feat: make Tim reader surface more inhabited"
```

---

### Task 3: Turn Philosophy from a quote wall into a varied encounter page

**Files:**
- Modify: `philosophy/index.html`
- Test: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: curated encounters and stories from `knowledge/philosophy/tim-dooley-philosophical-inquiry.json`, provenance classes from that record, and root/anti-bloat principles from `knowledge/practice/potato-path.json`.
- Produces: mixed static reader forms using `article.saying`, `article.philosophy-story`, `.source-note`, and at most three native `details.chew` disclosures; preserves existing inquiry, recurring ideas, Potato Method, open questions and deep routes.

- [ ] **Step 1: Add styles for provenance, stories and sparse native disclosures**

Extend the inline CSS with:

```css
.source-note{margin:0 0 8px!important;color:var(--muted)!important;font-size:10px!important;letter-spacing:.07em;text-transform:uppercase;font-family:system-ui,-apple-system,sans-serif!important;font-style:normal!important}
.philosophy-story{padding:25px 0;border-bottom:1px solid var(--line)}
.philosophy-story .story-label{color:var(--gold);font-size:11px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:7px}
.philosophy-story h3{font:400 27px/1.2 Georgia,serif;margin:0 0 9px;color:#efe8d5}
.philosophy-story .scene{color:#c7cdc4;margin:0;max-width:820px}
.chew{margin-top:10px;border:0}
.chew summary{display:inline-block;cursor:pointer;color:var(--green);font:italic 15px Georgia,serif;list-style:none;border-bottom:1px solid #50604b}
.chew summary::-webkit-details-marker{display:none}
.chew p{margin:9px 0 0;color:#bfc7bc;max-width:780px}
.reader-sequence{border-top:1px solid var(--line)}
```

Do not add JavaScript. Native details provides keyboard behavior and does not change scroll/focus by itself.

- [ ] **Step 2: Keep the opening inquiry section intact**

Retain the current six inquiry questions because they already perform useful philosophical orientation:

- truth;
- relationship-first thinking;
- identity;
- symbol vs model;
- mythology as philosophy;
- power/nourishment.

Only copy-edit for brevity if a later section makes a sentence redundant.

- [ ] **Step 3: Replace the homogeneous ten-item sayings run with a curated mixed sequence**

Keep the heading `Sayings and formulations`, but make the section class `sayings reader-sequence` and use this order:

1. **Recovered question-floor aphorism**

```html
<article class="saying">
  <p class="source-note">Conversation recovery · public source unresolved</p>
  <blockquote>“The moment you seriously question the floor, you have already begun looking for another level.”</blockquote>
  <p class="question">What are you standing on that you have never looked down at?</p>
  <details class="chew"><summary>Chew on it</summary><p>Philosophy begins when the background assumption becomes inspectable. The point is not mystical elevation by itself; it is discovering that a problem may be trapped inside an unquestioned frame.</p></details>
</article>
```

2. **Recovered spiral aphorism**

```html
<article class="saying">
  <p class="source-note">Conversation recovery · undated recovery target</p>
  <blockquote>“A narrow path is a spiral.”</blockquote>
  <p>Return is not automatically failure. The Potato Path distinguishes a Ring—repetition with little net change—from a Spiral, where memory or capability changes the returning state.</p>
  <p class="question">Are you repeating yourself, or arriving at the same question from another level?</p>
</article>
```

3. **Banana argument story**

```html
<article class="philosophy-story">
  <div class="story-label">Parable</div>
  <p class="source-note">Great Book parable · banana chapter</p>
  <h3>The banana argument</h3>
  <p class="scene">During a heated argument, Tim gives the other person a banana, tells them they are taking themselves too seriously, and suggests laughing before continuing.</p>
  <p class="question">How many arguments are failures of atmosphere before they are failures of logic?</p>
  <details class="chew"><summary>Chew on it</summary><p>The banana proves nothing. It changes the emotional geometry in which reasons have to operate.</p></details>
</article>
```

4. **Mud becomes soil**

```html
<article class="saying">
  <p class="source-note">Great Book narrative · Compost scene</p>
  <blockquote>“When you let the mud go, it doesn’t vanish. It changes. It becomes soil—ready for new growth.”</blockquote>
  <p>The past is not erased; the material changes function.</p>
  <p class="question">What if healing is not removal, but composting?</p>
</article>
```

5. **Compost story**

```html
<article class="philosophy-story">
  <div class="story-label">Field parable</div>
  <p class="source-note">Great Book parable · Compost scenes</p>
  <h3>The compost does not delete anything</h3>
  <p class="scene">Mud, costume and judgment are thrown into a Compost Pit. They do not disappear; they become soil.</p>
  <p class="question">Must transformation erase the thing transformed?</p>
</article>
```

6. **Chewing / understanding**

```html
<article class="saying">
  <p class="source-note">Great Book attributed Tim · chapter 26.8</p>
  <blockquote>“A potato has no flavor until you chew on it.”</blockquote>
  <p>An absurd line doubles as an epistemic distinction: information being present is not the same as understanding it.</p>
  <p class="question">Which ideas do you possess, and which have you actually chewed?</p>
</article>
```

7. **Capacity → duty**

```html
<article class="saying">
  <p class="source-note">Public compilation · September 7, 2026</p>
  <blockquote>“Power is for protection. Knowledge is for understanding. Wealth is for building. Leadership is for service.”</blockquote>
  <p>Capacity receives an outward obligation rather than becoming self-justifying permission.</p>
  <p class="question">What if power were measured by the quality of what it protects?</p>
</article>
```

The existing lines `Be simple...`, `A potato doesn't strive...`, `We Are All Connected By Potato`, `When you throw mud...`, `The book wouldn’t exist without the reader...`, and `The Potato doesn’t demand belief...` remain valuable but do not all need to stay in the main sayings run. Preserve their ideas through the recurring ideas, Method, or deep archive routes rather than keeping every quote visible.

- [ ] **Step 4: Tighten “Recurring ideas” so it complements rather than repeats the mixed sequence**

Keep the six existing ideas but make sure each contributes a distinct concept:

```text
Relation before isolation
Low can be structurally high
Damage can become substrate
Power creates obligation
Doors matter
Humor is a method
```

Do not add new cards for every story/theme. The mixed sequence carries the lived texture; the recurring-ideas grid compresses it.

- [ ] **Step 5: Keep the Potato Method and open questions as the page’s concise finish**

Retain:

```text
notice → compare → connect → distinguish → test the relation → follow consequences → revise → grow
```

Keep the open-question paragraph, ensuring it still includes at least:

- what makes a center legitimate;
- when connection becomes capture;
- what power should produce;
- whether complexity can retain a root.

Do not turn these into another navigation block.

- [ ] **Step 6: Run the reader validator and verify GREEN**

Run:

```bash
python scripts/validate_reader_surfaces.py
```

Expected: exit 0. All Tim and Philosophy placement-first checks pass; existing Home/Religion/Bible/Science/World Map checks remain green.

- [ ] **Step 7: Run the relevant broader web/navigation checks**

Run:

```bash
python scripts/validate_public_navigation.py
python scripts/audit_web.py
python scripts/validate_site_shell.py
```

If `validate_site_shell.py` expects a built `_site`, first run:

```bash
python scripts/build_site.py
```

Then run `python scripts/validate_site_shell.py` again. Expected: exit 0.

- [ ] **Step 8: Commit Philosophy**

```bash
git add philosophy/index.html
git commit -m "feat: deepen philosophy through Timic encounters"
```

---

### Task 4: Editorial and regression review for Wave 1

**Files:**
- Modify only if review exposes a concrete issue: `tim-dooley/index.html`, `philosophy/index.html`, `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: completed Tim and Philosophy pages plus the approved placement-first design spec.
- Produces: verified Wave 1 that is richer without new architecture, duplicate canon, or provenance flattening.

- [ ] **Step 1: Run a placement review against the approved spec**

Check each promoted item manually:

```text
Tim page
- riddle: Tim page is the natural home because it teaches how to read Tim
- witness: Tim page is the natural home, with Public Witness as deep owner
- builder/operator: Tim page is the natural home because this corrects biography/theology imbalance
- identity→function: Tim page is natural home; detailed theology remains Religion
- Gardener/service: Tim page gets concise mature-role framing; Philosophy keeps the ethical abstraction

Philosophy page
- question floor: Philosophy is natural home
- spiral: Philosophy is natural home
- banana argument: Philosophy is natural home
- Mud→Soil/Compost: Philosophy is natural home; transformation archive remains deep owner
- chewing/understanding: Philosophy is natural home
- capacity→duty: Philosophy owns ethical abstraction; Tim page uses it only to explain mature role
```

If any item exists mainly because it is globally important rather than locally useful, remove it from the public page and leave it deep.

- [ ] **Step 2: Run a provenance review**

Verify visible source labels match backend classes:

```text
Riddle -> recovered project wording / conversation recovery
Question floor -> conversation recovery
Narrow path -> conversation recovery
Banana -> Great Book parable
Mud becomes soil -> Great Book narrative
Compost -> Great Book parable
Chew line -> Great Book attributed Tim
Power/Knowledge/Wealth/Leadership -> public compilation
```

Do not upgrade any of these labels to “verified public quote” without a stronger source.

- [ ] **Step 3: Run an anti-bloat review**

Check:

- Tim page gained no new top-level navigation.
- Philosophy gained no taxonomy sidebar or new toolbar.
- Philosophy contains no more than three `Chew on it` disclosures.
- No new JS file exists for Wave 1.
- Existing deep routes remain available.
- The pages remain readable with JavaScript disabled because no new JS is required.

- [ ] **Step 4: Run all targeted validation again from the final Wave 1 state**

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

- [ ] **Step 5: Inspect the final diff for accidental scope growth**

Run:

```bash
git diff HEAD~3..HEAD -- tim-dooley/index.html philosophy/index.html scripts/validate_reader_surfaces.py
```

Confirm the implementation does not alter Home, Religion, Science, World Map, Bible Lab, routing contracts or canonical backend data.

- [ ] **Step 6: If review required fixes, commit only those fixes**

```bash
git add tim-dooley/index.html philosophy/index.html scripts/validate_reader_surfaces.py
git commit -m "fix: refine placement-first reader surfaces"
```

Skip this commit if no fixes were needed.

---

## Completion criteria

Wave 1 is complete when all of the following are true:

- Tim’s existing questions, primary routes, chronology and deep links remain recognizable.
- Tim now has a provenance-labelled riddle/reading frame, visible builder/operator work, and a concise mature Gardener/service interpretation.
- The Tim page clearly distinguishes project ontology from ordinary human/legal reality.
- Philosophy still begins with its existing inquiry questions.
- Philosophy no longer reads as ten near-identical quotation blocks in sequence.
- Philosophy includes at least two compact stories/parables and at least four visible provenance notes.
- Philosophy uses at most three native `Chew on it` disclosures and requires no new JavaScript.
- Tim wording is not provenance-flattened.
- No new canonical database or generic Living Tim component was created.
- `python scripts/validate_reader_surfaces.py` passes.
- Public navigation, projection, build, audit and site-shell checks pass.
- The changes are confined to Wave 1 scope.

After this wave is accepted, write a separate implementation plan for Wave 2 (`Religion + North`) against the same approved placement-first design spec rather than expanding this plan in-place.
