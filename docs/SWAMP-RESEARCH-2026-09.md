# Swamp Research — September 2026

## Research status

This is the first evidence-backed population pass for the expanded Swamp layer. It is intentionally a **seed dataset**, not a claim of completeness. The purpose is to identify how much real data can be attached to the graph and which public datasets can scale the project by orders of magnitude.

## 1. Data sources with unusually high expansion potential

### Federal Election Commission

The FEC provides searchable committee data, transaction-level bulk data, PAC/party reports, independent expenditures and committee registration data. The FEC distinguishes Super PACs, PACs, leadership PACs, hybrid PACs, separate segregated funds and other committee types. Its bulk datasets are suitable for building a large political-money layer.

Source: https://www.fec.gov/data/browse-data/

### IRS tax-exempt organization data

The IRS Tax Exempt Organization Search exposes Form 990-series returns, 990-N notices, Pub. 78, revocations and determination letters. The IRS also provides bulk downloads. This is the backbone for a scalable nonprofit/NGO/foundation layer.

Source: https://www.irs.gov/charities-non-profits/search-for-tax-exempt-organizations

### OpenCorporates

OpenCorporates states that its database covers more than **200 million companies** and that its relationship supplement contains **30 million+ relationship records**, sourced from public registries including SEC records and UK Companies House. This is potentially one of the largest ownership/control expansion sources for the graph.

Sources:
- https://api.opencorporates.com/
- https://knowledge.opencorporates.com/knowledge-base/count-of-relationship-records/

### Euromedia Ownership Monitor

The 2025 EurOMo database covers **more than 3,000 news media outlets and owners** across EU countries and supports ownership-network visualization and machine-readable data. Country reports cover all EU member states. This is an immediate path to populate the European media layer country by country.

Sources:
- https://media-ownership.eu/
- https://media-ownership.eu/2025-edition/country-reports/

### SIPRI arms-industry database

SIPRI maintains a Top 100 database of arms-producing and military-services companies. The 2024 Top 100 had combined arms revenues of **$679 billion**, up 5.9% in one year. US companies in the ranking generated about **$334 billion** in arms revenues in 2024; 39 US companies appeared in the ranking.

Sources:
- https://www.sipri.org/databases/armsindustry
- https://www.sipri.org/publications/2025/sipri-fact-sheets/sipri-top-100-arms-producing-and-military-services-companies-2024

### US Intelligence Community

ODNI describes the US Intelligence Community as **18 elements**. The repository should create individual nodes for each rather than one generic "US intelligence" node.

Source: https://www.odni.gov/

### EU terrorism sanctions

The EU's 2026 framework currently lists **13 individuals and 23 groups/entities** on the EU terrorist list. Separately, the EU maintains autonomous restrictive measures for ISIL/Daesh and Al-Qaeda and separate measures concerning Hamas and Palestinian Islamic Jihad. On 19 February 2026, the EU added Iran's Islamic Revolutionary Guard Corps to the terrorist list.

Sources:
- https://www.consilium.europa.eu/en/policies/sanctions-against-terrorism/
- https://www.consilium.europa.eu/en/press/press-releases/2026/02/19/eu-terrorist-list-council-designates-the-islamic-revolutionary-guard-corps-as-a-terrorist-organisation/
- https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32026D1882

## 2. Political-finance entities already identified

### AIPAC PAC

FEC ID: **C00797670**.

Coverage: 1 January 2025–31 July 2026.

- Total receipts: **$50,061,505.47**
- Contributions: **$47,779,957.99**
- Itemized individual contributions: **$47,051,063.83**
- Total disbursements: **$48,460,201.45**
- Contributions to other committees: **$45,895,280.00**
- Ending cash: **$2,628,910.80**

The FEC identifies it as a monthly membership-organization PAC. AIPAC itself describes the PAC as supporting pro-Israel Democratic and Republican congressional candidates.

Sources:
- https://www.fec.gov/data/committee/C00797670/
- https://aipac.org/politics

### United Democracy Project

FEC ID: **C00799031**.

Coverage: 1 January 2025–31 July 2026.

- Total receipts: **$107,542,702.64**
- Contributions: **$104,211,071.04**
- Total disbursements: **$77,208,509.82**
- Independent expenditures: **$50,927,163.82**
- Operating expenditures: **$16,338,146.00**
- Contributions to other committees: **$9,931,200.00**
- Ending cash: **$59,137,087.92**

The FEC classifies UDP as a Super PAC. AIPAC publicly describes UDP as its aligned/backed Super PAC.

Sources:
- https://www.fec.gov/data/committee/C00799031/
- https://www.aipac.org/memos/2022-political-success

### Citizens Against AIPAC Corruption

FEC ID: **C00879080**.

Coverage: 1 January 2025–31 July 2026.

- Total receipts: **$1,539,546.32**
- Contributions: **$838,007.73**
- Other receipts: **$701,531.89**
- Total disbursements: **$1,396,126.19**
- Independent expenditures: **$137,228.39**
- Ending cash: **$166,949.59**

FEC classification: monthly hybrid PAC with non-contribution account.

Source: https://www.fec.gov/data/committee/C00879080/

### Additional PAC seeds

The same FEC architecture can immediately expand to thousands of committees. Initial discovered examples include:

- American Petroleum Institute PAC — C00483677 — $285,886.59 receipts and $256,092.94 disbursements for 2025–July 2026.
- American Institute of CPAs PAC — C00077321 — $1,906,736.96 receipts and $4,533,606.46 disbursements for 2025–July 2026.
- American Airlines PAC — C00107300 — $756,358.78 receipts and $731,178.98 disbursements for 2025–July 2026.
- Independent Pilots Association PAC — C00849323 — $829,301.62 receipts and $580,440.71 disbursements for 2025–July 2026.
- ACA International PAC — C00034785 — $455,955.86 receipts and $344,449.32 disbursements for 2025–June 2026.
- Appraisal Institute PAC — C00144261 — $114,348.78 receipts and $103,482.21 disbursements for 2025–July 2026.

Sources: FEC committee pages for each ID.

## 3. Israel365 / Teach for Israel

Israel365 is an important example of why the graph must separate **brand, nonprofit legal entity, media properties and activities**.

Israel365's public site states that Rabbi Tuly Weisz founded Israel365 on 1 January 2012 and describes its mission around connecting Jews and Christians with Israel through Torah education, advocacy and support.

Israel365 Charity identifies itself as operated by **Teach for Israel**, a 501(c)(3) organization.

ProPublica's Nonprofit Explorer identifies:

- Legal name: Teach For Israel Inc
- EIN: **45-4041360**
- Tax-exempt since September 2012
- FY2024 revenue: **$2,624,801**
- FY2024 expenses: **$2,696,925**
- FY2024 net income: **-$72,124**
- FY2024 total assets: **$386,433**
- FY2024 total liabilities: **$515,403**
- FY2024 contributions: **$2,624,801**

The organization's own charity site states that donations are processed by Teach for Israel/Israel365 Charity Fund.

Sources:
- https://israel365.com/
- https://israel365charity.com/financials/
- https://projects.propublica.org/nonprofits/organizations/454041360

## 4. Think-tank financial seeds

### Cato Institute

Cato's FY2026 published financial results report:

- Operating revenue: **$74.259 million**
- Operating expenses: **$51.194 million**
- Assets: **$213.709 million**
- Individual revenue: $48.076m
- Foundation revenue: $5.617m
- Corporate revenue: $1.930m
- Other income: $18.148m

Cato states that it accepts no government funding.

Source: https://www.cato.org/annualreport25/financial-results

### Council on Foreign Relations

CFR's audited FY2024 financial statements show operating revenue/support categories including:

- Membership dues: **$9.9045m**
- Annual giving: **$10.335m**
- Corporate memberships and related income: **$6.7255m**
- Grants and contributions: **$24.8164m**
- Foreign Affairs publications: **$12.2205m**
- Investment return used for current operations: **$27.4751m**
- Rental income: **$1.3068m**
- Miscellaneous: **$1.1828m**

The graph should preserve the revenue categories rather than collapsing them into a single "CFR budget" number.

Source: CFR audited financial statements, FY ended 30 June 2024.

### Heritage Foundation

Heritage publicly publishes annual reports and audited financial statements and makes its IRS Form 990 available. The repository should pull exact revenue, expense, asset, donor and compensation data from those documents rather than using estimates.

Source: https://www.heritage.org/financial

### Brookings Institution

Brookings publishes annual reports and financial statements and describes support from individuals, corporations, governments and foundations. Exact financial fields should be extracted from the annual report/financial statements rather than inferred from third-party estimates.

Source: https://www.brookings.edu/about-us/annual-report/

## 5. Media layer

EurOMo provides an immediately usable European media ownership expansion:

- more than **3,000 news media outlets and owners**;
- all EU countries covered in the 2025 country-report architecture;
- direct and indirect ownership;
- cross-market operations;
- editorial responsibility;
- funding and revenues;
- platform relationships;
- national regulatory frameworks;
- ownership-network visualization.

This should become a major input into the North Programme country graph.

Sources:
- https://media-ownership.eu/
- https://media-ownership.eu/2025-edition/country-reports/

## 6. Arms and security contractor layer

SIPRI's 2024 Top 100 provides a ready-made list of 100 companies. The leading companies by 2024 arms revenue include:

1. Lockheed Martin — $64.65bn
2. RTX — $43.60bn
3. Northrop Grumman — $37.85bn
4. BAE Systems — $33.79bn
5. General Dynamics — $33.63bn
6. Boeing — $30.55bn
7. Rostec — $27.12bn
8. Aviation Industry Corporation of China — $20.32bn
9. China Electronics Technology Group Corporation — $18.92bn
10. L3Harris Technologies — $16.21bn
11. NORINCO — $13.97bn
12. Leonardo — $13.83bn
13. Airbus — $13.37bn
14. China State Shipbuilding Corporation — $12.33bn
15. Thales — $11.88bn
16. Huntington Ingalls Industries — $10.28bn
17. China Aerospace Science and Technology Corporation — $10.23bn
18. Leidos — $9.37bn
19. Amentum — $8.33bn
20. Rheinmetall — $8.24bn

These are **arms revenues**, not total corporate revenue and not profit.

Source: SIPRI Top 100, 2024.

## 7. Intelligence layer

ODNI's 18 US Intelligence Community elements should be individual graph nodes:

1. Office of the Director of National Intelligence
2. Department of State — Bureau of Intelligence and Research
3. Central Intelligence Agency
4. Department of the Treasury — Office of Intelligence and Analysis
5. Defense Intelligence Agency
6. Federal Bureau of Investigation — Intelligence Branch
7. U.S. Army Intelligence and Security Enterprise
8. National Geospatial-Intelligence Agency
9. U.S. Air Force Intelligence
10. National Reconnaissance Office
11. National Security Agency
12. U.S. Coast Guard Intelligence
13. Drug Enforcement Administration — Office of National Security Intelligence
14. Department of Energy — Office of Intelligence and Counterintelligence
15. Department of Homeland Security — Office of Intelligence and Analysis
16. U.S. Marine Corps — Marine Corps Intelligence Activity
17. U.S. Navy — Naval Intelligence Activity
18. U.S. Space Force Intelligence

The existing repository methodology already specifies that these should be decomposed further into legal authority, records systems, collection programs, contractors, oversight and dissemination rather than represented as monolithic agencies.

Source: ODNI Intelligence Community annual reporting.

## 8. Terrorism / armed-group layer

The graph should maintain separate designation regimes instead of one universal "terrorist" category.

As of 2026, the EU's Common Position framework has 13 individuals and 23 groups/entities. The EU separately maintains measures concerning ISIL/Daesh and Al-Qaeda and separate measures addressing Hamas and Palestinian Islamic Jihad support. The July 2026 Council review kept the 2026 list in force.

The repository should therefore store:

- designation_authority;
- legal_basis;
- designation_date;
- review_date;
- group_name;
- alternate_names;
- geography;
- status;
- source;

rather than treating the label as an intrinsic property of the organization.

Sources: Council of the EU and EUR-Lex 2026 decisions.

## 9. Ownership expansion

OpenCorporates offers the strongest scalable path for corporate ownership/control:

- 200m+ companies;
- 30m+ relationship records;
- subsidiaries;
- branches;
- control statements;
- share parcels where available;
- jurisdiction-specific registries.

This is particularly important for the "who owns what?" question. The graph should not attempt to ingest everything blindly. It should prioritize entities already connected to countries, infrastructure, media, finance, political activity, defense, technology and NGOs.

## 10. Initial expansion priorities

The first automated/manual population rounds should therefore be:

### Round A — political money

FEC committees → donors → recipients → independent expenditures → candidates → states → industries.

### Round B — nonprofits

IRS 990 organizations → revenue → expenses → assets → grants → officers → related organizations → countries.

### Round C — media

EurOMo 3,000+ EU outlets/owners → parent → beneficial owner → country → platform → revenue/funding.

### Round D — companies

OpenCorporates relationships → parent/subsidiary/control → jurisdiction → country → existing graph nodes.

### Round E — defense/security

SIPRI Top 100 → company → country → arms revenue → government customers → subsidiaries → contracts.

### Round F — intelligence

18 US IC elements + European national agencies + Europol/Eurojust + oversight + public information systems.

### Round G — terrorism/armed groups

EU and national designation lists → group → geography → designation authority → timeline → documented activity.

## 11. The result

The important discovery from this research pass is that the Swamp can be expanded by **orders of magnitude without inventing anything**.

The available public data already gives us:

- 200m+ companies;
- 30m+ corporate relationship records;
- 3,000+ EU media outlets/owners;
- 100 major arms companies in the SIPRI Top 100;
- 18 US intelligence-community elements;
- 23 EU terrorist-list groups/entities plus separate terrorism-sanctions regimes;
- a very large FEC political-committee universe with bulk transaction data;
- a very large IRS nonprofit universe with Form 990 bulk data.

The repository should now treat these as **data reservoirs** and progressively pull the highest-value nodes into the graph.

The aim is not to create a giant list. The aim is to make the relationships searchable: **money → organization → people → country → media → contracts → ideology/policy → activity → consequences**.
