-- Update score value to its correct form
WITH cte_appropriate_score
AS (
	SELECT
		l.username,
		l.media_id,
		CASE
			WHEN u.is_buggy AND u.score_format = "POINT_10_DECIMAL"
				THEN CAST(l.scores_anichan AS REAL) / 10
			WHEN u.is_buggy AND u.score_format = "POINT_10"
				THEN CAST(l.scores_anichan AS INTEGER) / 10
			ELSE
				l.scores
		END AS scores
	FROM lists l
	JOIN users u
	USING (username)
)
UPDATE lists SET scores = cas.scores
FROM cte_appropriate_score cas
WHERE lists.username = cas.username AND lists.media_id = cas.media_id 