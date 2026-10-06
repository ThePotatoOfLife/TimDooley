# Bible Comparator Quality Overhaul + Wave 26

Date: 2026-09-13
Status: approved design, pre-implementation

## Goal
Improve the public Bible comparator by auditing active relations, rewriting weak records, normalizing reader explanations, simplifying layer loading, and adding a new research wave only where coverage is missing.

Keep the existing reader model: one comparison at a time, filters, chronology, Bible order, counter-text view, keyboard navigation, and evidence separation.

## Reader contract
Each active comparison should make these six items clear:
1. What happened on the project side?
2. What is the biblical scene?
3. Where do they correspond?
4. Where do they differ?
5. What is the strongest supported conclusion?
6. Why is the comparison useful?

## Quality audit
Audit every relation loaded into the public browser for:
- modern-side specificity;
- biblical specificity and context;
- sequence density;
- source direction and chronology;
- provenance;
- mismatch/countertext quality;
- supported-conclusion clarity;
- reader clarity;
- duplication;
- research value.

Outcomes: retain, rewrite, merge/redirect, or downgrade/quarantine.

Weak research material may remain archived but should not rank like a strong public relation.

## Reader presentation
Normalize active cards around:
- title;
- project anchor;
- Scripture scope;
- What happened;
- Biblical scene;
- Where they correspond;
- Where they differ;
- Supported conclusion;
- Why it matters;
- provenance/supporting evidence.

Level-A dossiers keep paired-scene and expanded evidence treatment. Older records receive safe fallbacks only from existing data; missing context must be flagged rather than invented.

## Layer architecture
Replace expanding wave-specific runtime loading with one manifest-driven loader.

The manifest registers relation and fragment layers with:
- stable layer ID;
- path;
- status (`canonical`, `additive`, `research`, `quarantined`);
- precedence;
- optional owner/note.

A generic loader merges canonical + additive layers by stable IDs and preserves the existing reader data contract. Research/quarantined layers stay out of the default public corpus.

Static/no-JS compilation must consume the same manifest so static and dynamic readers expose the same active set.

## Wave 26 gap families
Mine only after the audit. Priorities:
1. developmental Father/parent imagery;
2. burden, yoke, delegation, and release;
3. throne participation versus source identity;
4. descent/emptying versus project shedding language;
5. mediation and source distinction;
6. pruning, fruit, cultivation, and judgment;
7. inheritance, adoption, and autonomous children;
8. exile, return, and restored dwelling;
9. priest/king/prophet role separation;
10. temple/body/house distinctions.

Countertexts are first-class evidence and should be promoted where they materially limit or redistribute a proposed mapping.

## Validation
High-strength or Level-A public relations must include:
- unique ID;
- project anchor;
- biblical references;
- source direction/discovery history;
- meaningful mismatch/countertext;
- strongest supported conclusion;
- comparison rationale;
- passage coverage or explicit reason for omission.

Validate manifest paths, unique layer IDs, intentional enrichments, quarantine exclusion, static/dynamic parity, and existing reader behavior.

Final implementation must pass the full repository quality workflow.

## Migration order
1. Add audit tooling and baseline the active corpus.
2. Produce a machine-readable quality report.
3. Rewrite, merge, or quarantine weak records.
4. Normalize reader presentation.
5. Add manifest + generic loader.
6. Register existing active layers and verify parity.
7. Add Wave 26 from the post-audit gap list.
8. Re-run audit and full verification.
9. Open an implementation PR with counts of retained, rewritten, merged, quarantined, and added relations.

## Non-goals
No full page redesign, no deletion of research history, no replacement of primary-source recovery with interpretation, and no collapsing distinct project roles merely because a biblical text allocates them differently.

## Success
A new reader can understand strong comparisons without prior project knowledge; strong records explain both correspondence and limitation; weak coincidences are visibly weaker; duplicates are consolidated; layer ownership is manifest-driven; static and dynamic readers match; Wave 26 fills real gaps; and the full repository checks pass.
