# World Finance Foundation

## Purpose

The World Finance Foundation is the empirical base layer for answering a deceptively difficult question: **who owes whom, through what instrument, in what currency, and through which institution?**

The canonical machine-readable seed is `data/world-financial-system-foundation.json`. It sits underneath the existing finance/debt blueprint and is intended to feed the World Map later without turning the map into a collection of unsourced arrows.

## The core distinction

Finance has several different kinds of authority that must not be collapsed:

- **Monetary authority** — the institution that issues or governs a currency and monetary policy.
- **Fiscal issuer** — the government or supranational institution legally responsible for a bond or loan.
- **Debt manager** — the institution that executes borrowing and portfolio management.
- **Creditor / holder** — the lender or holder of a claim.
- **Custodian / intermediary** — an institution or jurisdiction through which a holding is recorded.
- **Settlement infrastructure** — the system through which cash or securities move.
- **Reserve holder** — a monetary authority holding reserve assets.

The ECB can therefore be the monetary authority for the euro while France, Germany, Italy and the other euro-area governments remain distinct sovereign debt issuers. Likewise, Danmarks Nationalbank manages Danish central-government debt on behalf of the Minister of Finance while Denmark retains the krone and fixes it closely to the euro.

## Seed institutions

The first institutional registry includes the Federal Reserve, ECB/Eurosystem, Danmarks Nationalbank, Bank of England, Bank of Canada, Norges Bank, Sveriges Riksbank, Bank of Japan and Reserve Bank of Australia.

The euro record contains the 21 euro-area EU member states after Bulgaria's adoption of the euro on 1 January 2026. Denmark remains outside the euro area; the krone's central rate is recorded as 7.46038 DKK per EUR under Denmark's fixed-exchange-rate policy.

## Debt is not one number

The data model deliberately keeps these concepts separate:

- general-government gross debt;
- central-government debt;
- U.S. federal debt held by the public;
- total U.S. public debt outstanding;
- debt securities outstanding;
- cross-border bank claims;
- official reserve assets;
- custody-reported foreign holdings of U.S. Treasury securities.

This matters immediately in Denmark: Eurostat reported Danish general-government gross debt at 26.8% of GDP in 2026 Q1, while Danmarks Nationalbank reports central-government debt at DKK 235.4 billion, or 7.6% of GDP, at end-2025. Both can be correct because they measure different institutional scopes.

## Creditor resolution

“Who owns the debt?” is often less precise than the available evidence. The foundation therefore uses a five-level creditor-resolution ladder:

1. named counterparty;
2. holder sector or country;
3. custody location;
4. confidential aggregate;
5. unknown.

Treasury International Capital country tables are useful but primarily custodial, so a country shown in the table is not automatically the ultimate beneficial owner. IMF COFER has the opposite limitation: it provides powerful global reserve-currency aggregates while individual economy submissions remain confidential.

## Current seed observations

The foundation stores a small set of sourced snapshots to prove the schema rather than pretending to be a complete time-series database.

Eurostat's 2026 Q1 release reports general-government gross debt at 88.9% of GDP for the euro area and 82.9% for the EU. Denmark was 26.8%.

IMF COFER reported USD 13.10 trillion in global official foreign-exchange reserves in 2026 Q1, with the U.S. dollar at 57.13% of allocated reserves. The aggregate must not be used to infer an individual country's unpublished reserve portfolio.

The U.S. Treasury's July 2026 TIC table reports custody-attributed Treasury holdings of USD 1,103.9 billion for Japan, USD 998.3 billion for the United Kingdom and USD 618.0 billion for mainland China. These are useful edges only when the custody caveat remains attached.

The European Commission's 2026 funding plan targets EUR 180 billion of EU-Bond issuance across the year, including EUR 80 billion in long-term issuance in the second half. Those securities are modeled as Commission/EU borrowing rather than silently assigned to a member state's national debt.

## North Axis bridge

`data/world-axis-fields.json` remains the source for the project-defined North field. The finance layer does **not** redefine countries as being legally or politically controlled by that field. Instead, North can become an aggregation lens over empirical financial records.

That allows questions such as:

- Which North jurisdictions share the euro and which retain national currencies?
- Where does ECB/Eurosystem monetary authority overlap with national fiscal authority?
- Which non-euro North central banks connect to Eurosystem settlement infrastructure?
- Who holds the bonds issued by North jurisdictions, to the extent the evidence resolves the creditor?
- Which North banking systems have claims on counterparties outside North, and vice versa?
- What currency and maturity exposures create refinancing dependencies?
- Which obligations are sovereign, supranational, bank, corporate or household?

Norway is already a useful example of why this graph matters: Norges Bank is outside the euro area but has active institutional links to Eurosystem settlement infrastructure. Such a connection is a real financial edge, not a claim of euro membership.

## Map integration

The intended World Map projection is:

- **points** for central banks, treasuries, debt-management offices and settlement institutions;
- **lines** for sourced directed holdings, debt, lending, liquidity and settlement relationships;
- **polygons** for currency areas and comparable scalar layers such as debt/GDP;
- **inspectors** that expose the debt concept, issuer, creditor resolution, currency, instrument, period, unit, source and caveats.

No debt arrow should be rendered merely because two countries are financially related. A map edge should exist only when the direction and meaning are explicit.

## Next data passes

The highest-value extensions are BIS international banking claims, BIS debt-securities statistics, Eurostat government-debt breakdowns, Treasury holder-sector/TIC history, ECB and national-central-bank balance-sheet categories, supranational issuers such as the EU and ESM, and dated bond/maturity structures.

This is the base from which the site can eventually answer “who owes whom?” without confusing money, debt, custody, ownership, settlement, reserves and political geography.
