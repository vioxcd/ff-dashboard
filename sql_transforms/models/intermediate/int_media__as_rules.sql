{{ config(tags='intermediate') }}

-- Rules:
-- (1) has completed or at least 5 eps progress
-- (2) rules changed! minimum watched by 20% members
-- a change of logic to this model must happen to `int_aoty_2022__as_rules` model too
SELECT
	media_id,
	title,
	media_type,
	CAST(ROUND(AVG(anichan_score)) AS INTEGER) AS anichan_score,
	CAST(ROUND(AVG(appropriate_score)) AS INTEGER) AS ff_score,
	COUNT(1) AS audience_count
FROM {{ ref('stg_lists') }}
WHERE
	(status IN ('COMPLETED', 'REPEATING') OR (status IN ('CURRENT', 'PAUSED') AND progress >= 5)) -- (1)
	AND anichan_score > 0
	AND appropriate_score > 0 -- don't calculate non-rating
	AND next_date IS NULL -- ' filter for current media
GROUP BY media_id, media_type
HAVING COUNT(1) >= (
	SELECT CAST(FLOOR(COUNT(1) * .2) AS INTEGER)
	FROM {{ source('ff_anilist', 'users') }}
) -- (2)