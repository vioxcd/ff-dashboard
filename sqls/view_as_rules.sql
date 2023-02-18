CREATE VIEW v_as_rules
AS
SELECT
	media_id,
	title,
	media_type,
	CAST(AVG(anichan_score) AS INTEGER) AS anichan_score,
	CAST(AVG(appropriate_score) AS INTEGER) AS ff_score,
	COUNT(1) AS audience_count
FROM v_appropriate_score
WHERE (status = 'COMPLETED' OR (status IN ('CURRENT', 'PAUSED') AND progress >= 5)) -- rules: completed or at least 5 eps progress
	AND CAST(anichan_score AS INTEGER) > 0 -- don't calculate non-rating
	AND CAST(appropriate_score AS INTEGER) > 0 -- don't calculate non-rating
GROUP BY title, media_type
HAVING COUNT(1) >= 5 -- rules: minimum watched by 5 members
-- ORDER BY 3 DESC, 4 DESC, 5 DESC, 1 DESC  -- ordering