{{ config(
	tags=["final", "export", "dashboard"]
) }}

SELECT
	season_year,
	season,
	season_code,
	in_season_rank,
	media_id,
	title,
	anichan_score,
	ff_score,
	audience_count
FROM {{ ref('int_media__seasonals') }}