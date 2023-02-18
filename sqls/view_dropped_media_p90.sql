-- a view that lists number of dropped counts per-media, filtered in .9 percentile
-- used to answer the question of "what's the most disliked series?"
-- it's set to .9 because the .9 counts are 2 (and it's too little)
CREATE VIEW v_dropped_media_p90
AS
WITH
dropped_lists AS (
	SELECT
		username,
		media_id,
		title,
		media_type
	FROM v_appropriate_score
	WHERE status = "DROPPED"
),
dropped_counts AS (
	SELECT
		media_id,
		title,
		media_type,
		COUNT(1) AS n
	FROM dropped_lists
	GROUP BY title, media_type
),
ordered_dropped AS (
	SELECT
		*,
		1 - PERCENT_RANK()
			OVER(ORDER BY n DESC)
			AS pct_rank
	FROM dropped_counts
)
SELECT
	dc.*,
	md.cover_image_url_xl
FROM ordered_dropped dc
	JOIN media_details md
	ON dc.title = md.title AND dc.media_type = md.type
WHERE pct_rank > .9 -- * can change this if it's too much
ORDER BY n DESC