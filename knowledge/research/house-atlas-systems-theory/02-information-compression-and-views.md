# Information Theory, Compression and Views

**Status:** exploratory research; non-canonical.

## Core idea

The House is too large for any one public surface to show directly. Every View therefore compresses.

The right question is not whether a View loses information. It must. The right question is whether it loses information that matters for the current task.

## Information bottleneck

Let:

- `X` = relevant full corpus state;
- `Z` = a compressed representation such as homepage, Room header or summary;
- `Y` = the user's task or question.

A useful conceptual neighbor is the information bottleneck objective:

```text
min I(X;Z) - beta I(Z;Y)
```

Interpretation:

- do not carry the whole archive into `Z`;
- preserve what is useful for `Y`.

The homepage is therefore not failed because it omits almost everything. It succeeds if it preserves orientation.

Working expression:

> **A good threshold is a task-relevant compression, not a miniature archive.**

## Rate-distortion thinking

Different Views may tolerate different losses.

A timeline cannot casually lose ordering or date uncertainty.
A source view cannot lose attribution.
A map cannot lose real geography.
A scientific comparison cannot lose units or status boundaries.
A religious comparison cannot lose mismatch and source direction.
A Mountain synthesis cannot lose the path back to its ingredients.

Hence every important View should eventually have a **loss profile**.

Candidate fields:

```text
input_scope
selection/filter
aggregation
omitted_relation_types
omitted_time_detail
omitted_uncertainty
omitted_minor_cases
preserved_invariants
source_path_back
```

Expression:

> **Every View is a lossy channel; declare what it is allowed to lose.**

## Mountain and Tree refinement

Mountain can be treated as coarse-graining:

```text
q: X_fine -> X_coarse
```

Tree is the reverse navigation direction: expanding a synthesis into differentiated parts, children, descendants, examples or sources.

But Tree is not generally the mathematical inverse of Mountain because coarse-graining is many-to-one.

Important distinction:

> **Mountain and Tree are inverse navigation directions, not necessarily inverse functions.**

Navigation can remain reversible because the system stores identity and provenance routes even when the summary itself cannot reconstruct every omitted detail.

## Minimum Description Length

The repository already prefers deep canonical owners over file proliferation. Minimum Description Length provides a useful formal neighbor:

```text
cost ≈ L(model) + L(data | model)
```

Applied qualitatively:

- too few owners/grammars: architecture is simple, but content requires endless exceptions;
- too many owners/grammars: local representation becomes easy, but maintenance and navigation explode.

This gives a principled intuition for consolidation and Room fission.

Expression:

> **Good architecture compresses repetition without compressing distinctions.**

## Room fission through compression pressure

Splitting a Room becomes more defensible when the unified representation creates repeated exception cost:

- distinct reader tasks;
- unrelated reasons to change;
- different source/update cadences;
- several incompatible specialist representations;
- many inbound links naturally target subsections;
- child material has independent explanatory depth.

Do not split merely because a file is long.

## Navigation entropy

At a choice point with `n` equally plausible options, maximum choice entropy grows like:

```text
H = log2(n)
```

Real choices are not equally likely, but the intuition is useful: more undifferentiated choices increase orientation burden.

A list of twelve `Related` links is more ambiguous than twelve links grouped by:

- Part of;
- Contains;
- Evidence;
- Compare;
- Developed from;
- Depends on.

Hence:

> **Relation labels are information, not decoration.**

## Orientation budget

A practical House concept:

> **Every interface has an orientation budget.**

Before adding another panel, menu, filter, graph control or card group, ask whether the user can still answer:

- where am I?
- what changed?
- what can I do next?

This is particularly important for World Map, graph, timeline and analytical dashboards.

## Backend density versus frontend density

These should be treated as independent variables.

The backend may need high density:

- provenance;
- relations;
- contradiction history;
- version states;
- multiple evidence classes.

The frontend should expose only the density useful to the current task.

Expression:

> **Backend density and frontend density should be decoupled.**

## Compression classes

Useful distinction:

- storage compression — fewer bytes;
- structural compression — deduplicated canonical ownership;
- reader compression — fewer visible choices/details;
- explanatory compression — one model explains several observations;
- destructive compression — provenance or important distinctions erased.

The project should reward the first four when they preserve what matters and reject the fifth.

## Integration-loss protocol

When many records are compressed into a synthesis, review:

1. Were unique dates preserved?
2. Is exact source wording preserved somewhere when material?
3. Are contradictions represented?
4. Are epistemic classes retained?
5. Can alternative interpretations still be reached?
6. Are values, units and directions preserved when material?
7. Can major conclusions be traced back to evidence?
8. Did inconvenient minority/outlier cases disappear?

Known losses should be stated, not hidden.

## Goodhart warning

Metrics can corrupt the thing they measure when optimized directly.

Examples:

- maximize node count -> placeholder nodes;
- maximize relation count -> generic edges;
- maximize page count -> thin pages;
- maximize source count -> citation stuffing;
- maximize coverage -> fake completeness;
- maximize confidence -> uncertainty suppression.

Therefore:

> **House metrics should diagnose more often than they optimize.**
