# Results: where does the number go?

8034 rows, one per school x CIP code x award level. 2130 of 4949 school x CIP pairs have more than one award level (5215 rows).

Q1: bachelor's degrees at ASU Campus Immersion in CIP 11.0701. Truth: [701].
Q2: completions by award level, all schools. Truth: 451,677 in total.

| Model | Size | Q1 answer | Q1 | Q2 total | Q2 |
|---|---|---|---|---|---|
| Property graph: count on the edge | 1,110 nodes, 8,034 edges | 701 | ✓ | 451,677 | ✓ |
| RDF: intermediate offering node | 43,455 triples | 701 | ✓ | 451,677 | ✓ |
| RDF 1.1: standard reification | 56,438 triples | 701 | ✓ | 451,677 | ✓ |
| RDF 1.2: << >> annotation syntax | 32,336 triples | 701 | ✓ | 451,677 | ✓ |
| RDF 1.2: named reifier per row | 32,336 triples | 701 | ✓ | 451,677 | ✓ |
| RDF-star 2021: << >> annotation syntax (pyoxigraph 0.3.22) | 23,949 triples | 18, 701, 842 | ✗ | 1,061,729 | ✗ |
| RDF 1.2: reifier named for the pair (slip) | 28,898 triples | 18, 701, 842 | ✗ | 1,061,729 | ✗ |
