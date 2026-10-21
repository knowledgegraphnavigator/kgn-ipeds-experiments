---
title: "Can a Reasoner Rebuild the Sample?"
slug: can-a-reasoner-rebuild-the-sample
experiment: 6
series_part: "Part 2: Meaning"
kgn_section: "Building Knowledge Graphs"
languages: [OWL 2, Turtle, SPARQL]
ontology: "custom OWL"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/06-can-a-reasoner-rebuild-the-sample/
status: planned
---

# Can a Reasoner Rebuild the Sample?

This dataset's 45 institutions were chosen with 26 written rules: public R1, HBCU, online-heavy (80% or more exclusively distance), tribal college, Hispanic-serving proxy, and so on. Each rule is a class definition in disguise.

This experiment encodes the strata as OWL 2 classes with datatype restrictions, loads the raw facts and runs a reasoner. If the ontology is right, the reasoner should put every school back in its original stratum without being told which one. Where it fails, the gaps teach something: rules that depend on ordering ("largest enrollment first"), closed-world assumptions OWL won't make, and thresholds that need SPARQL or SHACL rules instead. The visual shows asserted and inferred edges in different colors. The post serves as a practical introduction to what reasoning can and can't do.

**Visualization:** Graph where inferred class memberships animate in after the reasoner runs.
