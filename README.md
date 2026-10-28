# Knowledge Graph Experiments with IPEDS Higher-Ed Data

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

A 13-part series that uses one public dataset (45 U.S. institutions, 8,034 program offerings, 1,065 CIP codes from NCES IPEDS 2024) to show how languages, ontologies and graph models change what a knowledge graph can say. Each experiment will get its own folder with code and data, plus a companion post on [KnowledgeGraphNavigator.com](https://knowledgegraphnavigator.com).

## Part 1: Syntax

1. [One University, Six Syntaxes](01-same-facts-six-syntaxes.md) · Languages & Formats · JSON-LD, Microdata, RDFa, Turtle, N-Triples, JSONL · **[built](experiments/01-same-facts-six-syntaxes/)**
2. [One Question, Four Query Languages](02-one-question-four-query-languages.md) · Languages & Formats · SPARQL, Cypher, GQL, SQL · **[built](experiments/02-one-question-four-query-languages/)**
3. [Where Does the Number Go? RDF vs. Property Graphs](03-rdf-vs-property-graph.md) · Languages & Formats · Turtle, RDF-star, Cypher

## Part 2: Meaning

4. [Same Data, Three Worldviews](04-swap-the-ontology.md) · Core Concepts · JSON-LD, Turtle, OWL
5. [Programs as a Taxonomy: CIP in SKOS](05-cip-as-skos.md) · Core Concepts · Turtle, SKOS
6. [Can a Reasoner Rebuild the Sample?](06-can-a-reasoner-rebuild-the-sample.md) · Building Knowledge Graphs · OWL 2, Turtle, SPARQL
7. [Where Did This Fact Come From?](07-provenance-three-ways.md) · Core Concepts · RDF-star, TriG, PROV-O

## Part 3: Search

8. [The Claim Verification Graph](08-claim-verification-graph.md) · Knowledge Graphs for SEO · JSON-LD, SPARQL, SHACL
9. [Red Nodes: Validating a Graph with SHACL](09-shacl-data-quality.md) · Building Knowledge Graphs · SHACL, Turtle
10. [From Local IDs to Global Entities](10-entity-linking-sameas.md) · Ecosystems & Knowledge Bases · JSON-LD, SPARQL

## Part 4: Analysis

11. [Do Program Portfolios Recover the Carnegie Classes?](11-program-mix-similarity.md) · Building Knowledge Graphs · Cypher, Python (NetworkX)
12. [GraphRAG vs. CSV RAG: A 20-Question Benchmark](12-graphrag-vs-csv-rag.md) · Knowledge Graphs for SEO · SPARQL, Cypher, JSONL
13. [Putting the Graph on a Map](13-geography-layer.md) · Languages & Formats · GeoSPARQL, WKT, GeoJSON

## Dataset caveats

- 45 institutions is a teaching sample, not a basis for generalizing.
- Within each stratum, selection favors the largest school.
- Several decoded IPEDS labels are flagged "verify" in the dataset README.
- `cip_title` is blank by design; join the NCES CIP 2020 list.

## License

- **Code** is licensed under the [MIT License](LICENSE).
- **Written content** (experiment narratives, documentation and blog drafts) is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CONTENT). You may share and adapt it with attribution to Ray Martinez / KnowledgeGraphNavigator.com.
- **Data** in [`/data`](data/) comes from NCES IPEDS (2024 collection year) and is a U.S. government work in the public domain.
