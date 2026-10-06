# Kingdom Atlas — Relationship Architecture

The Kingdom Atlas is the master relationship vocabulary for the project. Its basic unit is not a country, person or institution. It is the **relationship between nodes**.

## The 14 relationship families

### 1. Genealogical
Parent, child, ancestry, descent, succession, lineage and family.

### 2. Institutional
Membership, jurisdiction, delegation, oversight, incorporation, regulation and formal authority.

### 3. Financial
Ownership, lending, investment, debt, guarantees, transfers, dividends, taxation and capital flows.

### 4. Political
Alliance, treaty, representation, voting, coalition, sovereignty, diplomacy and policy influence.

### 5. Religious
Belief, institution, doctrine, ritual, scripture, clergy, pilgrimage and religious influence.

### 6. Intellectual
Ideas, schools of thought, authorship, criticism, citation, research and conceptual inheritance.

### 7. Geographic
Border, location, corridor, proximity, territory, maritime route and spatial dependence.

### 8. Cultural
Language, art, music, literature, customs, symbols, shared memory and cultural exchange.

### 9. Technological
Dependency, interoperability, ownership of technology, standards, infrastructure, licensing and supply chains.

### 10. Information
Publication, communication, data, media, platform relationships, archives and information flows.

### 11. Social
Community, employment, migration, networks, demographic relationships and social institutions.

### 12. Symbolic
Metaphor, representation, archetype, visual correspondence and conceptual association.

### 13. Functional
Input/output, service provision, infrastructure dependence, operational role and system function.

### 14. Mythological
A relationship internal to the Potatoverse canon. It must be labelled as such and cannot be used as empirical evidence merely because it is represented in the graph.

## Node ontology

A node can be:

`person · character · archetype · divine role · place · state · kingdom · institution · company · infrastructure · technology · resource · financial instrument · event · idea · text · artwork · symbol · project`

## Every serious relationship should answer

**Source:** What is the originating node?

**Relationship:** What exactly connects the two nodes?

**Target:** What is being connected to?

**Agency:** Who controls, creates, finances or governs the relationship?

**Time:** When did the relationship exist?

**Evidence:** What establishes it?

**Confidence:** How strong is the evidence?

**Consequence:** What other relationships depend on it?

## Example: a real-world chain

`France → member-of → European Union`

`European Union → establishes-rules-for → single market`

`single market → enables-cross-border → goods/services/capital/people`

`company → operates-within → single market`

`company → employs → workers`

`workers → contribute-to → tax/social-security system`

The graph becomes useful when these edges can be followed rather than when the nodes merely have descriptions.

## Example: mythological chain

`Father → mythological-source → Son`

`Son → symbolically-becomes → Ladder`

`Son → embodies → Door`

`Door → connects → levels of existence`

This is intentionally stored in a different evidence class from the France/EU chain.

## The Atlas question

The centre of the Atlas is not a single institution. It is the recurring civilizational problem of how human systems organize power, resources, meaning, responsibility, knowledge and life across time.

The long-term ambition is to make the Atlas traversable: choose a node, see its relationships, filter by relationship family, filter by evidence class, move through time, and follow the consequences outward.
