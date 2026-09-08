# Root Navigation Architecture

Status: active architectural specification
Date: 2026-09-08

## Purpose

The front page is the coordinate system of The Potato of Life, not a conventional homepage and not a search screen.

The visitor enters at the center. The center is represented as the North Pole / root position. From that fixed position the corpus unfolds in place.

The interface must therefore provide enormous access without repeatedly moving the visitor between pages.

## Fundamental structure

```text
ROOT
  |
  v
POTATO OF LIFE
  |
  +----------------+
  |                |
 WORLD            AXIS
  |                |
 THINGS           STRUCTURE
```

This is the only top-level information architecture exposed to the visitor.

Core material is represented at the center:

```text
POTATO OF LIFE
  +-- TIM DOOLEY
  +-- POTATOISM
  +-- THOUGHT
  +-- CANON
  +-- WORLD/
  +-- AXIS/
```

There is no top-level `CORE/` directory and no top-level `TEXTS/` directory.

Texts are World objects. A Bible, Edda, book, paper or document belongs to the relevant World context while retaining its own canonical identity.

## Ontological rule

At the highest level:

- **WORLD = things, events, places, people, institutions, texts and observable corpus material.**
- **AXIS = structures, orientations, symbolic models, geometry, relations and organizing interpretations.**

This is a navigation distinction, not a claim that every concept has only one possible interpretation.

A canonical node exists once. A node may appear through multiple directory paths without being duplicated.

```text
many paths ---> ONE NODE
```

## Backend versus presentation

The existing repository taxonomy is deliberately preserved underneath the new interface. `Spirit -> Mind -> Matter` remains a filing/classification coordinate used by audits and source data; it is not exposed as the homepage's primary tree.

The center interface adds a **presentation projection**:

```text
repository-index.json
        |
        v
build_root_navigation_index.py
        |
        v
root-record-index.json
        |
        v
WORLD / AXIS tree
```

This is important: World/Axis is a view over the corpus, not a destructive replacement of the existing backend taxonomy.

A record therefore retains its original backend classification while receiving a generated `navigation_path` for presentation.

## Center invariant

The visitor does not travel through the website as a game.

The visitor remains at the center and reveals structure.

Opening a directory must not require a full-page navigation.

Opening a record should reveal its dossier in place while leaving the tree available.

## Interface model

The front page has four simultaneous layers:

1. **Orientation** — North Pole / center / current path.
2. **Tree** — expandable directories and records.
3. **Dossier** — selected record content shown in place.
4. **State** — expanded nodes, selected node, scroll position and URL state.

The browser URL may encode the selected path, but changing that state must not require abandoning the center interface.

## Directory rules

Directories are views over the corpus. They are not duplicate databases.

A directory may contain:

- another directory;
- a canonical node reference;
- a document reference;
- a view over a record family;
- a generated collection.

A directory must never create a second identity for an existing node merely because the node appears in another context.

## Record rules

Every important subject should resolve to one canonical identity.

A record may carry:

- identity and aliases;
- description;
- type;
- chronology;
- sources;
- evidence;
- relationships;
- interpretations;
- project-canon material where applicable;
- uncertainty and unknowns.

The interface must preserve distinctions between evidence, interpretation, comparison, speculation and project canon.

## Relationship rules

Edges are typed. A generic `A -> B` edge is insufficient for important relationships.

Examples:

```text
located_in
member_of
owned_by
controlled_by
mentions
influenced
historically_precedes
symbolically_corresponds_to
evidence_for
```

A graph edge is not a dossier and is not proof of causation.

## Progressive disclosure

The entire repository must be accessible, but the entire repository must not be rendered into the initial DOM.

The front page initially exposes only the highest-level structure. Expanding a branch renders its children. Large collections are grouped before their individual records are rendered.

Required controls:

- expand;
- collapse;
- collapse all / reset;
- current path;
- selected record;
- return to root without leaving the page.

## State persistence

The interface preserves useful navigation state using URL state and local browser state where appropriate.

At minimum:

- expanded branches;
- selected node;
- current path;
- scroll position where practical.

Reloading the page should not unnecessarily destroy the user's position in the corpus.

## Data source

The navigation is generated from the repository's canonical/generated registries rather than becoming a second manually maintained corpus.

The deployment sequence is now:

```text
canonical record registry
        |
repository index
        |
root navigation index
        |
static site
```

`data/root-navigation.json` contains only stable semantic vocabulary and presentation rules. `data/root-record-index.json` is generated and disposable. It must never become a second identity store.

## Build boundary

The center homepage intentionally has its own shell. The generic site-header transformation must not overwrite `index.html` or its compatibility alias `root.html`.

The center page is therefore a deliberate exception to the generic presentation shell, and its validator checks for the center tree instead of requiring the standard header.

## Non-goals

The root interface is not:

- a search-first interface;
- a conventional marketing homepage;
- a game or quest system;
- a second copy of the repository data;
- a flat list of every record;
- a replacement for deep dossier pages.

## Architectural invariant

```text
ONE CORPUS
MANY PATHS
ONE CANONICAL IDENTITY
MANY VIEWS
ONE CENTER
```

The homepage is the coordinate system from which the corpus is unfolded.