-- Update score value to its correct form
WITH cte_appropriate_score
AS (
	SELECT
		l.username,
		l.media_id,
		CASE
			WHEN u.is_buggy AND u.score_format = "POINT_10_DECIMAL"
				THEN CAST(l.anichan_score AS REAL) / 10
			WHEN u.is_buggy AND u.score_format = "POINT_10"
				THEN CAST(l.anichan_score AS INTEGER) / 10
			ELSE
				l.score
		END AS score
	FROM lists l
	JOIN users u
	USING (username)
)
UPDATE lists SET score = cas.score
FROM cte_appropriate_score cas
WHERE lists.username = cas.username AND lists.media_id = cas.media_id