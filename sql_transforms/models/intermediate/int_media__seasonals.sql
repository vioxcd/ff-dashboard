{{ config(tags='intermediate') }}

WITH
seasonal_as_rules AS (
	SELECT
		ar.*,
		md.*,
		CASE season
			WHEN "WINTER" THEN 0
			WHEN "SPRING" THEN 1
			WHEN "SUMMER" THEN 2
			ELSE 3
		END AS season_code
	FROM {{ ref('int_media__as_rules') }} ar
		JOIN {{ source('ff_anilist', 'media_details') }} md
		USING (media_id)
	WHERE
		season IS NOT NULL
		AND season_year IS NOT NULL
),

season_ranked AS (
	SELECT
		ROW_NUMBER() OVER (PARTITION BY season_year, season_code
							ORDER BY
								anichan_score DESC,
								ff_score DESC,
								audience_count DESC
							) AS in_season_rank,
		*
	FROM seasonal_as_rules
)

SELECT *
FROM season_ranked
ORDER BY season_year DESC, season_code DESC, ff_score DESC