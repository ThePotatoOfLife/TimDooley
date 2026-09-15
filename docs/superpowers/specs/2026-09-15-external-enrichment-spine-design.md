# External Enrichment Spine — Design

**Date:** 2026-09-15  
**Status:** Approved architectural design under refinement; implementation not yet started  
**Repository:** `ThePotatoOfLife/TimDooley`

## Purpose

Build one durable path for mining high-value information outside the repository and using it to deepen existing canonical knowledge without creating parallel truth systems, shallow scraper dumps, runtime dependencies on third-party APIs, or untraceable claims.

The External Enrichment Spine operationalizes the project’s existing claim lifecycle:

`source → retrieval → raw observation → normalization → identity resolution → classification → promotion candidate → canonical-owner review/promotion → reader/map/story projection → contradiction/revision → refresh`

Outside data is evidence first. It does not become project canon merely because an adapter retrieved it.

## Design principles

1. **Thicken existing owners before creating new ones.** External data should enrich canonical records, graphs, timelines, evidence ledgers, readers, and maps already owned by the project.
2. **Relationship-first.** Prefer sources that expose typed relationships, flows, provenance, dates, amounts, or identities over sources that provide only descriptive prose.
3. **Raw and promoted layers remain distinct.** Store source-native identifiers and retrieval metadata separately from normalized project objects.
4. **Identity resolution is explicit.** Never silently merge a company, institution, person, paper, country, text, or work solely because labels resemble one another.
5. **Source semantics survive normalization.** A GLEIF accounting-consolidation parent is not automatically beneficial ownership; a Crossref affiliation string is not automatically proof of current employment; a FIGARO sector flow is not a firm-to-firm supply contract; symbolic comparison is not historical dependency.
6. **Source competence is scoped.** No source is globally “authoritative.” A source can be strong for one field and inappropriate for another.
7. **Licensing is a first-class field.** Every source adapter records reuse terms, attribution requirements, redistribution constraints, and retrieval method.
8. **Refresh follows volatility.** Static public-domain texts are append-only/versioned; procurement and entity data can refresh frequently; scholarly metadata and macroeconomic observations refresh on source-appropriate cadences.
9. **No credential requirement for the first implementation slice.** Prefer open endpoints and downloads that can run reproducibly. Credentialed sources can be added later behind optional adapters.
10. **No automatic theological validation.** Empirical datasets can contextualize historical, scientific, cultural, or world-system claims, but do not prove or disprove Potatoverse theology by category error.
11. **No mass ingestion merely because a source is large.** Start with bounded pilots that prove identity, provenance, normalization, promotion, and public usefulness.
12. **Adapters never write canon.** Retrieval and normalization code may emit candidates; only the promotion layer can enrich a canonical owner.
13. **Public pages never depend on live external APIs.** External retrieval happens in research/build tooling; the deployed site consumes validated same-origin outputs.

## Existing architecture this extends

The spine integrates with, rather than replaces:

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

### Canonical ownership boundaries

The project already has several source-related layers. They must remain distinct:

- **`knowledge/indexes/source-index.json`** remains the canonical **claim/provenance navigation layer**. It answers: what evidence class supports a claim, where is the source, what is missing, what contradicts it, and what canonical owner uses it?
- **`data/research.json`** remains an existing domain-level empirical **source + fact ledger**. It is not immediately rewritten or deleted. The enrichment spine should be able to feed or eventually supersede parts of it through an explicit migration, not a flag-day replacement.
- **`data/country-source-registry.json`** remains the country-domain **coverage/selection registry**. It should reference global external source IDs rather than define competing source identities forever.
- **`data/indicator-source-matrix.json`** remains the metric-to-source selection layer and should also reference the global source IDs.
- **New `data/external-source-registry.json`** becomes the single canonical machine-facing identity for external providers, datasets, APIs, libraries and registries used by adapters.

The source index and external source registry therefore answer different questions:

`source-index = what supports this claim?`

`external-source-registry = what is this external provider/dataset, how may we retrieve it, what is it competent to establish, and what adapter owns it?`

No second global source registry should be created later under another name.

## Architecture

### 1. Global external source registry

Canonical path:

`data/external-source-registry.json`

A source record exists before an adapter is allowed to create promotion candidates from that source.

Minimum shape:

```json
{
  "id": "crossref",
  "name": "Crossref REST API",
  "domains": ["scholarly-metadata"],
  "source_class": "scholarly-infrastructure-metadata",
  "competence_scope": [
    "registered DOI identity",
    "publisher-deposited bibliographic metadata",
    "registered relations and updates when supplied"
  ],
  "not_competent_for": [
    "proving the scientific conclusions of a paper",
    "proving an author's current institutional employment"
  ],
  "homepage": "https://www.crossref.org/",
  "access": "public-api",
  "authentication": "none",
  "license_or_reuse": "record source-specific field restrictions; do not assume abstracts are reusable merely because metadata is retrievable",
  "refresh_policy": "on-demand/periodic",
  "adapter_status": "implemented|planned|disabled",
  "adapter_owner": "scripts/enrichment/crossref.py",
  "retrieval_policy": "bounded requests, caching, backoff and identifiable client where appropriate"
}
```

Do **not** assign a single blanket `P0/P1/S1/S2` evidence class to a provider. The existing `source-index` evidence class belongs to the **claim/source use**, because one provider may be primary for identity metadata while secondary or irrelevant for a different claim.

### 2. Raw retrieval envelope

Every adapter emits source-preserving records before normalization.

```json
{
  "source_id": "crossref",
  "adapter_version": "1",
  "retrieved_at": "2026-09-15T00:00:00Z",
  "source_updated_at": null,
  "source_record_id": "10.xxxx/example",
  "source_url": "...",
  "request_key": "doi:10.xxxx/example",
  "payload_hash": "sha256:...",
  "license_note": "...",
  "raw": {}
}
```

Rules:

- preserve source-native IDs;
- preserve retrieval timestamp and source update date when supplied;
- preserve a deterministic request key;
- hash or version raw payloads when practical;
- never silently overwrite materially changed source records;
- do not store unnecessary personal data;
- do not treat web search snippets as raw source records;
- giant upstream datasets are not committed to Git merely for archival completeness;
- live API failures never delete the last known good normalized record.

For the first slice, raw API payloads are retained only as **small test fixtures and bounded provenance evidence**, not as an ever-growing raw mirror of Crossref or ROR.

### 3. Adapter contract

Every adapter follows the same conceptual interface:

1. `retrieve(key)` → raw retrieval envelope;
2. `normalize(raw)` → deterministic source-semantic candidate objects;
3. `resolve(candidate)` → explicit identity-resolution results;
4. `validate(candidate)` → errors, warnings, ambiguity and competence checks;
5. emit promotion candidates.

Adapters **must not**:

- mutate canonical knowledge owners;
- invent missing identifiers;
- collapse source-specific relation types into generic project edges;
- infer factual conclusions beyond the source competence scope;
- expose live third-party responses directly to the public site.

Each normalized output records `adapter_version` and `normalizer_version` so a later transformation change can be distinguished from a source-data change.

### 4. Identity resolution

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

Only `exact`, `source-declared`, or reviewed `crosswalked` matches may become automatically promotable. `probable`, `ambiguous`, and `unresolved` candidates stay outside canonical owners until reviewed.

Resolution records should preserve:

- identifier type and value;
- resolution method;
- source supplying the link;
- confidence/state;
- alternative candidate IDs when ambiguous;
- review decision and date if manually resolved.

### 5. Normalized object model

Three common objects cover the first architecture: **entity link**, **observation**, and **relation**.

#### Entity link

```json
{
  "source_id": "crossref",
  "source_record_id": "10.xxxx/example",
  "source_entity": "affiliation-0",
  "project_or_external_id": "ror:XXXXXXXXX",
  "identity_state": "source-declared",
  "resolution_method": "ROR ID supplied by source"
}
```

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

Relation types retain the source’s actual semantics. Do not normalize accounting parenthood, legal ownership, beneficial ownership, operational control, procurement, citation, authorship, affiliation or input-output dependency into one generic relation such as `owns`, `connected-to`, or `depends-on`.

### 6. Candidate lifecycle

Every enrichment candidate has an explicit state:

`retrieved → normalized → resolved → promotable | review_required | rejected → promoted → superseded`

A candidate can move backward only through a recorded review/revision event.

Useful reason codes include:

- `identity_ambiguous`;
- `source_outside_competence`;
- `license_unclear`;
- `conflicts_with_existing`;
- `definition_mismatch`;
- `stale_source`;
- `insufficient_locator`;
- `duplicate_existing`;
- `privacy_boundary`;
- `manual_review_required`.

Do not hide these decisions inside logs. Promotion/rejection reasoning is part of provenance.

### 7. Promotion gate

Normalized records do not write directly into canonical files.

Promotion requires all applicable gates to pass:

1. canonical owner exists or creation is independently justified;
2. identity confidence is sufficient;
3. source identity and competence scope are known;
4. license/reuse handling is known;
5. field/edge semantics match the target owner;
6. conflicting observations are preserved rather than overwritten;
7. time/period is recorded where meaningful;
8. provenance can be traced to an exact source record/query;
9. privacy/person-level boundaries are satisfied;
10. a reader-facing projection would not overstate what the source establishes.

Avoid a single synthetic “truth score.” Promotion is a **multi-gate decision** because source quality, identity certainty, temporal fit, semantics and reuse rights are different dimensions and should remain inspectable.

Promotion may produce:

- a new evidence/source record;
- an observation attached to a country/company/paper/event;
- a typed graph edge;
- a timeline attestation;
- a contradiction/reconciliation record;
- an update to an existing source route;
- a public reader/map fact backed by the canonical owner.

### 8. Provenance lineage

Every promoted item must support this round trip:

`public statement → canonical owner → promoted record → normalized candidate → identity-resolution record → raw/source locator → external source`

Minimum lineage fields:

- source ID;
- source record ID or deterministic query key;
- source URL or locator;
- retrieved timestamp;
- source update timestamp where available;
- observation/validity period where relevant;
- adapter version;
- normalizer version;
- identity-resolution method/state;
- promotion decision/date;
- confidence/status;
- license/reuse note.

A future source or normalizer correction must be able to identify which promoted records were derived from the affected lineage.

### 9. Freshness and staleness

Temporal state must not be reduced to `accessed`.

Where available, distinguish:

- `valid_at` / `period` — when the fact is about;
- `source_updated_at` — when the external source says its record changed;
- `retrieved_at` — when the project fetched it;
- `last_verified_at` — when the project last confirmed the normalized interpretation;
- `refresh_after` — next expected refresh threshold;
- `freshness_state` — `fresh | due | stale | unknown | superseded`.

Rules:

- stale data remains visible when historically relevant, but must be labeled stale;
- refresh failure preserves the last known good record;
- source deletion does not silently delete project history;
- a changed payload that normalizes to the same semantic object is not treated as a meaningful knowledge change;
- a material normalized change creates a version/update event.

### 10. Conflict and change handling

External sources can disagree, and one source can revise itself.

Rules:

- preserve source-specific observations;
- never average incompatible definitions by default;
- distinguish dates and reporting periods;
- distinguish source revision from project reinterpretation;
- retain superseded values when historically meaningful;
- prefer primary national sources for national facts when methodology is known, while preserving international normalized series for comparison;
- expose meaningful conflicts through the project’s contradiction/reconciliation architecture;
- a correction/retraction/update relation in scholarly metadata should propagate as a status signal to the Science owner rather than silently altering the original bibliographic record.

### 11. Projection boundary

Public surfaces consume canonical/normalized same-origin data, not raw API responses.

Examples:

- Science reader → paper provenance, DOI, institution, funder, update/correction/retraction context;
- World Map → company parent edges, procurement edges, sector dependencies;
- North → measured economic/security relationships and obligations;
- Story/Timeline → first-party attestation dates and role-transition evidence;
- Religion/Philosophy → locally verified primary-text passages and relation-sequence comparisons.

External enrichment therefore **cannot freeze or break the public reader because an upstream API is slow or unavailable**. Network retrieval is a research/build concern, not a browser-runtime dependency.

### 12. Run reporting and observability

Every enrichment run should be able to report:

- requested;
- fetched;
- cache hits;
- unchanged;
- materially changed;
- normalized;
- exact/source-declared/crosswalked identities;
- ambiguous/unresolved identities;
- promotable;
- review required;
- rejected;
- promoted;
- stale retained;
- retrieval failures.

The run report is diagnostic evidence, not a new canonical knowledge owner. CI should validate shape/behavior with fixtures rather than requiring live APIs.

## Rollout

### Phase 1 — Crossref + ROR scholarly provenance

**Why first:** low integration risk, strong open metadata, direct fit with the existing Science library, and a clean test of the complete enrichment lifecycle.

Crossref retrieval is keyed primarily by DOI and should normalize, where present:

- canonical DOI;
- title;
- authors;
- publication dates;
- container/journal;
- reference identifiers;
- ORCID IDs;
- ROR IDs supplied in source metadata;
- funders;
- licenses;
- relation/update metadata;
- abstracts only when reuse is known to be safe and useful.

Crossref competence boundary:

> Crossref can establish what bibliographic metadata was registered for a DOI. It does not establish that the paper’s scientific claims are correct.

ROR resolves institution identity and supplies canonical organization metadata/crosswalks.

ROR competence boundary:

> ROR is an organization identity registry. A ROR match identifies the organization; it does not by itself prove that a person currently works there unless the relevant source explicitly supplies that affiliation.

First public payoff: selected existing Science records gain traceable scholarly provenance without hand-entering bibliographic metadata.

Representative first-slice records should be chosen by these criteria:

- already cited somewhere in `knowledge/science/`;
- stable DOI available;
- useful to more than one project record where possible;
- diverse enough to exercise authorship, institution/funder and relation/update fields;
- small enough that a human can verify every normalized field.

**Non-goals:**

- downloading arbitrary full papers;
- creating profiles of every paper author;
- building a global citation graph;
- treating a reference list as endorsement;
- live Crossref/ROR calls from the public browser.

### Phase 2 — Denmark / EU relational economy pilot

Use a bounded Danish/EU sample rather than global bulk ingestion.

Sources:

1. **GLEIF** — legal entity identity plus direct/ultimate accounting-consolidating parent relationships.
2. **Open Ownership Denmark** — beneficial-ownership data mapped from the Danish CVR into Beneficial Ownership Data Standard.
3. **TED Search API** — public procurement notices, buyers, suppliers where available, amounts, CPV sectors, NUTS geography and dates.
4. **Eurostat / FIGARO** — inter-country supply/use/input-output dependencies.

Source-semantic boundaries are mandatory:

- GLEIF parenthood is accounting-consolidation metadata, not a universal beneficial-ownership claim;
- beneficial-ownership records are not automatically operational-control claims;
- a TED notice establishes procurement/award metadata within that notice’s semantics, not proof that every contracted good/service was delivered exactly as planned;
- FIGARO expresses modeled/compiled sector and country economic relationships, not named firm-to-firm supply contracts.

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

## Storage strategy

### Repository-owned control plane

Git should contain:

- `data/external-source-registry.json`;
- schemas/contracts;
- adapters and normalization code;
- small deterministic fixtures;
- bounded normalized outputs actually used by canonical owners;
- provenance manifests/checksums;
- canonical owner updates;
- validator rules.

### Large upstream data

Examples: GLEIF bulk, FIGARO matrices.

- do not commit giant raw upstream files to Git;
- keep manifests/checksums/source metadata in the repository;
- generate bounded normalized subsets needed by the project;
- make refresh scripts reproducible;
- use source snapshots or workflow artifacts outside Git when full raw retention is required.

### Primary texts

- locally store only editions whose reuse basis is established;
- preserve original source and edition metadata;
- hash local source files;
- treat updates as new edition/version records, not silent replacements.

## Privacy and person-level boundaries

- Do not build dossiers on private individuals from incidental personal data.
- Scholarly author names/ORCIDs may be retained as bibliographic provenance without automatically creating canonical person dossiers.
- Person-level beneficial-ownership data in later phases must be deliberately public, legally reusable, materially relevant, and minimized to what is necessary for the stated graph purpose.
- Do not infer hidden ownership, wrongdoing, ideology, health, religion, or personal traits from network proximity.
- A public identifier does not automatically justify projecting all associated personal information onto the public site.

## Failure behavior

The pipeline must fail conservatively:

- network timeout → keep last good normalized data and mark refresh failure;
- source returns malformed/unexpected shape → reject new candidate, do not corrupt canonical owner;
- identifier disappears → preserve historical record and mark unavailable/superseded as appropriate;
- identity becomes ambiguous → stop automatic promotion;
- license/reuse becomes unclear → stop redistribution/promotion of affected content until reviewed;
- canonical owner is missing → require explicit owner decision rather than creating a placeholder record;
- public projection cannot prove provenance round-trip → omit the new projected fact rather than display an untraceable statement.

## Testing strategy

Every adapter must have fixture-based tests independent of live network availability.

Required contracts:

1. source-native fixture parses deterministically;
2. normalization preserves source IDs and semantics;
3. identity resolution has explicit confidence/status;
4. repeated ingestion is idempotent;
5. changed source records create updates rather than duplicate entities;
6. semantically unchanged payload changes do not create false knowledge revisions;
7. ambiguous identities do not auto-promote;
8. conflicting observations coexist;
9. source competence boundaries are enforced;
10. provenance round-trip succeeds;
11. stale-but-last-good data survives refresh failure;
12. no raw source dump is accidentally exposed in the public artifact;
13. no live network is required by the normal test suite;
14. existing repository quality/build/Pages checks remain green.

For public projections, add targeted validator assertions to existing quality gates rather than creating parallel CI workflows.

## First implementation slice

The first implementation plan covers only **Crossref + ROR** and the shared spine primitives required to support them.

Expected deliverables:

- `data/external-source-registry.json` with Crossref and ROR plus future-source stubs only where they are already part of approved project architecture;
- shared enrichment schemas for raw envelope, identity resolution, normalized candidate and provenance lineage;
- DOI canonicalization and DOI-keyed Crossref adapter;
- ROR organization resolver;
- deterministic fixture set;
- promotion-gate validator;
- bounded provenance storage for a small representative Science sample;
- enrichment of a small representative set of existing Science owners;
- public Science projection of DOI/source provenance where appropriate;
- run summary/reporting;
- documentation explaining refresh, staleness and failure behavior.

Implementation constraints:

- live source retrieval is an explicit refresh/research operation, not a requirement of ordinary CI;
- tests use committed fixtures;
- no personal email/contact is hardcoded into source clients; optional polite-pool/contact configuration must come from non-secret project configuration/environment where appropriate;
- adapters never mutate canonical owners directly;
- no new “master science file” is created merely to hold enrichment output;
- no GLEIF/TED/FIGARO ingestion enters Phase 1.

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

The architecture is successful when an external discovery can be retrieved, normalized, identity-resolved, classified, reviewed, promoted into the correct existing canonical owner, shown publicly with provenance, refreshed later without duplication, and challenged or revised without losing the source trail.

The project should end each enrichment pass with:

- more trustworthy depth per canonical record;
- stronger source traceability;
- clearer source competence boundaries;
- no duplicate source identities;
- no unjustified identity merges;
- no unnecessary raw data committed to Git;
- no new live third-party dependency in public pages;
- and at least one reader/map/research path that becomes more useful because of the enrichment.
