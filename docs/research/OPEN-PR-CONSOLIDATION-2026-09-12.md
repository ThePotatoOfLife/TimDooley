# Open PR Consolidation — 2026-09-12

This file records how open branches are being absorbed into the canonical project. An open PR is an input source, not an automatic merge candidate. The consolidation target is PR #45 (`project-consolidation-2026-09-12`) and ultimately `main`.

## Classification

| PR | Subject | Disposition | Unique value / destination |
|---:|---|---|---|
| #44 | World Map unification | **base / recover fully** | Already forms the base of PR #45. `/world-map/` canonical, 3D compatibility redirect, 2D legacy archived, public links normalized. Remaining no-Atlas rename work continues in #45. |
| #43 | project operating map | **partial recovery** | Keep the useful operator/orientation documentation after rewriting stale Atlas terminology and ownership assumptions. |
| #42 | composable map registry | **partial recovery** | Recover registry-driven layer/compositor/query/country-card behavior into World Map. Do not restore World Atlas naming, duplicate public routes, or obsolete tool/Lens surfaces. |
| #40 | Bible comparator completion | **partial recovery** | Recover richer Bible reader/filter/wave/argument behavior and ownership checks. Normalize Timeline links to Timeline and keep Religion broad. Do not restore a separate validation workflow. |
| #39 | visible map metrics | **partial recovery** | Recover useful scalar/metric rendering not superseded by #42/current map. Do not restore Lens terminology as a product abstraction. |
| #38 | web audit path semantics | **partial recovery if still missing** | Recover `<base href>` / generated world-map vendor path semantics only if current `audit_web.py` still lacks them. |
| #36 | science formulation wave 014 | **recover** | Eight additive index/model records recovered into #45 at commit `c118217f`. |
| #35 | deeper 3D map / D4 / relation / religion | **partial recovery** | Recover unique observable dimensions, relation inspector contracts, religion/worldview projections and safe Axis semantics where compatible with the simplified World Map UI. |
| #33 | Door / entanglement / constraints / fate modeling | **recover selectively** | Large additive science, timeline, tradition and timeline-pack corpus. Import unique records, but rename `*-atlas.*` objects by actual function and preserve empirical/symbolic firewalls. |
| #32 | SEO architecture | **partial recovery** | Recover current-compatible SEO normalization, description enrichment and sitemap history logic if absent. Do not overwrite newer public architecture. |
| #31 | shared reader design / runtime hardening | **partial recovery** | Recover missing runtime/path/retry/site-shell fixes only. Timeline page changes are obsolete because Timeline is canonical. |
| #30 | audit + country refresh reliability | **superseded/partial** | Later #31/#32 and current cleanup supersede most of it. Recover bounded country-refresh retry only if missing. |
| #29 | Christianity / Jesus / eschatology | **recover selectively** | Recover theology research corpus, denominational matrix, scholar map, Thomas faith timeline and FAQ. Rename retired Atlas files and subordinate public Christianity material to Religion rather than creating a competing top-level owner. |
| #28 | Science model-contract overhaul | **partial recovery** | Keep `science-model-registry.json` / useful FAQ-model structure if not already present. Do not restore older Science Atlas UI/workflow; current Science portal is newer. |
| #25 | Great Book / prediction / 1987–2030 Timeline | **recover selectively** | Recover unique timeline/core/culture/FAQ records. Timeline UI itself must be reconciled with current canonical Timeline. Rename Chapter-24 Atlas record by function. |
| #23 | reader guide / homepage UI | **mostly superseded** | Earlier reader/app shell. Recover only a demonstrably missing accessibility/runtime fix. Do not overwrite current homepage. |
| #19 | app.js fix | **superseded unless unique** | One-file predecessor; compare against current app before discarding. |
| #9 | science completion corpus | **partial recovery** | Many science canon/source/index files may already exist through later work. Recover only missing unique records and audit logic. |
| #1 | early integration/text corpus repair | **mostly superseded** | Do not restore old Atlas manifests/workflows/pages. Recover only still-missing public-domain text corpus or canonical integrity records after exact comparison. |

## Temporary integration PRs

PRs #46, #47 and #48 were opened only to test whether old source branches could merge cleanly into the consolidation branch. They are dirty because the repository architecture has moved on. Their useful changes are being recovered directly into #45 instead; these temporary PRs will be closed once recovery is complete.

## Canonical rules during recovery

- `main` is the final source of truth.
- `/world-map/` is the only current geographic product. `Atlas` is not an active project primitive.
- `/timeline/` is the only current timeline product.
- `/religion/` is the broad religious inquiry owner; `/traditions/bible/` owns the deep Tim/Son ↔ Bible comparison.
- Current Science portal ownership wins over older Science Atlas UI branches.
- Archive/design history may preserve old terms, but active runtime/data/docs use precise names: map, registry, layer, model, research, comparison, index, method, programme.
- Empirical, interpretive and project-canon material remain typed rather than flattened together.
- A side branch is closed only after its still-useful material is represented in #45/`main` or explicitly documented as intentionally superseded.
