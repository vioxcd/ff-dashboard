{{ config(tags=["intermediate"]) }}

WITH
get_media_lists AS (
	SELECT
		ar.*,
		md.season,
		md.season_year,
		md.episodes,
		md.format,
		md.average_score,
		md.mean_score,
		md.source,
		md.studios,
		md.is_sequel,
		md.cover_image_url_xl AS cover_image_url
	FROM {{ ref('int_media__as_rules') }} ar
	JOIN {{ source('ff_anilist', 'media_details') }} md
		USING (media_id)
),

get_sections AS (
	SELECT
		CASE
			WHEN anichan_score >= 90 OR ff_score >= 90
				THEN "gold"
			WHEN (anichan_score > 85 AND anichan_score < 90)
				OR (ff_score > 85 AND ff_score < 90)
				THEN "silver"
			WHEN anichan_score = 85 OR ff_score = 85
				THEN "bronze"
			ELSE "-"
		END AS section,
		*
	FROM get_media_lists
),

get_sections_rank AS (
	SELECT
		ROW_NUMBER() OVER (PARTITION BY media_type
							ORDER BY
								CASE section
									WHEN "gold" THEN 0
									WHEN "silver" THEN 1
									WHEN "bronze" THEN 2
									ELSE 3
								END,
								anichan_score DESC,
								ff_score DESC,
								audience_count DESC,
								title DESC
							) AS ranking,
		*
	FROM get_sections
)

SELECT *
FROM get_sections_rank
ORDER BY ranking