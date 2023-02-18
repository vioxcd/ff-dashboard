-- * 90th percentile of the most divisive series (using score standard deviation)
-- the final results are joined to `v_as_rules` so that `ff_score` can be displayed
CREATE VIEW v_divisive_media_p90
AS
WITH
ordered_divs AS (
	SELECT
		*,
		1 - PERCENT_RANK()
			OVER(ORDER BY ff_stddev DESC)
			AS pct_rank
	FROM v_media_stddev
)
SELECT
	od.*,
	md.cover_image_url_xl
FROM ordered_divs od
	JOIN media_details md
	ON od.title = md.title AND od.media_type = md.type
WHERE pct_rank > .9 -- * can change this if it's too much
ORDER BY ff_stddev DESC