# Financial Institution Gap Closure

The finance graph had central banks, currencies and debt instruments, but it was still missing several institutions that explain **how obligations actually move through the system**. The canonical role map is now `data/world-financial-institution-topology.json`.

## The test for adding an institution

An institution belongs in the graph when removing it makes an important financial relationship impossible to explain.

That produces six distinct missing layers.

### 1. Who actually holds the securities?

BIS IDS is excellent for the issuer side of international bonds but does not identify holders. The IMF's Portfolio Investment Positions by Counterpart Economy dataset closes much of that gap by recording cross-border portfolio assets by the residence of the issuer and by instrument class.

This becomes the preferred country-to-country **holder-side** complement to BIS bond issuance. It still does not identify a specific pension fund, bank or household unless another source does.

### 2. Who sits between markets and projects?

Development banks create a multi-leg chain:

`shareholder capital → development bank → bond market funding → loan/guarantee → government/company/project`

The first North/global set is IMF, IBRD, IDA, EIB, NIB and EBRD.

NIB is particularly important to North because it is actually owned by Denmark, Estonia, Finland, Iceland, Latvia, Lithuania, Norway and Sweden. EIB is the EU member-state policy bank. EBRD connects European and other shareholders to transition, private-sector and reconstruction finance.

These are not ordinary sovereign debts and should not be attributed directly to member states simply because those states are shareholders.

### 3. How do the instructions and money move?

Swift, CLS, Fedwire, Euroclear, Clearstream and DTCC do different jobs.

**Swift** communicates standardized financial messages. A Swift message is not the cash settlement itself.

**CLS** settles eligible FX transactions payment-versus-payment and therefore closes a real settlement-risk relationship across major currencies, including DKK, EUR, USD, NOK, SEK and others.

**Fedwire** settles large-value USD transfers in Federal Reserve money.

**Euroclear and Clearstream** provide securities issuance, custody and settlement infrastructure. The custodian holding a security in the chain is not necessarily its beneficial owner.

**DTCC** provides clearing/netting/settlement infrastructure in major U.S. securities markets.

This layer lets the graph represent the difference between communication, settlement, custody and ownership.

### 4. What rules constrain the network?

FSB, BCBS and CPMI supply three separate rule layers:

- FSB coordinates international financial-stability policy.
- BCBS develops prudential bank standards.
- CPMI develops standards for payments, clearing and settlement.

Inside the EU, EBA, ESMA and EIOPA cover banking, securities and insurance/pensions respectively, while the Single Resolution Board provides the bank-failure/resolution layer for the Banking Union.

These bodies should normally stay hidden on the map until a user traces regulation, supervision or failure resolution. Their importance is semantic, not visual.

### 5. How do we know two records refer to the same institution?

GLEIF and the Legal Entity Identifier system close the entity-identity gap.

The graph should gradually use LEIs for banks, funds, issuers and other legal entities where available. That gives a stable identifier independent of display name and provides public reference and ownership relationships. This is essential before the graph grows into thousands of institutions.

### 6. Where is the non-bank money?

Banks are only part of the creditor side. Pension funds, insurers, sovereign funds and asset managers hold enormous quantities of bonds and equities.

Two first North exemplars are:

- **GPFG/Norges Bank Investment Management**, because its holdings are unusually transparent and globally important.
- **ATP**, because it provides a direct Danish bridge between pension liabilities, bond/swap hedging and long-term investment.

The graph will also retain holder-sector classes so it can represent pension funds or insurers even when individual institutions are not disclosed.

## What is intentionally not added yet

Deposit-insurance systems, individual derivatives CCPs, every national debt-management office and rating agencies are useful, but they become informative only when the underlying bank/debt/derivative records exist.

Adding them now would create decorative nodes rather than explanatory ones.

The rule remains: **build the relationship first, then expose the institution required to explain it.**
