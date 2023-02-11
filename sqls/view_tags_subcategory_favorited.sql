-- Most favorited tags over subcategory, by counts and score average
CREATE VIEW v_tags_favorited
AS
WITH
wide_favourite_tags AS (
  	SELECT f.user_id, vwt.*
  	FROM favourites f
  	JOIN v_wide_tags vwt
  	ON f.name = vwt.title
),
sub_category_stat AS (
  	SELECT
		name,
		sub_category,
		COUNT(1) AS counts,
		AVG(ff_avg) AS ff_score_avg
	FROM wide_favourite_tags
	GROUP BY 1, 2
)
SELECT
		name,
		sub_category,
		counts,
		DENSE_RANK() OVER (PARTITION BY sub_category
							ORDER BY counts DESC)
							AS sub_category_ranks_by_count,
		ff_score_avg,
		DENSE_RANK() OVER (PARTITION BY sub_category
							ORDER BY ff_score_avg DESC)
							AS sub_category_ranks_by_avg
FROM sub_category_stat
ORDER BY 2, 3 DESC, 5 DESC