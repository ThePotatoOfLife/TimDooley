# World Map Scalar Integrity Addendum

## Status
Amendment to `2026-09-12-world-map-coverage-enrichment-design.md` after live-map review reported missing population for many countries and zero population/area for Greenland.

This addendum is part of the same architectural enrichment wave and must be implemented before infrastructure population.

## 1. Confirmed defects

### 1.1 Ordinary country population is read from the wrong presentation path
`world-map/3d-country-card.js` currently reads Population from `record.observations.population` for default/contextual population display.

Many canonical enriched records instead retain valid population in legacy/top-level structures such as:

```json
"population": {
  "value": 261800000,
  "source": "World Bank WDI"
}
```

while `observations` remains empty.

The generated demography builder already has an external UN-WPP fallback, but the compact country card does not use that generated population as its primary presentation authority.

Result: many countries show `—`/missing population even though population exists elsewhere in the map data pipeline.

### 1.2 Greenland population exists but is isolated in the entity owner
`data/world-map-entities.json` correctly owns Greenland population:

```text
56,740
reference date 2026-01-01
Statistics Greenland
```

However `scripts/build_world_demography.py` iterates only the canonical 195-country index. Greenland is not projected into the generic demography runtime used by ordinary hover/population surfaces.

### 1.3 Greenland area is not owned at all by the entity scalar path
`scripts/build_world_country_facts.py` also iterates only the canonical 195-country index.

`GRL` therefore receives no ordinary `world-country-facts` area observation. Generic hover then falls through to raw renderer/runtime area properties, which can display as zero.

The official Statistics Greenland reference value is:

```text
Greenland total area: 2,166,086 km²
ice-free area: 410,449 km²
```

The map's ordinary `Area` stat should use total area and preserve the definition explicitly. Ice-free area may be exposed as a separate later observation; it must not silently replace total area.

## 2. Correct architecture: one scalar resolver for countries and entities

Do not patch Greenland separately in three UI files.

Introduce/extend the shared runtime scalar contract so every renderable map entity can answer:

```js
populationObservation(code)
areaObservation(code)
scalarObservation(code, metricId)
```

Expected population resolution for canonical countries:

1. canonical `observations.population` when present and valid;
2. compatible canonical legacy/top-level population field, preserving its source/date semantics;
3. generated UN WPP fallback from the demography runtime;
4. unknown (`null`) — never numeric zero.

Expected population resolution for non-sovereign registered entities:

1. entity-owned population observation;
2. generated entity demography projection if available;
3. unknown.

Expected area resolution for canonical countries:

1. canonical geography area/land-area field with explicit definition;
2. generated country-facts fallback with source/definition;
3. unknown.

Expected area resolution for registered entities:

1. entity-owned area observation;
2. generated entity-facts projection;
3. unknown.

## 3. Greenland canonical scalar record

Extend `GRL` in `data/world-map-entities.json` with an explicit area observation:

```json
"area": {
  "value": 2166086,
  "unit": "km²",
  "definition": "total area",
  "reference_period": "2025",
  "source": "Statistics Greenland — Greenland in Figures 2025",
  "source_url": "https://stat.gl/publ/EN/GF/2025/pdf/Greenland%20in%20Figures%202025.pdf"
}
```

Population remains:

```json
"population": {
  "value": 56740,
  "reference_date": "2026-01-01",
  "source": "Statistics Greenland"
}
```

No value may be inferred from polygon coordinate area.

## 4. Generated presentation snapshots must include registered entities

### Demography
`build_world_demography.py` keeps the 195-country `countries` plane but gains a separate `entities` plane populated from `world-map-entities.json`.

It must not increment canonical country population coverage with territories.

### Facts
`build_world_country_facts.py` similarly gains a separate `entities` plane for identity/geography display facts.

Greenland must project:

```text
name: Greenland
capital: Nuuk
area: 2,166,086 km²
definition: total area
entity_type: self-governing-territory
```

## 5. Country card and hover

The country card must stop calling only `observation(record, 'population')` for population presentation.

Both country card and hover should ask the shared scalar/entity runtime first.

Required behavior:

- an ordinary country with valid top-level/fallback population shows population;
- Greenland shows 56.7K / 56,740 depending on compact/full surface;
- Greenland Area shows 2,166,086 km²;
- missing data shows `—`, never `0` merely because a code path failed;
- provenance/year/definition remains available to evidence/hover surfaces.

## 6. Stat layer behavior

`stat.population` and `stat.area` must resolve the same scalar cells used by cards/hover rather than relying on a separate raw feature property authority.

This removes the current class of disagreement where:

```text
Axis says Greenland = valid entity
Entity card says population exists
Population stat says 0/missing
Area stat says 0
```

One entity must have one resolved scalar answer per metric.

## 7. Eastern Europe North status

The Eastern Europe North review from the parent design is **not implemented yet**.

The first implementation cohort remains:

```text
LVA Latvia
LTU Lithuania
POL Poland
ROU Romania
CZE Czechia
SVK Slovakia
```

The implementation plan should treat this after scalar correctness and coverage integrity, before the larger infrastructure wave.

No country is added to North purely because it belongs to NATO/EU or an empirical functional chain.

## 8. Revised implementation order

The enriched map should now proceed in this order:

1. **Scalar correctness / entity parity**
   - fix ordinary-country population presentation;
   - add Greenland total area;
   - project registered entities into demography/facts snapshots;
   - make card/hover/Stats consume one scalar resolver;
   - validate no missing scalar becomes zero.

2. **Coverage/integrity ledger**
   - derive coverage from actual content;
   - detect duplicate ISO3 owners;
   - repair stale counters.

3. **Türkiye canonical recovery**
   - consolidate usable `turkey.json` material into `turkiye.json` with provenance/staleness.

4. **Eastern Europe North review**
   - LVA/LTU/POL/ROU/CZE/SVK first cohort;
   - explicit role/basis/confidence/note.

5. **Expand already-collected Stats**
   - growth, inflation, unemployment, labour-force participation, life expectancy, fertility, urbanization, internet, CO2 and comparable PPP/poverty where defensible.

6. **Membership authority consolidation**
   - NATO, BRICS, AUKUS, Five Eyes into canonical empirical owner.

7. **Infrastructure population**
   - ports/terminals;
   - grids/interconnectors;
   - cables/IXPs;
   - pipelines/LNG/storage;
   - rail/freight/customs;
   - deeper gateways.

8. **Impact integration**
   - only explicit infrastructure dependencies become causal edges.

9. **Tier-A/Tier-B country enrichment**
   - use coverage ledger as the rolling backlog.

## 9. Required regression tests

- canonical sovereign count remains exactly 195;
- Greenland remains a non-sovereign map entity and North-primary project profile;
- `populationObservation('GRL').value == 56740`;
- `areaObservation('GRL').value == 2166086`;
- Greenland area definition is `total area`;
- Greenland population/area never render as numeric zero unless an authoritative source actually reports zero;
- representative ordinary country with top-level population but empty `observations` still resolves population;
- population/area Stats, hover and card use the same resolved value;
- missing scalar resolves to `null`/`—`, not `0`;
- first Eastern Europe North cohort remains unmodified until its explicit implementation slice.

## Self-review

- This amendment fixes a shared scalar-authority defect rather than special-casing Greenland in UI code.
- It preserves the 195-country sovereign model.
- It distinguishes Greenland total area from ice-free area.
- It moves scalar correctness ahead of enrichment so new data cannot enter inconsistent presentation paths.
- It does not alter the approved empirical-vs-project Axis firewall.
