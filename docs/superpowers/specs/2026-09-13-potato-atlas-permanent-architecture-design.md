# Potato Atlas Permanent Architecture

## Status
Approved architecture for the next-generation repository and website.

## Goal
Create one durable information architecture that scales without repeated taxonomy rewrites, duplicate canonical owners, route churn, or presentation-specific copies of knowledge.

## Core model
The permanent model has four object types:

1. **Node** — one current canonical subject.
2. **Relation** — a typed connection between subjects.
3. **Artifact** — preserved source, history, research, version, conversation, work, observation, or other provenance-bearing material.
4. **View** — a generated or curated way to present Nodes and Artifacts without owning them.

Conceptually: `G = T_N + E_R + E_A`, where `T_N` is the North spine, `E_R` is the typed relation graph, and `E_A` is Archive/provenance depth.

## One North Axis
Every active Atlas Node except the root has exactly one `north_parent`. The root has none. Following `north_parent` must always terminate at the root and must never cycle.

This does not mean a Node has only one relationship. It means there is exactly one canonical answer to: **what is the next broader structural context?**

Read upward, the same structure is Mountain: many-to-one integration. Read downward, it is Tree: one-to-many differentiation. Do not maintain separate Mountain and Tree hierarchies.

A page may expose many links, but only one link is the canonical North Gate.

## Atlas / Plane
The Atlas is the current knowledge Plane. It contains durable subjects such as people, concepts, places, systems, events, works, organisms, institutions, models, texts, equations, countries, communities, and other substantial identifiable subjects.

Each active Node has:
- one stable ID;
- one canonical owner;
- one canonical public URL;
- one `north_parent` unless it is root;
- zero or more typed relations;
- zero or more Archive references;
- explicit epistemic/provenance metadata.

Physical repository folders do not define the public ontology.

## Archive / depth
Archive is first-class content. It preserves primary sources, dated conversations, historical states, timelines, research notes, evidence, comparative sources, superseded interpretations, original works, datasets, collections, provenance, and authorship.

Archive is not dead storage: archived material may later alter current Atlas understanding and be promoted after review.

Keep two downward families distinct:
- **structural descent**: contains, part-of, example-of, subsystem/component relationships;
- **provenance descent**: history, source, evidence, research, version, documents, attests.

## Swamp as repository-health condition
Swamp is not a directory. It is a diagnostic state signaled by duplicate canonical owners, orphans, unresolved relation endpoints, missing provenance, untyped contradictions, unclassified research waves, duplicate public ownership, circular North ancestry, dead Archive material, route conflicts, or CSS/layout ownership conflicts.

Swamp belongs in audits and CI.

## Biological design constraints
Use real potato biology only as a structural comparator, never as proof of project metaphysics.

Useful distinctions:
- tuber is a modified underground stem, not a root;
- eyes are bud/meristem sites;
- dormancy preserves organized potential;
- apical dominance can coexist with distributed viable eyes;
- tuber can change from storage sink to growth source;
- stolons form a transport network;
- clonal continuity can preserve both capacity and disease burden.

Repository translation: provenance/context supports current knowledge; canonical synthesis compresses; entry points expose viable growth; reader projections expand; Archive memory may become future source; inherited errors require deliberate cleanup.

## Rooms and Views
Science, Religion, Philosophy, World, Politics, Life & Body, History, Works, Economics, and future domains are Views/Rooms, not canonical ownership containers.

A Node may appear in unlimited Views without duplication. A View may change, merge, split, or disappear without changing Node identity or canonical URL.

## Permanent routes
Target route model:
- `/` — current summit/orientation;
- `/atlas/` — current knowledge Plane;
- `/atlas/<id>/` — canonical Node;
- `/archive/` — Archive landing;
- `/archive/<artifact-id>/` — public Artifact where appropriate;
- named domain routes or `/path/<id>/` — Views.

Canonical Node URLs must not encode mutable taxonomy. Existing public URLs remain compatible during migration.

## Universal page grammar
Every canonical Node page must make four questions easy to answer without search:
1. What is this?
2. What is one level broader?
3. What is around or inside this?
4. Where did this understanding come from?

Semantic page order:
1. North Gate / broader context.
2. Page identity and summary.
3. Human-readable primary content.
4. Typed lateral relations/comparisons.
5. Structural children/components.
6. Archive depth: History, Sources, Research, Versions/Collections as applicable.

Breadcrumbs show canonical North ancestry. The View used to arrive may be shown separately as context.

## Reader adapters
Use one page shell but different content adapters by Node kind. Examples:
- person: biography, roles, timeline, relationships, evidence;
- country: geography, institutions, economy, systems, map, sources;
- equation/model: expression, variables, assumptions, lineage, tests, sources;
- biological structure: anatomy/function, diagram, components, science sources, separately labeled comparisons;
- event: chronology, actors, causes/consequences, sources;
- work: artifact, creator, date, context, relationships;
- institution/company: identity, ownership/control, function, assets/obligations, relationships, evidence.

Do not make raw JSON field names the final human page structure.

## Representation rule
Use the representation suited to the question: map for place, graph for relationship, timeline for sequence, diagram for structure, dossier for claims/evidence, reader for prose, table for comparison, specialist tool only when it adds real capability.

## Web platform rules
- Static semantic HTML owns meaning and core navigation.
- JavaScript progressively enhances filtering, maps, timelines, comparisons, and graph exploration.
- One semantic page shell across generated and hand-written surfaces.
- One design system; remove independent embedded page-shell CSS over time.
- Keep explicit CSS ownership. Do not create new global structural `.nav`, `.grid`, `.section`, `.card`, `.record`, or `.status` rules.
- Use layered CSS ownership such as `reset, legacy, base, shell, components, modules, utilities`.
- Keep current accessibility strengths: skip link, semantic landmarks, visible focus, keyboard operation, reduced-motion support, generous targets.
- Routine clicks must not unexpectedly zoom, refocus, scroll, steal focus, or resize major layout regions. Explicit Focus/Locate/Zoom actions may do so.
- Prefer stable layout, responsive components, and dimensioned assets.

## Build / validation separation
Builders produce artifacts. Validators inspect and pass/fail. Validators must not mutate source or `_site` to repair the thing they are testing.

## Registry architecture
The new Atlas registry must cover explicit canonical owners across both `knowledge/` and `data/`, while respecting source-of-truth mappings. It must not promote every nested JSON object automatically.

Promotion requires durable subject identity and canonical ownership.

## North invariants
The Atlas validator must eventually enforce:
1. exactly one active root;
2. every active non-root Node has one `north_parent`;
3. each parent resolves;
4. every North chain reaches root;
5. no North cycles;
6. children are derived from parent references;
7. canonical IDs are unique;
8. canonical URLs are unique;
9. important relation endpoints resolve or are explicitly unresolved/research;
10. every canonical owner has provenance/source path.

During migration, Nodes may be `active`, `candidate`, `legacy`, or `archive_only`.

## Epistemic firewall
Preserve these distinctions:
- project canon/self-description != independently verified empirical fact;
- analogy != identity;
- comparison != historical transmission;
- symbolic mapping != literal anatomy or physics;
- scientific comparator != proof of metaphysical claim;
- disputed/inferential claims remain typed;
- empirical financial/legal quantities are never merged numerically with symbolic quantities.

Navigation altitude never overrides epistemic class.

## Deprecation policy
The overhaul is architecture-radical but knowledge-conservative.

Use: `inspect -> classify -> normalize -> connect -> promote -> redirect -> verify -> deprecate -> prune`.

Do not delete unique wording, provenance, authorship, dated contradiction, original creative material, or source evidence merely because a synthesis exists elsewhere.

## Migration phases
0. Baseline current main and quality gates.
1. Add this constitution, machine-readable contract, initial schemas, and validators.
2. Build normalized Atlas registry without moving owners.
3. Curate root + `north_parent` for high-value active Nodes, then expand.
4. Introduce one design system and shared semantic shell.
5. Generate `/atlas/<id>/` pages with reader adapters.
6. Generate `/` summit and retire five-door ownership assumptions while preserving compatibility.
7. Unify Archive Views: History, Sources, Research, Collections.
8. Convert domain surfaces into Views over Atlas.
9. Gradually consolidate physical owners only where useful.
10. Deprecate and prune obsolete manifests, duplicate shells, compatibility hacks, and fully absorbed duplicate masters after audits pass.

## Permanent success criterion
A reader can land on any substantial canonical page and immediately understand what it is, what is broader, what it contains/connects to, and where the understanding came from. Corpus size may grow dramatically while orientation cost remains approximately constant.
