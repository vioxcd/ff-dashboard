{{ config(
	tags=["final", "dashboard"]
) }}

SELECT
	media_id,
	title,
	media_type,
	status,
	audience_count,
	pct_rank,
	cover_image_url
FROM {{ ref('int_media__by_status_join_media') }}
WHERE status = "CURRENT"