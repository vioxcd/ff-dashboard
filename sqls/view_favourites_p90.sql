CREATE VIEW v_favorites_p90 AS
WITH
counted_favs AS (
	SELECT
		name,
		type,
		cover_image_url,
		COUNT(1) AS counts
	FROM favourites
	GROUP BY 1, 2
	ORDER BY 3 DESC
), ordered_per_type AS (
	SELECT
		*,
		1 - PERCENT_RANK()
			OVER(PARTITION BY type ORDER BY counts DESC)
			AS pct_rank
	FROM counted_favs
)
SELECT *
FROM ordered_per_type
WHERE pct_rank > .9