---
title: "Putting the Graph on a Map"
slug: geography-layer
experiment: 13
series_part: "Part 4: Analysis"
kgn_section: "Languages & Formats"
languages: [GeoSPARQL, WKT, GeoJSON]
ontology: "GeoSPARQL; schema.org Place"
dataset: IPEDS 2024 GEO Audit Test Dataset v1.0
repo_path: /experiments/13-geography-layer/
status: planned
---

# Putting the Graph on a Map

Every institution in the dataset has a latitude, longitude, county, NCES locale code and BEA region. This experiment adds those as a spatial layer and models them two ways: as schema.org Place and GeoCoordinates, and with OGC GeoSPARQL geometries.

Once the graph knows where things are, it can answer new questions: which rural institutions offer fully online programs, or how out-of-state distance enrollment compares with a school's home region. The visual pairs a map with the graph, so selecting a region filters both. The narrative covers the gap between describing a location (what schema.org does) and reasoning about one (what GeoSPARQL does), and why local-intent searches put pressure on institutions to get location data right.

**Visualization:** Linked map and graph panels with region and locale filters.
