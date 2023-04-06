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

mapped_lists AS (
	-- some users have used a different `score_format` in the past and their previous
	-- score (the ones different than the current `score_format`) is still encoded in the
	-- `anichan_score` value
	--
	-- this make it seems like there's two possible score value: the "correct" one following
	-- the current `score_format` and the `anichan_score` preserved one
	--
	-- the thing is, we can do translation between these two format, that is:
	-- `anichan` -> `correct` -> `appropriate`, where
	-- - `anichan` are the preserved ("original" if you like) ones
	-- - `correct` are anichan's appropriated to user's current `score_format`
	-- - `appropriate` are `correct` translated to 100s
	--
	-- for users with `score_format` of 10s, 100s, or 10.0s, translations is not a problem
	-- because their it's easy to do, while for users with `score_format` of 3s and 5s,
	-- a mapping table like this are needed to know exactly what `anichan` score ranges
	-- are translated to which 3s or 5s
	--
	-- as have stated above, these mappings only exists for users that are known to have
	-- `score_format` of 3s and 5s
	--
	-- anyway, the Anilist API has this bug where the 1st record out of each 50 batch
	-- are the actual score used by the user, while the other 49s follows the `anichan_score`
	-- and this bug is *always* encoded in `raw_lists` score. why? because to get the "correct"
	-- score is very slow (must fetch 1 records per-request) and is mostly unnecessary
	-- (scores rarely changes)
	--
	-- so, here we're trying to map each of those buggy `score` to an already known mapping of
	-- `anichan_score` (the mappings are from previously done "correct but slow" ETL)
	SELECT
		rl.user_id,
		rl.username,
		m.score,  -- use score from the mapping
		rl.anichan_score,
		rl.status,
		rl.media_id,
		rl.media_type,
		rl.title,
		rl.progress,
		rl.completed_at,
		rl.retrieved_date,
		rl.next_date
	FROM {{ source('ff_anilist', 'score_mapping') }} m
	JOIN converted_raw_lists rl
		ON m.anichan_score = rl.score
		AND m.user_id = rl.user_id
	WHERE rl.score != '0'
),

should_be_mapped_but_not_included AS (
	-- the data here includes users that changed their `score_format` in the future,
	-- so there's no mapping for them, but their `correct_score` are translated from
	-- `anichan` (the preserved ones), assumming they're actually not changing that much
	--
	-- the translation here (the ranges) mostly follows the `score_mapping` previously defined
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
		AND rl.user_id NOT IN (
			SELECT DISTINCT user_id
			FROM {{ source('ff_anilist', 'score_mapping') }}
		)
),

nonmapped_lists AS (
	SELECT *
	FROM converted_raw_lists
	WHERE
		user_id || '-' || media_id || '-' || media_type NOT IN (
			SELECT user_id || '-' || media_id || '-' || media_type
			FROM mapped_lists
			UNION
			SELECT user_id || '-' || media_id || '-' || media_type
			FROM should_be_mapped_but_not_included
		)
),

all_lists AS (
	SELECT * FROM mapped_lists
	UNION
	SELECT * FROM should_be_mapped_but_not_included
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