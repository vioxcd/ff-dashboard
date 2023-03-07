{{ config(
	tags=["staging", "historical"]
) }}

WITH
all_lists AS (
	SELECT *
	FROM {{ ref("stg_lists_2022") }}
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