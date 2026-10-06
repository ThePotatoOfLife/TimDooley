# Potato House Wave 6 Homepage Editorial Refinement Design

Status: approved architectural direction; written-spec review gate

## Goal

Wave 6 stabilizes and lightly refines the homepage after the House, projections, readiness, Hub convergence, Explore, and specialist Views have clear contracts.

This is the most conservative wave in the programme.

The homepage already has the correct high-level structure. Wave 6 therefore protects the current reader experience while making its destinations, machine discovery, and deployment artifact agree with House authority.

The governing rule is:

> The House may make Home more reliable, but it must not make Home more complicated.

## Current protected baseline

The homepage currently contains:

1. project identity / hero;
2. concise project-purpose statement;
3. concise evidence boundary;
4. exactly five primary gateway rows:
   - Tim Dooley;
   - Religion;
   - Philosophy;
   - Science;
   - World;
5. short question-led previews for those gateways;
6. a small secondary editorial row;
7. quiet footer access to Sources and Explore;
8. semantic static HTML that works without JavaScript.

That structure is the baseline to preserve.

Wave 6 does not redesign Home merely because the backend has become more sophisticated.

## Chosen approach

Use a protected, hand-authored editorial homepage whose destinations and machine metadata are validated or derived from House contracts.

Rejected alternatives:

- freeze Home completely: visually safe but leaves route/discovery duplication unmanaged;
- generate Home from the House: architecturally neat but would turn an editorial threshold into a database view;
- make readiness or graph centrality choose Home content automatically: confuses operational metadata with editorial judgment.

The homepage remains human-authored semantic HTML.

## Authority boundary

The House owns:

- the five primary public Hub IDs;
- their canonical routes;
- their canonical order;
- public-surface type and parent relationships;
- whether secondary destinations resolve;
- machine/discovery route identity;
- publication/readiness information used as editorial input.

The homepage owns:

- wording;
- visual hierarchy;
- question previews;
- amount of information shown;
- optional Start-here editorial choices;
- secondary editorial emphasis;
- whether a valid route deserves homepage prominence.

House authority does not automatically imply homepage visibility.

## Canonical five-door contract

The primary homepage gateway order is fixed by public-surface authority:

```text
tim
religion
philosophy
science
world
```

with canonical routes:

```text
/tim-dooley/
/religion/
/philosophy/
/science/
/world/
```

World is the fifth Hub. World Map remains a specialist View under World.

Homepage source HTML may remain static, but validation must prove its five gateway destinations match the House registry exactly.

A late build or patch step must not silently substitute a specialist route such as `/world-map/` for `/world/`.

## Primary gateway semantics

Each primary gateway should remain a normal reader choice rather than an exposed ontology label.

The current pattern is good:

- domain name;
- one short purpose statement;
- one or two natural-language questions.

Examples of the intended style:

- `Who is Tim Dooley?`
- `What changed over time?`
- `What is Potatoism?`
- `How does it relate to other religions?`
- `What makes a claim true?`
- `Can these ideas be formalized?`
- `What can actually be tested?`
- `How is the world connected?`

Do not replace this with Room IDs, branch names, lifecycle states, or backend terminology.

## Evidence boundary

The homepage evidence boundary should remain short.

Its job is to tell a first-time reader that project self-description, autobiography, comparative interpretation, scientific/historical evidence and external documentation are not one undifferentiated evidence layer.

Detailed source hierarchy, contradiction method, provenance rules and epistemic classes belong deeper in the site.

Home must not become the archive methodology manual.

## Secondary editorial links

The current `Other threads` row is treated as editorial discovery, not primary taxonomy.

Secondary links may include topics such as culture/subculture, symbols, technology, society or economics when they are useful.

Rules:

- secondary editorial links do not redefine the five-Hub architecture;
- they must resolve to valid public destinations;
- they may change over time without changing House ontology;
- they remain visually subordinate to the five primary gateways;
- a larger backend domain does not automatically deserve a Home link.

Wave 6 does not remove the current secondary row merely for conceptual neatness.

## Global secondary surfaces

The House recognizes important global secondary surfaces such as:

- Timeline;
- Explore;
- Sources.

Global validity does not require equal homepage prominence.

Explore and Sources may remain quiet footer/utility routes.

Timeline may remain primarily reached through Tim unless later editorial evidence shows that placing it directly on Home helps first-time readers.

Rule:

> A globally valid route is not automatically a primary homepage route.

## Optional Start-here paths

A small `Start here` area is allowed but not required.

Do not add one merely because the architecture permits it.

If it proves useful, keep it intentionally small and question-led, for example:

- Who is Tim Dooley?
- What is the Potato of Life?
- How is the world connected?

A Start-here item must:

- resolve to a stable public destination;
- be appropriate for first-time readers;
- be sufficiently mature/public-ready;
- be intentionally selected by editorial judgment.

Wave 3 readiness may inform eligibility. It may not select homepage prominence automatically.

## Editorial selection law

Homepage prominence must never be determined solely by:

- graph degree;
- record count;
- file size;
- recency of commit;
- number of Rooms touched;
- inference score;
- readiness score;
- research priority;
- symbolic centrality inside project canon;
- technical complexity.

These signals can inform editorial review, but the homepage criterion is simpler:

> Does this help a first-time visitor understand the project and choose a useful next step?

## No generated homepage content from Gardener queues

Wave 3 Gardener output must not directly render:

- maturity meters;
- stale-item warnings;
- research queues;
- "most ready" cards;
- "most connected" cards;
- automatic featured items;
- truth/confidence scores.

A Gardener recommendation may trigger human review of Home. It cannot mutate Home.

## Machine discovery convergence

Current machine/discovery systems already mirror the five-door public architecture.

Wave 6 should move them toward shared route authority so `scripts/build_discovery.py` and related SEO/discovery code do not permanently maintain an independent five-door list.

Preferred direction after Wave 1 is implemented:

```text
public-surfaces.json
        ↓
canonical five-door resolver
        ↓
Home validation
build_discovery.py
llms.txt / discovery.json
question pages
site-index / sitemap metadata
JSON-LD or equivalent machine metadata
```

The exact consumer migration can be staged.

Do not create a new homepage registry when public-surface authority already exists.

## Discovery relationship to visible Home

Machine discovery may expose much more depth than Home.

That is expected.

The visible Home is an editorial threshold.

Machine indexes may contain:

- question pages;
- A-Z routes;
- sitemap coverage;
- canonical entities;
- machine-readable public-surface IDs;
- deep research discovery routes.

Those outputs must still agree with the five canonical public Hubs rather than invent a parallel top-level architecture.

## JSON-LD / metadata policy

Homepage structured metadata may be enriched when it improves machine understanding, but it must consume or validate against existing surface/identity authority.

Do not duplicate canonical identity facts solely inside inline JSON-LD.

Metadata convergence should be quiet: richer machine semantics without more visible homepage clutter.

## Protected visual signature

Wave 6 protects semantic/visual identity rather than exact pixels.

The homepage should remain recognizably the current page family:

- dark, restrained presentation;
- large `POTATO OF LIFE` identity;
- short explanatory introduction;
- five spacious primary gateway rows;
- natural-language question cues;
- small subordinate discovery links;
- readable responsive collapse on narrow screens.

Do not use Wave 6 to add:

- a giant graph;
- Room cards;
- lifecycle badges;
- ontology diagrams;
- D1–D11 controls;
- animated relationship maps;
- dozens of topic cards;
- an archive file tree;
- automatic activity feeds;
- backend status dashboards.

Any substantial homepage redesign requires a separate explicit design approval.

## Semantic non-regression contract

Prefer contract assertions over full HTML snapshots.

Validate at least:

- exactly one homepage reader surface;
- exactly five primary gateway rows;
- exact primary gateway IDs/routes/order;
- World is fifth;
- World Map is not a primary gateway;
- one concise project-purpose block exists;
- one concise evidence-boundary block exists;
- gateway descriptions/questions remain present;
- secondary links are visually/structurally subordinate;
- Explore and Sources remain reachable;
- no backend schema/Room/file-path terminology leaks into the five primary labels;
- mobile markup remains semantically valid;
- no JavaScript is required for core gateway navigation.

Do not freeze every sentence, whitespace choice or CSS declaration.

## Exact-artifact verification

Wave 6 must validate the final deployable artifact, not only `index.html` in the source tree.

The repository build pipeline includes discovery, SEO, public ontology/patching and other post-build operations.

Final verification should therefore prove on the exact `_site/index.html` produced by the complete build sequence:

- five primary gateways remain present;
- their canonical routes remain correct;
- World remains `/world/`;
- no later patch inserts a competing top-level route;
- machine metadata and visible route semantics agree;
- source and deploy artifact preserve the same homepage architecture.

Validators must never mutate the artifact into compliance.

## Build/discovery failure behavior

- public-surface registry unavailable when required: fail architecture validation;
- visible Home route differs from canonical primary route: fail;
- discovery layer route differs from canonical primary route: fail;
- optional secondary editorial route missing: report/fail according to its declared status rather than guessing a replacement;
- readiness unavailable: keep Home unchanged;
- machine index generation unavailable: preserve static Home and fail/report through its existing discovery contract;
- late build patch changes the five-door contract: fail exact-artifact verification.

No fallback may guess a replacement primary Hub.

## Relationship to Waves 1–5

Wave 1 determines stable public-surface identities and canonical routes.

Wave 2 determines safe contextual/public projection relations.

Wave 3 determines maturity/readiness as internal editorial input.

Wave 4 converges the five Hubs onto shared House semantics while protecting their page identities.

Wave 5 makes Explore and specialist Views share canonical identity safely.

Wave 6 exposes only the small amount of that architecture a first-time visitor actually needs.

## Continuous Gardener loop after Wave 6

After Wave 6, growth should follow a continuous cycle rather than another wholesale architecture rewrite:

```text
capture
→ provenance
→ identity / owner
→ normalize
→ relate
→ synthesize
→ readiness
→ public projection
→ editorial review
→ publish / feature where appropriate
→ validate
→ prune or archive duplicate presentation
→ repeat
```

Homepage review is one editorial checkpoint inside this loop, not the destination of all knowledge.

## Non-goals

Wave 6 does not:

- redesign the homepage;
- generate Home from backend records;
- expose Rooms on Home;
- expose Gardener queues on Home;
- expose readiness/truth scores;
- make Timeline a primary gateway automatically;
- make Explore a primary gateway;
- add more than five primary Hubs;
- remove secondary editorial links merely for taxonomy purity;
- select featured material from graph metrics automatically;
- make JavaScript necessary for primary navigation;
- replace question-led labels with schema language;
- duplicate public-surface authority in a new registry;
- trust the source tree without checking the final deploy artifact.

## Success criteria

Wave 6 succeeds when:

1. the homepage remains visually and structurally close to the current successful baseline;
2. exactly five primary gateways remain Tim, Religion, Philosophy, Science and World;
3. visible Home routes agree with public-surface authority;
4. machine discovery consumes or validates against the same route authority;
5. World cannot drift back to World Map as the fifth primary door;
6. question-led human descriptions remain intact;
7. secondary routes remain subordinate and do not redefine taxonomy;
8. optional Start-here paths, if used, are manually curated and public-ready;
9. readiness informs editorial review without rendering itself;
10. machine metadata can grow richer without visual clutter;
11. static HTML remains fully usable without JavaScript;
12. final `_site` verification proves deployment preserves the same architecture;
13. later knowledge growth does not require repeated homepage redesign;
14. the full six-wave architecture can enter a continuous Gardener cycle.

## Invariants

1. The homepage is an editorial threshold, not a visualization of the House.
2. Five primary gateways remain exactly five.
3. World is the fifth Hub; World Map is a specialist View.
4. House authority governs destination identity, not editorial wording.
5. Editorial prominence remains human-governed.
6. Readiness is advisory, not a homepage renderer.
7. Graph centrality is not homepage importance.
8. Machine discovery may be deep; visible Home stays simple.
9. Question-led language outranks backend terminology for first-time readers.
10. Secondary links do not become primary taxonomy accidentally.
11. Start-here is optional and intentionally curated.
12. Static semantic HTML is the primary substrate.
13. Source and deployed homepage architecture must agree.
14. Backend sophistication should reduce, not increase, public cognitive load.
15. The protected current design may evolve only through explicit editorial/design decisions, not as a side effect of backend convergence.
