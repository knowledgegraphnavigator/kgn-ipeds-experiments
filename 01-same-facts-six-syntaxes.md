---
title: "One University, Six Syntaxes"
slug: same-facts-six-syntaxes
experiment: 1
series_part: "Part 1: Syntax"
kgn_section: "Languages & Formats"
languages: [JSON-LD, Microdata, RDFa, Turtle, N-Triples, JSONL]
ontology: "schema.org"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/01-same-facts-six-syntaxes/
status: built
---

# One University, Six Syntaxes

Rose-Hulman Institute of Technology reports the same facts to IPEDS every year: an address, a Carnegie class, 2,334 students, a 76.9% admit rate. This experiment writes those facts six times, once each in JSON-LD, Microdata, RDFa, Turtle, N-Triples and JSONL, and renders all six as a graph.

All six carry the same facts, but only four produce the identical graph. The two HTML formats inherit the page's `lang="en"`, so their strings come back language-tagged, and Microdata has no way to say "decimal," so the admission rate becomes a double. The point most readers miss is that choosing a format and choosing a data model are separate decisions, and that the format can still change the details. The post walks through what each syntax is good at, why JSON-LD became the default for structured data on the web, and where Turtle stays easier to read. The repo includes a script that round-trips each file through an RDF parser to prove the graphs match.

**Visualization:** Six code panels beside one shared, highlighted graph.

**Code, results and how to run it:** [`experiments/01-same-facts-six-syntaxes/`](experiments/01-same-facts-six-syntaxes/)
