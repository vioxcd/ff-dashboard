CREATE VIEW v_appropriate_score
AS
SELECT *,
	CASE score_format
		WHEN 'POINT_10_DECIMAL' THEN CAST(ROUND(scores * 10) AS INTEGER)
		WHEN 'POINT_10' THEN scores * 10
		WHEN 'POINT_5' THEN scores * 20
		WHEN 'POINT_3' THEN
			CASE scores
				WHEN 1 THEN 35
				WHEN 2 THEN 70
				WHEN 3 THEN 100
			END
		ELSE scores
	END AS appropriate_score,
	CASE score_format
		WHEN 'POINT_10_DECIMAL' THEN CAST((scores * 10) AS INTEGER)
		WHEN 'POINT_10' THEN scores * 10
		WHEN 'POINT_5' THEN
			CASE scores
				WHEN 1 THEN 10
				WHEN 2 THEN 40
				WHEN 3 THEN 50
				WHEN 4 THEN 70
				WHEN 5 THEN 90
			END
		WHEN 'POINT_3' THEN
			CASE scores
				WHEN 1 THEN 35
				WHEN 2 THEN 60
				WHEN 3 THEN 100
			END
		ELSE scores
	END AS anichan_score
FROM lists
	JOIN users
	USING (username)