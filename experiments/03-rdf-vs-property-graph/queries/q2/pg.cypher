// Total completions at each award level, across all 45 institutions.
// The CSV totals are the ground truth.
MATCH (:Institution)-[r:CONFERRED]->(:Cip)
RETURN r.awardLevelCode AS level, sum(r.completions) AS total
ORDER BY level;
