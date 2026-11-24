// How many bachelor's degrees (award level 5) did Arizona State University
// Campus Immersion confer in CIP 11.0701 (Computer Science) in 2023-24?
// Property graph: the count is a property on the CONFERRED edge.
MATCH (i:Institution {unitid: '104151'})-[r:CONFERRED]->(c:Cip {code: '11.0701'})
WHERE r.awardLevelCode = 5
RETURN r.completions AS completions;
