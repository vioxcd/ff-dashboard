{{ config(tags='intermediate') }}


WITH
calculated_minimal_users AS (
	-- 20% rules
	SELECT CAST(FLOOR(COUNT(1) * .2) AS INTEGER) AS minimal_user
	FROM {{ source('ff_anilist', 'users') }}
)

SELECT
	media_id,
	title,
	media_type,
	CAST(ROUND(AVG(anichan_score)) AS INTEGER) AS anichan_score,
	CAST(ROUND(AVG(appropriate_score)) AS INTEGER) AS ff_score,
	COUNT(1) AS audience_count
FROM {{ ref('stg_lists') }}
WHERE
	(status = 'COMPLETED' OR (status IN ('CURRENT', 'PAUSED') AND progress >= 5))
	AND anichan_score > 0
	AND appropriate_score > 0
	AND next_date IS NULL  -- ' filter for current media
GROUP BY media_id, media_type
HAVING COUNT(1) IN (
	(SELECT minimal_user - 1 FROM calculated_minimal_users),
	(SELECT minimal_user - 2 FROM calculated_minimal_users),
	(SELECT minimal_user - 3 FROM calculated_minimal_users)
)  -- ' potential
ORDER BY
	ff_score DESC,
	audience_count DESC