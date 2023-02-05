-- a view that lists standard deviation of each media
-- used to answer the question of "what's the most divisive series?"
CREATE VIEW v_media_stddev AS
WITH
filtered_lists AS (
	SELECT
		username,
		media_id,
		title,
		media_type,
		CAST(scores_anichan AS INTEGER) AS scores_anichan,
		CAST(appropriate_score AS INTEGER) AS appropriate_score 
	FROM v_appropriate_score
	WHERE CAST(scores_anichan AS INTEGER) > 0
		AND CAST(appropriate_score AS INTEGER) > 0
),
average_scores AS (
	SELECT
		media_id,
		title,
		media_type,
		CAST(AVG(scores_anichan) AS INTEGER) AS anichan_avg,
		CAST(AVG(appropriate_score) AS INTEGER) AS ff_avg,
		COUNT(1) AS n
	FROM filtered_lists
	GROUP BY title, media_type
	HAVING COUNT(1) > 5
),
scores_stddev AS (
	SELECT
		a.title,
		a.media_type,
		SQRT(SUM(POWER(f.scores_anichan - a.anichan_avg, 2)) / a.n) AS anichan_stddev,
		SQRT(SUM(POWER(f.appropriate_score - a.ff_avg, 2)) / a.n) AS ff_stddev,
		a.n
	FROM average_scores a
	JOIN filtered_lists f
	USING(media_id)
	GROUP BY 1, 2
	ORDER BY n DESC
)
SELECT *
FROM scores_stddev
ORDER BY
	anichan_stddev DESC,
	ff_stddev DESC