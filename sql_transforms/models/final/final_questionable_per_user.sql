{{ config(
	tags=["final", "dashboard"]
) }}

WITH
ordered_score_diff AS (
	SELECT
		sd.*,
		ROW_NUMBER() OVER (PARTITION BY username
						   ORDER BY score_diff DESC)
						   AS user_score_diff,
		md.cover_image_url_xl AS cover_image_url
	FROM {{ ref('int_media__score_diff') }} sd
	JOIN {{ source('ff_anilist', 'media_details') }} md
		USING (media_id)
),

users_with_no_questionable_titles AS (
	SELECT
		username,
		-1 AS media_id,
		"no questionable title" AS title,
		"-" AS media_type,
		-1 AS mean_score,
		-1 AS audience_count,
		-1 AS appropriate_score,
		-1 AS score_diff,
		-1 AS user_score_diff,
		"-" AS cover_image_url
	FROM {{ source('ff_anilist', 'users') }}
	WHERE username NOT IN (
		SELECT username FROM ordered_score_diff
	)
),

result_set AS (
	SELECT *
	FROM ordered_score_diff
	WHERE user_score_diff = 1  -- ' pick highest score_diff
)

SELECT *
FROM result_set
UNION
SELECT *
FROM users_with_no_questionable_titles
ORDER BY score_diff DESC