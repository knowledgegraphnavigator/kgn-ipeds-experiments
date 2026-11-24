MERGE (i:Institution {unitid: '104151', name: "Arizona State University Campus Immersion"})
MERGE (c:Cip {code: '11.0701', family: "Computer and Information Sciences and Support Services"})
CREATE (i)-[:CONFERRED {awardLevelCode: 5, completions: 701}]->(c)
CREATE (i)-[:CONFERRED {awardLevelCode: 7, completions: 842}]->(c)
CREATE (i)-[:CONFERRED {awardLevelCode: 17, completions: 18}]->(c);
