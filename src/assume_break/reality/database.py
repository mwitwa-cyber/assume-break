"""Expanded Zambian ground-truth reality database (2025-2026)."""

from __future__ import annotations

from assume_break.state import RealityFact

ZAMBIAN_REALITY_DATABASE: list[RealityFact] = [
    # ─── TAX ───────────────────────────────────────────────────────────
    RealityFact(
        category="TAX",
        fact="Turnover Tax (TOT) applies to businesses with annual turnover ≤ ZMW 5,000,000 at a flat rate of 5% on gross revenue. No deductions for expenses are allowed under TOT.",
        source="Zambia Revenue Authority – 2025 Tax Guide",
        effective_date="2025-01-01",
        keywords=["turnover", "tax", "tot", "revenue", "small business", "5%", "zmw"],
    ),
    RealityFact(
        category="TAX",
        fact="Corporate Income Tax (CIT) standard rate is 30%. Manufacturing and farming enjoy a reduced rate of 10-15%. Companies must register for CIT if turnover exceeds ZMW 5,000,000.",
        source="Income Tax Act Cap 323 – 2025 Amendments",
        effective_date="2025-01-01",
        keywords=["corporate", "income", "tax", "cit", "30%", "manufacturing", "farming"],
    ),
    RealityFact(
        category="TAX",
        fact="Rental Income Tax is 16% of gross rental income for individuals. No deductions for mortgage interest or maintenance are permitted.",
        source="ZRA Practice Note – Property Income 2025",
        effective_date="2025-01-01",
        keywords=["rental", "income", "tax", "property", "16%", "landlord"],
    ),
    RealityFact(
        category="TAX",
        fact="Property Transfer Tax (PTT) is 8% of the open market value on transfer of land, shares, or mining rights.",
        source="Property Transfer Tax Act – 2025",
        effective_date="2025-01-01",
        keywords=["property", "transfer", "tax", "ptt", "8%", "land", "shares", "mining rights"],
    ),
    RealityFact(
        category="TAX",
        fact="Withholding Tax on dividends paid to non-residents is 20%. For residents, it is 15%. Double Taxation Agreements may reduce rates for treaty countries.",
        source="Income Tax Act – WHT Schedule 2025",
        effective_date="2025-01-01",
        keywords=["withholding", "tax", "dividend", "non-resident", "20%", "15%"],
    ),
    RealityFact(
        category="TAX",
        fact="VAT standard rate is 16% on taxable supplies. Essential foodstuffs (mealie meal, fresh vegetables, milk) are zero-rated. VAT registration threshold is ZMW 800,000 annual turnover.",
        source="Value Added Tax Act – 2025",
        effective_date="2025-01-01",
        keywords=["vat", "16%", "value added", "tax", "zero-rated", "registration", "threshold"],
    ),

    # ─── ENERGY ────────────────────────────────────────────────────────
    RealityFact(
        category="ENERGY",
        fact="Fuel pump prices as of Q1 2025: Petrol K29.92/litre, Diesel K25.11/litre. Prices are set by the Energy Regulation Board (ERB) and adjusted monthly based on international crude oil prices and ZMW/USD exchange rate.",
        source="Energy Regulation Board – Q1 2025 Price Schedule",
        effective_date="2025-01-15",
        keywords=["fuel", "petrol", "diesel", "price", "erb", "energy", "pump"],
    ),
    RealityFact(
        category="ENERGY",
        fact="Fuel price volatility: 5-8% monthly fluctuations are normal. Any business plan assuming fixed fuel costs will face significant variance. Hedging instruments are not widely available in Zambia.",
        source="ERB Historical Price Analysis 2023-2025",
        effective_date="2025-01-01",
        keywords=["fuel", "volatility", "price", "fluctuation", "hedging", "diesel", "petrol"],
    ),
    RealityFact(
        category="ENERGY",
        fact="Load-shedding risk: ZESCO implements scheduled power cuts during low-water years. Kariba Dam levels critically low in 2024-2025. Businesses must budget for generator/solar backup at ~ZMW 15-25/kWh vs grid rate of ~ZMW 1.50/kWh.",
        source="ZESCO Load Management Schedule 2025",
        effective_date="2025-01-01",
        keywords=["electricity", "load-shedding", "power", "zesco", "generator", "solar", "kariba"],
    ),
    RealityFact(
        category="ENERGY",
        fact="Probability of a >15% fuel price shock within any 6-month window is approximately 10%, driven by global crude movements and kwacha depreciation events.",
        source="BoZ Commodity Risk Assessment 2025",
        effective_date="2025-01-01",
        keywords=["fuel", "shock", "price", "risk", "crude", "kwacha", "depreciation"],
    ),

    # ─── FINANCE ───────────────────────────────────────────────────────
    RealityFact(
        category="FINANCE",
        fact="Bank of Zambia policy rate: 14.5% as of Q1 2025. The Monetary Policy Committee meets quarterly and has signaled a cautious tightening bias.",
        source="Bank of Zambia – Monetary Policy Statement Q1 2025",
        effective_date="2025-01-01",
        keywords=["interest", "rate", "boz", "policy", "monetary", "bank of zambia"],
    ),
    RealityFact(
        category="FINANCE",
        fact="Commercial bank lending rates range from 24-32% for SME loans. Collateral requirements typically 150-200% of loan value. Average loan processing time: 4-8 weeks.",
        source="Bankers Association of Zambia – Lending Survey 2025",
        effective_date="2025-01-01",
        keywords=["lending", "rate", "loan", "bank", "sme", "collateral", "interest", "financing"],
    ),
    RealityFact(
        category="FINANCE",
        fact="Headline inflation rate: ~11% year-on-year (Q1 2025). Food inflation higher at ~14%. Core inflation (excluding food and energy) at ~8.5%.",
        source="Zambia Statistics Agency – CPI Report January 2025",
        effective_date="2025-01-01",
        keywords=["inflation", "cpi", "food", "prices", "cost", "zamstat"],
    ),
    RealityFact(
        category="FINANCE",
        fact="ZMW/USD exchange rate: approximately ZMW 27-29 per USD (Q1 2025). The kwacha has depreciated ~15% over the past 12 months. Forward cover is expensive at 8-12% premium.",
        source="Bank of Zambia – Exchange Rate Bulletin 2025",
        effective_date="2025-01-01",
        keywords=["exchange", "rate", "kwacha", "usd", "dollar", "forex", "currency", "depreciation"],
    ),

    # ─── LOGISTICS ─────────────────────────────────────────────────────
    RealityFact(
        category="LOGISTICS",
        fact="La Niña weather pattern confirmed for Q1-Q2 2025. Expect above-average rainfall causing flooding in Western, Southern, and Luapula provinces. Historical flood events disrupt roads for 2-6 weeks.",
        source="Zambia Meteorological Department – Seasonal Forecast 2025",
        effective_date="2025-01-01",
        keywords=["flood", "rain", "la nina", "weather", "western", "southern", "logistics", "road"],
    ),
    RealityFact(
        category="LOGISTICS",
        fact="Rural feeder roads in Western and Northern provinces are unpaved. During rainy season (Nov-Apr), 40-60% of rural roads become impassable. Cold chain logistics impossible without 4x4 vehicles.",
        source="Road Development Agency – Network Status Report 2025",
        effective_date="2025-01-01",
        keywords=["road", "rural", "feeder", "unpaved", "rainy", "season", "4x4", "western", "northern"],
    ),
    RealityFact(
        category="LOGISTICS",
        fact="Lusaka-Ndola dual carriageway (T3): 58% complete as of January 2025. Completion expected Q4 2026. Significant delays and diversions on this corridor affecting transit times by 2-4 hours.",
        source="Road Development Agency – Major Projects Update 2025",
        effective_date="2025-01-01",
        keywords=["lusaka", "ndola", "t3", "dual carriageway", "road", "construction", "copperbelt"],
    ),
    RealityFact(
        category="LOGISTICS",
        fact="Cold chain infrastructure: Only 3 certified cold storage facilities between Lusaka and Copperbelt. No cold storage in Western, North-Western, or Muchinga provinces. Post-harvest losses for fresh produce average 30-40%.",
        source="Zambia Development Agency – Agri-Logistics Assessment 2025",
        effective_date="2025-01-01",
        keywords=["cold", "chain", "storage", "fresh", "produce", "perishable", "post-harvest", "loss"],
    ),

    # ─── MINING ────────────────────────────────────────────────────────
    RealityFact(
        category="MINING",
        fact="Mineral royalty rates (2025): Copper/Cobalt open pit 10%, underground 5.5%. Gold 6%. Gemstones 6%. Royalties are calculated on gross value (norm value) with no deductions for costs.",
        source="Mines and Minerals Development Act – 2025 SI",
        effective_date="2025-01-01",
        keywords=["mining", "royalty", "copper", "cobalt", "gold", "mineral", "tax"],
    ),
    RealityFact(
        category="MINING",
        fact="Export duty on raw copper concentrate: 15% of gross value. This incentivizes local smelting and refining. Export of unprocessed minerals requires MMMD approval.",
        source="Customs and Excise (Mining) Regulations 2025",
        effective_date="2025-01-01",
        keywords=["export", "duty", "copper", "concentrate", "smelting", "mining", "processing"],
    ),
    RealityFact(
        category="MINING",
        fact="Mining license timeline: Large-scale mining license application takes 6-12 months. Requires Environmental Impact Assessment (EIA) from ZEMA, community consultation, and resettlement action plan if applicable.",
        source="MMMD – Mining Licensing Guidelines 2025",
        effective_date="2025-01-01",
        keywords=["mining", "license", "eia", "zema", "permit", "application", "timeline"],
    ),
    RealityFact(
        category="MINING",
        fact="Mining CIT rate: 30% standard. However, mining companies face additional 'variable profit tax' of 15% on taxable income exceeding 8% of gross sales. Effective tax burden can reach 45%+.",
        source="Income Tax Act – Mining Provisions 2025",
        effective_date="2025-01-01",
        keywords=["mining", "tax", "corporate", "profit", "variable", "cit"],
    ),

    # ─── AGRICULTURE ───────────────────────────────────────────────────
    RealityFact(
        category="AGRICULTURE",
        fact="Food Reserve Agency (FRA) maize floor price: ZMW 280 per 50kg bag (2025 marketing season). FRA purchases are limited to designated areas and subject to budget availability.",
        source="FRA – 2025 Crop Marketing Gazette Notice",
        effective_date="2025-04-01",
        keywords=["maize", "fra", "food reserve", "price", "agriculture", "crop", "floor"],
    ),
    RealityFact(
        category="AGRICULTURE",
        fact="Farmer Input Support Programme (FISP): Government subsidizes seed and fertilizer for smallholders farming 0.5-5 hectares. Beneficiary must contribute ZMW 400. Program covers ~1 million farmers.",
        source="Ministry of Agriculture – FISP Guidelines 2025",
        effective_date="2025-01-01",
        keywords=["fisp", "subsidy", "fertilizer", "seed", "agriculture", "smallholder", "input"],
    ),
    RealityFact(
        category="AGRICULTURE",
        fact="Maize export ban risk: Government has historically imposed export bans during deficit years (2024 drought-impacted season). Any agri-business relying on export markets must factor 20-30% probability of periodic export restrictions.",
        source="Ministry of Agriculture – Strategic Grain Reserve Policy",
        effective_date="2025-01-01",
        keywords=["maize", "export", "ban", "restriction", "agriculture", "grain", "drought"],
    ),
    RealityFact(
        category="AGRICULTURE",
        fact="Agricultural land lease rates: Government land in farming blocks ranges ZMW 50-200/hectare/year. Private farmland in commercial areas (Mkushi, Chisamba) can reach ZMW 2,000-5,000/hectare/year.",
        source="Ministry of Lands – Agricultural Land Allocation 2025",
        effective_date="2025-01-01",
        keywords=["land", "lease", "agriculture", "farm", "hectare", "mkushi", "chisamba"],
    ),

    # ─── LABOR ─────────────────────────────────────────────────────────
    RealityFact(
        category="LABOR",
        fact="Minimum wage (2025): ZMW 2,500/month for general workers, ZMW 3,000/month for shop workers in Lusaka/Copperbelt, ZMW 2,100/month for domestic workers. Applies to all formal sector employers.",
        source="Ministry of Labour – Minimum Wages and Conditions of Employment Order 2025",
        effective_date="2025-01-01",
        keywords=["minimum", "wage", "salary", "labour", "labor", "worker", "pay"],
    ),
    RealityFact(
        category="LABOR",
        fact="NAPSA employer contribution: 5% of gross salary (mandatory). Employee contribution: 5%. Total 10%. Applies to all employees earning above ZMW 1,000/month. Non-compliance attracts 5% penalty per month.",
        source="NAPSA Act – Contribution Schedule 2025",
        effective_date="2025-01-01",
        keywords=["napsa", "pension", "contribution", "employer", "social security", "payroll"],
    ),
    RealityFact(
        category="LABOR",
        fact="Skills Development Levy: 0.5% of total payroll, payable monthly to TEVETA. Applies to employers with 5+ employees. Funds are used for vocational training programs.",
        source="TEVETA Act – Skills Development Levy Regulations",
        effective_date="2025-01-01",
        keywords=["skills", "levy", "teveta", "payroll", "training", "development"],
    ),
    RealityFact(
        category="LABOR",
        fact="Workers' Compensation Fund: Employer-funded, sector-dependent rates (0.5-5% of payroll). Mining and construction attract highest rates. Claims processing takes 3-6 months.",
        source="Workers' Compensation Act – 2025 Gazette",
        effective_date="2025-01-01",
        keywords=["workers", "compensation", "insurance", "injury", "safety", "payroll"],
    ),

    # ─── IMPORT/EXPORT ─────────────────────────────────────────────────
    RealityFact(
        category="IMPORT_EXPORT",
        fact="COMESA preferential tariffs: Zero or reduced duty on goods originating from COMESA member states with valid Certificate of Origin. Rules of origin require 35% local value addition.",
        source="COMESA Trade Protocol – Zambia Implementation 2025",
        effective_date="2025-01-01",
        keywords=["comesa", "tariff", "import", "export", "preferential", "trade", "duty"],
    ),
    RealityFact(
        category="IMPORT_EXPORT",
        fact="Standard customs duty rates: 0% (raw materials/capital goods), 5% (semi-processed goods), 15% (intermediate goods), 25% (finished consumer goods). Applies to non-preferential imports.",
        source="Customs and Excise Act – Tariff Schedule 2025",
        effective_date="2025-01-01",
        keywords=["customs", "duty", "import", "tariff", "rate", "goods"],
    ),
    RealityFact(
        category="IMPORT_EXPORT",
        fact="VAT on imports: 16% of CIF value plus customs duty. Payable at point of entry. VAT-registered importers can claim input credit. Non-registered importers bear full cost.",
        source="VAT Act – Import Provisions 2025",
        effective_date="2025-01-01",
        keywords=["vat", "import", "customs", "cif", "tax"],
    ),
    RealityFact(
        category="IMPORT_EXPORT",
        fact="Import Declaration Fee (IDF): 5% of CIF value on all imports. This is a non-refundable fee separate from customs duty. Significantly increases landed cost of imported goods.",
        source="Customs and Excise – IDF Regulations 2025",
        effective_date="2025-01-01",
        keywords=["idf", "import", "declaration", "fee", "cif", "customs", "cost"],
    ),

    # ─── DIGITAL/TELECOM ───────────────────────────────────────────────
    RealityFact(
        category="DIGITAL",
        fact="ZICTA licensing: All electronic communication services require ZICTA license. Application fee ZMW 50,000+. Annual license renewal. VAS providers need separate content service license.",
        source="ZICTA – Licensing Framework 2025",
        effective_date="2025-01-01",
        keywords=["zicta", "license", "telecom", "digital", "communication", "vas"],
    ),
    RealityFact(
        category="DIGITAL",
        fact="Data Protection Act 2021: Requires registration with Data Protection Commissioner for any entity processing personal data. Cross-border data transfer requires adequacy assessment. Penalties up to ZMW 1,000,000.",
        source="Data Protection Act No. 3 of 2021",
        effective_date="2025-01-01",
        keywords=["data", "protection", "privacy", "gdpr", "personal", "digital", "compliance"],
    ),
    RealityFact(
        category="DIGITAL",
        fact="Mobile money regulatory caps: Individual daily transaction limit ZMW 30,000. Monthly limit ZMW 150,000. Agent float requirements and KYC tiering apply. Mobile money operators must partner with licensed banks.",
        source="Bank of Zambia – National Payment Systems Directives 2025",
        effective_date="2025-01-01",
        keywords=["mobile", "money", "payment", "digital", "fintech", "transaction", "limit"],
    ),
    RealityFact(
        category="DIGITAL",
        fact="Internet penetration: ~35% of population (2025). Mobile broadband coverage ~70% in urban areas, <20% in rural areas. Average mobile data cost: ~ZMW 5/GB. Fixed broadband limited to major cities.",
        source="ZICTA – ICT Indicators Report Q4 2024",
        effective_date="2025-01-01",
        keywords=["internet", "broadband", "mobile", "data", "connectivity", "rural", "urban"],
    ),

    # ─── BUSINESS REGISTRATION ─────────────────────────────────────────
    RealityFact(
        category="REGISTRATION",
        fact="PACRA company registration: Private company ZMW 250 (online), takes 1-3 business days. Requires minimum 1 director, 1 shareholder. Annual return filing fee ZMW 150, due within 90 days of financial year end.",
        source="PACRA – Companies Act Registration Guide 2025",
        effective_date="2025-01-01",
        keywords=["pacra", "registration", "company", "business", "incorporate", "annual return"],
    ),
    RealityFact(
        category="REGISTRATION",
        fact="ZEMA Environmental Impact Assessment: Required for mining, manufacturing, large-scale agriculture, and construction projects. Full EIA costs ZMW 50,000-500,000 and takes 3-6 months. Environmental Project Brief (EPB) for smaller projects: ZMW 10,000-50,000.",
        source="ZEMA – EIA Regulations 2025",
        effective_date="2025-01-01",
        keywords=["zema", "eia", "environment", "impact", "assessment", "license", "permit"],
    ),
    RealityFact(
        category="REGISTRATION",
        fact="Health-related businesses (food processing, restaurants, pharmacies) require Health Registration Authority (HRA) certification. Inspection and certification takes 4-8 weeks. Annual renewal required.",
        source="HRA – Business Certification Guidelines 2025",
        effective_date="2025-01-01",
        keywords=["health", "hra", "food", "safety", "certification", "restaurant", "pharmacy"],
    ),
    RealityFact(
        category="REGISTRATION",
        fact="Tourism and hospitality businesses require ZNTB (Zambia National Tourism Board) license. Annual license fee ZMW 5,000-25,000 depending on establishment size. Grading inspection mandatory.",
        source="Tourism and Hospitality Act – Licensing Regulations 2025",
        effective_date="2025-01-01",
        keywords=["tourism", "hotel", "hospitality", "zntb", "license", "lodge", "travel"],
    ),
]
