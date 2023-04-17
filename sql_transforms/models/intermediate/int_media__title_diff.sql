{{ config(tags='intermediate') }}

SELECT
	sd.media_id,
	sd.title,
	sd.media_type,
	CAST(AVG(appropriate_score) AS INTEGER) AS should_be_score,
	COUNT(1) AS audience_count,
	sd.mean_score AS actual_score,
	sd.audience_count AS actual_audience_count,
	md.cover_image_url_xl AS cover_image_url
FROM {{ ref('int_media__score_diff') }} sd
JOIN {{ source('ff_anilist', 'media_details') }} md
	USING (media_id)
GROUP BY media_id
ORDER BY audience_count DESC, should_be_score DESC