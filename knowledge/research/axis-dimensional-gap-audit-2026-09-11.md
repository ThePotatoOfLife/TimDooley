# Axis / Relational Atlas — Dimensional Gap Audit

Updated: 2026-09-11  
Status: research/design note; not a canonical empirical claim

## Why this audit exists

The project now has a strong D1-D11 analytical/project-symbolic spine, a time contract, a relationship verticality contract, a measurable-safe flow grammar, pairwise relational state, and spiral geometry research. The remaining risk is to make D1-D11 carry too many unrelated meanings.

The key distinction is:

- **D1-D11** = analytical/project-symbolic depth operators.
- **orthogonal observables** = measurable coordinates that may exist at any D-level.

A relation can therefore be D4 empirically, D6 historically, D8 compositionally and D10 systemically while also having independent values for capacity, utilization, latency, confidence, dependence, reversibility, resilience and scale.

The new machine-readable owner for these cross-cutting observables is `data/relational-observable-dimensions.json`.

## Major gap 1 — higher-order relations

The current pairwise edge model is insufficient for relations that only exist collectively.

Examples:

- a treaty regime signed by many states
- a coalition or alliance whose collective rule is not equivalent to every pair being allied independently
- a research consortium
- a family or board decision
- a standards body
- an ownership syndicate
- a multi-country electricity market
- a production chain whose effect depends on several participants together

Network science increasingly distinguishes ordinary pairwise graphs from higher-order systems represented by hypergraphs or simplicial complexes. Higher-order interactions can produce collective dynamics not recoverable from a set of independent pairwise links.

Atlas consequence:

- create a genuine group-relation object with three or more participants;
- retain each participant's role;
- store group-level governance, entry/exit, flows and thresholds;
- allow a pairwise visualization only as a declared derived projection with an information-loss warning.

Implemented contract: `data/relational-hyperedge-state.schema.json`.

Strongest Axis fit:

- D5: group accession/activation/decision thresholds
- D8: Rooms/composition/federation
- D9: coordinated relay among multiple participants
- D10: collective system effect

Research references:

- Battiston et al., *The physics of higher-order interactions in complex systems*, Nature Physics 17 (2021), https://doi.org/10.1038/s41567-021-01371-4
- Battiston et al., *Collective dynamics on higher-order networks*, Nature Reviews Physics 8 (2026), https://www.nature.com/articles/s42254-025-00916-3

## Major gap 2 — capacity versus realized flow

A link may exist without being fully used.

Keep separate:

- stock
- flow
- rate
- capacity
- utilization
- reserve margin
- balance

Examples:

- gas pipeline capacity vs gas actually transported
- interconnector capacity vs electricity flow
- port capacity vs throughput
- credit line vs amount drawn
- military capability vs deployment
- treaty commitment vs activated commitment
- data bandwidth vs traffic

Visual opportunity:

`outer tube/corridor = documented capacity`

`inner line/particles = realized flow`

`gap = slack/reserve capacity`

This is much more meaningful than one line width trying to express all three concepts.

## Major gap 3 — latency, queueing and congestion

The Atlas has flow and relay ideas, but delay needs to become first-class.

Useful observables:

- latency
- throughput
- queue/backlog
- utilization
- bottleneck
- loss rate
- lead/lag

Strongest Axis fit:

- D5: capacity threshold / gate
- D9: relay delay and fidelity
- D10: bottleneck/system performance

Never infer congestion from visual crowding; a capacity model is required.

## Major gap 4 — reversibility and hysteresis

A system can return to the same headline state without returning to the same internal state.

Questions:

- Is the relation reversible?
- What condition reverses it?
- Is the return path different from the outward path?
- What switching cost remains?
- What memory persists after apparent restoration?

This is particularly important for D3 and D6.

The spiral becomes more meaningful here: one revolution can return to a superficially similar state while radius, pitch, composition or evidence shows what changed.

## Major gap 5 — scale

Scale is currently partly implicit inside Axis/change-of-description, but it needs explicit measurement metadata.

Distinguish:

- micro / meso / macro
- local / subnational / national / regional / global
- firm / sector / country / alliance / world-system

A relation can reverse interpretation across scale. A supplier can be replaceable for one company yet systemically critical for an entire sector.

D10 aggregation should therefore always report scale and aggregation loss.

## Major gap 6 — causal status

The project has already protected against treating adjacency as causation, but causal status should be machine-readable.

Useful classes:

- association
- temporal precedence
- mechanistic hypothesis
- causal inference
- experimental/quasi-experimental evidence
- scenario intervention
- unknown

A path `A -> B -> C` in the graph is not automatically a causal chain.

Research reference:

- Runge et al., *Identifying causal gateways and mediators in complex spatio-temporal systems*, Nature Communications 6 (2015), https://www.nature.com/articles/ncomms9502

## Major gap 7 — resilience as a perturbation question

Resilience is not another country score. It asks what remains functional after a defined disturbance.

Candidate observables:

- redundancy
- alternate paths
- service loss after edge/node removal
- cascade depth
- recovery time
- reserve margin
- single-point-of-failure exposure
- robustness under removal

D2 can show cascading failure and lock-in; D7 can show capacity regenerated after disruption; D8 can show redundant composition; D10 can show system-wide robustness.

Research reference:

- Artime et al., *Robustness and resilience of complex networks*, Nature Reviews Physics 6 (2024), https://www.nature.com/articles/s42254-023-00676-y

## Major gap 8 — tipping points and early-warning signals

D5 Door becomes much more rigorous when some thresholds are empirically modeled.

Possible signals in suitable domains include increasing variance, autocorrelation/critical slowing down or other domain-specific indicators before a regime shift.

Strict rule: do not show “tipping proximity” unless the system has a validated model and sufficient time-series data.

Research reference:

- Scheffer et al., *Early-warning signals for critical transitions*, Nature 461 (2009), https://www.nature.com/articles/nature08227

## Major gap 9 — counterfactual sensitivity

A relationship becomes much more intelligible when the Atlas can ask:

> What happens if this edge disappears?

Possible outputs:

- substitute paths
- rerouting cost
- service loss
- exposure change
- recovery requirement
- newly isolated nodes

This should always be labeled analysis/scenario, not observation.

This could become one of the strongest D10 tools because it separates a visually central relation from a genuinely critical one.

## Major gap 10 — accounting / conservation identities

Some domains have real accounting constraints and the Atlas should exploit them.

Examples:

- energy: supply = use + storage change + losses within a defined boundary
- finance: balance-sheet assets/liabilities/equity identities
- population: opening stock + inflows - outflows = closing stock, modulo definitions
- material systems: source/sink/storage balances

This makes missing or inconsistent data detectable.

Important firewall: do not transfer physical conservation language into social, theological or symbolic relations merely because it is aesthetically appealing.

## Major gap 11 — observability is not controllability

A node can be easy to observe but difficult to influence, or structurally central but dynamically irrelevant to an intervention.

The current D10 formal lens already recognizes this distinction. It should remain a hard gate: do not label a node a leverage point or driver node unless a dynamical model supports the claim.

Research references:

- Liu, Slotine & Barabási, *Controllability of complex networks*, Nature 473 (2011), https://www.nature.com/articles/nature10011
- Leitold et al., *Controllability and observability in complex networks — the effect of connection types*, Scientific Reports 7 (2017), https://www.nature.com/articles/s41598-017-00160-5

## Major gap 12 — multiplex coupling across relation families

The same pair/group can be connected through trade, debt, energy, migration, research, security and culture simultaneously.

The important future question is not merely whether those layers exist but whether one layer depends on or changes another.

Examples:

- energy dependence changes political bargaining
- financial exposure changes vulnerability to sanctions
- migration/diaspora changes remittance and information networks
- standards alignment changes technology trade
- research ties create later industrial capability

Multilayer-network research warns that aggregating these layers can hide or distort system dynamics.

Research references:

- De Domenico et al., *The physics of spreading processes in multilayer networks*, Nature Physics 12 (2016), https://www.nature.com/articles/nphys3865
- De Domenico, *More is different in real-world multilayer networks*, Nature Physics 19 (2023), https://www.nature.com/articles/s41567-023-02132-1

## Major gap 13 — synchronization and phase, but only when real time series exist

Synchronization can be meaningful for:

- electricity grids
- recurring market/activity cycles
- transport schedules
- seasonal demand
- communications
- repeated institutional cycles

It should not be used for vague emotional/spiritual “frequency.”

Research reference:

- Ghosh et al., *The synchronized dynamics of time-varying networks*, Physics Reports 949 (2022), https://doi.org/10.1016/j.physrep.2021.10.006

## Major gap 14 — uncertainty should influence rendering without becoming strength

Evidence confidence, data coverage, missingness and freshness should be visually independent from relation magnitude.

Candidate grammar:

- width = compatible magnitude
- motion = directed rate
- outer shell = capacity
- inner flow = realized use
- dashing = inferred/estimated relation
- fading = freshness or confidence, but only one at a time and explicitly labeled
- spiral = recurrence/dynamics
- vertical projection = Axis role

This prevents one visual channel from trying to carry five meanings.

## Major gap 15 — derived relation versus canonical relation

Many future “relations” will actually be analysis products:

- community membership
- centrality
- observed-vs-expected trade residual
- systemic importance
- dependency concentration
- resilience under removal
- trophic/upstream position
- inferred causal gateway

These need derivation metadata:

- input IDs
- method
- time scope
- assumptions
- uncertainty
- source coverage
- projection/information loss

They should never silently become canonical edges.

## Recommended implementation sequence after this audit

1. Keep D1-D11 unchanged as the vertical analytical spine.
2. Adopt `relational-observable-dimensions.json` as the cross-cutting metric vocabulary.
3. Allow higher-order group relations through `relational-hyperedge-state.schema.json`.
4. Upgrade one real bilateral dataset first — preferably trade — with stock/flow semantics, direction, period and evidence.
5. Add capacity/utilization on one infrastructure family.
6. Make selected-edge inspection show observable coordinates before Axis interpretation.
7. Add D6 spiral only for dated recurrence/change.
8. Add D8 group/hyperedge composition rather than rendering every institution as a clique.
9. Add counterfactual edge-removal analysis in a clearly labeled scenario mode.
10. Add resilience and tipping analysis only after domain-specific models exist.
11. Add D10 controllability/observability only for systems with explicit dynamics.
12. Add D11 objective comparison last, because its conclusions depend on all lower measurements and declared criteria.

## Architectural conclusion

The Atlas should not ask for one number that says how high, good, powerful or important a relation is.

A mature relation is better represented as a vector:

`R = (order, family, evidence, time, quantity semantics, direction, magnitude, capacity, utilization, dependence, delay, reversibility, dynamics, resilience, causal status, agency, scale, Axis projections)`

D1-D11 then become operators over that richer object rather than substitutes for missing data.
