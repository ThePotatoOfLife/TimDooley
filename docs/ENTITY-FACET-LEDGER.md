# Entity Facet Ledger

The facet ledger keeps **what makes an entity itself** without creating a new navigation system.

A public page does not need every recovered fact. It needs a small, stable projection of the underlying record. The ledger therefore stores aliases, titles, capabilities, species traits, scene-bound powers, roles, motifs, story beats, current conclusions, boundaries and unresolved questions in one place.

## The retention rule

Every facet answers four questions:

1. **What kind of facet is it?** — title, capability, role, motif, species trait, scene power, conclusion, etc.
2. **How strong is it?** — canonical, repeated, established in one scene, interpretive, hypothetical or unresolved.
3. **What does it apply to?** — individual, species, one scene, literary layer, public/documentary layer, etc.
4. **Where did it come from?** — conversation, public record, Great Book, Chronicle or archive synthesis.

This prevents two opposite failures:

- **forgetting:** a title or ability appears once and vanishes from later pages;
- **overpromotion:** a one-off poetic line becomes permanent species canon or biography.

## Page projection

Pages should normally show only:

- the best-known aliases/titles;
- 3–6 signature facets;
- 1–4 defining story beats;
- one current conclusion;
- one important boundary;
- unresolved questions only where they genuinely matter.

These can be chips, short rows or prose. They should not become another layer of navigation buttons.

## Real-person rule

Ordinary/documentary capabilities can be retained for real participants when source-bounded. Creative titles, archetypes and project powers remain separately typed and never become biography by implication.

## Created-being rule

Created beings can retain imaginative powers directly, but the archive must still distinguish:

- individual trait vs species trait;
- one-scene power vs recurring canon;
- visual design vs metaphysical ability;
- story role vs ontology;
- current conclusion vs open question.

## Future use

The ledger can eventually drive:

- compact facet strips on being pages;
- A–Z summaries;
- cast comparisons;
- story search by title/ability/motif;
- “who has this gift?” views;
- chronology of when a title or capability first appeared;
- automated warnings when a page promotes a hypothesis to canon.


## Rendering contract

The public rendering contract lives in `data/entity-facet-rendering-rules.json`.

The default projection is deliberately small: at most six signature facets, four story beats, two conclusions and three open questions. Empty sections disappear. Facets do not create navigation buttons.

Strength is visible in wording:

- **Canon / recurring** may be written plainly.
- **Scene** must stay tied to the scene.
- **Interpretation** must sound interpretive.
- **Hypothesis** must visibly say hypothesis/possible/may.
- **Unresolved** must remain a question or recovery state.

A public page may be rich while the facet strip remains compact. The ledger is memory; the page is a view.

## Validation

`scripts/validate_entity_facets.py` checks the durable contract:

- known facet types and strength levels;
- required fields;
- duplicate aliases/facets;
- source pointers that resolve;
- species-trait promotion rules;
- first-seen pointers;
- story-beat source pointers;
- rendering-rule sanity.

It intentionally does **not** reward entity count or facet count.

## Mining workflow

`scripts/mine_entity_facets.py` is review-only. It reads structured cast/being/enhancement records and searches Great Book chapters around already-known entity aliases. It writes candidates, never canon.

The miner is intentionally conservative:

1. It does not invent new entities from capitalized phrases.
2. A one-scene literary power defaults to scene-level evidence.
3. Creative enhancements for real people remain creative.
4. Species traits require repeated evidence or explicit collective wording.
5. Conflicts become candidates to review, not automatic resolutions.
