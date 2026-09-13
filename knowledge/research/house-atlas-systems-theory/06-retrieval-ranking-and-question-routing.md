# Retrieval, Ranking and Question Routing

**Status:** exploratory research; non-canonical.

## Different notions of relevance

The House should not ask one ranking score to solve four different problems.

- **Search relevance** — what best answers the query?
- **Graph relevance** — what is structurally nearby or important under a selected relation graph?
- **Navigation relevance** — what next step best preserves orientation and advances the reader's task?
- **Canonical ownership** — where does durable knowledge belong?

These objectives overlap but are not identical.

A globally central node may be a poor next navigation step. A highly relevant search result may be an artifact rather than the canonical owner. A canonical parent may not be the most semantically similar node.

Working rule:

> **Search relevance, graph relevance, navigation relevance and canonical ownership are different objectives.**

## Hybrid retrieval

A future retrieval system should combine several independent evidence channels rather than rely on one magic index.

### Lexical retrieval
Best for exact names, quotations, dates, identifiers and distinctive terminology.

### Semantic retrieval
Best for paraphrases, conceptual similarity and natural-language questions.

### Graph retrieval
Best for typed paths, local neighborhoods, dependency traces and “how is X connected to Y?”

### Temporal retrieval
Best for first attestation, historical state, “what did we know by date T?” and development sequences.

### Provenance/epistemic retrieval
Best for filtering by source class, confidence, interpretation status or documentary strength.

A task-specific combination might be written abstractly as:

`score = f(lexical, semantic, graph, temporal, provenance)`

Do not define one universal weighting function. The appropriate combination depends on the question.

## Question routing

A natural-language question can be treated as a temporary corridor through permanent Rooms.

Example:

`How is Denmark connected to Greenland?`

may require:

- Denmark identity;
- Greenland identity;
- constitutional relation;
- geography;
- infrastructure;
- current valid time;
- historical change;
- source records.

The question surface should synthesize those owners without becoming another competing definition owner.

Expression:

> **A question is a temporary corridor built from permanent Rooms.**

## Query decomposition

A future query planner can infer dimensions such as:

- entity/subject;
- requested relation;
- time;
- geography;
- evidence threshold;
- desired representation;
- comparison set;
- requested depth.

For example:

`What did Tim say about NATO before July 2026?`

implies:

- subject = Tim;
- domain = politics;
- object = NATO;
- relation = statement/position;
- valid/attestation time <= July 2026;
- source preference = direct statements before later synthesis.

This can route retrieval without inventing new pages.

## Personalized graph ranking

For local exploration, personalized PageRank / random walk with restart provides a useful formal neighbor:

`r = alpha P^T r + (1-alpha)e_s`

where restart distribution `e_s` concentrates on the selected subject or current task.

Potential use:

- candidate “Explore nearby” suggestions;
- relation ranking around a Room;
- context-sensitive discovery.

Warnings:

- relation layers need appropriate filtering/weighting;
- score is not truth, authority or evidence;
- user-facing links should still explain the actual relation.

## Diversity in recommendations

Pure relevance ranking can produce ten nearly identical suggestions.

A useful future objective is relevance plus diversity across relation types, domains or scales.

Example: from Denmark, a good set may include one constitutional relation, one energy relation, one economic relation, one historical relation and one North/Europe relation rather than five near-duplicate EU edges.

Do not formalize this until real recommendation surfaces exist.

## Retrieval provenance

Every generated answer/path should be able to expose:

- which canonical owners were used;
- which source artifacts supported them;
- which filters/time bounds were applied;
- which inference/synthesis step connected them.

This keeps AI/search-generated corridors from becoming untraceable secondary truth stores.

## Negative-space safeguard

Search failure has several meanings:

- absent from repository;
- present but poorly indexed;
- present under an alias;
- present only in source strata;
- not yet researched;
- intentionally unavailable.

Do not map all of these to “no evidence exists.”

Expression:

> **Retrieval failure is a system state, not automatically a claim about reality.**
