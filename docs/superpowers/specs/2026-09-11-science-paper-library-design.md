# Science Paper Library Portal Design

## Goal

Make `/science/` the single, clean public entrance to the project's scientific and mathematical work. Readers should be able to scan every substantial science document by title and abstract, filter the collection without navigating a maze of sub-sites, open a complete human-readable document, and download or inspect the canonical source record.

## Reader principle

The public science experience is a research library, not a second encyclopedia homepage and not a wall of unrelated cards. The default page should answer one question quickly: **what can I read here?**

The abstract is only a doorway. Full information belongs in the opened paper/document.

## Canonical ownership

- `knowledge/science/**/*.json` remains the canonical structured science source layer.
- `/science/` is the sole public Science hub.
- `/science/papers/<slug>/` is the generated human-readable form of a qualifying science record.
- Existing specialist readers such as `science/quantum/`, `science/spudlight/`, `science/axis-11d-sun-spiral/`, `science/celestial-particles/`, `science/vibe-gates/`, and `science/research-map/` may remain as supporting readers. They are not alternate Science homepages.
- The portal must not create a second manually maintained database of papers.

## Portal layout

The page is intentionally restrained.

1. Existing global navigation.
2. Large `SCIENCE` heading and one short sentence describing the library.
3. One search box: `Search titles, abstracts, equations, concepts…`.
4. One compact **Field** selector.
5. One compact **Document type** selector.
6. A result count.
7. One continuous list of every qualifying science document.

Each result row contains:

- document type;
- one or more field labels;
- title;
- abstract;
- at most one representative equation/formal expression when available;
- `Read full paper →` (or `Read full document →` where paper would overstate the record);
- `Download source JSON`.

No separate subject cards are required above the library. Subjects are filtering metadata, not architecture.

## Fields

Fields are multi-valued tags. A record may belong to more than one. The initial public vocabulary should stay broad enough to remain useful as the archive grows:

- Physics
- Cosmology & Astronomy
- Quantum Science
- Neuroscience
- Biology
- Chemistry
- Psychology
- Information Science
- Mathematics & Formal Systems
- Cross-disciplinary

Mathematics remains useful as a field when the document is primarily mathematical/formal. The presence of equations alone does not make a physics or neuroscience paper a Mathematics paper.

The generator should infer fields conservatively from canonical metadata, titles, topics, domain IDs, and explicit curated overrides. It must not use opaque semantic/fuzzy classification that readers cannot audit.

## Document types

Document type answers **what kind of thing am I opening?**, independently of scientific field.

- Theory / Paper
- Research Programme
- Formal Note / Framework
- Scientific Audit
- Recovery / Archaeology
- Research Record

Do not promote every JSON record to a polished scientific paper. Records whose content is historical recovery, an audit, a narrow formulation upgrade, or a research programme should be labelled accordingly.

## Qualification

The library should expose all substantial public-facing science records while avoiding administrative/index noise.

A record qualifies when it contains enough reader material to form a useful complete document: for example an abstract or substantive purpose/summary plus meaningful scientific/formal content such as model structure, equations, findings, methods, tests, limitations, references, or research questions.

Exclude pure routing/index files, ledgers whose only purpose is inventory, and tiny metadata-only records from the default paper library. They remain available in the raw source layer and may be linked from related documents.

Qualification must be deterministic and testable.

## Human-readable document renderer

Each generated `/science/papers/<slug>/` page should use the record's real structure rather than force every record into identical fake academic headings.

Preferred order when fields exist:

1. title;
2. document type, fields, date/version, status/maturity;
3. abstract;
4. research question / purpose / importance;
5. model, formulation, state space, mechanisms, or method;
6. equations and equation context;
7. derivations, findings, results, implications, or model contributions;
8. empirical programme, observables, tests, advancement gates;
9. limitations, boundaries, counter-models, falsification/failure conditions;
10. unresolved questions / completion path / next work;
11. lineage / related records;
12. external references;
13. source controls.

The renderer must omit empty sections rather than manufacture content.

Nested dictionaries and lists should render as readable subsections, definition lists, equations, bullets, tables where structurally appropriate, and compact metadata—not as raw JSON dumps.

## Equations

Equations should be first-class content on full document pages. Preserve original notation and label whether an expression is recovered/project-authored, conversation-developed, archive-generated, or an established external comparator whenever the source record carries that distinction.

The portal result row may show only one representative expression to help recognition. The complete document should show all useful equations/formulations extracted from the record.

## Source access

Every generated document includes:

- `Download source JSON` using the deployed `knowledge/science/...json` path with the HTML `download` attribute where practical;
- `View source on GitHub` linking to the canonical repository path;
- the canonical repository-relative source path in small provenance text.

The source controls are secondary to reading the paper, but always available.

## Search and filtering

Client-side filtering is enough for the portal.

Search should match deterministic generated text from:

- title;
- abstract;
- fields;
- document type;
- status/maturity;
- equations;
- selected keywords/topics.

Filters combine conjunctively: search AND selected field AND selected document type.

The default view is **all qualifying documents**. No reader should need to know which scientific department owns a paper before finding it.

## Information density

The visual rule is low eye-load:

- one result per horizontal row on desktop;
- no card masonry/grid for the main library;
- generous separators and whitespace;
- abstracts visible by default;
- advanced technical detail only inside full documents;
- no giant subject descriptions;
- no duplicated overview prose for every category;
- mobile collapses each row vertically without hiding the abstract.

## Existing generated science catalog

`scripts/build_science_catalog.py` already recursively discovers `knowledge/science/**/*.json`, extracts abstracts/equations/findings, and writes deployed science catalog material. Extend this existing generator rather than building another parallel system.

The generator becomes responsible for:

- canonical record discovery;
- deterministic qualification;
- field and type classification;
- paper metadata/catalog generation;
- full readable paper pages;
- patching/building the Science hub;
- preserving raw source access.

## Deployment

The public Pages workflow must run the science catalog/paper build after `scripts/build_site.py` and before site-shell validation/deployment, matching the existing integrity workflow sequence.

## Evidence and epistemic boundaries

The renderer must preserve the project's existing distinction between:

- defined mathematics;
- formal frameworks/toy models;
- scientific audits;
- recovered historical/project material;
- archive/conversation-developed formalizations;
- established external science;
- speculative physical proposals.

Formatting a record as a polished readable document must never silently upgrade its scientific status.

## Success criteria

- `/science/` immediately presents the complete qualifying library with abstracts.
- A reader can find all documents without navigating sub-sites.
- Field and document-type filters remain compact and optional.
- Every result opens a full readable page.
- Full pages expose the substantive record rather than a short generated snippet.
- Equations and technical material are readable and not lost.
- Every full page exposes the canonical source JSON and GitHub source.
- `knowledge/science/**/*.json` remains the only canonical paper data source.
- Adding a new qualifying science record automatically adds it to the built library without manually editing `/science/`.
- Existing epistemic/status labels survive rendering.
- GitHub Pages actually runs the science paper generator before deployment.
