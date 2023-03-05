{{ config(
	tags=["staging", "cleaning", "bug_fixing", "mapping"]
) }}

WITH
mapped_lists AS (
	-- `raw_lists` score has this bug where the 1st record out of each 50 batch
	-- are the actual score used by the user, while the other 49s follows the `anichan_score`
	--
	-- here, try to map each of those buggy `score` to an already known mapping of
	-- `anichan_score` (the mappings are from previously done "correct but slow" ETL)
	SELECT
		rl.username,
		m.score,  -- use score from the mapping
		rl.anichan_score,
		rl.status,
		rl.media_id,
		rl.media_type,
		rl.title,
		rl.progress,
		rl.completed_at,
		rl.retrieved_date
	FROM {{ source('ff_anilist', 'score_mapping') }} m
		JOIN {{ source('ff_anilist', 'raw_lists') }} rl
		ON m.anichan_score = rl.score
			AND m.username = rl.username
	WHERE CAST(rl.score AS INTEGER) != 0
),

nonmapped_lists AS (
	SELECT *
	FROM {{ source('ff_anilist', 'raw_lists') }}
	WHERE
		username || '-' || media_id || '-' || media_type NOT IN (
			SELECT username || '-' || media_id || '-' || media_type
			FROM mapped_lists
		)
),

all_lists AS (
	-- vertically join the two lists
	-- and at the same time remove duplicate entries
	SELECT * FROM mapped_lists
	UNION
	SELECT * FROM nonmapped_lists
),

transformed_to_appropriate_score AS (
	-- the same operation as in `v_appropriate_score`
	SELECT
		*,
		CASE u.score_format
			WHEN 'POINT_10_DECIMAL' THEN CAST(l.anichan_score AS REAL) / 10
			WHEN 'POINT_10' THEN CAST(l.anichan_score AS REAL) / 10
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
	USING (username)
)

-- made it as how initial `lists` looks like
-- important for next stage deduplication
SELECT
	id AS user_id,
	username,
	score_format,
	generation,
	CAST(appropriate_score AS INTEGER) AS score,
	CAST(anichan_score AS INTEGER) AS anichan_score,
	status,
	media_id,
	media_type,
	title,
	progress,
	completed_at,
	retrieved_date
FROM transformed_to_appropriate_score
ORDER BY
	user_id,
	media_id