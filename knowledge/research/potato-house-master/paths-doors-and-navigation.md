# Potato House — Paths, Doors and Navigation

**Status:** research design; non-canonical.

Movement through the House needs separate semantics even when several movements are rendered as ordinary links.

## Core traversal types

### Road
A typed semantic relation between existing things. It answers **why are these connected?** A Road does not imply state change.

Examples: part-of, member-of, owns, depends-on, supplies, influences, compares-with, supports, contradicts, located-in.

### Path
An ordered sequence selected for a task. A Path may combine Roads, North steps, context changes, Views and Doors. Most Paths can be generated temporarily.

### Door
A guarded state/context transition. It answers **what changes if this threshold is crossed?**

Examples: research→canonical, internal→public, draft→released, unresolved→reviewed, legacy-schema→replacement.

A hyperlink may expose a Door, but hyperlinks are not automatically Doors.

### Ladder
An ordered sequence of meaningful Doors/thresholds where order matters.

### North step
A selected orientation move toward broader integration/criterion in a declared context. It is not the only broader relation and never implies truth rank.

### Root trace
Traversal toward provenance, cause, support, memory, obligation, substrate or residue. Root traces can branch.

### Tree branch
Traversal toward descendants, applications, specialized forms, examples or generated outputs.

### Context switch
Same stable identity, different Room/lens/jurisdiction/time/translation/audience.

### View switch
Same canonical material, different representation: reader, map, graph, timeline, table, diagram, dossier.

## One primary way up, many ways down/out

The recurring project intuition should become a UI rule rather than ontology:

- expose one primary North action when useful;
- permit many downward/deeper/generative paths;
- keep other broader contexts explicit;
- allow many provenance roots;
- allow many lateral Roads.

```text
             primary North
                  ↑
             current thing
       ↙          ↓          ↘
   branches     detail      contexts
      ↓           ↓           ↔
     many        many         many

  roots/provenance can also branch below
```

## Breadcrumb law

Breadcrumbs represent the current route/context, not a single true taxonomy.

`Science → Neuroscience → Thalamus`

and

`Potato of Life → Body comparison → Thalamus`

may reach the same stable subject.

Do not duplicate identities merely to obtain different breadcrumbs.

## Stable subject-page compass

A normal subject surface should repeatedly expose:

1. **Orientation** — current context and primary North route.
2. **Understand** — current synthesis.
3. **Connected** — important typed Roads.
4. **Inside / Branches** — parts, descendants, applications.
5. **History** — Occurrences/state changes.
6. **Roots / Evidence** — provenance, sources, dependencies.
7. **Other contexts** — Room/lens switches.
8. **Deeper** — specialist material/Artifacts.

Room-specific renderers may rearrange the interior, but repeated navigation order should remain predictable.

## Important Path classes

- **Orientation Path:** subject → North → broader synthesis → criteria.
- **Evidence Path:** public statement → Assertion → Activity → Artifact/source.
- **History Path:** current state → earlier states/Occurrences.
- **Composition Path:** part → system → larger system.
- **Decomposition Path:** system → components.
- **Generative Path:** Seed/synthesis → branches → Fruit.
- **Research Path:** question → sources → candidate assertions → testing → promotion/rejection.
- **Repair Path:** failure → diagnosis → containment → repair → validated replacement → compatibility retirement.
- **Programme Path:** mission → workstreams → Room inputs → analyses → outputs.

These are generated traversals, not permanent duplicate page trees.

## Search/question routing

Search is a temporary corridor through permanent Rooms.

`question → classify intent → locate Rooms/primitives → retrieve → synthesize View → preserve routes to owners/sources`

Search never decides canonical ownership.

Repeated high-value questions may become Guides/Views, not duplicate Subjects.

## Door contract

A future Door schema should capture:

- affected subjects;
- source state/context;
- guard/preconditions;
- trigger;
- transition Activity;
- destination state/context;
- preserved invariants;
- generated provenance;
- reversibility;
- rollback/return;
- time/evidence.

## Navigation hygiene

Permanent site rules:

- links navigate; buttons change state/perform actions;
- essential meaning never requires hover or dragging;
- repeated navigation stays in predictable relative order;
- major pages have multiple discovery methods;
- focus order preserves meaning;
- changing focus/input does not unexpectedly change context;
- no surprise zoom, scroll or major layout jumps;
- semantic HTML carries core navigation before JS enhancement.

These rules match the House principle: orientation should be stable even when Views are adaptive.

## Path health

A healthy traversal makes these answerable:

- Where am I?
- What did I traverse?
- Why is this destination connected?
- Did state/context change?
- Can I return?
- What evidence supports the relation/transition?

Navigation becomes Swamp-like when routes loop without orientation, depend on hidden state, remove exits, or create competing URLs/owners for the same identity.
