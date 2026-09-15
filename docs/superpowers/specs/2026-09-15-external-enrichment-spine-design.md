# External Enrichment Spine — Design

**Date:** 2026-09-15  
**Status:** Approved architectural design; implementation not yet started  
**Repository:** `ThePotatoOfLife/TimDooley`

## Purpose

Build one durable path for mining high-value information outside the repository and using it to deepen existing canonical knowledge without creating parallel truth systems, shallow scraper dumps, or untraceable claims.

The External Enrichment Spine operationalizes the project’s existing claim lifecycle:

`source → retrieval → raw observation → identity resolution → classification → normalized observation/relation → canonical-owner candidate → review/promotion → reader/map/story projection → contradiction/revision → refresh`

Outside data is evidence first. It does not become project canon merely because an adapter retrieved it.

## Design principles

1. **Thicken existing owners before creating new ones.** External data should enrich canonical records, graphs, timelines, evidence ledgers, readers, and maps already owned by the project.
2. **Relationship-first.** Prefer sources that expose typed relationships, flows, provenance, dates, amounts, or identities over sources that provide only descriptive prose.
3. **Raw and promoted layers remain distinct.** Store source-native identifiers and payload metadata separately from normalized project objects.
4. **Identity resolution is explicit.** Never silently merge a company, institution, person, paper, country, text, or work solely because labels resemble one another.
5. **Source semantics survive normalization.** A GLEIF accounting-consolidation parent is not automatically beneficial ownership; a Crossref affiliation string is not automatically an institution identity; a symbolic comparison is not a historical dependency.
6. **Licensing is a first-class field.** Every source adapter records reuse terms, attribution requirements, redistribution constraints, and retrieval method.
7. **Refresh follows volatility.** Static public-domain texts are append-only/versioned; procurement and entity data can refresh frequently; scholarly metadata and macroeconomic observations refresh on source-appropriate cadences.
8. **No credential requirement for the first implementation slice.** Prefer open endpoints and downloads that can run in CI or a reproducible local process. Credentialed sources can be added later behind optional adapters.
9. **No automatic theological validation.** Empirical datasets can contextualize historical, scientific, cultural, or world-system claims, but do not prove or disprove Potatoverse theology by category error.
10. **No mass ingestion merely because a source is large.** Start with bounded pilots that prove identity, provenance, normalization, promotion, and public usefulness.

## Existing architecture this extends

The spine should integrate with, rather than replace:

- `knowledge/guides/project-growth-compass.json`
- `knowledge/indexes/source-index.json`
- `knowledge/indexes/inference-ledger.json`
- `knowledge/indexes/context-graph.json`
- `knowledge/timeline/developmental-genealogy.json`
- `knowledge/reader/tim-dooley-question-index.json`
- `data/backend.json`
- `data/country-source-registry.json`
- `data/indicator-source-matrix.json`
- `data/research.json`
- `data/graph-registry.json`
- `data/potatoism-concept-registry.json`
- `knowledge/economics/north-obligation-graph-schema.json`
- `data/full-text-coverage.json`
- `data/religious-text-library.json`

The repository’s current doctrine — inspect, consolidate, deepen, connect, expose, verify, prune — remains the governing editorial rule.

## Architecture

### 1. Source registry

A machine-readable source record describes each external source before any adapter is allowed to promote data from it.

Minimum fields:

```json
{
  "id": "crossref",
  "name": "Crossref REST API",
  "domains": ["scholarly-metadata"],
  "source_class": "external-primary-metadata",
  "homepage": "https://www.crossref.org/",
  "access": "public-api",
  "authentication": "none",
  "license_or_reuse": "metadata largely open; preserve field-specific exceptions",
  "refresh": "on-demand/periodic",
  "adapter_status": "implemented|planned|disabled",
  "retrieval_policy": "polite rate limits; identify client where appropriate"
}
```

This may extend `data/country-source-registry.json` or become a broader canonical registry if the country registry is too domain-specific. There must still be one canonical source identity per external source.

### 2. Raw retrieval envelope

Every adapter emits source-preserving records before normalization.

```json
{
  "source_id": "crossref",
  "retrieved_at": "2026-09-15T00:00:00Z",
  "source_record_id": "10.xxxx/example",
  "source_url": "...",
  "payload_hash": "sha256:...",
  "license_note": "...",
  "raw": {}
}
```

Rules:

- preserve source-native IDs;
- preserve retrieval timestamp;
- hash or version raw payloads when practical;
- do not silently overwrite materially changed source records;
- do not store unnecessary personal data;
- do not treat web search snippets as raw source records.

### 3. Identity resolution

Normalize into project identities using explicit crosswalks.

Priority identifiers:

- country: ISO 3166 / existing canonical country ID;
- company/legal entity: LEI where available, plus national registration identifiers as secondary keys;
- institution: ROR;
- scholarly work: DOI;
- person: ORCID where supplied and appropriate, otherwise source-qualified identity only;
- procurement buyer/supplier: source identifier + resolved LEI/national registration where possible;
- canonical text/work: project corpus ID + edition/translator/language identifiers;
- project concept/event: existing canonical repository IDs only.

Identity states:

`exact`, `source-declared`, `crosswalked`, `probable`, `ambiguous`, `unresolved`.

Only `exact`, `source-declared`, or reviewed `crosswalked` matches may automatically enrich canonical owners. `probable` and `ambiguous` records stay in evidence/review layers.

### 4. Normalized observation and relation model

Two common objects are sufficient for the first architecture.

#### Observation

```json
{
  "subject_id": "country:DK",
  "metric": "government-debt-gdp",
  "value": 27.9,
  "unit": "percent-gdp",
  "period": "2025-Q4",
  "source_id": "eurostat",
  "source_record_id": "...",
  "retrieved_at": "...",
  "confidence": "direct",
  "epistemic_class": "empirical"
}
```

#### Relation

```json
{
  "from": "lei:CHILD",
  "to": "lei:PARENT",
  "type": "direct-accounting-consolidating-parent",
  "direction": "from-child-to-parent",
  "valid_from": null,
  "valid_to": null,
  "amount": null,
  "geography": null,
  "source_id": "gleif",
  "source_record_id": "...",
  "confidence": "source-declared",
  "epistemic_class": "empirical"
}
```

The relation type must retain the source’s actual semantics. Do not normalize several legally distinct ownership/control relationships into generic `owns`.

### 5. Promotion layer

Normalized records do not write directly into canonical files.

Promotion checks:

1. canonical owner exists or is justified;
2. identity confidence is sufficient;
3. source class and license are known;
4. field/edge semantics match the target owner;
5. conflicting observations are preserved rather than overwritten;
6. time/period is recorded where meaningful;
7. provenance can be traced back to the exact source record;
8. a reader-facing projection would not overstate what the source establishes.

Promotion may produce:

- a new evidence/source record;
- an observation attached to a country/company/paper/event;
- a typed graph edge;
- a timeline attestation;
- a contradiction/reconciliation record;
- a public reader/map fact backed by the canonical owner.

### 6. Projection layer

Public surfaces should consume canonical/normalized data, not raw API responses.

Examples:

- Science reader → paper provenance, DOI, institution, funder, correction/retraction context;
- World Map → company parent edges, procurement edges, sector dependencies;
- North → measured economic/security relationships and obligations;
- Story/Timeline → first-party attestation dates and role-transition evidence;
- Religion/Philosophy → locally verified primary-text passages and relation-sequence comparisons.

## Rollout

### Phase 1 — Crossref + ROR scholarly provenance

**Why first:** low integration risk, strong open metadata, direct fit with the existing Science library, and a clean test of the complete enrichment lifecycle.

Crossref adapter should retrieve by DOI and normalize, where present:

- DOI;
- title;
- authors;
- publication dates;
- container/journal;
- references;
- ORCID IDs;
- ROR IDs supplied for affiliations/funders;
- funders;
- licenses;
- relation/update metadata;
- abstracts only when reuse is safe and useful.

ROR resolves institutional identity and supplies canonical organization metadata/crosswalks.

First public payoff: Science records gain traceable scholarly provenance without hand-entering bibliographic metadata.

**Non-goal:** downloading arbitrary full papers.

### Phase 2 — Denmark / EU relational economy pilot

Use a bounded Danish/EU sample rather than global bulk ingestion.

Sources:

1. **GLEIF** — legal entity identity plus direct/ultimate accounting-consolidating parent relationships.
2. **Open Ownership Denmark** — beneficial-ownership data mapped from the Danish CVR into Beneficial Ownership Data Standard.
3. **TED Search API** — public procurement notices, buyers, suppliers where available, amounts, CPV sectors, NUTS geography and dates.
4. **Eurostat / FIGARO** — inter-country supply/use/input-output dependencies.

Pilot questions:

- Which Danish legal entities can be resolved across LEI, CVR-derived beneficial ownership, and TED?
- Which public buyers award contracts to which suppliers, in what sector, geography and period?
- Which supplier groups have identifiable parent relationships?
- Which industries depend on imported inputs from which countries according to FIGARO?
- Can the existing North obligation/dependency graph represent all four source families without semantic collapse?

**Non-goal:** millions of entities or exhaustive EU procurement in the first slice.

### Phase 3 — Comparative primary-text expansion

Extend the local full-text corpus one legally verified edition at a time.

Priority candidates already identified by the repository:

- Iliad;
- Odyssey;
- Kalevala;
- Quran public-domain study translation where redistribution is legally appropriate;
- Bhagavad Gita public-domain edition where appropriate;
- further Norse sagas;
- Gilgamesh and other comparative works only after edition rights/provenance are checked.

Each corpus record must preserve:

- work;
- tradition;
- original language;
- edition;
- translator/editor;
- publication year;
- source URL;
- copyright/reuse basis;
- local file hash;
- structural divisions;
- search/read/TTS readiness.

The comparative engine should compare **relation sequences and mismatches**, not treat keyword overlap as evidence of identity or influence.

Because Project Gutenberg’s determinations are U.S.-specific, redistribution decisions must consider the project’s actual publication context and the rights status of the particular edition. Do not bulk-copy Project Gutenberg merely because the site hosts an edition.

### Phase 4 — Story / Timeline primary-source archaeology

This phase mines public first-party Tim Dooley / Potato of Life artifacts for documentary chronology.

Target objects:

- public posts;
- videos;
- stream descriptions/transcripts where legitimately available;
- public images/artifacts with dates;
- repository commits/documents that establish terminology or interpretation changes.

Output unit:

```text
artifact → timestamp → exact attestation → concept/role → context → later reinterpretation → confidence
```

Priority questions:

- earliest attestation for Potato of Life;
- earliest Father role;
- earliest Door/Ladder/Axis/North usages;
- chronology of Son/death/crucifixion language;
- April 2025 reinterpretation boundary;
- February 2026 North crystallization;
- later reinterpretations that must not be backdated.

Third-party hostile or derivative archives may identify leads, but must not silently become primary evidence for Tim’s own statements.

## Later adapters

After the spine is proven, likely high-value adapters include:

- SIPRI — military expenditure and arms/security context;
- UNHCR — displacement/refugee flows;
- WIPO — patents and innovation;
- OECD — productivity, tax, labour, health, education and governance;
- IMF — macroeconomics, fiscal, debt, external accounts and forecasts;
- ILO — labour and social protection;
- WTO / UNCTAD — trade, tariffs, FDI, shipping and commodities;
- WHO — health systems and mortality;
- ITU — digital connectivity;
- IRENA / IEA — energy capacity, generation and security;
- OpenAlex — publication/institution/citation graphs;
- Wikidata / library authority systems — identity crosswalks, not final truth authorities;
- Europeana — cultural objects if an API credential is later justified.

Each must pass the same source-registry, identity, semantics, provenance and promotion rules.

## Refresh and storage strategy

### Small/on-demand APIs

Examples: DOI metadata, individual organization resolution.

- retrieve on demand or in bounded batches;
- cache normalized results with retrieval timestamps;
- preserve source IDs so records can refresh idempotently.

### Large downloadable datasets

Examples: GLEIF bulk, FIGARO matrices.

- do not commit giant raw upstream files to Git;
- keep manifests/checksums/source metadata in the repository;
- generate bounded normalized subsets needed by the project;
- make refresh scripts reproducible;
- use source snapshots or artifacts outside Git when full raw retention is required.

### Primary texts

- locally store only editions whose reuse basis is established;
- preserve original source and edition metadata;
- hash local source files;
- treat updates as new edition/version records, not silent replacements.

## Provenance contract

Every promoted fact or edge must be traceable to:

`canonical object → normalized record → raw/source record → external source`

Minimum provenance fields:

- source ID;
- source record ID or stable query key;
- source URL;
- retrieved timestamp;
- observation/validity period where relevant;
- transformation/normalization version;
- identity-resolution method;
- confidence/status;
- license/reuse note.

## Conflict handling

External sources can disagree.

Rules:

- preserve source-specific observations;
- never average incompatible definitions by default;
- distinguish dates and reporting periods;
- distinguish accounting parenthood, legal ownership, beneficial ownership, operational control and procurement relationships;
- prefer primary national sources for national facts when methodology is known, while preserving international normalized series for comparison;
- expose meaningful conflicts through the project’s contradiction/reconciliation architecture.

## Safety, privacy and scope boundaries

- Do not build dossiers on private individuals from incidental personal data.
- Restrict person-level economic graph ingestion to data that is deliberately public, legally reusable, materially relevant and necessary for the project’s stated purpose.
- Do not infer hidden ownership or wrongdoing from network proximity.
- Do not convert absence of data into evidence of absence unless the source semantics justify it.
- Do not scrape services in violation of their access policies.
- Do not copy copyrighted modern translations merely because they are readable online.
- Do not allow an external source adapter to bypass the project’s epistemic classification system.

## Testing strategy

Every adapter must have fixture-based tests independent of live network availability.

Required contracts:

1. source-native fixture parses deterministically;
2. normalization preserves source IDs and semantics;
3. identity resolution has explicit confidence/status;
4. repeated ingestion is idempotent;
5. changed source records create updates rather than duplicate entities;
6. ambiguous identities do not auto-promote;
7. conflicting observations coexist;
8. provenance round-trip succeeds;
9. no raw source dump is accidentally exposed in the public artifact;
10. existing repository quality/build/Pages checks remain green.

For public projections, add targeted validator assertions rather than creating parallel CI workflows.

## First implementation slice

The first implementation plan should cover only **Crossref + ROR** and the shared spine primitives required to support them.

Deliverables:

- external-source registry extension/owner;
- raw retrieval envelope schema;
- normalized observation/entity-link schema sufficient for scholarly metadata;
- DOI-based Crossref adapter;
- ROR organization resolver;
- fixture tests;
- provenance storage;
- enrichment of a small representative set of existing Science paper records;
- public Science projection of the new provenance where appropriate;
- documentation explaining refresh and failure behavior.

Explicitly defer GLEIF/TED/FIGARO ingestion until the first slice proves the architecture.

## Authoritative external references used for this design

- Crossref REST API: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- Crossref access/authentication: https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/
- GLEIF Level 2 / Who Owns Whom: https://www.gleif.org/en/lei-data/access-and-use-lei-data/level-2-data-who-owns-whom
- GLEIF data access: https://www.gleif.org/en/lei-data/access-and-use-lei-data
- TED Search API: https://docs.ted.europa.eu/api/latest/search.html
- Eurostat FIGARO database: https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/database
- Open Ownership Denmark: https://www.openownership.org/en/map/country/denmark/
- Project Gutenberg license guidance: https://www.gutenberg.org/policy/license
- Project Gutenberg permission guidance: https://www.gutenberg.org/policy/permission

## Success criteria

The architecture is successful when an external discovery can be ingested, identified, classified, normalized, reviewed, promoted into the correct existing canonical owner, shown publicly with provenance, refreshed later without duplication, and challenged or revised without losing the source trail.

The project should end each enrichment pass with **more trustworthy depth per canonical record**, not merely more downloaded data.
