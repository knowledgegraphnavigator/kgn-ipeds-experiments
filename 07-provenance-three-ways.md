---
title: "Where Did This Fact Come From?"
slug: provenance-three-ways
experiment: 7
series_part: "Part 2: Meaning"
kgn_section: "Core Concepts"
languages: [RDF-star, TriG, PROV-O]
ontology: "PROV-O; Wikidata qualifiers"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/07-provenance-three-ways/
status: planned
---

# Where Did This Fact Come From?

UCF's fall 2024 admit rate is 40.1%. The figure comes from the ADM2024 survey, it's derived by dividing admits by applicants, and a newer survey will replace it next year. A graph that stores only "40.1" has thrown away everything that makes the number trustworthy.

This experiment attaches provenance to that one fact in three ways: with RDF-star annotations, with named graphs in TriG, and with the W3C PROV-O vocabulary. It then compares all three to Wikidata's references and qualifiers. The dataset's data dictionary already records source file, variable and survey year for every column, so provenance can be generated instead of written by hand. The narrative argues that for any graph feeding AI answers, statement-level sourcing is a requirement and not an extra.

**Visualization:** One fact node expanding into its source, survey year and derivation chain.
