# Root Navigation Redesign — Roadmap

Status: active implementation plan
Date: 2026-09-08

## Phase 0 — Preserve the old state

- [x] Preserve the current `main` state in `archive/pre-center-navigation-2026-09-08`.
- [x] Keep the current `root-navigation` work isolated while the redesign is rebuilt.

## Phase 1 — Establish the contract

- [x] Define `ROOT -> POTATO OF LIFE -> WORLD | AXIS`.
- [x] Remove `CORE/` and `TEXTS/` as top-level concepts.
- [x] Define the center as a fixed coordinate system rather than a destination.
- [x] Define one canonical node identity with many possible navigation paths.
- [x] Define directories as generated views rather than duplicate data.
- [x] Define in-place dossier reading.
- [x] Define progressive disclosure and state persistence.

## Phase 2 — Build the center interface

- [ ] Replace the current homepage with the North Pole / center composition.
- [ ] Keep Tim Dooley, Potato of Life, Thought and Canon directly visible at the center.
- [ ] Expose only `WORLD/` and `AXIS/` as the fundamental branches.
- [ ] Add expandable directory rows without full-page navigation.
- [ ] Add a persistent center/path indicator.
- [ ] Add expand-all / collapse-all / reset behavior.
- [ ] Add keyboard-accessible tree behavior.

## Phase 3 — Make the tree data-driven

- [ ] Consume the generated `data/repository-index.json`.
- [ ] Create a small semantic navigation manifest for the stable root vocabulary.
- [ ] Map existing repository records into World and Axis views without duplicating records.
- [ ] Expose legacy/deep material through generated record collections rather than fake hard-coded links.
- [ ] Validate that every intended collection resolves to a real page or canonical record.
- [ ] Prevent empty/fake directories.

## Phase 4 — In-place record reading

- [ ] Add a dossier panel to the homepage.
- [ ] Render a selected record's description, type, source, chronology and relationship summary in place.
- [ ] Preserve the expanded tree while the dossier changes.
- [ ] Link from the dossier to the canonical deep page only when a full reading view is genuinely useful.
- [ ] Make `node.html` the universal deep-record fallback where appropriate.

## Phase 5 — State and addressability

- [ ] Encode selected path/node in the URL without replacing the center interface.
- [ ] Restore selected state from the URL on reload.
- [ ] Persist expansion state locally.
- [ ] Support browser back/forward for selection changes.
- [ ] Preserve useful scroll state.

## Phase 6 — Corpus classification

- [ ] Audit the existing repository index against the World/Axis distinction.
- [ ] Identify records that currently sit in old `spirit/mind/matter` classifications but need a World or Axis presentation.
- [ ] Define explicit classification metadata where inference is unsafe.
- [ ] Keep the old backend classification available during migration so existing audits do not break prematurely.
- [ ] Add typed directory membership / view metadata rather than duplicating records.

## Phase 7 — Remove obsolete frontend structure

- [ ] Remove duplicate top-level navigation concepts from the homepage.
- [ ] Retire the old root menu once the new center tree covers its destinations.
- [ ] Consolidate competing navigation CSS where safe.
- [ ] Remove dead links discovered during the migration.
- [ ] Keep deep pages alive even when they stop being primary navigation destinations.

## Phase 8 — Verification

- [ ] Run JSON/data integrity checks.
- [ ] Run source-of-truth and duplication audits.
- [ ] Run route validation.
- [ ] Run site build.
- [ ] Run stability audit.
- [ ] Run site-shell validation.
- [ ] Test the homepage with an empty generated index and with a populated index.
- [ ] Test mobile behavior.
- [ ] Test keyboard navigation and screen-reader semantics.
- [ ] Test large record counts for performance.
- [ ] Test URL restoration and local state restoration.

## Phase 9 — Migration cleanup

- [ ] Compare the old and new navigation trees.
- [ ] Confirm that no meaningful backend collection became inaccessible.
- [ ] Confirm that no record was duplicated merely to make navigation convenient.
- [ ] Update project structure documentation.
- [ ] Update TODO with the new live frontier.
- [ ] Only then consider merging the redesigned branch.

## Hard constraints

1. No search-first homepage.
2. No forced page-to-page navigation for ordinary tree exploration.
3. No top-level `CORE/` branch.
4. No top-level `TEXTS/` branch.
5. No duplicate canonical records for navigation purposes.
6. No giant initial DOM containing the entire corpus.
7. No invented directories that have no actual backing content.
8. No gamified travel/progression metaphor.
9. The center remains available at all times.
10. The front page is a view of the corpus, not a separate corpus.
