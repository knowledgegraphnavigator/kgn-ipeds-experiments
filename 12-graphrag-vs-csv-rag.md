---
title: "GraphRAG vs. CSV RAG: A 20-Question Benchmark"
slug: graphrag-vs-csv-rag
experiment: 12
series_part: "Part 4: Analysis"
kgn_section: "Knowledge Graphs for SEO"
languages: [SPARQL, Cypher, JSONL]
ontology: "schema.org + custom"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/12-graphrag-vs-csv-rag/
status: planned
---

# GraphRAG vs. CSV RAG: A 20-Question Benchmark

Does putting data in a graph make AI answers more accurate? This experiment tests the idea instead of assuming it.

Twenty questions with known answers are asked three ways: an LLM retrieving from the raw CSVs, an LLM writing SPARQL against the RDF graph, and an LLM writing Cypher against the property graph. Answers are scored for correctness, and the failures are categorized: wrong join, wrong field, misread code, invented value. The repo publishes the questions, gold answers and every model transcript so others can rerun it. The narrative is direct about the results, including where the graph helped, where plain retrieval held up, and what that means for anyone structuring content to be cited by AI answer engines.

**Visualization:** Scoreboard by question type, with drill-down to each query and answer.
