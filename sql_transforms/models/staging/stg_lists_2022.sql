{{ config(
	tags=["staging", "extra_attributes", "reorder-columns"]
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
	FROM {{ source('ff_anilist', 'lists_2022') }} l
		JOIN {{ source('ff_anilist', 'users') }} u
	USING (username)
)

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
