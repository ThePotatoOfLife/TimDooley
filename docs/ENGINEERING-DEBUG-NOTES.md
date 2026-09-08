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

## Working rule

When a failure is discovered:
1. trace it to the producer/consumer boundary;
2. identify whether the failure is acquisition, canonical ownership, generation, routing, rendering, or validation;
3. fix the underlying contract rather than the visible symptom;
4. verify through CI or an equivalent reproducible check;
5. record the root cause, exact solution, and remaining regression requirement here.
