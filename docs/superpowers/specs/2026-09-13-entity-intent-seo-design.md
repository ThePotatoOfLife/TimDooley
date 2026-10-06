# Entity + Intent SEO Overhaul — Design

**Date:** 2026-09-13
**Status:** Approved for implementation

## Goal

Make the public Tim Dooley / Potato of Life archive technically excellent for crawling while also giving search engines a clear entity model, distinct search intent for each canonical page, strong first-party provenance signals, useful internal topical relationships, and high-quality social/search metadata.

## Principles

1. SEO remains a projection of the real archive. Do not create thin keyword pages or duplicate canonical content.
2. Every indexable page gets one clear search intent and one self-canonical URL.
3. Tim Dooley, The Potato of Life, the archive, and individual research topics must not be flattened into one generic page type.
4. Structured data describes visible page content only. It must not invent biography, credentials, affiliation, authorship, or identity claims.
5. Existing reader navigation remains authoritative. SEO helpers must not clutter or replace the five-door reader structure.
6. First-party source authority, evidence boundaries, chronology, and canonical owners should reinforce discoverability.
7. Internal links should follow real topical relationships, not keyword frequency.

## Architecture

Keep `scripts/optimize_seo.py` as the final site-wide SEO projection step. Add a focused strategy module that classifies built pages by route/content and returns intent metadata, schema type, entity/topic relationships and related canonical destinations. The optimizer consumes this strategy after all content builders have run.

The strategy layer will distinguish at least:

- home / archive entity root
- Tim Dooley profile and identity readers
- Potato of Life / Potatoism concept pages
- Bible / comparative religion research
- North / Axis / geopolitical programme pages
- science portal and scientific paper pages
- timeline / chronology pages
- evidence / source-authority pages
- question pages
- record / source-owner pages
- generic support pages

## Search metadata

For curated pages with strong existing titles/descriptions, preserve good copy. For generic or weak metadata, generate intent-aware replacements. Prefer query-descriptive titles such as `Tim Dooley — Biography, Timeline, Ideas & Evidence` or `Tim Dooley and the Bible — Biblical Parallels, Sources & Countertexts` over generic archive labels.

Avoid keyword stuffing and repeated site-name suffixes. Titles should normally stay under ~70 characters; descriptions should normally stay under ~170 characters while remaining natural.

## Structured data

Keep global `WebSite` and `BreadcrumbList` markup. Add page-appropriate primary types:

- homepage: `WebSite` + `CollectionPage`
- Tim profile readers: `ProfilePage` with `mainEntity` as a conservative `Person` object only where the page visibly presents Tim as a person/topic; do not encode spiritual claims as factual properties
- research/topic readers: `Article` or `CollectionPage` depending on page structure
- timeline: `CollectionPage`
- question pages: `WebPage`; use `FAQPage` only for pages that visibly contain multiple question-answer pairs meeting schema rules
- science papers: `ScholarlyArticle` only where the built page is actually a paper/document; otherwise `Article`
- source/evidence pages: `Article` or `CollectionPage`

Use `about`, `mainEntity`, `isPartOf`, and `breadcrumb` to connect pages to the archive and topic entities. Do not add unsupported `sameAs` URLs.

## Social metadata

Every indexable page should have Open Graph and Twitter metadata. Add `og:image` and `twitter:image` only when a stable site-owned image exists; otherwise do not fabricate one. Use `summary_large_image` only when an image is actually present.

## Internal topical links

Add a compact build-time related-context block only where the page does not already provide strong equivalent navigation. Links come from an explicit route relationship map, not keyword scraping. Examples:

- Tim profile → timeline, evidence, public witness, source authority
- Bible → religion, timeline, source authority, Tim biblical-case reader
- North → world map, timeline, philosophy/religion where relevant
- science → research map, model-testing/material source surfaces

The block must remain secondary to reader content and must not create circular link spam.

## Sitemaps and indexing

Continue deriving sitemaps from final built self-canonical indexable HTML. Keep question, record and science-paper child sitemaps. Preserve source-backed `lastmod` dates. Noindex redirects/helpers remain excluded.

## Quality diagnostics

Expand the SEO report to include:

- intent classification coverage
- primary schema-type coverage
- image/social-card coverage
- weak/generic title count
- weak/generic description count
- duplicate title/description groups
- pages with related-context links
- entity-root linkage coverage

CI should fail on missing canonical/metadata/structured-data contracts, but image absence remains a warning when no stable asset exists.

## Non-goals

- no mass-generated keyword landing pages
- no hidden SEO text
- no fabricated author credentials or organization/person relationships
- no claims that project mythology is external fact
- no public navigation redesign
- no dependence on JavaScript for canonical metadata or structured data
