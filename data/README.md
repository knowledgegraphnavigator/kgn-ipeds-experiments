# IPEDS 2024 GEO Audit Test Dataset

Ground-truth institutional data for verifying claims on university websites against the ArcherEDU Higher Education Schema (85 entities) and for mapping programs by CIP code.

## Sources

- NCES IPEDS Data Center, complete data files: https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx (2024 collection year).
- Files used: HD2024 (directory), IC2024 (revised `_rv`), COST1_2024 (2024-25 cost of attendance and charges), ADM2024 (fall 2024 admissions), EF2024A (fall 2024 enrollment), EF2024A_DIST (distance-ed enrollment), EF2024D (retention, student-faculty ratio), GR2024 (graduation rates; 4-yr 2018 cohort, 2-yr 2021 cohort), GR200_24 (200% graduation rates), SFA2324 (2023-24 student aid), C2024_A (completions by CIP, revised `_rv`), C2024DEP (programs offered and distance-ed availability, revised `_rv`).
- Where a zip contained a revised `_rv` file, the revised file was used.

## Files

| File | Rows | Grain |
|---|---|---|
| institutions-v1.0.csv | 45 | 1 per institution |
| cost-aid-v1.0.csv | 45 | 1 per institution |
| admissions-enrollment-v1.0.csv | 45 | 1 per institution |
| offerings-v1.0.csv | 45 | 1 per institution |
| outcomes-v1.0.csv | 45 | 1 per institution |
| programs-v1.0.csv | 8034 | UNITID x CIPCODE x AWLEVEL (first majors) |
| data-dictionary-v1.0.csv | 226 | 1 per output column |

Join key across all files: `UNITID`. `opeid` (institutions) is the join key for College Scorecard.

## Sample method

Eligibility (applied to HD2024): CYACTIVE=1; PSET4FLG=1 (Title IV, primarily postsecondary); WEBADDR present; SECTOR 1-6 (degree-granting public, nonprofit, for-profit, 2-yr and 4-yr); fall 2024 total enrollment >0; COST1 charges present (CHG2AY3 or CHG1PY3). Additionally required, except for graduate-only institutions (INSTCAT=1): a GR2024 adjusted cohort >0, and ADM2024 applicant data unless IC OPENADMP=1 (open admission).

Selection rule (deterministic, no randomness): strata are processed in order S01-S26. Within each stratum, eligible institutions not already chosen by an earlier stratum are ranked by fall 2024 total enrollment (EF2024A EFALEVEL=1, descending; ties by UNITID) and the top N taken. Strata marked "distinct regions" take at most one institution per BEA region (OBEREG); the religious stratum takes at most one per RELAFFIL code. Online share = EF2024A_DIST EFDEEXC/EFDETOT (all students). HSI status is not in HD2024, so an HSI proxy is used: Hispanic share of UG headcount >=25% (EF2024A), 50 states + DC only. Scripts are reproducible from the raw files.

## Sample composition

| Stratum | Definition | N | Institutions |
|---|---|---|---|
| S01 | Public 4yr R1 (Carnegie 15) | 4 | Arizona State University Campus Immersion; University of Central Florida; Ohio State University-Main Campus; University of Washington-Seattle Campus |
| S02 | Public 4yr R2 (Carnegie 16) | 2 | Kennesaw State University; California State University-Fullerton |
| S03 | Public regional/master's (Carnegie 18-20, <50% exclusively distance) | 3 | Utah Valley University; California State University-Northridge; CUNY Hunter College |
| S04 | Private nonprofit R1 (Carnegie 15) | 2 | New York University; University of Southern California |
| S05 | Private nonprofit large doctoral/prof or master's (Carnegie 17-18) | 2 | Keiser University-Ft Lauderdale; St. John's University-New York |
| S06 | Private nonprofit liberal arts (Carnegie 21) | 3 | Wesleyan University; Bucknell University; University of Richmond |
| S07 | Private nonprofit small baccalaureate diverse (Carnegie 22, <5,000) | 2 | Trine University; St. Francis College |
| S08 | Religious-affiliated private nonprofit, campus-based (RELAFFIL coded, <50% exclusively distance, distinct affiliations) | 3 | Brigham Young University; DePaul University; Baylor University |
| S09 | Faith-related special focus (Carnegie 24) | 1 | Midwestern Baptist Theological Seminary |
| S10 | For-profit 4yr, online-heavy (>=80% exclusively distance) | 2 | University of Phoenix-Arizona; American Public University System |
| S11 | For-profit 4yr, campus-based (<50% exclusively distance) | 1 | NUC University |
| S12 | For-profit 2yr | 1 | Auguste Escoffier School of Culinary Arts-Boulder |
| S13 | Public 2yr community college | 4 | Ivy Tech Community College; Northern Virginia Community College; Tarrant County College District; Connecticut State Community College |
| S14 | Private nonprofit 2yr | 1 | Ultimate Medical Academy |
| S15 | HBCU - public 4yr | 1 | North Carolina A & T State University |
| S16 | HBCU - private nonprofit | 1 | Howard University |
| S17 | Tribal college (TRIBAL=1) | 1 | Fond du Lac Tribal and Community College |
| S18 | HSI proxy - public 4yr regional (Carnegie 17-20, >=25% Hispanic UG headcount, 50 states) | 1 | San Jose State University |
| S19 | HSI proxy - public 2yr (>=25% Hispanic UG headcount, 50 states) | 1 | East Los Angeles College |
| S20 | Graduate-only (INSTCAT=1) | 2 | Mayo Clinic College of Medicine and Science; Touro University California |
| S21 | Predominantly online nonprofit/public (>=80% exclusively distance) | 2 | Western Governors University; Southern New Hampshire University |
| S22 | Nursing/health special focus 4yr (Carnegie 26) | 1 | Chamberlain University-Illinois |
| S23 | Health special focus 2yr (Carnegie 10) | 1 | Jersey College |
| S24 | Engineering/technology special focus (Carnegie 28) | 1 | Rose-Hulman Institute of Technology |
| S25 | Arts/music/design special focus (Carnegie 30) | 1 | Los Angeles Film School |
| S26 | Rural public 2yr (LOCALE 41-43) | 1 | Cuesta College |

Total: 45 institutions. Sector mix: Private not-for-profit, 4-year or above: 19; Public, 4-year or above: 12; Public, 2-year: 6; Private for-profit, 4-year or above: 5; Private for-profit, 2-year: 2; Private not-for-profit, 2-year: 1. Region mix: Far West: 9; Southeast: 8; Mid East: 7; Great Lakes: 6; Southwest: 4; Rocky Mountains: 4; New England: 3; Plains: 3; Outlying areas: 1.

Note: because the rule is largest-enrollment-first, the sample leans toward large institutions within each stratum (e.g. multi-state online institutions are reported under their IPEDS home state).

## Coding conventions

- IPEDS missing / not-applicable codes (-1, -2, -3) and suppressed or blank values are output as blank.
- Coded fields are given as both `<field>_code` (raw IPEDS code) and a decoded label where the code list is known with confidence: SECTOR, CONTROL, ICLEVEL, HLOFFER, INSTCAT, C21BASIC (Carnegie 2021 basic), HBCU, TRIBAL, LOCALE, INSTSIZE, OBEREG, CALSYS, CNTLAFFI, ADMCON1/ADMCON7, AWLEVEL, CIP 2-digit families (CIP 2020).
- IC yes/no flags (1/0) output as Yes/No. Rates are percents (0-100). Dollars are nominal USD.
- Derived rates (admit rate, yield, online share, graduation rates from GR2024 counts) are computed as numerator/denominator x 100, rounded to 1 decimal.

## Known gaps and undecoded fields

- **No College Scorecard data yet** (planned v1.1): institutional accreditor (accreditingBodyName), earnings/medianSalary, employment outcomes, debt, repayment. Join via `opeid`.
- **Not available in IPEDS at all**: programmatic/specialized accreditation, licensure exam pass rates, per-program tuition (COST1 CIPTUIT fields cover only program reporters' largest programs), tuition per semester (IPEDS reports annual tuition and per-credit charges; `calendar_system` is provided to derive per-term figures), maximum enrollment / class-size caps, employment rate.
- **Net price by income** is not present in the downloaded SFA2324.csv (no NPIS/NPGRN/NPT4 variables); requires the separate net-price file for 2023-24 from the Data Center.
- **Dual enrollment/dual credit flag**: absent from IC2024 (only CREDITS2-4 present). CREDITS2/3/4 labelled per prior-year dictionary (life experience / AP / none) - verify.
- **cip_title** (programs) intentionally blank: 6-digit CIP titles are not in the downloaded files and were not invented. Join the NCES CIP 2020 code list.
- **Raw code kept, decode with _Dict**: RELAFFIL (only 30 Roman Catholic, 54 Baptist, 75 Southern Baptist, 80 Jewish, 94 LDS decoded; e.g. 102 left raw), DISTNCED, COST1 BOARD (meal plan).
- **Labels inferred from file structure / prior-year dictionaries (verify)**: GR2024 GRTYPE codes (validated: Ohio State 150% rate 87.7% vs GR200 88%), IC VET1-VET5, SLO5/51/52/53/6/7/8, CREDITS2-4, EF2024A_DIST EFDEEX1/EFDEEX2, C2024DEP DE vs DES suffixes.
- **Omitted (meaning uncertain)**: COST1 CHG10AY*, IC SLO521/SLOA/SLOB, STUSRV*, DSTNCED1-3, EF2024A_DIST EFDEEX3-5, IC tuition-plan and professional-program fields.
- ADM/test-score fields are blank for open-admission institutions; GR fields blank for graduate-only institutions (Mayo Clinic College of Medicine and Science, Touro University California); 2-yr GR fields blank for 4-yr institutions and vice versa.
- HSI is a proxy (headcount-based), not the official Department of Education HSI eligibility list.

## Dictionary files needed to close decoding gaps

IC2024_Dict.zip, COST1_2024_Dict.zip, GR2024_Dict.zip, C2024DEP_Dict.zip, EF2024A_DIST_Dict.zip, ADM2024_Dict.zip, SFA2324_Dict.zip (confirm net-price location).
