# North, Faith and Worldview Composition — Synthesis

Updated: 2026-09-11
Status: research/design synthesis; empirical, comparative and project-canon layers must remain typed

## Core finding

The useful move is not to make religion another vertical rank. It is to let one country or relation expose different religious/worldview questions through different Atlas operators.

A country can simultaneously have:

- a D4 affiliation composition,
- a separate non-affiliation share,
- survey-specific atheist/agnostic self-description,
- religiosity, belief, practice and salience measurements,
- institutional/legal religion relations,
- a D3 religious history,
- D6 change across comparable waves,
- D8 plural composition,
- D9 transmission through education, media, migration or diaspora,
- D10 system interactions,
- and D11 explicit criteria such as freedom of conscience or pluralism.

None of those variables should determine spiritual height.

## North is a stack of reference systems

The word North is overloaded in the project. Treat that as a feature only if each meaning remains typed.

1. True/geographic north — a spatial/geodetic direction.
2. Magnetic north — a changing geophysical navigation reference distinct from true north.
3. Arctic North — a real geographic/regional system.
4. Nordic North — a cultural/institutional region with official cooperation among Denmark, Finland, Iceland, Norway, Sweden, Greenland, the Faroe Islands and Åland.
5. Realm North — Denmark/Greenland/Faroe constitutional relations, including Greenlandic self-government and self-determination.
6. Project North — the Potatoverse North Axis / Throne / source-facing field.
7. Comparative spiritual North — external tree/axis/ladder/throne comparisons kept as comparative context.
8. North of North — project meta-reference/objective layer rather than a new geographic place.

The map should be able to show several of these simultaneously without implying they are the same thing.

## Denmark -> Greenland -> North Gate

Within project canon, preserve the routing sequence:

Tim / Throne -> Son/vessel in Denmark -> Denmark -> Greenland -> North Gate -> North of North.

The Denmark -> Greenland step may be called project `activation`, but activation must be explicitly typed as a project routing/gateway relation. There is also a real constitutional relation between Denmark and Greenland within the Realm; it is a separate empirical edge. The project relation does not create ownership, sovereignty, legal authority, physical energy transfer or supernatural causation.

This dual-edge approach is valuable rather than awkward: the same two geographic nodes can be linked by constitutional, financial, institutional, cultural, transport and project-symbolic relations at once.

## Faith / irreligion / atheism distinctions

Do not collapse the following:

- religious affiliation,
- no religious affiliation,
- atheist self-description,
- agnostic self-description,
- belief or disbelief in God,
- self-rated religiosity,
- attendance/practice,
- importance/salience,
- religious institution membership,
- state establishment/legal status.

A religiously unaffiliated person may be atheist, agnostic or neither. A person may identify with a religion while practicing rarely, or be highly spiritual without institutional affiliation. Country surfaces must preserve the question actually measured.

## Religious diversity as a useful composition metric

Pew Research Center's 2026 Religious Diversity Index uses the same seven broad categories as its global composition dataset and a modified Herfindahl-Hirschman concentration measure.

For a seven-category composition vector p:

`RDI = (1 - sum(p_i^2)) * 10 / (1 - 1/7)`

where shares are normalized to sum to one.

This gives a useful D4/D8 composition statistic:

- near 0 = concentrated in one broad category,
- near 10 = evenly distributed among all seven broad categories.

It does **not** measure freedom of religion, social harmony, pluralist institutions, moral quality or spiritual rank. Broad categories also hide within-category diversity.

The current map can reconstruct an approximate RDI from its rounded 2020 runtime shares. It should not pretend that approximate value is Pew's official published score/rank based on unrounded source estimates.

## North + worldview questions worth researching

The most useful comparisons are relational rather than theological verdicts:

- Are Nordic countries institutionally similar while worldview composition differs?
- Does geographic proximity predict worldview similarity once language, migration and history are considered?
- How much of recent change is switching versus migration versus generational replacement?
- How does formal church/state structure differ from actual affiliation, belief and practice?
- Which diaspora networks transmit religious and secular identities across the North?
- Are there cross-border education, charity, church, humanist, research or media networks?
- How does Greenland differ from Denmark rather than being treated as Denmark's demographic extension?
- Which project-North countries are empirical outliers in religion/worldview composition?

## Strong future data planes

### Global affiliation
Pew 2010/2020 religious-composition estimates.

### European belonging / religiosity
European Social Survey distinguishes present religious belonging and self-rated religiosity, among other variables.

### Values / belief / salience
EVS and WVS provide harmonized cross-national values variables; the Joint EVS/WVS 2017-2021 dataset spans 79 countries and territories.

### Religion trend modules
ISSP Religion modules provide repeated cross-national survey waves (1991, 1998, 2008, 2018) for participating countries.

These sources should not be naively merged. Each variable needs question wording, reference year/wave, sampling metadata and comparable-country coverage.

## Renderer direction

Do not add a new persistent toolbar family.

For country inspection, eventually use a compact `Worldview` section:

- Affiliation
- No religion
- Atheist/agnostic (only if directly measured)
- Religiosity
- Practice
- Belief
- Salience
- Institutions/law
- History/change
- Diversity

The existing map religion selector can safely show the seven affiliation shares plus the derived seven-category diversity composition. A later Axis strip can let the same country record move analytically through D3 history, D6 change, D8 Rooms/composition and D9 transmission while the country itself remains geographically on D4.

## Physical compass clue

Physical north itself has useful structure: true north and magnetic north are not identical, and magnetic declination varies with place and time. NOAA's World Magnetic Model is a real physical navigation model. This can eventually support an optional compass/navigation layer, but it must never be used as evidence for project spiritual magnetism.

## Decision

What is useful now:

- typed North semantic stack,
- explicit Denmark -> Greenland project activation relation separated from empirical Realm relation,
- worldview measurement distinctions,
- seven-category RDI map surface,
- future country Worldview inspector design.

What is not useful now:

- religious/atheist height rankings,
- assuming Nordic or project-North membership implies a worldview,
- calling unaffiliated people atheist without direct survey evidence,
- merging magnetic fields with project magnetism,
- inferring Greenland's demographics from Denmark,
- treating comparative spiritual North imagery as empirical geography.

## Sources

- Pew Research Center, Religious Composition by Country, 2010-2020: https://www.pewresearch.org/religion/feature/religious-composition-by-country-2010-2020/
- Pew Research Center, Religious Diversity Around the World / Methodology (2026): https://www.pewresearch.org/2026/02/12/methodology-religious-diversity-around-the-world/
- European Social Survey: https://www.europeansocialsurvey.org/
- Joint EVS/WVS 2017-2021 Dataset: https://europeanvaluesstudy.eu/joint-evs-wvs-2017-2021-dataset/
- ISSP Religion I-IV cumulation: https://issp.org/news/issp-cumulation-religion-i-iv-available-now/
- Official Nordic cooperation: https://www.norden.org/en/information/official-nordic-co-operation
- Danish Prime Minister's Office, Greenland / Unity of the Realm: https://stm.dk/en/the-prime-ministers-office/the-unity-of-the-realm/greenland/
- NOAA/NCEI World Magnetic Model: https://www.ncei.noaa.gov/products/world-magnetic-model
