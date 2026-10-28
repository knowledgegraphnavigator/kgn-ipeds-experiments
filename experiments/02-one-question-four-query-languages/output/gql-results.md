# GQL results (GraphLite)

Graph: 1062 nodes, 1958 edges (all institutions and CIP families, health-professions offerings only).

- **baseline:** GQL returned 6 schools, identical to SQL, SPARQL and Cypher.
- **bachelors:** GQL returned 5 schools, identical to SQL, SPARQL and Cypher.
- **any-online:** GQL returned 10 schools, identical to SQL, SPARQL and Cypher.

- **Write the CIP code as a number: 51 instead of '51':** GQL returned 0.
- **Write the threshold as a proportion: > 0.6 instead of > 60:** GQL returned 13.
- **Ask the opposite: which schools do NOT clear 60%:** GQL returned error.
