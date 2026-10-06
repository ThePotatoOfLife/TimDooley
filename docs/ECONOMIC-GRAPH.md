# European Economic Graph

The European Economic Graph is the empirical research layer of the North Programme. It is designed as a living dataset, not a one-time report.

## 1. What the graph actually maps

The graph follows relationships among governments, EU institutions, central banks, commercial banks, companies, owners, financial instruments, infrastructure, energy systems, research institutions, labour markets and strategic dependencies.

A useful record is:

`source → relationship → target`

with:

`date · jurisdiction · source · evidence class · confidence · value · currency · notes`

The graph therefore asks questions such as:

- Who owns or controls the asset?
- Who finances it?
- Who buys from it?
- Which infrastructure does it depend on?
- Which regulation governs it?
- Which country bears the fiscal obligation?
- Which supply chain breaks if the relationship fails?
- Which other nodes become more or less important when the relationship changes?

## 2. Initial empirical baseline — 2025

Eurostat's government-finance release for Q4 2025 reports EU government debt at **81.7% of GDP**. France stood at **115.6%**, Belgium at **107.9%**, and Denmark at **27.9%**. France and Belgium therefore enter the North Programme as materially different fiscal cases from Denmark. The same release reports EU government expenditure at **49.5% of GDP** and revenue at **46.4%** in 2025, with the EU deficit at **3.1% of GDP**. Source: Eurostat, 22 April 2026.

Source: https://ec.europa.eu/eurostat/fr/web/products-euro-indicators/w/2-22042026-bp

These numbers are descriptive observations. They do not by themselves identify which expenditures should be reduced, which taxes should change, or what policy would be optimal.

## 3. The single market as a network

The EU single market is not simply a trade statistic. It is a relationship system. The European Commission describes it as guaranteeing free movement of goods, capital, services and labour/people across the EU and reports a market of about 450 million consumers and approximately €18 trillion in GDP.

Source: https://commission.europa.eu/topics/single-market_en

For the graph, this creates several distinct edge families:

`state → member-of → EU`

`company → sells-into → single-market`

`worker → may-work-in → member-state`

`capital → crosses-border-within → single-market`

`goods → move-through → internal-market`

The graph should preserve these as separate relationships rather than collapsing them into a single label such as “integration”.

## 4. Energy as infrastructure + market + dependency

The European Commission's Energy Union framework combines security of supply, an integrated internal energy market, energy efficiency, decarbonisation and research/innovation. The integrated-market dimension explicitly depends on adequate infrastructure and the ability to move energy across borders.

Source: https://energy.ec.europa.eu/strategy/energy-union_en

The graph should consequently connect:

`resource → generation → grid → market → industry → household`

while separately tracking:

`country → import-dependence → supplier`

`grid → interconnector → neighbouring-grid`

`industry → electricity-demand → generation-system`

`policy → regulation → market`

## 5. Priority country cases

### France

Research questions:

- How is general government spending distributed across functions and levels of government?
- Which expenditure is legally committed, politically discretionary or economically productive?
- How do pensions, healthcare, transfers and public administration interact?
- Which public investments have high long-run productivity value?
- Which tax expenditures duplicate explicit subsidies or public programmes?
- How do French energy, nuclear, grid and industrial policies interact with European systems?

Baseline fiscal observation: 115.6% debt/GDP at end-2025; 2025 deficit 5.1% of GDP.

### Belgium

Research questions:

- Which responsibilities are federal, regional or community-level?
- Where do administrative competences overlap?
- How does public expenditure map onto service delivery?
- How do pensions, healthcare and transfers interact with the fiscal position?
- How does Belgium's infrastructure and logistics position connect it to the wider European economy?

Baseline fiscal observation: 107.9% debt/GDP at end-2025; 2025 deficit 5.2% of GDP.

### Denmark

Denmark is useful as a contrasting fiscal and institutional case rather than as a template to copy automatically. Its end-2025 government debt ratio was 27.9% of GDP and its 2025 general government balance was positive at 2.9% of GDP according to Eurostat.

The research question is therefore not “how can France become Denmark?” but “which institutional, demographic, fiscal and economic relationships help explain the difference, and which are transferable?”

## 6. Graph layers

The first implementation should grow into these connected datasets:

1. Countries and jurisdictions
2. EU institutions
3. Public finances
4. Government bonds and debt holders
5. Banks and financial intermediaries
6. Companies and ownership/control
7. Procurement and public funding
8. Energy generation and infrastructure
9. Ports, rail, roads and telecommunications
10. Trade and value chains
11. Technology and research
12. Labour and skills
13. Strategic dependencies
14. Geopolitical relationships

## 7. Evidence classes

- **Observed** — directly supported by a reliable source.
- **Calculated** — derived transparently from observed values.
- **Estimated** — modelled or approximate.
- **Scenario** — conditional projection.
- **Interpretation** — analytical reading.
- **Historical** — documented past event or relationship.
- **Mythological** — Potatoverse material.

The same node can have relationships in several evidence classes. The interface must show the class rather than silently mixing them.

## 8. First graph entries

The structured seed dataset lives in `data/nodes.json` and `data/relationships.json`. Research evidence and the research queue live in `data/research.json`.

The website is deliberately only showing a small visible graph at first. The underlying architecture is designed to grow without changing the model.

## 9. Next research pass

The highest-value next step is not adding random facts. It is deepening existing relationships: France expenditure, Belgian institutional structure, European energy infrastructure, public procurement, strategic technology dependencies and North Atlantic infrastructure.
