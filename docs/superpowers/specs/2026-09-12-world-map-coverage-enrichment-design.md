# World Map Coverage-Led Enrichment Design

## Status
Conceptual direction approved in chat on 2026-09-12. This spec turns the approved coverage-ledger / gateway-and-hinge enrichment wave into a repository architecture, while incorporating the user's additional request to review underrepresented Eastern European countries for North-axis inclusion.

## Goal
Increase the World Map's real informational density and usefulness by filling the highest-leverage gaps in the existing substrate rather than adding more UI.

The wave has five linked outcomes:

1. derive trustworthy coverage from actual canonical content;
2. recover fragmented/duplicate country information into canonical owners;
3. expose already-collected but underused comparable observations;
4. enrich a ranked set of structurally important gateway/hinge countries and infrastructure categories;
5. review missing Eastern European North-axis profiles using the project's established North logic, with explicit role/basis/confidence rather than automatic reassignment.

The ordinary map interface should remain compact. This wave primarily enriches what existing country cards, groups, stats, chains, gateways and Impact traces can answer.

---

## 1. Core principles

### 1.1 Coverage is descriptive, not a geopolitical score
Do not collapse structural importance and missingness into one pseudo-scientific national score.

The system may rank enrichment work operationally, but must preserve separate fields such as:

```text
coverage completeness
structural connectors
active chains
gateway adjacency
impact connectivity
missing high-value domains
```

A country's enrichment priority is a backlog decision, not a claim about intrinsic national importance.

### 1.2 Actual content outranks stored counters
Existing `coverage.observations`, `coverage.relationships` and `coverage.sources` counters are known to be stale in some records. Egypt, Indonesia, South Africa and China can contain meaningful relationships/sources while counters still report zero.

The new coverage ledger must derive coverage from the actual record structure on every build/audit. Stored counters may be repaired from that derived truth but are never the ranking authority.

### 1.3 Recover before researching
When multiple records or legacy aliases describe the same ISO3 entity, recover valid evidence into the canonical owner before acquiring it again.

Known first regression case:

```text
TUR canonical owner: data/countries/turkiye.json
legacy parallel record: data/countries/turkey.json
```

Usable material in the legacy record must be migrated with provenance into `turkiye.json`, stale/current distinctions preserved, and the legacy record retired or converted into a non-authoritative alias/redirect artifact according to existing country-library conventions.

No two active country data owners may claim the same ISO3.

### 1.4 Missing is not zero
Coverage states must distinguish:

- `represented`
- `missing`
- `unknown`
- `pending-source`
- `not-applicable`

Do not coerce null/unknown into zero.

### 1.5 Empirical substrate and project Axis remain separate
Infrastructure, memberships, trade, grids, ports and regional chains are empirical/contextual data.
North/West/East/South profiles remain project-interpretive overlays with explicit basis/confidence/role.

The enrichment wave must never infer Axis membership directly from NATO, EU, OECD, REC or infrastructure membership.

---

## 2. Selected architecture: generated World Map Coverage Ledger

Create a generated/internal coverage ledger rather than another hand-maintained authority.

Recommended owner:

```text
data/world-map-coverage-ledger.json   # generated artifact
scripts/build_world_map_coverage.py   # derivation owner
```

The ledger evaluates all 195 canonical sovereign records plus registered first-class map entities where relevant.

Example:

```json
{
  "version": "1.0.0",
  "generated_at": "...",
  "policy": {
    "country_count": 195,
    "missing_is_zero": false,
    "ranking_is_operational_not_geopolitical": true
  },
  "entities": {
    "TUR": {
      "identity": "represented",
      "observations": {
        "represented": 10,
        "available_domains": ["population","gdp","inflation"],
        "missing_domains": ["..."],
        "freshness": {"fresh": 8, "stale": 2, "undated": 0}
      },
      "relationships": {"represented": 7},
      "provenance": {"source_records": 4},
      "systems": {
        "chains": ["..."],
        "gateways": ["turkish-straits"],
        "impact_edges": 3
      },
      "domains": {
        "strategic_geography": "partial",
        "energy": "partial",
        "logistics": "missing",
        "digital": "missing"
      },
      "quality_flags": ["duplicate-iso3-record"]
    }
  }
}
```

The ledger is not a normal UI layer. It supports validators, enrichment planning and optional compact provenance/coverage hints in existing cards later.

---

## 3. Coverage dimensions

The first ledger version should derive at least:

1. identity / canonical ownership
2. comparable observations
3. observation freshness / dateability
4. provenance / sources
5. relationships
6. institutional memberships
7. capabilities
8. dependencies
9. builds / active projects
10. strategic geography
11. ports / logistics
12. energy / resources / grids
13. trade / value chains
14. digital / technology infrastructure
15. regional systems
16. functional chains
17. gateways
18. directed impact connectivity

Each dimension returns a state plus useful counts, not a synthetic 0-100 truth score.

A separate deterministic backlog sorter may use ordered rules such as:

```text
known duplicate/integrity defect first
then gateway/chokepoint adjacency
then multi-chain connector
then missing dependency/infrastructure domains
then general descriptive gaps
```

The sorter must expose *why* an item ranked where it did.

---

## 4. Wave zero: repair the substrate before enrichment

### 4.1 Duplicate ISO3 / alias audit
Scan `data/countries/*.json` and ensure exactly one active canonical owner per canonical ISO3.

Required first case: `TUR`.

The audit should identify:

- duplicate ISO3 owners;
- legacy filename aliases;
- enrichment fragments not consolidated;
- identity mismatches;
- canonical index entries whose filename/record id disagree.

### 4.2 Recompute coverage counters
A maintenance/consolidation pass should update record-level coverage summaries from actual content so human-facing counters stop contradicting the file contents.

This is bookkeeping only; it must not erase richer fields merely to fit a counter schema.

### 4.3 Preserve provenance during recovery
Migrated legacy material receives provenance such as:

```json
{
  "migration_source": "data/countries/turkey.json",
  "migration_date": "2026-09-12",
  "authority": "legacy-recovered",
  "requires_refresh": true
}
```

Fields with old point estimates may be retained as historical observations or marked stale rather than silently presented as 2026 facts.

---

## 5. Expose already-collected comparable observations

`refresh_country_atlas.py` already attempts acquisition of fourteen World Bank indicators:

- population
- GDP
- GDP per capita
- GDP per capita PPP
- real growth
- inflation
- unemployment
- labour-force participation
- life expectancy
- fertility
- urbanization
- poverty
- CO2 emissions per capita
- internet penetration

The World Map runtime currently exposes only a smaller subset.

The enrichment wave should project additional comparable variables when their coverage and units are suitable, while preserving source/year/missingness.

Recommended first new Stats fields:

1. real GDP growth
2. inflation
3. unemployment
4. labour-force participation
5. life expectancy
6. fertility
7. urbanization
8. internet penetration
9. CO2 emissions per capita
10. poverty only when definition/comparability metadata is adequate

PPP GDP per capita can also become available if the runtime already has the required numeric normalization.

No new permanent Stats UI family is required; expand the existing registry/data path.

---

## 6. First ranked country enrichment wave

This wave is operationally ranked by existing structural connectivity plus observed underfill. It is not a statement that rank 1 is 'more important' than rank 8 in any absolute sense.

### Tier A — gateway-and-hinge core

1. **Türkiye (`TUR`)**
   - repair `turkey` / `turkiye` fragmentation;
   - Turkish Straits;
   - Black Sea / Mediterranean interface;
   - European / Caucasus / Middle Eastern corridors;
   - ports, pipelines, LNG, rail, EU trade, energy transit, dependencies, cables/digital infrastructure.

2. **Egypt (`EGY`)**
   - Suez / SUMED;
   - Mediterranean / Red Sea interface;
   - ports, canal system, LNG/gas, submarine cables;
   - Nile/water exposure, food import dependence, alternative-route impact.

3. **Indonesia (`IDN`)**
   - Malacca and wider Indonesian maritime passages;
   - ASEAN / G20 / Indian-Pacific connectivity;
   - ports, shipping, cables, nickel/battery chains, energy, manufacturing.

4. **South Africa (`ZAF`)**
   - Cape of Good Hope alternative route;
   - SADC / BRICS / G20;
   - Transnet ports/rail, Eskom/grid, power pools, mineral corridors, industrial dependencies.

5. **Iran (`IRN`)**
   - Hormuz / Persian Gulf;
   - energy export/transit and Eurasian connectivity;
   - ports, pipelines, rail, power links, Caspian/Gulf systems.

6. **Panama (`PAN`)**
   - Panama Canal;
   - Atlantic/Pacific interface;
   - canal water/operational constraints, paired ports, logistics zones, cables, alternative routes.

7. **Djibouti (`DJI`)**
   - Bab el-Mandeb / Red Sea;
   - Ethiopia access and East African logistics;
   - ports, cable landings, corridor dependencies.

### Tier B — regional multipliers

8. **China (`CHN`)** — ports, rail, grids, industrial clusters, critical-mineral processing, semiconductor/battery and BRI dependencies.
9. **India (`IND`)** — ports, freight corridors, hydrocarbon entry points, grids, digital infrastructure, pharmaceutical/industrial chains.
10. **Kenya (`KEN`)** — Mombasa/Northern Corridor, EAC power/digital/payment systems.
11. **Nigeria (`NGA`)** — ports, petroleum/gas infrastructure, West African Power Pool, cables, ECOWAS transport/payment systems.
12. **Morocco (`MAR`)** — Tanger-Med/Atlantic-Mediterranean interface, EU interconnectors, energy, rail/logistics, cables.

Later waves should be selected from the ledger rather than hard-coded continent quotas.

---

## 7. Ranked infrastructure categories

The first infrastructure population order is:

### 1. Ports and maritime terminals
Why first: they connect gateway routes to actual countries, logistics, energy and industry and can immediately feed the Impact graph.

Initial focus clusters:

- Bosporus/Dardanelles and major Turkish ports;
- Port Said/Alexandria/Suez/Red Sea terminals;
- Singapore / Malacca-adjacent Indonesian and Malaysian ports;
- Durban/Richards Bay/Cape Town/Ngqura;
- Bandar Abbas and relevant Hormuz-facing terminals;
- Balboa/Colón;
- Djibouti/Doraleh;
- Mombasa;
- Lagos/Tin Can/Lekki;
- Tanger-Med.

### 2. Electricity grids, interconnectors and regional power pools
Priority systems:

- European interconnectors tied to existing North/Northern Energy chains;
- Southern African Power Pool;
- West African Power Pool;
- East African regional interconnection projects;
- relevant North African/European links.

### 3. Subsea cables, landing stations and Internet Exchange Points
Priority basins:

- North Atlantic;
- Mediterranean / Red Sea;
- West African coast;
- East African coast;
- Indian Ocean / Southeast Asia;
- Panama / Caribbean-Pacific interface.

### 4. Pipelines, LNG terminals, storage and refinery interfaces
Priority systems:

- Türkiye / Black Sea / Caspian / European transit;
- North Sea / Northern Energy;
- North Africa / Mediterranean;
- Gulf / Hormuz;
- Southern African gas/power interfaces.

### 5. Rail/freight corridors and border/customs nodes
Priority corridors:

- Poland–Ukraine / Eastern Security;
- Türkiye–Europe–Caucasus;
- East African Northern/Central Corridors;
- Southern African mineral/port corridors;
- Sahel-to-coast access;
- Eurasian land corridors.

### 6. Gateway operational structure
Deepen existing gateways from points into systems where evidence exists:

- entrances / associated terminals;
- operators / authorities;
- dated flow observations;
- known constraints;
- documented alternatives;
- explicit affected systems/edges.

### 7. Strategic industrial/mineral corridors
Represent extraction → processing → energy → rail → port → downstream industry as linked nodes where sourced.

### 8. Air cargo, payment and data gateways
Second-stage infrastructure after the physical spine.

---

## 8. Infrastructure data architecture

Do not stuff every infrastructure asset into country JSON as duplicated free text.

Introduce canonical empirical owners by asset class or a unified infrastructure registry with typed records, for example:

```text
data/world-map-infrastructure.json
```

Initial type vocabulary should reuse the already-declared gateway model:

- port
- strait
- canal
- maritime-route
- grid-interconnector
- subsea-cable-system
- cable-landing
- internet-exchange
- pipeline
- lng-terminal
- refinery/storage-interface
- rail-junction
- freight-corridor
- border/customs-node
- air-hub
- payment-interface
- data-gateway

Each asset must have:

```text
id
label
type
location/geometry or explicit no-geometry status
countries/entities
systems/chains
operator/authority when known
observation/status/date when relevant
source/source_url
evidence class
```

Country records and runtime should reference these ids rather than copy authoritative asset facts into multiple owners.

Existing `world-map-gateways.json` can remain the chokepoint/gateway owner initially and either become a specialized projection from the infrastructure registry later or be incorporated deliberately during a subsequent consolidation. Do not duplicate gateway authority in this wave.

---

## 9. Impact integration

The recently added Impact engine should be extended only where the new infrastructure record contains an explicit dependency relationship.

Examples:

```text
country -> depends-on -> port
industrial corridor -> depends-on -> grid interconnector
country/system -> uses-gateway -> Turkish Straits
cable landing -> member-of-system -> cable system
```

Contextual adjacency alone is not dependency.

New infrastructure node kinds should reuse the existing impact-node architecture rather than build another tracer.

---

## 10. Institutional membership consolidation

`world-institution-memberships.json` is the canonical modern membership owner but currently does not contain every group still represented in `world-relational-map.json`.

First consolidation candidates:

- NATO
- BRICS
- AUKUS
- Five Eyes

Move/normalize empirical membership authority into `world-institution-memberships.json`, preserving source/date/status/partners/non-country metadata. Compatibility projections may remain in the relational/runtime files, but hand-maintained duplicate member lists must not remain authoritative in two places.

This change is structural cleanup, not a political classification change.

---

## 11. Eastern Europe North-axis review

### 11.1 Why review is warranted
The current project North profile already includes:

- Estonia as North-primary;
- Ukraine as North-primary;
- Germany/Finland/Sweden/Denmark and other European anchors;
- Türkiye as the late North endpoint/gate.

Yet several countries already participate in the map's Baltic, Eastern Security and European Strategic Autonomy chains without a North orientation. This creates an interpretive gap inside the project's own established North system.

### 11.2 First review cohort
Review these first:

- Latvia (`LVA`)
- Lithuania (`LTU`)
- Poland (`POL`)
- Romania (`ROU`)
- Czechia (`CZE`)
- Slovakia (`SVK`)

Expected likely outcome, subject to the project's evidence/recovered-language review:

- Latvia: North primary or secondary, high/medium confidence;
- Lithuania: North primary or secondary, high/medium confidence;
- Poland: North primary or secondary, high confidence as Baltic/Eastern Security hinge;
- Romania: North secondary/bridge, medium-high confidence;
- Czechia: North secondary, medium-high confidence;
- Slovakia: North secondary, medium confidence.

These are project-interpretive classifications, not claims of sovereignty, command, consent or formal bloc membership.

### 11.3 Second review cohort
Do not auto-add, but explicitly review:

- Bulgaria (`BGR`)
- Hungary (`HUN`)
- Croatia (`HRV`)
- Slovenia (`SVN`)
- Moldova (`MDA`)

Their likely roles are bridge/secondary/provisional rather than assumed primary membership until project-specific evidence is recovered.

### 11.4 Balkans remain differentiated
Do not sweep Albania, Bosnia and Herzegovina, Serbia, Montenegro or North Macedonia into North merely because they are European or NATO-adjacent.

They can be reviewed later with country-specific rationale and overlap/frontier roles where appropriate.

### 11.5 Validator rule
Axis validation must require every new orientation to carry:

```text
axis
role
basis
confidence
note
```

and explicitly forbid creation of North orientation solely from `EU`, `NATO`, `OECD`, `Eastern Security` or any other empirical membership.

---

## 12. Browser behavior

This enrichment wave should not add a new permanent top-level control.

Existing surfaces improve automatically:

- **Stats** gains more comparable indicators;
- **Country card** gains richer IS/HAS/CAN/NEEDS/DEPENDS/BUILDS context from runtime;
- **Groups** reads consolidated empirical memberships;
- **Chains** gains real infrastructure context;
- **Gateways** gains associated infrastructure;
- **Impact** gains explicit infrastructure dependencies;
- **North Axis** reflects approved profile changes.

Optional coverage information may appear as quiet provenance text inside the selected-country card only if it materially helps users distinguish rich vs sparse records. Do not show a public 'completion score'.

---

## 13. TDD / validation contract

Create a dedicated validator before production changes.

It must test at least:

### Coverage ledger
- canonical sovereign count remains exactly 195;
- every canonical country has one active ISO3 owner;
- duplicate ISO3 detection catches a synthetic duplicate fixture;
- derived relationship/source counts reflect actual record content rather than stale counters;
- missing is never represented as numeric zero by the ledger state model;
- ledger records explain priority reasons rather than exposing a geopolitical score.

### Türkiye recovery
- exactly one active canonical `TUR` owner after migration;
- canonical `turkiye.json` retains/references Turkish-Straits, NATO/G20 and EU-trade legacy material with provenance;
- stale historical numeric observations are not silently relabeled current.

### Stats projection
- runtime exposes the newly selected World Bank indicators with source/year/missingness;
- missing indicators remain absent/unknown rather than zero;
- unit metadata is preserved.

### Membership authority
- NATO/BRICS/AUKUS/Five Eyes empirical membership comes from the canonical membership owner;
- compatibility layers do not maintain divergent manual member sets.

### Infrastructure
- infrastructure ids are unique;
- every asset has type, country/entity association, provenance and location/no-geometry policy;
- contextual membership does not create Impact dependency automatically;
- explicit dependencies can become typed Impact nodes/edges.

### North-axis review
- first-cohort additions, once approved in implementation plan, carry role/basis/confidence/note;
- validator forbids automatic Axis derivation from empirical group or chain membership;
- Russia/UK/etc. existing frontier semantics remain intact unless separately changed.

---

## 14. Implementation decomposition

This architectural design is intentionally implemented in sequential slices:

1. coverage/integrity validator + generated ledger;
2. duplicate recovery and coverage-counter repair, beginning with Türkiye;
3. additional comparable Stats projection;
4. empirical membership consolidation;
5. North-axis first-cohort review/update;
6. infrastructure registry foundation + first ports/maritime assets;
7. grid/cable/pipeline/freight expansion for Tier A countries;
8. Impact/runtime projection of explicit infrastructure dependencies;
9. Tier B regional multiplier enrichment;
10. full exact-head CI and merge.

The implementation plan may split infrastructure population into multiple commits/PRs if source volume becomes too large for one safely reviewable change, but all slices must obey this canonical design.

---

## 15. Out of scope for this first wave

- filling every deepening field for all 195 countries;
- a public completion/ranking leaderboard;
- synthetic national power or importance scores;
- automatic Axis classification from institutions;
- every global port/cable/pipeline;
- live AIS/shipping telemetry;
- complete company/beneficial-ownership graphs;
- complete AfCFTA/EU/world trade-flow ingestion;
- a new permanent 'Infrastructure' or 'Coverage' toolbox.

The measure of success is not field count. It is whether the existing map can answer materially more useful relational questions with sourced, correctly-owned data.

---

## Self-review

- No TBD/TODO placeholders.
- The design separates empirical enrichment, operational prioritization and project-interpretive Axis classification.
- Coverage is derived from actual content rather than stale counters.
- Duplicate records are recovered before new research.
- Infrastructure uses canonical ids and provenance rather than duplicated country prose.
- Impact only receives explicit dependency semantics.
- The first North-review cohort is defined, while second-tier and Balkan cases remain deliberately non-automatic.
- Scope is large but decomposable into ordered implementation slices without requiring a new front-end surface.
