SELECT
  title,
  media_type
FROM v_appropriate_score
WHERE status IN ('COMPLETED', 'CURRENT')
GROUP BY title, media_type
HAVING COUNT(1) >= 5
EXCEPT
SELECT
  title,
  media_type
FROM v_appropriate_score
WHERE status = 'COMPLETED' OR (status = 'CURRENT' AND progress >= 5)
GROUP BY title, media_type
HAVING COUNT(1) >= 5