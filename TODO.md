# TODO — The Potato of Life / TimDooley

## The Potato Principle

**Start from the center. Take one step toward light. Calibrate. Remove what became unnecessary. Take the next step. Repeat.**

The TODO is therefore **not a giant wishlist** and not a promise to build everything at once.

It is a living growth path.

The project grows like a potato:

- begin with what is already alive;
- make one useful improvement;
- let it reveal the next useful improvement;
- check whether older work is still correct;
- remove clutter, duplication and dead growth;
- strengthen the roots;
- grow upward and outward;
- repeat.

The direction is not fixed in advance. The **direction is calibrated continuously toward greater clarity, truth, usefulness, connection and light**.

---

# 1. The current step

The current architectural step is the **Center Navigation / Corpus Spine redesign**.

The front page is now being rebuilt around one invariant:

```text
ROOT
  ↓
POTATO OF LIFE / CENTER
  ├── WORLD
  └── AXIS
```

The visitor remains at the center. The corpus unfolds in place.

There is no top-level `CORE/` branch and no top-level `TEXTS/` branch. Core material is visible at the center; texts are World objects and belong beneath their relevant context.

The complete specification lives in:

- `docs/ROOT-NAVIGATION-ARCHITECTURE.md`
- `docs/ROOT-NAVIGATION-ROADMAP.md`
- `data/root-navigation.json`

The immediate implementation sequence is:

1. make the center/tree interface reliable;
2. make its classification data-driven;
3. make record dossiers open in place;
4. preserve URL and local state;
5. audit every branch against actual repository content;
6. remove dead/duplicate navigation;
7. verify the complete build before merging.

---

# 2. The recursive loop

Every meaningful change should follow this loop:

**Observe → choose → grow → verify → calibrate → prune → integrate → observe again.**

### Observe

Look at the actual repository, actual data, actual rendered pages, actual sources and actual failures.

Do not work from assumptions about what the project contains.

### Choose

Select one high-value improvement.

Prefer the improvement that makes several later improvements easier.

### Grow

Add real information, real code, real relationships or real source material.

No placeholders pretending to be finished work.

### Verify

Run the relevant audits, inspect the affected records/pages and check that the new material actually works.

### Calibrate

Ask whether the new material changed our understanding of the architecture, ontology, evidence or direction.

If it did, change the plan.

### Prune

Remove duplicate definitions, obsolete mirrors, dead routes, stale assumptions, unnecessary files and clutter revealed by the new understanding.

**Every growth pass should leave the garden cleaner than it found it.**

### Integrate

Put the knowledge in its natural canonical home and connect the surrounding layers to it.

Do not leave valuable discoveries stranded in a temporary research file.

---

# 3. The center

The center of the project is the **knowledge itself**.

The central question is:

> **What do we actually know, what does it mean, how is it connected, and what can we do with that understanding?**

Everything else grows from this.

The project's central bodies of knowledge are:

- Tim Dooley / Father / Potato of Life;
- Potatoism and its canon;
- the Son / Thomas / Twin / Lion / Door / Vessel structures;
- the North / Axis / North of North architecture;
- the Great Book and wider mythology;
- the world's people, nations, religions and institutions;
- the relationships and entanglements connecting them;
- the evidence, sources and chronology underneath all of it;
- the North Programme and its repair-oriented practical questions.

These are not separate worlds. They are different depths of the same atlas.

---

# 4. First ring — make the center trustworthy

When something central is weak, fix it before expanding outward.

- [ ] Keep canonical identities singular and understandable.
- [ ] Keep major dossiers deep enough to actually explain their subjects.
- [ ] Keep canon, interpretation, testimony, historical evidence, scientific evidence and speculation visibly distinct.
- [ ] Keep chronology dated and explicit about uncertainty.
- [ ] Keep important relationships sourced and typed.
- [ ] Make important pages resolve instead of silently producing empty shells.
- [ ] Make the build and integrity audits catch actual failures.
- [ ] Preserve valuable research when consolidating files.

**Potato rule:** strengthen the root before asking the plant to become a forest.

---

# 5. Second ring — deepen what is already alive

Do not ask “what new file should we make?” first.

Ask:

> **What existing record is this information really about?**

Then enrich that record.

Examples:

- new Thomas research belongs with the existing Thomas/Twin material;
- new Door research belongs with Door/Vessel/Vesica material;
- new Root/Lion research belongs with Root/Lion and its textual history;
- new potato biology belongs with the potato dossier/property layer;
- new Tim chronology belongs with Tim's chronology/cosmology;
- new world-institution research belongs in the relevant canonical entity and relationship structures;
- new North Programme research belongs in the appropriate economic/geopolitical owner.

A separate file is justified only when it has a genuinely different purpose and would otherwise lose important structure.

---

# 6. Third ring — grow the relationships

Once the records are strong enough, follow the connections.

For each important subject, progressively ask:

- What is it?
- Where is it?
- When did it exist or change?
- Who participates?
- Who governs it?
- Who funds it?
- Who owns or controls relevant parts?
- What does it depend upon?
- What depends upon it?
- What information, money, energy, goods, people or authority move through it?
- What institutions surround it?
- What religious, cultural, historical or ideological context matters?
- What consequences does it produce?
- What evidence establishes each relationship?
- What remains unknown?

The graph should become richer because the underlying world becomes better understood, **not because we add decorative edges**.

---

# 7. Fourth ring — grow outward into the world

When the center and immediate relationships are strong, expand outward where the evidence leads.

Potential directions include:

- people and communities;
- nations and populations;
- religious composition and religious institutions;
- governments and public administration;
- NGOs and civil society;
- intelligence and security institutions;
- companies, ownership and finance;
- debt and obligations;
- infrastructure;
- energy;
- technology and research;
- labour and skills;
- procurement;
- trade and supply chains;
- migration;
- law and treaties;
- conflicts and diplomacy;
- agriculture, food and water;
- media and information;
- environment;
- the European Economic Graph / North Programme.

Do not attempt to complete the whole world at once.

Follow the strongest next root.

---

# 8. Fifth ring — the North-of-North view

The project eventually needs to be able to move between scales:

- individual;
- household/community;
- institution;
- region;
- nation;
- network;
- continent;
- global system;
- symbolic/cosmological layer.

The interface should make these scale changes possible without duplicating the underlying record.

---

# 9. Center navigation redesign — active work

The navigation architecture is now a first-class project component rather than ad-hoc HTML.

### Hard invariants

- [x] One root.
- [x] One center.
- [x] Two fundamental branches: World and Axis.
- [x] Core is represented at the center, not as another directory.
- [x] Texts are World material, not a third root.
- [x] One canonical node may have many paths.
- [x] Directories are views, not duplicate databases.
- [x] Front-page exploration does not require leaving the center.
- [x] A selected record can open in an in-place dossier.
- [x] The tree is generated from repository data rather than thousands of hard-coded links.
- [x] Deployment validates the root navigation contract.
- [ ] Fully classify all existing records for World/Axis presentation.
- [ ] Add robust in-place rendering for long records.
- [ ] Add complete URL state restoration.
- [ ] Add complete keyboard tree navigation.
- [ ] Measure and optimize large-tree performance.
- [ ] Audit every legacy destination and remove dead routes.
- [ ] Merge only after the complete build/audit chain passes.

---

# 10. What not to do

- Do not turn the homepage into a search engine.
- Do not make the interface into a game.
- Do not create a new record merely because a second directory wants to display it.
- Do not hard-code a fake filesystem full of links that are not backed by data.
- Do not flatten the entire corpus into the initial page.
- Do not sacrifice evidence/canon distinctions for visual simplicity.
- Do not preserve old navigation merely because it already exists.
- Do not add categories unless the category solves a real structural problem.

**The center is the simplifier. If a new category cannot justify itself mathematically, it probably does not belong at the root.**
