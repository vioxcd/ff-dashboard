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
		CAST(anichan_score AS INTEGER) AS anichan_score,
		CAST(appropriate_score AS INTEGER) AS appropriate_score 
	FROM v_appropriate_score
	WHERE CAST(anichan_score AS INTEGER) > 0
		AND CAST(appropriate_score AS INTEGER) > 0
),
average_scores AS (
	SELECT
		media_id,
		title,
		media_type,
		CAST(AVG(anichan_score) AS INTEGER) AS anichan_avg,
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
		a.anichan_avg,
		a.ff_avg,
		CAST(
			SQRT(SUM(POWER(f.anichan_score - a.anichan_avg, 2)) / a.n)
			AS INTEGER
		) AS anichan_stddev,
		CAST(
			SQRT(SUM(POWER(f.appropriate_score - a.ff_avg, 2)) / a.n)
			AS INTEGER
		) AS ff_stddev,
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
	ff_stddev DESC,
	anichan_stddev DESC