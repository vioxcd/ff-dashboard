{{ config(tags='intermediate') }}

WITH
scores_stddev  AS (
	SELECT
		ar.title,
		ar.media_type,
		ar.anichan_score,
		ar.ff_score,
		CAST(
			SQRT(SUM(POWER(l.anichan_score - ar.anichan_score, 2)) / ar.audience_count)
			AS INTEGER
		) AS anichan_stddev,
		CAST(
			SQRT(SUM(POWER(l.appropriate_score - ar.ff_score, 2)) / ar.audience_count)
			AS INTEGER
		) AS ff_stddev,
		ar.audience_count
	FROM {{ ref('int_media__as_rules') }} ar
		JOIN {{ ref('stg_lists') }} l
		USING(media_id)
	WHERE appropriate_score > 0
	GROUP BY 1, 2
)

SELECT
	*,
	1 - PERCENT_RANK()
		OVER(ORDER BY ff_stddev DESC)
		AS pct_rank
FROM scores_stddev