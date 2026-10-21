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
status: planned
---

# One Question, Four Query Languages

Which schools offer a fully online master's in the health professions and also graduate more than 60% of their students in six years? A prospective student could plausibly ask this, and answering it means joining institutions, programs, award levels, distance-education flags and outcomes.

The experiment asks the question four ways: in SPARQL against a triplestore, in Cypher against Neo4j, in ISO GQL, and in SQL against the original CSVs. Each version is shown next to the subgraph it returns. The answers should agree. Where they don't, the cause is usually a modeling choice and not a bug, which is the experiment's real subject. Readers see how pattern-matching languages express joins as shapes, while SQL treats them as table operations. The post ends by covering where each language fits in a modern stack.

**Visualization:** Query editor tabs that light up the matching subgraph.
