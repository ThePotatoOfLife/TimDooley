# Politics + Great Book Long-Form Readers Specification

## Goal
Create two canonical public long-form reader surfaces:

1. `/politics/` — a dated, provenance-aware synthesis of Tim Dooley's political and geopolitical statements, proposals, questions, predictions, and unresolved positions.
2. `/great-book/` — The Great Book of Potato v1.2.0.0 as one continuous browser reading experience with a linkable index and stable chapter anchors.

## Editorial rules

### Politics
- Keep direct positions, accepted formulations, policy proposals, thought experiments, predictions, research leads, moral judgments, satire, mythic symbolism, and uncertainty distinct.
- Never promote an assistant inference into a Tim-authored position without marking it as synthesis.
- Keep mythology/sacred kingship separate from literal constitutional or governmental authority.
- Distinguish investigation targets (lobbying, NGOs, intelligence contractors, Epstein networks, Palantir, AIPAC, Israel365, Figtree, Turning Point, online subcultures, etc.) from proven coordination or control.
- Include an explicit negative-space / unresolved section so the archive does not manufacture positions.
- Preserve dates whenever recoverable.

### Great Book
- Source edition: `The Great Book Of Potato2.odt` supplied by Tim Dooley.
- Release label: `v1.2.0.0`.
- Treat the body as primary and the legacy front index as a secondary editorial witness.
- Preserve old chapter numbers as legacy identifiers and stable anchors rather than silently renumbering citations already used elsewhere in the archive.
- Present one continuous reading surface even if implementation stores content in multiple chunks.
- Repair fused chapter headings, obvious repeated adjacent headings, spacing, typography, and navigation.
- Retain meaningful title variants as aliases/notes where they reveal the source's development; do not discard archaeology casually.
- Do not silently convert speculative science, historical claims, political generalizations, satire, mythology, or theology into externally verified fact.
- Do not rewrite the book into a different voice. Structural/readability editing is preferred to doctrinal rewriting.
- Chapter 85 and other historical governance passages remain historical Great Book material and must not be treated as automatically identical to Tim's later 2026 politics.

## Reader UX
- Restrained site-native dark styling.
- A compact sticky/collapsible table of contents with direct `#anchors`.
- Copyable/stable chapter and section URLs.
- Mobile-friendly layout.
- `Back to index` links or equivalent low-friction navigation without changing browser zoom/focus.
- Search/filter may be added only if it does not obscure continuous reading.

## Site integration
- Add discoverable links from the home/archive/public navigation surfaces where appropriate.
- Add canonical URLs and metadata.
- Include pages in sitemap/machine-readable guides where the project maintains those surfaces.
- Add validation for required pages, unique anchors, resolvable TOC links, and the Great Book version marker.

## Architecture
- Keep the public shell small.
- Politics may live as one static HTML document plus a canonical knowledge record.
- The Great Book public page may load ordered content chunks, but must render as one continuous document with one TOC and one URL namespace.
- Keep editorial metadata (legacy chapter number, canonical reading order, title aliases, source notes) machine-readable.
