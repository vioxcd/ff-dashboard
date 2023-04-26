{{ config(tags='intermediate') }}

SELECT
	s.*,
	md.cover_image_url_xl AS cover_image_url
FROM {{ ref('int_media__by_status') }} s
JOIN {{ source('ff_anilist', 'media_details') }} md
	USING (media_id)
ORDER BY status, audience_count DESC