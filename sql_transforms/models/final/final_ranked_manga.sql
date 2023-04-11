{{ config(
	tags=["final", "export"]
) }}


-- exclude empty data (season, season_year, episodes, studios) and redundant (format)
SELECT
	ranking,
	section,
	media_id,
	title,
	media_type,
	anichan_score,
	ff_score,
	audience_count,
	average_score,
	mean_score,
	source,
	is_sequel,
	cover_image_url
FROM {{ ref('int_media__section_and_ranking') }}
WHERE media_type == "MANGA"