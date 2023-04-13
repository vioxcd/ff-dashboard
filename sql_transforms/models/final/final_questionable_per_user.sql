{{ config(
	tags=["final", "dashboard"]
) }}

WITH ordered_score_diff AS (
	SELECT
		*,
		ROW_NUMBER() OVER (PARTITION BY username
						   ORDER BY score_diff DESC)
						   AS user_score_diff
	FROM {{ ref('int_media__score_diff') }}
)

SELECT *
FROM ordered_score_diff
WHERE user_score_diff = 1  -- ' pick highest score_diff
