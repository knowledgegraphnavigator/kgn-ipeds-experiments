-- Which schools offer a fully online master's in the health professions
-- and graduate more than 60% of their students within six years?
--
-- SQL (DuckDB), run directly against the IPEDS CSVs.
SELECT
    i.UNITID                        AS unitid,
    i.name                          AS institution,
    o.gr4_rate_150_all_pct          AS grad_rate_6yr,
    count(*)                        AS online_health_masters
FROM programs      AS p
JOIN institutions  AS i ON i.UNITID = p.UNITID
JOIN outcomes      AS o ON o.UNITID = p.UNITID
WHERE p.cip_2digit = '51'                       -- Health Professions
  AND p.awlevel_code = 7                        -- Master's degree
  AND p.programs_offered_fully_distance > 0     -- offered fully online
  AND o.gr4_rate_150_all_pct > 60               -- 150% of normal time = 6 years
GROUP BY i.UNITID, i.name, o.gr4_rate_150_all_pct
ORDER BY grad_rate_6yr DESC;
