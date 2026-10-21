---
title: "Red Nodes: Validating a Graph with SHACL"
slug: shacl-data-quality
experiment: 9
series_part: "Part 3: Search"
kgn_section: "Building Knowledge Graphs"
languages: [SHACL, Turtle]
ontology: "schema.org; SHACL"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/09-shacl-data-quality/
status: planned
---

# Red Nodes: Validating a Graph with SHACL

A graph is only as good as its constraints. This experiment writes SHACL shapes for the higher-ed graph: every program needs a credential level, every price needs a currency, graduation rates must fall between 0 and 100, and graduate-only institutions shouldn't carry undergraduate outcomes.

Then it runs them. The violations come from real gaps the README already documents: no institutional accreditor yet, CIP titles that need a join, religious affiliation codes left undecoded, and fields marked "verify." Each violation appears as a red node. The narrative presents validation as documentation that runs and compares SHACL with JSON Schema and the Rich Results Test. Teams that publish structured data at scale should treat shapes like unit tests.

**Visualization:** Graph with violating nodes in red and a sidebar listing each failed constraint.
