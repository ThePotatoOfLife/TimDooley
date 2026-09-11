# Christianity Atlas

This document defines how Christianity is carved into the repository without flattening Christianity into a single belief system.

## 1. Start with the text

The Bible is treated as a source corpus before it is treated as theology. The repository's preferred complete English source is the World English Bible (WEB), a public-domain modern English translation. The source manifest is `data/sources/bible-world-english-bible.json`.

The next archival step is to vendor the complete WEB book-by-book, with chapter and verse boundaries preserved. The text should remain immutable source material; commentary and interpretation belong in separate layers.

## 2. Then reconstruct the world around the text

A Bible passage has at least five useful contexts:

`text → language → historical setting → literary context → reception/interpretation`

The repository should therefore distinguish Hebrew/Aramaic/Greek textual traditions, ancient Near Eastern and Second Temple contexts, Roman-period contexts, early Christian reception, later denominational interpretation, and modern scholarship.

## 3. Christianity is not one denomination

The graph begins with the broad Christian family and branches into major historical traditions:

`Christianity → ancient apostolic traditions → Roman Catholic / Eastern Orthodox / Oriental Orthodox / Church of the East traditions → Western Protestant families → later movements → independent and indigenous churches`

The exact branching is historical rather than purely theological. Some churches disagree over communion, authority, Christology, canon, sacraments and whether another movement should be considered Christian at all. The archive records those boundary claims instead of choosing one church's definition as the neutral definition.

## 4. Core Christian questions

The Christianity node should eventually expose the major questions directly:

- Who is God?
- Who is Jesus?
- What is the Trinity?
- What is the Holy Spirit?
- What is creation?
- What is sin and human alienation?
- What does salvation mean?
- What does the cross mean?
- What does resurrection mean?
- What is the kingdom of God?
- What is the church?
- What are baptism and Eucharist?
- What authority belongs to scripture, tradition, bishops, councils, pastors and communities?
- What does Christian love require?
- What happens after death?
- What is the final renewal of creation?

These are not all answered identically by all Christians.

## 5. Denomination comparison

Every tradition should be compared along the same relational axes rather than by stereotypes:

`God → Christology → scripture → tradition → authority → church government → baptism → Eucharist → salvation → predestination → saints/Mary → images → clergy → worship → ethics → eschatology`

This makes disagreement visible while preserving the common center.

## 6. Christianity as a world system

The repository should not stop at doctrine. Christianity has generated and participated in institutions and material networks:

`belief → congregation → clergy → property → school → hospital → monastery → university → charity → publisher → mission → migration → state relationship → cultural production`

Those relationships can be mapped by country and period. They should not be treated as evidence that all Christians or all churches share a political position.

## 7. Demography

The latest comprehensive Pew Research Center estimates currently used here are based on 2020 population data and were published in 2025. They estimate 2.3 billion Christians, or 28.8% of the world's population. Christianity remained the world's largest broad religious category. Christians were a majority in 120 countries and territories. The geographic center has shifted strongly: 31% of the world's Christians lived in sub-Saharan Africa, 24% in Latin America and the Caribbean, and 22% in Europe in 2020.

The demographic node must preserve the difference between affiliation and belief. A census answer of 'Christian' does not establish doctrinal conformity, church attendance or practice.

## 8. Canon must remain plural

The standard Protestant 66-book canon is only one Christian canon. Catholic, Eastern Orthodox, Oriental Orthodox, Ethiopian/Eritrean and East-Syriac traditions have different canon histories and collections. The repository should make the differences navigable rather than silently treating additional books as anomalies.

Canon graph:

`community → liturgical use → manuscript tradition → canon recognition → translation → commentary → doctrine`

## 9. Historical spine

The basic timeline is:

`Second Temple Judaism → Jesus movement → apostolic communities → early Christian literature → imperial-era councils → differentiated eastern/western traditions → East-West rupture → Reformation → Catholic reform and Protestant confessionalization → global missions and indigenous churches → Pentecostal/charismatic expansion → contemporary global Christianity`

Every step should be populated with primary sources, dates, places, institutions and disputes.

## 10. Relationship to the canonical Potatoverse tree

Christianity can be connected to the existing tree, but the connection must be typed.

- **Source:** biblical creation and God-language; comparative theology belongs here.
- **Separation:** heaven/earth, life/death, creation/fall, covenant and identity distinctions.
- **Ladder:** mountain, temple, pilgrimage, discipleship, ascent/descent and transformation motifs.
- **Door:** a project-level comparison to Christ as threshold, gate, mediator or passage; not a claim that Christianity teaches the repository's Door ontology literally.
- **Son:** Jesus Christ and the Christian Son-language; crucifixion and resurrection are historical/theological Christian claims, while the project's Son→Door transformation is its own interpretive layer.
- **Tree of Life:** Genesis and Revelation supply direct biblical anchors; later Christian theology adds resurrection and new-creation readings.
- **Tree of Strife:** can be compared with sin, death, exile, violence and broken communion, but is not itself a Christian canonical doctrine.
- **Potato:** material creation, food, soil and ordinary life can support analogy, but Potatoism remains project mythology.

## 11. Integrity rules

A repository reader should always be able to tell whether a statement is:

`biblical text | historical reconstruction | denominational self-description | demographic measurement | scholarly interpretation | comparative symbolism | Potatoverse interpretation`

No theological tradition is treated as the neutral owner of Christianity. No denomination is reduced to a caricature. No demographic number is treated as a measure of faith intensity. No project symbol is retroactively presented as biblical doctrine.

## 12. Next carving pass

The next major Christianity pass should put the complete public-domain WEB text into the repository book-by-book, then add chapter/verse indexing, canon comparison, textual history, early Christian sources, councils and creeds, denomination-specific confessions, country-level demographic tables, church institutional graphs, Christian art and architecture, monasticism, missions, social teaching, secularization and contemporary Christian communities.
