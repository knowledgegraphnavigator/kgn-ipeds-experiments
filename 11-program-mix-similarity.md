---
title: "Do Program Portfolios Recover the Carnegie Classes?"
slug: program-mix-similarity
experiment: 11
series_part: "Part 4: Analysis"
kgn_section: "Building Knowledge Graphs"
languages: [Cypher, Python (NetworkX)]
ontology: "labeled property graph"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/11-program-mix-similarity/
status: planned
---

# Do Program Portfolios Recover the Carnegie Classes?

Carnegie classifications group institutions by research activity, degree levels and size. A different question: if you only knew which programs a school offers, which schools would look alike?

This experiment projects the institution-to-CIP graph onto institution-to-institution similarity using shared programs, then runs community detection. The resulting clusters are compared with the Carnegie classes and the sample strata. Some groupings should be expected, like the R1s or the 2-year colleges. The surprises are more interesting: a special-focus school that clusters with a research university, or two online giants that look nothing alike. The narrative introduces graph projection and community detection without math-heavy notation and shows how the method extends to competitive analysis for program marketing.

**Visualization:** Force-directed network, nodes colored by detected community, outlined by Carnegie class.
