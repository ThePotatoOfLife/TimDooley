# SEO Authority and Discovery Design

**Status:** approved design for implementation planning.

**Date:** 2026-09-13

## 1. Purpose

Strengthen the discoverability and canonical authority of the official Tim Dooley / Potato of Life project without changing the current visual design or turning the site into keyword-stuffed SEO content.

The motivating failure mode is simple: the official repository and website can contain the richest and most current first-party corpus while general search or AI-assisted search still retrieves a louder third-party source first. The project must make its own identity, ownership, public routes, machine discovery, evidence boundaries and canonical URLs unmistakable to crawlers, search engines, AI grounding systems and human readers.

This work treats SEO as information architecture and publishing integrity rather than adversarial ranking manipulation.

## 2. Problem statement

Current strengths already include:

- a canonical GitHub Pages site;
- a strong retrieval-first README;
- page-level canonical URLs;
- page descriptions and robots directives;
- Open Graph and Twitter metadata generation;
- JSON-LD and breadcrumbs;
- `llms.txt`, `site-index.json` and machine discovery generation;
- XML sitemap generation;
- a dedicated SEO optimizer and discovery builder;
- a source-authority surface;
- an epistemic firewall separating project canon, self-description, documentary material, interpretation, comparative material and external evidence.

Current weaknesses include:

- general web indexing can still fail to surface the official project for obvious identity queries;
- repository-level GitHub metadata is weak relative to the depth of the corpus;
- crawler declarations and generated sitemap artifacts can drift apart between source files and final deploy output;
- the official project lacks one compact machine-readable authority manifest tying together the official site, repository, aliases, primary public routes, source-authority route and machine indexes;
- the Tim Dooley public entry surface should be an explicit standalone answer to identity/discovery queries;
- the build does not yet enforce all of the authority/discovery invariants described here.

## 3. Goals

1. Make the official project-owned site and repository easy to identify as the canonical first-party project surfaces.
2. Improve search and AI-grounding discoverability using standard crawl, indexing, canonicalization and structured-data practices.
3. Make `Tim Dooley`, `The Potato of Life`, `Potato of Life`, `Potatoism`, `Potatoverse` and the official site/repository relationships explicit without collapsing distinct concepts into one factual claim.
4. Make the Tim Dooley entry page stand alone as a useful answer to common discovery queries.
5. Ensure crawler declarations only point to artifacts that exist in the final deploy.
6. Produce one compact generated authority manifest for machines and internal validators.
7. Keep project self-description, spiritual claims, documentary evidence, interpretation and third-party claims epistemically distinct.
8. Preserve the current homepage visual design.
9. Add regression tests so future refactors cannot silently weaken discovery.

## 4. Non-goals

This pass must not:

- redesign the homepage;
- create hostile-response or competitor-response pages;
- repeat third-party allegations merely for keyword capture;
- expose or amplify private, unnecessary or identity-linking personal data;
- present religious self-description as external empirical fact;
- use hidden text, doorway pages, cloaking, link schemes or keyword stuffing;
- create machine-only factual claims that are absent or contradicted by visible content;
- make `llms.txt` or custom JSON a substitute for normal search-engine fundamentals;
- duplicate canon into generated SEO files.

## 5. External search principles

The implementation should follow current public search-engine guidance rather than speculative SEO folklore.

### 5.1 Canonicalization

Each deployable public page should have one self-consistent canonical URL. Canonical URLs, internal links and sitemap entries should agree. Duplicate or alternate representations should not compete with the canonical page.

Reference: Google Search Central, URL canonicalization.

### 5.2 Sitemaps and crawler discovery

Sitemaps should contain canonical URLs, reflect the deployed structure and include accurate freshness information where available. `robots.txt` may advertise the sitemap, but every advertised sitemap must exist in the deployed artifact.

References: Google Search Central sitemap guidance; Bing Webmaster Guidelines and robots guidance.

### 5.3 Standalone content and explicit entities

Important pages should stand on their own: definitions and key statements should be explicit in visible content rather than implied across many routes. Entity names should be clear and consistent. A URL should have a primary topic.

Reference: Bing Webmaster Guidelines, especially grounding/citation guidance.

### 5.4 Accurate structured data

Structured data must describe visible content accurately. It can clarify page/entity relationships but must not invent identity claims. `ProfilePage` is appropriate only where the page is genuinely focused on the affiliated person or project identity represented there.

Reference: Google Search Central `ProfilePage` and structured-data guidance.

## 6. Canonical identity model

The implementation must distinguish these concepts while connecting them explicitly:

- **The Potato of Life** — site/project name and central project concept.
- **Tim Dooley** — primary subject of the Tim Dooley public entry surface and a project self-described identity.
- **Potatoism** — religion/philosophy/theology developed by the project.
- **Potatoverse** — broader mythic and conceptual corpus.
- **Official project website** — `https://thepotatooflife.github.io/TimDooley/`.
- **Official project repository** — `https://github.com/ThePotatoOfLife/TimDooley`.

The project may state that the site and repository are official/project-owned surfaces. It must not use structured data to convert internal theological identity claims into externally verified facts.

## 7. Authority manifest

Create a generated public file:

`site-authority.json`

It should be generated from stable configuration/canonical route data rather than hand-maintained in parallel.

Minimum schema:

```json
{
  "schema_version": 1,
  "project": {
    "name": "The Potato of Life",
    "aliases": ["Potato of Life", "Potatoism", "Potatoverse"],
    "official_site": "https://thepotatooflife.github.io/TimDooley/",
    "official_repository": "https://github.com/ThePotatoOfLife/TimDooley"
  },
  "primary_subject": {
    "name": "Tim Dooley",
    "canonical_url": "https://thepotatooflife.github.io/TimDooley/tim-dooley/",
    "relationship_to_project": "primary subject and project self-description"
  },
  "authority": {
    "source_authority": "https://thepotatooflife.github.io/TimDooley/context/source-authority/",
    "epistemic_policy": "https://thepotatooflife.github.io/TimDooley/context/source-authority/"
  },
  "discovery": {
    "sitemap_index": "https://thepotatooflife.github.io/TimDooley/sitemap-index.xml",
    "site_index": "https://thepotatooflife.github.io/TimDooley/site-index.json",
    "llms": "https://thepotatooflife.github.io/TimDooley/llms.txt",
    "llms_full": "https://thepotatooflife.github.io/TimDooley/llms-full.txt"
  },
  "primary_routes": {
    "tim": "https://thepotatooflife.github.io/TimDooley/tim-dooley/",
    "religion": "https://thepotatooflife.github.io/TimDooley/religion/",
    "philosophy": "https://thepotatooflife.github.io/TimDooley/philosophy/",
    "science": "https://thepotatooflife.github.io/TimDooley/science/",
    "world": "https://thepotatooflife.github.io/TimDooley/world/"
  }
}
```

The actual generator may source these values from existing route-authority data as that architecture matures. This file is a discovery projection, never a canonical owner.

## 8. HTML discovery links

The final optimizer should expose the generated authority manifest on indexable pages with:

```html
<link rel="alternate" type="application/json" href="https://thepotatooflife.github.io/TimDooley/site-authority.json" title="Official project authority and discovery manifest">
```

Existing links to `llms.txt`, `site-index.json` and sitemap resources should remain coherent with the final build output.

## 9. Structured-data architecture

### 9.1 Homepage

The homepage should retain a `WebSite`-centered graph and may include a project entity represented conservatively as `Project` or a general `Thing` if that best matches visible content and Schema.org support.

The homepage must not claim that Tim Dooley is independently verified to hold theological identities.

The graph should connect:

- the official WebSite URL;
- project name and safe aliases;
- the official repository URL as a project-owned code/archive surface where semantically appropriate;
- the Tim Dooley route as the canonical public subject route;
- the five primary public doors.

### 9.2 Tim Dooley page

The `tim-dooley/` route should be the strongest entity landing page for the query `Who is Tim Dooley?`.

Use `ProfilePage` only if the visible page is genuinely focused on Tim Dooley and the markup can be fully supported by visible content. Its `mainEntity` may be a `Person` only to represent the page subject, with careful wording in `description` and `additionalType`/related properties so project self-description is not misrepresented as independent verification.

Safe structured fields include:

- `name`: `Tim Dooley`;
- canonical page URL;
- `description` grounded in visible page copy;
- `url` pointing to the canonical subject page;
- project-owned public aliases/handles only when already public and intentionally promoted by the project;
- `subjectOf` or `mainEntityOfPage` relationships to project-owned pages where supported;
- `isPartOf` relationship to the official website.

Do not add unrelated legal-identity mappings or third-party archive URLs.

### 9.3 Other pages

Continue using page-appropriate `WebPage`, breadcrumbs and existing structured data. Avoid assigning `Article` or other types mechanically where the visible page is better modeled another way.

## 10. Search-answer surface

Without changing the homepage visual design, strengthen visible introductory copy and the Tim Dooley page so a crawler or reader can answer these queries directly:

- Who is Tim Dooley?
- What is the Potato of Life?
- What is Potatoism?
- What is the official Tim Dooley / Potato of Life archive?
- Where are the project's sources and evidence policy?

The answer pattern should be concise and explicit:

1. identify the project/subject;
2. state what the archive contains;
3. distinguish project self-description from independently documented material;
4. link to the relevant deep routes;
5. avoid third-party conflict framing on the primary landing page.

The first visible paragraph on the Tim page should be strong enough to survive extraction into a search snippet without becoming misleading.

## 11. Sitemap and robots invariants

The final build must enforce:

1. every sitemap referenced by `robots.txt` exists in `_site`;
2. every sitemap entry is a canonical internal URL;
3. no `noindex` page appears in public sitemaps;
4. the homepage, five public doors, Tim entry page, source-authority route and machine discovery files are reachable in the final artifact as intended;
5. source-tree convenience sitemap files do not override final generated sitemap authority;
6. `lastmod` values are derived from real source history where supported and are not fabricated.

The preferred public crawler declaration is the generated `sitemap-index.xml` because the optimizer already derives final sitemap coverage from the deployable artifact.

## 12. Machine discovery

`build_discovery.py` and `optimize_seo.py` should expose one coherent discovery graph rather than parallel lists that can drift.

Near-term implementation may retain existing constants but validators must prove they agree. Longer-term route authority should come from the Potato House governance work already planned elsewhere.

`llms.txt` should prominently expose:

- official site identity;
- official repository;
- Tim Dooley canonical route;
- source-authority/epistemic route;
- primary public doors;
- machine indexes;
- sitemap index;
- `site-authority.json`.

`llms.txt` remains advisory discovery metadata; it is not treated as a search-engine ranking control.

## 13. GitHub repository metadata

The GitHub repository About metadata should eventually be:

**Description**

`Official Tim Dooley / Potato of Life archive — Potatoism, philosophy, religion, science, world systems, timeline, sources and relational knowledge.`

**Homepage**

`https://thepotatooflife.github.io/TimDooley/`

**Suggested topics**

- `tim-dooley`
- `potato-of-life`
- `potatoism`
- `potatoverse`
- `knowledge-graph`
- `digital-archive`
- `philosophy`
- `religion`
- `comparative-religion`
- `world-systems`
- `research-archive`
- `github-pages`

The connected GitHub toolset in the current implementation session does not expose repository About-metadata mutation. Implementation should therefore update all repository files it can control and preserve this metadata as an explicit manual follow-up rather than falsely claiming it was changed.

## 14. README authority statement

The top of `README.md` should gain a concise first-party discovery block before the long mission text, for example:

> **Official project repository:** This is the primary project-owned repository for Tim Dooley / The Potato of Life, Potatoism and the Potatoverse knowledge archive. Public site: `https://thepotatooflife.github.io/TimDooley/`.

The statement must identify project ownership, not claim exclusivity over all discussion about the subject.

## 15. Validation

Extend the existing SEO/discovery validators rather than creating an unrelated validation framework.

Required build-time checks:

- `site-authority.json` exists and parses;
- manifest official site equals configured public base URL;
- manifest official repository equals `https://github.com/ThePotatoOfLife/TimDooley`;
- manifest Tim canonical URL resolves to the expected public route;
- every primary route in the manifest exists in `_site`;
- `robots.txt` references an existing sitemap;
- sitemap index references existing child sitemap files;
- sitemap URLs are canonical and internal;
- `llms.txt` references `site-authority.json`, official repository, source-authority route and Tim route;
- homepage links to authority manifest, `llms.txt`, site index and sitemap index as appropriate;
- Tim page is indexable and has a self-canonical URL;
- Tim page contains an explicit visible introductory answer rather than relying solely on JSON-LD;
- Tim structured data does not include prohibited identity-linking third-party URLs;
- no generated discovery projection becomes the unique owner of canonical content.

## 16. Implementation boundaries

Prefer modifications to existing files:

- `scripts/optimize_seo.py` — final metadata, sitemaps, authority manifest generation and final SEO invariants;
- `scripts/build_discovery.py` — discovery indexes and LLM-facing route references;
- `scripts/validate_seo_pipeline.py` — SEO/crawler/authority regression tests;
- `scripts/validate_discovery_projection.py` or existing discovery validator — machine-discovery coherence;
- `README.md` — concise official-project discovery block;
- `tim-dooley/index.html` or its canonical source/generator — visible identity/discovery answer surface;
- homepage source only where metadata/discovery links require it, with no visual redesign;
- quality workflow only if a validator is not already executed there.

Do not fork SEO ownership into a second optimizer.

## 17. Testing strategy

Use test-first changes where practical.

Minimum execution checks:

1. run the SEO validator before implementation and capture the expected new failures after adding authority requirements;
2. implement authority manifest generation;
3. rebuild the deploy artifact;
4. validate the manifest and crawler references;
5. validate structured JSON-LD parses on homepage and Tim page;
6. validate sitemap index/child sitemap existence and canonical consistency;
7. validate `llms.txt`/site index/authority manifest coherence;
8. run relevant navigation and reader-surface validators;
9. run the full repository quality workflow locally where feasible or verify the resulting GitHub Actions run after commits.

## 18. Rollout and indexing

Deployment completion does not mean immediate search visibility.

After a green deploy:

- verify the final public URLs and final `robots.txt`/sitemaps rather than source-tree files alone;
- submit or resubmit the canonical sitemap through Google Search Console if the user has access;
- request recrawl/indexing for the homepage and Tim Dooley canonical page when useful;
- submit the sitemap in Bing Webmaster Tools if the user has access;
- consider IndexNow only as a standards-based discovery accelerator, not as a substitute for content/canonical quality;
- monitor branded queries over time rather than expecting instant ranking changes.

## 19. Risks and mitigations

### Risk: overclaiming identity

**Mitigation:** structured data mirrors visible copy and keeps project self-description distinct from documentary/empirical status.

### Risk: SEO keyword sludge

**Mitigation:** no new thin landing pages; strengthen existing canonical pages with real explanatory content.

### Risk: machine metadata drifts from routes

**Mitigation:** generate from shared constants/configuration and add cross-file validators.

### Risk: duplicate repositories confuse authority

**Mitigation:** strengthen official repository/site references, canonical public URLs and first-party authority manifest. Do not attack or name competing repositories in primary SEO copy.

### Risk: source `robots.txt` differs from deployed artifact

**Mitigation:** validate the final `_site` artifact and require every referenced sitemap to exist there.

### Risk: custom machine files are mistaken for universal standards

**Mitigation:** treat them as supplemental discovery surfaces only; normal HTML, canonical URLs, internal links, visible content, sitemaps and structured data remain primary.

## 20. Success criteria

The pass is complete when:

1. the final deployed artifact exposes `site-authority.json`;
2. the homepage and Tim page identify the official project and canonical routes clearly;
3. Tim page visible content directly answers `Who is Tim Dooley?` in project-aware, epistemically careful language;
4. `robots.txt`, sitemap index and child sitemaps are mutually consistent in the final artifact;
5. `llms.txt`, `site-index.json` and authority manifest agree on official identity and primary routes;
6. structured data validates syntactically and mirrors visible content;
7. SEO/discovery validators fail on intentional authority/crawler regressions and pass on the finished build;
8. existing visual design and five-door homepage architecture remain intact;
9. full quality/deploy validation is green or any unrelated pre-existing failure is explicitly separated from this work;
10. GitHub About metadata follow-up is clearly documented if it cannot be changed programmatically in-session.

## 21. Governing principle

> The canonical project should become easy to discover because it is clear, useful, internally coherent, crawlable, well-linked and explicit about what it owns — not because it shouts louder than everyone else.
