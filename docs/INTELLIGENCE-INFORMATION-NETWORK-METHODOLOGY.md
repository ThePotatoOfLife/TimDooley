# Intelligence & Information Network: Methodology

This layer turns the repository into a historical and institutional network rather than a list of agencies.

## 1. What the network is trying to reconstruct

The target is the observable information environment:

`institution -> legal authority -> collection source -> information system -> processing -> analyst -> dissemination -> decision -> oversight -> archive`

A second layer records the world around that chain:

`agency -> partner -> contractor -> company -> financial institution -> court -> media -> public archive`

A third layer records time:

`founded -> reorganized -> database introduced -> authority changed -> operation -> scandal -> investigation -> reform -> records released`

The repository should therefore be able to answer questions such as:

- Who created a record?
- Under what legal authority?
- Which institution could access it?
- Where was it stored or indexed?
- Which other institutions could receive it?
- When did that authority begin and end?
- When did the system change?
- What public evidence demonstrates the relationship?
- What remains unknown?

## 2. Agency does not equal database

A major modeling mistake would be to represent “the CIA” or “the FBI” as one giant database.

Instead, separate:

- organization;
- statutory authority;
- mission;
- record system;
- collection program;
- case file;
- analyst/product;
- sharing channel;
- oversight body;
- archive/declassification mechanism.

For example, the FBI describes its Central Records System as an electronic index for requested information and separately maintains the public Vault as an FOIA library. These are different graph objects. The Vault contains released records, not the entirety of the FBI's internal information environment.

## 3. Public-source evidence hierarchy

### Tier A — primary institutional records

Declassified documents, statutes, regulations, court opinions, inspector-general reports, parliamentary reports, official archival releases, congressional investigations and authenticated exhibits.

### Tier B — formal secondary investigations

Commission reports, academic archival research and institutional histories based on substantial primary access.

### Tier C — reputable reporting

Investigative journalism and reporting with named sources, documents or independently verifiable evidence.

### Tier D — archival leads

Internet archives, forum captures, screenshots, anonymous documents and secondary compilations. These can identify research targets but should not automatically establish a fact.

### Tier E — allegation

Claims whose evidentiary status is unresolved. Preserve them because they may matter historically, but label them as allegations.

## 4. Assassination and death records

The graph should have a dedicated attribution model.

A death record can contain:

`victim -> death -> date -> place -> official cause -> investigation -> suspected actor -> attribution evidence -> court result -> intelligence claim -> journalistic claim -> counterevidence`

This prevents a common research failure: converting “X was accused of killing Y” into “X killed Y.”

For intelligence agencies, use the same discipline. A historical allegation that an agency participated in an assassination should remain an allegation until documentary, judicial or investigative evidence supports a stronger status.

## 5. Scandal model

A scandal is not one node with one description. It should become a timeline:

`program created -> secrecy -> activity -> exposure -> investigation -> institutional response -> legal/oversight change -> declassification -> later reassessment`

Useful anchor cases include COINTELPRO, MKULTRA, the Church Committee investigations, Watergate, Iran-Contra, the post-9/11 surveillance controversies, Snowden disclosures and the Epstein investigations.

## 6. Database archaeology

For every identified system, record:

- name;
- owner;
- legal basis;
- creation date;
- predecessor;
- successor;
- record categories;
- input sources;
- access classes;
- sharing partners;
- retention rules where public;
- oversight;
- public release mechanism;
- known changes;
- known controversies;
- current status if publicly documented.

This makes “data flow” historical rather than merely conceptual.

## 7. Intelligence alliances

The network should model alliances as their own institutions or agreements.

Examples include Five Eyes, NATO intelligence structures, bilateral liaison relationships, EU law-enforcement cooperation and Europol information exchange.

An alliance edge should specify its domain. “Works with” is too vague. Prefer:

`SIGINT-sharing`

`criminal-intelligence-sharing`

`military liaison`

`counterterrorism coordination`

`technical cooperation`

`joint investigation`

`legal assistance`

## 8. Europol and European data flow

The European layer deserves special attention because information can cross national boundaries without the organizations becoming one institution.

Model:

`national authority -> national database -> EU legal mechanism -> Europol/other EU node -> analysis/project -> participating authority`

Then connect this to the North Programme's country graph.

This is where PET, FE, BND, DGSE, AIVD, Europol, INTERPOL, Eurojust and national police systems can eventually be mapped without pretending they form one centralized European intelligence service.

## 9. Internet information ecology

4chan, Kiwi Farms and Reddit belong in a different layer from intelligence agencies, but the layers can intersect through documented investigations, platform moderation, court records, media archives, law-enforcement releases and public reporting.

The correct model is:

`platform -> community -> post/thread -> amplification -> migration -> incident -> investigation -> archive`

not:

`platform = ideology`.

4chan contains many boards and communities. Reddit contains many subreddits. Kiwi Farms is a specific forum/community ecosystem. Their histories, governance models and moderation structures must remain distinct.

## 10. Hate-symbol and group mapping

The heatmap should represent:

- group;
- symbol;
- symbol meaning;
- alternate meanings;
- date first documented;
- geographic appearance;
- incident;
- source;
- confidence.

A symbol should never automatically identify a person as extremist. ADL itself warns that many symbols have non-extremist meanings and must be evaluated in context.

Likewise, group membership should be sourced. Use ranges for membership estimates and preserve the date of the estimate.

## 11. Heatmap architecture

The eventual map should support multiple layers:

### Layer A — institutions

Agency headquarters, publicly documented offices, courts, parliaments and archives.

### Layer B — historical events

Scandals, investigations, attacks, prosecutions, major demonstrations and platform incidents.

### Layer C — extremist activity

Publicly documented group activity and hate incidents.

### Layer D — information infrastructure

Public archives, declassification portals, court databases, transparency databases and data-sharing systems.

### Layer E — migration

Movement of communities or information between platforms.

Every layer gets its own epistemic status so the map does not visually imply that all points have equal evidentiary weight.

## 12. What “lesser things” means

The network should deliberately go below famous agencies.

Useful smaller nodes include:

- records offices;
- inspector-general offices;
- parliamentary committees;
- court clerks and public dockets;
- police intelligence units;
- financial-intelligence units;
- border databases;
- customs systems;
- biometric systems;
- vehicle-registration systems;
- passenger-name-record systems;
- procurement databases;
- sanctions lists;
- contractor companies;
- archival institutions;
- local investigative journalists;
- platform moderators;
- community archives;
- research institutes.

These nodes often explain how information actually moves between large institutions.

## 13. North Programme connection

For the European/North Programme graph, each institution should eventually be linked to:

`country -> ministry -> legal authority -> budget -> infrastructure -> information system -> international partner -> data exchange -> oversight`

This produces a genuinely relational European security/information graph rather than a list of intelligence agencies.

## 14. Safety and research integrity

This project is an open-source historical and institutional map. It should not attempt to discover classified systems, evade security controls, identify covert personnel, publish private addresses, or provide instructions for exploiting intelligence infrastructure.

The objective is to understand publicly observable institutional relationships, historical records, governance, information architecture and documented controversies.
