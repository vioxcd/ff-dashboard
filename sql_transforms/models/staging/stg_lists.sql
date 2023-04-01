{{ config(
	materialized="table",
	tags=["staging", "historical"],
	post_hook="DROP TABLE stg_tmp_lists"
) }}

WITH
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
	FROM {{ ref('stg_tmp_lists') }} l
		JOIN {{ source('ff_anilist', 'users') }} u
	USING (username)
),

initial_lists AS (
	SELECT DISTINCT  -- there's duplicate here too...
		id AS user_id,
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
),

all_lists AS (
	SELECT *
	FROM initial_lists
	UNION
	SELECT *
	FROM {{ ref("stg_raw_lists") }}
),

numbered_lists AS (
	-- any difference between the columns listed in PARTITION BY
	-- would result in the record being identified as new
	-- i.e. it's different from the previous ones.
	-- and as it's different, it's possible to filter using `number = 1`
	-- (2 means it's "unchanged" (duplicated);
	-- 1 can be used to filter what's "changed")
	SELECT *,
		ROW_NUMBER() OVER (
			PARTITION BY
				username,
				media_id,
				media_type,
				anichan_score,
				status
			ORDER BY
				retrieved_date
		) AS number
	FROM all_lists
),

historical_lists AS (
	SELECT *,
		LEAD(retrieved_date) OVER (
			PARTITION BY
				username,
				media_id,
				media_type
			ORDER BY
				retrieved_date ASC
		) AS next_date
	FROM numbered_lists
	WHERE number = 1 -- ' filter
)

SELECT
	user_id, username, score_format, generation, score,
	anichan_score, appropriate_score, status, media_id, media_type,
	title, progress, completed_at, retrieved_date, next_date
FROM historical_lists