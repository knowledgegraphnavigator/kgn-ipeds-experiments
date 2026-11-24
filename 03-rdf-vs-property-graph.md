---
title: "Where Does the Number Go? RDF vs. Property Graphs"
slug: rdf-vs-property-graph
experiment: 3
series_part: "Part 1: Syntax"
kgn_section: "Languages & Formats"
languages: [Turtle, RDF-star, RDF 1.2, Cypher, SPARQL]
ontology: "schema.org; labeled property graph"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/03-rdf-vs-property-graph/
status: built
---

# Where Does the Number Go? RDF vs. Property Graphs

In 2023-24, Arizona State University Campus Immersion conferred 701 bachelor's degrees in Computer Science (CIP 11.0701). That count doesn't belong to the school or to the program. It belongs to the relationship between them, and only at one award level: the same pair also produced 842 master's degrees and 18 research doctorates.

This experiment writes all 8,034 program rows in five models and queries each in a real engine: a property graph with the count on the edge (Kùzu), RDF with an intermediate offering node, RDF 1.1 standard reification, RDF 1.2 named reifiers, and RDF-star annotation syntax (Oxigraph). Every model that gives each row its own edge, node or reifier returns 701. The same `<< >>` Turtle file read under the 2021 RDF-star semantics returns 18, 701 and 842, and inflates total completions from 451,677 to 1,061,729, because 43% of school-CIP pairs have more than one award level. Naming an RDF 1.2 reifier for the pair instead of the row repeats the mistake. The narrative covers what each model costs and why RDF 1.2 and GQL matter for teams choosing a graph database today.

**Visualization:** Six mini-graphs of the same relationship, one per model, with the answer each engine returns.

**Code, results and how to run it:** [`experiments/03-rdf-vs-property-graph/`](experiments/03-rdf-vs-property-graph/)
