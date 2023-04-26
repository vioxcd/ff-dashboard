{{ config(tags='intermediate') }}

WITH
calculated_minimal_users AS (
	-- 20% rules
	SELECT CAST(FLOOR(COUNT(1) * .2) AS INTEGER) AS minimal_user
	FROM {{ source('ff_anilist', 'users') }}
),

counted_lists AS (
	-- same as `as_rules, but include `n - 1`
	SELECT
		media_id,
		title,
		media_type,
		CAST(ROUND(AVG(anichan_score)) AS INTEGER) AS anichan_score,
		CAST(ROUND(AVG(appropriate_score)) AS INTEGER) AS ff_score,
		COUNT(1) AS audience_count
	FROM {{ ref('stg_lists') }}
	WHERE
		(status = 'COMPLETED' OR (status IN ('CURRENT', 'PAUSED') AND progress >= 5))
		AND anichan_score > 0
		AND appropriate_score > 0
		AND next_date IS NULL
		AND media_type = "ANIME"  -- manga doesn't have seasons...
	GROUP BY media_id, media_type
	HAVING COUNT(1) >= (
		-- same as `as_rules`, but with -1 to include
		-- ongoing series in last & current season
		SELECT minimal_user - 1
		FROM calculated_minimal_users
	)
),

season_rules AS (
	-- helps ordering the columns
	SELECT
		*,
		CASE season
			WHEN "WINTER" THEN 0
			WHEN "SPRING" THEN 1
			WHEN "SUMMER" THEN 2
			ELSE 3
		END AS season_code
	FROM {{ source('ff_anilist', 'media_details') }}
	WHERE
		season IS NOT NULL
		AND season_year IS NOT NULL
		AND media_id IN (SELECT DISTINCT media_id FROM counted_lists) -- filter for non-planning
),

season_dim AS (
	-- rank all season for determining `current and last season` later
	SELECT
		*,
		ROW_NUMBER() OVER (ORDER BY
							season_year DESC,
							season_code DESC
						) AS season_rank
	FROM (
		SELECT DISTINCT season, season_code, season_year
		FROM season_rules
	)
),

current_season AS (
	SELECT
		sd.*,
		l.*,
		md.cover_image_url_xl AS cover_image_url
	FROM counted_lists l
	JOIN {{ source('ff_anilist', 'media_details') }} md
		USING (media_id)
	JOIN season_dim sd
		USING (season, season_year)
	WHERE
		season_rank = 1
		AND audience_count >= (
			-- apply -1 to current and last
			SELECT minimal_user - 1
			FROM calculated_minimal_users
		)
),

current_season_possibly_unrated AS (
	SELECT
		season,
		(SELECT season_code FROM current_season),
		season_year,
		(SELECT season_rank FROM current_season),
		media_id,
		title,
		media_type,
		0 AS anichan_score,
		0 AS ff_score,
		audience_count,
		cover_image_url
	FROM {{ ref('int_media__by_status_join_media') }}
	WHERE
		status = "CURRENT"
		AND media_type = "ANIME"
		AND season = (SELECT season FROM current_season)
		AND season_year = (SELECT season_year FROM current_season)
),

current_season_all AS (
	SELECT *
	FROM current_season
	UNION
	SELECT *
	FROM current_season_possibly_unrated
),

last_season AS (
	SELECT
		sd.*,
		l.*,
		md.cover_image_url_xl AS cover_image_url
	FROM counted_lists l
	JOIN {{ source('ff_anilist', 'media_details') }} md
		USING (media_id)
	JOIN season_dim sd
		USING (season, season_year)
	WHERE
		season_rank = 2
		AND audience_count >= (
			-- apply -1 to current and last
			SELECT minimal_user - 1
			FROM calculated_minimal_users
		)
),

non_current_and_last_season AS (
SELECT
		sd.*,
		l.*,
		md.cover_image_url_xl AS cover_image_url
	FROM counted_lists l
	JOIN {{ source('ff_anilist', 'media_details') }} md
		USING (media_id)
	JOIN season_dim sd
		USING (season, season_year)
	WHERE
		season_rank NOT IN (1, 2)
		AND audience_count >= (
			SELECT minimal_user
			FROM calculated_minimal_users
		)
),

all_seasons AS (
	SELECT *
	FROM current_season_all
	UNION
	SELECT *
	FROM last_season
	UNION
	SELECT *
	FROM non_current_and_last_season
),

in_season_ranked AS (
	SELECT
		-- rank within its own season
		ROW_NUMBER() OVER (PARTITION BY season_year, season_code
							ORDER BY
								ff_score DESC,
								anichan_score DESC,
								audience_count DESC
							) AS in_season_rank,
		*
	FROM all_seasons
)

SELECT
	season_year,
	season,
	season_code,
	season_rank,
	in_season_rank,
	media_id,
	title,
	media_type,
	anichan_score,
	ff_score,
	audience_count,
	cover_image_url
FROM in_season_ranked
ORDER BY season_year DESC, season_code DESC, ff_score DESC