{{ config(tags='intermediate') }}

WITH
lists_by_status AS (
	SELECT
		media_id,
		title,
		media_type,
		status
	FROM {{ ref('stg_lists') }}
	WHERE status IN ("CURRENT", "DROPPED", "PLANNING") AND next_date IS NULL
),

status_counts AS (
	SELECT
		media_id,
		title,
		media_type,
		status,
		COUNT(1) AS audience_count
	FROM lists_by_status
	GROUP BY media_id, media_type, status
),

ordered_status AS (
	SELECT
		*,
		1 - PERCENT_RANK()
			OVER(PARTITION BY status
				 ORDER BY audience_count DESC
			) AS pct_rank
	FROM status_counts
)

SELECT
	os.*,
	md.cover_image_url_xl AS cover_image_url
FROM ordered_status os
JOIN {{ source('ff_anilist', 'media_details') }} md
	USING (media_id)
WHERE pct_rank > .95
ORDER BY status, audience_count DESC