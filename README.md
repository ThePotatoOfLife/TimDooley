# The Potato of Life — Living Atlas

This repository is the source archive, research engine and static public atlas for the Tim Dooley / Potatoverse project.

## Start here

**Read first:** [`docs/TIM-DOOLEY-CANON.md`](docs/TIM-DOOLEY-CANON.md)

Then use the public site to navigate the repository, timeline, world, people, ideas, books, Potatoism and movements layers. The repository is deliberately being built as a **relationship-first knowledge system**: records are useful, but the connections between records are the main object of study.

## What changed in the stable architecture

The project is now large enough that reliability has to be treated as part of the data model. The build generates a repository-wide index from the JSON tree, validates the static artifact before deployment, and keeps canonical records distinct from derived views, research layers and archives. The browser should not have to guess which of dozens of files contains a record.

The intended pipeline is:

**source data → canonical/derived indexes → integrity audits → static build → deployment → human check**

A missing optional record should be visible as missing; it should not silently turn into an empty page. A bad source file should be isolated by the build and reported by validation. A relationship should not manufacture a node merely because an identifier appears at one end of an edge.

## The Great Book of Potato

The Great Book is a growing library rather than a single page:

1. **The Potato** — mud, root, nourishment, regeneration and absurdity.
2. **The Father** — Tim Dooley, Source, Garden, Tree, House and Throne.
3. **The Son** — Jesus, Thomas, Twin, Lion, Joseph, Red Heifer and vessel.
4. **The Door** — Vesica Piscis, mandorla, Narrow Gate, Needle's Eye and interface.
5. **The Tree** — roots, trunk, branches, fruit and seed.
6. **The Tree of Strife** — Swamp, Mud, Drains, Dogs, Farmers and extraction.
7. **The Axis** — North, South, East, West, ladder, mountain and polar orientation.
8. **The Spiral** — time, recurrence, 33, 100,000 hours, death and return.
9. **The Cube** — Saturn, enclosure, rigidity, bureaucracy and material limitation.
10. **The Mill** — wind, grain, flour, transformation, debt and the millstone.
11. **The Ancient Mirrors** — Odin, Tammuz, Genesis, Abraham, Moses, David, Jesus and Thomas.
12. **The Body** — breath, spine, brain, thalamus, pineal metaphor and embodiment.
13. **The Potatoverse** — internet culture, memes, stories, livestreaming, humour and digital mythology.
14. **The North Programme** — Europe, Canada, Greenland, economics, energy, infrastructure, technology and geopolitics.
15. **The Kingdom** — Spudlight, Garden, renewal, civilization and the New Earth as a symbolic horizon.

## The core architecture

**Tim Dooley → Source → Separation → Ladder → Door → Son → Tree of Life → Tree of Strife → Potato → World → North Programme**

The project deliberately maintains two complementary disciplines:

- **empirical:** people, nations, companies, money, debt, ownership, infrastructure, procurement, energy, trade, research, labour, technology and geopolitical relationships;
- **symbolic/project-defined:** Potatoism, mythology, archetypes, geometry, metaphor, narrative and interpretive structures.

The two can be compared and connected, but a symbolic edge is never silently promoted to empirical evidence.

## Canonical data principles

### 1. One canonical owner

An important identifier should have one canonical home. Indexes, enrichments, research notes, graph projections and archives should point back to it rather than becoming competing copies.

### 2. Relationships first

A country is a node. A company is a node. A person is a node. A debt is a node. A cable, port, treaty, research institute or source document can be a node. But the relationship tells us what the node actually does in the system: owns, controls, funds, depends on, supplies, regulates, influences, competes with, migrates through, cites or transforms.

### 3. Time matters

Anything that can change should carry a date, valid period or reference year. Current, historical and projected states must not be silently mixed.

### 4. Evidence has a type

The archive distinguishes observed facts, calculations, estimates, scenarios, historical claims, interpretations, mythology and creative material. Provenance should retain source, source type, methodology, date and confidence whenever possible.

### 5. Missing is a real state

Unknown, unavailable, disputed and not-yet-researched are different from zero, false or nonexistent. The project should preserve those distinctions.

### 6. Depth must be independent of the graph

A relationship is not a substitute for a dossier. Important records should explain what something is, its history, function, context, population or users, institutions, geography, evidence, uncertainty and relationships.

## Blueprint system

The blueprint registry is the ontology layer behind future expansion. It currently covers country, people/dwellers, culture/subculture, religion, governance, finance/debt, ownership/control, companies, supply chains, energy, trade, research, law, media, health, education, environment, security, infrastructure, labour, procurement, demography, agriculture/food/water, technology, events, places, movements, extremism/high-control, treaties, resources and related structures.

Blueprints should become progressively more useful rather than merely longer. A good blueprint specifies:

- identity and aliases;
- classification boundaries;
- temporal fields;
- geography and population;
- organization and institutions;
- operation/function;
- ownership, funding or control where relevant;
- material and technical dependencies;
- relationships and edge types;
- evidence and provenance;
- derived measures;
- uncertainty and failure modes;
- validation rules;
- refresh/acquisition requirements.

## Wise notes for future work

These are deliberately kept here as engineering/research lessons for the next expansion phase:

> **Do not solve a missing-data problem by adding another mirror.** First decide which file owns the concept, then make every other layer reference or enrich that owner.

> **If a page can fail silently, the project will eventually fail mysteriously.** Prefer explicit diagnostics, build-time checks and visible empty/error states over graceful-looking blanks.

> **A blueprint is valuable when it changes what we can collect and validate.** More fields alone are not more knowledge; the fields should expose mechanisms, relationships, time, evidence and uncertainty.

> **Never confuse a graph endpoint with a canonical record.** An ID appearing in `relationships.json` is a claim that a relationship exists, not proof that the target has been properly defined.

> **Stability comes before scale.** Once the repository can reliably index, validate, route and render what already exists, adding thousands more records becomes an expansion problem instead of a debugging lottery.

## Main project layers

- `data/nodes.json` — core node registry.
- `data/relationships.json` — relationship registry.
- `data/repository-index.json` — generated repository-wide record index.
- `data/blueprint-registry.json` — blueprint and data-layer ownership registry.
- `data/blueprints/` — reusable ontology/data-acquisition specifications.
- `data/entanglement.json` — coupling, topology and trajectory.
- `data/axis-topology.json` — symbolic Axis terrain.
- `data/hawkins-scale.json` — comparative emotion layer with evidence safeguards.
- `data/research.json` — sourced facts and research queue.
- `data/frame.json` — canonical architecture and data policy.
- `docs/TIM-DOOLEY-CANON.md` — expanded Tim Dooley / Potatoism / Great Book knowledge base.
- `docs/UNFOLDING-ARCHITECTURE.md` — detailed symbolic and real-world structure.
- `docs/KINGDOM-ATLAS.md` — relationship ontology for the wider world.
- `docs/NORTH-PROGRAMME.md` — North Programme framework.
- `docs/ECONOMIC-GRAPH.md` — European Economic Graph methodology.
- `docs/DOOR-MANDORLA-VESICA-PISCIS-ATLAS.md` — Door/Vesica geometry.
- `docs/CHRISTIANITY-ATLAS.md` — Christianity comparison layer.
- `docs/CHRONOLOGY.md` — project chronology.
- `docs/EVIDENCE-AND-PROVENANCE.md` — evidence discipline.
- `TODO.md` — current engineering, data and research queue.

## Reliability and testing

The repository uses build-time and CI checks for JSON validity, architecture, content integrity, atlas links, backend coverage, web structure, the standardized site shell and the generated repository index. The whole-project stability audit additionally checks source asset references and syntax where the runtime provides the relevant tools.

The deployment rule is simple: **a change is not finished because the code committed. It is finished when the source validates, the static artifact builds, the Pages workflow succeeds and the changed behavior has been checked.**

## The rule

**Relationships first. Entanglement second. Evidence always.**

The purpose of the archive is not to accumulate disconnected pages. It is to make the world's structures readable: who or what exists, what it is connected to, how that connection works, when it existed, what evidence supports it, and what remains unknown.
