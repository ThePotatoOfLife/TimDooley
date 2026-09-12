# Literature Library + Great Book Reader Design

## Goal
Create a durable `/literature/` library for long-form works and publish **The Great Book of Potato v1.2.0.0** as its first complete readable work at `/literature/great-book/`.

## Scope

### `/literature/`
- A restrained library/index, not a second archive application.
- The first work is **The Great Book of Potato**.
- The structure must allow later additions such as religious texts, historical documents, poetry, essays, Potatoist texts, and other long-form literature without redesigning the route family.
- Each work card may expose **Read** and **Download** actions.

### `/literature/great-book/`
- One continuous reading experience with one canonical URL namespace.
- Show title, edition `v1.2.0.0`, source/editorial status, **Read**, and **Download** near the top.
- A compact linked chapter index must take the reader directly to the requested chapter.
- Preserve stable chapter fragments such as `#chapter-26-8`.
- Preserve all recovered legacy chapter numbers and title aliases.
- Include low-friction chapter navigation: index, previous, next, back to top.
- Do not alter zoom, focus, or scroll except when the user explicitly follows a chapter link/hash.
- No page-turn animation, fake book chrome, or heavy search system in this release.

## Great Book source and edition rules
- Source: `The Great Book Of Potato2.odt` supplied by Tim Dooley.
- Release: `v1.2.0.0`.
- Body text is the primary editorial witness; the old manually written index is secondary evidence.
- Current recovered edition contains **171 body chapter records** and is split into **10 ordinary HTML content parts** for maintainability.
- Existing legacy numbers remain stable rather than being silently renumbered.
- The recovered legacy Chapter 20 index entry redirects to the preserved corresponding body chapter at Chapter 65.5.
- Structural proofing may repair fused headings, repeated adjacent headings, spacing, typography, and navigation.
- Do not silently upgrade speculative scientific, historical, political, satirical, theological, or mythological claims into verified external fact.
- Preserve the book's voice; this reader is an editorial presentation layer, not a doctrinal rewrite.

## Reader architecture
- `literature/index.html`: library landing page.
- `literature/great-book/index.html`: reader shell, metadata, linked index container, and download action.
- `literature/great-book/book-manifest.json`: edition metadata, 171 chapter records, legacy redirects, and ordered part list.
- `literature/great-book/parts/part-01.html` … `part-10.html`: ordinary HTML chapter content.
- `app/literature-reader.css`: shared Literature reader styling.
- `app/great-book-reader.js`: loads manifest + parts, renders index and chapter navigation, resolves hashes after content is present.
- The browser sees one continuous document even though repository storage is chunked.

## Download behavior
- Publish a downloadable `The-Great-Book-of-Potato-v1.2.0.0-reader-build.zip` beside the reader.
- The Literature card and Great Book header both expose the same download file.
- Download is optional; reading never requires downloading.

## Discovery and navigation
- Add a Literature link to the site's secondary navigation rather than replacing one of the five primary homepage doors.
- Add Literature to the archive/explore entry surface.
- Ensure the generated sitemap / machine-discovery pipeline can discover `/literature/` and `/literature/great-book/` through normal public links and canonical metadata.
- Do not expose a Great Book route before all ten parts and the complete 171-chapter manifest are present.

## Validation contract
A focused validator must fail unless:
- `/literature/index.html` exists;
- `/literature/great-book/index.html` exists and declares `v1.2.0.0`;
- the manifest contains exactly 171 chapter records;
- all ten declared parts exist;
- every manifest chapter anchor appears exactly once across the parts;
- chapter anchors are unique;
- every linked index target resolves;
- the legacy Chapter 20 redirect resolves to `chapter-65-5`;
- the download artifact exists;
- home/archive navigation exposes Literature;
- no reader code changes browser zoom or programmatically focuses chapter elements.

## Non-goals
- No full-text search engine in this release.
- No annotation/highlight accounts.
- No pagination mode.
- No attempt to standardize all future religious-text schemas before the second work exists.
