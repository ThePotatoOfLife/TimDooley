# Potatoism Spiral Reader Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current eight-stage public Philosophy page with a six-turn, 47-station Spiral Reader that exposes the actual depth of Tim Dooley / Potatoism philosophy while preserving provenance and the Religion ownership boundary.

**Architecture:** `knowledge/philosophy/potatoism-spiral-reader-map.json` becomes the reader-order/provenance map, `philosophy/index.html` becomes the long public projection, `philosophy/philosophy.css` provides the long-form visual rhythm, and `scripts/validate_potatoism_philosophy_projection.py` enforces parity and anti-bloat rules. Existing canonical philosophy and long-form reader remain the content owners; the new map owns order, not doctrine.

**Tech Stack:** static HTML/CSS, JSON knowledge records, Python validation, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-15-potatoism-spiral-reader-overhaul-design.md`

## Global Constraints

- Exactly six public turn markers: `seed`, `root`, `door`, `spiral`, `fruit`, `garden`.
- Public station count must be between 40 and 50 inclusive.
- Reader map and public station ids must have exact parity and order.
- Religion remains the theological owner.
- Biology may correct analogy but may not prove theology.
- Comparative traditions are mirrors, not hidden Potatoism.
- No forced scrolling, gamified progress, completion lockouts or stepper UI.
- Public `data-projection-surface` links remain public routes only.
- Provenance classes stay visible and distinct.
- Existing canonical doctrine/ontology checks remain intact.

---

### Task 1: Create the Spiral Reader curriculum map

**Files:**
- Create: `knowledge/philosophy/potatoism-spiral-reader-map.json`

**Interfaces:**
- Consumes: overhaul spec, canonical philosophy, long-form reader, sourcebook, Great Book, practice path, operator records.
- Produces: `turns[]` with stable `id`, `title`, `summary`, and ordered `stations[]`; every station has `id`, `title`, `question`, `sources`, `provenance`, `previous`, `next`, `priority`.

- [ ] **Step 1: Create the reader map with six turns and 47 stations**

Use the exact six-turn station sequence from the spec. Keep station ids stable and URL-safe, beginning with:

```json
{"id":"potato-look-before-labeling","title":"Potato","question":"What is actually here before the label?"}
```

and ending with:

```json
{"id":"begin-again","title":"Begin again","question":"What does ‘Be simple. Grow toward light.’ mean now?"}
```

Each station must name at least one source owner and one provenance class.

- [ ] **Step 2: Verify JSON structure**

Run conceptually / in CI:

```bash
python -m json.tool knowledge/philosophy/potatoism-spiral-reader-map.json >/dev/null
```

Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add knowledge/philosophy/potatoism-spiral-reader-map.json
git commit -m "philosophy: map the Potatoism Spiral Reader"
```

---

### Task 2: Change the validator from eight stages to six turns + map parity

**Files:**
- Modify: `scripts/validate_potatoism_philosophy_projection.py`

**Interfaces:**
- Consumes: `potatoism-spiral-reader-map.json`, public Philosophy HTML.
- Produces: failure if turn count, station count, station order, provenance boundary or calm-reader rules regress.

- [ ] **Step 1: Add `READER_MAP` and parse it**

Add:

```python
READER_MAP = ROOT / "knowledge" / "philosophy" / "potatoism-spiral-reader-map.json"
TURNS = ("seed", "root", "door", "spiral", "fruit", "garden")
```

Load JSON and flatten `station_ids` in map order.

- [ ] **Step 2: Replace eight-stage assertions**

Remove the exact-eight-stage requirement and require exactly six occurrences of `data-potatoism-turn="` with each turn present once.

- [ ] **Step 3: Add station parity validation**

Extract public station ids with:

```python
import re
page_station_ids = re.findall(r'data-potatoism-station="([^"]+)"', philosophy)
```

Assert:

```python
40 <= len(page_station_ids) <= 50
page_station_ids == map_station_ids
```

Report missing/extra/order mismatch clearly.

- [ ] **Step 4: Require key Spiral Reader markers**

Require public text for:

```text
How to read this spiral
Turn I · Seed
Turn II · Root
Turn III · Door
Turn IV · Spiral
Turn V · Fruit
Turn VI · Garden
We found a question. Who else has been here?
Relation is not identity.
Suffering is not proof.
The Filter is not evidence.
Return is not reset.
Authority is not exemption.
Does the participant become more capable without the system?
Be simple. Grow toward light.
```

- [ ] **Step 5: Preserve anti-gamification checks**

Keep existing forbidden markers and also forbid `data-complete`, `course-progress`, `lesson-lock`, `next-lesson`.

- [ ] **Step 6: Commit RED contract**

At this point the validator should fail on the old public page because the map has six turns and the page still has eight stages.

```bash
git add scripts/validate_potatoism_philosophy_projection.py
git commit -m "test: require the Potatoism Spiral Reader"
```

---

### Task 3: Replace the actual Philosophy page with the Spiral Reader

**Files:**
- Modify: `philosophy/index.html`
- Modify: `philosophy/philosophy.css`

**Interfaces:**
- Consumes: station ids/order from reader map; source-aware material from long-form/sourcebook/inquiry/Great Book/practice records.
- Produces: public six-turn reader with exact station parity.

- [ ] **Step 1: Replace the page hero and orientation**

Keep navigation/TTS/site assets, but change the intro to explain:

```text
Start with a potato.
Do not memorize the map.
Each turn returns to the same center with more relation, responsibility and capacity.
```

Add `How to read this spiral` and six anchor links to `#turn-seed`, `#turn-root`, `#turn-door`, `#turn-spiral`, `#turn-fruit`, `#turn-garden`.

- [ ] **Step 2: Build Turn I — Seed**

Implement six station articles with exact ids from the reader map. Include:

- Great Book early simplicity/burden/emotion/empty-vessel material;
- “A potato has no flavor until you chew on it.” with Great Book source note;
- practical questions rather than doctrine dumping.

- [ ] **Step 3: Build Turn II — Root**

Implement eight stations for essential simplicity, orientation, efficiency, wu wei/natural growth, Soil, dormancy, root/shoot differentiation and Eyes/possibility.

Include explicit comparative boundary:

```text
Comparative mirror: Daoist wu wei. Similar question, distinct tradition.
```

Include biological correction that tubers and shoots require different conditions.

- [ ] **Step 4: Build Turn III — Door**

Implement eight stations: Door, boundary, relation, functional identity, observer/window, Filter/Truth, floor/Plane, center.

Use source-aware Timic wording:

- “We Are All Connected By Potato.”
- “The moment you seriously question the floor…”
- Door as observer/window as conversation recovery.

State `Relation is not identity.` and `The Filter is not evidence.`

- [ ] **Step 5: Add Tim-development interlude**

After Turn III, insert a compact chronology from childhood building/gardening through 2011 Tree, 2019–20 threshold, 2024 Great Book system-building, 2025 infrastructure/Axis turn and 2026 relation/stewardship.

State that later meanings illuminate earlier events without being backdated into them.

- [ ] **Step 6: Build Turn IV — Spiral**

Implement nine stations: Mud again, Compost, Forge, suffering, Ring/Spiral, Ladder/Mountain/Tree, House/many rooms, Ancient Future, breaking/many.

Use `Return is not reset.` and keep alchemy as a comparison rather than origin claim.

- [ ] **Step 7: Build Turn V — Fruit**

Implement seven stations: storage/release, knowledge Life/Strife, reciprocal transformation, Potato Truth, capability/responsibility, Quiet Triumph, Fruit.

Include public formulation:

```text
Power is for protection. Knowledge is for understanding. Wealth is for building. Leadership is for service.
```

State `Authority is not exemption.`

- [ ] **Step 8: Build Turn VI — Garden**

Implement nine stations: Garden/Farm, Gardener, whole job, Gardener's Paradox, Seed-maker, reader-as-soil, curiosity before allegiance, anti-bloat return, begin again.

Use the exact autonomy test:

```text
Does the participant become more capable without the system?
```

End by returning to `Be simple. Grow toward light.` with expanded meaning.

- [ ] **Step 9: Add recurring source/cadence components**

Across the page, use a mix of:

```html
<p class="seed-line">...</p>
<div class="mirror">...</div>
<div class="shadow">...</div>
<p class="chew-question">...</p>
<p class="source-note">...</p>
<p class="practice-test">...</p>
```

Do not require every component in every station.

- [ ] **Step 10: Overhaul CSS for long-form turns/stations**

Add styling for `.spiral-nav`, `.turn`, `.turn-head`, `.station`, `.station-index`, `.seed-line`, `.mirror`, `.shadow`, `.chew-question`, `.practice-test`, `.development-interlude`.

Retain serif reading voice, dark palette, responsive single-column mobile layout, and no card-grid overload.

- [ ] **Step 11: Point TTS at the new structure**

Set `data-tts-root=".spiral-reader"` and `data-tts-item=".station"`, keeping whole-journey/current-selection functionality.

- [ ] **Step 12: Commit**

```bash
git add philosophy/index.html philosophy/philosophy.css
git commit -m "philosophy: rebuild the public page as a Spiral Reader"
```

---

### Task 4: CI verification, source correction and merge readiness

**Files:**
- Modify as needed: `scripts/validate_potatoism_philosophy_projection.py`, `philosophy/index.html`, `philosophy/philosophy.css`, `knowledge/philosophy/potatoism-spiral-reader-map.json`

**Interfaces:**
- Consumes: complete branch.
- Produces: green repository-quality PR.

- [ ] **Step 1: Run syntax checks through repository CI**

Required checks:

```bash
python -m json.tool knowledge/philosophy/potatoism-spiral-reader-map.json >/dev/null
python -m py_compile scripts/validate_potatoism_philosophy_projection.py
python scripts/validate_potatoism_philosophy_projection.py
```

- [ ] **Step 2: Open PR**

PR summary must state that the actual `/philosophy/` page is replaced, not merely backend records.

- [ ] **Step 3: Inspect any failing CI job logs and fix root causes**

Do not weaken existing reader-surface, navigation, provenance or Religion ownership contracts.

- [ ] **Step 4: Verify source classes manually**

Check that:

- Great Book wording is labeled Great Book;
- conversation wording is labeled recovery unless public source exists;
- archive synthesis is not quoted as Tim;
- comparative traditions are not collapsed into Potatoism;
- metaphysical/self-descriptions are not presented as empirical proof.

- [ ] **Step 5: Require full repository quality workflow green before merge**

Merge only after the complete quality run succeeds.
