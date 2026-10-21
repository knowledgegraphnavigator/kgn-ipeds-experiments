---
title: "From Local IDs to Global Entities"
slug: entity-linking-sameas
experiment: 10
series_part: "Part 3: Search"
kgn_section: "Ecosystems & Knowledge Bases"
languages: [JSON-LD, SPARQL]
ontology: "schema.org sameAs; Wikidata"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/10-entity-linking-sameas/
status: planned
---

# From Local IDs to Global Entities

Inside IPEDS, Ohio State is 204796. In College Scorecard it's an OPE ID. In Wikidata it's a Q-number, and Google has its own Knowledge Graph ID. Each identifier is a door into a different body of knowledge.

This experiment reconciles all 45 institutions to Wikidata using its IPEDS ID property, links OPE IDs for the planned Scorecard join, and visualizes the resulting sameAs network. It reports how many matched cleanly, where branch campuses and system offices confused the match, and which schools' own websites declare sameAs links in their markup. The narrative explains entity reconciliation as the step that turns a dataset into part of the wider web of data, and why it matters for being recognized as an entity in search.

**Visualization:** Bipartite view: local identifiers on the left, global entities on the right, sameAs bridges between.
