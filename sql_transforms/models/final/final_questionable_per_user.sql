{{ config(
	tags=["final", "dashboard"]
) }}

WITH ordered_score_diff AS (
	SELECT
		sd.*,
		ROW_NUMBER() OVER (PARTITION BY username
						   ORDER BY score_diff DESC)
						   AS user_score_diff,
		md.cover_image_url_xl AS cover_image_url
	FROM {{ ref('int_media__score_diff') }} sd
	JOIN {{ source('ff_anilist', 'media_details') }} md
		USING (media_id)
)

SELECT *
FROM ordered_score_diff
WHERE user_score_diff = 1  -- ' pick highest score_diff
