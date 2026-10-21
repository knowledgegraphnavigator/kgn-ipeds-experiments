---
title: "Same Data, Three Worldviews"
slug: swap-the-ontology
experiment: 4
series_part: "Part 2: Meaning"
kgn_section: "Core Concepts"
languages: [JSON-LD, Turtle, OWL]
ontology: "schema.org; Wikidata; custom OWL"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/04-swap-the-ontology/
status: planned
---

# Same Data, Three Worldviews

An ontology determines which questions a graph can answer. This experiment models the same 45 institutions three ways: with schema.org's CollegeOrUniversity, EducationalOccupationalProgram and Offer; with Wikidata's item-and-statement model; and with a small purpose-built OWL ontology.

The three graphs differ in useful ways. schema.org is built for search engines and flattens things, so tuition, graduation rate and retention end up as loosely attached properties. Wikidata keeps everything but nests it under qualifiers. The custom ontology expresses the domain precisely, but no external system can read it. Readers watch the same facts land in three different shapes and then see what each shape makes easy or hard to query. The takeaway is that most real projects use more than one ontology and map between them.

**Visualization:** Toggle between three ontology views of one institution; nodes morph between layouts.
