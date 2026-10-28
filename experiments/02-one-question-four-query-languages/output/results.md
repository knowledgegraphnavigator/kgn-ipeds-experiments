# Results: one question, four query languages

Question: *Which schools offer a fully online master's in the health professions and graduate more than 60% of their students within six years?*

## baseline: Fully online programs; all-student six-year rate

SQL, SPARQL and Cypher return the same 6 schools.

| Institution | Six-year rate (%) | Online health master's fields |
|---|---|---|
| University of Southern California | 91.8 | 3 |
| New York University | 87.6 | 1 |
| University of Washington-Seattle Campus | 85.2 | 3 |
| Baylor University | 80.0 | 1 |
| University of Central Florida | 78.0 | 3 |
| Keiser University-Ft Lauderdale | 61.0 | 3 |

## bachelors: Fully online programs; bachelor's-seeking six-year rate

SQL, SPARQL and Cypher return the same 5 schools.

| Institution | Six-year rate (%) | Online health master's fields |
|---|---|---|
| University of Southern California | 91.8 | 3 |
| New York University | 87.8 | 1 |
| University of Washington-Seattle Campus | 85.2 | 3 |
| Baylor University | 80.0 | 1 |
| University of Central Florida | 78.0 | 3 |

## any-online: Fully or partly online programs; all-student six-year rate

SQL, SPARQL and Cypher return the same 10 schools.

| Institution | Six-year rate (%) | Online health master's fields |
|---|---|---|
| University of Southern California | 91.8 | 6 |
| Ohio State University-Main Campus | 87.7 | 6 |
| New York University | 87.6 | 3 |
| University of Washington-Seattle Campus | 85.2 | 3 |
| Baylor University | 80.0 | 2 |
| University of Central Florida | 78.0 | 3 |
| San Jose State University | 69.2 | 2 |
| DePaul University | 67.8 | 2 |
| St. John's University-New York | 66.1 | 3 |
| Keiser University-Ft Lauderdale | 61.0 | 4 |

- **bachelors vs baseline:** drops Keiser University-Ft Lauderdale; adds none.
- **any-online vs baseline:** drops none; adds San Jose State University, DePaul University, St. John's University-New York, Ohio State University-Main Campus.

## Small edits, big discrepancies

Each row is one typo-sized change to how the strict question is written. Baseline: 6 schools.

| Edit | SQL | SPARQL | Cypher |
|---|---|---|---|
| Write the CIP code as a number: 51 instead of '51' | 6 | 0 | 6 |
| Write the threshold as a proportion: > 0.6 instead of > 60 | 13 | 13 | 13 |
| Put the rate condition inside an outer join or OPTIONAL block | 14 | 14 | n/a |
| Ask the opposite: which schools do NOT clear 60%? | 7 | 8 | 7 |

- **Write the CIP code as a number: 51 instead of '51'.** The code is stored as text. DuckDB and Kuzu quietly convert 51 to '51' and still return the right schools. SPARQL compares RDF terms, so the integer 51 never matches the string "51": it returns nothing, with no error.
- **Write the threshold as a proportion: > 0.6 instead of > 60.** IPEDS rates are stored as percents (0-100). Every school with a rate clears 0.6.
- **Put the rate condition inside an outer join or OPTIONAL block.** A condition inside an outer join or OPTIONAL only decides whether the optional part attaches. Schools below 60% stay in the answer with a blank rate.
- **Ask the opposite: which schools do NOT clear 60%.** Each query uses its language's usual negation. SQL and Cypher evaluate NOT (NULL > 60) as unknown and drop the school with no rate. SPARQL's NOT EXISTS asks whether a matching rate exists, finds none, and keeps it.
