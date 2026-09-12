# World Map System Intelligence Design

## Status
Continuation of the approved World Map world-systems architecture, 2026-09-12.

## Goal
Make the hidden capability / dependency / resilience / chains / projects architecture materially useful in the ordinary World Map without adding another permanent toolbox or inventing synthetic geopolitical scores.

## Core rule
The browser should expose evidence the repository actually owns. A country may have explicit capabilities, typed dependencies, active builds, functional-chain roles and gateway positions. Missing evidence remains unknown. The system must not turn sparse evidence into a numerical capability, alignment or resilience score.

## Runtime country system context
Every canonical 195-country runtime record receives a `systems` object with:

- `capabilities`: explicit strings derived only from canonical country-record fields such as `energy_and_resources.strategic_assets`, `trade_and_value_chains.strategic_value_chains`, or a future explicit capability field.
- `dependencies`: explicit dependency relationships/fields only; absence means unknown, not independent.
- `builds`: sourced canonical observations whose keys explicitly indicate a project/tender/build/expansion/planned phase.
- `chains`: IDs of functional chains already owned by `data/world-system-chains.json`.
- `gateways`: IDs of sourced gateway/chokepoint records directly associated with the country.
- `resilience`: evidence context only. It records which kinds of evidence are present and states that no aggregate resilience score is inferred.

The generated runtime also reports coverage counts for these system-context fields.

## Gateway layer
Create `data/world-map-gateways.json` as the first empirical gateway owner.

Initial records are high-connectivity maritime chokepoints for which a current common source exists:

- Strait of Malacca
- Strait of Hormuz
- Suez Canal / SUMED corridor
- Bab el-Mandeb
- Danish Straits
- Turkish Straits
- Panama Canal
- Cape of Good Hope route

The first observation uses the latest available EIA 2026 chokepoint table at implementation time. Each record carries:

- `id`, `label`, `type`
- approximate map-anchor `coordinates` with `coordinate_precision: approximate-center` and an explicit warning that coordinates are for visualization, not navigation
- `countries`: directly bordering / host country ISO3 codes used for contextual display
- `systems`
- `observation` with value, unit, period, source, source URL
- `description`
- `epistemic_type: observed`

Gateway records are empirical. The symbolic Door analogy stays outside the empirical record.

## Browser behavior

### Country card
Add a compact `System role` section only when evidence exists:

- `Can` — up to three explicit capability tags
- `Depends` — up to two explicit dependency tags
- `Building` — up to two sourced project/build tags
- `Gateways` — up to two gateway labels

Functional chains remain their own compact section.

Do not show a noisy empty section.

### Contextual gateway points
Add a lightweight `3d-gateways.js` module to the ordinary boot path after the shared runtime exists.

When a country is selected:

- show only gateway points directly associated with that country;
- clear them on deselection;
- keep labels hidden at low zoom and reveal them only when useful;
- clicking a gateway point may show a compact popup containing label, type, latest observed transit value/period and source name;
- gateway points must not create a new normal top-bar button.

## Registry
Promote these existing contextual families to current where their runtime implementation now exists:

- `derived.capability`
- `derived.dependency`
- `derived.resilience`

Add contextual records for:

- `derived.builds`
- `gateway.context`

All remain `ordinary:false` / contextual and therefore do not create normal navigation clutter.

## Evidence rules

1. `nations-economies-coupled.json` and similar legacy unsourced strategic prose must not become a canonical browser source merely because it contains rich-looking fields.
2. Capability extraction requires explicit canonical country fields; no capability is inferred from GDP, Axis orientation, or institutional membership alone.
3. Dependency extraction requires an explicit dependency field or typed dependency relationship.
4. Build extraction requires a sourced observation with an explicitly project/build-like key.
5. Gateway throughput is dated and sourced; it is not treated as timeless capacity.
6. Resilience is not numerically scored in this wave.

## Validation
Add `scripts/validate_world_map_system_intelligence.py` and wire it into repository quality checks. It must fail if:

- gateway records are absent, unsourced, lack valid map anchors, or contain noncanonical ISO3 country codes;
- generated runtime does not provide `systems` for all 195 countries;
- runtime contains a `capability_score`, `resilience_score`, or similar synthetic score;
- system coverage metadata is absent;
- contextual runtime APIs are absent;
- country card does not consume system context;
- gateway module is not booted contextually;
- contextual registry entries are missing/current-owner drift occurs.

## Out of scope for this wave

- full global port inventory
- full cable landing-station inventory
- full pipeline / grid interconnector inventory
- GLEIF or TED bulk ingestion
- FIGARO input-output ingestion
- synthetic strategic-power score
- synthetic resilience score
- permanent new top-level map menu
