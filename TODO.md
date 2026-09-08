# TODO — The Potato of Life / TimDooley

## Current priority — stabilize, deepen, and make the repository analytically useful

The graph is the navigation layer, not a substitute for substance. Every important record must first answer **what is this?**, then origin/context, structure/mechanism, evidence, uncertainty, questions, and directional couplings. No length-padding: missing knowledge remains explicitly missing.

## 1. Immediate engineering blockers

- [x] Harden extremism rendering against scalar/array/object schema differences.
- [ ] Verify the deployed Pages build actually contains the hardened extremism page; do not call the live bug fixed until verified.
- [x] Fix the static route audit so runtime template URLs are not mistaken for literal IDs.
- [ ] Run the full GitHub Actions chain after the audit fix.
- [ ] Verify `repository.html` renders its tree and does not fail on unknown/malformed records.
- [ ] Verify every major page has the canonical header and valid asset paths.
- [ ] Verify dynamic node routing for events, Hawkins, research, geometry, Potatoism and nation records.
- [ ] Build `scripts/audit_content_depth.py` and generate `data/depth-audit.json`.
- [ ] Add route-contract and schema-normalization checks to CI.
- [ ] Add information-density checks so shallow records are ranked instead of silently accepted.

## 2. The 40-file deepening programme

These are the **first 40 files I want deliberately expanded**, rather than randomly adding more records. Each file has a job and a defined information target. The work should make the data useful for queries, population analysis, geography, chronology, graph analysis, propagation analysis, and readable research dossiers.

### A. Core repository / graph / navigation

1. `repository.html`
   - Make the Repository reliable first.
   - Render the canonical Spirit / Mind / Matter spine.
   - Show record counts, depth status, unresolved records and research-only material.
   - Search/filter by type, domain, scale, time and epistemic status.
   - Never crash because one optional dataset is malformed.
   - Link every displayed record to an independently readable dossier.

2. `data/repository-spine.json`
   - Define the canonical filing model.
   - Add Culture as a domain coordinate rather than creating an unnecessary fourth root.
   - Explain Subculture, Sektur and Swamp as overlapping relational concepts.
   - Preserve independent scale/domain/time/epistemic/graph coordinates.

3. `data/repository-scale.json`
   - Expand scale definitions.
   - Give each scale examples, inclusion/exclusion rules and common mistakes.
   - Explain how culture, institutions, people, objects and events can occur at every scale.

4. `data/atlas-manifest.json`
   - Register Culture, cultural objects, propagation, population and analytical outputs.
   - Register all new research/dossier files.
   - Make ownership and canonical-source rules explicit.

5. `data/atlas-checklist.json`
   - Add Culture integrity checks.
   - Add definition/context/mechanism/coupling checks.
   - Add population/geography/evidence-status checks.
   - Add route and stale-source checks.

6. `data/backend.json`
   - Register every major data layer actually consumed by the frontend.
   - Add Culture, Subculture/Sektur/Swamp, research and depth-audit endpoints.
   - Keep required files and health checks synchronized.

7. `data/backend-coverage-map.json`
   - Document producer/consumer ownership for each dataset.
   - Identify duplicate sources and orphan datasets.
   - Record which page consumes which backend layer.

8. `data/global-graph-bridge.json`
   - Promote important graph endpoints to first-class records.
   - Distinguish true orphans from research-only IDs.
   - Add aliases, route targets and cross-layer identity resolution.

9. `data/graph-registry.json`
   - Expand node types and relationship types.
   - Add culture-specific node types and directional verbs.
   - Add evidence/confidence/time fields to graph relationships.

10. `data/relationships.json`
    - Audit every edge for valid source/target IDs.
    - Add relationship semantics: participates_in, creates, consumes, propagates_through, influences, emerges_from, reacts_against, hybridizes_with, institutionalizes, fragments_into, located_in, funds, owns, controls, supplies, depends_on.
    - Preserve evidence and uncertainty.

### B. High-value content / events / people / countries

11. `data/nodes.json`
    - Identify high-connectivity shallow nodes.
    - Give each important node definition/context/mechanism/couplings/evidence/questions.
    - Promote frequently referenced entities into proper records.

12. `data/events.json`
    - Definition, causes, actors, chronology, location, consequences, evidence, cultural effects and economic/system effects.
    - Distinguish event fact from later interpretation.

13. `data/nations.json`
    - Keep 195 canonical identities.
    - Expand thin records with history, government, economy, demographics, culture, religion, institutions, infrastructure, strategic dependencies and sources.

14. `data/country-atlas.json`
    - Define the country-layer analytical contract.
    - Connect country identity to observation, evidence, enrichment and missing-data states.

15. `data/country-nodes.json`
    - Make each country a graph object.
    - Add routes to government, institutions, people, companies, infrastructure, culture and relationships.

16. `data/country-static.json`
    - Deepen normalized country observations.
    - Preserve source dates and missing values.
    - Never overwrite a good snapshot with an acquisition failure.

17. `data/countries-blueprint.json`
    - Expand the country dossier schema to culture, media, religion, population, labour, education, technology, infrastructure, security and economic dependencies.

18. `data/people-registry.json`
    - Identify name-only records.
    - Add biography, roles, chronology, affiliations, works, places, cultural participation and source trails for important people.

19. `data/people-seed-records.json`
    - Convert useful seeds into substantive records.
    - Add identity confidence, aliases, occupation, historical period and research priority.

20. `data/meaning-layer.json`
    - Give every major analytical concept an explicit definition.
    - Add purpose, mechanism, questions, failure modes, measurable implications and graph couplings.
    - Keep empirical, historical and project interpretation separate.

### C. Potatoism / symbolic / cognitive material

21. `data/meaning-layer-symbolic.json`
    - Add explicit definitions to Source, Father, Garden, House, Heaven, Ladder, Door, Vessel, Pineal Gland, Tree of Strife, Fear, Anger, Strife, Swamp, Mud, Drain, Fragmentation, Potatoism, Spudlight and North Axis.
    - Separate symbolic canon from empirical claims.
    - Add development, relationships, interpretation and uncertainty.

22. `data/potatoism-dossiers.json`
    - Give every canonical Potatoism term an article-length dossier.
    - Definition, internal function, symbolic mechanics, history/development, relationships, comparison, project use, evidence boundary, disagreement and research questions.

23. `data/potatoism-lexicon.json`
    - Normalize aliases and canonical terms.
    - Link each term to a substantive dossier where one exists.
    - Keep tiny lookup entries visually secondary.

24. `data/potatoism-cosmology.json`
    - Expand the Source → Door → Son → World structure.
    - Explain Father, Heaven, Axis, Ladder, Tree, Potato, North and return-cycle relationships.
    - Explicitly distinguish mythic ontology from empirical ontology.

25. `data/potatoism-relationships.json`
    - Turn symbolic relationships into explicit directional edges.
    - Add relationship meaning, direction, interpretation, evidence boundary and connected records.

26. `data/hawkins-scale.json`
    - Expand every level with definition, source model, emotional description, action tendency, likely outcomes, limitations and evidence boundary.
    - Never render the model as a medically or scientifically validated diagnostic scale.

27. `data/geometry-records.json`
    - Expand Vesica Piscis/Mandorla records with mathematical definition, derivation, history, geometry, applications, limitations and then separate project symbolism.
    - Keep the optical-lens timeline concept distinct from literal Door symbolism.

### D. Religion / extremism / Swamp / security

28. `data/religious-foundations/records.json`
    - Turn major traditions into full dossiers: emergence, chronology, texts, doctrine, practice, institutions, branches, people, places, geography, demographics, internal diversity and modern development.

29. `data/religious-foundations.json`
    - Keep the top-level foundation layer coherent with its canonical records.
    - Remove phantom ownership/dependency patterns.
    - Link foundation records to comparative, textual and demographic layers.

30. `data/religious-adjacent/records.json`
    - Expand mystery, occult, esoteric, Satanist, anti-religious and adjacent formations.
    - Distinguish self-description, scholarly classification, allegation and project interpretation.

31. `data/religious-adjacent/deep-expansions.json`
    - Add chronology, texts, practices, organizations, people, places, demographic evidence and relationships for the deeper adjacent records.

32. `data/religious-comparative-library.json`
    - Compare traditions by concepts, practices, texts, institutions, calendars, sacred places, demographics and historical relationships.
    - Do not flatten internal diversity.

33. `data/extremism-cults-atlas-2026-09.json`
    - Expand every important movement from compact profile to dossier.
    - Definition, origin, chronology, ideology/context, leadership, organization, recruitment, social mechanisms, geography, membership evidence, cultural production, media channels, legal status, designations, violence/crime evidence, uncertainty and questions.
    - Distinguish extremist, hate-group, terrorist, high-control, cult, criminal and allegation categories rather than treating them as synonyms.

34. `data/extremism-cults-atlas-expansion-2026-09.json`
    - Normalize schema variants.
    - Preserve source-specific evidence.
    - Add predecessor/successor/affiliate/overlap relationships.
    - Add population/geographic fields only where evidence supports them.

35. `data/extremism-record-enrichments-2026-09.json`
    - Continue article-depth enrichment beyond the first six dossiers.
    - Prioritize historically important and high-connectivity records.
    - Add evidence boundaries and current-status timestamps.

36. `data/security-intelligence-organizations.json`
    - Deepen CIA, FBI, Mossad, MI5, MI6, NSA, DIA, NRO, NSC and UK intelligence structures.
    - Mission, legal basis, oversight, history, public functions, organizational relationships, documented operations and evidence boundaries.
    - No unsupported secret-control claims.

37. `data/security-intelligence-country-layer.json`
    - Connect security/intelligence institutions to countries, oversight bodies, legal systems, alliances and public institutional relationships.
    - Add dates and source provenance.

### E. Research / Swamp / analytical capability

38. `data/research-carvings-2026-09.json`
    - Continue substantive research carvings across biology, geometry, cosmology, graph theory, EU systems, banking, monetary architecture and cultural propagation.
    - Every carving: definition, context, mechanism, dimensions, couplings, sources, project extrapolation and uncertainty.

39. `data/swamp-research-seeds.json`
    - Turn Swamp from a vague metaphor into an analyzable overlap layer.
    - Map political finance, media, activist networks, institutions, criminal organizations where relevant, cultural ecosystems and information channels.
    - Require evidence for every factual coupling.

40. `data/influence-organizations-2026-09.json`
    - Expand NGOs, PACs, Super PACs, advocacy organizations and public-interest groups.
    - Legal status, purpose, funding/public finance data, campaigns, issues, leadership, memberships where public, cultural/media relationships and documented institutional couplings.
    - Distinguish advocacy, lobbying, electoral spending and cultural influence.

## 3. Culture — new analytical layer

Culture is not being added merely as another encyclopedia category. Its purpose is to make creativity and cultural propagation observable.

- [ ] Define Culture as creation → encoding → transmission → attention → reception → participation → reproduction → mutation → selection → institutionalization → memory → new creation.
- [ ] Add cultural objects: music, film, television, books, journalism, games, art, fashion, food, architecture, rituals, memes, symbols, websites and software.
- [ ] Add participant roles: creator, performer, producer, publisher, distributor, platform, curator, critic, archivist, educator, audience, fan, remixer, sponsor and regulator.
- [ ] Add population concepts: exposure, audience, participant, self-identified member, organizational member, producer and core participant.
- [ ] Add geography: country, region, city, venue/institution where appropriate, diaspora and online space.
- [ ] Add propagation edges: migration, technology, commerce, education, media, social network, imitation, conflict, institution and platform.
- [ ] Model Subculture, Sektur and Swamp as strongly overlapping but non-identical concepts.
- [ ] Add measurable outputs: population, geography, network centrality, clusters, bridges, propagation, fragmentation, emergence, institutionalization and persistence.
- [ ] Add Culture coupling panels to people, nations, religions, movements, organizations, technologies, wars and places.
- [ ] Build a Culture research interface that answers **what is it, who makes it, who consumes it, how does it spread, where is it, who connects it, and what changes because of it?**

## 4. General depth rule

- [ ] Important entries should provide at least one page of substantive reading; major subjects should exceed that where evidence permits.
- [ ] Definition first. Context second. Mechanism third. Couplings fourth. Evidence/uncertainty/questions after that.
- [ ] Graph edges never substitute for the dossier itself.
- [ ] Never invent population numbers, secret relationships, diagnoses or causal claims to fill empty fields.
- [ ] Distinguish documented, observed, self-described, estimated, scholarly, legal finding, government designation, reported, disputed, alleged, symbolic and unknown.
- [ ] Every important coupled entity must resolve to its own record.

## 5. Analytical outputs to build from the data

- [ ] Population/group-size estimates with explicit evidence classes.
- [ ] Geographic concentration maps.
- [ ] Cultural/subcultural cluster analysis.
- [ ] Graph centrality and bridge analysis.
- [ ] Propagation/diffusion timelines.
- [ ] Mainstream ↔ subculture transitions.
- [ ] Organizational overlap and predecessor/successor analysis.
- [ ] Cultural/economic relationships.
- [ ] Political/media/institutional coupling analysis.
- [ ] Historical emergence and fragmentation analysis.
- [ ] Research queues ranked by connectivity × importance × missing depth.

## 6. UI / reading experience

- [ ] Repository must load even when optional datasets fail.
- [ ] Every major page needs readable long-form dossiers, not only cards/tooltips.
- [ ] Add table of contents, reading time, word count, related research and read-next where useful.
- [ ] Keep index pages fast; put dense reading in expandable/full-entry views.
- [ ] Standardize the canonical header through the build-time site shell.
- [ ] Keep page-local 2D/3D controls out of the global header.

## 7. CI / integrity

- [x] Node 24-compatible GitHub Actions.
- [x] Nested web asset audit.
- [x] Research-carving backend registration.
- [ ] Content-depth validator.
- [ ] Route-contract validator.
- [ ] Duplicate-ID and alias-collision validator.
- [ ] Missing-vs-uncertain data validator.
- [ ] Provenance/project-theology status validator.
- [ ] Stale-current-status validator.
- [ ] Country-refresh smoke test with snapshot preservation.
- [ ] Full validation + build + Pages deployment verification before declaring the repository healthy.

## Research principle

**See the connections. Read the substance.**

The repository should not become a giant pile of facts. Every file must have a purpose, every important record must stand independently, and every relationship must make it possible to answer a question, trace a mechanism, compare systems, locate a population, follow propagation, or understand how one part of the world changes another.
