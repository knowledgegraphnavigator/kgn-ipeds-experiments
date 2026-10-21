---
title: "Where Does the Number Go? RDF vs. Property Graphs"
slug: rdf-vs-property-graph
experiment: 3
series_part: "Part 1: Syntax"
kgn_section: "Languages & Formats"
languages: [Turtle, RDF-star, Cypher]
ontology: "schema.org; labeled property graph"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/03-rdf-vs-property-graph/
status: planned
---

# Where Does the Number Go? RDF vs. Property Graphs

In 2023-24, Arizona State conferred a specific number of bachelor's degrees in one CIP code. That count doesn't belong to the school or to the program. It belongs to the relationship between them.

This experiment loads the 8,034 program rows into an RDF triplestore and a property graph database and examines how each one handles facts that describe a relationship. A property graph puts the count on the edge. Classic RDF has to create an intermediate "offering" node, and RDF-star can annotate the triple directly. The visual shows all three models side by side. The narrative explains why the two ecosystems grew apart, what each gives up, and why converging standards like RDF 1.2 and GQL matter for teams choosing a graph database today.

**Visualization:** Three mini-graphs of the same offering: edge property, intermediate node, quoted triple.
