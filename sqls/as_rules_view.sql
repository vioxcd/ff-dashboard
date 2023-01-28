CREATE VIEW v_as_rules
AS
SELECT
	media_id,
	title,
	media_type,
	ROUND(AVG(appropriate_score), 2) AS avg_score,
	COUNT(1) AS audience_count
FROM v_appropriate_score
WHERE (status = 'COMPLETED' OR (status = 'CURRENT' AND progress >= 5)) -- rules: completed or at least 5 eps progress
	AND CAST(appropriate_score AS INTEGER) > 0 -- don't calculate non-rating
GROUP BY title, media_type
HAVING COUNT(1) >= 5 -- rules: minimum watched by 5 members