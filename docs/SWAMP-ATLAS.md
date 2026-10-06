# Swamp Atlas — Organizations, Attention, Money and Influence

## Purpose

The Swamp is the project's name for the dense lower layer where information, money, institutions, ideology, attention, conflict and organizational incentives accumulate.

It is **not a claim that all organizations in this atlas are secretly coordinated**. The atlas is designed to discover and test relationships. A relationship belongs in the graph because there is evidence for it, because it is an explicit public affiliation, because money or ownership can be documented, or because the relationship is clearly marked as a hypothesis requiring investigation.

The Swamp therefore becomes an **organizational ecology**, not a conspiracy catalogue.

## What belongs in the Swamp

The expanded atlas should track at least these families:

- news media and broadcasters;
- newspapers and magazines;
- digital publishers;
- independent journalists and commentators;
- paparazzi and celebrity media;
- film and television studios;
- production companies;
- talent agencies;
- NGOs and charities;
- foundations;
- think tanks;
- policy institutes;
- political parties;
- PACs and Super PACs where applicable;
- lobbying organizations;
- campaign committees;
- watchdogs;
- fact-checkers;
- civil-liberties organizations;
- advocacy organizations;
- intelligence agencies;
- military and security organizations;
- defense contractors;
- private intelligence and security firms;
- technology platforms;
- advertising networks;
- public-relations firms;
- universities and research institutes;
- religious organizations;
- new religious movements and cult-like groups, when that classification is supported by reliable sources;
- ideological movements;
- activist networks;
- militias and armed non-state groups;
- terrorist organizations, with careful factual sourcing and no glorification;
- criminal organizations where relevant to documented financial or institutional relationships.

## The country-coupling model

Every organization should be attachable to one or more geographic nodes without pretending that nationality equals control.

Recommended fields:

```text
organization_id
name
organization_type
country_of_origin
countries_of_operation
headquarters
legal_jurisdiction
founding_date
status
annual_revenue
annual_expenditure
assets
staff_count
members_or_reach
political_spending
funding_sources
ownership
board_members
leadership
parent_organization
subsidiaries
partners
known_grants
known_contracts
known_lobbying
media_properties
ideological_orientation
publicly_stated_mission
activity_level
last_verified
sources
confidence
```

## Country coupling

A media company can be coupled to a country through several distinct relationships:

1. **Founded in** — historical origin.
2. **Legally incorporated in** — legal jurisdiction.
3. **Headquartered in** — operational centre.
4. **Owned by** — controlling owner or parent.
5. **Operates in** — actual activity.
6. **Licensed in** — regulatory relationship.
7. **Funded by** — documented financial source.
8. **Receives public money from** — grants, contracts or subsidies.
9. **Employs in** — workforce geography.
10. **Audience in** — measurable audience concentration.
11. **Political activity in** — lobbying, campaign spending or advocacy.
12. **Infrastructure in** — physical assets or technical systems.

This prevents the simplistic error of saying that an international organization "belongs to" one country when its actual structure spans many jurisdictions.

## Money map

The financial layer should answer:

**Where did the money originate?**

**Who received it?**

**Through which legal entity?**

**For what purpose?**

**How much?**

**When?**

**What relationship followed?**

Useful relationship types:

- DONATES_TO
- GRANTS_TO
- CONTRACTS_WITH
- OWNS
- CONTROLS
- FUNDS
- LOBBIES
- ADVERTISES_WITH
- INVESTS_IN
- SUBSIDIZES
- RECEIVES_FROM
- EMPLOYS
- REPRESENTS
- PARTNERS_WITH
- REGULATES
- INVESTIGATES
- WATCHES
- REPORTS_ON
- CITES
- DISTRIBUTES
- BROADCASTS
- PRODUCES
- ACQUIRES
- SELLS

## Activity measurement

"Activity" should not be one vague score. Store multiple observable dimensions.

### Financial activity

- annual revenue;
- expenditure;
- grants distributed;
- political expenditure;
- lobbying expenditure;
- contract value;
- advertising revenue.

### Human activity

- employees;
- volunteers;
- members;
- registered supporters;
- journalists;
- researchers;
- deployed personnel where publicly documented.

### Information activity

- articles published;
- broadcasts;
- posts;
- citations;
- investigations;
- audience/reach;
- web traffic where reliably measured;
- social-media activity.

### Political activity

- bills lobbied;
- meetings disclosed;
- campaign contributions;
- endorsements;
- litigation;
- public campaigns;
- policy papers.

### Geographic activity

Count activity by country and year.

This produces a map of **where an organization is actually active**, rather than merely where its headquarters is located.

## AIPAC and PACs

AIPAC and other political organizations should be represented as specific legal and organizational entities with separate records for PACs, Super PACs, advocacy organizations, foundations and associated entities when they are legally distinct.

The graph should never collapse all related entities into one blob. It should instead show:

**Entity → legal status → funding → spending → recipients → candidates → issues → geography → dates.**

The same method applies to every political organization regardless of ideology.

## Israel 365 / similar media and advocacy organizations

Organizations such as Israel365 should be entered as identifiable entities and researched through the same neutral schema:

- legal entity;
- founders and leadership;
- country/jurisdiction;
- declared mission;
- media properties;
- nonprofit status where applicable;
- revenue and expenditure;
- donors and grants where public;
- partnerships;
- audience;
- political advocacy;
- geographic operations;
- documented ideological orientation.

The graph should not infer secret control from ideological similarity or shared audiences.

## "Figtree" and ambiguous names

Ambiguous names must never be turned into a node solely because a name appears in a conversation.

For a candidate such as "Figtree":

1. identify the exact organization/entity;
2. identify jurisdiction;
3. identify official website or registration;
4. identify leadership;
5. distinguish similarly named entities;
6. only then create the node.

If identity cannot be established, store it in a research queue rather than the canonical graph.

## Watchdogs and intelligence organizations

The repository should systematically catalogue:

- government inspectorates;
- parliamentary oversight bodies;
- ombuds institutions;
- anti-corruption agencies;
- financial-intelligence units;
- intelligence agencies;
- national audit institutions;
- media watchdogs;
- civil-society watchdogs;
- fact-checking organizations;
- election-monitoring organizations;
- human-rights organizations.

The key distinction is between **formal authority** and **informal influence**.

An intelligence agency may possess legal collection powers. A watchdog may possess investigative capacity but no coercive authority. A media organization may possess enormous agenda-setting capacity but no legal authority. These are different edges in the graph.

## Contractors

Defense, intelligence and government contractors should be linked through:

- contracts;
- framework agreements;
- procurement notices;
- subsidiaries;
- ownership;
- executives;
- revolving-door employment;
- research partnerships;
- government customers;
- geographic deployment.

The graph should distinguish **contract value** from **profit**, because a large contract does not equal equivalent profit.

## Armed groups and terrorism

Militias, insurgent groups and terrorist organizations may be represented where necessary for geopolitical and security research, but only through factual, sourced fields:

- organization;
- ideology as self-described or reliably documented;
- geography;
- period of activity;
- leadership where reliably established;
- attacks/events;
- financing where documented;
- affiliates;
- opponents;
- state relationships where evidenced;
- designation status by specific governments or international bodies.

Avoid romanticizing, recruiting for, or operationally assisting violent organizations.

## Political ideologies

Ideology should be a separate node family rather than a secret-membership label.

Examples of relationship types:

- INFLUENCED_BY
- IDENTIFIES_WITH
- ADVOCATES
- CRITIQUES
- HISTORICALLY_ASSOCIATED_WITH
- FUNDED_BY
- OPPOSES

A politician should not be marked as belonging to a "cult," faction or handler network unless the repository has evidence sufficient to support that characterization.

Where evidence is weaker, use:

- associated with;
- publicly aligned with;
- advised by;
- employed by;
- donated to;
- received funding from;
- attended events with;
- cited by;
- publicly endorsed.

These are far more informative than speculative labels.

## Politicians and leaders

For each public political figure, the graph can eventually show:

**Person → party → constituency → committees → donors → PACs → lobbyists → policy organizations → media appearances → endorsements → campaign spending → legislation → voting record → declared ideology → geographic base.**

For media figures:

**Person → employer → owner → production company → agent → advertisers → programs → publications → audience → political activity → public affiliations.**

For NGO leaders:

**Person → NGO → board → funders → grants → campaigns → partners → government contracts → policy outputs.**

This creates an evidence graph rather than a personality gossip database.

## Paparazzi and Hollywood

The entertainment layer should be treated as an industry network:

- studios;
- production companies;
- distributors;
- streamers;
- talent agencies;
- management companies;
- publishers;
- tabloids;
- paparazzi agencies;
- celebrity news sites;
- advertisers;
- awards organizations;
- unions;
- financiers.

The important relationships are ownership, employment, financing, distribution, advertising and production—not assumptions about personal secret affiliations.

## The Farm / Sek­tur / subcultural Swamp

The Farm is the project's metaphor for an attention ecosystem in which people, memes, conflicts and identities are repeatedly cultivated for reaction.

The Farm has:

- producers;
- consumers;
- moderators;
- algorithms;
- advertisers;
- influencers;
- spectators;
- conflict loops;
- rewards;
- punishments;
- archives;
- migration between platforms.

"Sektur" and similar terms should be treated as project vocabulary until an exact external referent is established.

The graph should ask:

**Which platform? Which community? Which period? Which people? Which content? Which incentives? Which measurable activity?**

## Josh

"Josh" is currently an ambiguous reference and should **not** be promoted into a factual organizational or personal node without identification.

Create a research placeholder only when there is enough source material to determine which Josh is intended. If the user supplies the relevant screenshots, files, URLs or exact context, the repository can then distinguish:

- person;
- pseudonym;
- community identity;
- platform account;
- organization;
- employer;
- public activity;
- documented relationships.

This is especially important because the Swamp Atlas deals with real people and organizations. An ambiguous name should never become an accusation by accident.

## The 10,000 Trees of Strife

The "10,000 Trees of Strife" is best implemented as a **scalable taxonomy**, not literally 10,000 invented accusations.

Each Tree can represent a recurring systemic pattern, such as:

1. attention extraction;
2. outrage monetization;
3. institutional duplication;
4. opaque ownership;
5. regulatory capture;
6. lobbying dependency;
7. information asymmetry;
8. financial extraction;
9. corruption risk;
10. algorithmic amplification;
11. propaganda;
12. polarization;
13. grift;
14. nepotism;
15. revolving-door incentives;
16. dependency on one supplier;
17. debt spiral;
18. infrastructure neglect;
19. media concentration;
20. political fragmentation.

The remaining trees can be generated from **observable relationship patterns**, with each tree requiring evidence before entering the empirical layer.

The Tree of Strife therefore becomes a diagnostic system:

**Root = underlying incentive.**

**Trunk = institution/process.**

**Branches = actors and relationships.**

**Leaves = observable outputs.**

**Fruit = consequences.**

**Seeds = mechanisms reproducing the problem.**

## From Swamp to Garden

The purpose of the atlas is not simply to find villains.

It is to understand the ecology well enough to identify:

- useful organizations;
- harmful incentives;
- duplicate institutions;
- bridges between otherwise disconnected groups;
- concentrated power;
- fragmented power;
- money bottlenecks;
- information bottlenecks;
- regulatory gaps;
- productive collaborations;
- resilient structures.

That is the transition from **Swamp Atlas** to **Garden Atlas**.

The ultimate metric is not how many organizations we can accuse.

It is how much of the system we can actually explain.

## Research queue

The first expansion queue should prioritize:

### Media

National broadcasters, major newspapers, digital publishers, regional media, alternative media and major entertainment networks in every North Programme country.

### NGOs

Major NGOs by country, legal status, budget, staff, grants, operations and policy domain.

### Think tanks

Think tanks ranked by funding, publications, government access, policy citations and geographic activity.

### Watchdogs

Watchdogs ranked by investigative output, jurisdiction, funding, staff and documented findings.

### Political finance

PACs, Super PACs, campaign committees, lobby organizations, major donors, foundations and recipient politicians, using jurisdiction-specific legal records.

### Security

Intelligence agencies, police agencies, military institutions, contractors and documented procurement networks.

### Armed groups

Active groups by country and conflict theatre, with factual status and dates.

### Entertainment

Studios, streamers, agencies, production companies, publishers and celebrity-media networks.

### Ideology

Political and religious ideologies as explicit concepts connected to organizations through documented statements, membership, publications or historical association.

## Core principle

The Swamp becomes useful when every claim can eventually answer:

**Who?**

**Where?**

**When?**

**What do they do?**

**Who pays?**

**Who owns or controls it?**

**Who works there?**

**Who benefits?**

**Who is affected?**

**How large is the activity?**

**How certain are we?**

**What other nodes does it connect to?**

That is the empirical form of the Potato principle: **everything is in relation, but every important relationship should be made inspectable.**
