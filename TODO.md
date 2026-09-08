# TODO — The Potato of Life / TimDooley

## Current priority — make the repository load, make the data coherent, then deepen what already exists

The repository is now large enough that **duplication, orphaned layers, shallow mirrors, route failures and competing canonical sources are a bigger risk than simply adding more files**. Work in this order:

1. **P0 — site actually loads and CI deploys**
2. **P0 — canonical data ownership and duplicate-layer audit**
3. **P1 — deepen high-connectivity existing records**
4. **P1 — make Culture/Subculture/Sektur/Swamp analytically useful**
5. **P1 — improve population/geography/network extraction**
6. **P2 — expand long-form research and project canon**
7. **P2 — cosmetic/UI refinement after the data contracts are stable**

## Immediate progress

- [x] Fix the build-site regular-expression escaping that prevented canonical headers from being injected during the Pages build.
- [x] Add `scripts/build_canonical_record_registry.py` to inventory record-like IDs across JSON layers and expose duplicate-ID ownership candidates.
- [ ] Run the registry generator in CI and commit its generated `data/canonical-record-registry.json` report.
- [ ] Use the registry to assign one canonical owner to every important ID, then preserve derived, research and archive views as references.

## Next implementation sequence

1. Verify the current Pages run completes successfully.
2. Run the canonical registry against the complete data tree.
3. Add duplicate-ID, alias-collision and missing-reference failures to the audit suite.
4. Repair stale Potatoism integration paths.
5. Resolve the country 194/195 discrepancy.
6. Build canonical joins for religion, extremism, intelligence/security and Swamp.
7. Promote high-connectivity shallow records into full dossiers.
8. Finish the Culture/Subculture analytical outputs.

## Canonical ownership rule

Every important record must have one canonical owner. Other files may be identity indexes, schemas, observations, enrichments, derived graph projections, research, symbolic interpretation or archives, but they must identify their role and point back to the canonical record. No duplicate copy should be deepened merely to increase word count.

## Depth rule

Every substantial record answers: **What is this thing? What is its context? How does it work? What does it participate in? What evidence supports it? What remains uncertain?** Graph edges never substitute for an independent dossier.

## Deployment rule

A change is not complete until the source audit passes, the static build succeeds, the shell audit passes, the Pages workflow succeeds, and the deployed pages are checked for the changed behavior.

## Research principle

**See the connections. Read the substance.** Every file must have a purpose, every important record must stand independently, and every relationship must make it possible to answer a question, trace a mechanism, compare systems, locate a population, follow propagation, or understand how one part of the world changes another.
