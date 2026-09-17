# Concrete Culture Field Atlas — Design

**Date:** 2026-09-17  
**Status:** approved direction; implementation pending written-spec review  
**Public surface:** `/context/culture/`  
**Primary House Room:** `culture-information`  
**Interfaces:** `archive-sources`, `world-systems`, `time-history`, `research-lab`

## 1. Purpose

The current Culture / Cult / Subculture reader is strong on mechanisms but still too abstract. It explains culture formation, subculture, high-control dynamics, conflict culture, classification power, reputation capture, archive persistence and correction, but a reader can finish the page without seeing enough of the actual social machinery in the world.

This expansion makes invisible networks tangible without collapsing distinct kinds of formations into one moral category. The public reader should be able to inspect named groups, organizations, scenes, online communities, NGOs, criminal networks, cultural movements, public cases, money flows, attention flows, recruitment flows, documented violence, legal status, platform relations, and human trajectories.

The core public question becomes:

> Who or what is actually here, how are they connected, what flows between them, what happened, what is established versus alleged, and how does a living person or local scene become a durable public role, organization, institution, conflict, archive, or culture?

The design must preserve the existing rule that culture, subculture, cult/high-control formation, gang, movement, NGO, criminal network, fandom, anti-fandom, platform, institution and mainstream culture are not synonyms and are not a single developmental ladder.

## 2. Existing architecture to preserve

The expansion builds on, rather than replaces:

- `data/culture-ontology.json`
- `data/subculture-research-map.json`
- `knowledge/culture/culture-formation-zeitgeist-atlas.json`
- `knowledge/world/under-culture-shadow-network-atlas.json`
- `context/culture/index.html`

The current architecture already provides the necessary epistemic firewall:

- shared audience is not proof of common command;
- adjacency is not coordination;
- a donor relationship is not donor control without additional evidence;
- a cultural label does not prove membership, motive, criminality or moral quality;
- a `cult` label is not a substitute for feature-level evidence;
- project metaphors such as Farm, Sektur, Swamp and Tree of Strife organize questions but do not prove external allegations.

The new concrete layer should make those boundaries easier to see because the same schema will hold very different examples side by side.

## 3. Architectural choice

Use one canonical concrete field atlas plus one provenance ledger, then build a static public projection from them.

### 3.1 Canonical atlas

Create:

`knowledge/culture/concrete-culture-field-atlas.json`

This file owns the cultural interpretation and relationship structure. It does **not** become the canonical identity owner for external organizations where another Room has that role.

Top-level collections:

- `formations`
- `human_cases`
- `events`
- `flows`
- `relationships`
- `pathways`
- `case_groups`
- `public_projection`

### 3.2 Source ledger

Create:

`knowledge/culture/concrete-culture-source-ledger.json`

Every externally testable claim in the atlas must resolve to one or more source IDs in this ledger. The ledger records URL, publisher, publication date, source class, accessed date, claim scope and notes about limitations.

### 3.3 Public projection

Create a build-time projector rather than a second hand-maintained content database.

Preferred implementation:

`scripts/project_public_culture_field.py`

The projector reads the canonical atlas and source ledger, renders a curated static HTML block, and injects it into the built Culture page between stable markers. This preserves:

- SEO and machine readability;
- no-JavaScript access;
- TTS compatibility through the existing `.culture-page` root;
- one canonical data owner;
- the repository rule that the public reader is a projection rather than a competing database.

The projector should be invoked by the existing public build/ontology pipeline after the base site is built and before public-navigation validation.

## 4. Data model

### 4.1 Formation record

A `formation` represents a named or analytically bounded social formation.

Required fields:

- `id`
- `name`
- `formation_types`
- `description`
- `places`
- `period`
- `status`
- `source_refs`

Optional but important fields:

- `self_description`
- `external_classifications`
- `stated_purpose_or_beliefs`
- `structure`
- `membership_model`
- `symbols_and_markers`
- `recruitment_channels`
- `funding_model`
- `commercial_model`
- `high_control_features`
- `violence_context`
- `legal_status`
- `platforms`
- `public_routes`
- `uncertainties`

Allowed `formation_types` include at minimum:

- `scene`
- `subculture`
- `fandom`
- `anti_fandom`
- `online_forum`
- `movement`
- `ngo`
- `charity`
- `advocacy_organization`
- `religious_organization`
- `high_control_formation`
- `gang_or_criminal_group`
- `criminal_network`
- `motorcycle_club_or_rocker_group`
- `company`
- `platform`
- `institution`
- `mainstream_culture`
- `canonical_culture`

A formation may have more than one type, but each type must be independently justified. For example, `online_forum` does not imply `high_control_formation`; `subculture` does not imply `gang_or_criminal_group`; `ngo` does not imply `movement`; a movement may contain NGOs without being reducible to them.

### 4.2 Human case record

A `human_case` is the person-behind-the-role layer. Its purpose is to restore sequence and agency rather than provide a dossier.

Required fields:

- `id`
- `display_name`
- `public_basis`
- `case_type`
- `summary`
- `timeline`
- `network_path`
- `source_refs`

Optional fields:

- `origin_event`
- `public_label_or_role`
- `attention_mechanisms`
- `audience_or_archive_roles`
- `platform_effects`
- `institutional_intersections`
- `documented_consequences`
- `reply_or_reclamation`
- `correction_or_later_context`
- `privacy_notes`

The intended narrative shape is:

`person -> event/content -> audience interest -> label -> repetition -> archive -> community lore -> status/money incentives -> institutional intersection -> consequences -> reply/reclamation/correction/persistence`

The record must distinguish what the person did from what audiences said about the person.

### 4.3 Event record

Required fields:

- `id`
- `event_type`
- `date_or_period`
- `places`
- `participants`
- `description`
- `evidence_status`
- `source_refs`

Useful event types include:

- `conflict_declared`
- `shooting`
- `assault`
- `arrest`
- `charge`
- `conviction`
- `acquittal`
- `court_dissolution`
- `platform_block`
- `regulatory_action`
- `schism`
- `migration`
- `fundraising`
- `grant`
- `campaign`
- `mainstreaming_milestone`
- `museum_or_canon_milestone`
- `public_reply`
- `correction`

### 4.4 Flow record

A `flow` makes the network tangible by showing what actually moves.

Required fields:

- `id`
- `flow_type`
- `from`
- `to`
- `period`
- `description`
- `evidence_status`
- `source_refs`

Supported flow types:

- `money`
- `grant`
- `donation`
- `membership_fee`
- `commercial_revenue`
- `illicit_proceeds`
- `attention`
- `audience`
- `information`
- `archive_material`
- `recruitment`
- `people`
- `status`
- `legitimacy`
- `goods`
- `weapons`
- `drugs`
- `violent_task`
- `instruction`
- `platform_traffic`

Money records may include `amount`, `currency`, `amount_type`, and `period`, but only when sourced. Unknown amounts remain unknown.

### 4.5 Relationship record

Required fields:

- `from`
- `relationship`
- `to`
- `period`
- `evidence_status`
- `source_refs`

Core relationships include:

- `EMERGES_FROM`
- `PART_OF`
- `SPLITS_FROM`
- `ALLIES_WITH`
- `IN_CONFLICT_WITH`
- `RECRUITS_FROM`
- `RECRUITS`
- `FUNDS`
- `RECEIVES_FROM`
- `DONATES_TO`
- `GRANTS_TO`
- `EMPLOYS`
- `HOSTS`
- `ARCHIVES`
- `AMPLIFIES`
- `MONETIZES`
- `REPORTS_ON`
- `INVESTIGATES`
- `REGULATES`
- `PROSECUTES`
- `CLASSIFIES`
- `BLOCKS_OR_DEPLATFORMS`
- `MIGRATES_TO`
- `INFLUENCES`
- `MAINSTREAMS_INTO`
- `CANONIZED_BY`

## 5. Evidence states and legal-status discipline

Every claim capable of harming a living person or organization must expose its evidentiary state.

Allowed high-level evidence states:

- `first_party_stated`
- `official_record`
- `court_established`
- `audited_financial`
- `scholarly_analysis`
- `reputable_secondary`
- `attributed_allegation`
- `open_question`
- `project_analysis`

For criminal/legal material, use explicit status fields such as:

- `suspected`
- `investigated`
- `charged`
- `convicted`
- `acquitted`
- `dissolved_by_court`
- `appeal_pending`
- `historical_official_classification`

Never rewrite `suspected` or `charged` as `committed`. A group-level conflict record must not be converted into guilt for every member. An aggregate police statistic must not be attributed to a named group unless the source does so.

## 6. Privacy and human-dignity rules

The concrete layer must make networks visible without becoming another exposure system.

Rules:

1. Do not publish home addresses, phone numbers, private email addresses, private family details, leaked credentials, or similar personal data.
2. Minors are anonymized by default, even when an official source gives age and nationality. Their role can be described at the minimum level needed to understand the mechanism.
3. A living individual is named in a human case only when there is a strong public basis: established public figure, central named party in authoritative public records, or the individual has deliberately and publicly reclaimed or told the relevant story.
4. Do not import diagnoses, disability claims, intelligence claims, sexual details, or other sensitive attributes merely because an adversarial community discusses them.
5. `lolcow` is treated as an audience label / internet-cultural classification, not a natural type of person.
6. Prefer `online exploited personality`, `viral subject`, `anti-fandom target`, `public meme subject`, or another mechanism-level description in analytical prose where appropriate.
7. The person-behind-the-label view should increase context and agency rather than reproduce humiliating material.
8. Archive screenshots and hostile-source quotations are leads, not authority. They require corroboration for factual claims.

## 7. Initial evidence-backed corpus

The first implementation should deliberately mix unlike cases so the reader learns distinctions rather than one grand theory.

### 7.1 Danish rocker/gang conflict field, 2023–2025

Use Danish National Police rocker/gang reporting to build named conflict edges and date ranges, including examples such as:

- LTF ↔ Hells Angels MC
- Brabrandgruppen ↔ Sort på Sort
- Satudarah MC ↔ A26
- NBV ↔ VO Status
- LGP Gruppen ↔ MV Gruppen
- GT Gruppen ↔ Afdeling 12
- LTF ↔ NNV
- NNV ↔ Tingbjerg 202

This case demonstrates `group identity + territory/status + conflict relation + dated violence risk + law-enforcement classification` without treating every surrounding subculture participant as criminal.

Primary source family: Danish Police rocker/gang reports.

### 7.2 Loyal to Familia legal-status case

Use the Danish Supreme Court dissolution judgment to show how one formation can simultaneously be:

- a social association in constitutional analysis;
- a named gang formation in police practice;
- the subject of a court-established dissolution;
- involved in separately dated conflict relations.

The public projection must say exactly what the court established and avoid universalizing from LTF to all gangs, immigrant communities, neighborhoods or subcultures.

### 7.3 Violence-as-a-Service / OTF GRIMM

Use Europol and Danish/Swedish police sources to model the four-role chain:

`instigator -> recruiter -> enabler -> perpetrator`

Record the flows explicitly:

- money/order;
- recruitment;
- encrypted/social-platform communication;
- logistics/weapons;
- violent task;
- cross-border movement.

This is a strong example of how digital culture, status, money, criminal organization and physical violence can couple without being the same layer.

### 7.4 Foxtrot and Dalen network examples

Use Swedish Police/Europol material only for specific sourced propositions, especially the documented use of Violence-as-a-Service and youth recruitment. Do not build speculative biographies of individual suspects.

### 7.5 NXIVM

Use U.S. Department of Justice material around Keith Raniere’s conviction and sentencing to show the difference between:

- a self-described personal-development organization;
- concentrated charismatic authority;
- nested secret structure;
- coercive collateral and dependency mechanisms described in court proceedings;
- a criminal enterprise established through convictions.

This is the initial high-control case where the legal record is strong enough to keep the page concrete without relying on a loose `cult` label.

### 7.6 Kiwi Farms / adversarial archive ecology

Use the existing `data/subculture-research-map.json` node as the project bridge, but strengthen external sourcing.

Public case points may include:

- forum / adversarial-archive function;
- Cloudflare’s September 2022 emergency block and its stated reason;
- later UK Online Safety Act / Ofcom interaction where relevant;
- platform migration as an infrastructure relationship;
- distinction between the forum, its users, any target community and the broader `Farm` analytical model.

Do not treat forum repetition as factual corroboration about a target.

### 7.7 Snark / anti-fandom as a general formation

Use current scholarship, including research on celebrity snark spaces as `tiny publics`, to model how recurring commentary groups develop vernacular, governance, collective morality and cross-platform persistence.

This supplies a scholarly bridge between fandom, anti-fandom, informal tribunal dynamics and the existing reaction-economy model.

### 7.8 Ghyslain Raza / “Star Wars Kid” — person behind the label

Use the National Film Board of Canada documentary and related first-party/public institutional material.

Narrative emphasis:

`teenager makes private video -> other students publish it -> viral remix culture -> public label separates from person -> widespread circulation -> personal consequences -> later public reclamation -> right-to-be-forgotten / digital-shadow reflection`

This is a model case for the page’s “person behind the cow / meme / label” idea precisely because Raza later chose to participate publicly in reconstructing his own story.

The page should not reproduce humiliating clips or insults as spectacle.

### 7.9 Hip-hop — scene to mainstream to canon

Use Smithsonian sources to show a non-criminal cultural pathway:

`Bronx neighborhoods/block parties -> DJ/MC/graffiti/b-boy scene -> crews and local subculture -> commercial recording -> national/global mass culture -> museum collection / anthology / canonical preservation`

This prevents the concrete field from teaching that strong networks or subcultures are inherently pathological.

### 7.10 NGO money-flow contrasts

Use audited/official financial reporting to contrast organizational financing without implying equivalence of mission.

Initial examples:

- MSF: 2025 revenue above €2.6bn, 98% of operating income from private sources, over 7.5m private donors/foundations.
- ICRC: roughly CHF 1.76bn donor contributions in 2025, with the published source mix including 84% governments and European Commission.

Optional second wave:

- Greenpeace International annual reports;
- Amnesty International audited financial statements.

The purpose is to make `money flow` tangible while showing that funding architecture varies dramatically across lawful institutions.

## 8. Public Culture page structure

The existing conceptual sections remain. Add a concrete field after the foundational distinctions and before the late abstract synthesis.

### Section A — Who is actually here?

A compact directory of selected formations with type chips, place/period, and one-sentence description.

The same visual component must be able to show `gang`, `NGO`, `forum`, `high-control formation`, `scene`, `movement`, `institution` and `mainstream culture` without implying equivalence.

### Section B — Where violence actually appears

Show dated events and conflict edges only where supported.

Example views:

- LTF ↔ Hells Angels conflict period;
- NNV ↔ Tingbjerg 202 conflict;
- violence-as-a-service chain;
- selected official case events.

Explicitly distinguish group conflict, aggregate environment statistics and individual adjudicated acts.

### Section C — Follow the money, attention and recruitment

Render several flow chains:

- NGO donor → organization → programme expenditure;
- instigator → payment → recruiter → perpetrator;
- person/content → audience → archive → secondary creator → further attention;
- local scene → commercial distribution → mass audience → institutional preservation.

### Section D — People behind the labels

Narrative case cards with no more identifying detail than needed.

Each card uses three layers:

1. `The public story`
2. `The network story`
3. `The human story`

Initial named human case: Ghyslain Raza.

Future cases require the same privacy/public-basis gate.

### Section E — How a formation changes type

Show several contrasting pathways:

- culture mainstreaming (hip-hop);
- conflict/criminal service formation (Violence-as-a-Service);
- high-control nested organization (NXIVM);
- online archive / anti-fandom ecology;
- volunteer/cause → NGO/institutional organization.

A formation can split, stop, reverse, overlap or occupy several states at once. Do not imply an inevitable ladder.

### Section F — Concrete Tree of Strife

Render Tree of Strife as a traceable analytical view, never as proof of hidden coordination.

Example:

`status/money incentive -> online recruitment -> recruiter -> encrypted platform -> young perpetrator -> violent event -> policing/court response -> archive/news attention -> deterrence/recruitment feedback`

A second non-criminal Tree should show:

`local need/ideal -> volunteers/donors -> organization -> funding -> programme -> public visibility -> institutional persistence`

This contrast prevents the project metaphor from becoming synonymous with malign networks.

## 9. Source hierarchy

Preferred source order by claim type:

1. court judgments / legislation / official police or regulator records;
2. audited financial statements and official filings;
3. intergovernmental or government reports;
4. peer-reviewed scholarship;
5. direct first-party organizational statements for self-description;
6. established professional journalism for contextual narrative;
7. archival/adversarial/community material as lead-generation or reception history only.

Self-description may establish `what the group says it is`, not `what independent evidence establishes`.

## 10. Initial source pack

The implementation source ledger should begin with at least the following source families:

- Danish Police, Rocker- og bandesituationen / 2025 reporting: https://politi.dk/aktuelt/statistik/bander-og-rockere
- Danish Supreme Court, Loyal to Familia dissolution judgment: https://www.domstol.dk/media/rkfnpmdi/123-20-hjr-anonymiseret.pdf
- Europol OTF GRIMM: https://www.europol.europa.eu/how-we-work/operations/operational-taskforce-grimm
- Europol, Violence-as-a-Service role chain: https://www.europol.europa.eu/media-press/newsroom/news/instigator-to-perpetrator-how-violence%E2%80%91%E2%80%91%E2%80%91service-operates
- Europol, Denmark/Sweden recruitment case: https://www.europol.europa.eu/media-press/newsroom/news/teenagers-recruited-hitmen-denmark-and-sweden-strike-back-violence-service
- Europol 2026 criminal-network report: https://www.europol.europa.eu/publication-events/main-reports/blueprint-of-criminal-opportunism
- Swedish Police, GRIMM/Foxtrot/Dalen recruitment reporting: https://polisen.se/aktuellt/nyheter/nationell/2025/december/193-gripna-sedan-starten-av-europol-operationen-grimm/
- U.S. DOJ, NXIVM conviction/sentencing material: https://www.justice.gov/usao-edny/pr/nxivm-leader-keith-raniere-sentenced-120-years-prison-racketeering-and-sex-trafficking
- Cloudflare, Blocking Kiwifarms: https://blog.cloudflare.com/kiwifarms-blocked/
- Ofcom FOI / Kiwi Farms regulatory context: https://www.ofcom.org.uk/siteassets/resources/documents/about-ofcom/foi/2025/july/kiwifarms.st.pdf
- Sage / New Media & Society, `The governance of snarking: Anti-fandom as tiny publics` (2026): https://journals.sagepub.com/doi/abs/10.1177/14614448261473906
- National Film Board of Canada, `Star Wars Kid: The Rise of the Digital Shadows`: https://www.nfb.ca/film/star-wars-kid-the-rise-of-the-digital-shadows/
- Smithsonian/NMAAHC hip-hop history and canon sources: https://nmaahc.si.edu/explore/initiatives/hip-hop-revolutions
- MSF 2025 figures: https://www.msf.org/international-activity-report-2025/2025-figures
- ICRC Annual Report 2025: https://www.icrc.org/en/report/icrc-annual-report-2025
- Greenpeace International annual reports: https://www.greenpeace.org/international/about/annual-report/
- Amnesty International finances and audited accounts: https://www.amnesty.org/en/about-us/finances-and-pay/

## 11. Validation and tests

### 11.1 Schema validation

Create a schema or explicit validator that checks:

- unique IDs;
- valid formation and evidence types;
- all referenced entities exist;
- all source refs resolve;
- flows with amounts include currency and period;
- legal claims include legal status;
- human cases include `public_basis` and `privacy_notes`;
- named minors are rejected unless an explicit exceptional-public-interest override exists; first implementation should use no such override.

### 11.2 Evidence safety checks

Validator should fail if:

- `suspected`, `charged`, `convicted`, or equivalent legal language appears without an authoritative source ref;
- an aggregate statistic is attached to a named formation without a source explicitly making that attribution;
- a human case uses private-address/contact fields;
- a `lolcow` classification is stored as an intrinsic person type rather than an attributed audience label;
- a project-canon relation is marked as externally established evidence.

### 11.3 Public projection checks

Extend public validation to require the built Culture page to expose:

- `data-culture-field`
- at least one formation from each of several distinct classes;
- `People behind the labels`
- `Where violence actually appears`
- `Follow the flows`
- `How a formation changes type`
- source links or source IDs for every rendered concrete case;
- no missing TTS compatibility under `.culture-page`.

### 11.4 Regression boundary

Do not make the new concrete atlas a dependency for the five primary Doors. If the projector fails, quality checks should fail the build rather than silently publish stale concrete claims.

## 12. First implementation slice

The first build should be meaningful but bounded:

1. create atlas + source ledger + validator;
2. seed 8–12 contrastive cases/formation records from the source pack;
3. add events/flows/relationships for the strongest documented examples;
4. add one human-behind-the-label narrative (Ghyslain Raza);
5. add one scene→mainstream/canon narrative (hip-hop);
6. add one high-control/court case (NXIVM);
7. add Danish gang conflict and Violence-as-a-Service records;
8. add one online forum/anti-fandom ecology record (Kiwi Farms/snark distinction);
9. add NGO funding contrasts (MSF/ICRC; optional Greenpeace/Amnesty in the same wave if source extraction is clean);
10. project the public-safe records into `/context/culture/`;
11. extend CI and verify TTS still reads the injected concrete layer.

## 13. Deferred work

Not part of the first implementation:

- full interactive graph browser;
- geospatial map of every organization;
- comprehensive gang registry;
- private-person dossiers;
- automatic scraping of hostile forums;
- automated inference of ideology, motive, membership or criminality;
- ranking organizations by morality or danger;
- treating the Tree of Strife as a literal hidden-command graph.

A later graph UI can consume the same canonical atlas after the records and evidence discipline are proven.

## 14. Success criteria

A reader should be able to leave the Culture page able to answer concrete questions such as:

- What is a gang, an online anti-fandom, an NGO, a movement and a high-control formation, and why are they not the same thing?
- Which named Danish groups were in documented conflict in a particular period?
- How can a violent task be ordered, recruited, enabled and carried out across borders?
- What did a court actually establish about LTF or NXIVM, as distinct from internet labels?
- How does money enter different lawful organizations, and how does that differ from illicit or violence-for-hire flows?
- How can a local cultural scene become mainstream and then institutionally canonical?
- How can a human being become separated from a public meme/role and later reclaim part of the story?
- How can an archive preserve evidence while also preserving obsolete or decontextualized identities?
- What is known, what is alleged, what is project analysis, and what remains unknown?

The page succeeds when the invisible network becomes inspectable without pretending that visibility makes every relationship causal, criminal, coordinated or morally equivalent.
