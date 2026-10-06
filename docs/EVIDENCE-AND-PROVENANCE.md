# Evidence and Provenance Standard

This repository deliberately contains different kinds of material. The system only becomes useful at scale if those kinds remain distinguishable.

## Evidence classes

### Observed
Directly supported by a reliable primary or authoritative source.

**Example:** Eurostat reports France government debt at 115.6% of GDP at the end of 2025.

### Calculated
A transparent derivation from observed values.

**Example:** calculating the percentage-point difference between two published debt ratios.

### Estimated
A modelled or approximate value where complete observation is unavailable.

**Requirement:** assumptions must be stated.

### Scenario
A conditional projection.

**Example:** “If expenditure grows 1 percentage point slower than nominal GDP, debt dynamics could improve.” This is not a forecast until a complete model and assumptions are supplied.

### Interpretation
An analytical reading of evidence.

Interpretation can be rigorous, but it remains distinct from observation.

### Historical
A claim about the past supported by documentary or scholarly evidence.

### Mythological
A canonical element of the Potatoverse. Its validity is internal to the mythic framework and it must not be presented as empirical proof.

### Creative
A deliberate artistic construction: speech, story, poem, song, image, game or other work.

### Open question
A claim or relationship requiring further research.

## Provenance record

The preferred record is:

`claim → source → publication/access date → jurisdiction → evidence class → confidence → calculation/method → notes`

For graph edges:

`source node → relationship → target node → evidence → date → source → confidence`

## Confidence

Use confidence as a description of evidence quality, not truth itself:

- **High:** authoritative source or multiple strong independent sources.
- **Medium:** credible evidence with limitations or incomplete coverage.
- **Low:** preliminary evidence, uncertain interpretation or weak source base.
- **Framework:** intentionally assigned to a conceptual/mythological relationship rather than an empirical probability.

## Source hierarchy

For empirical economics and public policy, prefer:

1. Official statistical agencies and primary datasets
2. EU institutions and national governments
3. Central banks and regulators
4. International organizations with transparent methodology
5. Peer-reviewed research and established academic sources
6. Reputable specialist research
7. Journalism for discovery and context, followed by primary-source verification

Search snippets are leads, not evidence.

## Versioning

When a major claim changes, preserve the old value and record the revision. Do not silently rewrite the past.

## Separation rule

A symbolic relationship may generate a research question. A research result may influence a philosophical interpretation. Neither automatically validates the other.

## Current factual baseline

The current website and seed data use Eurostat's Q4 2025 government-finance release for the initial France/Belgium/Denmark/EU debt baseline and European Commission material for the single market and Energy Union descriptions.

## Review protocol

Before publishing a significant empirical relationship:

- identify the exact claim;
- find the strongest available source;
- record the source date;
- record the jurisdiction;
- classify the evidence;
- preserve the original number or quotation needed to reproduce the conclusion;
- record calculations separately;
- identify uncertainty;
- connect the claim to the wider graph.

This standard exists so the repository can become enormous while remaining intelligible.
