-- Tags sub category ranked by count and ff average score
CREATE VIEW v_tags_subcategory_ranked
AS
WITH
sub_category_stat AS (
	SELECT
		name,  -- tag name
		sub_category,
		COUNT(1) AS counts,
		AVG(ff_avg) AS ff_score_avg
	FROM v_wide_tags
	GROUP BY 1, 2
)
SELECT
	name,
	sub_category,
	counts,
	DENSE_RANK() OVER (PARTITION BY sub_category
						ORDER BY counts DESC)
						AS ranks_by_count,
	ff_score_avg,
	DENSE_RANK() OVER (PARTITION BY sub_category
						ORDER BY ff_score_avg DESC)
						AS ranks_by_ff_score_avg
FROM sub_category_stat
ORDER BY 2, 3 DESC, 5 DESC -- easier to see the table this way