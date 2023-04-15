{{ config(tags='intermediate') }}

WITH
counted_favs AS (
	SELECT
	 	item_id,
		name,
		type,
		cover_image_url,
		COUNT(1) AS audience_count
	FROM {{ ref('stg_favourites') }}
	GROUP BY 1, 2
),

ordered_per_type AS (
	SELECT
		*,
		1 - PERCENT_RANK()
			OVER(PARTITION BY type
				 ORDER BY audience_count DESC)
			AS pct_rank
	FROM counted_favs
)

SELECT *
FROM ordered_per_type
