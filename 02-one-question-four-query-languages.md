---
title: "One Question, Four Query Languages"
slug: one-question-four-query-languages
experiment: 2
series_part: "Part 1: Syntax"
kgn_section: "Languages & Formats"
languages: [SPARQL, Cypher, GQL, SQL]
ontology: "schema.org + custom"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/02-one-question-four-query-languages/
status: built
---

# One Question, Four Query Languages

Which schools offer a fully online master's in the health professions and also graduate more than 60% of their students in six years? A prospective student could plausibly ask this, and answering it means joining institutions, programs, award levels, distance-education flags and outcomes.

The experiment asks the question four ways: in SQL against the original CSVs, in SPARQL against an RDF graph, in Cypher against an embedded property graph, and in ISO GQL. All four ran, on DuckDB, rdflib, Kùzu and GraphLite, and returned the same six schools. The real subject is what happens when the definitions change: counting the bachelor's-seeking graduation rate drops the answer to five schools, and counting partly online programs raises it to ten. All four languages moved together every time. Small slips are different: leaving the quotes off one code makes SPARQL and GQL return nothing while SQL and Cypher still return six, and the four languages' usual ways of saying "not" disagree about a school with missing data. Readers see how pattern-matching languages express joins as shapes, while SQL treats them as table operations. The post ends by covering where each language fits in a modern stack.

**Visualization:** Query tabs beside a graph of every candidate school, with a switch for each definition.

**Code, results and how to run it:** [`experiments/02-one-question-four-query-languages/`](experiments/02-one-question-four-query-languages/)
