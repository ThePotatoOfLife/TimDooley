# Potato Atlas Foundation Implementation Plan — Part 2

This continues `2026-09-13-potato-atlas-foundation-implementation.md`.

### Task 4: Normalized registry builder
Create `scripts/build_atlas_registry.py` and `data/atlas-owner-seeds.json`; add CI. Discover explicit owners across `knowledge/` and `data/` while respecting `data/canonical-source-map.json`. Never auto-promote arbitrary nested JSON objects. Produce a deterministic generated registry. Commit `feat: normalize Atlas ownership registry`.

### Task 5: Swamp health audit
Create `scripts/audit_atlas_swamp.py` and `knowledge/indexes/atlas-health-policy.json`; add CI. Report duplicate owners, orphans, unresolved parents/edges, route collisions, provenance gaps and stale migration contracts with explicit severity. Commit `feat: add Atlas Swamp health audit`.

### Task 6: Shared page shell and design system
Create `knowledge/site/atlas-page-shell-contract.json`, `app/design-system.css`, `scripts/validate_atlas_page_shell.py`; modify `app/reader.css` and CI. Shell order is site shell -> North context -> header -> content -> relations -> children -> Archive depth -> footer. Add explicit CSS layers/tokens while retaining `layout-guard.css` for migration. Commit `feat: establish shared Atlas page shell`.

### Task 7: Static Atlas pages
Create `scripts/build_atlas_pages.py` and `scripts/validate_built_atlas.py`; modify `scripts/build_site.py` and CI. Write the built-output validator first. Generate `/atlas/` and `/atlas/<id>/` from reader models, not recursive JSON headings. Render one North Gate, typed relations, structural children and Archive depth. Keep pages useful without JavaScript. Commit `feat: generate canonical Atlas pages`.

### Task 8: Data-driven Views
Create `data/atlas-views.json`; modify `data/frontend-atlas-bridge.json`, builders and navigation validators. Replace exact-five-door ownership with configurable Views while preserving existing URLs. Domain surfaces reference Atlas Nodes instead of owning duplicate definitions. Move compatibility repair into build logic so validators no longer mutate output. Commit `refactor: project public rooms from Atlas views`.

### Task 9: Homepage summit
Modify `index.html`, `app/design-system.css` and `scripts/validate_site_shell.py`. Replace five-door visual ownership with Start Here, Ways Through, Atlas and Archive orientation. Reuse the shared shell and preserve stable interaction with no surprise zoom, focus, scroll or major layout shifts. Commit `feat: make homepage the Atlas summit`.

### Task 10: Deprecation ledger
Create `knowledge/indexes/atlas-deprecation-ledger.json` and `docs/ATLAS-MIGRATION.md`; modify `README.md`. Inventory legacy manifests, routing contracts, generated shells and CSS compatibility layers. Track each through `active -> compatibility -> deprecated -> removable` with replacement owner and removal preconditions. Run the complete quality workflow before removal. Commit `docs: establish Atlas deprecation ledger`.

## Final verification
All previous quality gates and all new Atlas gates must pass. Existing public routes remain functional. No canonical content is deleted simply to satisfy the new structure. North orientation, ownership and provenance are mechanically validated.
