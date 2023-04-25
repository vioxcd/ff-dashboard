{{ config(
	tags=["final", "export", "dashboard"]
) }}

SELECT
	p.*,
	md.cover_image_url_xl AS cover_image_url
FROM {{ ref('int_media__potential') }} p
JOIN {{ source('ff_anilist', 'media_details') }} md
	USING (media_id)
WHERE
	anichan_score >= 80
	OR ff_score >= 80