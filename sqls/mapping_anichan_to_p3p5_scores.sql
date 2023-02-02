-- A mapping view that converts anichan score to p3p5 scores
-- p3p5 scores have known and non-random mapping,
-- so it's easier to convert to it and then converting to appropriate score
CREATE VIEW m_anichan_to_p3p5_scores
AS
SELECT username, scores, scores_anichan
FROM lists
WHERE username IN (
	SELECT username
	FROM users
	WHERE score_format IN ("POINT_5", "POINT_3")
)
GROUP BY 1, 2, 3