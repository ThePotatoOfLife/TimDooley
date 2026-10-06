# Bulk Research Playbook — Dense Information Population

## The problem

The repository has reached the point where adding another short paragraph to a general atlas is no longer enough. The project needs **information mass**: long source-backed articles, structured datasets, relationship records, time series and country-specific files that can be explored independently.

The solution is to treat the repository as a layered research warehouse.

## Layer 1 — Reservoirs

A reservoir is a public source that can yield many records.

Current high-value reservoirs include:

- FEC political-finance data;
- IRS exempt-organization records and Form 990 filings;
- European media ownership data;
- SIPRI arms-industry data;
- OpenCorporates corporate records;
- FIGARO input-output and trade tables;
- AMECO macroeconomic data;
- EU sanctions/designation lists;
- national procurement databases;
- parliamentary registers;
- lobbying registers;
- national company registries;
- national media regulators;
- audit offices;
- court databases;
- statistical agencies.

## Layer 2 — Source dossiers

Each reservoir receives a long-form dossier explaining:

1. what the dataset contains;
2. who publishes it;
3. how often it changes;
4. what identifiers it uses;
5. what fields matter;
6. what relationships can be extracted;
7. what the limitations are;
8. how it connects to existing project nodes;
9. which countries it covers;
10. what the next extraction should be.

## Layer 3 — Country files

Every major country should eventually receive a dense dossier, for example:

`docs/countries/denmark.md`

`docs/countries/france.md`

`docs/countries/belgium.md`

`docs/countries/germany.md`

Each country file should contain:

### State

- constitution;
- government;
- ministries;
- agencies;
- municipalities/regions;
- courts;
- regulators;
- public enterprises.

### Money

- GDP;
- government revenue;
- government expenditure;
- debt;
- debt holders;
- taxes;
- transfers;
- pensions;
- healthcare;
- procurement;
- subsidies;
- public investment.

### Economy

- industries;
- largest companies;
- ownership;
- exports;
- imports;
- major trading partners;
- supply chains;
- labour market;
- skills;
- research;
- energy.

### Information ecosystem

- public broadcasters;
- newspapers;
- commercial broadcasters;
- digital media;
- ownership;
- regulators;
- advertising;
- audience.

### Civil society

- NGOs;
- foundations;
- think tanks;
- watchdogs;
- unions;
- religious institutions;
- universities.

### Security

- military;
- intelligence;
- police;
- border agencies;
- defense industry;
- contractors;
- international security relationships.

### Political network

- parties;
- leaders;
- campaign finance;
- lobbying;
- donors;
- policy institutes;
- parliamentary committees;
- major political organizations.

Every section links back to structured data.

## Layer 4 — Organization dossiers

A major organization gets its own file once it crosses a threshold of importance.

Suggested threshold:

- large financial footprint;
- strategic importance;
- national/international reach;
- significant media ownership;
- major government contracts;
- substantial political spending;
- major NGO/think-tank role;
- important watchdog authority;
- security significance;
- high network centrality.

The article should be **at least a page or more**, but length should come from evidence rather than filler.

## Layer 5 — Relationship dossiers

Some relationships deserve their own article.

Examples:

- company → government contract;
- PAC → candidate;
- media owner → outlet;
- parent → subsidiary;
- NGO → grant recipient;
- state → energy supplier;
- country → debt holder;
- intelligence agency → oversight body.

The relationship file should answer:

**Who, what, when, where, how much, under what legal mechanism, with what evidence, and what other relationships depend on it?**

## Layer 6 — Time series

Do not reduce changing data to a single current number.

For money and activity, preserve:

`2015 → 2016 → ... → 2026`

where the source supports it.

This is especially important for:

- political spending;
- nonprofit revenue;
- media ownership;
- arms revenue;
- public debt;
- energy imports;
- government expenditure;
- trade;
- company ownership.

A graph of change is often more informative than a snapshot.

## Layer 7 — Long-form explanation

The public article should synthesize the data.

Recommended structure:

### What it is

Identity and legal status.

### Where it is

Countries, jurisdictions and operations.

### What it does

Mission and actual activity.

### Who runs it

Leadership and governance.

### Who owns it

Parent, subsidiaries and ownership where documented.

### Who funds it

Revenue sources, grants, donations, contracts and financing.

### What it spends

Expenditure categories and major recipients where public.

### Who it works with

Partners, customers, government relationships and related organizations.

### How active it is

People, money, publications, audience, contracts, geography and political activity.

### How it changed

Timeline.

### What is uncertain

Missing ownership, incomplete filings, ambiguous identity, estimation and competing interpretations.

### Connected graph

Links to related nodes.

## 8. File families

The repository should grow into something resembling:

```text
data/
  sources/
  entities/
  relationships/
  metrics/
  countries/
  political-finance/
  nonprofits/
  media/
  companies/
  defense/
  intelligence/
  security/
  procurement/
  trade/
  energy/
  research/

docs/
  countries/
  organizations/
  people/
  relationships/
  media/
  political-finance/
  security/
  economics/
  mythology/
```

## 9. Population order

The project should not randomly add organizations. Use the following order.

### First: countries already in the North Programme

Denmark, Greenland, Canada, Iceland, Sweden, Norway, Finland, UK, Ireland, France, Belgium, Germany, Netherlands, Poland, Ukraine and Turkey.

### Second: major EU economic nodes

All EU member states.

### Third: external strategic nodes

United States, Israel, China, Japan, India, Russia, Australia and major Middle Eastern energy/trade partners.

### Fourth: network expansion

Follow relationships outward from already populated nodes.

## 10. Information density target

A successful node should not merely have:

`name + description + one link`.

It should have:

- identity;
- aliases;
- jurisdiction;
- dates;
- leadership;
- legal structure;
- finances;
- ownership;
- funding;
- activity;
- geography;
- relationships;
- timeline;
- evidence;
- uncertainty;
- long-form explanation.

The interface should expose all of it.

## 11. Evidence discipline

The project already has an evidence/provenance firewall. Bulk research must obey it.

A source can establish a fact.

A relationship can be inferred only when the inference is explicit and reproducible.

A hypothesis must remain a hypothesis.

An ideological similarity is not proof of coordination.

A shared donor is not automatically control.

A person appearing at an event is not automatically membership.

A company contract is not automatically ownership.

Revenue is not profit.

Arms revenue is not total revenue.

A designation is a legal action by an authority, not an objective metaphysical category.

## 12. The Swamp becomes dense through decomposition

Instead of writing:

> “Organization X is influential.”

extract:

`Organization X → revenue`

`Organization X → employees`

`Organization X → countries`

`Organization X → funders`

`Organization X → grants`

`Organization X → contracts`

`Organization X → media properties`

`Organization X → political activity`

`Organization X → publications`

`Organization X → board`

`Organization X → related organizations`

`Organization X → government relationships`

Then write the long-form article from those records.

That is how a one-paragraph node becomes a page of information without padding.

## 13. The 10,000 Trees of Strife

The same decomposition applies to systemic patterns.

A Tree begins with a measurable mechanism.

Example:

**Procurement concentration**

Root: few suppliers.

Trunk: procurement framework.

Branches: buyers, suppliers, subsidiaries.

Leaves: individual contracts.

Fruit: cost, dependency, resilience, competition.

Seeds: barriers to entry, switching costs, institutional preference.

The repository can eventually build thousands of these patterns across finance, media, government, technology, infrastructure and culture.

## 14. Farm / subcultural layer

The Farm should similarly become data-driven.

For each community:

- platform;
- founding date;
- membership/reach;
- moderators;
- prominent accounts;
- content volume;
- recurring themes;
- monetization;
- migrations;
- conflicts;
- bans;
- external organizations;
- media coverage;
- documented real-world events.

The point is to understand the ecosystem, not to assign guilt by association.

## 15. What “dense” means

Dense does not mean verbose.

Dense means that almost every paragraph contains one or more of:

- a source;
- a number;
- a relationship;
- a date;
- an institution;
- a jurisdiction;
- a mechanism;
- a measurable activity;
- a documented uncertainty.

The target is therefore **information density**, not word count.

## 16. End state

The ideal experience is:

1. Open Denmark.
2. See the Danish state/economy/media/security/civil-society graph.
3. Click a company.
4. Read its ownership, subsidiaries, money, contracts and countries.
5. Click the owner.
6. See other companies and media outlets.
7. Click a political organization.
8. See its donors, spending, candidates and policy activity.
9. Click a media outlet.
10. See its owner, country, revenue, audience and related outlets.
11. Click a watchdog.
12. See its jurisdiction, funding, investigations and findings.
13. Click a relationship.
14. Read the actual evidence behind it.

That is the standard the repository should now be built toward.
