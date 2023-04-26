{{ config(
	tags=["staging", "cleaning", "bug_fixing", "mapping"]
) }}

WITH
converted_raw_lists AS (
	SELECT
		user_id,
		username,
		score,
		CAST(anichan_score AS INTEGER) AS anichan_score, -- only this one lol
		status,
		media_id,
		media_type,
		title,
		progress,
		completed_at,
		retrieved_date,
		next_date
	FROM {{ source('ff_anilist', 'raw_lists') }}
),

map_anichan_score_to_point_3_and_5_format AS (
	-- the translation here (the ranges) mostly follows the `score_mapping` previously investigated
	-- e.g. users in those table have these ranges of `anichan_score` for these ranges of `correct_score`
	SELECT
		rl.user_id,
		rl.username,
		CASE u.score_format
			WHEN 'POINT_3' THEN
				CASE
					WHEN rl.anichan_score = 100 THEN 3
					WHEN rl.anichan_score >= 60 THEN 2
					ELSE 1
				END
			WHEN 'POINT_5' THEN
				CASE
					WHEN rl.anichan_score >= 90 THEN 5
					WHEN rl.anichan_score >= 70 THEN 4
					WHEN rl.anichan_score >= 50 THEN 3
					WHEN rl.anichan_score >= 30 THEN 2
					ELSE 1
				END
			ELSE NULL
		END AS score,
		rl.anichan_score,
		rl.status,
		rl.media_id,
		rl.media_type,
		rl.title,
		rl.progress,
		rl.completed_at,
		rl.retrieved_date,
		rl.next_date
	FROM converted_raw_lists rl
	JOIN {{ source('ff_anilist', 'users') }} u
		ON rl.user_id = u.id
	WHERE rl.score != '0'
		AND u.score_format IN ('POINT_3', 'POINT_5')
),

nonmapped_lists AS (
	SELECT *
	FROM converted_raw_lists
	WHERE
		user_id || '-' || media_id || '-' || media_type NOT IN (
			SELECT user_id || '-' || media_id || '-' || media_type
			FROM map_anichan_score_to_point_3_and_5_format
		)
),

all_lists AS (
	SELECT * FROM map_anichan_score_to_point_3_and_5_format
	UNION
	SELECT * FROM nonmapped_lists
),

transformed_to_appropriate_score AS (
	-- the same operation as in `v_appropriate_score`
	SELECT
		*,
		CASE u.score_format
			WHEN 'POINT_10_DECIMAL' THEN CAST(l.anichan_score AS REAL) / 10
			WHEN 'POINT_10' THEN CAST(l.anichan_score AS INTEGER) / 10
			ELSE l.score
		END AS correct_score,
		CASE u.score_format
			WHEN 'POINT_10_DECIMAL' THEN CAST(l.anichan_score AS INTEGER)
			WHEN 'POINT_10' THEN CAST(l.anichan_score AS INTEGER)
			WHEN 'POINT_5' THEN l.score * 20
			WHEN 'POINT_3' THEN
				CASE l.score
					WHEN 1 THEN 35
					WHEN 2 THEN 70
					WHEN 3 THEN 100
				END
			ELSE l.score
		END AS appropriate_score
	FROM all_lists l
	JOIN {{ source('ff_anilist', 'users') }} u
		ON l.user_id = u.id
)

-- made it as how initial `lists` looks like
-- important for next stage deduplication
SELECT
	user_id,
	username,
	score_format,
	generation,
	correct_score AS score,
	CAST(anichan_score AS INTEGER) AS anichan_score,
	CAST(appropriate_score AS INTEGER) AS appropriate_score,
	status,
	media_id,
	media_type,
	title,
	progress,
	completed_at,
	retrieved_date,
	next_date
FROM transformed_to_appropriate_score
ORDER BY
	user_id,
	media_id