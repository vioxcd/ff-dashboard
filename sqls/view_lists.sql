-- Create new lists with correct score
CREATE VIEW v_lists AS
SELECT
	l.username,
	CASE
		WHEN vbu.is_buggy AND score_format = "POINT_10_DECIMAL"
			THEN CAST(scores_anichan AS REAL) / 10
		WHEN vbu.is_buggy AND score_format = "POINT_10"
			THEN CAST(scores_anichan AS INTEGER) / 10
		ELSE
			scores
	END AS scores,
	l.scores_anichan,
	l.status,
	l.media_id,
	l.media_type,
	l.title,
	l.progress,
	l.completed_at
FROM lists l
JOIN v_buggy_users vbu
USING (username)