CREATE VIEW v_appropriate_score
AS
SELECT *,
	CASE score_format
		WHEN 'POINT_10_DECIMAL' THEN CAST(ROUND(scores * 10) AS INTEGER)
		WHEN 'POINT_10' THEN scores * 10
		WHEN 'POINT_5' THEN scores * 20
		ELSE scores
	END AS appropriate_score
FROM lists
	JOIN users
	USING (username)