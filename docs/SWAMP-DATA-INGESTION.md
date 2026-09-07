# Swamp Data Ingestion — Bulk Research Architecture

## Purpose

The repository is now large enough that individual articles are no longer the limiting factor. The limiting factor is **systematic extraction**.

The objective of this document is to turn large public datasets into a controlled stream of dense, country-linked records.

The rule is:

> **Do not dump the internet into the repository. Build a funnel that extracts the highest-value relationships and preserves the source behind every extraction.**

## 1. The bulk-data funnel

Every reservoir follows the same pipeline:

`source → raw/index → normalized entities → relationships → metrics → country attachment → evidence record → graph node → article`

A source can be enormous without every record being worth putting into the public graph.

### Stage A — Source index

Record:

- source name;
- publisher;
- dataset name;
- URL;
- jurisdiction;
- coverage period;
- update frequency;
- file format;
- record count if available;
- licensing/terms;
- last retrieval date.

### Stage B — Raw/index layer

Preserve the identifiers necessary to retrieve the underlying record again.

Examples:

- FEC committee ID;
- FEC transaction ID;
- IRS EIN;
- IRS Object ID;
- media outlet identifier;
- corporate registration number;
- SIPRI company/rank/year;
- government procurement identifier;
- sanctions designation identifier.

### Stage C — Normalization

Normalize names without destroying the original source spelling.

Every entity should have:

`canonical_name`

`source_name`

`aliases`

`jurisdiction`

`identifier`

`entity_type`

`status`

### Stage D — Relationship extraction

Turn records into explicit edges.

Examples:

`PAC → DONATES_TO → CANDIDATE`

`DONOR → CONTRIBUTES_TO → PAC`

`COMPANY → OWNED_BY → PARENT`

`MEDIA_OUTLET → OWNED_BY → COMPANY`

`NGO → GRANTS_TO → NGO`

`COMPANY → CONTRACTS_WITH → GOVERNMENT`

`AGENCY → OVERSEES → PROGRAM`

`WATCHDOG → INVESTIGATES → ORGANIZATION`

`ORGANIZATION → OPERATES_IN → COUNTRY`

### Stage E — Metrics

Metrics remain separate from relationships.

For organizations:

- revenue;
- expenditure;
- assets;
- liabilities;
- employees;
- members;
- audience;
- grants;
- contracts;
- political spending;
- lobbying spending;
- media reach.

For relationships:

- monetary value;
- percentage ownership;
- transaction count;
- frequency;
- start date;
- end date;
- geographic scope;
- confidence.

## 2. FEC: political money reservoir

The Federal Election Commission is one of the most useful sources because its data is already relational.

The FEC provides:

- committee master records;
- committee types;
- candidates;
- individual contributions;
- committee-to-committee transactions;
- disbursements;
- independent expenditures;
- filings and reports;
- enforcement information;
- audits;
- advisory opinions;
- historical filings;
- bulk transaction data.

The FEC says its downloadable bulk files can contain transaction-level data and that its PostgreSQL database dumps contain data from 1975 to the present for major schedules.

The graph should therefore be capable of representing decades of political-money history.

### FEC normalized record

```text
committee_id
committee_name
committee_type
sponsor
treasurer
party
state
candidate_id
cycle
filing_period
receipts
disbursements
cash_on_hand
debts
source
retrieved_at
```

### FEC transaction record

```text
transaction_id
filer_committee
recipient_committee
candidate
contributor_name
contributor_employer
contributor_occupation
city
state
transaction_date
amount
transaction_type
memo_text
cycle
source
```

### Why this matters

A single donor can be connected to:

`person → employer → industry → PAC → candidate → district → election → independent expenditure → policy issue`

A committee can be connected to:

`committee → sponsor → industry → donors → candidates → other committees → spending vendors`

This is exactly the type of relationship density the project is trying to capture.

## 3. IRS: nonprofit and NGO reservoir

The IRS is an equally important bulk reservoir for American NGOs, foundations and tax-exempt organizations.

The IRS currently provides:

- Publication 78 data;
- automatic revocations;
- Form 990-N;
- Form 990;
- Form 990-EZ;
- Form 990-PF;
- Form 990-T for eligible organizations;
- determination letters;
- the Exempt Organizations Business Master File.

The Business Master File currently contains approximately **1.96 million records** in the August 2026 posting.

### NGO normalization

```text
EIN
legal_name
DBA
exemption_type
foundation_status
formation_date
city
state
country
mission
revenue
expenses
assets
liabilities
net_assets
contributions
program_service_revenue
investment_income
grantmaking
employees
officers
board
related_organizations
filing_year
source
```

### Form 990 relationship extraction

The 990 layer should look beyond the headline revenue number.

Extract:

- grants made;
- grants received;
- related organizations;
- controlled organizations;
- officers/directors/trustees;
- highest-compensated employees;
- independent contractors;
- lobbying where disclosed;
- political activity disclosures;
- program services;
- foreign activity;
- donor/public-support categories;
- investments;
- property;
- debt;
- transactions with interested persons.

This can turn a nonprofit into a genuine institutional graph node.

## 4. European media reservoir

The European Media Ownership Monitor is particularly valuable because it already thinks in terms of ownership networks.

The 2025 system covers more than **3,000 news media outlets and owners** across the EU.

For each outlet, the graph should attempt to preserve:

```text
outlet
country
market
media_sector
owner
parent_company
beneficial_owner
ownership_percentage
editorial_control
revenue
funding
employees
audience
platforms
regulator
cross_border_operations
source
```

### Media graph

The useful structure is not:

`France → media`

It is:

`France → regulator → outlet → parent → beneficial owner → other outlets → advertising → audience → political/institutional relationships`

The same company can therefore be attached to multiple countries without pretending that all activity is national.

## 5. Corporate ownership reservoir

OpenCorporates provides a massive corporate universe. The repository should **not** attempt to copy hundreds of millions of companies into GitHub.

Instead, use targeted expansion.

### Trigger entities

Prioritize companies that are already connected to:

- governments;
- critical infrastructure;
- energy;
- defense;
- media;
- finance;
- telecommunications;
- AI/cloud;
- pharmaceuticals;
- ports;
- rail;
- aviation;
- mining;
- food;
- political organizations;
- major NGOs;
- strategic research.

Then expand:

`company → parent → subsidiaries → directors → jurisdiction → other holdings → government contracts → infrastructure → suppliers → customers`

This creates a high-value subgraph instead of a useless company dump.

## 6. Defense reservoir

SIPRI's Arms Industry Database is unusually clean for the defense layer.

The current Top 100 provides a standardized ranking and arms-revenue series. SIPRI also provides historical Excel data going back to 2002.

The 2024 Top 100 had combined arms revenue of **$679 billion**, the highest total recorded by SIPRI.

The repository should import the full Top 100 as a structured table, then connect each company to:

- country;
- parent group;
- subsidiaries;
- government customers where documented;
- major products/services;
- procurement records;
- ownership;
- research relationships;
- intelligence/security relationships.

Do not confuse arms revenue with total company revenue or profit.

## 7. Intelligence reservoir

The US Intelligence Community provides an immediate institutional skeleton of 18 elements.

The graph should create separate records for each element and then add:

- parent department;
- mission;
- legal authority;
- oversight;
- budget information where public;
- public programs;
- contracts;
- research relationships;
- interagency relationships;
- congressional oversight;
- inspectors general;
- declassified material.

The same methodology should later be applied to European national intelligence organizations and EU-level bodies.

## 8. Watchdog reservoir

Watchdogs should not be treated as one category.

Separate:

- state auditors;
- inspector generals;
- anti-corruption agencies;
- financial regulators;
- election monitors;
- ombuds offices;
- human-rights organizations;
- media monitors;
- fact-checkers;
- investigative journalism organizations;
- parliamentary committees.

For each one:

`jurisdiction → legal authority → funding → staff → investigations → findings → subjects → enforcement power → publication`

This lets the graph compare formal oversight with civil-society oversight.

## 9. Armed-group reservoir

The security layer must preserve the difference between:

- terrorist designation;
- insurgency;
- militia;
- rebel organization;
- criminal organization;
- armed political movement;
- state military;
- private military/security company.

A designation is an event issued by an authority. It is not an intrinsic scientific property.

Therefore store:

```text
group
alias
designating_authority
legal_basis
designation_date
review_date
geography
status
ideology
leadership
funding
affiliates
conflict_events
source
```

The graph can then answer questions such as:

`Which groups are designated by the EU?`

`Which countries designate the same group?`

`Which groups operate in a particular theatre?`

`When did designation change?`

without turning the repository into propaganda.

## 10. Entertainment / Hollywood reservoir

The entertainment graph should be built from industry relationships:

`studio → production → distributor → platform → advertiser → audience`

and:

`actor → agency → management → production → studio → distributor`

plus:

`publication → celebrity → story → paparazzi agency → advertiser → platform`

The project can then study concentration, ownership, distribution and economic scale without making claims about secret personal relationships.

## 11. Political ideology reservoir

Ideology should be modeled as a separate object.

Useful records include:

- ideology name;
- historical period;
- canonical texts;
- organizations;
- parties;
- publications;
- intellectual figures;
- declared policy positions;
- geographic distribution;
- historical relationships;
- internal factions;
- opponents;
- changes over time.

The key relationship is:

`person/organization → publicly identifies with → ideology`

rather than:

`person → secretly belongs to → ideology`

unless reliable evidence actually establishes the latter.

## 12. Country coupling

Every important entity should eventually receive a country matrix.

Example:

| Entity | Origin | Legal | HQ | Operations | Ownership | Funding | Audience | Political activity |
|---|---|---|---|---|---|---|---|---|
| Organization A | US | US | US | EU+US | US parent | US donors | EU+US | US |
| Organization B | UK | UK | UK | EU | multinational | mixed | UK+EU | UK/EU |

This is much more informative than a single `country=United States` field.

## 13. Activity index

Do not create a single mysterious “influence score.”

Store dimensions independently:

### Money

`revenue + spending + grants + contracts + political expenditure`

### People

`employees + members + volunteers + leadership`

### Information

`publications + broadcasts + investigations + citations + audience`

### Political

`lobbying + campaign activity + litigation + endorsements + policy outputs`

### Geography

`countries + facilities + operations + audience`

### Network

`degree + weighted degree + betweenness + bridges + dependency concentration`

A composite index can be calculated later, but the raw dimensions must remain visible.

## 14. The 10,000 Trees of Strife as data

Each Tree should be an observable pattern record.

```text
tree_id
pattern_name
domain
root_incentive
institutional_mechanism
actors
relationships
observable_outputs
measurable_indicators
countries
period
severity_if_measurable
counterexamples
mitigations
sources
confidence
```

Examples:

- media concentration;
- procurement concentration;
- lobbying dependency;
- opaque ownership;
- regulatory duplication;
- attention monetization;
- donor concentration;
- revolving-door employment;
- debt refinancing dependence;
- single-source supply dependence;
- platform dependency;
- infrastructure bottleneck;
- algorithmic amplification;
- institutional fragmentation;
- subsidy dependence;
- grant concentration;
- information asymmetry;
- corruption risk.

The “10,000” is therefore a target capacity. The repository should only create a tree when it can specify the pattern and evidence.

## 15. Farm / Sektur

The Farm is represented as a **subcultural systems model**, not a factual accusation against an undefined group.

A populated Farm record should contain:

`platform → community → moderators → influencers → content → audience → monetization → conflict loop → migration → archive`

Sektur remains a research term until an exact external referent is identified.

If a specific community is meant, the repository should attach:

- exact platform;
- exact community name;
- URLs or identifiers;
- dates;
- membership/reach where measurable;
- moderation structure;
- documented monetization;
- major recurring themes;
- documented organizational relationships.

## 16. Josh

The current repository deliberately does not identify “Josh” because the name is insufficient to determine which person or account is meant.

The correct ingestion process is:

`candidate → identity resolution → source verification → public role → employer/community → activity → relationships`

No canonical node should be created from an ambiguous name alone.

## 17. Storage strategy

Large source datasets should remain external or in compact source indexes. GitHub should contain:

1. normalized high-value records;
2. source indexes;
3. extraction scripts/configuration;
4. reproducible summaries;
5. selected transaction/relationship samples;
6. generated indexes;
7. long-form articles for major nodes.

Do not commit multi-gigabyte government dumps into the repository.

## 18. The desired end state

A reader should be able to open a country and see:

`country → government → agencies → parties → PACs → donors → NGOs → think tanks → watchdogs → media → owners → contractors → intelligence/security → infrastructure → energy → companies → people → money → contracts → historical events`

Then open any node and receive:

- a long-form explanation;
- structured facts;
- financial metrics;
- country relationships;
- ownership;
- leadership;
- activity history;
- related nodes;
- evidence;
- uncertainty;
- source links.

That is the architecture required for the repository to become dense rather than merely large.
