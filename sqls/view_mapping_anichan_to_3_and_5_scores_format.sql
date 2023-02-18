-- A mapping view that converts anichan score to 3 and 5 scores format
-- these 3 and 5 scores have known and non-random mapping,
-- so it's easier to convert to it and then converting to appropriate score
-- ? to be used in an Airflow pipeline
CREATE VIEW vm_anichan_to_3_and_5_scores_format_mapping
AS
SELECT username, scores, scores_anichan
FROM lists
WHERE username IN (
	SELECT username
	FROM users
	WHERE score_format IN ("POINT_5", "POINT_3")
)
GROUP BY 1, 2, 3