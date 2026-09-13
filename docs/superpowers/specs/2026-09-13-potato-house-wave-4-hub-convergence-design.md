# Potato House Wave 4 Hub Convergence Design

Status: approved architectural direction; written-spec review gate

## Goal

Wave 4 makes the five major public Hubs consume the same House route/projection authority while preserving their distinct editorial voice, visual structure, and specialist function.

The five Hubs are:

- Tim Dooley
- Religion
- Philosophy
- Science
- World

Wave 4 is not a redesign wave.

Its purpose is to make these pages agree about the underlying House without making the pages become each other.

## Governing principle

> Shared authority and shared semantics; protected layout and protected editorial identity.

The House should own what must be consistent:

- stable public-surface identity;
- canonical route;
- peer/public-Hub relationships;
- Room references;
- public projection references;
- canonical machine metadata;
- parent/specialist relationships;
- route compatibility and migration state.

Each Hub continues to own:

- explanatory prose;
- editorial order;
- domain-specific components;
- page-level interaction model;
- local visual rhythm;
- specialist reader experience.

## Chosen approach

Use a shared Hub envelope derived from Waves 1–3 rather than a universal page template.

Rejected alternatives:

- universal Hub template: too destructive and would flatten pages whose different forms are useful;
- validation-only convergence: protects design but leaves too much route and metadata duplication alive;
- new manually maintained super-registry: duplicates authority already established by the House.

The shared Hub envelope should be derived from existing contracts rather than becoming another permanent knowledge owner.

Conceptually:

```text
public-surfaces.json
rooms.json
public-page-projections.json
readiness where relevant
        ↓
shared Hub envelope
        ↓
Tim / Religion / Philosophy / Science / World
```

## Protected public signatures

Wave 4 treats the current five Hubs as protected design signatures.

The implementation may repair route drift, improve machine metadata, and converge repeated structural semantics. It must not broadly rewrite the pages merely to make code generation easier.

### Tim Dooley

Tim remains biographical, developmental, and work-oriented.

Protected characteristics include:

- identity/development questions;
- Timeline/public-record/evidence routes;
- developmental spine;
- work/builder layer;
- Gardener/service framing;
- distinction between project ontology and ordinary personhood/evidence boundaries;
- compact deeper exploration block.

Wave 4 must not turn Tim into a generic topic-card Hub.

### Religion

Religion remains theological and comparative.

Protected characteristics include:

- Potatoist theological center;
- source / manifestation / religious-life distinction;
- Bible comparison laboratory;
- comparative Christianity/Judaism/Islam questions;
- explicit comparison/evidence boundary;
- deeper Traditions routes.

The Bible laboratory must not be reduced to a generic Related block.

### Philosophy

Philosophy remains a reader journey.

Protected characteristics include:

- staged philosophical movements;
- long-form explanatory flow;
- sayings, stories, quotations and reflections;
- sparse `Chew on it` disclosures;
- explicit Religion ownership boundary;
- deep source / long-form philosophy route.

The page must not be flattened into a generic grid of concepts.

### Science

Science remains a research/document library.

Protected characteristics include:

- formal-model / analogy / metaphor / evidence boundaries;
- scientific orientation questions;
- search;
- field and document-type filters;
- crawlable/static science catalog;
- progressive JavaScript enhancement;
- direct access to full documents;
- compact deeper science routes.

The library must not become a generic Hub card renderer.

### World

World remains a gateway into sibling lenses.

Protected characteristics include:

- World as the fifth primary Hub;
- World Map, Politics & Geopolitics, North, and World Systems as sibling lenses;
- no assumption that geography/map is the parent of all world-facing material;
- clear empirical / programme / political / symbolic boundaries;
- ordinary deep routes to archive and sources.

Wave 4 must not make World Map the World landing page again.

## Shared Hub envelope

The minimum derived envelope should be able to answer:

```json
{
  "surface_id": "science",
  "canonical_route": "/science/",
  "surface_type": "hub",
  "primary_room_ids": [],
  "peer_surface_ids": ["tim", "religion", "philosophy", "world"],
  "parent_surface_id": "home",
  "projection_id": "science",
  "specialist_surface_ids": [],
  "compatibility_routes": [],
  "machine_metadata": {}
}
```

The exact generated representation may differ after Waves 1–3 are implemented. The important requirement is that the envelope is derived, replaceable, and not a new canonical fact owner.

## Navigation semantics

Wave 4 separates navigation semantics from navigation presentation.

The House determines:

- which major Hubs exist;
- their canonical routes;
- which Hub is current;
- which public parent/specialist relationships are valid.

Individual pages may determine:

- whether all peer links are shown in the first visible navigation;
- how local navigation is presented;
- whether local specialist routes deserve more prominence than peer Hubs;
- visual treatment and markup form, provided semantic navigation remains accessible.

Therefore convergence does not require identical navigation markup.

## Route authority

Wave 1 public-surface authority controls canonical Hub routes.

Wave 4 must remove or validate manually duplicated Hub-route knowledge where practical.

The target route family is:

- Home `/`
- Tim `/tim-dooley/`
- Religion `/religion/`
- Philosophy `/philosophy/`
- Science `/science/`
- World `/world/`

Specialist links remain valid where context calls for them.

World Map remains `/world-map/` as a specialist View under World.

## Machine metadata convergence

Wave 4 should quietly converge repeated non-editorial metadata where safe:

- canonical URL;
- stable `surface_id`;
- current public parent;
- Room references;
- projection reference;
- specialist-view relationships;
- evidence/source destination where declared;
- machine-discovery route identity;
- public-surface type;
- compatibility-route metadata.

The visible page need not display this internal structure.

If JSON-LD or machine discovery already has a dedicated builder/owner, Wave 4 should validate or feed that existing system rather than create a duplicate metadata pipeline.

## Shared contextual blocks

Wave 2 may supply reference-oriented blocks such as:

- Related
- Broader context
- History
- Sources & evidence
- Explore further

Wave 4 may converge how these blocks resolve destinations and machine semantics.

It must not require every Hub to display every block.

Rules:

1. no empty universal scaffolding;
2. no generated block may replace domain-specific primary content;
3. each emitted destination must resolve through Wave 1/2 authority;
4. human-curated wording may remain where it improves the reader experience;
5. a Hub may omit a structurally valid block when it would add clutter without reader value.

## Relationship to Wave 3 readiness

Wave 3 readiness is advisory for substantive public knowledge, not core route existence.

Wave 4 may use readiness to avoid surfacing immature material inside optional Related/History/Sources blocks.

Wave 4 must not allow readiness output to remove core Hub/Home navigation or silently rewrite published pages.

Examples:

- `public_route` comes from Wave 1;
- `projection relation` comes from Wave 2;
- `maturity/readiness` comes from Wave 3;
- `how a Hub presents valid mature material` belongs to Wave 4.

No layer subsumes the others.

## Migration stages

### Stage A — Protect current signatures

Before broad convergence edits, strengthen reader-surface validation so the current good page forms become explicit non-regression contracts.

The validator should capture semantic signatures rather than pixel snapshots.

Examples:

Tim:
- developmental spine exists;
- work layer exists;
- Timeline route exists.

Religion:
- theological center exists;
- Bible laboratory exists;
- evidence boundary exists.

Philosophy:
- staged journey exists;
- multiple story/parable forms exist;
- deep long-form source exists.

Science:
- search exists;
- field/type filters exist;
- static catalog marker exists;
- scientific boundary language exists.

World:
- exactly four core sibling lenses exist;
- World Map is one lens, not World's parent;
- World archive/source routes remain available.

### Stage B — Converge route authority

Update Hub-route consumers to use or validate against Wave 1 public-surface authority.

Visible HTML should change only where a current route is wrong or a duplicate authority causes drift.

Do not rewrite layout while changing route authority.

### Stage C — Converge projection consumption

Make existing compact `data-projection-surface` blocks validate against or consume Wave 2 projections where useful.

Prefer validation before replacement.

Move to generated link blocks only where the result demonstrably preserves or improves the existing public experience.

### Stage D — Retire duplicate authority

Only after all affected consumers use House authority should redundant route definitions be downgraded or derived.

Inspect every consumer before retiring fields from:

- `data/frontend-atlas-bridge.json`;
- `manifest.json`;
- static build helpers;
- machine discovery builders;
- generated navigation validators.

Do not delete historical rationale or compatibility data merely because it is no longer primary authority.

## Frontend bridge migration

By Wave 4, parts of `data/frontend-atlas-bridge.json` may be derivable from House contracts.

Potentially derivable concerns include:

- five primary public-door routes;
- public parent route identity;
- stable public-surface destinations.

Concerns that may remain bridge-specific include:

- branch-to-public-door mapping;
- backend-family projection compatibility;
- archive/deep-route compatibility;
- record/path fallback behavior.

Wave 4 must determine this from actual consumers. It must not declare the whole bridge obsolete as a conceptual cleanup exercise.

## Manifest boundary

`manifest.json` continues to own branch/pathway/archive semantics while it has unique information or active consumers.

Route identity should increasingly validate against public-surface authority rather than be independently invented in the manifest.

The manifest must not become a public-page prose owner.

## CSS and component policy

Wave 4 does not require a CSS refactor.

Do not create a giant shared stylesheet simply because five pages share colors or typography.

Shared CSS/component extraction is justified only when:

- the duplication creates actual drift or maintenance risk;
- the extracted unit has one clear responsibility;
- visual output can be shown to remain materially unchanged;
- the change does not force pages into one design system abstraction they do not need.

Domain-specific layout and components may remain local.

## Build-time vs runtime

Essential navigation and machine metadata should prefer build-time/static semantics.

Runtime JavaScript may enhance specialist interactions such as Science filtering, but Wave 4 must not make basic Hub identity, routes, or deeper navigation dependent on JavaScript.

## Public-design non-regression rule

A backend convergence change must not cause a broad public visual/layout rewrite unless that redesign is separately proposed and approved.

Do not use strict pixel freezing as the main guard because it would block ordinary responsive/accessibility improvements.

Instead preserve semantic design signatures and critical interaction behavior.

A Hub after Wave 4 should remain immediately recognizable as the same page family as before Wave 4.

## Validation

Wave 4 validators should prove at least:

- all five Hub IDs resolve through public-surface authority;
- all five canonical routes are unique and correct;
- World remains the fifth primary Hub;
- World Map remains a specialist child/View, not the fifth Hub;
- Hub route consumers do not maintain conflicting primary routes;
- every Hub has a reader-surface identity;
- protected design signatures remain present;
- existing domain-specific interactions remain available;
- essential navigation is present in semantic HTML;
- projection blocks reference valid Wave 2 destinations where convergence has occurred;
- readiness is not rendered as a public score;
- no Hub becomes a canonical fact owner merely for renderer convenience;
- no raw backend JSON/file paths leak into ordinary public navigation;
- generated/build artifact preserves the same canonical route semantics as source;
- public and machine-discovery routes agree.

## Exact-artifact verification

If Wave 4 modifies any build, discovery, patching, or shared-navigation code, final verification must run against the exact built `_site` artifact after the complete repository build/post-build sequence.

The source tree being correct is not sufficient if deployment transforms it differently.

## Testing philosophy

Prefer contract assertions over full HTML snapshots.

Test the properties that matter:

- canonical routes;
- structural markers;
- essential interactions;
- protected reader signatures;
- valid deeper destinations;
- domain-specific components still present;
- no forbidden backend leakage.

Do not freeze incidental whitespace, exact prose, or every CSS declaration.

## Failure behavior

- missing public-surface authority: fail convergence validation;
- conflicting canonical Hub route: fail;
- missing protected signature after a convergence edit: fail;
- optional projection unavailable: keep existing semantic deeper links and report mismatch;
- readiness unavailable: do not remove core navigation;
- bridge/manifest migration incomplete: retain compatibility contract rather than guessing;
- specialist component unavailable: preserve ordinary page reading and report the specialist failure according to its existing validator.

Validators must never mutate HTML into compliance.

## Wave 5 handoff

Wave 4 should leave Explore and specialist Views with a reliable answer to:

- what the five canonical Hubs are;
- which Hub is the ordinary public parent for a subject/branch where declared;
- which specialist Views exist;
- which route is canonical;
- which projection relations are safe to expose;
- which material is intentionally backend-only or not ready for public use.

Wave 5 can then deepen relational traversal without competing with the ordinary public Hubs.

## Non-goals

Wave 4 does not:

- replace the five Hubs with one template;
- redesign Home;
- redesign Explore;
- rewrite all Hub prose;
- flatten Science into a generic card grid;
- flatten Philosophy into a topic index;
- flatten Religion's Bible lab into Related links;
- flatten Tim's developmental structure into a generic profile;
- make World Map the World homepage;
- expose Gardener/readiness scores publicly;
- require identical navigation markup;
- require a framework rewrite;
- require one universal stylesheet;
- delete the frontend bridge or manifest before consumer migration;
- duplicate canonical knowledge for rendering convenience.

## Success criteria

Wave 4 succeeds when:

1. all five Hubs consume or validate against one canonical public-surface authority;
2. common route/machine/projection semantics no longer drift independently;
3. current good public page forms remain recognizable and functional;
4. protected domain-specific signatures are enforced by validators;
5. World is consistently the fifth Hub and World Map remains specialist;
6. optional projection blocks can use common House semantics without becoming universal scaffolding;
7. readiness affects optional substantive exposure, not core route existence;
8. legacy route authority is retired only after real consumer migration;
9. static semantic HTML remains sufficient for ordinary Hub navigation;
10. build/deploy artifacts preserve source route semantics;
11. public visual complexity does not increase merely because backend intelligence increases;
12. Wave 5 can treat Hubs, Explore and specialist Views as complementary rather than competing public architectures.

## Invariants

1. Shared semantics do not require shared layout.
2. The current public design is a protected baseline.
3. Route authority belongs to the House, not duplicated page literals.
4. Editorial prose remains curated.
5. Domain-specific interfaces remain domain-specific.
6. World is a Hub; World Map is a View.
7. Generated context is subordinate to reader clarity.
8. Readiness does not control core navigation.
9. Essential navigation does not depend on JavaScript.
10. Compatibility contracts are retired only after consumer migration.
11. Machine metadata may converge quietly without becoming public clutter.
12. Validators protect meaning and behavior, not incidental pixels.
13. No renderer becomes a knowledge owner.
14. No backend convergence justifies an unapproved public redesign.
15. The five Hubs should agree about the House without becoming each other.
