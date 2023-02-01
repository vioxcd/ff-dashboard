SELECT
  title,
  media_type,
  CAST(AVG(appropriate_score) AS INTEGER) AS avg_score,
  CAST(AVG(scores_anichan) AS INTEGER) AS avg_anichan_score,
  COUNT(1) AS audience_count
FROM v_appropriate_score
WHERE (status = 'COMPLETED' OR (status = 'CURRENT' AND progress >= 5)) -- rules
  AND CAST(appropriate_score AS INTEGER) > 0 -- don't calculate non-rating
  AND CAST(scores_anichan AS INTEGER) > 0
GROUP BY title, media_type
HAVING COUNT(1) >= 5
ORDER BY 3 DESC, 5 DESC, 1 DESC