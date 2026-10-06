# Religion → Society Graph

**Status:** Research architecture and data specification

This page fills a major weakness in the repository: religious traditions were described richly, but the bridge from belief to the observable world was still too thin.

The purpose is not to reduce religion to politics or economics. It is to make visible the many intermediate layers through which religious traditions actually become socially observable.

## 1. The missing middle

The weak model is:

`religion → country`

The stronger model is:

`religion → text → interpretation → specialist → institution → building → property → community → family → education → charity → media → political/legal environment → economy → country`

A second chain captures movement:

`migration → diaspora → congregation → school → charity → media → political participation → next generation`

A third captures conflict:

`religious difference → legal boundary → political mobilization → conflict/cooperation → institutional response → demographic change`

A fourth captures material infrastructure:

`belief → ritual → sacred place → building/land → maintenance → labour → finance → procurement → local economy`

This is the layer that allows the repository's religious research to connect honestly to the World and North Programme layers.

## 2. Religious institutions are different kinds of nodes

The repository should distinguish:

- congregation
- parish
- diocese
- church
- monastery
- convent
- synagogue
- yeshiva
- mosque
- madrasa
- waqf
- temple
- ashram
- matha
- monastery
- vihara
- stupa
- gurdwara
- shrine
- sectarian association
- pilgrimage organization
- seminary
- university
- charity
- foundation
- publishing house
- media organization
- cemetery
- sacred-land trust
- religious political organization

These should not all be represented as a generic `religious institution` node.

## 3. Property and assets

A major future graph is:

`religious institution → owns/leases/uses → property`

Property can include:

- worship buildings
- schools
- monasteries
- cemeteries
- agricultural land
- forests
- pilgrimage facilities
- hospitals
- universities
- archives
- libraries
- museums
- community centers
- housing
- offices
- endowment assets

The repository's ownership model should distinguish **legal ownership**, **beneficial control**, **custodial use**, **leasehold**, **trust/endowment**, and **public ownership**.

This is especially important for Islamic waqf/endowment structures, church property, monastery land, Hindu temple trusts and other institutional forms where the economic relationship is not equivalent to ordinary corporate ownership.

## 4. Finance

Religious finance is heterogeneous.

Possible flows include:

`member → donation → institution`

`institution → wage → clergy/staff`

`institution → maintenance → contractor`

`endowment → investment → income → religious service`

`pilgrim → travel/hospitality → local economy`

`state → subsidy/grant → institution`

`institution → charity → household`

The graph must not assume that religious institutions are primarily profit-seeking economic actors. The point is to map actual financial relationships where evidence exists.

## 5. Education

Education is one of the strongest transmission mechanisms.

`tradition → doctrine → curriculum → teacher → student → household → next generation`

Possible institutions include:

- religious primary schools
- secondary schools
- seminaries
- yeshivot
- madrasas
- Islamic universities
- Christian universities
- Buddhist monasteries
- Hindu gurukulas
- Sikh educational institutions
- Sunday schools
- catechetical programs
- adult education
- informal study circles

The graph should distinguish state-accredited education from religious instruction and informal transmission.

## 6. Family and lifecycle

Religion frequently becomes observable through lifecycle events:

- birth naming
- circumcision
- baptism
- confirmation
- coming-of-age ceremonies
- marriage
- funeral
- mourning
- pilgrimage
- initiation
- ordination
- monastic vows

This produces a graph connecting religious practice to household formation and demographic continuity.

## 7. Calendar and economic rhythm

Religious calendars can influence observable social systems:

`holy day → working-time rule → transport pattern → retail demand → hospitality → food supply → public schedule`

Examples include Ramadan, Eid, Christmas, Easter, Passover, Yom Kippur, Diwali, Vesak, Vaisakhi, Rosh Hashanah, Lunar New Year-associated religious observances and numerous local calendars.

The repository should research these empirically rather than assuming that every observance has the same economic significance.

## 8. Pilgrimage as an infrastructure system

Pilgrimage should become a full graph domain.

`pilgrim → route → transport → accommodation → sacred site → ritual → local economy`

Relevant infrastructure includes:

- airports
- railways
- roads
- ports
- hotels
- food supply
- water
- sanitation
- security
- medical services
- religious facilities
- crowd-management systems

This provides a direct bridge from the religious layer into the European Economic Graph.

## 9. Religious law and public law

The repository should distinguish four things:

1. theological teaching;
2. internal religious law;
3. state law influenced by religious history;
4. current state law regulating religion.

These are often conflated.

A better graph is:

`religious tradition → ethical/legal teaching`

`religious institution → internal rule`

`historical religion → constitutional development`

`state → religious-freedom law`

`state → regulates institution`

`court → interprets law`

This is essential for comparing European states, Turkey, Canada, the United Kingdom and other jurisdictions.

## 10. Secularization and disaffiliation

The religious graph must contain the possibility that affiliation declines or disappears.

Useful nodes:

- secularization
- disaffiliation
- nonreligion
- atheism
- agnosticism
- religious switching
- mixed households
- nominal affiliation
- private belief
- institutional decline
- revival
- conversion
- migration-driven change

Pew's 2010–2020 research shows substantial changes in religious composition and notes that Christian disaffiliation contributed to increased religious diversity in several countries. citeturn0search5turn0search8

This means the graph cannot treat a country's historical religious identity as a permanent demographic fact.

## 11. Religious diversity

Religious diversity should be measured separately from religious freedom, secularization and pluralism.

Pew's 2026 Religious Diversity Index covers 201 countries and territories using seven broad categories and a 0–10 scale. It explicitly notes that there is no single universally accepted way to subdivide large traditions such as Christianity. citeturn0search1turn0search2

The repository should therefore maintain:

`country → religious-composition → source/date`

`country → diversity-index → source/date`

`country → constitutional-status → legal-source`

`country → freedom-of-religion → legal-source`

These are different edges.

## 12. Conflict and cooperation

Religion should not be represented as inherently peaceful or inherently violent. Historical outcomes vary by context.

Useful graph relationships include:

- persecution-of
- protects
- tolerates
- restricts
- recognizes
- subsidizes
- suppresses
- converts
- competes-with
- cooperates-with
- shares-site-with
- intermarriage-with
- merges-with
- syncretizes-with
- separates-from

Every conflict record should identify actors, date, location, institutional mechanism and evidence rather than assigning moral properties to an entire religion.

## 13. Migration and diaspora

Migration is one of the strongest mechanisms through which religious traditions become geographically distributed.

`origin-region → migration → destination-country → diaspora-community → institution → second-generation transmission`

A country may therefore contain a religious tradition without having historical roots in that country, while a tradition may retain multiple institutions across continents.

This is particularly important for Christianity, Islam, Judaism, Hindu traditions, Sikhism, Buddhism, Jainism, Zoroastrianism and many African and Indigenous traditions.

## 14. Media and information

Modern religion has a digital layer:

- television
- radio
- newspapers
- publishing
- websites
- podcasts
- livestreams
- social media
- online sermons
- digital scripture
- online communities
- religious education platforms

The graph should distinguish official institutional media from independent creators and anonymous communities.

## 15. Political participation

Religious communities can participate in politics through many mechanisms:

- voting blocs
- parties
- advocacy organizations
- civil-society organizations
- charities
- public campaigns
- lobbying
- constitutional movements
- peace movements
- nationalist movements
- minority-rights organizations

A religious identity should never be treated as proof that every adherent supports a political position.

## 16. North Programme country template

Every North Programme country should eventually receive the same research template:

### Constitutional layer

- constitution
- established religion, if any
- church/state relationship
- religious freedom
- registration requirements
- religious education
- religious courts/family-law interface

### Demographic layer

- religious composition
- unaffiliated population
- denominations
- regional concentration
- age profile where available
- migration and conversion

### Institutional layer

- major religious organizations
- clergy/specialists
- schools
- universities
- charities
- media
- sacred property

### Geographic layer

- major sacred sites
- pilgrimage routes
- historic religious landscapes
- diaspora concentrations

### Economic layer

- donations
- endowments
- property
- employment
- tourism/pilgrimage
- charity expenditure
- public funding

### Historical layer

- emergence
- state recognition
- reform
- migration
- conflict
- secularization
- revival

### Evidence layer

Every claim receives:

- source
- publication date
- underlying date of observation
- geography
- methodology
- confidence
- epistemic status

## 17. Epistemic statuses

This is a critical repository control.

Every religious claim should be tagged as one or more of:

`self-understanding`

`primary-textual`

`archaeological`

`historical-scholarship`

`demographic`

`institutional`

`legal`

`economic`

`comparative-interpretation`

`project-mythology`

The final category is specifically for the Potatoverse's own symbolic system. It must never silently become a historical claim.

## 18. The central bridge

The religious branch now has a natural connection to the repository's larger architecture:

`Source`

↓

`religious conceptions of ultimate reality`

↓

`cosmology`

↓

`text / oral tradition`

↓

`interpretation`

↓

`doctrine / philosophy`

↓

`ritual`

↓

`institution`

↓

`people / family / community`

↓

`place / building / land`

↓

`law / education / charity / media`

↓

`migration / demographics / politics / economy`

↓

`World`

↓

`European Economic Graph`

↓

`North Programme`

This is the missing bridge between the upper symbolic architecture and the observable world.

## 19. Research rule

The repository should always ask three questions before creating a religious edge:

**What kind of relationship is this?**

Textual, historical, institutional, demographic, legal, geographic, economic, theological, comparative or mythological?

**What evidence supports it?**

Primary text, archaeological record, census, law, institutional record, scholarly work or project interpretation?

**What exactly is being claimed?**

The religion's own belief, a historian's reconstruction, an observed social fact, or the project's symbolic interpretation?

That discipline prevents the religious graph from becoming either a flat encyclopedia or an undifferentiated mythology.
