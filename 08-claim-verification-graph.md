---
title: "The Claim Verification Graph"
slug: claim-verification-graph
experiment: 8
series_part: "Part 3: Search"
kgn_section: "Knowledge Graphs for SEO"
languages: [JSON-LD, SPARQL, SHACL]
ontology: "schema.org"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/08-claim-verification-graph/
status: planned
---

# The Claim Verification Graph

Universities publish thousands of claims: tuition, graduation rates, online availability, student-faculty ratios. AI answer engines repeat them. How many are true?

The experiment crawls the structured data and visible claims on a sample of the 45 institutions' sites and graphs each claim against IPEDS ground truth. Each edge gets a status: match, mismatch, stale, unverifiable or missing. This is the job the dataset was built for, so the experiment also tests the dataset. Some mismatches turn out to be definitional (in-state vs. out-of-state tuition, 4-year vs. 6-year graduation rates) and not errors. The post shows how a knowledge graph turns an audit spreadsheet into something you can query, and why consistent, verifiable facts matter for how AI systems describe an institution.

**Visualization:** Institution hub with claim edges colored by verification status.
