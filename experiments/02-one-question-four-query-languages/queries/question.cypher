// Which schools offer a fully online master's in the health professions
// and graduate more than 60% of their students within six years?
//
// Cypher (Kuzu), against a labeled property graph built from the same CSVs.
MATCH (i:Institution)-[:OFFERS]->(o:Offering)-[:IN_FAMILY]->(f:CipFamily {code: '51'})
WHERE o.awardLevelCode = 7
  AND o.fullyDistance > 0
  AND i.gradRate150All > 60
RETURN i.unitid         AS unitid,
       i.name           AS institution,
       i.gradRate150All AS gradRate6yr,
       count(o)         AS onlineHealthMasters
ORDER BY gradRate6yr DESC;
