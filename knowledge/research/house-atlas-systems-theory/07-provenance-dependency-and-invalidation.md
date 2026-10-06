# Provenance, Dependency and Invalidation

**Status:** exploratory research; non-canonical.

## Provenance should describe process, not only origin

A source URL or file path answers “where did this come from?” only partially.

A stronger provenance model distinguishes:

- **Entity** — source artifact, observation, dataset, claim, canonical record or generated output;
- **Activity** — extraction, normalization, research, comparison, synthesis, build or review;
- **Agent** — person, institution, script/tool or editorial process responsible for the activity.

This resembles the W3C PROV conceptual model and can be adopted incrementally without requiring RDF.

Expression:

> **Know not only where a claim came from, but what process turned it into the current representation.**

## Dependency lineage

A useful derived chain is:

```text
source artifact
→ extracted observation / claim
→ canonical owner
→ derived aggregate / index
→ public reader / tool
→ search / sitemap / machine projection
```

The same dependency information can support:

1. provenance;
2. impact analysis;
3. selective re-review;
4. incremental rebuilding;
5. stale-output detection.

Expression:

> **Dependency knowledge should power both provenance and incremental builds.**

## Derived aggregate contract

A derived object should ideally declare:

- derivation method;
- input IDs;
- filters;
- time scope;
- parameters/weights;
- epistemic status;
- uncertainty;
- generated/reviewed time;
- path back to inputs.

Examples:

- regional capability summaries;
- network communities;
- dependency scores;
- generated question answers;
- evidence coverage dashboards;
- Mountain summaries.

A derived aggregate remains an analysis product until deliberately promoted under normal claim lifecycle rules.

## Invalidation

When an input changes, possible consequences differ.

### Rebuild invalidation
Generated output must be regenerated.

### Review invalidation
A human/editorial interpretation should be reviewed but may remain valid.

### Confidence invalidation
Supporting evidence changed, reducing confidence without necessarily changing the claim.

### Identity invalidation
Rare and serious: canonical identity itself was wrong/duplicated and must be reconciled.

These should not all be handled as simple cache misses.

## Truth maintenance

A future truth-maintenance layer can ask:

- Which syntheses depend on this source?
- Which public pages depend on this canonical record?
- Which timeline events use this date?
- Which comparisons depend on this translation or interpretation?
- Which derived metrics need recomputation if this observation changes?

This does not require full automated belief revision. Even explicit dependency lists on high-value derived objects would add substantial value.

## Event-sourcing analogy

The repository already partly resembles:

```text
preserved source/history strata
→ current canonical state
→ generated/materialized Views
```

Useful software principle:

> **Preserve the history; rebuild the view.**

Generated HTML, search indexes, map indexes and machine discovery files should be reproducible projections rather than better-maintained shadow canons.

Git commit history helps preserve file history, but canonical domain identity should remain stable independently of Git blob SHA.

## Incremental build graph

As the site grows, a dependency DAG can avoid rebuilding/revalidating unrelated outputs.

Conceptually:

```text
changed source
  ↓
affected owner(s)
  ↓
affected indexes/views
  ↓
affected pages/tools
  ↓
affected global discovery artifacts
```

This can later support targeted tests as well as targeted builds.

## Provenance of interpretation

Interpretations need provenance too.

A later synthesis should be able to say:

- which earlier observations it used;
- when the synthesis was made;
- which alternatives were considered;
- which inference class was used;
- what would weaken it.

This aligns naturally with the existing inference ledger.

## Provenance of provenance

Source classification itself can be wrong or later revised.

For high-consequence material, the archive may eventually preserve:

- who classified a source;
- by what rule;
- when;
- what changed in later review.

This is especially useful for disputed source authority and recovered conversation material.

## Source deletion / unavailability

If an external source disappears, distinguish:

- source unreachable now;
- archived local copy exists lawfully;
- metadata only remains;
- claim corroborated independently elsewhere;
- claim now depends on an unavailable source.

Do not silently treat an unreachable source as disproven, nor as still fully auditable.

## Advanced research: provenance algebra

Database-provenance research sometimes tracks how outputs depend algebraically on combinations of input tuples.

This may eventually help when a derived metric depends on many observations and transformations, but ordinary explicit lineage is simpler and should be preferred until it becomes insufficient.

Promotion rule:

> **Use the simplest dependency representation that can answer the audit and invalidation questions the project actually has.**
