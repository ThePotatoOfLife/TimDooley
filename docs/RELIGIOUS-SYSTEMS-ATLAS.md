# Religious Systems Atlas

**Repository layer:** The Source → The Separation → The Ladder → The Door → The Son → The Tree of Life → The World

**Status:** Research/reference layer

**Purpose:** Expand the religious foundation of the repository from a list of traditions into a navigable system of texts, doctrines, ritual, institutions, divine beings, sacred geography, historical change, esotericism and social coupling.

> This page is comparative research. It does not declare one religion true or false. Religious self-understanding, historical scholarship, and the Potatoverse's own symbolic interpretation must remain distinguishable.

## 1. What counts as a religious system?

A religion is rarely only a list of beliefs. A functioning tradition normally contains some combination of a conception of ultimate reality, stories or cosmology, authoritative texts or oral transmission, ritual practices, ethical expectations, communities, institutions, sacred places, specialists, calendars and mechanisms for transmitting the tradition across generations.

Those components do not have to exist in the same form. Christianity has churches, clergy, scripture and creeds. Rabbinic Judaism has Torah, rabbinic interpretation, halakhic practice and communal institutions. Islam has Qur'an, Sunnah, legal schools, mosques, scholars and waqf institutions. Hindu traditions have multiple textual canons, temples, lineages, philosophical schools and devotional communities without a single central church. Buddhism has monastic lineages, lay communities, multiple canons and philosophical schools. Shinto is organized heavily around shrine, ritual, place and kami rather than a universal creed.

Therefore the repository should model religion as a **graph of relationships**, not as a flat category.

`tradition → conception-of-ultimate-reality → cosmology → text/oral corpus → interpretation → doctrine → ritual → institution → community → place → historical society`

A second path is equally important:

`tradition → transmission → migration → diaspora → institution → education → family → next generation`

And a third:

`tradition → law/ethics → political settlement → property → public institution → social consequences`

## 2. Ultimate reality is not the same category everywhere

The repository must not silently translate every religious concept into the word "god."

### Personal or relational deity

Judaism, Christianity and Islam all organize their central theology around the one God, although their descriptions and theological systems differ substantially. In Judaism the God of Israel is bound to covenant and Torah. Christianity develops a Trinitarian theology in which Father, Son and Holy Spirit are understood within one God. Islam places **tawhid**, divine oneness, at the center and rejects the attribution of partners to God.

### Many deities within a larger sacred cosmos

Greek, Roman, Egyptian, Norse, Mesopotamian and many other historical religions contain multiple divine beings with different powers, genealogies, cults and local relationships. The graph should preserve each pantheon rather than flattening it into "polytheism."

### Ultimate reality beyond a simple creator-god category

Some Hindu philosophical traditions speak of Brahman as ultimate reality; Buddhist traditions can organize the path around awakening, dependent origination and nirvana rather than a creator god; Daoist traditions use Dao as a category of ultimate way/order rather than simply a personal deity.

### Sacred beings that are not gods

Angels, demons, jinn, devas, bodhisattvas, saints, ancestors, kami and spirits cannot automatically be assigned the same node type. Their theological status varies by tradition.

The graph therefore uses a controlled vocabulary:

- ultimate-reality
- creator-god
- deity
- divine-person
- emanation
- avatar
- prophet
- messiah
- sage
- buddha
- bodhisattva
- angelic-being
- demon
- jinn
- spirit
- ancestor
- saint
- hero
- culture-bringer
- cosmic-principle
- mythological-being

## 3. Abrahamic family: relationship without collapse

### Judaism

Judaism is an ancient Israelite/Jewish religious civilization whose history contains biblical, Second Temple, rabbinic, medieval, mystical and modern denominational layers.

The Torah is the central textual foundation of Jewish religious life, while the Tanakh contains Torah, Prophets and Writings. Rabbinic Judaism adds Mishnah, Talmud, Midrash and extensive halakhic interpretation. These are not interchangeable books: they occupy different positions in the history of authority and interpretation.

The core graph should therefore be:

`Judaism → Torah → Tanakh → rabbinic interpretation → Mishnah/Talmud → Halakhah → community practice`

The divine node is **YHWH / God of Israel**. Jewish theology also contains angels and other heavenly beings, but these should not be represented as independent gods. Later Jewish mystical traditions introduce rich symbolic vocabularies around the Shekhinah, divine attributes, sefirot, heavenly palaces and visionary ascent.

Important branches include Orthodox, Haredi, Modern Orthodox, Conservative/Masorti, Reform, Reconstructionist, Hasidic and Karaite traditions. The repository should eventually distinguish **denomination**, **movement**, **legal school**, **Hasidic dynasty**, **community** and **institution**, because these are different graph types.

### Christianity

Christianity emerges from the first-century Jewish environment of Roman Judea and Galilee and develops through the early Jesus movement, apostolic communities, councils, creeds, monastic traditions, episcopal institutions, medieval churches, Reformation movements and modern denominations.

The central textual graph is:

`Hebrew Bible/Old Testament traditions → Jesus movement → New Testament → apostolic interpretation → creeds → church traditions/confessions`

Mainstream Nicene Christianity is Trinitarian: Father, Son and Holy Spirit are confessed within one God. Jesus Christ occupies the central christological position. The graph must preserve the distinction between **Jesus as a historical/religious figure**, **Jesus as interpreted by Christian theology**, and **Jesus as a Potatoverse symbol**.

Major Christian families include Catholic, Eastern Orthodox, Oriental Orthodox, Assyrian Church of the East, Anglican, Lutheran, Reformed, Presbyterian, Methodist, Baptist, Anabaptist, Pentecostal, Evangelical, Adventist, Latter-day Saint and many independent traditions.

Christian esotericism is not a single system. Relevant historical layers include Christian mysticism, monastic contemplation, hesychasm, apophatic theology, Christian Kabbalah, Rosicrucian currents and Gnostic traditions. Gnostic traditions must be represented historically rather than assumed to be identical with all Christianity.

### Islam

Islam emerges in seventh-century Arabia around the Qur'anic revelation associated with Muhammad and the formation of the early Muslim community.

Its central graph is:

`Allah/God → revelation → Qur'an → Muhammad → Sunnah/Hadith → interpretation → fiqh → community`

The theological center is **tawhid**, the oneness of God. Prophets are not gods. Angels and jinn are created beings, not alternative gods. Iblis has a particular status in Islamic theology and should not simply be mapped to the Christian concept of Satan without qualification.

The major institutional and intellectual branches include Sunni, Shia and Ibadi traditions, together with legal schools such as Hanafi, Maliki, Shafi'i, Hanbali and Ja'fari. Shia traditions include Twelver and Ismaili branches among others. Sufi orders form another important network and should be modeled as lineages and institutions rather than merely as a denomination parallel to Sunni/Shia.

Islamic esotericism includes Sufi metaphysics, Ibn Arabi's writings, Ismaili esoteric interpretation, Islamic philosophy, illuminationist traditions and historical movements such as Hurufism.

## 4. Dharmic traditions

### Hindu traditions

"Hinduism" is a family name applied to an extremely diverse collection of Indian religious traditions rather than a single founder-centered church. The repository must preserve this structural difference.

Important textual layers include Vedic literature, Upanishads, epics, Bhagavad Gita, Puranas, Dharmashastra, Agamas and Tantras. Philosophical and devotional traditions include Vaishnavism, Shaivism, Shaktism, Smartism, Advaita Vedanta, Vishishtadvaita, Dvaita and numerous regional lineages.

Important concepts include dharma, karma, samsara, moksha, atman, Brahman in relevant philosophical traditions, bhakti, yoga and forms of ritual sacrifice or worship.

The deity graph should include Vishnu, Shiva, Devi/Shakti, Lakshmi, Saraswati, Ganesha, Krishna, Rama, Hanuman and regional deities while retaining the distinction between deity, avatar, philosophical ultimate and local form.

Esoteric material includes Tantra, mantra, yantra, kundalini traditions, chakra systems, Agamic ritual and multiple yoga lineages. These are not interchangeable and should be connected to their actual textual and institutional traditions.

### Buddhism

Buddhism begins with Gautama Buddha and the early Buddhist community in ancient South Asia. Its central problem is not simply belief in a god but the transformation of suffering through insight and practice.

The graph should include:

`Buddha → teaching/Dharma → Sangha → practice → insight → liberation/nirvana`

The Four Noble Truths, Noble Eightfold Path, dependent origination, impermanence, non-self and karma are foundational concepts in different formulations. Theravada, Mahayana and Vajrayana represent broad historical families containing many schools.

Buddhist traditions also contain devas, bodhisattvas, buddhas and other beings. These should not be flattened into creator gods. Vajrayana introduces elaborate tantric systems of deity yoga, mantra, mandala and initiation.

### Jainism

Jainism provides a radically important comparison because liberation is organized around nonviolence, discipline and the purification of the jiva rather than dependence on a creator god.

Mahavira is the most historically prominent Tirthankara of the current era in Jain tradition, while Jain cosmology contains a much longer succession. Digambara and Svetambara traditions should be treated separately, with further schools such as Sthanakvasi and Terapanthi.

Core graph:

`jiva → karma → ethical discipline → ahimsa → liberation`

Anekantavada and aparigraha are important conceptual nodes.

### Sikhism

Sikhism emerges in fifteenth-century Punjab through Guru Nanak and the succession of Sikh Gurus. Its central theological concept is Ik Onkar, the one divine reality. The Guru Granth Sahib occupies a unique authoritative position in Sikh life.

Important social nodes include sangat, langar, seva, the Khalsa, gurdwaras and Sikh diaspora networks. Nam simran and devotional/mystical readings of Gurbani provide an important contemplative layer.

## 5. Iranian, East Asian and Japanese systems

### Zoroastrianism

Zoroastrianism is an ancient Iranian tradition associated with Zarathustra. Its dating remains debated, so the repository should preserve a range rather than invent precision.

The Avesta and especially the Gathas are central textual sources. Ahura Mazda, asha, ethical choice and the conflict between truth/order and destructive forces form major theological concepts. Later Zoroastrian literature develops a more elaborate cosmology including Angra Mainyu/Ahriman, Amesha Spentas and yazatas.

The graph should connect the tradition to Iranian history, Sasanian institutions, later Parsi communities and modern diaspora networks.

### Daoist traditions

Daoism contains philosophical and organized religious dimensions that developed over long periods. The Daodejing and Zhuangzi are crucial philosophical texts, while later organized traditions produced ritual systems, priesthoods, scriptures and institutions.

Important concepts include Dao, wu wei, ziran, qi, yin-yang and harmony. Religious Daoism contains celestial bureaucracies, local gods, immortals and ritual specialists.

Esoteric branches include internal alchemy, meditation, talismans, ritual technologies and longevity practices. The graph should connect these to particular lineages rather than presenting "Daoism" as a single homogeneous school.

### Shinto

Shinto is a Japanese tradition centered on kami, shrine ritual, purity, place, ancestry and relationships between humans and the sacred landscape. Its history is inseparable from interaction with Buddhism and other Japanese religious systems.

Important textual sources include Kojiki and Nihon Shoki, while shrine traditions preserve extensive ritual and local genealogies. Kami include Amaterasu, Susanoo, Tsukuyomi, Inari and Hachiman, among many others.

The graph should distinguish ancient kami traditions, shrine institutions, folk practice, State Shinto as a modern political formation, and postwar shrine traditions.

## 6. Ancient pantheon layer

The repository should not place ancient religions below modern religions merely because they are older. They form historical systems in their own right.

### Mesopotamia

The Mesopotamian layer should eventually distinguish Sumerian, Akkadian, Babylonian and Assyrian contexts. Key divine figures include An/Anu, Enlil, Enki/Ea, Inanna/Ishtar, Utu/Shamash, Nanna/Sin, Marduk, Nergal and others. Relationships between deities, cities, temples, kingship and political change are central.

### Canaanite and Levantine traditions

Nodes should include El, Baal, Asherah, Anat and other beings with careful attention to textual and archaeological context. The relationship between broader ancient West Semitic religious culture and Israelite religion must be researched rather than asserted as a simple one-to-one lineage.

### Egypt

Egyptian religion requires separate deity, temple, funerary, kingship and cosmological layers. Important figures include Ra, Amun, Ptah, Osiris, Isis, Horus, Set, Thoth, Anubis and Hathor. The graph should capture regional cult centers and historical theological combinations rather than treating the pantheon as static.

### Greece and Rome

Greek religion contains gods, heroes, local cults, mysteries, temples, festivals and civic structures. Important figures include Zeus, Hera, Poseidon, Athena, Apollo, Artemis, Aphrodite, Ares, Hermes, Demeter, Dionysus, Hestia, Hades, Kronos, Gaia and Uranus.

Roman religion should be connected to Greek traditions through historical processes of identification and adaptation, not through a simplistic "Roman copy" model. Roman institutions, state cult, household religion and imperial practice deserve separate nodes.

### Norse and Germanic traditions

The Norse graph should include Odin, Frigg, Thor, Baldr, Tyr, Heimdall, Freyja, Freyr, Loki, Hel and the world-tree Yggdrasil. Sources such as the Poetic Edda and Prose Edda are medieval records of earlier traditions, so the graph must distinguish source date from the antiquity of the material described.

Yggdrasil is particularly useful for the Tree of Life comparison, but it should remain a **comparative parallel**, not proof that the Potatoverse Tree of Life is historically derived from Norse religion.

## 7. Satanism and modern religious movements

Satanism must be represented as an umbrella rather than a single theology.

The repository should distinguish:

1. literary Satanic imagery;
2. historical accusations of devil worship;
3. nineteenth- and twentieth-century occult currents;
4. organized modern Satanism;
5. symbolic/atheistic Satanism;
6. theistic or occult Satanist currents;
7. contemporary activist movements using Satanic symbolism.

The Church of Satan and The Satanic Temple should be separate institutional nodes. Their philosophies, organizational histories and public activities should not be merged simply because both use Satanic symbolism.

The graph should also preserve the crucial epistemic distinction between **a group's own stated beliefs** and **external accusations about the group**.

## 8. Esotericism as a transmission network

Esotericism should not become a magical "everything is connected" layer. Instead, it should be treated as a historical network of texts, practices, teachers, symbols and institutions.

Useful categories include:

- Jewish mysticism
- Merkabah and Hekhalot traditions
- Kabbalah
- Christian mysticism
- Gnosticism
- Hermeticism
- Neoplatonism
- alchemy
- ceremonial magic
- Rosicrucianism
- Western occultism
- Theosophy
- modern Western esotericism
- Islamic Sufism
- Ismaili esoteric interpretation
- Hindu Tantra
- Buddhist Tantra/Vajrayana
- Daoist internal alchemy
- Japanese Shugendo and related syncretic practices

Every esoteric node should have a **historical source**, **tradition**, **period**, **practice**, **text**, **institution/lineage**, and **interpretive status** where possible.

## 9. Sacred geography

Religion is spatial. A complete graph therefore needs sacred geography rather than a simple list of countries.

Examples include Jerusalem, Mecca, Medina, Varanasi, Bodh Gaya, Amritsar, Lhasa, Mount Athos, Rome, Santiago de Compostela, Mount Sinai, Safed, Karbala, Najaf, Kyoto, Ise, Delphi, Eleusis, Memphis, Thebes, Uruk and many others.

The useful relationship types are:

`tradition → sacred-place`

`deity → cult-center`

`pilgrimage → route`

`route → transport-infrastructure`

`shrine/temple → institution`

`institution → land/building`

`place → tourism/economy`

`place → conflict/protection`

This creates a bridge from religious history to the repository's economic and infrastructure graph.

## 10. Religious change

Traditions should be modeled through time.

Useful events are:

- emergence
- earliest attestation
- canon formation
- translation
- reform
- schism
- council
- conquest
- migration
- diaspora formation
- state adoption
- state suppression
- institutional recognition
- revival
- secularization
- conversion
- deconversion
- syncretism
- revivalist movement
- modernization

A religion therefore becomes a temporal graph rather than a frozen encyclopedia entry.

## 11. Country coupling

A country should never simply be tagged "Christian," "Muslim" or "Hindu" without qualification.

The repository should distinguish:

- census identity
- self-identification
- religious practice
- institutional membership
- constitutional status
- established religion
- state recognition
- religious freedom law
- religious education
- religious courts or family-law systems
- sacred property
- clergy training
- charities
- pilgrimage
- diaspora networks
- migration
- conversion/deconversion

Pew's current global dataset provides a useful quantitative base: it covers 201 countries and territories and uses more than 2,700 censuses and surveys. It also explicitly warns that religious identification cannot always be measured precisely. citeturn0search0turn0search3

The repository should therefore store the source and uncertainty of demographic values rather than presenting them as exact facts.

## 12. The North Programme religious layer

For the North Programme, the first country pass should cover:

`Canada → Greenland → Denmark → Faroe Islands → Iceland → United Kingdom → European Union → Ukraine → Turkey`

Each country should eventually receive a religious-system page containing:

- population composition;
- constitutional relationship to religion;
- major historical traditions;
- current denominations;
- migration/diaspora flows;
- religious institutions;
- schools and universities;
- charities;
- sacred buildings and land;
- religious media;
- political parties where relevant;
- religious freedom law;
- conflicts and cooperation;
- demographic change;
- sources and confidence.

This matters because religious diversity is not uniform across the North Programme geography. Pew's 2020 index, for example, classifies Canada, the United Kingdom and France among highly diverse countries, while the global pattern varies dramatically between countries. citeturn0search1turn0search2

## 13. The graph rule

The final religious architecture should obey one rule:

> **Never connect two religious things merely because they sound similar. Connect them because there is a documented textual, historical, institutional, geographic, demographic or explicitly comparative relationship.**

The repository can contain a second layer for symbolic comparison, but it must be labeled as comparison.

Therefore:

`historical relationship ≠ theological equivalence ≠ symbolic parallel ≠ project mythology`

Keeping these four relationship types separate is what allows the religious branch to become large without becoming conceptually meaningless.

## 14. Next carving targets

The largest remaining gaps are:

1. Bahá'i Faith
2. Confucian traditions
3. African traditional religions
4. Yoruba religious systems
5. Vodun traditions
6. Akan traditions
7. Indigenous North American traditions
8. Indigenous Australian traditions
9. Mesoamerican traditions
10. Andean traditions
11. Polynesian traditions
12. Slavic traditions
13. Celtic traditions
14. Baltic traditions
15. Finnish/Uralic traditions
16. modern Paganisms
17. Wicca
18. Theosophy
19. Rastafari
20. new religious movements
21. secular humanism and nonreligious worldviews
22. atheism and agnosticism as worldview categories
23. religious conversion/deconversion
24. religious persecution and freedom
25. religious institutions as property and economic actors

These should be added as separate records and coupled into the existing graph rather than replacing the canonical Frame.
