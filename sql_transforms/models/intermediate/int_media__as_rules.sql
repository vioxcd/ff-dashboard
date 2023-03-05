{{ config(tags='intermediate') }}

-- Rules:
-- (1) has completed or at least 5 eps progress
-- (2) minimum watched by 5 members
SELECT
	media_id,
	title,
	media_type,
	CAST(ROUND(AVG(anichan_score)) AS INTEGER) AS anichan_score,
	CAST(ROUND(AVG(appropriate_score)) AS INTEGER) AS ff_score,
	COUNT(1) AS audience_count
FROM {{ ref('stg_lists') }}
WHERE
	(status = 'COMPLETED' OR (status IN ('CURRENT', 'PAUSED') AND progress >= 5)) -- (1)
	AND anichan_score > 0
	AND appropriate_score > 0 -- don't calculate non-rating
GROUP BY title, media_type
HAVING COUNT(1) >= 5 -- (2)
