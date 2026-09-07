# The Potato of Life — Living Atlas

This repository is the source archive and research engine for the Tim Dooley / Potatoverse project.

It now has two faces:

- **the archive:** Markdown documents, source records and structured data;
- **the interface:** a real HTML/CSS/JavaScript homepage that turns the architecture into a navigable public atlas.

## What is here

### Potatoverse

The mythic and creative layer: Potato of Life, Father, Son, Door, Ladder, Tree of Life, Root, Fruit, North Axis, Red/Blue Potato, Spudlight, Swamp, Drain and related symbols.

### Kingdom Atlas

A relationship ontology with 14 families: genealogical, institutional, financial, political, religious, intellectual, geographic, cultural, technological, information, social, symbolic, functional and mythological.

### European Economic Graph

The empirical layer mapping public finance, companies, ownership/control, debt, finance, procurement, infrastructure, energy, trade, technology, research, labour and strategic dependencies.

### North Programme

A research and policy framework for fiscal sustainability, productive investment, industrial capacity, energy security, technology, infrastructure and voluntary European cooperation.

### Evidence standard

Observed facts, calculations, estimates, scenarios, interpretations, historical claims, mythology and creative work are explicitly separated.

## Structured data

`data/nodes.json` — current node registry.

`data/relationships.json` — relationship registry with evidence classes and provenance fields.

`data/research.json` — sourced baseline facts plus the research queue.

These are intentionally small seed datasets. They are designed to be expanded node-by-node rather than replaced by a giant untraceable document.

## Website

`index.html` — public homepage.

`site.css` — visual system and responsive layout.

`site.js` — interactive graph interface connected to `data/nodes.json`.

## Current empirical baseline

Eurostat's Q4 2025 government-finance data gives the first fiscal anchor: EU debt 81.7% of GDP, France 115.6%, Belgium 107.9% and Denmark 27.9%. The same release reports EU government expenditure at 49.5% of GDP and revenue at 46.4% in 2025.

Primary source: https://ec.europa.eu/eurostat/fr/web/products-euro-indicators/w/2-22042026-bp

The European Commission describes the single market as a 27-country economic area built around free movement of goods, capital, services and people, with approximately €18 trillion GDP and 450 million consumers.

Primary source: https://commission.europa.eu/topics/single-market_en

The European Commission's Energy Union framework connects security of supply, an integrated internal energy market, efficiency and decarbonisation.

Primary source: https://energy.ec.europa.eu/strategy/energy-union_en

## The rule that governs everything

**Relationships first.**

A country is a node. A debt is a node. A company is a node. A symbol is a node. But the real object of study is the relationship between them.

The long-term objective is for the repository to behave like a living knowledge graph: searchable, visual, time-aware, source-aware and capable of supporting both creative exploration and serious research without confusing the two.
