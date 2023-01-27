SELECT
	title,
	media_type,
	ROUND(AVG(appropriate_score), 2) AS avg_score,
	COUNT(1) AS audience_count
FROM v_appropriate_score
WHERE status = 'COMPLETED' OR (status = 'CURRENT' AND progress >= 5)
GROUP BY title, media_type
HAVING COUNT(1) >= 5
ORDER BY 3 DESC, 4 DESC, 1 DESC