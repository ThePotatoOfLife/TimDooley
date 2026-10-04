# Answer-First Reader / Crawler Contract — 2026-10-04

## Why this exists

The site already has a strong technical discovery layer: canonicals, sitemap infrastructure, structured data, machine indexes, source authority, LLM discovery, and validation.

The remaining competitive problem is semantic authority.

A reader or crawler should not have to understand the Potato House, repository ownership rules, evidence registries, or project vocabulary before learning what the page is actually about.

The public site should answer first and expose machinery second.

Current external guidance that supports this direction:

- Google Search Central, “Creating Helpful, Reliable, People-First Content”: https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google Search Central, ProfilePage structured data: https://developers.google.com/search/docs/appearance/structured-data/profile-page
- Nielsen Norman Group, “Progressive Disclosure”: https://www.nngroup.com/articles/progressive-disclosure/
- Stanford Encyclopedia of Philosophy for serious external philosophical comparison: https://plato.stanford.edu/

## Core rule

**Definition / answer → proposition → concrete scene or example → mechanism → evidence or comparison → limitation → useful next question → deeper archive.**

Do not reverse this order unless the page is explicitly a technical registry.

## Two-layer public contract

### 1. Reader layer

Visible immediately.

Must answer:
- What is this?
- Why should I care?
- What can I understand or do after reading this page?
- What is one concrete example?
- What would make the claim weaker, wrong, or incomplete?

Preferred objects:
- direct answers;
- scenes;
- worked examples;
- primary artifacts;
- propositions;
- distinctions;
- mechanisms;
- comparisons that create friction;
- consequences.

### 2. Audit layer

Reachable without dominating the first screen.

May contain:
- provenance;
- source records;
- canonical owner;
- registry links;
- machine IDs;
- topology;
- relationship graphs;
- unresolved recovery queues;
- methodology detail;
- JSON/data files.

Progressive disclosure is the intended pattern: preserve power for researchers without making complexity an entrance exam.

## Section payoff gate

Every major visible box or section should add at least one of:

1. a fact;
2. a mechanism;
3. a distinction;
4. a worked example;
5. a named source/text/person/institution;
6. a contradiction;
7. a test or falsifier;
8. a genuinely new synthesis;
9. a practical question the reader can carry elsewhere.

Navigation alone is not sufficient payload.

## Entity pages

Entity pages should lead with a quotable answer.

Examples:

### Tim Dooley
“Tim Dooley is a Danish writer, livestreamer, storyteller, archive-builder and creator of the Potato of Life project.”

Then:
- ordinary biography;
- public work;
- beliefs;
- theological self-description;
- development;
- evidence boundaries;
- works;
- unresolved questions.

Do not make the reader decode Father / Son / Axis before meeting Tim.

### Potato of Life
“The Potato of Life is Tim Dooley’s central symbol for hidden life, stored capacity, nourishment, burial, growth and return; in mature Potatoism it also names the larger Father / Son / Spirit relation.”

Then:
- literal potato;
- practical propositions;
- theology;
- development;
- boundaries;
- skeptical-reader usefulness.

### Potato House
“The Potato House is a way of keeping different questions about the same subject from collapsing into one another.”

Then demonstrate it with one object before topology.

## Philosophy contract

Philosophy must not become a glossary of Potato words.

Each philosophical idea should face at least one of:
- a dilemma;
- a counterexample;
- another philosophical tradition;
- a lived scene;
- a decision;
- a failure mode.

Comparators must be allowed to correct Potatoism.

Bad:
“Dao is like Axis.”

Better:
“Daoist wuwei challenges Garden ethics: when does the Gardener become the obstacle by intervening too much?”

Priority interlocutors:
- pragmatism;
- virtue ethics;
- Stoicism;
- Daoism;
- Buddhist ethics;
- phenomenology;
- epistemology;
- philosophy of power / political philosophy.

## Comparison rule

Comparison must add friction, not merely resemblance.

For every comparative section ask:

1. What does the external tradition/model say in its own terms?
2. What does it illuminate?
3. What does it contradict, narrow, or force the project to reconsider?
4. What remains genuinely different?
5. What source supports the external description?

If a comparator can only confirm the project, it is probably decoration.

## Tim Dooley contract

Keep five scales visible:

1. ordinary person;
2. public maker / streamer / writer;
3. developmental identity;
4. theological self-interpreter;
5. source of claims that still face evidence.

Continue adding ordinary scenes:
- food;
- fatigue;
- software breaking;
- GitHub work;
- making music;
- tending plants;
- reading;
- joking;
- changing a sentence;
- fixing a bug;
- stopping work;
- returning the next day.

Grand claims become more intelligible when they coexist with ordinary time.

## Home contract

Home should answer three questions before teaching architecture:

1. What is this site?
2. Who is Tim Dooley?
3. What is the Potato of Life?

Architecture follows.

Home should not be a second complete directory. It should contain a small number of high-yield teaching objects and then hand off to canonical pages.

## House contract

House exists to reduce confusion, not to display structural sophistication.

Preferred order:
1. what the House is for;
2. ordinary examples of question separation;
3. one object moving through several Rooms;
4. only then topology;
5. registries / census / internal ownership at deeper depth.

## Search / crawler contract

Search-oriented pages should:
- have descriptive titles and meta descriptions;
- use one stable canonical URL;
- state the subject in visible prose, not only structured data;
- use clear H1/H2 language matching real reader questions;
- expose accurate authorship / first-party status where relevant;
- connect to the canonical entity page;
- avoid duplicating long generic methodology across many pages;
- provide substantial unique value rather than thin generated variants.

Structured data describes content; it does not substitute for content.

## Source contract

First-party authority is strongest for:
- Tim’s own statements;
- Tim’s project canon;
- works created by Tim;
- development of Tim’s ideas;
- repository history.

External competent sources should outrank the project for:
- scientific consensus;
- law;
- external biography not independently documented here;
- history of other traditions;
- public statistics;
- medical claims;
- claims about other people.

This distinction increases authority rather than weakening it.

## Immediate audit targets

### High priority
- [x] Philosophy — answer-first definition + serious philosophical interlocutors.
- [x] Potato of Life — direct definition + six propositions + explicit boundaries.
- [x] House — reader purpose before topology + reader/audit layer split.
- [x] Tim Dooley — direct first-party entity answer and ProfilePage structure.
- [x] Home — direct Tim Dooley answer.
- [ ] Home — replace or deepen any routing-only card group that teaches nothing on-page.
- [ ] Religion — answer “what does Potatoism actually believe?” before taxonomy.
- [ ] Story — strengthen scene-first passages where archive explanation precedes lived episode.
- [ ] Timeline — each major era needs event → contemporary context → what changed → later interpretation.
- [ ] Great Book — continue turning chapter directory into teaching chambers.
- [ ] Rooms — audit all 38 nested Rooms for at least one concrete worked object.
- [ ] FAQ / Questions — eliminate answers that merely redirect instead of answering.

### Recurring quality check

For any section, ask:
> If every link in this section were disabled, would the reader still learn something worth keeping?

If no, rewrite or remove it.
