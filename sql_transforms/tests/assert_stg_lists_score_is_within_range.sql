-- `stg_lists` are the backbone historical lists that is frequently changed and modified
-- make sure that I don't do anything wrong by putting this sanity tests here
SELECT *
FROM {{ ref("stg_lists") }}
WHERE
	(
		(score_format = "POINT_10_DECIMAL" AND CAST(score AS DECIMAL) > 10.0)
		OR
		(score_format = "POINT_100" AND CAST(score AS INTEGER) > 100)
		OR
		(score_format = "POINT_10" AND CAST(score AS INTEGER) > 10)
		OR
		(score_format = "POINT_5" AND CAST(score AS INTEGER) > 5)
	)
	OR anichan_score > 100
	OR appropriate_score > 100