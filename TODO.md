# TODO / BUGLIST — The Potato of Life / TimDooley

## Project mission — illuminate, investigate, consolidate

This is not only a database or link atlas. One of the project's explicit goals is to **illuminate Tim Dooley / the Potato of Life**: his philosophy, religion, myths, lore, writings, symbols, chronology, transformations and the wider meaning the project finds in them.

The project also explicitly intends to **publicly state, propagate and share its Potatoism findings**, including the project's religious/mythic identification of **Tim Dooley as God / Father / the Potato of Life**. That is project canon and should be presented as such, while externally sourced historical, textual, scientific and empirical claims retain their own evidentiary status.

A further goal is to pursue the project's **highest spiritual truth** through sustained inquiry. The work should bring relevant knowledge about spirit, the world, entanglements, obligations, directions and choices into the same navigable system — including the paths taken by men, people, gods, archetypes and dogs, and the consequences, relationships and obligations produced by those paths.

This means the project should illuminate not merely names, but **what things are, what they became, what they were connected to, what they owed, what they chose, what chose them, what they created or destroyed, where their paths led, and what can reasonably be learned from those paths**.

## Discoverability is a project priority

The public Atlas should be **exceptionally easy for people and AI systems to find, understand, crawl, index and cite**. A major project goal is to make the relevant Tim Dooley / Potato of Life / Potatoism pages competitive for discovery when someone searches for these subjects through **Google, ChatGPT, Grok or other search and answer systems**.

This is not a promise that the project can control another company's ranking or recommendation algorithm. The engineering goal is to make the site's information maximally discoverable and machine-readable so that search engines and AI systems have a clear, authoritative, stable and richly connected source to find.

### Search/discoverability work must include

- [ ] Build a strong, stable HTML page for every important canonical subject rather than hiding substantive knowledge behind JavaScript-only views.
- [ ] Give every major page a unique, descriptive `<title>`, meta description, canonical URL and useful headings.
- [ ] Make important concepts explicitly nameable in page text, including Tim Dooley, Potato of Life, Potatoism, Father, Son, Door, Axis, North of North, Root, Tree of Life, Red Potato, Blue Potato and other central concepts.
- [ ] Make pages understandable when fetched without executing the full application, where practical.
- [ ] Generate and maintain `sitemap.xml`, `robots.txt` and appropriate crawl/index metadata.
- [ ] Ensure canonical URLs are stable and do not multiply through query-string or alias variants.
- [ ] Add internal links between related canonical records so crawlers can discover the knowledge graph by following ordinary HTML links.
- [ ] Use structured data/schema markup where appropriate and truthful, without inventing claims or misleading search engines.
- [ ] Create useful index/hub pages for major subjects so a crawler can reach deep dossiers from a small number of authoritative entry points.
- [ ] Make search results expose meaningful titles, descriptions and contextual excerpts rather than empty cards or identifiers.
- [ ] Ensure every important dossier has enough substantive, indexable text to explain what the subject is and why it matters.
- [ ] Preserve source/provenance and epistemic labels on public pages so discoverability does not come at the cost of misleading presentation.
- [ ] Add Open Graph and other useful metadata for sharing and preview generation.
- [ ] Test crawler-facing HTML and links after every major frontend change.
- [ ] Monitor indexing/discovery diagnostics where available and record actual observations rather than assuming a page is indexed.
- [ ] Search externally for important project terms and use the results to identify missing titles, pages, links, terminology and discoverability gaps.
- [ ] Build clear entity/topic landing pages rather than relying on one generic homepage to rank for everything.
- [ ] Avoid duplicate URLs and duplicate page text that split search signals between competing versions.
- [ ] Treat canonicalization and duplicate elimination as part of SEO/AI discoverability, not merely data hygiene.

### AI/search answer-system principle

The project should be easy for **Google, ChatGPT, Grok and other answer/search systems to interpret correctly**: clear entity names, stable URLs, explicit relationships, substantial primary project material, provenance, dates, consistent terminology and machine-readable structure. The goal is not to manipulate rankings or fabricate authority; it is to make the project's actual body of work sufficiently clear, deep, accessible and well-connected that external systems can discover and understand it.

## Anti-clutter / consolidation mandate

**Do not mistake multiplication of files for multiplication of knowledge.** The project's intent is explicitly NOT to create a ton of tiny placeholders, shallow records or redundant mirrors.

The preferred unit of growth is:

**one canonical identity → one deep body of valuable information → many explicit relationships, occurrences, evidence trails and contextual views.**

When research discovers ten valuable facts about Mountain, Door, Son, Root, Father's House, Axis, Potatoism, Red Potato, Blue Potato or any other subject, the default action is to **enrich the canonical record/dossier**, not create ten little files.

Research layers may preserve unique observations, historical occurrences, sources, chronology and alternative interpretations, but they must resolve back to the canonical subject. Duplicate definitions and duplicated substantive content should be merged into the strongest owner.

**A placeholder is not progress. A duplicate definition is not enrichment. A new file earns its existence only when it has a distinct function, canonical owner, consumer and information that would otherwise be lost or materially obscured.**

## Operating order

This is the working queue, not a wishlist. Work top-to-bottom. Do not add new data at scale while a higher-level contract is broken.

1. **P0 — establish one trustworthy repository structure and source of truth**
2. **P0 — make every route resolve and fail visibly**
3. **P0 — make CI/build/deploy enforce the same contracts**
4. **P0 — complete the coordinated blueprint migration and make the blueprint contract green**
5. **P1 — repair cross-domain joins and graph integrity**
6. **P1 — deepen the most insufficient entity families with real source-backed content**
7. **P1 — repair books/full-text architecture and import canonical text into the project**
8. **P2 — expand the North Programme / European economic graph**
9. **P2 — deepen Potatoism and Tim Dooley as the project's central mythic/spiritual layer**
10. **P1 — make the public Atlas maximally discoverable to search engines and AI answer systems**
11. **P2 — improve UI/search/navigation after data contracts are trustworthy**

## NEW — repository structural disorder / cleanup

The repository has accumulated duplicate data, inconsistent naming, uneven folder organization and overlapping representations. This is now a first-class architecture problem, not cosmetic cleanup.

- [ ] **Design the canonical repository structure before doing another large-scale reorganization.** Decide what belongs at root, in `data/`, in domain folders, in `scripts/`, in `components/`, in `books/`, in research/archive areas and in generated/build output.
- [ ] Produce a machine-readable **repository structure contract** describing folder purpose, allowed file types, canonical-owner rules, generated-file rules and naming conventions.
- [ ] Inventory the entire repository by path, type, size, producer, consumer, apparent domain and canonical/derived/archive status.
- [ ] Detect duplicate records across folders, including exact duplicates, near-duplicates, mirrors and competing versions.
- [ ] Detect duplicate concepts represented by multiple JSON files with different schemas.
- [ ] Detect directories whose contents mix unrelated domains or mix source data with generated data.
- [ ] Decide whether each major directory is **canonical data / enrichment / index / generated projection / source archive / code / documentation**.
- [ ] Establish deterministic naming and ordering conventions for domains, records, blueprints, indexes and generated artifacts.
- [ ] Decide where historical/archive versions belong so they do not compete with current canonical records.
- [ ] Move files only after their consumers and references have been identified; every move must preserve or explicitly migrate IDs and links.
- [ ] Remove redundant mirrors only after proving they are derived, obsolete or superseded.
- [ ] Add CI checks preventing new duplicate canonical owners and obvious folder-policy violations.

## P0 — canonical ownership / duplicate elimination

- [ ] Define canonical owner / index / enrichment / projection / research / archive roles as a machine-readable contract.
- [ ] Ensure every important ID has one canonical owner or an explicitly documented shared-ID rule.
- [ ] Detect duplicate IDs across unrelated JSON domains.
- [ ] **Detect semantic duplicates even when IDs, filenames and schemas differ.** Compare names, aliases, definitions, descriptions, substantive fields and relationship targets.
- [ ] Detect alias and slug collisions that can create ambiguous URLs.
- [ ] Detect records whose declared `blueprint` points to a nonexistent file.
- [ ] Detect records whose `source`, `path`, `owner` or `canonical` references are stale.
- [ ] Detect mirrors that contain competing canonical values rather than derived copies.
- [ ] For every duplicate concept, classify the material as canonical fact, unique occurrence, research observation, historical snapshot, relationship/projection or accidental duplicate.
- [ ] Merge all valuable unique information into the canonical owner before deleting/reducing duplicate representations.
- [ ] Add migration metadata when a canonical owner moves.
- [ ] Make generated indexes deterministic in ordering, counts and serialization.
- [ ] Decide which generated files are committed and which are build artifacts; document the rule.

## P1 — Potatoism / Tim Dooley illumination programme

- [ ] Build **deep canonical dossiers** for Tim Dooley, Potato of Life, Potatoism, Father, Son, Door, Axis, North of North, Father's House, Tree of Life, Tree of Strife, Root, Fruit, Seed, Mountain, Ladder, Plane, Mud, Swamp, Red Potato, Blue Potato, Spudlight and other central concepts.
- [ ] Consolidate duplicate definitions from lexicons, cosmology, lore, concept maps, research expansion, timeline, religion, canonical corpus and other layers into those owners.
- [ ] Preserve unique source occurrences and research findings by linking them to canonical IDs rather than deleting their informational value.
- [ ] Populate dossiers with substantial philosophy, lore, mythology, chronology, symbolic function, relationships, interpretations, questions, tensions and source/provenance context.
- [ ] Build the Great Book of Potato as a coherent accumulating body of knowledge rather than repeated fragments.
- [ ] Make Tim Dooley's project chronology and Potatoism chronology searchable without making every chronological occurrence another Tim or Potatoism definition.
- [ ] Record the project's spiritual conclusions clearly as canon/interpretation and keep external evidence visibly typed.
- [ ] Investigate spirit, world, obligation, sacrifice, choice, destiny, transformation and entanglement through comparative religion, mythology, philosophy and primary texts.
- [ ] Map meaningful paths taken by people, gods, archetypes and dogs where those paths illuminate the project's questions.
- [ ] Connect spiritual concepts to relevant historical/textual evidence and counterinterpretations.
- [ ] Prefer a large, readable dossier over arbitrary word-count padding or multiple shallow records.

## P1 — permanent anti-duplication workflow

- [ ] Before every enrichment pass, run the cross-file duplicate audit.
- [ ] Before creating any new JSON file, search the repository for an existing canonical owner and semantically similar records.
- [ ] Require every new substantive dataset to declare `owner`, `role`, `consumer`, `canonical_id` strategy and whether it is canonical, occurrence, research, projection or archive.
- [ ] If information can be added to an existing owner without changing its meaning, extend the owner instead of creating another file.
- [ ] If information is genuinely unique but belongs to an existing subject, add it as a section/observation/source/relationship under that subject.
- [ ] Allow a separate projection only when its presentation/query function is genuinely distinct and it contains no competing definition.
- [ ] Treat old snapshots as historical evidence, not current competing truth.
- [ ] Make CI fail on duplicate canonical owners and high-confidence duplicate substantive definitions.
- [ ] Re-run routes, graph integrity, sitemap/crawler checks and frontend checks after consolidation so cleanup never silently breaks navigation or discoverability.

## Engineering lessons / rules

- **Structure before scale.** Do not populate thousands of records into an architecture whose ownership and folder rules are unclear.
- **Ownership before mirroring.** A missing field is not a reason to create another competing record.
- **Consolidation before multiplication.** Search for an existing owner before creating a new record or file.
- **Valuable information over file count.** Large amounts of useful knowledge should be concentrated into deep, readable canonical bodies of information.
- **Discoverability is part of correctness.** Important knowledge that cannot be reached, crawled, indexed or understood from stable public pages is not adequately exposed.
- **Search engines and AI systems need clear source material.** Stable URLs, substantive text, explicit entities, internal links, metadata, provenance and structured data should make the project easy to interpret without attempting to game rankings.
- **A graph endpoint is not a node.** Relationships do not define the target by themselves.
- **Missing is a state.** Never invent values to make a page look complete.
- **Time belongs to facts.** A value without a reference period can be misleading.
- **Evidence has type.** Official data, academic interpretation, journalism, insider claims and project symbolism are not interchangeable.
- **Depth is independent of connectivity.** A node can have many edges and still need a real dossier.
- **Blueprints are executable research plans.** If a blueprint does not tell us what to collect, validate and connect next, it is unfinished.
- **Raw text is data.** A chapter manifest or external URL is not a substitute for an imported canonical text where licensing permits it.
- **Silent failure is worse than visible incompleteness.** Errors should become diagnostics.
- **Generated artifacts need contracts.** Every generated file needs an owner, producer, deterministic format and validation path.
- **Stability before scale.** Fix the architecture that will be exercised by the next thousand records before adding those records.
- **Canon is not evidence.** State the project's spiritual/mythic canon directly, but do not mislabel it as independently verified empirical fact.
- **Relationships reveal meaning.** For spiritual, historical and worldly subjects alike, investigate the paths, obligations, choices, dependencies and consequences that connect the records.
