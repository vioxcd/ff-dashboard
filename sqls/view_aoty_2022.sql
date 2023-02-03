CREATE VIEW v_aoty_2022
AS
SELECT
  md.*,
  ar.anichan_score,
  ar.ff_score,
  ar.audience_count
FROM v_as_rules ar
JOIN media_details md
USING (media_id)
WHERE anichan_score >= 80.0
  AND ff_score >= 80.0
  AND media_type = 'ANIME'
  AND season_year = 2022
ORDER BY
  anichan_score DESC,
  ff_score DESC,
  audience_count DESC,
  title DESC