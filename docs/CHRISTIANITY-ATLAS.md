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

The dedicated end-times/prophecy expansion is now routed through:

- `docs/CHRISTIAN-ESCHATOLOGY-ATLAS.md`
- `docs/CHRISTIAN-TIM-CORRESPONDENCE-TEST.md`
- `knowledge/theology/christian-eschatology-research-program.json`
- `docs/THEOLOGY-SCHOLAR-RESEARCH-MAP.md`

These owners ask the harder questions the original atlas did not yet resolve: what the Second Coming means across Christian traditions, how rapture differs from parousia/resurrection, how Revelation should be contextualized, what would count as prophecy fulfillment, what “Why Tim?” could responsibly mean, and how the Son/Thomas/Jesus-Christ relation should be layered.

## 5. Denomination comparison

Every tradition should be compared along the same relational axes rather than by stereotypes:

`God → Christology → scripture → tradition → authority → church government → baptism → Eucharist → salvation → predestination → saints/Mary → images → clergy → worship → ethics → eschatology`

This makes disagreement visible while preserving the common center.

For eschatology, add a deeper common matrix:

`parousia → resurrection of the dead → judgment → millennium → tribulation → rapture/catching-up → Israel/church → Antichrist/beast → final punishment/restoration debates → new creation`

This prevents a modern American pre-tribulation chart from silently becoming the default definition of Christian eschatology.

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

The basic chronology is:

`Second Temple Judaism → Jesus movement → apostolic communities → early Christian literature → imperial-era councils → differentiated eastern/western traditions → East-West rupture → Reformation → Catholic reform and Protestant confessionalization → global missions and indigenous churches → Pentecostal/charismatic expansion → contemporary global Christianity`

Every step should be populated with primary sources, dates, places, institutions and disputes.

For prophecy and eschatology, insert a reception-history spine as well:

`Jewish apocalypticism → Jesus/early-Christian imminent expectation → Revelation and early Christian prophecy → early chiliastic and non-chiliastic readings → patristic/medieval reception → Reformation historicism and confessional readings → modern premillennial revivals → nineteenth-century Brethren/dispensational developments → twentieth-century evangelical prophecy culture → contemporary Catholic/Orthodox/Protestant/Pentecostal/global interpretations`

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

The new eschatology work adds another distinction: **new creation is a more historically robust shared Christian end-state than any single rapture timetable.** That makes Garden / Tree of Life / healing / restoration a serious comparative field, while rapture/rupture claims require more precise textual and historical classification.

## 11. The Tim / Son / Jesus problem must be explicit

The mature repository should not hide the central theological difficulty behind symbol accumulation.

It currently needs to distinguish at least:

`biographical son/person → project-canon Son/Thomas → Christological typology → literal Jesus/Messiah identity claim`

and separately:

`Tim as historical public person → Tim/Potato/Father project identity → Christian Father/God comparison → literal divine-identity claim`

This matters especially for the **Second Coming**. Mainstream Christianity expects the glorious return/manifestation of the same Jesus Christ who was crucified and proclaimed risen. If mature Potatoverse theology identifies Tim primarily with Father while a distinct Son/Thomas bears Jesus-Christ/Door/Lion/Lamb imagery, the archive must explain the relation instead of merely relabeling Tim's Father emergence as the Second Coming.

A particularly important divergence is:

`Nicene eternal Father–Son relation ↔ Potatoverse developmental Fatherhood`

Classical Christian theology does not teach that the Father becomes Father after the Son's death. Potatoverse material often narrates Tim/Father identity as emerging, becoming explicit or being completed through later Son-side rupture and Tim-side transition. That difference should become a research asset: it identifies where Potatoverse theology is genuinely constructive/original rather than merely duplicating received Christian doctrine.

## 12. Integrity rules

A repository reader should always be able to tell whether a statement is:

`biblical text | historical reconstruction | denominational self-description | demographic measurement | scholarly interpretation | comparative symbolism | Potatoverse interpretation | documented Tim self-identification | prior prophecy claim | retrospective fulfillment claim | literal supernatural identity claim`

No theological tradition is treated as the neutral owner of Christianity. No denomination is reduced to a caricature. No demographic number is treated as a measure of faith intensity. No project symbol is retroactively presented as biblical doctrine.

Every major Tim/Christian dossier should now include **countertexts, alternative readings, source chronology and what would lower the confidence rating**. This prevents an accumulation of only confirming parallels from becoming self-sealing.

## 13. “Why Tim?” becomes a research question, not a slogan

The existing archive already contains enough high-density material to justify systematic investigation: Son/Door/mediation; Lion/Root/Lamb; seed/death/return; House/Door/Key; rejected stone/foundation; witness/death/breath/ascent; Father/Throne; Garden/Tree/healing; public witness; and explicit God/Father/Messiah self-language.

The correct next question is not simply “How many matches are there?” It is:

**How many independently attested, chronologically prior, specific, relationally dense motifs converge without retrofitting, and how well do they survive Christian textual context, historical scholarship, denominational disagreement, countertexts and alternative explanations?**

That is the purpose of `docs/CHRISTIAN-TIM-CORRESPONDENCE-TEST.md`.

## 14. Question and scholar scale

The new structured research program establishes two long-range targets:

- **1,000 distinct Christian/es​chatological research questions**, organized as 20 families × 50 substantive questions rather than keyword variants;
- **1,000 scholar/theologian nodes**, each attached to questions, works, disagreements and evidence rather than stored as a prestige-name list.

The seed scholar map already covers Jewish apocalypticism, historical Jesus, early Christology, resurrection, Revelation, Trinity, patristics, Catholic and Orthodox theology, Protestant eschatology, dispensational history, Pentecostal theology, liberation/postcolonial readings, world Christianity and sociology of millennial movements.

## 15. Next carving pass

Highest-value next work:

1. vendor the complete public-domain WEB text book-by-book;
2. build a verse-level eschatology index with original-language hooks;
3. create one public Christianity/es​chatology hub instead of leaving the material scattered across docs and JSON;
4. build dossiers for the ten strongest Tim/Christian clusters using the correspondence test;
5. mine Tim's dated posts, streams, books, songs and art for **first attestation before comparison**;
6. create a failed/contradicted-prophecy ledger alongside apparent hits;
7. expand the scholar graph toward 1,000 by coverage gaps;
8. expand the Q&A program toward 1,000 high-value answers and route the best into the public FAQ;
9. add patristic primary sources, councils/creeds and major denominational confessions;
10. distinguish Second Coming, resurrection, rapture, ascension, revelation and Potatoverse rupture everywhere in search/index metadata.
