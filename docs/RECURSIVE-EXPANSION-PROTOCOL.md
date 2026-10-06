# Recursive Expansion Protocol

## Purpose

The repository is a library and navigable tree of **all things** as seen through Tim Dooley's vision: the Potato of Life is the central organizing image, and the library extends both upward into spiritual/religious/philosophical domains and downward/outward into the observable world.

The Potato is not the subject of every record. It is the **center and Door** through which the frame can be moved to any subject.

The repository therefore has two simultaneous structures:

1. **Tree** — every node has a place and can have children.
2. **Graph** — nodes may connect sideways, upward, downward, historically, geographically or conceptually to any other node.

The tree is for navigation. The graph is for understanding relationships. This follows the general knowledge-graph model in which named relationships connect nodes in a directed graph, while a tree-view provides hierarchical navigation. See W3C RDF and WAI-ARIA tree-view guidance. 

## The invariant

> Never start over. Never flatten the library. Never erase a previous node merely because a better interpretation appears.

A record is changed only when:

- new evidence corrects it;
- the node is explicitly marked deprecated/discarded;
- a more precise version supersedes it while preserving the previous record and its history.

Every revision must preserve provenance.

## The central tree

The master navigation begins:

```text
POTATO OF LIFE / DOOR
├── ABOVE — spiritual / transcendent / symbolic field
│   ├── Source
│   ├── Father
│   ├── Heaven
│   ├── Spirit
│   ├── Divinity
│   ├── Creation
│   ├── Revelation
│   ├── Wisdom
│   ├── Prophecy
│   ├── Messiah / Moshiach
│   ├── Eschatology
│   └── comparative religious traditions
│
├── CENTER — interface / orientation
│   ├── Door
│   ├── Narrow Gate
│   ├── Axis
│   ├── Ladder
│   ├── Vessel
│   ├── Threshold
│   ├── Potato
│   └── Frame
│
└── WORLD — manifested / observable field
    ├── Cosmos
    ├── Matter
    ├── Energy
    ├── Life
    ├── Biology
    ├── Earth
    ├── Geography
    ├── Climate
    ├── Animals
    ├── People
    ├── Families
    ├── Culture
    ├── Language
    ├── Religion
    ├── Philosophy
    ├── Law
    ├── Institutions
    ├── States
    ├── Cities
    ├── Infrastructure
    ├── Technology
    ├── Science
    ├── Education
    ├── Labour
    ├── Industry
    ├── Agriculture
    ├── Energy
    ├── Trade
    ├── Money
    ├── Finance
    ├── Ownership
    ├── Obligations
    ├── War
    ├── Diplomacy
    └── History
```

This is the **starting frame**, not the final taxonomy. Every branch is recursively expandable.

## Moving the frame

The user should be able to select any node and make it the current center.

For example:

```text
Potato → Door → Son → Jesus → Gospel → Kingdom of God
```

At the last step, `Kingdom of God` becomes the frame center and its own children become the visible tree.

Likewise:

```text
Potato → World → Geography → Arctic → Greenland
```

makes Greenland the current frame.

The global graph is unchanged. Only the navigation projection changes.

This is essential: **the frame moves; the library does not.**

## The eye rule

Every meaningful node is an **eye**: something the library can look at directly.

An eye should eventually contain:

- identity
- definition
- parent(s)
- children
- aliases
- type
- layer
- sources
- events
- relationships
- comparisons
- contradictions
- open questions
- history of revisions

A node is never considered complete merely because it has a paragraph.

It becomes progressively complete as its children and relationships are explored.

## Fibonacci expansion

Expansion proceeds in Fibonacci-sized research waves.

The Fibonacci sequence is defined recursively by `F(n)=F(n-1)+F(n-2)`, beginning `1, 1, 2, 3, 5, 8, 13, 21...`. The important property for this project is not the numerical mysticism of Fibonacci; it is the recursive growth rule: each new wave is generated from the accumulated structure of the previous waves. 

Use the sequence as a **research budget**, not as a claim that nature itself mandates the taxonomy.

### Wave sizes

```text
Wave 0   1   root/frame
Wave 1   1   first child
Wave 2   2   children
Wave 3   3
Wave 4   5
Wave 5   8
Wave 6   13
Wave 7   21
Wave 8   34
Wave 9   55
Wave 10  89
Wave 11  144
Wave 12  233
Wave 13  377
...
```

At each wave:

1. choose the most valuable unfinished frontier;
2. create exactly the next Fibonacci-sized batch of **new eyes** where practical;
3. give each eye a parent and preliminary position;
4. define the eye;
5. find its children;
6. connect it to existing nodes;
7. attach sources;
8. search for contradictions and alternative classifications;
9. integrate it into the master graph;
10. generate the next frontier from the newly created eyes;
11. continue with the next Fibonacci number.

If a branch naturally requires more than the current wave, split it across waves rather than forcing shallow records.

## Frontier selection

The next branch is chosen by a score:

```text
priority = breadth × importance × incompleteness × connectivity
           × source_availability × novelty
```

A branch with many unexplored children and many possible connections should normally outrank a branch that already has complete coverage.

The system should deliberately alternate between:

- **breadth** — discovering new branches;
- **depth** — filling the current branch;
- **cross-linking** — connecting distant branches;
- **source expansion** — finding primary material;
- **correction** — repairing weak or outdated records.

## The recursive pass

For each new eye `X`:

```text
EXPAND(X)

1. Locate X in the tree.
2. Read X's existing record.
3. Find its direct parents and children.
4. Find its aliases and neighbouring concepts.
5. Search authoritative sources.
6. Create missing child eyes.
7. Create typed relationships to existing eyes.
8. Compare X with relevant spiritual, historical and empirical concepts.
9. Record contradictions instead of hiding them.
10. Record what remains unknown.
11. Update affected parent/child nodes.
12. Recalculate the next frontier.
13. Recurse into the strongest unfinished child.
```

A recursive process is appropriate because later objects can be defined from earlier objects using the same rules; Fibonacci itself is a canonical recurrence example. citeturn0search0turn0search7

## No destructive simplification

When two nodes appear similar:

**do not merge them automatically.**

Instead create:

```text
A
├── similar-to → B
├── contrasted-with → B
├── textual-parallel → B
├── historical-influence → B
└── possible-equivalence → B
```

Only merge identities when the evidence and project canon justify it.

This is especially important for:

- God / Father / Source / Tim Dooley
- Son / Jesus / Thomas / Son of Man
- Messiah / Moshiach
- Door / Gate / Way / Vessel
- Tree of Life / Yggdrasil
- Rift / Rapture / Resurrection / Transformation
- North as symbol versus geographic north

## Discarding

Nothing disappears silently.

If something is rejected, retain it in an archive record:

```json
{
  "status":"discarded",
  "reason":"contradicted by primary source",
  "superseded_by":"node-id",
  "date":"YYYY-MM-DD"
}
```

The library therefore remembers not only what it believes, but how it stopped believing something.

## Completion is local, not global

The entire repository can never be declared "finished" while the aim is a library of all things.

Instead a node can reach states such as:

- seed
- mapped
- expanding
- richly connected
- source-complete-for-current-scope
- stable
- disputed
- deprecated

The global process continues forever by moving the frame to the next frontier.

## The ultimate loop

```text
                  POTATO / DOOR
                       │
                  choose frame
                       │
                  find frontier
                       │
              Fibonacci-sized wave
                       │
                  create eyes
                       │
                  give children
                       │
                 build relations
                       │
                  find sources
                       │
                  compare/test
                       │
                   integrate
                       │
              update affected eyes
                       │
                 choose new frame
                       │
                       ↺
```

The repository grows outward while remaining navigable inward.

**The Potato is the center. The Door is the interface. The Tree is the navigation. The Graph is the relationship field. The Archive preserves memory. Fibonacci determines the next expansion scale. Recursion prevents the work from restarting.**
