# Root Navigation Redesign — Roadmap

Status: active implementation plan
Date: 2026-09-08

## Phase 0 — Preserve the old state

- [x] Preserve the current `main` state in `archive/pre-center-navigation-2026-09-08`.
- [x] Preserve the previous root-navigation state in `archive/pre-center-tree-2026-09-08`.
- [x] Keep the redesign isolated on `root-navigation` while it is being rebuilt.

## Phase 1 — Establish the contract

- [x] Define `ROOT -> POTATO OF LIFE -> WORLD | AXIS`.
- [x] Remove `CORE/` and `TEXTS/` as top-level concepts.
- [x] Define the center as a fixed coordinate system rather than a destination.
- [x] Define one canonical node identity with many possible navigation paths.
- [x] Define directories as generated views rather than duplicate data.
- [x] Define in-place dossier reading.
- [x] Define progressive disclosure and state persistence.

## Phase 2 — Build the center interface

- [x] Replace the homepage with the North Pole / center composition.
- [x] Keep Tim Dooley, Potato of Life, Thought and Canon directly visible at the center.
- [x] Expose only `WORLD/` and `AXIS/` as the fundamental branches.
- [x] Add expandable directory rows without full-page navigation.
- [x] Add a persistent center/path indicator.
- [x] Add expand-roots / collapse-all / reset behavior.
- [x] Add an in-place dossier surface.
- [ ] Finish keyboard tree semantics and full accessibility audit.

## Phase 3 — Make the tree data-driven

- [x] Consume the generated repository index indirectly through a dedicated presentation projection.
- [x] Create a semantic navigation manifest for the stable root vocabulary.
- [x] Build `data/root-record-index.json` from `data/repository-index.json`.
- [x] Map records into World/Axis presentation paths without creating new identities.
- [x] Keep the old Spirit/Mind/Matter filing taxonomy in the backend while the frontend uses World/Axis.
- [x] Expose legacy/deep material as secondary reading surfaces rather than primary navigation.
- [ ] Validate every generated path against actual populated records in CI.
- [ ] Add explicit exceptions for records whose presentation classification cannot be safely inferred.

## Phase 4 — In-place record reading

- [x] Add a dossier panel to the homepage.
- [x] Render selected record identity, description, type, role, family and backend class in place.
- [x] Preserve the expanded tree while the dossier changes.
- [x] Provide a canonical deep-node fallback.
- [ ] Add chronology, relationship summary and source excerpts to the dossier.
- [ ] Add expandable long-form dossier sections without leaving the center.

## Phase 5 — State and addressability

- [x] Encode selected node in the URL without replacing the center interface.
- [x] Restore selected state from the URL on reload.
- [x] Persist expansion state locally.
- [x] Support hash-driven browser navigation.
- [ ] Add explicit browser back/forward history entries for selection changes.
- [ ] Preserve useful scroll state.

## Phase 6 — Corpus classification

- [x] Preserve the existing Spirit/Mind/Matter backend classification.
- [x] Add a separate presentation classification rather than mutating canonical taxonomy prematurely.
- [ ] Audit World/Axis assignment coverage from the generated index.
- [ ] Identify records that need explicit presentation overrides.
- [ ] Add typed multi-membership where a record legitimately belongs to multiple views.
- [ ] Ensure ambiguous classification never creates duplicate canonical records.

## Phase 7 — Remove obsolete frontend structure

- [x] Remove duplicate top-level concepts from the homepage.
- [x] Make the root page a compatibility alias rather than a second navigation system.
- [ ] Retire obsolete root navigation CSS after confirming no other page depends on it.
- [ ] Remove dead links discovered during the migration.
- [ ] Keep deep pages alive even when they stop being primary navigation destinations.

## Phase 8 — Verification

- [ ] Run JSON/data integrity checks against the actual generated index.
- [ ] Run source-of-truth and duplication audits.
- [ ] Run route validation.
- [ ] Run the complete site build.
- [ ] Run stability audit.
- [x] Update site-shell validation to understand the special center page.
- [ ] Test the homepage with an empty generated index and a populated index.
- [ ] Test mobile behavior.
- [ ] Test keyboard navigation and screen-reader semantics.
- [ ] Test large record counts for performance.
- [ ] Test URL restoration and local state restoration.

## Phase 9 — Migration cleanup

- [ ] Compare old and new navigation trees.
- [ ] Confirm that no meaningful backend collection became inaccessible.
- [ ] Confirm that no record was duplicated merely to make navigation convenient.
- [ ] Update project structure documentation to make World/Axis presentation explicit.
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
11. Backend taxonomy and presentation taxonomy remain separable.
12. A presentation path can never become a second canonical identity.
