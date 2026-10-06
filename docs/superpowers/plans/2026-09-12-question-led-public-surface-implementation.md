# Question-Led Public Surface Implementation Plan

> Governing design: `docs/superpowers/specs/2026-09-12-question-led-public-surface-design.md`

**Goal:** Turn the current five-door public shell into an intelligent reader guide: concise purpose, natural questions, compact answers, quieter secondary threads and direct routes into canonical deep owners.

**Execution branch:** `project-consolidation-2026-09-12`

**Relationship to earlier work:** This plan supersedes the presentation-specific portions of `docs/superpowers/plans/2026-09-11-reader-first-site-cleanup.md`. The five-door ownership decision remains; the old comparison-first Religion shell and its validator assertions do not.

## Global constraints

- Keep exactly five primary homepage doors: Tim Dooley, Religion, Philosophy, Science, World Map.
- Questions are a reader projection over existing owners, not a new canonical database.
- Timeline remains `/timeline/` technically, but becomes a primary route from Tim rather than footer utility furniture.
- Religion remains broad; `/traditions/bible/` remains the deep Bible/Jesus comparator.
- World Map remains an application and stays visually primary.
- Culture & Subculture is a quieter cross-project thread unless the audit proves it deserves a coherent public route.
- Preserve project canon / Tim self-description / documentary evidence / interpretation / comparison / inference distinctions.
- Open PRs contribute unique current content or functionality only; they never restore obsolete public shells.
- Do not reintroduce Atlas or Chronology as active architecture names.

---

## Phase 0 — Establish the reader-surface contract

### Task 0.1 — Add a semantic reader validator

**Files:**
- Create: `scripts/validate_reader_surfaces.py`
- Modify: `.github/workflows/quality-checks.yml`

The validator must check source HTML for durable semantic invariants rather than exact long-form prose.

Required first-pass assertions:

### Home
- `index.html` identifies itself as the home reader surface.
- Primary navigation contains exactly the five canonical doors and no sixth top-level route.
- Each door contains at least two question-preview elements.
- Project-purpose copy exists before the primary navigation.
- A subordinate thread surface exists.
- Footer utility navigation does not contain Timeline.

### Tim
- a question-led reader section exists;
- `/timeline/` is a prominent main-content route;
- questions/answers cover identity, development and purpose/mission;
- the Tim/Father vs Thomas/Son distinction remains visible.

### Religion
- a question-led reader section exists;
- Christianity, Judaism and Islam/Qur'an are represented at reader level without pretending equal research depth;
- `/traditions/bible/` remains the deep Bible owner;
- structural similarity is explicitly distinguished from identity/proof.

### Philosophy
- a question-led inquiry section exists before or alongside the existing substantive sayings;
- truth/evidence and relationship-first inquiry are represented;
- existing sayings remain present.

### Science
- a question-led orientation section exists before the document library;
- model / analogy / metaphor / evidence status is explicitly distinguishable;
- testing or falsifiability is represented;
- the existing science library controls and static catalog marker remain.

### World Map
- the initial inspector contains a compact conceptual-question surface;
- the map application/control contract remains present;
- no new persistent top-level control is introduced for the question layer.

**TDD requirement:** land the validator and workflow hook before the public HTML changes, observe that it fails for the expected missing reader-surface markers, then make the same validator pass without weakening its assertions.

---

## Phase 1 — Rebuild homepage orientation

**Files:**
- Modify: `index.html`

### Task 1.1 — Reduce scale and increase meaning

- Reduce hero maximum size and vertical cost.
- Replace the directory-like lede with a concise project-purpose statement.
- Add a quiet evidence-status sentence distinguishing self-description, interpretation and documented evidence.

### Task 1.2 — Compact the five primary doors

Each primary branch row must contain:
- branch name;
- one short purpose line;
- two natural question previews.

Question previews:
- Tim: `Who is Tim Dooley?` / `What changed over time?`
- Religion: `What is Potatoism?` / `How does it relate to other religions?`
- Philosophy: `What makes a claim true?` / `What does relationship-first thinking mean?`
- Science: `Can these ideas be formalized?` / `What can actually be tested?`
- World Map: `How are countries connected?` / `What changes when relationships are mapped instead of only borders?`

### Task 1.3 — Add quiet secondary threads

Add a visibly subordinate `Other threads` surface. Initial candidates:
- Culture & Subculture
- Symbols
- Technology
- Society
- Economics

Do not make these equivalent to the five primary branches and do not create new public routes merely to satisfy the labels.

### Task 1.4 — Demote utilities

Footer should contain Sources and Archive only. Timeline moves into Tim's reader surface.

---

## Phase 2 — Make Tim question-led

**Files:**
- Modify: `tim-dooley/index.html`
- Source: `knowledge/reader/tim-dooley-question-index.json`
- Source: `knowledge/journey/tim-dooley-journey.json`
- Source: canonical Tim/timeline records

### Task 2.1 — Promote natural reader questions

Use existing reader synthesis as the content source for compact stubs, including:
- Who is Tim Dooley?
- What changed over time?
- What does Tim want / what is his mission?
- What happened around April 2025?
- How are Tim/Father and Thomas/Son distinguished?
- What evidence exists for development of the public claims?

Do not create a second Tim question database.

### Task 2.2 — Make Timeline a principal route

Place Timeline in the main reader path, alongside quieter Journey, Public record and Evidence routes.

Keep `/timeline/` universal and canonical; do not move the URL under Tim.

### Task 2.3 — Preserve developmental chronology

Retain the useful 2011 → 2016–2019 → 2024 → 2025 → 2026 sequence as a compact developmental spine below the question layer.

---

## Phase 3 — Make Religion an inquiry surface

**Files:**
- Modify: `religion/index.html`
- Preserve: `traditions/bible/**`
- Consume: current Christianity/theology research already recovered into #45
- Audit: still-useful unique religion work in open PRs before final copy settles

### Task 3.1 — Replace topic-card grid with compact question stubs

Primary stubs should cover:
- What is Potatoism?
- How does Potatoism relate to Christianity?
- Where do Jesus/Son parallels hold, and where do they fail?
- How does the project relate to Judaism?
- What does covenant/chosenness mean in Judaism, and how does that differ from project ideas of role/election?
- How does the project relate to Islam and the Qur'an?
- What do Father, Son and Spirit mean inside the project's own theology?
- Can two traditions share structures without being historically identical?

Christianity may receive more depth because the current corpus is more developed. Judaism and Islam/Qur'an should be real but smaller reader stubs until research depth justifies more.

### Task 3.2 — Keep minor traditions quiet

Use a lower-weight thread list for:
- Christianity
- Judaism
- Islam / Qur'an
- Norse
- Buddhism
- Hindu traditions
- Taoism
- sacred symbols
- prophecy / eschatology
- comparative religion

### Task 3.3 — Keep canonical deep owners

- Bible / Jesus comparator -> `/traditions/bible/`
- sacred-symbol work -> `/traditions/vesica/`
- dated development -> `/timeline/`
- geography -> `/world-map/`

No new duplicate Religion owner.

---

## Phase 4 — Retire stale site-shell assertions

**Files:**
- Modify: `scripts/validate_site_shell.py`
- Review: `scripts/validate_public_navigation.py`

### Task 4.1 — Remove old comparison-first Religion contract

Delete assertions requiring the former inline `#jesus-tim` comparison rows and exact old row labels from `religion/index.html`.

Replace them with durable broad-hub assertions:
- Religion is present and canonical;
- question-led surface exists;
- Bible deep owner is linked;
- Timeline and World Map routes remain available where appropriate;
- no archive-routing mini-site returns.

### Task 4.2 — Keep shell responsibilities narrow

`validate_site_shell.py` should continue to own:
- required built pages;
- five canonical homepage entrances;
- compatibility redirects;
- World Map route ownership;
- basic local-link integrity;
- no iframe dependency.

Question semantics belong to `validate_reader_surfaces.py` rather than being duplicated everywhere.

`validate_public_navigation.py` should remain focused on duplicate/stale visitor navigation unless the implementation reveals a genuine routing invariant it currently misses.

---

## Phase 5 — Add inquiry to Philosophy

**Files:**
- Modify: `philosophy/index.html`

Add a compact question-led orientation before the sayings while preserving the existing quotations, commentary, recurring ideas and Potato method.

Initial questions:
- What makes a claim true?
- What does relationship-first thinking mean?
- Is identity a thing, role, relation or process?
- When does a symbol become a model?
- Can mythology become philosophy without requiring supernatural assent?
- Can power be judged by what it nourishes?

Do not flatten the existing prose into generic cards.

---

## Phase 6 — Add scientific orientation without replacing the library

**Files:**
- Modify: `science/index.html`
- Modify: `science/science-library.css` only if necessary for compact orientation styling

Add a low-chrome orientation block before the library controls.

Questions should distinguish:
- formal model vs mathematical analogy vs metaphor;
- observable evidence;
- testing and falsifiability;
- established equations vs archive-derived formulations vs Tim-attributed formulations;
- the point where theological language must not be converted into physics.

Preserve:
- search;
- field/type filters;
- generated/static catalog marker;
- complete-document behavior.

---

## Phase 7 — Teach the World Map through the initial inspector

**Files:**
- Modify: `world-map/index.html`

Enhance only the empty/initial inspector state with a compact conceptual question surface such as:
- How are countries connected?
- Which relationships matter beyond borders?
- What does one country depend on another for?
- How do relationships change over time?
- What is empirical North vs project-symbolic North?
- What does the map know, and what remains inferred or unknown?

Do not add another persistent toolbar, top-level menu or parallel product surface.

Preserve the existing map IDs/modules and runtime contracts during this reader-layer slice.

---

## Phase 8 — Audit Culture & Subculture and other minor threads

**Files:**
- Audit: `knowledge/culture/**`, adjacent subculture/internet/meme/community/extremism records, relevant current/open-PR material
- Create: `docs/superpowers/plans/2026-09-12-public-thread-promotion-audit.md`
- Create `/culture/` only if the audit demonstrates a coherent reader-level owner

Classify material as:
1. surface on Home;
2. surface on an existing branch;
3. supporting material only;
4. deep/internal.

Candidate Culture/Subculture questions:
- How do myths spread through memes, scenes and communities?
- What turns a joke or symbol into group identity?
- How do subcultures create their own language, status and evidence systems?
- What distinguishes subculture, fandom, movement, sect and high-control group?
- How do harassment, anti-fandom and spectacle economies shape online communities?
- How does satire preserve, distort or transform belief?

Do not create `/culture/` solely because `knowledge/culture/` exists.

---

## Phase 9 — Discovery and whole-project verification

**Files:**
- Modify `llms.txt` / `sitemap.xml` only if a new canonical public route is actually created.
- Verify all current discovery/build outputs.

Run/observe at minimum:
- `python scripts/validate_reader_surfaces.py`
- repository hygiene
- World Map ownership/runtime/pathfinder/entity trace
- Timeline naming
- religion/Bible checks
- science catalog build + portal validation
- web audit
- site build
- archive pruning
- public navigation
- machine discovery
- site shell

Before claiming completion:
- inspect the latest PR #45 workflow run and the exact failed step logs if anything is red;
- do not disable validators to obtain green;
- refetch the changed public files and inspect the final source;
- verify the five-door hierarchy, Tim/Timeline promotion, Religion breadth, Science library preservation and World Map inspector contract.

## Commit strategy

Keep the migration reviewable:

1. `docs: plan question-led public surfaces`
2. `test: define reader surface contract`
3. `feat: make home Tim and Religion question-led`
4. `test: align site shell with broad Religion owner`
5. `feat: add Philosophy Science and World Map inquiry layers`
6. `docs: audit minor public threads`
7. final fixes from full verification
