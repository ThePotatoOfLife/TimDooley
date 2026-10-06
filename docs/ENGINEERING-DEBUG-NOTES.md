# Engineering Debug Notes

This file records root causes and solutions discovered during repository scans. Read it before repeating an investigation.

## 2026-09-08 — Country atlas empty observations

**Symptom:** Nation pages showed `Not yet sourced` for all headline metrics. `country-static.json` contained 194 countries with empty observations even though the canonical scope was intended to be 195.

**Root cause:** The country refresh acquisition layer could interpret an API error/malformed World Bank response as an empty result, and the refresh path could continue to write the empty projection after an earlier validation failure.

**Solution:** Move validation to the acquisition boundary. Validate canonical scope before mutation; reject malformed/API-error payloads; paginate the World Bank response explicitly; require minimum acquisition coverage; and fail closed before changing country records or the static snapshot. Preserve the previous usable snapshot on acquisition failure.

**Important architectural lesson:** Do not fill Afghanistan or another individual country as a one-off. The headline metrics are owned by canonical country observations and their generated static projection. Fix the acquisition pipeline first.

**Regression still required:** Run the country workflow and verify 195 entries plus populated observations across Afghanistan, Albania, Andorra and random countries. Add a test proving an API-error payload cannot become an empty successful dataset.

## 2026-09-08 — Pages stability audit false positives

**Symptom:** Pages build reached `scripts/stability_audit.py` and failed with four broken references such as `${recordLink(x.term)}`, `${from}`, `${to}` and `'+esc(href)+'`.

**Root cause:** The audit used an HTML `href`/`src` regex over the complete HTML document, including executable `<script>` blocks. JavaScript template literals and string concatenation were therefore interpreted as literal filesystem references.

**Solution:** Remove `<script>` and `<style>` blocks before scanning literal HTML attributes. Keep the separate JavaScript syntax/local-data checks intact. This preserves real HTML link validation without confusing runtime-generated JavaScript URLs with static paths.

**Important architectural lesson:** Fix the boundary between HTML and executable source rather than weakening the reference audit or deleting the reported strings.

**Regression still required:** Re-run Pages and confirm the stability audit reports zero false positives and allows deployment to continue to the remaining gates.

## 2026-09-08 — Canonical record routing / Maersk

**Symptom:** `repository.html` could expose a record such as `maersk`, but `node.html?id=maersk` returned `No record found`.

**Root cause:** The repository index recursively discovers record-like objects across modular domain datasets, while the node resolver historically treated a small set of files as canonical node sources. `data/north-europe-economic-network.json` legitimately owns the Maersk network record, but the frontend did not resolve an indexed `source + exact JSON path` back to that record. The index was therefore broader than the resolver.

**Solution:** Keep the domain record in its owning source file. The node route now uses the repository index as a navigation projection and follows the indexed source file plus exact JSON path when a record is not found in the legacy core sources. The canonical-source map now explicitly registers `data/north-europe-economic-network.json` as the owner of that North European economic network record family. The repository index also records an owner family and role so later routing can distinguish canonical records from enrichments, projections, relationships and research layers.

**Important architectural lesson:** A record's physical location is not the same thing as its graph position. Do not copy domain records into `data/nodes.json` merely to make a route work. Resolve the canonical owner, then resolve the exact path. Parent/child navigation should be projections over one record, not duplicate record stores.

**Regression added:** Pages now builds the canonical record registry, repository index, and source-of-truth audit before the site build. The audit verifies declared source paths, exact indexed JSON paths, ID/path consistency, and competing canonical-owner candidates.

**Remaining work:** Inspect the audit output for duplicate IDs that are legitimate overlays versus genuine competing owners; migrate stale integration references; and make canonical registry ownership decisions explicit for any family still classified as general.

## 2026-09-08 — Source-of-truth audit false positives

**Symptom:** The first CI execution of the new source-of-truth audit failed with hundreds of `duplicate canonical owner candidate` errors, including countries, graph concepts, research records and intelligence organizations. It also reported the research directories as missing and interpreted a prose stale-reference declaration as a file path.

**Root cause:** The initial audit inferred canonical authority from the repository-index record role. That role is necessarily broad because the index discovers record-like objects everywhere. Consequently, projections, schemas, graph registries and overlays were falsely treated as canonical owners. The source map also stores `known_stale_references` as documentation, not executable source declarations, and Git does not preserve empty directories such as `data/research/` or `data/expansions/`.

**Solution:** Canonical authority is now derived only from explicit `canonical_owner`/`adjacent_owner` declarations in `canonical-source-map.json`. Repository-index roles remain descriptive. Source-map validation distinguishes files, glob patterns and directories, and the stale-reference list is structured as metadata rather than a fake path. The research directory declarations were removed because there is no repository contract requiring empty directories to exist.

**Actual result:** The failed run proved the repository contains substantial intentional duplication—4,206 record-like objects across 2,874 IDs in the canonical registry—but most of those repetitions are overlays or projections rather than competing owners. The next audit pass must classify the remaining *true* owner conflicts, not treat every repeated ID as an error.

## 2026-09-08 — Potatoism integration stale references

**Symptom:** `data/potatoism-integration.json` still declared `data/potatoism-master-corpus.json` and `data/potatoism-entities.json`, files that are not present in the current repository.

**Root cause:** The integration contract survived a previous corpus restructuring while retaining the old filenames. This made the architecture describe a source-of-truth that no longer existed.

**Solution:** The integration contract now points to `data/potatoism-dossiers.json` for canonical readable entities and `data/potatoism-canonical-corpus.json` for project-canon source material, while retaining deep layers, glossary and public observations as subordinate layers. The old filenames are no longer referenced.

## Working rule

When a failure is discovered:
1. trace it to the producer/consumer boundary;
2. identify whether the failure is acquisition, canonical ownership, generation, routing, rendering, or validation;
3. fix the underlying contract rather than the visible symptom;
4. verify through CI or an equivalent reproducible check;
5. record the root cause, exact solution, and remaining regression requirement here.
