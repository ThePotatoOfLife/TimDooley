# BIS Banking and Bond Data

The finance foundation now has a dedicated BIS layer at `data/bis-banking-bond-data.json`.

## Four different views of the financial system

**Locational Banking Statistics (LBS)** are residence-based. They tell us where a banking office books a position and where its counterparty resides. The data are unconsolidated and include intragroup positions. That makes LBS the right source for cross-border banking flows and currency/instrument geography.

**Consolidated Banking Statistics (CBS)** are nationality-based. They consolidate the worldwide positions of banking groups according to the country where the controlling parent is headquartered and exclude intragroup positions. CBS are the better tool for country-risk exposure and can show both immediate-counterparty and guarantor/ultimate-risk views.

**Debt Securities Statistics (DSS)** cover tradable debt issued in domestic and international markets from national sources. The model retains issuer sector, currency, maturity, market and valuation because countries do not all report securities on the same valuation basis.

**International Debt Securities (IDS)** are BIS-compiled security-level data for bonds and other debt securities issued outside the issuer's local market. They are available by issuer residence and nationality, currency, maturity and interest-rate type. IDS identify issuers, not holders; they must not be used to invent a creditor.

## Latest seed data

The current release vintage is 14 September 2026.

At end-Q1 2026 the LBS record about **$47.622 trillion** of cross-border claims and **$42.006 trillion** of cross-border liabilities across reporting banking offices. BIS separately describes cross-border bank credit at **$39.5 trillion**, up **$1.7 trillion** during Q1.

The CBS show **$43.383 trillion** of foreign claims on an immediate-counterparty basis across all bank nationalities at end-Q1 2026. International claims were **$27.416 trillion**, of which about **$12.445 trillion** had remaining maturity of up to one year.

The BIS-compiled IDS show **$35.096 trillion** of international debt securities outstanding in Q2 2026, at face value. About **$4.699 trillion** had remaining maturity of up to one year.

These figures are stored as global seed observations. They prove the semantics and give the World Map a current aggregate baseline; they are not a substitute for the bilateral and country-level series still to be materialized.

## Why the datasets cannot be added together

LBS and CBS overlap economically but use different geography and consolidation rules. LBS follows the residence of the booking office and includes positions between offices of the same banking group. CBS follows the nationality of the parent banking group and removes intragroup positions.

DSS and IDS likewise overlap: DSS aims to cover total tradable debt, while IDS focuses specifically on securities issued outside the issuer's local market. Their valuation and source construction can differ.

The atlas therefore stores the dataset identity on every observation and relation.

## World Map direction

The eventual finance view can use:

- **LBS arrows:** banking office location → counterparty residence;
- **CBS arrows:** banking-group nationality → counterparty country;
- **DSS polygons/cards:** issuer-country debt securities by sector, currency, maturity and market;
- **IDS issuer structure:** international bonds by residence/nationality, currency, maturity and rate type.

The map will not draw an IDS bond arrow to a creditor because IDS do not identify holders.

## North Axis use

North remains a project-defined filter over the empirical BIS data. The BIS records themselves are unchanged.

That makes it possible to calculate:

- North-to-North versus North-to-rest-of-world bank claims;
- liabilities of North residents to reporting banks elsewhere;
- exposures carried by banking groups headquartered in North jurisdictions;
- currency composition of international borrowing;
- short-term refinancing concentrations;
- government versus bank versus corporate debt-security stocks;
- immediate-counterparty versus guarantor-basis country-risk differences.

This is the layer that begins to turn “who owes whom?” into a real network rather than a national debt scoreboard.
