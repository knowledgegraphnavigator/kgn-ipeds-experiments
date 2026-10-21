---
title: "Programs as a Taxonomy: CIP in SKOS"
slug: cip-as-skos
experiment: 5
series_part: "Part 2: Meaning"
kgn_section: "Core Concepts"
languages: [Turtle, SKOS]
ontology: "SKOS; CIP 2020"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/05-cip-as-skos/
status: planned
---

# Programs as a Taxonomy: CIP in SKOS

Every U.S. academic program is classified with a CIP code: a two-digit family, a four-digit series and a six-digit program. In this dataset, 1,065 distinct codes are spread across 8,034 offerings, and Health Professions alone accounts for 979 of them.

This experiment turns the CIP hierarchy and the 12 IPEDS award levels into SKOS concept schemes, linking codes with skos:broader and adding labels from the NCES CIP 2020 list. A sunburst sized by completions shows where degrees actually get conferred. The narrative explains why SKOS exists apart from OWL. A taxonomy describes how concepts are organized, not what things are, and confusing the two causes a lot of broken ontologies. The post also covers how a controlled vocabulary like CIP gives the same meaning to "nursing" across hundreds of program pages.

**Visualization:** Zoomable sunburst: CIP family to series to program, sized by completions.
